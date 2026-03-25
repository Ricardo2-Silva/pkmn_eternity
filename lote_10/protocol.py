# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\internet\protocol.py
"""
Standard implementations of Twisted protocol-related interfaces.

Start here if you are looking to write a new protocol implementation for
Twisted.  The Protocol class contains some introductory material.
"""
from __future__ import division, absolute_import
import random
from zope.interface import implementer
from twisted.python import log, failure, components
from twisted.internet import interfaces, error, defer
from twisted.logger import _loggerFor
from twisted.python._oldstyle import _oldStyle

@implementer(interfaces.IProtocolFactory, interfaces.ILoggingContext)
@_oldStyle
class Factory:
    __doc__ = "\n    This is a factory which produces protocols.\n\n    By default, buildProtocol will create a protocol of the class given in\n    self.protocol.\n    "
    protocol = None
    numPorts = 0
    noisy = True

    @classmethod
    def forProtocol(cls, protocol, *args, **kwargs):
        """
        Create a factory for the given protocol.

        It sets the C{protocol} attribute and returns the constructed factory
        instance.

        @param protocol: A L{Protocol} subclass

        @param args: Positional arguments for the factory.

        @param kwargs: Keyword arguments for the factory.

        @return: A L{Factory} instance wired up to C{protocol}.
        """
        factory = cls(*args, **kwargs)
        factory.protocol = protocol
        return factory

    def logPrefix(self):
        """
        Describe this factory for log messages.
        """
        return self.__class__.__name__

    def doStart(self):
        """
        Make sure startFactory is called.

        Users should not call this function themselves!
        """
        if not self.numPorts:
            if self.noisy:
                _loggerFor(self).info("Starting factory {factory!r}", factory=self)
            self.startFactory()
        self.numPorts = self.numPorts + 1

    def doStop(self):
        """
        Make sure stopFactory is called.

        Users should not call this function themselves!
        """
        if self.numPorts == 0:
            return
        self.numPorts = self.numPorts - 1
        if not self.numPorts:
            if self.noisy:
                _loggerFor(self).info("Stopping factory {factory!r}", factory=self)
            self.stopFactory()

    def startFactory(self):
        """
        This will be called before I begin listening on a Port or Connector.

        It will only be called once, even if the factory is connected
        to multiple ports.

        This can be used to perform 'unserialization' tasks that
        are best put off until things are actually running, such
        as connecting to a database, opening files, etcetera.
        """
        return

    def stopFactory(self):
        """
        This will be called before I stop listening on all Ports/Connectors.

        This can be overridden to perform 'shutdown' tasks such as disconnecting
        database connections, closing files, etc.

        It will be called, for example, before an application shuts down,
        if it was connected to a port. User code should not call this function
        directly.
        """
        return

    def buildProtocol(self, addr):
        """
        Create an instance of a subclass of Protocol.

        The returned instance will handle input on an incoming server
        connection, and an attribute "factory" pointing to the creating
        factory.

        Alternatively, L{None} may be returned to immediately close the
        new connection.

        Override this method to alter how Protocol instances get created.

        @param addr: an object implementing L{twisted.internet.interfaces.IAddress}
        """
        p = self.protocol()
        p.factory = self
        return p


class ClientFactory(Factory):
    __doc__ = "\n    A Protocol factory for clients.\n\n    This can be used together with the various connectXXX methods in\n    reactors.\n    "

    def startedConnecting(self, connector):
        """
        Called when a connection has been started.

        You can call connector.stopConnecting() to stop the connection attempt.

        @param connector: a Connector object.
        """
        return

    def clientConnectionFailed(self, connector, reason):
        """
        Called when a connection has failed to connect.

        It may be useful to call connector.connect() - this will reconnect.

        @type reason: L{twisted.python.failure.Failure}
        """
        return

    def clientConnectionLost(self, connector, reason):
        """
        Called when an established connection is lost.

        It may be useful to call connector.connect() - this will reconnect.

        @type reason: L{twisted.python.failure.Failure}
        """
        return


