# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\logger\_legacy.py
"""
Integration with L{twisted.python.log}.
"""
from zope.interface import implementer
from ._levels import LogLevel
from ._format import formatEvent
from ._observer import ILogObserver
from ._stdlib import fromStdlibLogLevelMapping, StringifiableFromEvent

@implementer(ILogObserver)
class LegacyLogObserverWrapper(object):
    __doc__ = "\n    L{ILogObserver} that wraps an L{twisted.python.log.ILogObserver}.\n\n    Received (new-style) events are modified prior to forwarding to\n    the legacy observer to ensure compatibility with observers that\n    expect legacy events.\n    "

    def __init__(self, legacyObserver):
        """
        @param legacyObserver: a legacy observer to which this observer will
            forward events.
        @type legacyObserver: L{twisted.python.log.ILogObserver}
        """
        self.legacyObserver = legacyObserver

    def __repr__(self):
        return "{self.__class__.__name__}({self.legacyObserver})".format(self=self)

    def __call__(self, event):
        """
        Forward events to the legacy observer after editing them to
        ensure compatibility.

        @param event: an event
        @type event: L{dict}
        """
        if "message" not in event:
            event["message"] = ()
        elif "time" not in event:
            event["time"] = event["log_time"]
        elif "system" not in event:
            event["system"] = event.get("log_system", "-")
        elif "format" not in event:
            if event.get("log_format", None) is not None:
                event["format"] = "%(log_legacy)s"
                event["log_legacy"] = StringifiableFromEvent(event.copy())
                if not isinstance(event["message"], tuple):
                    event["message"] = ()
            if "log_failure" in event:
                if "failure" not in event:
                    event["failure"] = event["log_failure"]
            if "isError" not in event:
                event["isError"] = 1
            if "why" not in event:
                event["why"] = formatEvent(event)
        elif "isError" not in event:
            if event["log_level"] in (LogLevel.error, LogLevel.critical):
                event["isError"] = 1
        else:
            event["isError"] = 0
        self.legacyObserver(event)


def publishToNewObserver(observer, eventDict, textFromEventDict):
    """
    Publish an old-style (L{twisted.python.log}) event to a new-style
    (L{twisted.logger}) observer.

    @note: It's possible that a new-style event was sent to a
        L{LegacyLogObserverWrapper}, and may now be getting sent back to a
        new-style observer.  In this case, it's already a new-style event,
        adapted to also look like an old-style event, and we don't need to
        tweak it again to be a new-style event, hence the checks for
        already-defined new-style keys.

    @param observer: A new-style observer to handle this event.
    @type observer: L{ILogObserver}

    @param eventDict: An L{old-style <twisted.python.log>}, log event.
    @type eventDict: L{dict}

    @param textFromEventDict: callable that can format an old-style event as a
        string.  Passed here rather than imported to avoid circular dependency.
    @type textFromEventDict: 1-arg L{callable} taking L{dict} returning L{str}

    @return: L{None}
    """
    if "log_time" not in eventDict:
        eventDict["log_time"] = eventDict["time"]
    if "log_format" not in eventDict:
        text = textFromEventDict(eventDict)
        if text is not None:
            eventDict["log_text"] = text
            eventDict["log_format"] = "{log_text}"
        if "log_level" not in eventDict:
            if "logLevel" in eventDict:
                try:
                    level = fromStdlibLogLevelMapping[eventDict["logLevel"]]
                except KeyError:
                    level = None

    elif "isError" in eventDict:
        if eventDict["isError"]:
            level = LogLevel.critical
        else:
            level = LogLevel.info
    else:
        level = LogLevel.info
    if level is not None:
        eventDict["log_level"] = level
    if "log_namespace" not in eventDict:
        eventDict["log_namespace"] = "log_legacy"
    if "log_system" not in eventDict:
        if "system" in eventDict:
            eventDict["log_system"] = eventDict["system"]
    observer(eventDict)
