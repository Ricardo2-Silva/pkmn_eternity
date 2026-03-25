# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\protocols\tls.py
"""
Implementation of a TLS transport (L{ISSLTransport}) as an
L{IProtocol<twisted.internet.interfaces.IProtocol>} layered on top of any
L{ITransport<twisted.internet.interfaces.ITransport>} implementation, based on
U{OpenSSL<http://www.openssl.org>}'s memory BIO features.

L{TLSMemoryBIOFactory} is a L{WrappingFactory} which wraps protocols created by
the factory it wraps with L{TLSMemoryBIOProtocol}.  L{TLSMemoryBIOProtocol}
intercedes between the underlying transport and the wrapped protocol to
implement SSL and TLS.  Typical usage of this module looks like this::

    from twisted.protocols.tls import TLSMemoryBIOFactory
    from twisted.internet.protocol import ServerFactory
    from twisted.internet.ssl import PrivateCertificate
    from twisted.internet import reactor

    from someapplication import ApplicationProtocol

    serverFactory = ServerFactory()
    serverFactory.protocol = ApplicationProtocol
    certificate = PrivateCertificate.loadPEM(certPEMData)
    contextFactory = certificate.options()
    tlsFactory = TLSMemoryBIOFactory(contextFactory, False, serverFactory)
    reactor.listenTCP(12345, tlsFactory)
    reactor.run()

This API offers somewhat more flexibility than
L{twisted.internet.interfaces.IReactorSSL}; for example, a
L{TLSMemoryBIOProtocol} instance can use another instance of
L{TLSMemoryBIOProtocol} as its transport, yielding TLS over TLS - useful to
implement onion routing.  It can also be used to run TLS over unusual
transports, such as UNIX sockets and stdio.
"""
from __future__ import division, absolute_import
from OpenSSL.SSL import Error, ZeroReturnError, WantReadError
from OpenSSL.SSL import TLSv1_METHOD, Context, Connection
try:
    Connection(Context(TLSv1_METHOD), None)
except TypeError as e:
    if str(e) != "argument must be an int, or have a fileno() method.":
        raise
    raise ImportError("twisted.protocols.tls requires pyOpenSSL 0.10 or newer.")

from zope.interface import implementer, providedBy, directlyProvides
from twisted.python.compat import unicode
from twisted.python.failure import Failure
from twisted.internet.interfaces import ISystemHandle, INegotiated, IPushProducer, ILoggingContext, IOpenSSLServerConnectionCreator, IOpenSSLClientConnectionCreator, IProtocolNegotiationFactory, IHandshakeListener
from twisted.internet.main import CONNECTION_LOST
from twisted.internet._producer_helpers import _PullToPush
from twisted.internet.protocol import Protocol
from twisted.internet._sslverify import _setAcceptableProtocols
from twisted.protocols.policies import ProtocolWrapper, WrappingFactory

@implementer(IPushProducer)
class _ProducerMembrane(object):
    __doc__ = "\n    Stand-in for producer registered with a L{TLSMemoryBIOProtocol} transport.\n\n    Ensures that producer pause/resume events from the undelying transport are\n    coordinated with pause/resume events from the TLS layer.\n\n    @ivar _producer: The application-layer producer.\n    "
    _producerPaused = False

    def __init__(self, producer):
        self._producer = producer

    def pauseProducing(self):
        """
        C{pauseProducing} the underlying producer, if it's not paused.
        """
        if self._producerPaused:
            return
        self._producerPaused = True
        self._producer.pauseProducing()

    def resumeProducing(self):
        """
        C{resumeProducing} the underlying producer, if it's paused.
        """
        if not self._producerPaused:
            return
        self._producerPaused = False
        self._producer.resumeProducing()

    def stopProducing(self):
        """
        C{stopProducing} the underlying producer.

        There is only a single source for this event, so it's simply passed
        on.
        """
        self._producer.stopProducing()


