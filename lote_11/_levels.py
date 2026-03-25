# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\logger\_levels.py
"""
Log levels.
"""
from constantly import NamedConstant, Names

class InvalidLogLevelError(Exception):
    __doc__ = "\n    Someone tried to use a L{LogLevel} that is unknown to the logging system.\n    "

    def __init__(self, level):
        """
        @param level: A log level.
        @type level: L{LogLevel}
        """
        super(InvalidLogLevelError, self).__init__(str(level))
        self.level = level


class LogLevel(Names):
    __doc__ = "\n    Constants describing log levels.\n\n    @cvar debug: Debugging events: Information of use to a developer of the\n        software, not generally of interest to someone running the software\n        unless they are attempting to diagnose a software issue.\n\n    @cvar info: Informational events: Routine information about the status of\n        an application, such as incoming connections, startup of a subsystem,\n        etc.\n\n    @cvar warn: Warning events: Events that may require greater attention than\n        informational events but are not a systemic failure condition, such as\n        authorization failures, bad data from a network client, etc.  Such\n        events are of potential interest to system administrators, and should\n        ideally be phrased in such a way, or documented, so as to indicate an\n        action that an administrator might take to mitigate the warning.\n\n    @cvar error: Error conditions: Events indicating a systemic failure, such\n        as programming errors in the form of unhandled exceptions, loss of\n        connectivity to an external system without which no useful work can\n        proceed, such as a database or API endpoint, or resource exhaustion.\n        Similarly to warnings, errors that are related to operational\n        parameters may be actionable to system administrators and should\n        provide references to resources which an administrator might use to\n        resolve them.\n\n    @cvar critical: Critical failures: Errors indicating systemic failure (ie.\n        service outage), data corruption, imminent data loss, etc. which must\n        be handled immediately.  This includes errors unanticipated by the\n        software, such as unhandled exceptions, wherein the cause and\n        consequences are unknown.\n    "
    debug = NamedConstant()
    info = NamedConstant()
    warn = NamedConstant()
    error = NamedConstant()
    critical = NamedConstant()

    @classmethod
    def levelWithName(cls, name):
        """
        Get the log level with the given name.

        @param name: The name of a log level.
        @type name: L{str} (native string)

        @return: The L{LogLevel} with the specified C{name}.
        @rtype: L{LogLevel}

        @raise InvalidLogLevelError: if the C{name} does not name a valid log
            level.
        """
        try:
            return cls.lookupByName(name)
        except ValueError:
            raise InvalidLogLevelError(name)

    @classmethod
    def _priorityForLevel(cls, level):
        """
        We want log levels to have defined ordering - the order of definition -
        but they aren't value constants (the only value is the name).  This is
        arguably a bug in Twisted, so this is just a workaround for U{until
        this is fixed in some way
        <https://twistedmatrix.com/trac/ticket/6523>}.

        @param level: A log level.
        @type level: L{LogLevel}

        @return: A numeric index indicating priority (lower is higher level).
        @rtype: L{int}
        """
        return cls._levelPriorities[level]


LogLevel._levelPriorities = dict((level, index) for index, level in enumerate(LogLevel.iterconstants()))