class _InstanceFactory(ClientFactory):
    __doc__ = "\n    Factory used by ClientCreator.\n\n    @ivar deferred: The L{Deferred} which represents this connection attempt and\n        which will be fired when it succeeds or fails.\n\n    @ivar pending: After a connection attempt succeeds or fails, a delayed call\n        which will fire the L{Deferred} representing this connection attempt.\n    "
    noisy = False
    pending = None

    def __init__(self, reactor, instance, deferred):
        self.reactor = reactor
        self.instance = instance
        self.deferred = deferred

    def __repr__(self):
        return "<ClientCreator factory: %r>" % (self.instance,)

    def buildProtocol(self, addr):
        """
        Return the pre-constructed protocol instance and arrange to fire the
        waiting L{Deferred} to indicate success establishing the connection.
        """
        self.pending = self.reactor.callLater(0, self.fire, self.deferred.callback, self.instance)
        self.deferred = None
        return self.instance

    def clientConnectionFailed(self, connector, reason):
        """
        Arrange to fire the waiting L{Deferred} with the given failure to
        indicate the connection could not be established.
        """
        self.pending = self.reactor.callLater(0, self.fire, self.deferred.errback, reason)
        self.deferred = None

    def fire(self, func, value):
        """
        Clear C{self.pending} to avoid a reference cycle and then invoke func
        with the value.
        """
        self.pending = None
        func(value)


@_oldStyle
class ClientCreator:
    __doc__ = "\n    Client connections that do not require a factory.\n\n    The various connect* methods create a protocol instance using the given\n    protocol class and arguments, and connect it, returning a Deferred of the\n    resulting protocol instance.\n\n    Useful for cases when we don't really need a factory.  Mainly this\n    is when there is no shared state between protocol instances, and no need\n    to reconnect.\n\n    The C{connectTCP}, C{connectUNIX}, and C{connectSSL} methods each return a\n    L{Deferred} which will fire with an instance of the protocol class passed to\n    L{ClientCreator.__init__}.  These Deferred can be cancelled to abort the\n    connection attempt (in a very unlikely case, cancelling the Deferred may not\n    prevent the protocol from being instantiated and connected to a transport;\n    if this happens, it will be disconnected immediately afterwards and the\n    Deferred will still errback with L{CancelledError}).\n    "

    def __init__(self, reactor, protocolClass, *args, **kwargs):
        self.reactor = reactor
        self.protocolClass = protocolClass
        self.args = args
        self.kwargs = kwargs

    def _connect(self, method, *args, **kwargs):
        """
        Initiate a connection attempt.

        @param method: A callable which will actually start the connection
            attempt.  For example, C{reactor.connectTCP}.

        @param *args: Positional arguments to pass to C{method}, excluding the
            factory.

        @param **kwargs: Keyword arguments to pass to C{method}.

        @return: A L{Deferred} which fires with an instance of the protocol
            class passed to this L{ClientCreator}'s initializer or fails if the
            connection cannot be set up for some reason.
        """

        def cancelConnect(deferred):
            connector.disconnect()
            if f.pending is not None:
                f.pending.cancel()

        d = defer.Deferred(cancelConnect)
        f = _InstanceFactory(self.reactor, (self.protocolClass)(*self.args, **self.kwargs), d)
        connector = method(args, factory=f, **kwargs)
        return d

    def connectTCP(self, host, port, timeout=30, bindAddress=None):
        """
        Connect to a TCP server.

        The parameters are all the same as to L{IReactorTCP.connectTCP} except
        that the factory parameter is omitted.

        @return: A L{Deferred} which fires with an instance of the protocol
            class passed to this L{ClientCreator}'s initializer or fails if the
            connection cannot be set up for some reason.
        """
        return self._connect((self.reactor.connectTCP),
          host, port, timeout=timeout, bindAddress=bindAddress)

    def connectUNIX(self, address, timeout=30, checkPID=False):
        """
        Connect to a Unix socket.

        The parameters are all the same as to L{IReactorUNIX.connectUNIX} except
        that the factory parameter is omitted.

        @return: A L{Deferred} which fires with an instance of the protocol
            class passed to this L{ClientCreator}'s initializer or fails if the
            connection cannot be set up for some reason.
        """
        return self._connect((self.reactor.connectUNIX),
          address, timeout=timeout, checkPID=checkPID)

    def connectSSL(self, host, port, contextFactory, timeout=30, bindAddress=None):
        """
        Connect to an SSL server.

        The parameters are all the same as to L{IReactorSSL.connectSSL} except
        that the factory parameter is omitted.

        @return: A L{Deferred} which fires with an instance of the protocol
            class passed to this L{ClientCreator}'s initializer or fails if the
            connection cannot be set up for some reason.
        """
        return self._connect((self.reactor.connectSSL),
          host, port, contextFactory=contextFactory,
          timeout=timeout,
          bindAddress=bindAddress)


