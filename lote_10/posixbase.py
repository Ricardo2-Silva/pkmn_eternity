# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\internet\posixbase.py
"""
Posix reactor base class
"""
from __future__ import division, absolute_import
import socket, errno, os, sys
from zope.interface import implementer, classImplements
from twisted.internet import error, udp, tcp
from twisted.internet.base import ReactorBase, _SignalReactorMixin
from twisted.internet.main import CONNECTION_DONE, CONNECTION_LOST
from twisted.internet.interfaces import IReactorUNIX, IReactorUNIXDatagram, IReactorTCP, IReactorUDP, IReactorSSL, IReactorSocket, IHalfCloseableDescriptor, IReactorProcess, IReactorMulticast, IReactorFDSet
from twisted.python import log, failure, util
from twisted.python.runtime import platformType, platform
_NO_FILENO = error.ConnectionFdescWentAway("Handler has no fileno method")
_NO_FILEDESC = error.ConnectionFdescWentAway("File descriptor lost")
try:
    from twisted.protocols import tls
except ImportError:
    tls = None
    try:
        from twisted.internet import ssl
    except ImportError:
        ssl = None

unixEnabled = platformType == "posix"
processEnabled = False
if unixEnabled:
    from twisted.internet import fdesc, unix
    from twisted.internet import process, _signals
    processEnabled = True
elif platform.isWindows():
    try:
        import win32process
        processEnabled = True
    except ImportError:
        win32process = None

    class _SocketWaker(log.Logger):
        __doc__ = "\n    The I{self-pipe trick<http://cr.yp.to/docs/selfpipe.html>}, implemented\n    using a pair of sockets rather than pipes (due to the lack of support in\n    select() on Windows for pipes), used to wake up the main loop from\n    another thread.\n    "
        disconnected = 0

        def __init__(self, reactor):
            """Initialize.
        """
            self.reactor = reactor
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            server.bind(('127.0.0.1', 0))
            server.listen(1)
            client.connect(server.getsockname())
            reader, clientaddr = server.accept()
            client.setblocking(0)
            reader.setblocking(0)
            self.r = reader
            self.w = client
            self.fileno = self.r.fileno

        def wakeUp(self):
            """Send a byte to my connection.
        """
            try:
                util.untilConcludes(self.w.send, b'x')
            except socket.error as e:
                if e.args[0] != errno.WSAEWOULDBLOCK:
                    raise

        def doRead(self):
            """Read some data from my connection.
        """
            try:
                self.r.recv(8192)
            except socket.error:
                pass

        def connectionLost(self, reason):
            self.r.close()
            self.w.close()


    class _FDWaker(log.Logger, object):
        __doc__ = "\n    The I{self-pipe trick<http://cr.yp.to/docs/selfpipe.html>}, used to wake\n    up the main loop from another thread or a signal handler.\n\n    L{_FDWaker} is a base class for waker implementations based on\n    writing to a pipe being monitored by the reactor.\n\n    @ivar o: The file descriptor for the end of the pipe which can be\n        written to wake up a reactor monitoring this waker.\n\n    @ivar i: The file descriptor which should be monitored in order to\n        be awoken by this waker.\n    "
        disconnected = 0
        i = None
        o = None

        def __init__(self, reactor):
            """Initialize.
        """
            self.reactor = reactor
            self.i, self.o = os.pipe()
            fdesc.setNonBlocking(self.i)
            fdesc._setCloseOnExec(self.i)
            fdesc.setNonBlocking(self.o)
            fdesc._setCloseOnExec(self.o)
            self.fileno = lambda: self.i

        def doRead(self):
            """
        Read some bytes from the pipe and discard them.
        """
            fdesc.readFromFD(self.fileno(), (lambda data: None))

        def connectionLost(self, reason):
            """Close both ends of my pipe.
        """
            if not hasattr(self, "o"):
                return
            for fd in (self.i, self.o):
                try:
                    os.close(fd)
                except IOError:
                    pass

            del self.i
            del self.o


    class _UnixWaker(_FDWaker):
        __doc__ = "\n    This class provides a simple interface to wake up the event loop.\n\n    This is used by threads or signals to wake up the event loop.\n    "

        def wakeUp(self):
            """Write one byte to the pipe, and flush it.
        """
            if self.o is not None:
                try:
                    util.untilConcludes(os.write, self.o, b'x')
                except OSError as e:
                    if e.errno != errno.EAGAIN:
                        raise


    if platformType == "posix":
        _Waker = _UnixWaker
