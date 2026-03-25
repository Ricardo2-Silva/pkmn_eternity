# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\logger\_stdlib.py
"""
Integration with Python standard library logging.
"""
import logging as stdlibLogging
from zope.interface import implementer
from twisted.python.compat import _PY3, currentframe, unicode
from ._levels import LogLevel
from ._format import formatEvent
from ._observer import ILogObserver
toStdlibLogLevelMapping = {(LogLevel.debug): (stdlibLogging.DEBUG), 
 (LogLevel.info): (stdlibLogging.INFO), 
 (LogLevel.warn): (stdlibLogging.WARNING), 
 (LogLevel.error): (stdlibLogging.ERROR), 
 (LogLevel.critical): (stdlibLogging.CRITICAL)}

def _reverseLogLevelMapping():
    """
    Reverse the above mapping, adding both the numerical keys used above and
    the corresponding string keys also used by python logging.
    @return: the reversed mapping
    """
    mapping = {}
    for logLevel, pyLogLevel in toStdlibLogLevelMapping.items():
        mapping[pyLogLevel] = logLevel
        mapping[stdlibLogging.getLevelName(pyLogLevel)] = logLevel

    return mapping


fromStdlibLogLevelMapping = _reverseLogLevelMapping()

@implementer(ILogObserver)
class STDLibLogObserver(object):
    __doc__ = "\n    Log observer that writes to the python standard library's C{logging}\n    module.\n\n    @note: Warning: specific logging configurations (example: network) can lead\n        to this observer blocking.  Nothing is done here to prevent that, so be\n        sure to not to configure the standard library logging module to block\n        when used in conjunction with this module: code within Twisted, such as\n        twisted.web, assumes that logging does not block.\n\n    @cvar defaultStackDepth: This is the default number of frames that it takes\n        to get from L{STDLibLogObserver} through the logging module, plus one;\n        in other words, the number of frames if you were to call a\n        L{STDLibLogObserver} directly.  This is useful to use as an offset for\n        the C{stackDepth} parameter to C{__init__}, to add frames for other\n        publishers.\n    "
    defaultStackDepth = 4

    def __init__(self, name="twisted", stackDepth=defaultStackDepth):
        """
        @param loggerName: logger identifier.
        @type loggerName: C{str}

        @param stackDepth: The depth of the stack to investigate for caller
            metadata.
        @type stackDepth: L{int}
        """
        self.logger = stdlibLogging.getLogger(name)
        self.logger.findCaller = self._findCaller
        self.stackDepth = stackDepth

    def _findCaller(self, stackInfo=False, stackLevel=1):
        """
        Based on the stack depth passed to this L{STDLibLogObserver}, identify
        the calling function.

        @param stackInfo: Whether or not to construct stack information.
            (Currently ignored.)
        @type stackInfo: L{bool}

        @param stackLevel: The number of stack frames to skip when determining
            the caller (currently ignored; use stackDepth on the instance).
        @type stackLevel: L{int}

        @return: Depending on Python version, either a 3-tuple of (filename,
            lineno, name) or a 4-tuple of that plus stack information.
        @rtype: L{tuple}
        """
        f = currentframe(self.stackDepth)
        co = f.f_code
        if _PY3:
            extra = (None, )
        else:
            extra = ()
        return (
         co.co_filename, f.f_lineno, co.co_name) + extra

    def __call__(self, event):
        """
        Format an event and bridge it to Python logging.
        """
        level = event.get("log_level", LogLevel.info)
        failure = event.get("log_failure")
        if failure is None:
            excInfo = None
        else:
            excInfo = (
             failure.type, failure.value, failure.getTracebackObject())
        stdlibLevel = toStdlibLogLevelMapping.get(level, stdlibLogging.INFO)
        self.logger.log(stdlibLevel,
          (StringifiableFromEvent(event)), exc_info=excInfo)


class StringifiableFromEvent(object):
    __doc__ = "\n    An object that implements C{__str__()} in order to defer the work of\n    formatting until it's converted into a C{str}.\n    "

    def __init__(self, event):
        """
        @param event: An event.
        @type event: L{dict}
        """
        self.event = event

    def __unicode__(self):
        return formatEvent(self.event)

    def __bytes__(self):
        return unicode(self).encode("utf-8")

    if _PY3:
        __str__ = __unicode__
    else:
        __str__ = __bytes__
