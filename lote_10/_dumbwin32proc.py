# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\internet\_dumbwin32proc.py
"""
http://isometri.cc/strips/gates_in_the_head
"""
from __future__ import absolute_import, division, print_function
import os, sys, win32api, win32con, win32event, win32file, win32pipe, win32process, win32security, pywintypes
PIPE_ATTRS_INHERITABLE = win32security.SECURITY_ATTRIBUTES()
PIPE_ATTRS_INHERITABLE.bInheritHandle = 1
from zope.interface import implementer
from twisted.internet.interfaces import IProcessTransport, IConsumer, IProducer
from twisted.python.compat import items, _PY3
from twisted.python.win32 import quoteArguments
from twisted.python.util import _replaceIf
from twisted.internet import error
from twisted.internet import _pollingfile
from twisted.internet._baseprocess import BaseProcess

@_replaceIf(_PY3, getattr(os, "fsdecode", None))
def _fsdecode(x):
    """
    Decode a string to a L{unicode} representation, passing
    through existing L{unicode} unchanged.

    @param x: The string to be conditionally decoded.
    @type x: L{bytes} or L{unicode}

    @return: L{unicode}
    """
    if isinstance(x, bytes):
        return x.decode(sys.getfilesystemencoding())
    else:
        return x


def debug(msg):
    print(msg)
    sys.stdout.flush()


class _Reaper(_pollingfile._PollableResource):

    def __init__(self, proc):
        self.proc = proc

    def checkWork(self):
        if win32event.WaitForSingleObject(self.proc.hProcess, 0) != win32event.WAIT_OBJECT_0:
            return 0
        else:
            exitCode = win32process.GetExitCodeProcess(self.proc.hProcess)
            self.deactivate()
            self.proc.processEnded(exitCode)
            return 0


def _findShebang(filename):
    """
    Look for a #! line, and return the value following the #! if one exists, or
    None if this file is not a script.

    I don't know if there are any conventions for quoting in Windows shebang
    lines, so this doesn't support any; therefore, you may not pass any
    arguments to scripts invoked as filters.  That's probably wrong, so if
    somebody knows more about the cultural expectations on Windows, please feel
    free to fix.

    This shebang line support was added in support of the CGI tests;
    appropriately enough, I determined that shebang lines are culturally
    accepted in the Windows world through this page::

        http://www.cgi101.com/learn/connect/winxp.html

    @param filename: str representing a filename

    @return: a str representing another filename.
    """
    with open(filename, "rU") as f:
        if f.read(2) == "#!":
            exe = f.readline(1024).strip("\n")
            return exe


def _invalidWin32App(pywinerr):
    """
    Determine if a pywintypes.error is telling us that the given process is
    'not a valid win32 application', i.e. not a PE format executable.

    @param pywinerr: a pywintypes.error instance raised by CreateProcess

    @return: a boolean
    """
    return pywinerr.args[0] == 193


