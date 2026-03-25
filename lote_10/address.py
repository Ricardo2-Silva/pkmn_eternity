# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\internet\address.py
"""
Address objects for network connections.
"""
from __future__ import division, absolute_import
import attr, warnings, os
from zope.interface import implementer
from twisted.internet.interfaces import IAddress
from twisted.python.filepath import _asFilesystemBytes
from twisted.python.filepath import _coerceToFilesystemEncoding
from twisted.python.runtime import platform
from twisted.python.compat import _PY3

@implementer(IAddress)
@attr.s(hash=True)
class IPv4Address(object):
    __doc__ = '\n    An L{IPv4Address} represents the address of an IPv4 socket endpoint.\n\n    @ivar type: A string describing the type of transport, either \'TCP\' or\n        \'UDP\'.\n\n    @ivar host: A string containing a dotted-quad IPv4 address; for example,\n        "127.0.0.1".\n    @type host: C{str}\n\n    @ivar port: An integer representing the port number.\n    @type port: C{int}\n    '
    type = attr.ib(validator=(attr.validators.in_(["TCP", "UDP"])))
    host = attr.ib()
    port = attr.ib()


@implementer(IAddress)
@attr.s(hash=True)
class IPv6Address(object):
    __doc__ = '\n    An L{IPv6Address} represents the address of an IPv6 socket endpoint.\n\n    @ivar type: A string describing the type of transport, either \'TCP\' or\n        \'UDP\'.\n\n    @ivar host: A string containing a colon-separated, hexadecimal formatted\n        IPv6 address; for example, "::1".\n    @type host: C{str}\n\n    @ivar port: An integer representing the port number.\n    @type port: C{int}\n\n    @ivar flowInfo: the IPv6 flow label.  This can be used by QoS routers to\n        identify flows of traffic; you may generally safely ignore it.\n    @type flowInfo: L{int}\n\n    @ivar scopeID: the IPv6 scope identifier - roughly analagous to what\n        interface traffic destined for this address must be transmitted over.\n    @type scopeID: L{int} or L{str}\n    '
    type = attr.ib(validator=(attr.validators.in_(["TCP", "UDP"])))
    host = attr.ib()
    port = attr.ib()
    flowInfo = attr.ib(default=0)
    scopeID = attr.ib(default=0)


@implementer(IAddress)
class _ProcessAddress(object):
    __doc__ = "\n    An L{interfaces.IAddress} provider for process transports.\n    "


@attr.s(hash=True)
@implementer(IAddress)
class HostnameAddress(object):
    __doc__ = '\n    A L{HostnameAddress} represents the address of a L{HostnameEndpoint}.\n\n    @ivar hostname: A hostname byte string; for example, b"example.com".\n    @type hostname: L{bytes}\n\n    @ivar port: An integer representing the port number.\n    @type port: L{int}\n    '
    hostname = attr.ib()
    port = attr.ib()


@attr.s(hash=False, repr=False, eq=False)
@implementer(IAddress)
class UNIXAddress(object):
    __doc__ = "\n    Object representing a UNIX socket endpoint.\n\n    @ivar name: The filename associated with this socket.\n    @type name: C{bytes}\n    "
    name = attr.ib(converter=(attr.converters.optional(_asFilesystemBytes)))
    if getattr(os.path, "samefile", None) is not None:

        def __eq__(self, other):
            """
            Overriding C{attrs} to ensure the os level samefile
            check is done if the name attributes do not match.
            """
            if isinstance(other, self.__class__):
                res = self.name == other.name
            else:
                return False
            if not res:
                if self.name:
                    if other.name:
                        try:
                            return os.path.samefile(self.name, other.name)
                        except OSError:
                            pass
                        except (TypeError, ValueError) as e:
                            if not _PY3:
                                if not platform.isLinux():
                                    raise e

            return res

    else:

        def __eq__(self, other):
            if isinstance(other, self.__class__):
                return self.name == other.name
            else:
                return False

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        else:
            return True

    def __repr__(self):
        name = self.name
        if name:
            name = _coerceToFilesystemEncoding("", self.name)
        return "UNIXAddress(%r)" % (name,)

    def __hash__(self):
        if self.name is None:
            return hash((self.__class__, None))
        try:
            s1 = os.stat(self.name)
            return hash((s1.st_ino, s1.st_dev))
        except OSError:
            return hash(self.name)


class _ServerFactoryIPv4Address(IPv4Address):
    __doc__ = "Backwards compatibility hack. Just like IPv4Address in practice."

    def __eq__(self, other):
        if isinstance(other, tuple):
            warnings.warn("IPv4Address.__getitem__ is deprecated.  Use attributes instead.", category=DeprecationWarning,
              stacklevel=2)
            return (
             self.host, self.port) == other
        else:
            if isinstance(other, IPv4Address):
                a = (
                 self.type, self.host, self.port)
                b = (other.type, other.host, other.port)
                return a == b
            return False
