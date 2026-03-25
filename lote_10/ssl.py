# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\internet\ssl.py
"""
This module implements Transport Layer Security (TLS) support for Twisted.  It
requires U{PyOpenSSL <https://pypi.python.org/pypi/pyOpenSSL>}.

If you wish to establish a TLS connection, please use one of the following
APIs:

    - SSL endpoints for L{servers
      <twisted.internet.endpoints.SSL4ServerEndpoint>} and L{clients
      <twisted.internet.endpoints.SSL4ClientEndpoint>}

    - L{startTLS <twisted.internet.interfaces.ITLSTransport.startTLS>}

    - L{connectSSL <twisted.internet.interfaces.IReactorSSL.connectSSL>}

    - L{listenSSL <twisted.internet.interfaces.IReactorSSL.listenSSL>}

These APIs all require a C{contextFactory} argument that specifies their
security properties, such as certificate, private key, certificate authorities
to verify the peer, allowed TLS protocol versions, cipher suites, and so on.
The recommended value for this argument is a L{CertificateOptions} instance;
see its documentation for an explanation of the available options.

The C{contextFactory} name is a bit of an anachronism now, as context factories
have been replaced with "connection creators", but these objects serve the same
role.

Be warned that implementing your own connection creator (i.e.: value for the
C{contextFactory}) is both difficult and dangerous; the Twisted team has worked
hard to make L{CertificateOptions}' API comprehensible and unsurprising, and
the Twisted team is actively maintaining it to ensure that it becomes more
secure over time.

If you are really absolutely sure that you want to take on the risk of
implementing your own connection creator based on the pyOpenSSL API, see the
L{server connection creator
<twisted.internet.interfaces.IOpenSSLServerConnectionCreator>} and L{client
connection creator
<twisted.internet.interfaces.IOpenSSLServerConnectionCreator>} interfaces.

Developers using Twisted, please ignore the L{Port}, L{Connector}, and
L{Client} classes defined here, as these are details of certain reactors' TLS
implementations, exposed by accident (and remaining here only for compatibility
reasons).  If you wish to establish a TLS connection, please use one of the
APIs listed above.

@note: "SSL" (Secure Sockets Layer) is an antiquated synonym for "TLS"
    (Transport Layer Security).  You may see these terms used interchangeably
    throughout the documentation.
"""
from __future__ import division, absolute_import
from OpenSSL import SSL
supported = True
from zope.interface import implementer, implementer_only, implementedBy
from twisted.internet import tcp, interfaces
from twisted.python._oldstyle import _oldStyle

@implementer(interfaces.IOpenSSLContextFactory)
@_oldStyle
class ContextFactory:
    __doc__ = "A factory for SSL context objects, for server SSL connections."
    isClient = 0

    def getContext(self):
        """Return a SSL.Context object. override in subclasses."""
        raise NotImplementedError


class DefaultOpenSSLContextFactory(ContextFactory):
    __doc__ = "\n    L{DefaultOpenSSLContextFactory} is a factory for server-side SSL context\n    objects.  These objects define certain parameters related to SSL\n    handshakes and the subsequent connection.\n\n    @ivar _contextFactory: A callable which will be used to create new\n        context objects.  This is typically L{OpenSSL.SSL.Context}.\n    "
    _context = None

    def __init__(self, privateKeyFileName, certificateFileName, sslmethod=SSL.SSLv23_METHOD, _contextFactory=SSL.Context):
        """
        @param privateKeyFileName: Name of a file containing a private key
        @param certificateFileName: Name of a file containing a certificate
        @param sslmethod: The SSL method to use
        """
        self.privateKeyFileName = privateKeyFileName
        self.certificateFileName = certificateFileName
        self.sslmethod = sslmethod
        self._contextFactory = _contextFactory
        self.cacheContext()

    def cacheContext(self):
        if self._context is None:
            ctx = self._contextFactory(self.sslmethod)
            ctx.set_options(SSL.OP_NO_SSLv2)
            ctx.use_certificate_file(self.certificateFileName)
            ctx.use_privatekey_file(self.privateKeyFileName)
            self._context = ctx

    def __getstate__(self):
        d = self.__dict__.copy()
        del d["_context"]
        return d

    def __setstate__(self, state):
        self.__dict__ = state

    def getContext(self):
        """
        Return an SSL context.
        """
        return self._context