@implementer(IProcessTransport, IConsumer, IProducer)
class Process(_pollingfile._PollingTimer, BaseProcess):
    __doc__ = "\n    A process that integrates with the Twisted event loop.\n\n    If your subprocess is a python program, you need to:\n\n     - Run python.exe with the '-u' command line option - this turns on\n       unbuffered I/O. Buffering stdout/err/in can cause problems, see e.g.\n       http://support.microsoft.com/default.aspx?scid=kb;EN-US;q1903\n\n     - If you don't want Windows messing with data passed over\n       stdin/out/err, set the pipes to be in binary mode::\n\n        import os, sys, mscvrt\n        msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)\n        msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)\n        msvcrt.setmode(sys.stderr.fileno(), os.O_BINARY)\n\n    "
    closedNotifies = 0

    def __init__(self, reactor, protocol, command, args, environment, path):
        """
        Create a new child process.
        """
        _pollingfile._PollingTimer.__init__(self, reactor)
        BaseProcess.__init__(self, protocol)
        sAttrs = win32security.SECURITY_ATTRIBUTES()
        sAttrs.bInheritHandle = 1
        self.hStdoutR, hStdoutW = win32pipe.CreatePipe(sAttrs, 0)
        self.hStderrR, hStderrW = win32pipe.CreatePipe(sAttrs, 0)
        hStdinR, self.hStdinW = win32pipe.CreatePipe(sAttrs, 0)
        win32pipe.SetNamedPipeHandleState(self.hStdinW, win32pipe.PIPE_NOWAIT, None, None)
        StartupInfo = win32process.STARTUPINFO()
        StartupInfo.hStdOutput = hStdoutW
        StartupInfo.hStdError = hStderrW
        StartupInfo.hStdInput = hStdinR
        StartupInfo.dwFlags = win32process.STARTF_USESTDHANDLES
        currentPid = win32api.GetCurrentProcess()
        tmp = win32api.DuplicateHandle(currentPid, self.hStdoutR, currentPid, 0, 0, win32con.DUPLICATE_SAME_ACCESS)
        win32file.CloseHandle(self.hStdoutR)
        self.hStdoutR = tmp
        tmp = win32api.DuplicateHandle(currentPid, self.hStderrR, currentPid, 0, 0, win32con.DUPLICATE_SAME_ACCESS)
        win32file.CloseHandle(self.hStderrR)
        self.hStderrR = tmp
        tmp = win32api.DuplicateHandle(currentPid, self.hStdinW, currentPid, 0, 0, win32con.DUPLICATE_SAME_ACCESS)
        win32file.CloseHandle(self.hStdinW)
        self.hStdinW = tmp
        env = os.environ.copy()
        env.update(environment or {})
        newenv = {}
        for key, value in items(env):
            key = _fsdecode(key)
            value = _fsdecode(value)
            newenv[key] = value

        env = newenv
        args = [_fsdecode(x) for x in args]
        cmdline = quoteArguments(args)
        command = _fsdecode(command) if command else command
        path = _fsdecode(path) if path else path

        def doCreate():
            flags = win32con.CREATE_NO_WINDOW
            self.hProcess, self.hThread, self.pid, dwTid = win32process.CreateProcess(command, cmdline, None, None, 1, flags, env, path, StartupInfo)

        try:
            doCreate()
        except pywintypes.error as pwte:
            if not _invalidWin32App(pwte):
                raise OSError(pwte)
            else:
                sheb = _findShebang(command)
                if sheb is None:
                    raise OSError("%r is neither a Windows executable, nor a script with a shebang line" % command)
                else:
                    args = list(args)
                    args.insert(0, command)
                    cmdline = quoteArguments(args)
                    origcmd = command
                    command = sheb
                    try:
                        doCreate()
                    except pywintypes.error as pwte2:
                        if _invalidWin32App(pwte2):
                            raise OSError("%r has an invalid shebang line: %r is not a valid executable" % (
                             origcmd, sheb))
                        raise OSError(pwte2)

        win32file.CloseHandle(hStderrW)
        win32file.CloseHandle(hStdoutW)
        win32file.CloseHandle(hStdinR)
        self.stdout = _pollingfile._PollableReadPipe(self.hStdoutR, (lambda data: self.proto.childDataReceived(1, data)), self.outConnectionLost)
        self.stderr = _pollingfile._PollableReadPipe(self.hStderrR, (lambda data: self.proto.childDataReceived(2, data)), self.errConnectionLost)
        self.stdin = _pollingfile._PollableWritePipe(self.hStdinW, self.inConnectionLost)
        for pipewatcher in (self.stdout, self.stderr, self.stdin):
            self._addPollableResource(pipewatcher)

        self.proto.makeConnection(self)
        self._addPollableResource(_Reaper(self))

    def signalProcess(self, signalID):
        if self.pid is None:
            raise error.ProcessExitedAlready()
        if signalID in ('INT', 'TERM', 'KILL'):
            win32process.TerminateProcess(self.hProcess, 1)

    def _getReason(self, status):
        if status == 0:
            return error.ProcessDone(status)
        else:
            return error.ProcessTerminated(status)

    def write(self, data):
        """
        Write data to the process' stdin.

        @type data: C{bytes}
        """
        self.stdin.write(data)

    def writeSequence(self, seq):
        """
        Write data to the process' stdin.

        @type data: C{list} of C{bytes}
        """
        self.stdin.writeSequence(seq)

    def writeToChild(self, fd, data):
        """
        Similar to L{ITransport.write} but also allows the file descriptor in
        the child process which will receive the bytes to be specified.

        This implementation is limited to writing to the child's standard input.

        @param fd: The file descriptor to which to write.  Only stdin (C{0}) is
            supported.
        @type fd: C{int}

        @param data: The bytes to write.
        @type data: C{bytes}

        @return: L{None}

        @raise KeyError: If C{fd} is anything other than the stdin file
            descriptor (C{0}).
        """
        if fd == 0:
            self.stdin.write(data)
        else:
            raise KeyError(fd)

    def closeChildFD(self, fd):
        if fd == 0:
            self.closeStdin()
        elif fd == 1:
            self.closeStdout()
        elif fd == 2:
            self.closeStderr()
        else:
            raise NotImplementedError("Only standard-IO file descriptors available on win32")

    def closeStdin(self):
        """Close the process' stdin.
        """
        self.stdin.close()

    def closeStderr(self):
        self.stderr.close()

    def closeStdout(self):
        self.stdout.close()

    def loseConnection(self):
        """
        Close the process' stdout, in and err.
        """
        self.closeStdin()
        self.closeStdout()
        self.closeStderr()

    def outConnectionLost(self):
        self.proto.childConnectionLost(1)
        self.connectionLostNotify()

    def errConnectionLost(self):
        self.proto.childConnectionLost(2)
        self.connectionLostNotify()

    def inConnectionLost(self):
        self.proto.childConnectionLost(0)
        self.connectionLostNotify()

    def connectionLostNotify(self):
        """
        Will be called 3 times, by stdout/err threads and process handle.
        """
        self.closedNotifies += 1
        self.maybeCallProcessEnded()

    def maybeCallProcessEnded(self):
        if self.closedNotifies == 3:
            if self.lostProcess:
                win32file.CloseHandle(self.hProcess)
                win32file.CloseHandle(self.hThread)
                self.hProcess = None
                self.hThread = None
                BaseProcess.maybeCallProcessEnded(self)

    def registerProducer(self, producer, streaming):
        self.stdin.registerProducer(producer, streaming)

    def unregisterProducer(self):
        self.stdin.unregisterProducer()

    def pauseProducing(self):
        self._pause()

    def resumeProducing(self):
        self._unpause()

    def stopProducing(self):
        self.loseConnection()

    def __repr__(self):
        """
        Return a string representation of the process.
        """
        return "<%s pid=%s>" % (self.__class__.__name__, self.pid)