else:
    _Waker = _SocketWaker

class _SIGCHLDWaker(_FDWaker):
    __doc__ = "\n    L{_SIGCHLDWaker} can wake up a reactor whenever C{SIGCHLD} is\n    received.\n\n    @see: L{twisted.internet._signals}\n    "

    def __init__(self, reactor):
        _FDWaker.__init__(self, reactor)

    def install(self):
        """
        Install the handler necessary to make this waker active.
        """
        _signals.installHandler(self.o)

    def uninstall(self):
        """
        Remove the handler which makes this waker active.
        """
        _signals.installHandler(-1)

    def doRead(self):
        """
        Having woken up the reactor in response to receipt of
        C{SIGCHLD}, reap the process which exited.

        This is called whenever the reactor notices the waker pipe is
        writeable, which happens soon after any call to the C{wakeUp}
        method.
        """
        _FDWaker.doRead(self)
        process.reapAllProcesses()


class _DisconnectSelectableMixin(object):
    __doc__ = "\n    Mixin providing the C{_disconnectSelectable} method.\n    "

    def _disconnectSelectable(self, selectable, why, isRead, faildict={(error.ConnectionDone): (failure.Failure(error.ConnectionDone())), 
 (error.ConnectionLost): (failure.Failure(error.ConnectionLost()))}):
        """
        Utility function for disconnecting a selectable.

        Supports half-close notification, isRead should be boolean indicating
        whether error resulted from doRead().
        """
        self.removeReader(selectable)
        f = faildict.get(why.__class__)
        if f:
            if isRead:
                if why.__class__ == error.ConnectionDone:
                    if IHalfCloseableDescriptor.providedBy(selectable):
                        selectable.readConnectionLost(f)
            self.removeWriter(selectable)
            selectable.connectionLost(f)
        else:
            self.removeWriter(selectable)
            selectable.connectionLost(failure.Failure(why))