@implementer(ISystemHandle, INegotiated)
class TLSMemoryBIOProtocol(ProtocolWrapper):
    __doc__ = "\n    L{TLSMemoryBIOProtocol} is a protocol wrapper which uses OpenSSL via a\n    memory BIO to encrypt bytes written to it before sending them on to the\n    underlying transport and decrypts bytes received from the underlying\n    transport before delivering them to the wrapped protocol.\n\n    In addition to producer events from the underlying transport, the need to\n    wait for reads before a write can proceed means the L{TLSMemoryBIOProtocol}\n    may also want to pause a producer.  Pause/resume events are therefore\n    merged using the L{_ProducerMembrane} wrapper.  Non-streaming (pull)\n    producers are supported by wrapping them with L{_PullToPush}.\n\n    @ivar _tlsConnection: The L{OpenSSL.SSL.Connection} instance which is\n        encrypted and decrypting this connection.\n\n    @ivar _lostTLSConnection: A flag indicating whether connection loss has\n        already been dealt with (C{True}) or not (C{False}).  TLS disconnection\n        is distinct from the underlying connection being lost.\n\n    @ivar _appSendBuffer: application-level (cleartext) data that is waiting to\n        be transferred to the TLS buffer, but can't be because the TLS\n        connection is handshaking.\n    @type _appSendBuffer: L{list} of L{bytes}\n\n    @ivar _connectWrapped: A flag indicating whether or not to call\n        C{makeConnection} on the wrapped protocol.  This is for the reactor's\n        L{twisted.internet.interfaces.ITLSTransport.startTLS} implementation,\n        since it has a protocol which it has already called C{makeConnection}\n        on, and which has no interest in a new transport.  See #3821.\n\n    @ivar _handshakeDone: A flag indicating whether or not the handshake is\n        known to have completed successfully (C{True}) or not (C{False}).  This\n        is used to control error reporting behavior.  If the handshake has not\n        completed, the underlying L{OpenSSL.SSL.Error} will be passed to the\n        application's C{connectionLost} method.  If it has completed, any\n        unexpected L{OpenSSL.SSL.Error} will be turned into a\n        L{ConnectionLost}.  This is weird; however, it is simply an attempt at\n        a faithful re-implementation of the behavior provided by\n        L{twisted.internet.ssl}.\n\n    @ivar _reason: If an unexpected L{OpenSSL.SSL.Error} occurs which causes\n        the connection to be lost, it is saved here.  If appropriate, this may\n        be used as the reason passed to the application protocol's\n        C{connectionLost} method.\n\n    @ivar _producer: The current producer registered via C{registerProducer},\n        or L{None} if no producer has been registered or a previous one was\n        unregistered.\n\n    @ivar _aborted: C{abortConnection} has been called.  No further data will\n        be received to the wrapped protocol's C{dataReceived}.\n    @type _aborted: L{bool}\n    "
    _reason = None
    _handshakeDone = False
    _lostTLSConnection = False
    _producer = None
    _aborted = False

    def __init__(self, factory, wrappedProtocol, _connectWrapped=True):
        ProtocolWrapper.__init__(self, factory, wrappedProtocol)
        self._connectWrapped = _connectWrapped

    def getHandle(self):
        """
        Return the L{OpenSSL.SSL.Connection} object being used to encrypt and
        decrypt this connection.

        This is done for the benefit of L{twisted.internet.ssl.Certificate}'s
        C{peerFromTransport} and C{hostFromTransport} methods only.  A
        different system handle may be returned by future versions of this
        method.
        """
        return self._tlsConnection

    def makeConnection(self, transport):
        """
        Connect this wrapper to the given transport and initialize the
        necessary L{OpenSSL.SSL.Connection} with a memory BIO.
        """
        self._tlsConnection = self.factory._createConnection(self)
        self._appSendBuffer = []
        for interface in providedBy(transport):
            directlyProvides(self, interface)

        Protocol.makeConnection(self, transport)
        self.factory.registerProtocol(self)
        if self._connectWrapped:
            ProtocolWrapper.makeConnection(self, transport)
        self._checkHandshakeStatus()

    def _checkHandshakeStatus(self):
        """
        Ask OpenSSL to proceed with a handshake in progress.

        Initially, this just sends the ClientHello; after some bytes have been
        stuffed in to the C{Connection} object by C{dataReceived}, it will then
        respond to any C{Certificate} or C{KeyExchange} messages.
        """
        if self._aborted:
            return
        try:
            self._tlsConnection.do_handshake()
        except WantReadError:
            self._flushSendBIO()
        except Error:
            self._tlsShutdownFinished(Failure())
        else:
            self._handshakeDone = True
            if IHandshakeListener.providedBy(self.wrappedProtocol):
                self.wrappedProtocol.handshakeCompleted()

    def _flushSendBIO(self):
        """
        Read any bytes out of the send BIO and write them to the underlying
        transport.
        """
        try:
            bytes = self._tlsConnection.bio_read(32768)
        except WantReadError:
            pass
        else:
            self.transport.write(bytes)

    def _flushReceiveBIO(self):
        """
        Try to receive any application-level bytes which are now available
        because of a previous write into the receive BIO.  This will take
        care of delivering any application-level bytes which are received to
        the protocol, as well as handling of the various exceptions which
        can come from trying to get such bytes.
        """
        while not self._lostTLSConnection:
            try:
                bytes = self._tlsConnection.recv(32768)
            except WantReadError:
                break
            except ZeroReturnError:
                self._shutdownTLS()
                self._tlsShutdownFinished(None)
            except Error:
                failure = Failure()
                self._tlsShutdownFinished(failure)

            if not self._aborted:
                ProtocolWrapper.dataReceived(self, bytes)

        self._flushSendBIO()

    def dataReceived(self, bytes):
        """
        Deliver any received bytes to the receive BIO and then read and deliver
        to the application any application-level data which becomes available
        as a result of this.
        """
        self._tlsConnection.bio_write(bytes)
        if not self._handshakeDone:
            self._checkHandshakeStatus()
            if not self._handshakeDone:
                return
        if self._appSendBuffer:
            self._unbufferPendingWrites()
        self._flushReceiveBIO()

    def _shutdownTLS(self):
        """
        Initiate, or reply to, the shutdown handshake of the TLS layer.
        """
        try:
            shutdownSuccess = self._tlsConnection.shutdown()
        except Error:
            shutdownSuccess = False

        self._flushSendBIO()
        if shutdownSuccess:
            self.transport.loseConnection()

    def _tlsShutdownFinished(self, reason):
        """
        Called when TLS connection has gone away; tell underlying transport to
        disconnect.

        @param reason: a L{Failure} whose value is an L{Exception} if we want to
            report that failure through to the wrapped protocol's
            C{connectionLost}, or L{None} if the C{reason} that
            C{connectionLost} should receive should be coming from the
            underlying transport.
        @type reason: L{Failure} or L{None}
        """
        if reason is not None:
            if tuple(reason.value.args[:2]) == (-1, 'Unexpected EOF'):
                reason = Failure(CONNECTION_LOST)
        if self._reason is None:
            self._reason = reason
        self._lostTLSConnection = True
        self._flushSendBIO()
        self.transport.loseConnection()

    def connectionLost(self, reason):
        """
        Handle the possible repetition of calls to this method (due to either
        the underlying transport going away or due to an error at the TLS
        layer) and make sure the base implementation only gets invoked once.
        """
        if not self._lostTLSConnection:
            self._tlsConnection.bio_shutdown()
            self._flushReceiveBIO()
            self._lostTLSConnection = True
        reason = self._reason or reason
        self._reason = None
        self.connected = False
        ProtocolWrapper.connectionLost(self, reason)
        self._tlsConnection = None

    def loseConnection(self):
        """
        Send a TLS close alert and close the underlying connection.
        """
        if self.disconnecting or not self.connected:
            return
        elif not self._handshakeDone:
            if not self._appSendBuffer:
                self.abortConnection()
        self.disconnecting = True
        if not self._appSendBuffer:
            if self._producer is None:
                self._shutdownTLS()

    def abortConnection(self):
        """
        Tear down TLS state so that if the connection is aborted mid-handshake
        we don't deliver any further data from the application.
        """
        self._aborted = True
        self.disconnecting = True
        self._shutdownTLS()
        self.transport.abortConnection()

    def failVerification(self, reason):
        """
        Abort the connection during connection setup, giving a reason that
        certificate verification failed.

        @param reason: The reason that the verification failed; reported to the
            application protocol's C{connectionLost} method.
        @type reason: L{Failure}
        """
        self._reason = reason
        self.abortConnection()

    def write(self, bytes):
        """
        Process the given application bytes and send any resulting TLS traffic
        which arrives in the send BIO.

        If C{loseConnection} was called, subsequent calls to C{write} will
        drop the bytes on the floor.
        """
        if isinstance(bytes, unicode):
            raise TypeError("Must write bytes to a TLS transport, not unicode.")
        if self.disconnecting:
            if self._producer is None:
                return
        self._write(bytes)

    def _bufferedWrite(self, octets):
        """
        Put the given octets into L{TLSMemoryBIOProtocol._appSendBuffer}, and
        tell any listening producer that it should pause because we are now
        buffering.
        """
        self._appSendBuffer.append(octets)
        if self._producer is not None:
            self._producer.pauseProducing()

    def _unbufferPendingWrites(self):
        """
        Un-buffer all waiting writes in L{TLSMemoryBIOProtocol._appSendBuffer}.
        """
        pendingWrites, self._appSendBuffer = self._appSendBuffer, []
        for eachWrite in pendingWrites:
            self._write(eachWrite)

        if self._appSendBuffer:
            return
        if self._producer is not None:
            self._producer.resumeProducing()
            return
        if self.disconnecting:
            self._shutdownTLS()

    def _write(self, bytes):
        """
        Process the given application bytes and send any resulting TLS traffic
        which arrives in the send BIO.

        This may be called by C{dataReceived} with bytes that were buffered
        before C{loseConnection} was called, which is why this function
        doesn't check for disconnection but accepts the bytes regardless.
        """
        if self._lostTLSConnection:
            return
        bufferSize = 16384
        alreadySent = 0
        while alreadySent < len(bytes):
            toSend = bytes[alreadySent:alreadySent + bufferSize]
            try:
                sent = self._tlsConnection.send(toSend)
            except WantReadError:
                self._bufferedWrite(bytes[alreadySent:])
                break
            except Error:
                self._tlsShutdownFinished(Failure())
                break
            else:
                alreadySent += sent
                self._flushSendBIO()

    def writeSequence(self, iovec):
        """
        Write a sequence of application bytes by joining them into one string
        and passing them to L{write}.
        """
        self.write((b'').join(iovec))

    def getPeerCertificate(self):
        return self._tlsConnection.get_peer_certificate()

    @property
    def negotiatedProtocol(self):
        """
        @see: L{INegotiated.negotiatedProtocol}
        """
        protocolName = None
        try:
            protocolName = self._tlsConnection.get_alpn_proto_negotiated()
        except (NotImplementedError, AttributeError):
            pass

        if protocolName not in (b'', None):
            return protocolName
        else:
            try:
                protocolName = self._tlsConnection.get_next_proto_negotiated()
            except (NotImplementedError, AttributeError):
                pass

            if protocolName != b'':
                return protocolName
            return

    def registerProducer(self, producer, streaming):
        if self._lostTLSConnection:
            producer.stopProducing()
            return
        else:
            if not streaming:
                producer = streamingProducer = _PullToPush(producer, self)
            producer = _ProducerMembrane(producer)
            self.transport.registerProducer(producer, True)
            self._producer = producer
            if not streaming:
                streamingProducer.startStreaming()

    def unregisterProducer(self):
        if self._producer is None:
            return
        else:
            if isinstance(self._producer._producer, _PullToPush):
                self._producer._producer.stopStreaming()
            self._producer = None
            self._producerPaused = False
            self.transport.unregisterProducer()
            if self.disconnecting:
                if not self._appSendBuffer:
                    self._shutdownTLS()