class ReconnectingClientFactory(ClientFactory):
    __doc__ = "\n    Factory which auto-reconnects clients with an exponential back-off.\n\n    Note that clients should call my resetDelay method after they have\n    connected successfully.\n\n    @ivar maxDelay: Maximum number of seconds between connection attempts.\n    @ivar initialDelay: Delay for the first reconnection attempt.\n    @ivar factor: A multiplicitive factor by which the delay grows\n    @ivar jitter: Percentage of randomness to introduce into the delay length\n        to prevent stampeding.\n    @ivar clock: The clock used to schedule reconnection. It's mainly useful to\n        be parametrized in tests. If the factory is serialized, this attribute\n        will not be serialized, and the default value (the reactor) will be\n        restored when deserialized.\n    @type clock: L{IReactorTime}\n    @ivar maxRetries: Maximum number of consecutive unsuccessful connection\n        attempts, after which no further connection attempts will be made. If\n        this is not explicitly set, no maximum is applied.\n    "
    maxDelay = 3600
    initialDelay = 1.0
    factor = 2.718281828459045
    jitter = 0.119626565582
    delay = initialDelay
    retries = 0
    maxRetries = None
    _callID = None
    connector = None
    clock = None
    continueTrying = 1

    def clientConnectionFailed(self, connector, reason):
        if self.continueTrying:
            self.connector = connector
            self.retry()

    def clientConnectionLost(self, connector, unused_reason):
        if self.continueTrying:
            self.connector = connector
            self.retry()

    def retry(self, connector=None):
        """
        Have this connector connect again, after a suitable delay.
        """
        if not self.continueTrying:
            if self.noisy:
                log.msg("Abandoning %s on explicit request" % (connector,))
            return
        else:
            if connector is None:
                if self.connector is None:
                    raise ValueError("no connector to retry")
                else:
                    connector = self.connector
                self.retries += 1
                if self.maxRetries is not None:
                    if self.retries > self.maxRetries:
                        if self.noisy:
                            log.msg("Abandoning %s after %d retries." % (
                             connector, self.retries))
                        return
            else:
                self.delay = min(self.delay * self.factor, self.maxDelay)
                if self.jitter:
                    self.delay = random.normalvariate(self.delay, self.delay * self.jitter)
                if self.noisy:
                    log.msg("%s will retry in %d seconds" % (connector, self.delay))

            def reconnector():
                self._callID = None
                connector.connect()

            if self.clock is None:
                from twisted.internet import reactor
                self.clock = reactor
        self._callID = self.clock.callLater(self.delay, reconnector)

    def stopTrying(self):
        """
        Put a stop to any attempt to reconnect in progress.
        """
        if self._callID:
            self._callID.cancel()
            self._callID = None
        self.continueTrying = 0
        if self.connector:
            try:
                self.connector.stopConnecting()
            except error.NotConnectingError:
                pass

    def resetDelay(self):
        """
        Call this method after a successful connection: it resets the delay and
        the retry counter.
        """
        self.delay = self.initialDelay
        self.retries = 0
        self._callID = None
        self.continueTrying = 1

    def __getstate__(self):
        """
        Remove all of the state which is mutated by connection attempts and
        failures, returning just the state which describes how reconnections
        should be attempted.  This will make the unserialized instance
        behave just as this one did when it was first instantiated.
        """
        state = self.__dict__.copy()
        for key in ('connector', 'retries', 'delay', 'continueTrying', '_callID', 'clock'):
            if key in state:
                del state[key]

        return state


class ServerFactory(Factory):
    __doc__ = "\n    Subclass this to indicate that your protocol.Factory is only usable for servers.\n    "


@_oldStyle
class BaseProtocol:
    __doc__ = "\n    This is the abstract superclass of all protocols.\n\n    Some methods have helpful default implementations here so that they can\n    easily be shared, but otherwise the direct subclasses of this class are more\n    interesting, L{Protocol} and L{ProcessProtocol}.\n    "
    connected = 0
    transport = None

    def makeConnection(self, transport):
        """
        Make a connection to a transport and a server.

        This sets the 'transport' attribute of this Protocol, and calls the
        connectionMade() callback.
        """
        self.connected = 1
        self.transport = transport
        self.connectionMade()

    def connectionMade(self):
        """
        Called when a connection is made.

        This may be considered the initializer of the protocol, because
        it is called when the connection is completed.  For clients,
        this is called once the connection to the server has been
        established; for servers, this is called after an accept() call
        stops blocking and a socket has been received.  If you need to
        send any greeting or initial message, do it here.
        """
        return