@implementer(interfaces.IOpenSSLContextFactory)
@_oldStyle
class ClientContextFactory:
    __doc__ = "A context factory for SSL clients."
    isClient = 1
    method = SSL.SSLv23_METHOD
    _contextFactory = SSL.Context

    def getContext(self):
        ctx = self._contextFactory(self.method)
        ctx.set_options(SSL.OP_NO_SSLv2)
        return ctx


@implementer_only(interfaces.ISSLTransport, *[i for i in implementedBy(tcp.Client) if i != interfaces.ITLSTransport])
class Client(tcp.Client):
    __doc__ = "\n    I am an SSL client.\n    "

    def __init__(self, host, port, bindAddress, ctxFactory, connector, reactor=None):
        self.ctxFactory = ctxFactory
        tcp.Client.__init__(self, host, port, bindAddress, connector, reactor)

    def _connectDone(self):
        self.startTLS(self.ctxFactory)
        self.startWriting()
        tcp.Client._connectDone(self)


@implementer(interfaces.ISSLTransport)
class Server(tcp.Server):
    __doc__ = "\n    I am an SSL server.\n    "

    def __init__(self, *args, **kwargs):
        (tcp.Server.__init__)(self, *args, **kwargs)
        self.startTLS(self.server.ctxFactory)


class Port(tcp.Port):
    __doc__ = "\n    I am an SSL port.\n    "
    transport = Server
    _type = "TLS"

    def __init__(self, port, factory, ctxFactory, backlog=50, interface='', reactor=None):
        tcp.Port.__init__(self, port, factory, backlog, interface, reactor)
        self.ctxFactory = ctxFactory

    def _getLogPrefix(self, factory):
        """
        Override the normal prefix to include an annotation indicating this is a
        port for TLS connections.
        """
        return tcp.Port._getLogPrefix(self, factory) + " (TLS)"


class Connector(tcp.Connector):

    def __init__(self, host, port, factory, contextFactory, timeout, bindAddress, reactor=None):
        self.contextFactory = contextFactory
        tcp.Connector.__init__(self, host, port, factory, timeout, bindAddress, reactor)
        contextFactory.getContext()

    def _makeTransport(self):
        return Client(self.host, self.port, self.bindAddress, self.contextFactory, self, self.reactor)


from twisted.internet._sslverify import KeyPair, DistinguishedName, DN, Certificate, CertificateRequest, PrivateCertificate, OpenSSLAcceptableCiphers as AcceptableCiphers, OpenSSLCertificateOptions as CertificateOptions, OpenSSLDiffieHellmanParameters as DiffieHellmanParameters, platformTrust, OpenSSLDefaultPaths, VerificationError, optionsForClientTLS, ProtocolNegotiationSupport, protocolNegotiationMechanisms, trustRootFromCertificates, TLSVersion
__all__ = [
 'ContextFactory', 'DefaultOpenSSLContextFactory', 'ClientContextFactory', 
 'DistinguishedName', 
 'DN', 
 'Certificate', 'CertificateRequest', 'PrivateCertificate', 
 'KeyPair', 
 'AcceptableCiphers', 
 'CertificateOptions', 'DiffieHellmanParameters', 
 'platformTrust', 'OpenSSLDefaultPaths', 
 'TLSVersion', 
 'VerificationError', 'optionsForClientTLS', 
 'ProtocolNegotiationSupport', 
 'protocolNegotiationMechanisms', 
 'trustRootFromCertificates']