@implementer(IOpenSSLClientConnectionCreator, IOpenSSLServerConnectionCreator)
class _ContextFactoryToConnectionFactory(object):
    __doc__ = "\n    Adapter wrapping a L{twisted.internet.interfaces.IOpenSSLContextFactory}\n    into a L{IOpenSSLClientConnectionCreator} or\n    L{IOpenSSLServerConnectionCreator}.\n\n    See U{https://twistedmatrix.com/trac/ticket/7215} for work that should make\n    this unnecessary.\n    "

    def __init__(self, oldStyleContextFactory):
        """
        Construct a L{_ContextFactoryToConnectionFactory} with a
        L{twisted.internet.interfaces.IOpenSSLContextFactory}.

        Immediately call C{getContext} on C{oldStyleContextFactory} in order to
        force advance parameter checking, since old-style context factories
        don't actually check that their arguments to L{OpenSSL} are correct.

        @param oldStyleContextFactory: A factory that can produce contexts.
        @type oldStyleContextFactory:
            L{twisted.internet.interfaces.IOpenSSLContextFactory}
        """
        oldStyleContextFactory.getContext()
        self._oldStyleContextFactory = oldStyleContextFactory

    def _connectionForTLS(self, protocol):
        """
        Create an L{OpenSSL.SSL.Connection} object.

        @param protocol: The protocol initiating a TLS connection.
        @type protocol: L{TLSMemoryBIOProtocol}

        @return: a connection
        @rtype: L{OpenSSL.SSL.Connection}
        """
        context = self._oldStyleContextFactory.getContext()
        return Connection(context, None)

    def serverConnectionForTLS(self, protocol):
        """
        Construct an OpenSSL server connection from the wrapped old-style
        context factory.

        @note: Since old-style context factories don't distinguish between
            clients and servers, this is exactly the same as
            L{_ContextFactoryToConnectionFactory.clientConnectionForTLS}.

        @param protocol: The protocol initiating a TLS connection.
        @type protocol: L{TLSMemoryBIOProtocol}

        @return: a connection
        @rtype: L{OpenSSL.SSL.Connection}
        """
        return self._connectionForTLS(protocol)

    def clientConnectionForTLS(self, protocol):
        """
        Construct an OpenSSL server connection from the wrapped old-style
        context factory.

        @note: Since old-style context factories don't distinguish between
            clients and servers, this is exactly the same as
            L{_ContextFactoryToConnectionFactory.serverConnectionForTLS}.

        @param protocol: The protocol initiating a TLS connection.
        @type protocol: L{TLSMemoryBIOProtocol}

        @return: a connection
        @rtype: L{OpenSSL.SSL.Connection}
        """
        return self._connectionForTLS(protocol)


