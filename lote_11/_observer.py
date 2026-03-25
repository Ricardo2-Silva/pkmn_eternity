# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\logger\_observer.py
"""
Basic log observers.
"""
from zope.interface import Interface, implementer
from twisted.python.failure import Failure
from ._logger import Logger
OBSERVER_DISABLED = "Temporarily disabling observer {observer} due to exception: {log_failure}"

class ILogObserver(Interface):
    __doc__ = "\n    An observer which can handle log events.\n\n    Unlike most interfaces within Twisted, an L{ILogObserver} I{must be\n    thread-safe}.  Log observers may be called indiscriminately from many\n    different threads, as any thread may wish to log a message at any time.\n    "

    def __call__(event):
        """
        Log an event.

        @type event: C{dict} with (native) C{str} keys.
        @param event: A dictionary with arbitrary keys as defined by the
            application emitting logging events, as well as keys added by the
            logging system.  The logging system reserves the right to set any
            key beginning with the prefix C{"log_"}; applications should not
            use any key so named.  Currently, the following keys are used by
            the logging system in some way, if they are present (they are all
            optional):

                - C{"log_format"}: a PEP-3101-style format string which draws
                  upon the keys in the event as its values, used to format the
                  event for human consumption.

                - C{"log_flattened"}: a dictionary mapping keys derived from
                  the names and format values used in the C{"log_format"}
                  string to their values.  This is used to preserve some
                  structured information for use with
                  L{twisted.logger.extractField}.

                - C{"log_trace"}: A L{list} designed to capture information
                  about which L{LogPublisher}s have observed the event.

                - C{"log_level"}: a L{log level
                  <twisted.logger.LogLevel>} constant, indicating the
                  importance of and audience for this event.

                - C{"log_namespace"}: a namespace for the emitter of the event,
                  given as a unicode string.

                - C{"log_system"}: a string indicating the network event or
                  method call which resulted in the message being logged.
        """
        return


@implementer(ILogObserver)
class LogPublisher(object):
    __doc__ = "\n    I{ILogObserver} that fans out events to other observers.\n\n    Keeps track of a set of L{ILogObserver} objects and forwards\n    events to each.\n    "

    def __init__(self, *observers):
        self._observers = list(observers)
        self.log = Logger(observer=self)

    def addObserver(self, observer):
        """
        Registers an observer with this publisher.

        @param observer: An L{ILogObserver} to add.
        """
        if not callable(observer):
            raise TypeError("Observer is not callable: {0!r}".format(observer))
        if observer not in self._observers:
            self._observers.append(observer)

    def removeObserver(self, observer):
        """
        Unregisters an observer with this publisher.

        @param observer: An L{ILogObserver} to remove.
        """
        try:
            self._observers.remove(observer)
        except ValueError:
            pass

    def __call__(self, event):
        """
        Forward events to contained observers.
        """
        if "log_trace" in event:

            def trace(observer):
                """
                Add tracing information for an observer.

                @param observer: an observer being forwarded to
                @type observer: L{ILogObserver}
                """
                event["log_trace"].append((self, observer))

        else:
            trace = None
        brokenObservers = []
        for observer in self._observers:
            if trace is not None:
                trace(observer)
            try:
                observer(event)
            except Exception:
                brokenObservers.append((observer, Failure()))

        for brokenObserver, failure in brokenObservers:
            errorLogger = self._errorLoggerForObserver(brokenObserver)
            errorLogger.failure(OBSERVER_DISABLED,
              failure=failure,
              observer=brokenObserver)

    def _errorLoggerForObserver(self, observer):
        """
        Create an error-logger based on this logger, which does not contain the
        given bad observer.

        @param observer: The observer which previously had an error.
        @type observer: L{ILogObserver}

        @return: L{None}
        """
        errorPublisher = LogPublisher(*[obs for obs in self._observers if obs is not observer])
        return Logger(observer=errorPublisher)
