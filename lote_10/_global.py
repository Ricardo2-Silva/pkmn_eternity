# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\logger\_global.py
"""
This module includes process-global state associated with the logging system,
and implementation of logic for managing that global state.
"""
import sys, warnings
from twisted.python.compat import currentframe
from twisted.python.reflect import qual
from ._buffer import LimitedHistoryLogObserver
from ._observer import LogPublisher
from ._filter import FilteringLogObserver, LogLevelFilterPredicate
from ._logger import Logger
from ._format import eventAsText
from ._levels import LogLevel
from ._io import LoggingFile
from ._file import FileLogObserver
MORE_THAN_ONCE_WARNING = "Warning: primary log target selected twice at <{fileNow}:{lineNow}> - previously selected at <{fileThen}:{lineThen}>.  Remove one of the calls to beginLoggingTo."

class LogBeginner(object):
    __doc__ = '\n    A L{LogBeginner} holds state related to logging before logging has begun,\n    and begins logging when told to do so.  Logging "begins" when someone has\n    selected a set of observers, like, for example, a L{FileLogObserver} that\n    writes to a file on disk, or to standard output.\n\n    Applications will not typically need to instantiate this class, except\n    those which intend to initialize the global logging system themselves,\n    which may wish to instantiate this for testing.  The global instance for\n    the current process is exposed as\n    L{twisted.logger.globalLogBeginner}.\n\n    Before logging has begun, a L{LogBeginner} will:\n\n        1. Log any critical messages (e.g.: unhandled exceptions) to the given\n           file-like object.\n\n        2. Save (a limited number of) log events in a\n           L{LimitedHistoryLogObserver}.\n\n    @ivar _initialBuffer: A buffer of messages logged before logging began.\n    @type _initialBuffer: L{LimitedHistoryLogObserver}\n\n    @ivar _publisher: The log publisher passed in to L{LogBeginner}\'s\n        constructor.\n    @type _publisher: L{LogPublisher}\n\n    @ivar _log: The logger used to log messages about the operation of the\n        L{LogBeginner} itself.\n    @type _log: L{Logger}\n\n    @ivar _temporaryObserver: If not L{None}, an L{ILogObserver} that observes\n        events on C{_publisher} for this L{LogBeginner}.\n    @type _temporaryObserver: L{ILogObserver} or L{None}\n\n    @ivar _stdio: An object with C{stderr} and C{stdout} attributes (like the\n        L{sys} module) which will be replaced when redirecting standard I/O.\n    @type _stdio: L{object}\n\n    @cvar _DEFAULT_BUFFER_SIZE: The default size for the initial log events\n        buffer.\n    @type _DEFAULT_BUFFER_SIZE: L{int}\n    '
    _DEFAULT_BUFFER_SIZE = 200

    def __init__(self, publisher, errorStream, stdio, warningsModule, initialBufferSize=None):
        """
        Initialize this L{LogBeginner}.

        @param initialBufferSize: The size of the event buffer into which
            events are collected until C{beginLoggingTo} is called.  Or
            C{None} to use the default size.
        @type initialBufferSize: L{int} or L{types.NoneType}
        """
        if initialBufferSize is None:
            initialBufferSize = self._DEFAULT_BUFFER_SIZE
        self._initialBuffer = LimitedHistoryLogObserver(size=initialBufferSize)
        self._publisher = publisher
        self._log = Logger(observer=publisher)
        self._stdio = stdio
        self._warningsModule = warningsModule
        self._temporaryObserver = LogPublisher(self._initialBuffer, FilteringLogObserver(FileLogObserver(errorStream, (lambda event: eventAsText(event,
          includeTimestamp=False,
          includeSystem=False) + "\n")), [
         LogLevelFilterPredicate(defaultLogLevel=(LogLevel.critical))]))
        publisher.addObserver(self._temporaryObserver)
        self._oldshowwarning = warningsModule.showwarning

    def beginLoggingTo(self, observers, discardBuffer=False, redirectStandardIO=True):
        """
        Begin logging to the given set of observers.  This will:

            1. Add all the observers given in C{observers} to the
               L{LogPublisher} associated with this L{LogBeginner}.

            2. Optionally re-direct standard output and standard error streams
               to the logging system.

            3. Re-play any messages that were previously logged to that
               publisher to the new observers, if C{discardBuffer} is not set.

            4. Stop logging critical errors from the L{LogPublisher} as strings
               to the C{errorStream} associated with this L{LogBeginner}, and
               allow them to be logged normally.

            5. Re-direct warnings from the L{warnings} module associated with
               this L{LogBeginner} to log messages.

        @note: Since a L{LogBeginner} is designed to encapsulate the transition
            between process-startup and log-system-configuration, this method
            is intended to be invoked I{once}.

        @param observers: The observers to register.
        @type observers: iterable of L{ILogObserver}s

        @param discardBuffer: Whether to discard the buffer and not re-play it
            to the added observers.  (This argument is provided mainly for
            compatibility with legacy concerns.)
        @type discardBuffer: L{bool}

        @param redirectStandardIO: If true, redirect standard output and
            standard error to the observers.
        @type redirectStandardIO: L{bool}
        """
        caller = currentframe(1)
        filename, lineno = caller.f_code.co_filename, caller.f_lineno
        for observer in observers:
            self._publisher.addObserver(observer)

        if self._temporaryObserver is not None:
            self._publisher.removeObserver(self._temporaryObserver)
            if not discardBuffer:
                self._initialBuffer.replayTo(self._publisher)
            self._temporaryObserver = None
            self._warningsModule.showwarning = self.showwarning
        else:
            previousFile, previousLine = self._previousBegin
            self._log.warn(MORE_THAN_ONCE_WARNING,
              fileNow=filename,
              lineNow=lineno,
              fileThen=previousFile,
              lineThen=previousLine)
        self._previousBegin = (
         filename, lineno)
        if redirectStandardIO:
            streams = [
             (
              "stdout", LogLevel.info), ("stderr", LogLevel.error)]
        else:
            streams = []
        for stream, level in streams:
            oldStream = getattr(self._stdio, stream)
            loggingFile = LoggingFile(logger=Logger(namespace=stream, observer=(self._publisher)),
              level=level,
              encoding=(getattr(oldStream, "encoding", None)))
            setattr(self._stdio, stream, loggingFile)

    def showwarning(self, message, category, filename, lineno, file=None, line=None):
        """
        Twisted-enabled wrapper around L{warnings.showwarning}.

        If C{file} is L{None}, the default behaviour is to emit the warning to
        the log system, otherwise the original L{warnings.showwarning} Python
        function is called.

        @param message: A warning message to emit.
        @type message: L{str}

        @param category: A warning category to associate with C{message}.
        @type category: L{warnings.Warning}

        @param filename: A file name for the source code file issuing the
            warning.
        @type warning: L{str}

        @param lineno: A line number in the source file where the warning was
            issued.
        @type lineno: L{int}

        @param file: A file to write the warning message to.  If L{None},
            write to L{sys.stderr}.
        @type file: file-like object

        @param line: A line of source code to include with the warning message.
            If L{None}, attempt to read the line from C{filename} and
            C{lineno}.
        @type line: L{str}
        """
        if file is None:
            self._log.warn("{filename}:{lineno}: {category}: {warning}",
              warning=message,
              category=(qual(category)),
              filename=filename,
              lineno=lineno)
        else:
            self._oldshowwarning(message, category, filename, lineno, file, line)


globalLogPublisher = LogPublisher()
globalLogBeginner = LogBeginner(globalLogPublisher, sys.stderr, sys, warnings)