@implementer(IReactorTCP, IReactorUDP, IReactorMulticast)
class PosixReactorBase(_SignalReactorMixin, _DisconnectSelectableMixin, ReactorBase):
    __doc__ = "\n    A basis for reactors that use file descriptors.\n\n    @ivar _childWaker: L{None} or a reference to the L{_SIGCHLDWaker}\n        which is used to properly notice child process termination.\n    "
    _wakerFactory = _Waker

    def installWaker(self):
        """
        Install a `waker' to allow threads and signals to wake up the IO thread.

        We use the self-pipe trick (http://cr.yp.to/docs/selfpipe.html) to wake
        the reactor. On Windows we use a pair of sockets.
        """
        if not self.waker:
            self.waker = self._wakerFactory(self)
            self._internalReaders.add(self.waker)
            self.addReader(self.waker)

    _childWaker = None

    def _handleSignals(self):
        """
        Extend the basic signal handling logic to also support
        handling SIGCHLD to know when to try to reap child processes.
        """
        _SignalReactorMixin._handleSignals(self)
        if platformType == "posix":
            if processEnabled:
                if not self._childWaker:
                    self._childWaker = _SIGCHLDWaker(self)
                    self._internalReaders.add(self._childWaker)
                    self.addReader(self._childWaker)
                self._childWaker.install()
                process.reapAllProcesses()

    def _uninstallHandler(self):
        """
        If a child waker was created and installed, uninstall it now.

        Since this disables reactor functionality and is only called
        when the reactor is stopping, it doesn't provide any directly
        useful functionality, but the cleanup of reactor-related
        process-global state that it does helps in unit tests
        involving multiple reactors and is generally just a nice
        thing.
        """
        if self._childWaker:
            self._childWaker.uninstall()

    def spawnProcess(self, processProtocol, executable, args=(), env={}, path=None, uid=None, gid=None, usePTY=0, childFDs=None):
        args, env = self._checkProcessArgs(args, env)
        if platformType == "posix":
            if usePTY:
                if childFDs is not None:
                    raise ValueError("Using childFDs is not supported with usePTY=True.")
                return process.PTYProcess(self, executable, args, env, path, processProtocol, uid, gid, usePTY)
            else:
                return process.Process(self, executable, args, env, path, processProtocol, uid, gid, childFDs)
        elif platformType == "win32":
            if uid is not None:
                raise ValueError("Setting UID is unsupported on this platform.")
            else:
                if gid is not None:
                    raise ValueError("Setting GID is unsupported on this platform.")
                else:
                    if usePTY:
                        raise ValueError("The usePTY parameter is not supported on Windows.")
                    if childFDs:
                        raise ValueError("Customizing childFDs is not supported on Windows.")
                if win32process:
                    from twisted.internet._dumbwin32proc import Process
                    return Process(self, processProtocol, executable, args, env, path)
            raise NotImplementedError("spawnProcess not available since pywin32 is not installed.")
        else:
            raise NotImplementedError("spawnProcess only available on Windows or POSIX.")

    def listenUDP(self, port, protocol, interface='', maxPacketSize=8192):
        """Connects a given L{DatagramProtocol} to the given numeric UDP port.

        @returns: object conforming to L{IListeningPort}.
        """
        p = udp.Port(port, protocol, interface, maxPacketSize, self)
        p.startListening()
        return p

    def listenMulticast(self, port, protocol, interface='', maxPacketSize=8192, listenMultiple=False):
        """Connects a given DatagramProtocol to the given numeric UDP port.

        EXPERIMENTAL.

        @returns: object conforming to IListeningPort.
        """
        p = udp.MulticastPort(port, protocol, interface, maxPacketSize, self, listenMultiple)
        p.startListening()
        return p

    def connectUNIX(self, address, factory, timeout=30, checkPID=0):
        assert unixEnabled, "UNIX support is not present"
        c = unix.Connector(address, factory, timeout, self, checkPID)
        c.connect()
        return c

    def listenUNIX(self, address, factory, backlog=50, mode=438, wantPID=0):
        assert unixEnabled, "UNIX support is not present"
        p = unix.Port(address, factory, backlog, mode, self, wantPID)
        p.startListening()
        return p

    def listenUNIXDatagram(self, address, protocol, maxPacketSize=8192, mode=438):
        """
        Connects a given L{DatagramProtocol} to the given path.

        EXPERIMENTAL.

        @returns: object conforming to L{IListeningPort}.
        """
        assert unixEnabled, "UNIX support is not present"
        p = unix.DatagramPort(address, protocol, maxPacketSize, mode, self)
        p.startListening()
        return p

    def connectUNIXDatagram(self, address, protocol, maxPacketSize=8192, mode=438, bindAddress=None):
        """
        Connects a L{ConnectedDatagramProtocol} instance to a path.

        EXPERIMENTAL.
        """
        assert unixEnabled, "UNIX support is not present"
        p = unix.ConnectedDatagramPort(address, protocol, maxPacketSize, mode, bindAddress, self)
        p.startListening()
        return p

    if unixEnabled:
        _supportedAddressFamilies = (socket.AF_INET, socket.AF_INET6, socket.AF_UNIX)
    else:
        _supportedAddressFamilies = (socket.AF_INET, socket.AF_INET6)

    def adoptStreamPort(self, fileDescriptor, addressFamily, factory):
        """
        Create a new L{IListeningPort} from an already-initialized socket.

        This just dispatches to a suitable port implementation (eg from
        L{IReactorTCP}, etc) based on the specified C{addressFamily}.

        @see: L{twisted.internet.interfaces.IReactorSocket.adoptStreamPort}
        """
        if addressFamily not in self._supportedAddressFamilies:
            raise error.UnsupportedAddressFamily(addressFamily)
        elif unixEnabled and addressFamily == socket.AF_UNIX:
            p = unix.Port._fromListeningDescriptor(self, fileDescriptor, factory)
        else:
            p = tcp.Port._fromListeningDescriptor(self, fileDescriptor, addressFamily, factory)
        p.startListening()
        return p

    def adoptStreamConnection(self, fileDescriptor, addressFamily, factory):
        """
        @see:
            L{twisted.internet.interfaces.IReactorSocket.adoptStreamConnection}
        """
        if addressFamily not in self._supportedAddressFamilies:
            raise error.UnsupportedAddressFamily(addressFamily)
        if unixEnabled:
            if addressFamily == socket.AF_UNIX:
                return unix.Server._fromConnectedSocket(fileDescriptor, factory, self)
        return tcp.Server._fromConnectedSocket(fileDescriptor, addressFamily, factory, self)

    def adoptDatagramPort(self, fileDescriptor, addressFamily, protocol, maxPacketSize=8192):
        if addressFamily not in (socket.AF_INET, socket.AF_INET6):
            raise error.UnsupportedAddressFamily(addressFamily)
        p = udp.Port._fromListeningDescriptor(self,
          fileDescriptor, addressFamily, protocol, maxPacketSize=maxPacketSize)
        p.startListening()
        return p

    def listenTCP(self, port, factory, backlog=50, interface=''):
        p = tcp.Port(port, factory, backlog, interface, self)
        p.startListening()
        return p

    def connectTCP(self, host, port, factory, timeout=30, bindAddress=None):
        c = tcp.Connector(host, port, factory, timeout, bindAddress, self)
        c.connect()
        return c

    def connectSSL(self, host, port, factory, contextFactory, timeout=30, bindAddress=None):
        if tls is not None:
            tlsFactory = tls.TLSMemoryBIOFactory(contextFactory, True, factory)
            return self.connectTCP(host, port, tlsFactory, timeout, bindAddress)
        else:
            if ssl is not None:
                c = ssl.Connector(host, port, factory, contextFactory, timeout, bindAddress, self)
                c.connect()
                return c
            assert False, "SSL support is not present"

    def listenSSL(self, port, factory, contextFactory, backlog=50, interface=''):
        if tls is not None:
            tlsFactory = tls.TLSMemoryBIOFactory(contextFactory, False, factory)
            port = self.listenTCP(port, tlsFactory, backlog, interface)
            port._type = "TLS"
            return port
        else:
            if ssl is not None:
                p = ssl.Port(port, factory, contextFactory, backlog, interface, self)
                p.startListening()
                return p
            assert False, "SSL support is not present"

    def _removeAll(self, readers, writers):
        """
        Remove all readers and writers, and list of removed L{IReadDescriptor}s
        and L{IWriteDescriptor}s.

        Meant for calling from subclasses, to implement removeAll, like::

          def removeAll(self):
              return self._removeAll(self._reads, self._writes)

        where C{self._reads} and C{self._writes} are iterables.
        """
        removedReaders = set(readers) - self._internalReaders
        for reader in removedReaders:
            self.removeReader(reader)

        removedWriters = set(writers)
        for writer in removedWriters:
            self.removeWriter(writer)

        return list(removedReaders | removedWriters)


