# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\internet\process.py
"""
UNIX Process management.

Do NOT use this module directly - use reactor.spawnProcess() instead.

Maintainer: Itamar Shtull-Trauring
"""
from __future__ import division, absolute_import, print_function
from twisted.python.runtime import platform
if platform.isWindows():
    raise ImportError("twisted.internet.process does not work on Windows. Use the reactor.spawnProcess() API instead.")
import errno, gc, os, io, signal, stat, sys, traceback
try:
    import pty
except ImportError:
    pty = None

try:
    import fcntl, termios
except ImportError:
    fcntl = None

from zope.interface import implementer
from twisted.python import log, failure
from twisted.python.util import switchUID
from twisted.python.compat import items, range, _PY3
from twisted.internet import fdesc, abstract, error
from twisted.internet.main import CONNECTION_LOST, CONNECTION_DONE
from twisted.internet._baseprocess import BaseProcess
from twisted.internet.interfaces import IProcessTransport
ProcessExitedAlready = error.ProcessExitedAlready
reapProcessHandlers = {}

def reapAllProcesses():
    """
    Reap all registered processes.
    """
    for process in list(reapProcessHandlers.values()):
        process.reapProcess()


def registerReapProcessHandler(pid, process):
    """
    Register a process handler for the given pid, in case L{reapAllProcesses}
    is called.

    @param pid: the pid of the process.
    @param process: a process handler.
    """
    if pid in reapProcessHandlers:
        raise RuntimeError("Try to register an already registered process.")
    else:
        try:
            auxPID, status = os.waitpid(pid, os.WNOHANG)
        except:
            log.msg("Failed to reap %d:" % pid)
            log.err()
            auxPID = None

        if auxPID:
            process.processEnded(status)
        else:
            reapProcessHandlers[pid] = process


def unregisterReapProcessHandler(pid, process):
    """
    Unregister a process handler previously registered with
    L{registerReapProcessHandler}.
    """
    if not (pid in reapProcessHandlers and reapProcessHandlers[pid] == process):
        raise RuntimeError("Try to unregister a process not registered.")
    del reapProcessHandlers[pid]


class ProcessWriter(abstract.FileDescriptor):
    __doc__ = "\n    (Internal) Helper class to write into a Process's input pipe.\n\n    I am a helper which describes a selectable asynchronous writer to a\n    process's input pipe, including stdin.\n\n    @ivar enableReadHack: A flag which determines how readability on this\n        write descriptor will be handled.  If C{True}, then readability may\n        indicate the reader for this write descriptor has been closed (ie,\n        the connection has been lost).  If C{False}, then readability events\n        are ignored.\n    "
    connected = 1
    ic = 0
    enableReadHack = False

    def __init__(self, reactor, proc, name, fileno, forceReadHack=False):
        """
        Initialize, specifying a Process instance to connect to.
        """
        abstract.FileDescriptor.__init__(self, reactor)
        fdesc.setNonBlocking(fileno)
        self.proc = proc
        self.name = name
        self.fd = fileno
        if not stat.S_ISFIFO(os.fstat(self.fileno()).st_mode):
            self.enableReadHack = False
        elif forceReadHack:
            self.enableReadHack = True
        else:
            try:
                os.read(self.fileno(), 0)
            except OSError:
                self.enableReadHack = True

        if self.enableReadHack:
            self.startReading()

    def fileno(self):
        """
        Return the fileno() of my process's stdin.
        """
        return self.fd

    def writeSomeData(self, data):
        """
        Write some data to the open process.
        """
        rv = fdesc.writeToFD(self.fd, data)
        if rv == len(data):
            if self.enableReadHack:
                self.startReading()
        return rv

    def write(self, data):
        self.stopReading()
        abstract.FileDescriptor.write(self, data)

    def doRead(self):
        """
        The only way a write pipe can become "readable" is at EOF, because the
        child has closed it, and we're using a reactor which doesn't
        distinguish between readable and closed (such as the select reactor).

        Except that's not true on linux < 2.6.11. It has the following
        characteristics: write pipe is completely empty => POLLOUT (writable in
        select), write pipe is not completely empty => POLLIN (readable in
        select), write pipe's reader closed => POLLIN|POLLERR (readable and
        writable in select)

        That's what this funky code is for. If linux was not broken, this
        function could be simply "return CONNECTION_LOST".
        """
        if self.enableReadHack:
            return CONNECTION_LOST
        self.stopReading()

    def connectionLost(self, reason):
        """
        See abstract.FileDescriptor.connectionLost.
        """
        fdesc.setBlocking(self.fd)
        abstract.FileDescriptor.connectionLost(self, reason)
        self.proc.childConnectionLost(self.name, reason)


