# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyasn1\type\useful.py
import datetime
from pyasn1 import error
from pyasn1.compat import dateandtime
from pyasn1.compat import string
from pyasn1.type import char
from pyasn1.type import tag
from pyasn1.type import univ
__all__ = [
 "ObjectDescriptor", "GeneralizedTime", "UTCTime"]
NoValue = univ.NoValue
noValue = univ.noValue

class ObjectDescriptor(char.GraphicString):
    __doc__ = char.GraphicString.__doc__
    tagSet = char.GraphicString.tagSet.tagImplicitly(tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 7))
    typeId = char.GraphicString.getTypeId()


class TimeMixIn(object):
    _yearsDigits = 4
    _hasSubsecond = False
    _optionalMinutes = False
    _shortTZ = False

    class FixedOffset(datetime.tzinfo):
        __doc__ = "Fixed offset in minutes east from UTC."

        def __init__(self, offset=0, name='UTC'):
            self._FixedOffset__offset = datetime.timedelta(minutes=offset)
            self._FixedOffset__name = name

        def utcoffset(self, dt):
            return self._FixedOffset__offset

        def tzname(self, dt):
            return self._FixedOffset__name

        def dst(self, dt):
            return datetime.timedelta(0)

    UTC = FixedOffset()

    @property
    def asDateTimeParse error at or near `JUMP_IF_TRUE_OR_POP' instruction at offset 480_482

    @classmethod
    def fromDateTime(cls, dt):
        """Create |ASN.1| object from a :py:class:`datetime.datetime` object.

        Parameters
        ----------
        dt: :py:class:`datetime.datetime` object
            The `datetime.datetime` object to initialize the |ASN.1| object
            from

        Returns
        -------
        :
            new instance of |ASN.1| value
        """
        text = dt.strftime(cls._yearsDigits == 4 and "%Y%m%d%H%M%S" or "%y%m%d%H%M%S")
        if cls._hasSubsecond:
            text += ".%d" % (dt.microsecond // 1000)
        elif dt.utcoffset():
            seconds = dt.utcoffset().seconds
            if seconds < 0:
                text += "-"
            else:
                text += "+"
            text += "%.2d%.2d" % (seconds // 3600, seconds % 3600)
        else:
            text += "Z"
        return cls(text)


class GeneralizedTime(char.VisibleString, TimeMixIn):
    __doc__ = char.VisibleString.__doc__
    tagSet = char.VisibleString.tagSet.tagImplicitly(tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 24))
    typeId = char.VideotexString.getTypeId()
    _yearsDigits = 4
    _hasSubsecond = True
    _optionalMinutes = True
    _shortTZ = True


class UTCTime(char.VisibleString, TimeMixIn):
    __doc__ = char.VisibleString.__doc__
    tagSet = char.VisibleString.tagSet.tagImplicitly(tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 23))
    typeId = char.VideotexString.getTypeId()
    _yearsDigits = 2
    _hasSubsecond = False
    _optionalMinutes = False
    _shortTZ = False