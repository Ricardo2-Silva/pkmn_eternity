# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\logger\__init__.py
"""
Twisted Logger: Classes and functions to do granular logging.

Example usage in a module C{some.module}::

    from twisted.logger import Logger
    log = Logger()

    def handleData(data):
        log.debug("Got data: {data!r}.", data=data)

Or in a class::

    from twisted.logger import Logger

    class Foo(object):
        log = Logger()

        def oops(self, data):
            self.log.error("Oops! Invalid data from server: {data!r}",
                           data=data)

C{Logger}s have namespaces, for which logging can be configured independently.
Namespaces may be specified by passing in a C{namespace} argument to L{Logger}
when instantiating it, but if none is given, the logger will derive its own
namespace by using the module name of the callable that instantiated it, or, in
the case of a class, by using the fully qualified name of the class.

In the first example above, the namespace would be C{some.module}, and in the
second example, it would be C{some.module.Foo}.

@var globalLogPublisher: The L{LogPublisher} that all L{Logger} instances that
    are not otherwise parameterized will point to by default.
@type globalLogPublisher: L{LogPublisher}

@var globalLogBeginner: The L{LogBeginner} used to activate the main log
    observer, whether it's a log file, or an observer pointing at stderr.
@type globalLogBeginner: L{LogBeginner}
"""
__all__ = [
 'InvalidLogLevelError', 'LogLevel', 
 'formatEvent', 'formatEventAsClassicLogText', 
 'formatTime', 
 'timeFormatRFC3339', 
 'eventAsText', 
 'extractField', 
 'Logger', '_loggerFor', 
 'ILogObserver', 
 'LogPublisher', 
 'LimitedHistoryLogObserver', 
 'FileLogObserver', 'textFileLogObserver', 
 'PredicateResult', 
 'ILogFilterPredicate', 
 'FilteringLogObserver', 'LogLevelFilterPredicate', 
 'STDLibLogObserver', 
 'LoggingFile', 
 'LegacyLogObserverWrapper', 
 'globalLogPublisher', 
 'globalLogBeginner', 'LogBeginner', 
 'eventAsJSON', 'eventFromJSON', 
 'jsonFileLogObserver', 
 'eventsFromJSONLogFile', 
 'capturedLogs']
from ._levels import InvalidLogLevelError, LogLevel
from ._flatten import extractField
from ._format import formatEvent, formatEventAsClassicLogText, formatTime, timeFormatRFC3339, eventAsText
from ._logger import Logger, _loggerFor
from ._observer import ILogObserver, LogPublisher
from ._buffer import LimitedHistoryLogObserver
from ._file import FileLogObserver, textFileLogObserver
from ._filter import PredicateResult, ILogFilterPredicate, FilteringLogObserver, LogLevelFilterPredicate
from ._stdlib import STDLibLogObserver
from ._io import LoggingFile
from ._legacy import LegacyLogObserverWrapper
from ._global import globalLogPublisher, globalLogBeginner, LogBeginner
from ._json import eventAsJSON, eventFromJSON, jsonFileLogObserver, eventsFromJSONLogFile
from ._capture import capturedLogs