class ProcessReader(abstract.FileDescriptor):
    __doc__ = "\n    ProcessReader\n\n    I am a selectable representation of a process's output pipe, such as\n    stdout and stderr.\n    "
    connected = True

    def __init__(self, reactor, proc, name, fileno):
        """
        Initialize, specifying a process to connect to.
        """
        abstract.FileDescriptor.__init__(self, reactor)
        fdesc.setNonBlocking(fileno)
        self.proc = proc
        self.name = name
        self.fd = fileno
        self.startReading()

    def fileno(self):
        """
        Return the fileno() of my process's stderr.
        """
        return self.fd

    def writeSomeData(self, data):
        assert data == b''
        return CONNECTION_LOST

    def doRead(self):
        """
        This is called when the pipe becomes readable.
        """
        return fdesc.readFromFD(self.fd, self.dataReceived)

    def dataReceived(self, data):
        self.proc.childDataReceived(self.name, data)

    def loseConnection(self):
        if self.connected:
            if not self.disconnecting:
                self.disconnecting = 1
                self.stopReading()
                self.reactor.callLater(0, self.connectionLost, failure.Failure(CONNECTION_DONE))

    def connectionLost(self, reason):
        """
        Close my end of the pipe, signal the Process (which signals the
        ProcessProtocol).
        """
        abstract.FileDescriptor.connectionLost(self, reason)
        self.proc.childConnectionLost(self.name, reason)


class _BaseProcess(BaseProcess, object):
    __doc__ = "\n    Base class for Process and PTYProcess.\n    "
    status = None
    pid = None

    def reapProcess(self):
        """
        Try to reap a process (without blocking) via waitpid.

        This is called when sigchild is caught or a Process object loses its
        "connection" (stdout is closed) This ought to result in reaping all
        zombie processes, since it will be called twice as often as it needs
        to be.

        (Unfortunately, this is a slightly experimental approach, since
        UNIX has no way to be really sure that your process is going to
        go away w/o blocking.  I don't want to block.)
        """
        try:
            try:
                pid, status = os.waitpid(self.pid, os.WNOHANG)
            except OSError as e:
                if e.errno == errno.ECHILD:
                    pid = None
                else:
                    raise

        except:
            log.msg("Failed to reap %d:" % self.pid)
            log.err()
            pid = None

        if pid:
            self.processEnded(status)
            unregisterReapProcessHandler(pid, self)

    def _getReason(self, status):
        exitCode = sig = None
        if os.WIFEXITED(status):
            exitCode = os.WEXITSTATUS(status)
        else:
            sig = os.WTERMSIG(status)
        if exitCode or sig:
            return error.ProcessTerminated(exitCode, sig, status)
        else:
            return error.ProcessDone(status)

    def signalProcess(self, signalID):
        """
        Send the given signal C{signalID} to the process. It'll translate a
        few signals ('HUP', 'STOP', 'INT', 'KILL', 'TERM') from a string
        representation to its int value, otherwise it'll pass directly the
        value provided

        @type signalID: C{str} or C{int}
        """
        if signalID in ('HUP', 'STOP', 'INT', 'KILL', 'TERM'):
            signalID = getattr(signal, "SIG%s" % (signalID,))
        else:
            if self.pid is None:
                raise ProcessExitedAlready()
            try:
                os.kill(self.pid, signalID)
            except OSError as e:
                if e.errno == errno.ESRCH:
                    raise ProcessExitedAlready()
                else:
                    raise

    def _resetSignalDisposition(self):
        for signalnum in range(1, signal.NSIG):
            if signal.getsignal(signalnum) == signal.SIG_IGN:
                signal.signal(signalnum, signal.SIG_DFL)

    def _fork(self, path, uid, gid, executable, args, environment, **kwargs):
        """
        Fork and then exec sub-process.

        @param path: the path where to run the new process.
        @type path: L{bytes} or L{unicode}
        @param uid: if defined, the uid used to run the new process.
        @type uid: L{int}
        @param gid: if defined, the gid used to run the new process.
        @type gid: L{int}
        @param executable: the executable to run in a new process.
        @type executable: L{str}
        @param args: arguments used to create the new process.
        @type args: L{list}.
        @param environment: environment used for the new process.
        @type environment: L{dict}.
        @param kwargs: keyword arguments to L{_setupChild} method.
        """
        collectorEnabled = gc.isenabled()
        gc.disable()
        try:
            self.pid = os.fork()
        except:
            if collectorEnabled:
                gc.enable()
            raise
        else:
            if self.pid == 0:
                try:
                    sys.settrace(None)
                    (self._setupChild)(**kwargs)
                    self._execChild(path, uid, gid, executable, args, environment)
                except:
                    try:
                        stderr = os.fdopen(2, "wb")
                        msg = "Upon execvpe {0} {1} in environment id {2}\n:".format(executable, str(args), id(environment))
                        if _PY3:
                            stderr = io.TextIOWrapper(stderr, encoding="utf-8")
                        stderr.write(msg)
                        traceback.print_exc(file=stderr)
                        stderr.flush()
                        for fd in range(3):
                            os.close(fd)

                    except:
                        pass

                os._exit(1)
            if collectorEnabled:
                gc.enable()
            self.status = -1

    def _setupChild(self, *args, **kwargs):
        """
        Setup the child process. Override in subclasses.
        """
        raise NotImplementedError()

    def _execChild(self, path, uid, gid, executable, args, environment):
        """
        The exec() which is done in the forked child.
        """
        if path:
            os.chdir(path)
        if uid is not None or gid is not None:
            if uid is None:
                uid = os.geteuid()
            if gid is None:
                gid = os.getegid()
            os.setuid(0)
            os.setgid(0)
            switchUID(uid, gid)
        os.execvpe(executable, args, environment)

    def __repr__(self):
        """
        String representation of a process.
        """
        return "<%s pid=%s status=%s>" % (self.__class__.__name__,
         self.pid, self.status)