connectionDone = failure.Failure(error.ConnectionDone())
connectionDone.cleanFailure()

@implementer(interfaces.IProtocol, interfaces.ILoggingContext)
class Protocol(BaseProtocol):
    __doc__ = "\n    This is the base class for streaming connection-oriented protocols.\n\n    If you are going to write a new connection-oriented protocol for Twisted,\n    start here.  Any protocol implementation, either client or server, should\n    be a subclass of this class.\n\n    The API is quite simple.  Implement L{dataReceived} to handle both\n    event-based and synchronous input; output can be sent through the\n    'transport' attribute, which is to be an instance that implements\n    L{twisted.internet.interfaces.ITransport}.  Override C{connectionLost} to be\n    notified when the connection ends.\n\n    Some subclasses exist already to help you write common types of protocols:\n    see the L{twisted.protocols.basic} module for a few of them.\n    "

    def logPrefix(self):
        """
        Return a prefix matching the class name, to identify log messages
        related to this protocol instance.
        """
        return self.__class__.__name__

    def dataReceived(self, data):
        """
        Called whenever data is received.

        Use this method to translate to a higher-level message.  Usually, some
        callback will be made upon the receipt of each complete protocol
        message.

        @param data: a string of indeterminate length.  Please keep in mind
            that you will probably need to buffer some data, as partial
            (or multiple) protocol messages may be received!  I recommend
            that unit tests for protocols call through to this method with
            differing chunk sizes, down to one byte at a time.
        """
        return

    def connectionLost(self, reason=connectionDone):
        """
        Called when the connection is shut down.

        Clear any circular references here, and any external references
        to this Protocol.  The connection has been closed.

        @type reason: L{twisted.python.failure.Failure}
        """
        return


@implementer(interfaces.IConsumer)
class ProtocolToConsumerAdapter(components.Adapter):

    def write(self, data):
        self.original.dataReceived(data)

    def registerProducer(self, producer, streaming):
        return

    def unregisterProducer(self):
        return


components.registerAdapter(ProtocolToConsumerAdapter, interfaces.IProtocol, interfaces.IConsumer)

@implementer(interfaces.IProtocol)
class ConsumerToProtocolAdapter(components.Adapter):

    def dataReceived(self, data):
        self.original.write(data)

    def connectionLost(self, reason):
        return

    def makeConnection(self, transport):
        return

    def connectionMade(self):
        return


components.registerAdapter(ConsumerToProtocolAdapter, interfaces.IConsumer, interfaces.IProtocol)

@implementer(interfaces.IProcessProtocol)
class ProcessProtocol(BaseProtocol):
    __doc__ = "\n    Base process protocol implementation which does simple dispatching for\n    stdin, stdout, and stderr file descriptors.\n    "

    def childDataReceived(self, childFD, data):
        if childFD == 1:
            self.outReceived(data)
        elif childFD == 2:
            self.errReceived(data)

    def outReceived(self, data):
        """
        Some data was received from stdout.
        """
        return

    def errReceived(self, data):
        """
        Some data was received from stderr.
        """
        return

    def childConnectionLost(self, childFD):
        if childFD == 0:
            self.inConnectionLost()
        elif childFD == 1:
            self.outConnectionLost()
        elif childFD == 2:
            self.errConnectionLost()

    def inConnectionLost(self):
        """
        This will be called when stdin is closed.
        """
        return

    def outConnectionLost(self):
        """
        This will be called when stdout is closed.
        """
        return

    def errConnectionLost(self):
        """
        This will be called when stderr is closed.
        """
        return

    def processExited(self, reason):
        """
        This will be called when the subprocess exits.

        @type reason: L{twisted.python.failure.Failure}
        """
        return

    def processEnded(self, reason):
        """
        Called when the child process exits and all file descriptors
        associated with it have been closed.

        @type reason: L{twisted.python.failure.Failure}
        """
        return


