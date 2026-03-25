# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\internet\error.py
"""
Exceptions and errors for use in twisted.internet modules.
"""
from __future__ import division, absolute_import
import socket
from twisted.python import deprecate
from incremental import Version

class BindError(Exception):
    __doc__ = "An error occurred binding to an interface"

    def __str__(self):
        s = self.__doc__
        if self.args:
            s = "%s: %s" % (s, " ".join(self.args))
        s = "%s." % s
        return s


class CannotListenError(BindError):
    __doc__ = "\n    This gets raised by a call to startListening, when the object cannotstart\n    listening.\n\n    @ivar interface: the interface I tried to listen on\n    @ivar port: the port I tried to listen on\n    @ivar socketError: the exception I got when I tried to listen\n    @type socketError: L{socket.error}\n    "

    def __init__(self, interface, port, socketError):
        BindError.__init__(self, interface, port, socketError)
        self.interface = interface
        self.port = port
        self.socketError = socketError

    def __str__(self):
        iface = self.interface or "any"
        return "Couldn't listen on %s:%s: %s." % (iface, self.port,
         self.socketError)


class MulticastJoinError(Exception):
    __doc__ = "\n    An attempt to join a multicast group failed.\n    "


class MessageLengthError(Exception):
    __doc__ = "Message is too long to send"

    def __str__(self):
        s = self.__doc__
        if self.args:
            s = "%s: %s" % (s, " ".join(self.args))
        s = "%s." % s
        return s


class DNSLookupError(IOError):
    __doc__ = "DNS lookup failed"

    def __str__(self):
        s = self.__doc__
        if self.args:
            s = "%s: %s" % (s, " ".join(self.args))
        s = "%s." % s
        return s


class ConnectInProgressError(Exception):
    __doc__ = "A connect operation was started and isn't done yet."


class ConnectError(Exception):
    __doc__ = "An error occurred while connecting"

    def __init__(self, osError=None, string=''):
        self.osError = osError
        Exception.__init__(self, string)

    def __str__(self):
        s = self.__doc__ or self.__class__.__name__
        if self.osError:
            s = "%s: %s" % (s, self.osError)
        if self.args[0]:
            s = "%s: %s" % (s, self.args[0])
        s = "%s." % s
        return s


class ConnectBindError(ConnectError):
    __doc__ = "Couldn't bind"


class UnknownHostError(ConnectError):
    __doc__ = "Hostname couldn't be looked up"


class NoRouteError(ConnectError):
    __doc__ = "No route to host"


class ConnectionRefusedError(ConnectError):
    __doc__ = "Connection was refused by other side"


class TCPTimedOutError(ConnectError):
    __doc__ = "TCP connection timed out"


class BadFileError(ConnectError):
    __doc__ = "File used for UNIX socket is no good"


class ServiceNameUnknownError(ConnectError):
    __doc__ = "Service name given as port is unknown"


class UserError(ConnectError):
    __doc__ = "User aborted connection"


class TimeoutError(UserError):
    __doc__ = "User timeout caused connection failure"


class SSLError(ConnectError):
    __doc__ = "An SSL error occurred"


class VerifyError(Exception):
    __doc__ = "Could not verify something that was supposed to be signed.\n    "


class PeerVerifyError(VerifyError):
    __doc__ = "The peer rejected our verify error.\n    "


class CertificateError(Exception):
    __doc__ = "\n    We did not find a certificate where we expected to find one.\n    "


try:
    import errno
    errnoMapping = {(errno.ENETUNREACH): NoRouteError, 
     (errno.ECONNREFUSED): ConnectionRefusedError, 
     (errno.ETIMEDOUT): TCPTimedOutError}
    if hasattr(errno, "WSAECONNREFUSED"):
        errnoMapping[errno.WSAECONNREFUSED] = ConnectionRefusedError
        errnoMapping[errno.WSAENETUNREACH] = NoRouteError
except ImportError:
    errnoMapping = {}

def getConnectError(e):
    """Given a socket exception, return connection error."""
    if isinstance(e, Exception):
        args = e.args
    else:
        args = e
    try:
        number, string = args
    except ValueError:
        return ConnectError(string=e)
    else:
        if hasattr(socket, "gaierror") and isinstance(e, socket.gaierror):
            klass = UnknownHostError
        else:
            klass = errnoMapping.get(number, ConnectError)
        return klass(number, string)