class _FDDetector(object):
    __doc__ = "\n    This class contains the logic necessary to decide which of the available\n    system techniques should be used to detect the open file descriptors for\n    the current process. The chosen technique gets monkey-patched into the\n    _listOpenFDs method of this class so that the detection only needs to occur\n    once.\n\n    @ivar listdir: The implementation of listdir to use. This gets overwritten\n        by the test cases.\n    @ivar getpid: The implementation of getpid to use, returns the PID of the\n        running process.\n    @ivar openfile: The implementation of open() to use, by default the Python\n        builtin.\n    "
    listdir = os.listdir
    getpid = os.getpid
    openfile = open

    def __init__(self):
        self._implementations = [
         self._procFDImplementation, self._devFDImplementation,
         self._fallbackFDImplementation]

    def _listOpenFDs(self):
        """
        Return an iterable of file descriptors which I{may} be open in this
        process.

        This will try to return the fewest possible descriptors without missing
        any.
        """
        self._listOpenFDs = self._getImplementation()
        return self._listOpenFDs()

    def _getImplementation(self):
        """
        Pick a method which gives correct results for C{_listOpenFDs} in this
        runtime environment.

        This involves a lot of very platform-specific checks, some of which may
        be relatively expensive.  Therefore the returned method should be saved
        and re-used, rather than always calling this method to determine what it
        is.

        See the implementation for the details of how a method is selected.
        """
        for impl in self._implementations:
            try:
                before = impl()
            except:
                continue

            with self.openfile("/dev/null", "r"):
                after = impl()
            if before != after:
                return impl

        return impl

    def _devFDImplementation(self):
        """
        Simple implementation for systems where /dev/fd actually works.
        See: http://www.freebsd.org/cgi/man.cgi?fdescfs
        """
        dname = "/dev/fd"
        result = [int(fd) for fd in self.listdir(dname)]
        return result

    def _procFDImplementation(self):
        """
        Simple implementation for systems where /proc/pid/fd exists (we assume
        it works).
        """
        dname = "/proc/%d/fd" % (self.getpid(),)
        return [int(fd) for fd in self.listdir(dname)]

    def _fallbackFDImplementation(self):
        """
        Fallback implementation where either the resource module can inform us
        about the upper bound of how many FDs to expect, or where we just guess
        a constant maximum if there is no resource module.

        All possible file descriptors from 0 to that upper bound are returned
        with no attempt to exclude invalid file descriptor values.
        """
        try:
            import resource
        except ImportError:
            maxfds = 1024
        else:
            maxfds = min(1024, resource.getrlimit(resource.RLIMIT_NOFILE)[1])
        return range(maxfds)