class _PollLikeMixin(object):
    __doc__ = "\n    Mixin for poll-like reactors.\n\n    Subclasses must define the following attributes::\n\n      - _POLL_DISCONNECTED - Bitmask for events indicating a connection was\n        lost.\n      - _POLL_IN - Bitmask for events indicating there is input to read.\n      - _POLL_OUT - Bitmask for events indicating output can be written.\n\n    Must be mixed in to a subclass of PosixReactorBase (for\n    _disconnectSelectable).\n    "

    def _doReadOrWrite(self, selectable, fd, event):
        """
        fd is available for read or write, do the work and raise errors if
        necessary.
        """
        why = None
        inRead = False
        if event & self._POLL_DISCONNECTED:
            if not event & self._POLL_IN:
                if fd in self._reads:
                    inRead = True
                    why = CONNECTION_DONE
                else:
                    why = CONNECTION_LOST
        try:
            if selectable.fileno() == -1:
                why = _NO_FILEDESC
            else:
                if event & self._POLL_IN:
                    why = selectable.doRead()
                    inRead = True
            if not why:
                if event & self._POLL_OUT:
                    why = selectable.doWrite()
                    inRead = False
        except:
            why = sys.exc_info()[1]
            log.err()

        if why:
            self._disconnectSelectable(selectable, why, inRead)