class TLSMemoryBIOFactory(WrappingFactory):
    __doc__ = "\n    L{TLSMemoryBIOFactory} adds TLS to connections.\n\n    @ivar _creatorInterface: the interface which L{_connectionCreator} is\n        expected to implement.\n    @type _creatorInterface: L{zope.interface.interfaces.IInterface}\n\n    @ivar _connectionCreator: a callable which creates an OpenSSL Connection\n        object.\n    @type _connectionCreator: 1-argument callable taking\n        L{TLSMemoryBIOProtocol} and returning L{OpenSSL.SSL.Connection}.\n    "
    protocol = TLSMemoryBIOProtocol
    noisy = False

    def __init__(self, contextFactory, isClient, wrappedFactory):
        """
        Create a L{TLSMemoryBIOFactory}.

        @param contextFactory: Configuration parameters used to create an
            OpenSSL connection.  In order of preference, what you should pass
            here should be:

                1. L{twisted.internet.ssl.CertificateOptions} (if you're
                   writing a server) or the result of
                   L{twisted.internet.ssl.optionsForClientTLS} (if you're
                   writing a client).  If you want security you should really
                   use one of these.

                2. If you really want to implement something yourself, supply a
                   provider of L{IOpenSSLClientConnectionCreator} or
                   L{IOpenSSLServerConnectionCreator}.

                3. If you really have to, supply a
                   L{twisted.internet.ssl.ContextFactory}.  This will likely be
                   deprecated at some point so please upgrade to the new
                   interfaces.

        @type contextFactory: L{IOpenSSLClientConnectionCreator} or
            L{IOpenSSLServerConnectionCreator}, or, for compatibility with
            older code, anything implementing
            L{twisted.internet.interfaces.IOpenSSLContextFactory}.  See
            U{https://twistedmatrix.com/trac/ticket/7215} for information on
            the upcoming deprecation of passing a
            L{twisted.internet.ssl.ContextFactory} here.

        @param isClient: Is this a factory for TLS client connections; in other
            words, those that will send a C{ClientHello} greeting?  L{True} if
            so, L{False} otherwise.  This flag determines what interface is
            expected of C{contextFactory}.  If L{True}, C{contextFactory}
            should provide L{IOpenSSLClientConnectionCreator}; otherwise it
            should provide L{IOpenSSLServerConnectionCreator}.
        @type isClient: L{bool}

        @param wrappedFactory: A factory which will create the
            application-level protocol.
        @type wrappedFactory: L{twisted.internet.interfaces.IProtocolFactory}
        """
        WrappingFactory.__init__(self, wrappedFactory)
        if isClient:
            creatorInterface = IOpenSSLClientConnectionCreator
        else:
            creatorInterface = IOpenSSLServerConnectionCreator
        self._creatorInterface = creatorInterface
        if not creatorInterface.providedBy(contextFactory):
            contextFactory = _ContextFactoryToConnectionFactory(contextFactory)
        self._connectionCreator = contextFactory

    def logPrefix(self):
        """
        Annotate the wrapped factory's log prefix with some text indicating TLS
        is in use.

        @rtype: C{str}
        """
        if ILoggingContext.providedBy(self.wrappedFactory):
            logPrefix = self.wrappedFactory.logPrefix()
        else:
            logPrefix = self.wrappedFactory.__class__.__name__
        return "%s (TLS)" % (logPrefix,)

    def _applyProtocolNegotiation(self, connection):
        """
        Applies ALPN/NPN protocol neogitation to the connection, if the factory
        supports it.

        @param connection: The OpenSSL connection object to have ALPN/NPN added
            to it.
        @type connection: L{OpenSSL.SSL.Connection}

        @return: Nothing
        @rtype: L{None}
        """
        if IProtocolNegotiationFactory.providedBy(self.wrappedFactory):
            protocols = self.wrappedFactory.acceptableProtocols()
            context = connection.get_context()
            _setAcceptableProtocols(context, protocols)
        return

    def _createConnection(self, tlsProtocol):
        """
        Create an OpenSSL connection and set it up good.

        @param tlsProtocol: The protocol which is establishing the connection.
        @type tlsProtocol: L{TLSMemoryBIOProtocol}

        @return: an OpenSSL connection object for C{tlsProtocol} to use
        @rtype: L{OpenSSL.SSL.Connection}
        """
        connectionCreator = self._connectionCreator
        if self._creatorInterface is IOpenSSLClientConnectionCreator:
            connection = connectionCreator.clientConnectionForTLS(tlsProtocol)
            self._applyProtocolNegotiation(connection)
            connection.set_connect_state()
        else:
            connection = connectionCreator.serverConnectionForTLS(tlsProtocol)
            self._applyProtocolNegotiation(connection)
            connection.set_accept_state()
        return connection