class ConnectionClosed(Exception):
    __doc__ = "\n    Connection was closed, whether cleanly or non-cleanly.\n    "


class ConnectionLost(ConnectionClosed):
    __doc__ = "Connection to the other side was lost in a non-clean fashion"

    def __str__(self):
        s = self.__doc__.strip().splitlines()[0]
        if self.args:
            s = "%s: %s" % (s, " ".join(self.args))
        s = "%s." % s
        return s


class ConnectionAborted(ConnectionLost):
    __doc__ = "\n    Connection was aborted locally, using\n    L{twisted.internet.interfaces.ITCPTransport.abortConnection}.\n\n    @since: 11.1\n    "

    def __str__(self):
        s = [
         "Connection was aborted locally using ITCPTransport.abortConnection"]
        if self.args:
            s.append(": ")
            s.append(" ".join(self.args))
        s.append(".")
        return "".join(s)


class ConnectionDone(ConnectionClosed):
    __doc__ = "Connection was closed cleanly"

    def __str__(self):
        s = self.__doc__
        if self.args:
            s = "%s: %s" % (s, " ".join(self.args))
        s = "%s." % s
        return s


class FileDescriptorOverrun(ConnectionLost):
    __doc__ = "\n    A mis-use of L{IUNIXTransport.sendFileDescriptor} caused the connection to\n    be closed.\n\n    Each file descriptor sent using C{sendFileDescriptor} must be associated\n    with at least one byte sent using L{ITransport.write}.  If at any point\n    fewer bytes have been written than file descriptors have been sent, the\n    connection is closed with this exception.\n    "


class ConnectionFdescWentAway(ConnectionLost):
    __doc__ = "Uh"


class AlreadyCalled(ValueError):
    __doc__ = "Tried to cancel an already-called event"

    def __str__(self):
        s = self.__doc__
        if self.args:
            s = "%s: %s" % (s, " ".join(self.args))
        s = "%s." % s
        return s


class AlreadyCancelled(ValueError):
    __doc__ = "Tried to cancel an already-cancelled event"

    def __str__(self):
        s = self.__doc__
        if self.args:
            s = "%s: %s" % (s, " ".join(self.args))
        s = "%s." % s
        return s


class PotentialZombieWarning(Warning):
    __doc__ = "\n    Emitted when L{IReactorProcess.spawnProcess} is called in a way which may\n    result in termination of the created child process not being reported.\n\n    Deprecated in Twisted 10.0.\n    "
    MESSAGE = "spawnProcess called, but the SIGCHLD handler is not installed. This probably means you have not yet called reactor.run, or called reactor.run(installSignalHandler=0). You will probably never see this process finish, and it may become a zombie process."


deprecate.deprecatedModuleAttribute(Version("Twisted", 10, 0, 0), "There is no longer any potential for zombie process.", __name__, "PotentialZombieWarning")

class ProcessDone(ConnectionDone):
    __doc__ = "A process has ended without apparent errors"

    def __init__(self, status):
        Exception.__init__(self, "process finished with exit code 0")
        self.exitCode = 0
        self.signal = None
        self.status = status


class ProcessTerminated(ConnectionLost):
    __doc__ = "\n    A process has ended with a probable error condition\n\n    @ivar exitCode: See L{__init__}\n    @ivar signal: See L{__init__}\n    @ivar status: See L{__init__}\n    "

    def __init__(self, exitCode=None, signal=None, status=None):
        """
        @param exitCode: The exit status of the process.  This is roughly like
            the value you might pass to L{os.exit}.  This is L{None} if the
            process exited due to a signal.
        @type exitCode: L{int} or L{None}

        @param signal: The exit signal of the process.  This is L{None} if the
            process did not exit due to a signal.
        @type signal: L{int} or L{None}

        @param status: The exit code of the process.  This is a platform
            specific combination of the exit code and the exit signal.  See
            L{os.WIFEXITED} and related functions.
        @type status: L{int}
        """
        self.exitCode = exitCode
        self.signal = signal
        self.status = status
        s = "process ended"
        if exitCode is not None:
            s = s + " with exit code %s" % exitCode
        if signal is not None:
            s = s + " by signal %s" % signal
        Exception.__init__(self, s)