detector = _FDDetector()

def _listOpenFDs():
    """
    Use the global detector object to figure out which FD implementation to
    use.
    """
    return detector._listOpenFDs()


@implementer(IProcessTransport)
class Process(_BaseProcess):
    __doc__ = "\n    An operating-system Process.\n\n    This represents an operating-system process with arbitrary input/output\n    pipes connected to it. Those pipes may represent standard input,\n    standard output, and standard error, or any other file descriptor.\n\n    On UNIX, this is implemented using fork(), exec(), pipe()\n    and fcntl(). These calls may not exist elsewhere so this\n    code is not cross-platform. (also, windows can only select\n    on sockets...)\n    "
    debug = False
    debug_child = False
    status = -1
    pid = None
    processWriterFactory = ProcessWriter
    processReaderFactory = ProcessReader

    def __init__(self, reactor, executable, args, environment, path, proto, uid=None, gid=None, childFDs=None):
        """
        Spawn an operating-system process.

        This is where the hard work of disconnecting all currently open
        files / forking / executing the new process happens.  (This is
        executed automatically when a Process is instantiated.)

        This will also run the subprocess as a given user ID and group ID, if
        specified.  (Implementation Note: this doesn't support all the arcane
        nuances of setXXuid on UNIX: it will assume that either your effective
        or real UID is 0.)
        """
        if not proto:
            if not "r" not in childFDs.values():
                raise AssertionError
            else:
                assert "w" not in childFDs.values()
                _BaseProcess.__init__(self, proto)
                self.pipes = {}
                helpers = {}
                if childFDs is None:
                    childFDs = {0:"w", 
                     1:"r", 
                     2:"r"}
            debug = self.debug
            if debug:
                print("childFDs", childFDs)
        else:
            _openedPipes = []

            def pipe():
                r, w = os.pipe()
                _openedPipes.extend([r, w])
                return (r, w)

            fdmap = {}
            try:
                for childFD, target in items(childFDs):
                    if debug:
                        print("[%d]" % childFD, target)
                    if target == "r":
                        readFD, writeFD = pipe()
                        if debug:
                            print("readFD=%d, writeFD=%d" % (readFD, writeFD))
                        fdmap[childFD] = writeFD
                        helpers[childFD] = readFD
                    elif target == "w":
                        readFD, writeFD = pipe()
                        if debug:
                            print("readFD=%d, writeFD=%d" % (readFD, writeFD))
                        fdmap[childFD] = readFD
                        helpers[childFD] = writeFD
                    else:
                        assert type(target) == int, "%r should be an int" % (target,)
                        fdmap[childFD] = target

                if debug:
                    print("fdmap", fdmap)
                if debug:
                    print("helpers", helpers)
                self._fork(path, uid, gid, executable, args, environment, fdmap=fdmap)
            except:
                for pipe in _openedPipes:
                    os.close(pipe)

                raise

        self.proto = proto
        for childFD, parentFD in items(helpers):
            os.close(fdmap[childFD])
            if childFDs[childFD] == "r":
                reader = self.processReaderFactory(reactor, self, childFD, parentFD)
                self.pipes[childFD] = reader
            if childFDs[childFD] == "w":
                writer = self.processWriterFactory(reactor, self, childFD, parentFD,
                  forceReadHack=True)
                self.pipes[childFD] = writer

        try:
            if self.proto is not None:
                self.proto.makeConnection(self)
        except:
            log.err()

        registerReapProcessHandler(self.pid, self)

    def _setupChild(self, fdmap):
        """
        fdmap[childFD] = parentFD

        The child wants to end up with 'childFD' attached to what used to be
        the parent's parentFD. As an example, a bash command run like
        'command 2>&1' would correspond to an fdmap of {0:0, 1:1, 2:1}.
        'command >foo.txt' would be {0:0, 1:os.open('foo.txt'), 2:2}.

        This is accomplished in two steps::

            1. close all file descriptors that aren't values of fdmap.  This
               means 0 .. maxfds (or just the open fds within that range, if
               the platform supports '/proc/<pid>/fd').

            2. for each childFD::

                 - if fdmap[childFD] == childFD, the descriptor is already in
                   place.  Make sure the CLOEXEC flag is not set, then delete
                   the entry from fdmap.

                 - if childFD is in fdmap.values(), then the target descriptor
                   is busy. Use os.dup() to move it elsewhere, update all
                   fdmap[childFD] items that point to it, then close the
                   original. Then fall through to the next case.

                 - now fdmap[childFD] is not in fdmap.values(), and is free.
                   Use os.dup2() to move it to the right place, then close the
                   original.
        """
        debug = self.debug_child
        if debug:
            errfd = sys.stderr
            errfd.write("starting _setupChild\n")
        destList = fdmap.values()
        for fd in _listOpenFDs():
            if fd in destList:
                pass
            elif debug:
                if fd == errfd.fileno():
                    continue
                try:
                    os.close(fd)
                except:
                    pass

        if debug:
            print("fdmap", fdmap, file=errfd)
        for child in sorted(fdmap.keys()):
            target = fdmap[child]
            if target == child:
                if debug:
                    print(("%d already in place" % target), file=errfd)
                fdesc._unsetCloseOnExec(child)
            else:
                if child in fdmap.values():
                    newtarget = os.dup(child)
                    if debug:
                        print(("os.dup(%d) -> %d" % (child, newtarget)), file=errfd)
                    os.close(child)
                    for c, p in items(fdmap):
                        if p == child:
                            fdmap[c] = newtarget

                if debug:
                    print(("os.dup2(%d,%d)" % (target, child)), file=errfd)
                os.dup2(target, child)

        old = []
        for fd in fdmap.values():
            if fd not in old and fd not in fdmap.keys():
                old.append(fd)

        if debug:
            print("old", old, file=errfd)
        for fd in old:
            os.close(fd)

        self._resetSignalDisposition()

    def writeToChild(self, childFD, data):
        self.pipes[childFD].write(data)

    def closeChildFD(self, childFD):
        if childFD in self.pipes:
            self.pipes[childFD].loseConnection()

    def pauseProducing(self):
        for p in self.pipes.itervalues():
            if isinstance(p, ProcessReader):
                p.stopReading()

    def resumeProducing(self):
        for p in self.pipes.itervalues():
            if isinstance(p, ProcessReader):
                p.startReading()

    def closeStdin(self):
        """
        Call this to close standard input on this process.
        """
        self.closeChildFD(0)

    def closeStdout(self):
        self.closeChildFD(1)

    def closeStderr(self):
        self.closeChildFD(2)

    def loseConnection(self):
        self.closeStdin()
        self.closeStderr()
        self.closeStdout()

    def write(self, data):
        """
        Call this to write to standard input on this process.

        NOTE: This will silently lose data if there is no standard input.
        """
        if 0 in self.pipes:
            self.pipes[0].write(data)

    def registerProducer(self, producer, streaming):
        """
        Call this to register producer for standard input.

        If there is no standard input producer.stopProducing() will
        be called immediately.
        """
        if 0 in self.pipes:
            self.pipes[0].registerProducer(producer, streaming)
        else:
            producer.stopProducing()

    def unregisterProducer(self):
        """
        Call this to unregister producer for standard input."""
        if 0 in self.pipes:
            self.pipes[0].unregisterProducer()

    def writeSequence(self, seq):
        """
        Call this to write to standard input on this process.

        NOTE: This will silently lose data if there is no standard input.
        """
        if 0 in self.pipes:
            self.pipes[0].writeSequence(seq)

    def childDataReceived(self, name, data):
        self.proto.childDataReceived(name, data)

    def childConnectionLost(self, childFD, reason):
        os.close(self.pipes[childFD].fileno())
        del self.pipes[childFD]
        try:
            self.proto.childConnectionLost(childFD)
        except:
            log.err()

        self.maybeCallProcessEnded()

    def maybeCallProcessEnded(self):
        if self.pipes:
            return
        if not self.lostProcess:
            self.reapProcess()
            return
        _BaseProcess.maybeCallProcessEnded(self)