@implementer(IReactorFDSet)
class _ContinuousPolling(_PollLikeMixin, _DisconnectSelectableMixin):
    __doc__ = "\n    Schedule reads and writes based on the passage of time, rather than\n    notification.\n\n    This is useful for supporting polling filesystem files, which C{epoll(7)}\n    does not support.\n\n    The implementation uses L{_PollLikeMixin}, which is a bit hacky, but\n    re-implementing and testing the relevant code yet again is unappealing.\n\n    @ivar _reactor: The L{EPollReactor} that is using this instance.\n\n    @ivar _loop: A C{LoopingCall} that drives the polling, or L{None}.\n\n    @ivar _readers: A C{set} of C{FileDescriptor} objects that should be read\n        from.\n\n    @ivar _writers: A C{set} of C{FileDescriptor} objects that should be\n        written to.\n    "
    _POLL_DISCONNECTED = 1
    _POLL_IN = 2
    _POLL_OUT = 4

    def __init__(self, reactor):
        self._reactor = reactor
        self._loop = None
        self._readers = set()
        self._writers = set()

    def _checkLoop(self):
        """
        Start or stop a C{LoopingCall} based on whether there are readers and
        writers.
        """
        if self._readers or self._writers:
            if self._loop is None:
                from twisted.internet.task import LoopingCall, _EPSILON
                self._loop = LoopingCall(self.iterate)
                self._loop.clock = self._reactor
                self._loop.start(_EPSILON, now=False)
        elif self._loop:
            self._loop.stop()
            self._loop = None

    def iterate(self):
        """
        Call C{doRead} and C{doWrite} on all readers and writers respectively.
        """
        for reader in list(self._readers):
            self._doReadOrWrite(reader, reader, self._POLL_IN)

        for writer in list(self._writers):
            self._doReadOrWrite(writer, writer, self._POLL_OUT)

    def addReader(self, reader):
        """
        Add a C{FileDescriptor} for notification of data available to read.
        """
        self._readers.add(reader)
        self._checkLoop()

    def addWriter(self, writer):
        """
        Add a C{FileDescriptor} for notification of data available to write.
        """
        self._writers.add(writer)
        self._checkLoop()

    def removeReader(self, reader):
        """
        Remove a C{FileDescriptor} from notification of data available to read.
        """
        try:
            self._readers.remove(reader)
        except KeyError:
            return
        else:
            self._checkLoop()

    def removeWriter(self, writer):
        """
        Remove a C{FileDescriptor} from notification of data available to
        write.
        """
        try:
            self._writers.remove(writer)
        except KeyError:
            return
        else:
            self._checkLoop()

    def removeAll(self):
        """
        Remove all readers and writers.
        """
        result = list(self._readers | self._writers)
        self._readers.clear()
        self._writers.clear()
        return result

    def getReaders(self):
        """
        Return a list of the readers.
        """
        return list(self._readers)

    def getWriters(self):
        """
        Return a list of the writers.
        """
        return list(self._writers)

    def isReading(self, fd):
        """
        Checks if the file descriptor is currently being observed for read
        readiness.

        @param fd: The file descriptor being checked.
        @type fd: L{twisted.internet.abstract.FileDescriptor}
        @return: C{True} if the file descriptor is being observed for read
            readiness, C{False} otherwise.
        @rtype: C{bool}
        """
        return fd in self._readers

    def isWriting(self, fd):
        """
        Checks if the file descriptor is currently being observed for write
        readiness.

        @param fd: The file descriptor being checked.
        @type fd: L{twisted.internet.abstract.FileDescriptor}
        @return: C{True} if the file descriptor is being observed for write
            readiness, C{False} otherwise.
        @rtype: C{bool}
        """
        return fd in self._writers


if tls is not None or ssl is not None:
    classImplements(PosixReactorBase, IReactorSSL)
if unixEnabled:
    classImplements(PosixReactorBase, IReactorUNIX, IReactorUNIXDatagram)
if processEnabled:
    classImplements(PosixReactorBase, IReactorProcess)
if getattr(socket, "fromfd", None) is not None:
    classImplements(PosixReactorBase, IReactorSocket)
__all__ = ["PosixReactorBase"]
