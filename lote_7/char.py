# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyasn1\type\char.py
import sys
from pyasn1 import error
from pyasn1.type import tag
from pyasn1.type import univ
__all__ = [
 'NumericString', 'PrintableString', 'TeletexString', 'T61String', 'VideotexString', 
 'IA5String', 
 'GraphicString', 'VisibleString', 'ISO646String', 
 'GeneralString', 'UniversalString', 
 'BMPString', 'UTF8String']
NoValue = univ.NoValue
noValue = univ.noValue

class AbstractCharacterString(univ.OctetString):
    __doc__ = 'Creates |ASN.1| schema or value object.\n\n    |ASN.1| objects are immutable and duck-type Python 2 :class:`unicode` or Python 3 :class:`str`.\n    When used in octet-stream context, |ASN.1| type assumes "|encoding|" encoding.\n\n    Keyword Args\n    ------------\n    value: :class:`unicode`, :class:`str`, :class:`bytes` or |ASN.1| object\n        unicode object (Python 2) or string (Python 3), alternatively string\n        (Python 2) or bytes (Python 3) representing octet-stream of serialised\n        unicode string (note `encoding` parameter) or |ASN.1| class instance.\n\n    tagSet: :py:class:`~pyasn1.type.tag.TagSet`\n        Object representing non-default ASN.1 tag(s)\n\n    subtypeSpec: :py:class:`~pyasn1.type.constraint.ConstraintsIntersection`\n        Object representing non-default ASN.1 subtype constraint(s)\n\n    encoding: :py:class:`str`\n        Unicode codec ID to encode/decode :class:`unicode` (Python 2) or\n        :class:`str` (Python 3) the payload when |ASN.1| object is used\n        in octet-stream context.\n\n    Raises\n    ------\n    :py:class:`~pyasn1.error.PyAsn1Error`\n        On constraint violation or bad initializer.\n    '
    if sys.version_info[0] <= 2:

        def __str__(self):
            try:
                return self._value.encode(self.encoding)
            except UnicodeEncodeError:
                raise error.PyAsn1Error("Can't encode string '%s' with codec %s" % (self._value, self.encoding))

        def __unicode__(self):
            return unicode(self._value)

        def prettyIn(self, value):
            try:
                if isinstance(value, unicode):
                    return value
                else:
                    if isinstance(value, str):
                        return value.decode(self.encoding)
                    else:
                        if isinstance(value, (tuple, list)):
                            return self.prettyIn("".join([chr(x) for x in value]))
                        if isinstance(value, univ.OctetString):
                            return value.asOctets().decode(self.encoding)
                    return unicode(value)
            except (UnicodeDecodeError, LookupError):
                raise error.PyAsn1Error("Can't decode string '%s' with codec %s" % (value, self.encoding))

        def asOctets(self, padding=True):
            return str(self)

        def asNumbers(self, padding=True):
            return tuple([ord(x) for x in str(self)])

    else:

        def __str__(self):
            return str(self._value)

        def __bytes__(self):
            try:
                return self._value.encode(self.encoding)
            except UnicodeEncodeError:
                raise error.PyAsn1Error("Can't encode string '%s' with codec %s" % (self._value, self.encoding))

        def prettyIn(self, value):
            try:
                if isinstance(value, str):
                    return value
                else:
                    if isinstance(value, bytes):
                        return value.decode(self.encoding)
                    else:
                        if isinstance(value, (tuple, list)):
                            return self.prettyIn(bytes(value))
                        if isinstance(value, univ.OctetString):
                            return value.asOctets().decode(self.encoding)
                    return str(value)
            except (UnicodeDecodeError, LookupError):
                raise error.PyAsn1Error("Can't decode string '%s' with codec %s" % (value, self.encoding))

        def asOctets(self, padding=True):
            return bytes(self)

        def asNumbers(self, padding=True):
            return tuple(bytes(self))

    def prettyOut(self, value):
        return value

    def prettyPrint(self, scope=0):
        value = self.prettyOut(self._value)
        if value is not self._value:
            return value
        else:
            return AbstractCharacterString.__str__(self)

    def __reversed__(self):
        return reversed(self._value)


class NumericString(AbstractCharacterString):
    __doc__ = AbstractCharacterString.__doc__
    tagSet = AbstractCharacterString.tagSet.tagImplicitly(tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 18))
    encoding = "us-ascii"
    typeId = AbstractCharacterString.getTypeId()


class PrintableString(AbstractCharacterString):
    __doc__ = AbstractCharacterString.__doc__
    tagSet = AbstractCharacterString.tagSet.tagImplicitly(tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 19))
    encoding = "us-ascii"
    typeId = AbstractCharacterString.getTypeId()


class TeletexString(AbstractCharacterString):
    __doc__ = AbstractCharacterString.__doc__
    tagSet = AbstractCharacterString.tagSet.tagImplicitly(tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 20))
    encoding = "iso-8859-1"
    typeId = AbstractCharacterString.getTypeId()


class T61String(TeletexString):
    __doc__ = TeletexString.__doc__
    typeId = AbstractCharacterString.getTypeId()


class VideotexString(AbstractCharacterString):
    __doc__ = AbstractCharacterString.__doc__
    tagSet = AbstractCharacterString.tagSet.tagImplicitly(tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 21))
    encoding = "iso-8859-1"
    typeId = AbstractCharacterString.getTypeId()


class IA5String(AbstractCharacterString):
    __doc__ = AbstractCharacterString.__doc__
    tagSet = AbstractCharacterString.tagSet.tagImplicitly(tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 22))
    encoding = "us-ascii"
    typeId = AbstractCharacterString.getTypeId()


class GraphicString(AbstractCharacterString):
    __doc__ = AbstractCharacterString.__doc__
    tagSet = AbstractCharacterString.tagSet.tagImplicitly(tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 25))
    encoding = "iso-8859-1"
    typeId = AbstractCharacterString.getTypeId()


class VisibleString(AbstractCharacterString):
    __doc__ = AbstractCharacterString.__doc__
    tagSet = AbstractCharacterString.tagSet.tagImplicitly(tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 26))
    encoding = "us-ascii"
    typeId = AbstractCharacterString.getTypeId()


class ISO646String(VisibleString):
    __doc__ = VisibleString.__doc__
    typeId = AbstractCharacterString.getTypeId()


class GeneralString(AbstractCharacterString):
    __doc__ = AbstractCharacterString.__doc__
    tagSet = AbstractCharacterString.tagSet.tagImplicitly(tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 27))
    encoding = "iso-8859-1"
    typeId = AbstractCharacterString.getTypeId()


class UniversalString(AbstractCharacterString):
    __doc__ = AbstractCharacterString.__doc__
    tagSet = AbstractCharacterString.tagSet.tagImplicitly(tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 28))
    encoding = "utf-32-be"
    typeId = AbstractCharacterString.getTypeId()


class BMPString(AbstractCharacterString):
    __doc__ = AbstractCharacterString.__doc__
    tagSet = AbstractCharacterString.tagSet.tagImplicitly(tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 30))
    encoding = "utf-16-be"
    typeId = AbstractCharacterString.getTypeId()


class UTF8String(AbstractCharacterString):
    __doc__ = AbstractCharacterString.__doc__
    tagSet = AbstractCharacterString.tagSet.tagImplicitly(tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 12))
    encoding = "utf-8"
    typeId = AbstractCharacterString.getTypeId()
