# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\python\_tzhelper.py
"""
Time zone utilities.
"""
from datetime import datetime, timedelta, tzinfo
__all__ = [
 "FixedOffsetTimeZone",
 "UTC"]

class FixedOffsetTimeZone(tzinfo):
    __doc__ = "\n    Represents a fixed timezone offset (without daylight saving time).\n\n    @ivar name: A L{str} giving the name of this timezone; the name just\n        includes how much time this offset represents.\n\n    @ivar offset: A L{timedelta} giving the amount of time this timezone is\n        offset.\n    "

    def __init__(self, offset, name=None):
        """
        Construct a L{FixedOffsetTimeZone} with a fixed offset.

        @param offset: a delta representing the offset from UTC.
        @type offset: L{timedelta}

        @param name: A name to be given for this timezone.
        @type name: L{str} or L{None}
        """
        self.offset = offset
        self.name = name

    @classmethod
    def fromSignHoursMinutes(cls, sign, hours, minutes):
        """
        Construct a L{FixedOffsetTimeZone} from an offset described by sign
        ('+' or '-'), hours, and minutes.

        @note: For protocol compatibility with AMP, this method never uses 'Z'

        @param sign: A string describing the positive or negative-ness of the
            offset.

        @param hours: The number of hours in the offset.
        @type hours: L{int}

        @param minutes: The number of minutes in the offset
        @type minutes: L{int}

        @return: A time zone with the given offset, and a name describing the
            offset.
        @rtype: L{FixedOffsetTimeZone}
        """
        name = "%s%02i:%02i" % (sign, hours, minutes)
        if sign == "-":
            hours = -hours
            minutes = -minutes
        else:
            if sign != "+":
                raise ValueError("Invalid sign for timezone %r" % (sign,))
        return cls(timedelta(hours=hours, minutes=minutes), name)

    @classmethod
    def fromLocalTimeStamp(cls, timeStamp):
        """
        Create a time zone with a fixed offset corresponding to a time stamp in
        the system's locally configured time zone.

        @param timeStamp: a time stamp
        @type timeStamp: L{int}

        @return: a time zone
        @rtype: L{FixedOffsetTimeZone}
        """
        offset = datetime.fromtimestamp(timeStamp) - datetime.utcfromtimestamp(timeStamp)
        return cls(offset)

    def utcoffset(self, dt):
        """
        Return this timezone's offset from UTC.
        """
        return self.offset

    def dst(self, dt):
        """
        Return a zero C{datetime.timedelta} for the daylight saving time
        offset, since there is never one.
        """
        return timedelta(0)

    def tzname(self, dt):
        """
        Return a string describing this timezone.
        """
        if self.name is not None:
            return self.name
        else:
            dt = datetime.fromtimestamp(0, self)
            return dt.strftime("UTC%z")


UTC = FixedOffsetTimeZone.fromSignHoursMinutes("+", 0, 0)