class ProcessExitedAlready(Exception):
    __doc__ = "\n    The process has already exited and the operation requested can no longer\n    be performed.\n    "


class NotConnectingError(RuntimeError):
    __doc__ = "The Connector was not connecting when it was asked to stop connecting"

    def __str__(self):
        s = self.__doc__
        if self.args:
            s = "%s: %s" % (s, " ".join(self.args))
        s = "%s." % s
        return s


class NotListeningError(RuntimeError):
    __doc__ = "The Port was not listening when it was asked to stop listening"

    def __str__(self):
        s = self.__doc__
        if self.args:
            s = "%s: %s" % (s, " ".join(self.args))
        s = "%s." % s
        return s


class ReactorNotRunning(RuntimeError):
    __doc__ = "\n    Error raised when trying to stop a reactor which is not running.\n    "


class ReactorNotRestartable(RuntimeError):
    __doc__ = "\n    Error raised when trying to run a reactor which was stopped.\n    "


class ReactorAlreadyRunning(RuntimeError):
    __doc__ = "\n    Error raised when trying to start the reactor multiple times.\n    "


class ReactorAlreadyInstalledError(AssertionError):
    __doc__ = "\n    Could not install reactor because one is already installed.\n    "


class ConnectingCancelledError(Exception):
    __doc__ = "\n    An C{Exception} that will be raised when an L{IStreamClientEndpoint} is\n    cancelled before it connects.\n\n    @ivar address: The L{IAddress} that is the destination of the\n        cancelled L{IStreamClientEndpoint}.\n    "

    def __init__(self, address):
        """
        @param address: The L{IAddress} that is the destination of the
            L{IStreamClientEndpoint} that was cancelled.
        """
        Exception.__init__(self, address)
        self.address = address


class NoProtocol(Exception):
    __doc__ = "\n    An C{Exception} that will be raised when the factory given to a\n    L{IStreamClientEndpoint} returns L{None} from C{buildProtocol}.\n    "


class UnsupportedAddressFamily(Exception):
    __doc__ = "\n    An attempt was made to use a socket with an address family (eg I{AF_INET},\n    I{AF_INET6}, etc) which is not supported by the reactor.\n    "


class UnsupportedSocketType(Exception):
    __doc__ = "\n    An attempt was made to use a socket of a type (eg I{SOCK_STREAM},\n    I{SOCK_DGRAM}, etc) which is not supported by the reactor.\n    "


class AlreadyListened(Exception):
    __doc__ = "\n    An attempt was made to listen on a file descriptor which can only be\n    listened on once.\n    "


class InvalidAddressError(ValueError):
    __doc__ = "\n    An invalid address was specified (i.e. neither IPv4 or IPv6, or expected\n    one and got the other).\n\n    @ivar address: See L{__init__}\n    @ivar message: See L{__init__}\n    "

    def __init__(self, address, message):
        """
        @param address: The address that was provided.
        @type address: L{bytes}
        @param message: A native string of additional information provided by
            the calling context.
        @type address: L{str}
        """
        self.address = address
        self.message = message


__all__ = [
 'BindError', 'CannotListenError', 'MulticastJoinError', 
 'MessageLengthError', 
 'DNSLookupError', 'ConnectInProgressError', 
 'ConnectError', 'ConnectBindError', 
 'UnknownHostError', 'NoRouteError', 
 'ConnectionRefusedError', 'TCPTimedOutError', 
 'BadFileError', 
 'ServiceNameUnknownError', 'UserError', 'TimeoutError', 
 'SSLError', 
 'VerifyError', 'PeerVerifyError', 'CertificateError', 
 'getConnectError', 
 'ConnectionClosed', 'ConnectionLost', 
 'ConnectionDone', 'ConnectionFdescWentAway', 
 'AlreadyCalled', 
 'AlreadyCancelled', 'PotentialZombieWarning', 'ProcessDone', 
 'ProcessTerminated', 
 'ProcessExitedAlready', 'NotConnectingError', 
 'NotListeningError', 'ReactorNotRunning', 
 'ReactorAlreadyRunning', 
 'ReactorAlreadyInstalledError', 'ConnectingCancelledError', 
 'UnsupportedAddressFamily', 
 'UnsupportedSocketType', 'InvalidAddressError']