@implementer(IProcessTransport)
class PTYProcess(abstract.FileDescriptor, _BaseProcess):
    __doc__ = "\n    An operating-system Process that uses PTY support.\n    "
    status = -1
    pid = None

    def __init__(self, reactor, executable, args, environment, path, proto, uid=None, gid=None, usePTY=None):
        """
        Spawn an operating-system process.

        This is where the hard work of disconnecting all currently open
        files / forking / executing the new process happens.  (This is
        executed automatically when a Process is instantiated.)

        This will also run the subprocess as a given user ID and group ID, if
        specified.  (Implementation Note: this doesn't support all the arcane
        nuances of setXXuid on UNIX: it will assume that either your effective
        or real UID is 0.)
        """
        if pty is None:
            if not isinstance(usePTY, (tuple, list)):
                raise NotImplementedError("cannot use PTYProcess on platforms without the pty module.")
            abstract.FileDescriptor.__init__(self, reactor)
            _BaseProcess.__init__(self, proto)
            if isinstance(usePTY, (tuple, list)):
                masterfd, slavefd, _ = usePTY
        else:
            masterfd, slavefd = pty.openpty()
        try:
            self._fork(path, uid, gid, executable, args, environment, masterfd=masterfd,
              slavefd=slavefd)
        except:
            if not isinstance(usePTY, (tuple, list)):
                os.close(masterfd)
                os.close(slavefd)
            raise

        os.close(slavefd)
        fdesc.setNonBlocking(masterfd)
        self.fd = masterfd
        self.startReading()
        self.connected = 1
        self.status = -1
        try:
            self.proto.makeConnection(self)
        except:
            log.err()

        registerReapProcessHandler(self.pid, self)

    def _setupChild(self, masterfd, slavefd):
        """
        Set up child process after C{fork()} but before C{exec()}.

        This involves:

            - closing C{masterfd}, since it is not used in the subprocess

            - creating a new session with C{os.setsid}

            - changing the controlling terminal of the process (and the new
              session) to point at C{slavefd}

            - duplicating C{slavefd} to standard input, output, and error

            - closing all other open file descriptors (according to
              L{_listOpenFDs})

            - re-setting all signal handlers to C{SIG_DFL}

        @param masterfd: The master end of a PTY file descriptors opened with
            C{openpty}.
        @type masterfd: L{int}

        @param slavefd: The slave end of a PTY opened with C{openpty}.
        @type slavefd: L{int}
        """
        os.close(masterfd)
        os.setsid()
        fcntl.ioctl(slavefd, termios.TIOCSCTTY, "")
        for fd in range(3):
            if fd != slavefd:
                os.close(fd)

        os.dup2(slavefd, 0)
        os.dup2(slavefd, 1)
        os.dup2(slavefd, 2)
        for fd in _listOpenFDs():
            if fd > 2:
                try:
                    os.close(fd)
                except:
                    pass

        self._resetSignalDisposition()

    def closeStdin(self):
        return

    def closeStdout(self):
        return

    def closeStderr(self):
        return

    def doRead(self):
        """
        Called when my standard output stream is ready for reading.
        """
        return fdesc.readFromFD(self.fd, (lambda data: self.proto.childDataReceived(1, data)))

    def fileno(self):
        """
        This returns the file number of standard output on this process.
        """
        return self.fd

    def maybeCallProcessEnded(self):
        if self.lostProcess == 2:
            _BaseProcess.maybeCallProcessEnded(self)

    def connectionLost(self, reason):
        """
        I call this to clean up when one or all of my connections has died.
        """
        abstract.FileDescriptor.connectionLost(self, reason)
        os.close(self.fd)
        self.lostProcess += 1
        self.maybeCallProcessEnded()

    def writeSomeData(self, data):
        """
        Write some data to the open process.
        """
        return fdesc.writeToFD(self.fd, data)