@_oldStyle
class AbstractDatagramProtocol:
    __doc__ = "\n    Abstract protocol for datagram-oriented transports, e.g. IP, ICMP, ARP, UDP.\n    "
    transport = None
    numPorts = 0
    noisy = True

    def __getstate__(self):
        d = self.__dict__.copy()
        d["transport"] = None
        return d

    def doStart(self):
        """
        Make sure startProtocol is called.

        This will be called by makeConnection(), users should not call it.
        """
        if not self.numPorts:
            if self.noisy:
                log.msg("Starting protocol %s" % self)
            self.startProtocol()
        self.numPorts = self.numPorts + 1

    def doStop(self):
        """
        Make sure stopProtocol is called.

        This will be called by the port, users should not call it.
        """
        assert self.numPorts > 0
        self.numPorts = self.numPorts - 1
        self.transport = None
        if not self.numPorts:
            if self.noisy:
                log.msg("Stopping protocol %s" % self)
            self.stopProtocol()

    def startProtocol(self):
        """
        Called when a transport is connected to this protocol.

        Will only be called once, even if multiple ports are connected.
        """
        return

    def stopProtocol(self):
        """
        Called when the transport is disconnected.

        Will only be called once, after all ports are disconnected.
        """
        return

    def makeConnection(self, transport):
        """
        Make a connection to a transport and a server.

        This sets the 'transport' attribute of this DatagramProtocol, and calls the
        doStart() callback.
        """
        assert self.transport == None
        self.transport = transport
        self.doStart()

    def datagramReceived(self, datagram, addr):
        """
        Called when a datagram is received.

        @param datagram: the string received from the transport.
        @param addr: tuple of source of datagram.
        """
        return


@implementer(interfaces.ILoggingContext)
class DatagramProtocol(AbstractDatagramProtocol):
    __doc__ = "\n    Protocol for datagram-oriented transport, e.g. UDP.\n\n    @type transport: L{None} or\n        L{IUDPTransport<twisted.internet.interfaces.IUDPTransport>} provider\n    @ivar transport: The transport with which this protocol is associated,\n        if it is associated with one.\n    "

    def logPrefix(self):
        """
        Return a prefix matching the class name, to identify log messages
        related to this protocol instance.
        """
        return self.__class__.__name__

    def connectionRefused(self):
        """
        Called due to error from write in connected mode.

        Note this is a result of ICMP message generated by *previous*
        write.
        """
        return


class ConnectedDatagramProtocol(DatagramProtocol):
    __doc__ = "\n    Protocol for connected datagram-oriented transport.\n\n    No longer necessary for UDP.\n    "

    def datagramReceived(self, datagram):
        """
        Called when a datagram is received.

        @param datagram: the string received from the transport.
        """
        return

    def connectionFailed(self, failure):
        """
        Called if connecting failed.

        Usually this will be due to a DNS lookup failure.
        """
        return


@implementer(interfaces.ITransport)
@_oldStyle
class FileWrapper:
    __doc__ = "\n    A wrapper around a file-like object to make it behave as a Transport.\n\n    This doesn't actually stream the file to the attached protocol,\n    and is thus useful mainly as a utility for debugging protocols.\n    "
    closed = 0
    disconnecting = 0
    producer = None
    streamingProducer = 0

    def __init__(self, file):
        self.file = file

    def write(self, data):
        try:
            self.file.write(data)
        except:
            self.handleException()

    def _checkProducer(self):
        if self.producer:
            self.producer.resumeProducing()

    def registerProducer(self, producer, streaming):
        """
        From abstract.FileDescriptor
        """
        self.producer = producer
        self.streamingProducer = streaming
        if not streaming:
            producer.resumeProducing()

    def unregisterProducer(self):
        self.producer = None

    def stopConsuming(self):
        self.unregisterProducer()
        self.loseConnection()

    def writeSequence(self, iovec):
        self.write((b'').join(iovec))

    def loseConnection(self):
        self.closed = 1
        try:
            self.file.close()
        except (IOError, OSError):
            self.handleException()

    def getPeer(self):
        return ('file', 'file')

    def getHost(self):
        return "file"

    def handleException(self):
        return

    def resumeProducing(self):
        return

    def pauseProducing(self):
        return

    def stopProducing(self):
        self.loseConnection()


__all__ = [
 'Factory', 'ClientFactory', 'ReconnectingClientFactory', 'connectionDone', 
 'Protocol', 
 'ProcessProtocol', 'FileWrapper', 'ServerFactory', 
 'AbstractDatagramProtocol', 
 'DatagramProtocol', 'ConnectedDatagramProtocol', 
 'ClientCreator']
