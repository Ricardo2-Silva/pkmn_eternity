# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyasn1\type\univ.py
import math, sys
from pyasn1 import error
from pyasn1.codec.ber import eoo
from pyasn1.compat import binary
from pyasn1.compat import integer
from pyasn1.compat import octets
from pyasn1.type import base
from pyasn1.type import constraint
from pyasn1.type import namedtype
from pyasn1.type import namedval
from pyasn1.type import tag
from pyasn1.type import tagmap
NoValue = base.NoValue
noValue = NoValue()
__all__ = [
 'Integer', 'Boolean', 'BitString', 'OctetString', 'Null', 
 'ObjectIdentifier', 
 'Real', 'Enumerated', 
 'SequenceOfAndSetOfBase', 'SequenceOf', 'SetOf', 
 'SequenceAndSetBase', 
 'Sequence', 'Set', 'Choice', 'Any', 
 'NoValue', 'noValue']

class Integer(base.AbstractSimpleAsn1Item):
    __doc__ = "Create |ASN.1| type or object.\n\n    |ASN.1| objects are immutable and duck-type Python :class:`int` objects.\n\n    Keyword Args\n    ------------\n    value: :class:`int`, :class:`str` or |ASN.1| object\n        Python integer or string literal or |ASN.1| class instance.\n\n    tagSet: :py:class:`~pyasn1.type.tag.TagSet`\n        Object representing non-default ASN.1 tag(s)\n\n    subtypeSpec: :py:class:`~pyasn1.type.constraint.ConstraintsIntersection`\n        Object representing non-default ASN.1 subtype constraint(s)\n\n    namedValues: :py:class:`~pyasn1.type.namedval.NamedValues`\n        Object representing non-default symbolic aliases for numbers\n\n    Raises\n    ------\n    :py:class:`~pyasn1.error.PyAsn1Error`\n        On constraint violation or bad initializer.\n\n    Examples\n    --------\n\n    .. code-block:: python\n\n        class ErrorCode(Integer):\n            '''\n            ASN.1 specification:\n\n            ErrorCode ::=\n                INTEGER { disk-full(1), no-disk(-1),\n                          disk-not-formatted(2) }\n\n            error ErrorCode ::= disk-full\n            '''\n            namedValues = NamedValues(\n                ('disk-full', 1), ('no-disk', -1),\n                ('disk-not-formatted', 2)\n            )\n\n        error = ErrorCode('disk-full')\n    "
    tagSet = tag.initTagSet(tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 2))
    subtypeSpec = constraint.ConstraintsIntersection()
    namedValues = namedval.NamedValues()
    typeId = base.AbstractSimpleAsn1Item.getTypeId()

    def __init__(self, value=noValue, **kwargs):
        if "namedValues" not in kwargs:
            kwargs["namedValues"] = self.namedValues
        (base.AbstractSimpleAsn1Item.__init__)(self, value, **kwargs)

    def __and__(self, value):
        return self.clone(self._value & value)

    def __rand__(self, value):
        return self.clone(value & self._value)

    def __or__(self, value):
        return self.clone(self._value | value)

    def __ror__(self, value):
        return self.clone(value | self._value)

    def __xor__(self, value):
        return self.clone(self._value ^ value)

    def __rxor__(self, value):
        return self.clone(value ^ self._value)

    def __lshift__(self, value):
        return self.clone(self._value << value)

    def __rshift__(self, value):
        return self.clone(self._value >> value)

    def __add__(self, value):
        return self.clone(self._value + value)

    def __radd__(self, value):
        return self.clone(value + self._value)

    def __sub__(self, value):
        return self.clone(self._value - value)

    def __rsub__(self, value):
        return self.clone(value - self._value)

    def __mul__(self, value):
        return self.clone(self._value * value)

    def __rmul__(self, value):
        return self.clone(value * self._value)

    def __mod__(self, value):
        return self.clone(self._value % value)

    def __rmod__(self, value):
        return self.clone(value % self._value)

    def __pow__(self, value, modulo=None):
        return self.clone(pow(self._value, value, modulo))

    def __rpow__(self, value):
        return self.clone(pow(value, self._value))

    def __floordiv__(self, value):
        return self.clone(self._value // value)

    def __rfloordiv__(self, value):
        return self.clone(value // self._value)

    if sys.version_info[0] <= 2:

        def __div__(self, value):
            if isinstance(value, float):
                return Real(self._value / value)
            else:
                return self.clone(self._value / value)

        def __rdiv__(self, value):
            if isinstance(value, float):
                return Real(value / self._value)
            else:
                return self.clone(value / self._value)

    else:

        def __truediv__(self, value):
            return Real(self._value / value)

        def __rtruediv__(self, value):
            return Real(value / self._value)

        def __divmod__(self, value):
            return self.clone(divmod(self._value, value))

        def __rdivmod__(self, value):
            return self.clone(divmod(value, self._value))

        __hash__ = base.AbstractSimpleAsn1Item.__hash__

    def __int__(self):
        return int(self._value)

    if sys.version_info[0] <= 2:

        def __long__(self):
            return long(self._value)

    def __float__(self):
        return float(self._value)

    def __abs__(self):
        return self.clone(abs(self._value))

    def __index__(self):
        return int(self._value)

    def __pos__(self):
        return self.clone(+self._value)

    def __neg__(self):
        return self.clone(-self._value)

    def __invert__(self):
        return self.clone(~self._value)

    def __round__(self, n=0):
        r = round(self._value, n)
        if n:
            return self.clone(r)
        else:
            return r

    def __floor__(self):
        return math.floor(self._value)

    def __ceil__(self):
        return math.ceil(self._value)

    if sys.version_info[0:2] > (2, 5):

        def __trunc__(self):
            return self.clone(math.trunc(self._value))

    def __lt__(self, value):
        return self._value < value

    def __le__(self, value):
        return self._value <= value

    def __eq__(self, value):
        return self._value == value

    def __ne__(self, value):
        return self._value != value

    def __gt__(self, value):
        return self._value > value

    def __ge__(self, value):
        return self._value >= value

    def prettyIn(self, value):
        try:
            return int(value)
        except ValueError:
            try:
                return self.namedValues[value]
            except KeyError:
                raise error.PyAsn1Error("Can't coerce %r into integer: %s" % (value, sys.exc_info()[1]))

    def prettyOut(self, value):
        try:
            return str(self.namedValues[value])
        except KeyError:
            return str(value)

    def getNamedValues(self):
        return self.namedValues


class Boolean(Integer):
    __doc__ = "Create |ASN.1| type or object.\n\n    |ASN.1| objects are immutable and duck-type Python :class:`int` objects.\n\n    Keyword Args\n    ------------\n    value: :class:`int`, :class:`str` or |ASN.1| object\n        Python integer or boolean or string literal or |ASN.1| class instance.\n\n    tagSet: :py:class:`~pyasn1.type.tag.TagSet`\n        Object representing non-default ASN.1 tag(s)\n\n    subtypeSpec: :py:class:`~pyasn1.type.constraint.ConstraintsIntersection`\n        Object representing non-default ASN.1 subtype constraint(s)\n\n    namedValues: :py:class:`~pyasn1.type.namedval.NamedValues`\n        Object representing non-default symbolic aliases for numbers\n\n    Raises\n    ------\n    :py:class:`~pyasn1.error.PyAsn1Error`\n        On constraint violation or bad initializer.\n\n    Examples\n    --------\n    .. code-block:: python\n\n        class RoundResult(Boolean):\n            '''\n            ASN.1 specification:\n\n            RoundResult ::= BOOLEAN\n\n            ok RoundResult ::= TRUE\n            ko RoundResult ::= FALSE\n            '''\n        ok = RoundResult(True)\n        ko = RoundResult(False)\n    "
    tagSet = tag.initTagSet(tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 1))
    subtypeSpec = Integer.subtypeSpec + constraint.SingleValueConstraint(0, 1)
    namedValues = namedval.NamedValues(('False', 0), ('True', 1))
    typeId = Integer.getTypeId()


if sys.version_info[0] < 3:
    SizedIntegerBase = long
else:
    SizedIntegerBase = int

class SizedInteger(SizedIntegerBase):
    bitLength = leadingZeroBits = None

    def setBitLength(self, bitLength):
        self.bitLength = bitLength
        self.leadingZeroBits = max(bitLength - integer.bitLength(self), 0)
        return self

    def __len__(self):
        if self.bitLength is None:
            self.setBitLength(integer.bitLength(self))
        return self.bitLength


class BitString(base.AbstractSimpleAsn1Item):
    __doc__ = "Create |ASN.1| schema or value object.\n\n    |ASN.1| objects are immutable and duck-type both Python :class:`tuple` (as a tuple\n    of bits) and :class:`int` objects.\n\n    Keyword Args\n    ------------\n    value: :class:`int`, :class:`str` or |ASN.1| object\n        Python integer or string literal representing binary or hexadecimal\n        number or sequence of integer bits or |ASN.1| object.\n\n    tagSet: :py:class:`~pyasn1.type.tag.TagSet`\n        Object representing non-default ASN.1 tag(s)\n\n    subtypeSpec: :py:class:`~pyasn1.type.constraint.ConstraintsIntersection`\n        Object representing non-default ASN.1 subtype constraint(s)\n\n    namedValues: :py:class:`~pyasn1.type.namedval.NamedValues`\n        Object representing non-default symbolic aliases for numbers\n\n    binValue: :py:class:`str`\n        Binary string initializer to use instead of the *value*.\n        Example: '10110011'.\n\n    hexValue: :py:class:`str`\n        Hexadecimal string initializer to use instead of the *value*.\n        Example: 'DEADBEEF'.\n\n    Raises\n    ------\n    :py:class:`~pyasn1.error.PyAsn1Error`\n        On constraint violation or bad initializer.\n\n    Examples\n    --------\n    .. code-block:: python\n\n        class Rights(BitString):\n            '''\n            ASN.1 specification:\n\n            Rights ::= BIT STRING { user-read(0), user-write(1),\n                                    group-read(2), group-write(3),\n                                    other-read(4), other-write(5) }\n\n            group1 Rights ::= { group-read, group-write }\n            group2 Rights ::= '0011'B\n            group3 Rights ::= '3'H\n            '''\n            namedValues = NamedValues(\n                ('user-read', 0), ('user-write', 1),\n                ('group-read', 2), ('group-write', 3),\n                ('other-read', 4), ('other-write', 5)\n            )\n\n        group1 = Rights(('group-read', 'group-write'))\n        group2 = Rights('0011')\n        group3 = Rights(0x3)\n    "
    tagSet = tag.initTagSet(tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 3))
    subtypeSpec = constraint.ConstraintsIntersection()
    namedValues = namedval.NamedValues()
    typeId = base.AbstractSimpleAsn1Item.getTypeId()
    defaultBinValue = defaultHexValue = noValue

    def __init__(self, value=noValue, **kwargs):
        if value is noValue:
            if kwargs:
                try:
                    value = self.fromBinaryString((kwargs.pop("binValue")), internalFormat=True)
                except KeyError:
                    pass

                try:
                    value = self.fromHexString((kwargs.pop("hexValue")), internalFormat=True)
                except KeyError:
                    pass

            if value is noValue:
                if self.defaultBinValue is not noValue:
                    value = self.fromBinaryString((self.defaultBinValue), internalFormat=True)
        else:
            if self.defaultHexValue is not noValue:
                value = self.fromHexString((self.defaultHexValue), internalFormat=True)
            if "namedValues" not in kwargs:
                kwargs["namedValues"] = self.namedValues
        (base.AbstractSimpleAsn1Item.__init__)(self, value, **kwargs)

    def __str__(self):
        return self.asBinary()

    def __eq__(self, other):
        other = self.prettyIn(other)
        return self is other or self._value == other and len(self._value) == len(other)

    def __ne__(self, other):
        other = self.prettyIn(other)
        return self._value != other or len(self._value) != len(other)

    def __lt__(self, other):
        other = self.prettyIn(other)
        return len(self._value) < len(other) or len(self._value) == len(other) and self._value < other

    def __le__(self, other):
        other = self.prettyIn(other)
        return len(self._value) <= len(other) or len(self._value) == len(other) and self._value <= other

    def __gt__(self, other):
        other = self.prettyIn(other)
        return len(self._value) > len(other) or len(self._value) == len(other) and self._value > other

    def __ge__(self, other):
        other = self.prettyIn(other)
        return len(self._value) >= len(other) or len(self._value) == len(other) and self._value >= other

    def __len__(self):
        return len(self._value)

    def __getitem__(self, i):
        if i.__class__ is slice:
            return self.clone([self[x] for x in range(*i.indices(len(self)))])
        else:
            length = len(self._value) - 1
            if i > length or i < 0:
                raise IndexError("bit index out of range")
            return self._value >> length - i & 1

    def __iter__(self):
        length = len(self._value)
        while length:
            length -= 1
            yield self._value >> length & 1

    def __reversed__(self):
        return reversed(tuple(self))

    def __add__(self, value):
        value = self.prettyIn(value)
        return self.clone(SizedInteger(self._value << len(value) | value).setBitLength(len(self._value) + len(value)))

    def __radd__(self, value):
        value = self.prettyIn(value)
        return self.clone(SizedInteger(value << len(self._value) | self._value).setBitLength(len(self._value) + len(value)))

    def __mul__(self, value):
        bitString = self._value
        while value > 1:
            bitString <<= len(self._value)
            bitString |= self._value
            value -= 1

        return self.clone(bitString)

    def __rmul__(self, value):
        return self * value

    def __lshift__(self, count):
        return self.clone(SizedInteger(self._value << count).setBitLength(len(self._value) + count))

    def __rshift__(self, count):
        return self.clone(SizedInteger(self._value >> count).setBitLength(max(0, len(self._value) - count)))

    def __int__(self):
        return self._value

    def __float__(self):
        return float(self._value)

    if sys.version_info[0] < 3:

        def __long__(self):
            return self._value

    def asNumbers(self):
        """Get |ASN.1| value as a sequence of 8-bit integers.

        If |ASN.1| object length is not a multiple of 8, result
        will be left-padded with zeros.
        """
        return tuple(octets.octs2ints(self.asOctets()))

    def asOctets(self):
        """Get |ASN.1| value as a sequence of octets.

        If |ASN.1| object length is not a multiple of 8, result
        will be left-padded with zeros.
        """
        return integer.to_bytes((self._value), length=(len(self)))

    def asInteger(self):
        """Get |ASN.1| value as a single integer value.
        """
        return self._value

    def asBinary(self):
        """Get |ASN.1| value as a text string of bits.
        """
        binString = binary.bin(self._value)[2:]
        return "0" * (len(self._value) - len(binString)) + binString

    @classmethod
    def fromHexString(cls, value, internalFormat=False, prepend=None):
        """Create a |ASN.1| object initialized from the hex string.

        Parameters
        ----------
        value: :class:`str`
            Text string like 'DEADBEEF'
        """
        try:
            value = SizedInteger(value, 16).setBitLength(len(value) * 4)
        except ValueError:
            raise error.PyAsn1Error("%s.fromHexString() error: %s" % (cls.__name__, sys.exc_info()[1]))

        if prepend is not None:
            value = SizedInteger(SizedInteger(prepend) << len(value) | value).setBitLength(len(prepend) + len(value))
        if not internalFormat:
            value = cls(value)
        return value

    @classmethod
    def fromBinaryString(cls, value, internalFormat=False, prepend=None):
        """Create a |ASN.1| object initialized from a string of '0' and '1'.

        Parameters
        ----------
        value: :class:`str`
            Text string like '1010111'
        """
        try:
            value = SizedInteger(value or "0", 2).setBitLength(len(value))
        except ValueError:
            raise error.PyAsn1Error("%s.fromBinaryString() error: %s" % (cls.__name__, sys.exc_info()[1]))

        if prepend is not None:
            value = SizedInteger(SizedInteger(prepend) << len(value) | value).setBitLength(len(prepend) + len(value))
        if not internalFormat:
            value = cls(value)
        return value

    @classmethod
    def fromOctetString(cls, value, internalFormat=False, prepend=None, padding=0):
        r"""Create a |ASN.1| object initialized from a string.

        Parameters
        ----------
        value: :class:`str` (Py2) or :class:`bytes` (Py3)
            Text string like '\\x01\\xff' (Py2) or b'\\x01\\xff' (Py3)
        """
        value = SizedInteger(integer.from_bytes(value) >> padding).setBitLength(len(value) * 8 - padding)
        if prepend is not None:
            value = SizedInteger(SizedInteger(prepend) << len(value) | value).setBitLength(len(prepend) + len(value))
        if not internalFormat:
            value = cls(value)
        return value

    def prettyIn(self, value):
        if isinstance(value, SizedInteger):
            return value
        if octets.isStringType(value):
            if not value:
                return SizedInteger(0).setBitLength(0)
            if value[0] == "'":
                if value[-2:] == "'B":
                    return self.fromBinaryString((value[1:-2]), internalFormat=True)
                if value[-2:] == "'H":
                    return self.fromHexString((value[1:-2]), internalFormat=True)
                raise error.PyAsn1Error("Bad BIT STRING value notation %s" % (value,))
            else:
                if self.namedValues and not value.isdigit():
                    names = [x.strip() for x in value.split(",")]
                    try:
                        bitPositions = [self.namedValues[name] for name in names]
                    except KeyError:
                        raise error.PyAsn1Error("unknown bit name(s) in %r" % (names,))

                    rightmostPosition = max(bitPositions)
                    number = 0
                    for bitPosition in bitPositions:
                        number |= 1 << rightmostPosition - bitPosition

                    return SizedInteger(number).setBitLength(rightmostPosition + 1)
                else:
                    if value.startswith("0x"):
                        return self.fromHexString((value[2:]), internalFormat=True)
                    if value.startswith("0b"):
                        return self.fromBinaryString((value[2:]), internalFormat=True)
                    return self.fromBinaryString(value, internalFormat=True)
        else:
            if isinstance(value, (tuple, list)):
                return self.fromBinaryString(("".join([b and "1" or "0" for b in value])), internalFormat=True)
            else:
                if isinstance(value, BitString):
                    return SizedInteger(value).setBitLength(len(value))
                if isinstance(value, intTypes):
                    return SizedInteger(value)
            raise error.PyAsn1Error("Bad BitString initializer type '%s'" % (value,))


try:
    all
except NameError:

    def all(iterable):
        for element in iterable:
            if not element:
                return False

        return True


class OctetString(base.AbstractSimpleAsn1Item):
    __doc__ = 'Create |ASN.1| schema or value object.\n\n    |ASN.1| objects are immutable and duck-type Python 2 :class:`str` or Python 3 :class:`bytes`.\n    When used in Unicode context, |ASN.1| type assumes "|encoding|" serialisation.\n\n    Keyword Args\n    ------------\n    value: :class:`str`, :class:`bytes` or |ASN.1| object\n        string (Python 2) or bytes (Python 3), alternatively unicode object\n        (Python 2) or string (Python 3) representing character string to be\n        serialised into octets (note `encoding` parameter) or |ASN.1| object.\n\n    tagSet: :py:class:`~pyasn1.type.tag.TagSet`\n        Object representing non-default ASN.1 tag(s)\n\n    subtypeSpec: :py:class:`~pyasn1.type.constraint.ConstraintsIntersection`\n        Object representing non-default ASN.1 subtype constraint(s)\n\n    encoding: :py:class:`str`\n        Unicode codec ID to encode/decode :class:`unicode` (Python 2) or\n        :class:`str` (Python 3) the payload when |ASN.1| object is used\n        in text string context.\n\n    binValue: :py:class:`str`\n        Binary string initializer to use instead of the *value*.\n        Example: \'10110011\'.\n\n    hexValue: :py:class:`str`\n        Hexadecimal string initializer to use instead of the *value*.\n        Example: \'DEADBEEF\'.\n\n    Raises\n    ------\n    :py:class:`~pyasn1.error.PyAsn1Error`\n        On constraint violation or bad initializer.\n\n    Examples\n    --------\n    .. code-block:: python\n\n        class Icon(OctetString):\n            \'\'\'\n            ASN.1 specification:\n\n            Icon ::= OCTET STRING\n\n            icon1 Icon ::= \'001100010011001000110011\'B\n            icon2 Icon ::= \'313233\'H\n            \'\'\'\n        icon1 = Icon.fromBinaryString(\'001100010011001000110011\')\n        icon2 = Icon.fromHexString(\'313233\')\n    '
    tagSet = tag.initTagSet(tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 4))
    subtypeSpec = constraint.ConstraintsIntersection()
    typeId = base.AbstractSimpleAsn1Item.getTypeId()
    defaultBinValue = defaultHexValue = noValue
    encoding = "iso-8859-1"

    def __init__(self, value=noValue, **kwargs):
        if kwargs:
            if value is noValue:
                try:
                    value = self.fromBinaryString(kwargs.pop("binValue"))
                except KeyError:
                    pass

                try:
                    value = self.fromHexString(kwargs.pop("hexValue"))
                except KeyError:
                    pass

            if value is noValue:
                if self.defaultBinValue is not noValue:
                    value = self.fromBinaryString(self.defaultBinValue)
        else:
            if self.defaultHexValue is not noValue:
                value = self.fromHexString(self.defaultHexValue)
            if "encoding" not in kwargs:
                kwargs["encoding"] = self.encoding
        (base.AbstractSimpleAsn1Item.__init__)(self, value, **kwargs)

    if sys.version_info[0] <= 2:

        def prettyIn(self, value):
            if isinstance(value, str):
                return value
            elif isinstance(value, unicode):
                try:
                    return value.encode(self.encoding)
                except (LookupError, UnicodeEncodeError):
                    raise error.PyAsn1Error("Can't encode string '%s' with codec %s" % (value, self.encoding))

            elif isinstance(value, (tuple, list)):
                try:
                    return "".join([chr(x) for x in value])
                except ValueError:
                    raise error.PyAsn1Error("Bad %s initializer '%s'" % (self.__class__.__name__, value))

            else:
                return str(value)

        def __str__(self):
            return str(self._value)

        def __unicode__(self):
            try:
                return self._value.decode(self.encoding)
            except UnicodeDecodeError:
                raise error.PyAsn1Error("Can't decode string '%s' with codec %s" % (self._value, self.encoding))

        def asOctets(self):
            return str(self._value)

        def asNumbers(self):
            return tuple([ord(x) for x in self._value])

    else:

        def prettyIn(self, value):
            if isinstance(value, bytes):
                return value
            else:
                if isinstance(value, str):
                    try:
                        return value.encode(self.encoding)
                    except UnicodeEncodeError:
                        raise error.PyAsn1Error("Can't encode string '%s' with '%s' codec" % (value, self.encoding))

                elif isinstance(value, OctetString):
                    return value.asOctets()
                else:
                    if isinstance(value, base.AbstractSimpleAsn1Item):
                        return self.prettyIn(str(value))
                    if isinstance(value, (tuple, list)):
                        return self.prettyIn(bytes(value))
                return bytes(value)

        def __str__(self):
            try:
                return self._value.decode(self.encoding)
            except UnicodeDecodeError:
                raise error.PyAsn1Error("Can't decode string '%s' with '%s' codec at '%s'" % (self._value, self.encoding, self.__class__.__name__))

        def __bytes__(self):
            return bytes(self._value)

        def asOctets(self):
            return bytes(self._value)

        def asNumbers(self):
            return tuple(self._value)

    def prettyOut(self, value):
        return value

    def prettyPrint(self, scope=0):
        value = self.prettyOut(self._value)
        if value is not self._value:
            return value
        numbers = self.asNumbers()
        for x in numbers:
            if x < 32 or x > 126:
                return "0x" + "".join("%.2x" % x for x in numbers)
        else:
            return OctetString.__str__(self)

    @staticmethod
    def fromBinaryString(value):
        """Create a |ASN.1| object initialized from a string of '0' and '1'.

        Parameters
        ----------
        value: :class:`str`
            Text string like '1010111'
        """
        bitNo = 8
        byte = 0
        r = []
        for v in value:
            if bitNo:
                bitNo -= 1
            else:
                bitNo = 7
                r.append(byte)
                byte = 0
            if v in ('0', '1'):
                v = int(v)
            else:
                raise error.PyAsn1Error("Non-binary OCTET STRING initializer %s" % (v,))
            byte |= v << bitNo

        r.append(byte)
        return octets.ints2octs(r)

    @staticmethod
    def fromHexString(value):
        """Create a |ASN.1| object initialized from the hex string.

        Parameters
        ----------
        value: :class:`str`
            Text string like 'DEADBEEF'
        """
        r = []
        p = []
        for v in value:
            if p:
                r.append(int(p + v, 16))
                p = None
            else:
                p = v

        if p:
            r.append(int(p + "0", 16))
        return octets.ints2octs(r)

    def __len__(self):
        return len(self._value)

    def __getitem__(self, i):
        if i.__class__ is slice:
            return self.clone(self._value[i])
        else:
            return self._value[i]

    def __iter__(self):
        return iter(self._value)

    def __contains__(self, value):
        return value in self._value

    def __add__(self, value):
        return self.clone(self._value + self.prettyIn(value))

    def __radd__(self, value):
        return self.clone(self.prettyIn(value) + self._value)

    def __mul__(self, value):
        return self.clone(self._value * value)

    def __rmul__(self, value):
        return self * value

    def __int__(self):
        return int(self._value)

    def __float__(self):
        return float(self._value)

    def __reversed__(self):
        return reversed(self._value)


class Null(OctetString):
    __doc__ = "Create |ASN.1| schema or value object.\n\n    |ASN.1| objects are immutable and duck-type Python :class:`str` objects (always empty).\n\n    Keyword Args\n    ------------\n    value: :class:`str` or :py:class:`~pyasn1.type.univ.Null` object\n        Python empty string literal or any object that evaluates to `False`\n\n    tagSet: :py:class:`~pyasn1.type.tag.TagSet`\n        Object representing non-default ASN.1 tag(s)\n\n    Raises\n    ------\n    :py:class:`~pyasn1.error.PyAsn1Error`\n        On constraint violation or bad initializer.\n\n    Examples\n    --------\n    .. code-block:: python\n\n        class Ack(Null):\n            '''\n            ASN.1 specification:\n\n            Ack ::= NULL\n            '''\n        ack = Ack('')\n    "
    tagSet = tag.initTagSet(tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 5))
    subtypeSpec = OctetString.subtypeSpec + constraint.SingleValueConstraint(octets.str2octs(""))
    typeId = OctetString.getTypeId()

    def prettyIn(self, value):
        if value:
            return value
        else:
            return octets.str2octs("")


if sys.version_info[0] <= 2:
    intTypes = (
     int, long)
else:
    intTypes = (
     int,)
numericTypes = intTypes + (float,)

class ObjectIdentifier(base.AbstractSimpleAsn1Item):
    __doc__ = "Create |ASN.1| schema or value object.\n\n    |ASN.1| objects are immutable and duck-type Python :class:`tuple` objects (tuple of non-negative integers).\n\n    Keyword Args\n    ------------\n    value: :class:`tuple`, :class:`str` or |ASN.1| object\n        Python sequence of :class:`int` or string literal or |ASN.1| object.\n\n    tagSet: :py:class:`~pyasn1.type.tag.TagSet`\n        Object representing non-default ASN.1 tag(s)\n\n    subtypeSpec: :py:class:`~pyasn1.type.constraint.ConstraintsIntersection`\n        Object representing non-default ASN.1 subtype constraint(s)\n\n    Raises\n    ------\n    :py:class:`~pyasn1.error.PyAsn1Error`\n        On constraint violation or bad initializer.\n\n    Examples\n    --------\n    .. code-block:: python\n\n        class ID(ObjectIdentifier):\n            '''\n            ASN.1 specification:\n\n            ID ::= OBJECT IDENTIFIER\n\n            id-edims ID ::= { joint-iso-itu-t mhs-motif(6) edims(7) }\n            id-bp ID ::= { id-edims 11 }\n            '''\n        id_edims = ID('2.6.7')\n        id_bp = id_edims + (11,)\n    "
    tagSet = tag.initTagSet(tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 6))
    subtypeSpec = constraint.ConstraintsIntersection()
    typeId = base.AbstractSimpleAsn1Item.getTypeId()

    def __add__(self, other):
        return self.clone(self._value + other)

    def __radd__(self, other):
        return self.clone(other + self._value)

    def asTuple(self):
        return self._value

    def __len__(self):
        return len(self._value)

    def __getitem__(self, i):
        if i.__class__ is slice:
            return self.clone(self._value[i])
        else:
            return self._value[i]

    def __iter__(self):
        return iter(self._value)

    def __contains__(self, value):
        return value in self._value

    def index(self, suboid):
        return self._value.index(suboid)

    def isPrefixOf(self, other):
        """Indicate if this |ASN.1| object is a prefix of other |ASN.1| object.

        Parameters
        ----------
        other: |ASN.1| object
            |ASN.1| object

        Returns
        -------
        : :class:`bool`
            :class:`True` if this |ASN.1| object is a parent (e.g. prefix) of the other |ASN.1| object
            or :class:`False` otherwise.
        """
        l = len(self)
        if l <= len(other):
            if self._value[:l] == other[:l]:
                return True
        return False

    def prettyIn(self, value):
        if isinstance(value, ObjectIdentifier):
            return tuple(value)
        else:
            if octets.isStringType(value):
                if "-" in value:
                    raise error.PyAsn1Error("Malformed Object ID %s at %s: %s" % (value, self.__class__.__name__, sys.exc_info()[1]))
                try:
                    return tuple([int(subOid) for subOid in value.split(".") if subOid])
                except ValueError:
                    raise error.PyAsn1Error("Malformed Object ID %s at %s: %s" % (value, self.__class__.__name__, sys.exc_info()[1]))

            try:
                tupleOfInts = tuple([int(subOid) for subOid in value if subOid >= 0])
            except (ValueError, TypeError):
                raise error.PyAsn1Error("Malformed Object ID %s at %s: %s" % (value, self.__class__.__name__, sys.exc_info()[1]))

            if len(tupleOfInts) == len(value):
                return tupleOfInts
        raise error.PyAsn1Error("Malformed Object ID %s at %s" % (value, self.__class__.__name__))

    def prettyOut(self, value):
        return ".".join([str(x) for x in value])


class Real(base.AbstractSimpleAsn1Item):
    __doc__ = "Create |ASN.1| schema or value object.\n\n    |ASN.1| objects are immutable and duck-type Python :class:`float` objects.\n    Additionally, |ASN.1| objects behave like a :class:`tuple` in which case its\n    elements are mantissa, base and exponent.\n\n    Keyword Args\n    ------------\n    value: :class:`tuple`, :class:`float` or |ASN.1| object\n        Python sequence of :class:`int` (representing mantissa, base and\n        exponent) or float instance or *Real* class instance.\n\n    tagSet: :py:class:`~pyasn1.type.tag.TagSet`\n        Object representing non-default ASN.1 tag(s)\n\n    subtypeSpec: :py:class:`~pyasn1.type.constraint.ConstraintsIntersection`\n        Object representing non-default ASN.1 subtype constraint(s)\n\n    Raises\n    ------\n    :py:class:`~pyasn1.error.PyAsn1Error`\n        On constraint violation or bad initializer.\n\n    Examples\n    --------\n    .. code-block:: python\n\n        class Pi(Real):\n            '''\n            ASN.1 specification:\n\n            Pi ::= REAL\n\n            pi Pi ::= { mantissa 314159, base 10, exponent -5 }\n\n            '''\n        pi = Pi((314159, 10, -5))\n    "
    binEncBase = None
    try:
        _plusInf = float("inf")
        _minusInf = float("-inf")
        _inf = (_plusInf, _minusInf)
    except ValueError:
        _plusInf = _minusInf = None
        _inf = ()

    tagSet = tag.initTagSet(tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 9))
    subtypeSpec = constraint.ConstraintsIntersection()
    typeId = base.AbstractSimpleAsn1Item.getTypeId()

    @staticmethod
    def __normalizeBase10(value):
        m, b, e = value
        while m and m % 10 == 0:
            m /= 10
            e += 1

        return (
         m, b, e)

    def prettyIn(self, value):
        if isinstance(value, tuple):
            if len(value) == 3:
                if not isinstance(value[0], numericTypes) or not isinstance(value[1], intTypes) or not isinstance(value[2], intTypes):
                    raise error.PyAsn1Error("Lame Real value syntax: %s" % (value,))
                if isinstance(value[0], float):
                    if self._inf:
                        if value[0] in self._inf:
                            return value[0]
                    else:
                        if value[1] not in (2, 10):
                            raise error.PyAsn1Error("Prohibited base for Real value: %s" % (value[1],))
                        if value[1] == 10:
                            value = self._Real__normalizeBase10(value)
                    return value
            if isinstance(value, intTypes):
                return self._Real__normalizeBase10((value, 10, 0))
            if isinstance(value, float) or octets.isStringType(value):
                if octets.isStringType(value):
                    try:
                        value = float(value)
                    except ValueError:
                        raise error.PyAsn1Error("Bad real value syntax: %s" % (value,))

                if self._inf:
                    if value in self._inf:
                        return value
                e = 0
                while int(value) != value:
                    value *= 10
                    e -= 1

                return self._Real__normalizeBase10((int(value), 10, e))
        else:
            if isinstance(value, Real):
                return tuple(value)
        raise error.PyAsn1Error("Bad real value syntax: %s" % (value,))

    def prettyPrint(self, scope=0):
        try:
            return self.prettyOut(float(self))
        except OverflowError:
            return "<overflow>"

    @property
    def isPlusInf(self):
        """Indicate PLUS-INFINITY object value

        Returns
        -------
        : :class:`bool`
            :class:`True` if calling object represents plus infinity
            or :class:`False` otherwise.

        """
        return self._value == self._plusInf

    @property
    def isMinusInf(self):
        """Indicate MINUS-INFINITY object value

        Returns
        -------
        : :class:`bool`
            :class:`True` if calling object represents minus infinity
            or :class:`False` otherwise.
        """
        return self._value == self._minusInf

    @property
    def isInf(self):
        return self._value in self._inf

    def __add__(self, value):
        return self.clone(float(self) + value)

    def __radd__(self, value):
        return self + value

    def __mul__(self, value):
        return self.clone(float(self) * value)

    def __rmul__(self, value):
        return self * value

    def __sub__(self, value):
        return self.clone(float(self) - value)

    def __rsub__(self, value):
        return self.clone(value - float(self))

    def __mod__(self, value):
        return self.clone(float(self) % value)

    def __rmod__(self, value):
        return self.clone(value % float(self))

    def __pow__(self, value, modulo=None):
        return self.clone(pow(float(self), value, modulo))

    def __rpow__(self, value):
        return self.clone(pow(value, float(self)))

    if sys.version_info[0] <= 2:

        def __div__(self, value):
            return self.clone(float(self) / value)

        def __rdiv__(self, value):
            return self.clone(value / float(self))

    else:

        def __truediv__(self, value):
            return self.clone(float(self) / value)

        def __rtruediv__(self, value):
            return self.clone(value / float(self))

        def __divmod__(self, value):
            return self.clone(float(self) // value)

        def __rdivmod__(self, value):
            return self.clone(value // float(self))

    def __int__(self):
        return int(float(self))

    if sys.version_info[0] <= 2:

        def __long__(self):
            return long(float(self))

    else:

        def __float__(self):
            if self._value in self._inf:
                return self._value
            else:
                return float(self._value[0] * pow(self._value[1], self._value[2]))

        def __abs__(self):
            return self.clone(abs(float(self)))

        def __pos__(self):
            return self.clone(+float(self))

        def __neg__(self):
            return self.clone(-float(self))

        def __round__(self, n=0):
            r = round(float(self), n)
            if n:
                return self.clone(r)
            else:
                return r

        def __floor__(self):
            return self.clone(math.floor(float(self)))

        def __ceil__(self):
            return self.clone(math.ceil(float(self)))

        if sys.version_info[0:2] > (2, 5):

            def __trunc__(self):
                return self.clone(math.trunc(float(self)))

        def __lt__(self, value):
            return float(self) < value

        def __le__(self, value):
            return float(self) <= value

        def __eq__(self, value):
            return float(self) == value

        def __ne__(self, value):
            return float(self) != value

        def __gt__(self, value):
            return float(self) > value

        def __ge__(self, value):
            return float(self) >= value

        if sys.version_info[0] <= 2:

            def __nonzero__(self):
                return bool(float(self))

        else:

            def __bool__(self):
                return bool(float(self))

        __hash__ = base.AbstractSimpleAsn1Item.__hash__

    def __getitem__(self, idx):
        if self._value in self._inf:
            raise error.PyAsn1Error("Invalid infinite value operation")
        else:
            return self._value[idx]

    def isPlusInfinity(self):
        return self.isPlusInf

    def isMinusInfinity(self):
        return self.isMinusInf

    def isInfinity(self):
        return self.isInf


class Enumerated(Integer):
    __doc__ = "Create |ASN.1| type or object.\n\n    |ASN.1| objects are immutable and duck-type Python :class:`int` objects.\n\n    Keyword Args\n    ------------\n    value: :class:`int`, :class:`str` or |ASN.1| object\n        Python integer or string literal or |ASN.1| class instance.\n\n    tagSet: :py:class:`~pyasn1.type.tag.TagSet`\n        Object representing non-default ASN.1 tag(s)\n\n    subtypeSpec: :py:class:`~pyasn1.type.constraint.ConstraintsIntersection`\n        Object representing non-default ASN.1 subtype constraint(s)\n\n    namedValues: :py:class:`~pyasn1.type.namedval.NamedValues`\n        Object representing non-default symbolic aliases for numbers\n\n    Raises\n    ------\n    :py:class:`~pyasn1.error.PyAsn1Error`\n        On constraint violation or bad initializer.\n\n    Examples\n    --------\n\n    .. code-block:: python\n\n        class RadioButton(Enumerated):\n            '''\n            ASN.1 specification:\n\n            RadioButton ::= ENUMERATED { button1(0), button2(1),\n                                         button3(2) }\n\n            selected-by-default RadioButton ::= button1\n            '''\n            namedValues = NamedValues(\n                ('button1', 0), ('button2', 1),\n                ('button3', 2)\n            )\n\n        selected_by_default = RadioButton('button1')\n    "
    tagSet = tag.initTagSet(tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 10))
    subtypeSpec = constraint.ConstraintsIntersection()
    typeId = Integer.getTypeId()
    namedValues = namedval.NamedValues()


class SequenceOfAndSetOfBase(base.AbstractConstructedAsn1Item):
    __doc__ = "Create |ASN.1| type.\n\n    |ASN.1| objects are mutable and duck-type Python :class:`list` objects.\n\n    Keyword Args\n    ------------\n    componentType : :py:class:`~pyasn1.type.base.PyAsn1Item` derivative\n        A pyasn1 object representing ASN.1 type allowed within |ASN.1| type\n\n    tagSet: :py:class:`~pyasn1.type.tag.TagSet`\n        Object representing non-default ASN.1 tag(s)\n\n    subtypeSpec: :py:class:`~pyasn1.type.constraint.ConstraintsIntersection`\n        Object representing non-default ASN.1 subtype constraint(s)\n\n    sizeSpec: :py:class:`~pyasn1.type.constraint.ConstraintsIntersection`\n        Object representing collection size constraint\n\n    Examples\n    --------\n\n    .. code-block:: python\n\n        class LotteryDraw(SequenceOf):  #  SetOf is similar\n            '''\n            ASN.1 specification:\n\n            LotteryDraw ::= SEQUENCE OF INTEGER\n            '''\n            componentType = Integer()\n\n        lotteryDraw = LotteryDraw()\n        lotteryDraw.extend([123, 456, 789])\n    "

    def __init__(self, *args, **kwargs):
        if args:
            for key, value in zip(('componentType', 'tagSet', 'subtypeSpec', 'sizeSpec'), args):
                if key in kwargs:
                    raise error.PyAsn1Error("Conflicting positional and keyword params!")
                kwargs["componentType"] = value

        (base.AbstractConstructedAsn1Item.__init__)(self, **kwargs)

    def __getitem__(self, idx):
        try:
            return self.getComponentByPosition(idx)
        except error.PyAsn1Error:
            raise IndexError(sys.exc_info()[1])

    def __setitem__(self, idx, value):
        try:
            self.setComponentByPosition(idx, value)
        except error.PyAsn1Error:
            raise IndexError(sys.exc_info()[1])

    def clear(self):
        self._componentValues = []

    def append(self, value):
        self[len(self)] = value

    def count(self, value):
        return self._componentValues.count(value)

    def extend(self, values):
        for value in values:
            self.append(value)

    def index(self, value, start=0, stop=None):
        if stop is None:
            stop = len(self)
        try:
            return self._componentValues.index(value, start, stop)
        except error.PyAsn1Error:
            raise ValueError(sys.exc_info()[1])

    def reverse(self):
        self._componentValues.reverse()

    def sort(self, key=None, reverse=False):
        self._componentValues.sort(key=key, reverse=reverse)

    def __iter__(self):
        return iter(self._componentValues)

    def _cloneComponentValues(self, myClone, cloneValueFlag):
        for idx, componentValue in enumerate(self._componentValues):
            if componentValue is not noValue:
                if isinstance(componentValue, base.AbstractConstructedAsn1Item):
                    myClone.setComponentByPosition(idx, componentValue.clone(cloneValueFlag=cloneValueFlag))
                else:
                    myClone.setComponentByPosition(idx, componentValue.clone())

    def getComponentByPosition(self, idx, default=noValue, instantiate=True):
        """Return |ASN.1| type component value by position.

        Equivalent to Python sequence subscription operation (e.g. `[]`).

        Parameters
        ----------
        idx : :class:`int`
            Component index (zero-based). Must either refer to an existing
            component or to N+1 component (if *componentType* is set). In the latter
            case a new component type gets instantiated and appended to the |ASN.1|
            sequence.

        Keyword Args
        ------------
        default: :class:`object`
            If set and requested component is a schema object, return the `default`
            object instead of the requested component.

        instantiate: :class:`bool`
            If `True` (default), inner component will be automatically instantiated.
            If 'False' either existing component or the `noValue` object will be
            returned.

        Returns
        -------
        : :py:class:`~pyasn1.type.base.PyAsn1Item`
            Instantiate |ASN.1| component type or return existing component value

        Examples
        --------

        .. code-block:: python

            # can also be SetOf
            class MySequenceOf(SequenceOf):
                componentType = OctetString()

            s = MySequenceOf()

            # returns component #0 with `.isValue` property False
            s.getComponentByPosition(0)

            # returns None
            s.getComponentByPosition(0, default=None)

            s.clear()

            # returns noValue
            s.getComponentByPosition(0, instantiate=False)

            # sets component #0 to OctetString() ASN.1 schema
            # object and returns it
            s.getComponentByPosition(0, instantiate=True)

            # sets component #0 to ASN.1 value object
            s.setComponentByPosition(0, 'ABCD')

            # returns OctetString('ABCD') value object
            s.getComponentByPosition(0, instantiate=False)

            s.clear()

            # returns noValue
            s.getComponentByPosition(0, instantiate=False)
        """
        try:
            componentValue = self._componentValues[idx]
        except IndexError:
            if not instantiate:
                return default
            self.setComponentByPosition(idx)
            componentValue = self._componentValues[idx]

        if default is noValue or componentValue.isValue:
            return componentValue
        else:
            return default

    def setComponentByPosition(self, idx, value=noValue, verifyConstraints=True, matchTags=True, matchConstraints=True):
        """Assign |ASN.1| type component by position.

        Equivalent to Python sequence item assignment operation (e.g. `[]`)
        or list.append() (when idx == len(self)).

        Parameters
        ----------
        idx: :class:`int`
            Component index (zero-based). Must either refer to existing
            component or to N+1 component. In the latter case a new component
            type gets instantiated (if *componentType* is set, or given ASN.1
            object is taken otherwise) and appended to the |ASN.1| sequence.

        Keyword Args
        ------------
        value: :class:`object` or :py:class:`~pyasn1.type.base.PyAsn1Item` derivative
            A Python value to initialize |ASN.1| component with (if *componentType* is set)
            or ASN.1 value object to assign to |ASN.1| component.

        verifyConstraints: :class:`bool`
             If `False`, skip constraints validation

        matchTags: :class:`bool`
             If `False`, skip component tags matching

        matchConstraints: :class:`bool`
             If `False`, skip component constraints matching

        Returns
        -------
        self

        Raises
        ------
        IndexError:
            When idx > len(self)
        """
        componentType = self.componentType
        try:
            currentValue = self._componentValues[idx]
        except IndexError:
            currentValue = noValue
            if len(self._componentValues) < idx:
                raise error.PyAsn1Error("Component index out of range")

        if value is noValue:
            if componentType is not None:
                value = componentType.clone()
            else:
                if currentValue is noValue:
                    raise error.PyAsn1Error("Component type not defined")
        elif not isinstance(value, base.Asn1Item):
            pass
        if componentType is not None:
            if isinstance(componentType, base.AbstractSimpleAsn1Item):
                value = componentType.clone(value=value)
            if currentValue is not noValue:
                if isinstance(currentValue, base.AbstractSimpleAsn1Item):
                    value = currentValue.clone(value=value)
                else:
                    raise error.PyAsn1Error("Non-ASN.1 value %r and undefined component type at %r" % (value, self))
        else:
            if componentType is not None:
                if self.strictConstraints:
                    if not componentType.isSameTypeWith(value, matchTags, matchConstraints):
                        raise error.PyAsn1Error("Component value is tag-incompatible: %r vs %r" % (value, componentType))
            else:
                if not componentType.isSuperTypeOf(value, matchTags, matchConstraints):
                    raise error.PyAsn1Error("Component value is tag-incompatible: %r vs %r" % (value, componentType))
                if verifyConstraints:
                    if value.isValue:
                        try:
                            self.subtypeSpec(value, idx)
                        except error.PyAsn1Error:
                            exType, exValue, exTb = sys.exc_info()
                            raise exType("%s at %s" % (exValue, self.__class__.__name__))

                    if currentValue is noValue:
                        self._componentValues.append(value)
                else:
                    self._componentValues[idx] = value
            return self

    @property
    def componentTagMap(self):
        if self.componentType is not None:
            return self.componentType.tagMap

    def prettyPrint(self, scope=0):
        scope += 1
        representation = self.__class__.__name__ + ":\n"
        for idx, componentValue in enumerate(self._componentValues):
            representation += " " * scope
            if componentValue is noValue and self.componentType is not None:
                representation += "<empty>"
            else:
                representation += componentValue.prettyPrint(scope)

        return representation

    def prettyPrintType(self, scope=0):
        scope += 1
        representation = "%s -> %s {\n" % (self.tagSet, self.__class__.__name__)
        if self.componentType is not None:
            representation += " " * scope
            representation += self.componentType.prettyPrintType(scope)
        return representation + "\n" + " " * (scope - 1) + "}"

    @property
    def isValue(self):
        """Indicate that |ASN.1| object represents ASN.1 value.

        If *isValue* is `False` then this object represents just ASN.1 schema.

        If *isValue* is `True` then, in addition to its ASN.1 schema features,
        this object can also be used like a Python built-in object (e.g. `int`,
        `str`, `dict` etc.).

        Returns
        -------
        : :class:`bool`
            :class:`False` if object represents just ASN.1 schema.
            :class:`True` if object represents ASN.1 schema and can be used as a normal value.

        Note
        ----
        There is an important distinction between PyASN1 schema and value objects.
        The PyASN1 schema objects can only participate in ASN.1 schema-related
        operations (e.g. defining or testing the structure of the data). Most
        obvious uses of ASN.1 schema is to guide serialisation codecs whilst
        encoding/decoding serialised ASN.1 contents.

        The PyASN1 value objects can **additionally** participate in many operations
        involving regular Python objects (e.g. arithmetic, comprehension etc).
        """
        for componentValue in self._componentValues:
            if componentValue is noValue or not componentValue.isValue:
                return False

        return True


class SequenceOf(SequenceOfAndSetOfBase):
    __doc__ = SequenceOfAndSetOfBase.__doc__
    tagSet = tag.initTagSet(tag.Tag(tag.tagClassUniversal, tag.tagFormatConstructed, 16))
    componentType = None
    subtypeSpec = constraint.ConstraintsIntersection()
    sizeSpec = constraint.ConstraintsIntersection()
    typeId = SequenceOfAndSetOfBase.getTypeId()


class SetOf(SequenceOfAndSetOfBase):
    __doc__ = SequenceOfAndSetOfBase.__doc__
    tagSet = tag.initTagSet(tag.Tag(tag.tagClassUniversal, tag.tagFormatConstructed, 17))
    componentType = None
    subtypeSpec = constraint.ConstraintsIntersection()
    sizeSpec = constraint.ConstraintsIntersection()
    typeId = SequenceOfAndSetOfBase.getTypeId()


class SequenceAndSetBase(base.AbstractConstructedAsn1Item):
    __doc__ = "Create |ASN.1| type.\n\n    |ASN.1| objects are mutable and duck-type Python :class:`dict` objects.\n\n    Keyword Args\n    ------------\n    componentType: :py:class:`~pyasn1.type.namedtype.NamedType`\n        Object holding named ASN.1 types allowed within this collection\n\n    tagSet: :py:class:`~pyasn1.type.tag.TagSet`\n        Object representing non-default ASN.1 tag(s)\n\n    subtypeSpec: :py:class:`~pyasn1.type.constraint.ConstraintsIntersection`\n        Object representing non-default ASN.1 subtype constraint(s)\n\n    sizeSpec: :py:class:`~pyasn1.type.constraint.ConstraintsIntersection`\n        Object representing collection size constraint\n\n    Examples\n    --------\n\n    .. code-block:: python\n\n        class Description(Sequence):  #  Set is similar\n            '''\n            ASN.1 specification:\n\n            Description ::= SEQUENCE {\n                surname    IA5String,\n                first-name IA5String OPTIONAL,\n                age        INTEGER DEFAULT 40\n            }\n            '''\n            componentType = NamedTypes(\n                NamedType('surname', IA5String()),\n                OptionalNamedType('first-name', IA5String()),\n                DefaultedNamedType('age', Integer(40))\n            )\n\n        descr = Description()\n        descr['surname'] = 'Smith'\n        descr['first-name'] = 'John'\n    "
    componentType = namedtype.NamedTypes()

    class DynamicNames(object):
        __doc__ = "Fields names/positions mapping for component-less objects"

        def __init__(self):
            self._keyToIdxMap = {}
            self._idxToKeyMap = {}

        def __len__(self):
            return len(self._keyToIdxMap)

        def __contains__(self, item):
            return item in self._keyToIdxMap or item in self._idxToKeyMap

        def __iter__(self):
            return (self._idxToKeyMap[idx] for idx in range(len(self._idxToKeyMap)))

        def __getitem__(self, item):
            try:
                return self._keyToIdxMap[item]
            except KeyError:
                return self._idxToKeyMap[item]

        def getNameByPosition(self, idx):
            try:
                return self._idxToKeyMap[idx]
            except KeyError:
                raise error.PyAsn1Error("Type position out of range")

        def getPositionByName(self, name):
            try:
                return self._keyToIdxMap[name]
            except KeyError:
                raise error.PyAsn1Error("Name %s not found" % (name,))

        def addField(self, idx):
            self._keyToIdxMap["field-%d" % idx] = idx
            self._idxToKeyMap[idx] = "field-%d" % idx

    def __init__(self, **kwargs):
        (base.AbstractConstructedAsn1Item.__init__)(self, **kwargs)
        self._componentTypeLen = len(self.componentType)
        self._dynamicNames = self._componentTypeLen or self.DynamicNames()

    def __getitem__(self, idx):
        if octets.isStringType(idx):
            try:
                return self.getComponentByName(idx)
            except error.PyAsn1Error:
                raise KeyError(sys.exc_info()[1])

        try:
            return self.getComponentByPosition(idx)
        except error.PyAsn1Error:
            raise IndexError(sys.exc_info()[1])

    def __setitem__(self, idx, value):
        if octets.isStringType(idx):
            try:
                self.setComponentByName(idx, value)
            except error.PyAsn1Error:
                raise KeyError(sys.exc_info()[1])

        try:
            self.setComponentByPosition(idx, value)
        except error.PyAsn1Error:
            raise IndexError(sys.exc_info()[1])

    def __contains__(self, key):
        if self._componentTypeLen:
            return key in self.componentType
        else:
            return key in self._dynamicNames

    def __iter__(self):
        return iter(self.componentType or self._dynamicNames)

    def values(self):
        for idx in range(self._componentTypeLen or len(self._dynamicNames)):
            yield self[idx]

    def keys(self):
        return iter(self)

    def items(self):
        for idx in range(self._componentTypeLen or len(self._dynamicNames)):
            if self._componentTypeLen:
                yield (
                 self.componentType[idx].name, self[idx])
            else:
                yield (
                 self._dynamicNames[idx], self[idx])

    def update(self, *iterValue, **mappingValue):
        for k, v in iterValue:
            self[k] = v

        for k in mappingValue:
            self[k] = mappingValue[k]

    def clear(self):
        self._componentValues = []
        self._dynamicNames = self.DynamicNames()

    def _cloneComponentValues(self, myClone, cloneValueFlag):
        for idx, componentValue in enumerate(self._componentValues):
            if componentValue is not noValue:
                if isinstance(componentValue, base.AbstractConstructedAsn1Item):
                    myClone.setComponentByPosition(idx, componentValue.clone(cloneValueFlag=cloneValueFlag))
                else:
                    myClone.setComponentByPosition(idx, componentValue.clone())

    def getComponentByName(self, name, default=noValue, instantiate=True):
        """Returns |ASN.1| type component by name.

        Equivalent to Python :class:`dict` subscription operation (e.g. `[]`).

        Parameters
        ----------
        name: :class:`str`
            |ASN.1| type component name

        Keyword Args
        ------------
        default: :class:`object`
            If set and requested component is a schema object, return the `default`
            object instead of the requested component.

        instantiate: :class:`bool`
            If `True` (default), inner component will be automatically instantiated.
            If 'False' either existing component or the `noValue` object will be
            returned.

        Returns
        -------
        : :py:class:`~pyasn1.type.base.PyAsn1Item`
            Instantiate |ASN.1| component type or return existing component value
        """
        if self._componentTypeLen:
            idx = self.componentType.getPositionByName(name)
        else:
            try:
                idx = self._dynamicNames.getPositionByName(name)
            except KeyError:
                raise error.PyAsn1Error("Name %s not found" % (name,))

        return self.getComponentByPosition(idx, default=default, instantiate=instantiate)

    def setComponentByName(self, name, value=noValue, verifyConstraints=True, matchTags=True, matchConstraints=True):
        """Assign |ASN.1| type component by name.

        Equivalent to Python :class:`dict` item assignment operation (e.g. `[]`).

        Parameters
        ----------
        name: :class:`str`
            |ASN.1| type component name

        Keyword Args
        ------------
        value: :class:`object` or :py:class:`~pyasn1.type.base.PyAsn1Item` derivative
            A Python value to initialize |ASN.1| component with (if *componentType* is set)
            or ASN.1 value object to assign to |ASN.1| component.

        verifyConstraints: :class:`bool`
             If `False`, skip constraints validation

        matchTags: :class:`bool`
             If `False`, skip component tags matching

        matchConstraints: :class:`bool`
             If `False`, skip component constraints matching

        Returns
        -------
        self
        """
        if self._componentTypeLen:
            idx = self.componentType.getPositionByName(name)
        else:
            try:
                idx = self._dynamicNames.getPositionByName(name)
            except KeyError:
                raise error.PyAsn1Error("Name %s not found" % (name,))

        return self.setComponentByPosition(idx, value, verifyConstraints, matchTags, matchConstraints)

    def getComponentByPosition(self, idx, default=noValue, instantiate=True):
        """Returns |ASN.1| type component by index.

        Equivalent to Python sequence subscription operation (e.g. `[]`).

        Parameters
        ----------
        idx: :class:`int`
            Component index (zero-based). Must either refer to an existing
            component or (if *componentType* is set) new ASN.1 schema object gets
            instantiated.

        Keyword Args
        ------------
        default: :class:`object`
            If set and requested component is a schema object, return the `default`
            object instead of the requested component.

        instantiate: :class:`bool`
            If `True` (default), inner component will be automatically instantiated.
            If 'False' either existing component or the `noValue` object will be
            returned.

        Returns
        -------
        : :py:class:`~pyasn1.type.base.PyAsn1Item`
            a PyASN1 object

        Examples
        --------

        .. code-block:: python

            # can also be Set
            class MySequence(Sequence):
                componentType = NamedTypes(
                    NamedType('id', OctetString())
                )

            s = MySequence()

            # returns component #0 with `.isValue` property False
            s.getComponentByPosition(0)

            # returns None
            s.getComponentByPosition(0, default=None)

            s.clear()

            # returns noValue
            s.getComponentByPosition(0, instantiate=False)

            # sets component #0 to OctetString() ASN.1 schema
            # object and returns it
            s.getComponentByPosition(0, instantiate=True)

            # sets component #0 to ASN.1 value object
            s.setComponentByPosition(0, 'ABCD')

            # returns OctetString('ABCD') value object
            s.getComponentByPosition(0, instantiate=False)

            s.clear()

            # returns noValue
            s.getComponentByPosition(0, instantiate=False)
        """
        try:
            componentValue = self._componentValues[idx]
        except IndexError:
            componentValue = noValue

        if not instantiate:
            if componentValue is noValue or not componentValue.isValue:
                return default
            return componentValue
        else:
            if componentValue is noValue:
                self.setComponentByPosition(idx)
            componentValue = self._componentValues[idx]
            if default is noValue or componentValue.isValue:
                return componentValue
            return default

    def setComponentByPositionParse error at or near `JUMP_IF_TRUE_OR_POP' instruction at offset 312_314

    @property
    def isValue(self):
        """Indicate that |ASN.1| object represents ASN.1 value.

        If *isValue* is `False` then this object represents just ASN.1 schema.

        If *isValue* is `True` then, in addition to its ASN.1 schema features,
        this object can also be used like a Python built-in object (e.g. `int`,
        `str`, `dict` etc.).

        Returns
        -------
        : :class:`bool`
            :class:`False` if object represents just ASN.1 schema.
            :class:`True` if object represents ASN.1 schema and can be used as a normal value.

        Note
        ----
        There is an important distinction between PyASN1 schema and value objects.
        The PyASN1 schema objects can only participate in ASN.1 schema-related
        operations (e.g. defining or testing the structure of the data). Most
        obvious uses of ASN.1 schema is to guide serialisation codecs whilst
        encoding/decoding serialised ASN.1 contents.

        The PyASN1 value objects can **additionally** participate in many operations
        involving regular Python objects (e.g. arithmetic, comprehension etc).
        """
        componentType = self.componentType
        if componentType:
            for idx, subComponentType in enumerate(componentType.namedTypes):
                if not subComponentType.isDefaulted:
                    if subComponentType.isOptional:
                        pass
                    else:
                        if not self._componentValues:
                            return False
                        componentValue = self._componentValues[idx]
                        if componentValue is noValue or not componentValue.isValue:
                            return False

        else:
            for componentValue in self._componentValues:
                if componentValue is noValue or not componentValue.isValue:
                    return False

        return True

    def prettyPrint(self, scope=0):
        """Return an object representation string.

        Returns
        -------
        : :class:`str`
            Human-friendly object representation.
        """
        scope += 1
        representation = self.__class__.__name__ + ":\n"
        for idx, componentValue in enumerate(self._componentValues):
            if componentValue is not noValue:
                if componentValue.isValue:
                    representation += " " * scope
                    if self.componentType:
                        representation += self.componentType.getNameByPosition(idx)
                    else:
                        representation += self._dynamicNames.getNameByPosition(idx)
                representation = "%s=%s\n" % (
                 representation, componentValue.prettyPrint(scope))

        return representation

    def prettyPrintType(self, scope=0):
        scope += 1
        representation = "%s -> %s {\n" % (self.tagSet, self.__class__.__name__)
        for idx, componentType in enumerate(self.componentType.values() or self._componentValues):
            representation += " " * scope
            if self.componentType:
                representation += '"%s"' % self.componentType.getNameByPosition(idx)
            else:
                representation += '"%s"' % self._dynamicNames.getNameByPosition(idx)
            representation = "%s = %s\n" % (
             representation, componentType.prettyPrintType(scope))

        return representation + "\n" + " " * (scope - 1) + "}"

    def setDefaultComponents(self):
        return self

    def getComponentType(self):
        if self._componentTypeLen:
            return self.componentType

    def getNameByPosition(self, idx):
        if self._componentTypeLen:
            return self.componentType[idx].name


class Sequence(SequenceAndSetBase):
    __doc__ = SequenceAndSetBase.__doc__
    tagSet = tag.initTagSet(tag.Tag(tag.tagClassUniversal, tag.tagFormatConstructed, 16))
    subtypeSpec = constraint.ConstraintsIntersection()
    sizeSpec = constraint.ConstraintsIntersection()
    componentType = namedtype.NamedTypes()
    typeId = SequenceAndSetBase.getTypeId()

    def getComponentTagMapNearPosition(self, idx):
        if self.componentType:
            return self.componentType.getTagMapNearPosition(idx)

    def getComponentPositionNearType(self, tagSet, idx):
        if self.componentType:
            return self.componentType.getPositionNearType(tagSet, idx)
        else:
            return idx


class Set(SequenceAndSetBase):
    __doc__ = SequenceAndSetBase.__doc__
    tagSet = tag.initTagSet(tag.Tag(tag.tagClassUniversal, tag.tagFormatConstructed, 17))
    componentType = namedtype.NamedTypes()
    subtypeSpec = constraint.ConstraintsIntersection()
    sizeSpec = constraint.ConstraintsIntersection()
    typeId = SequenceAndSetBase.getTypeId()

    def getComponent(self, innerFlag=False):
        return self

    def getComponentByType(self, tagSet, default=noValue, instantiate=True, innerFlag=False):
        """Returns |ASN.1| type component by ASN.1 tag.

        Parameters
        ----------
        tagSet : :py:class:`~pyasn1.type.tag.TagSet`
            Object representing ASN.1 tags to identify one of
            |ASN.1| object component

        Keyword Args
        ------------
        default: :class:`object`
            If set and requested component is a schema object, return the `default`
            object instead of the requested component.

        instantiate: :class:`bool`
            If `True` (default), inner component will be automatically instantiated.
            If 'False' either existing component or the `noValue` object will be
            returned.

        Returns
        -------
        : :py:class:`~pyasn1.type.base.PyAsn1Item`
            a pyasn1 object
        """
        componentValue = self.getComponentByPosition((self.componentType.getPositionByType(tagSet)),
          default=default,
          instantiate=instantiate)
        if innerFlag:
            if isinstance(componentValue, Set):
                return componentValue.getComponent(innerFlag=True)
        return componentValue

    def setComponentByType(self, tagSet, value=noValue, verifyConstraints=True, matchTags=True, matchConstraints=True, innerFlag=False):
        """Assign |ASN.1| type component by ASN.1 tag.

        Parameters
        ----------
        tagSet : :py:class:`~pyasn1.type.tag.TagSet`
            Object representing ASN.1 tags to identify one of
            |ASN.1| object component

        Keyword Args
        ------------
        value: :class:`object` or :py:class:`~pyasn1.type.base.PyAsn1Item` derivative
            A Python value to initialize |ASN.1| component with (if *componentType* is set)
            or ASN.1 value object to assign to |ASN.1| component.

        verifyConstraints : :class:`bool`
            If `False`, skip constraints validation

        matchTags: :class:`bool`
            If `False`, skip component tags matching

        matchConstraints: :class:`bool`
            If `False`, skip component constraints matching

        innerFlag: :class:`bool`
            If `True`, search for matching *tagSet* recursively.

        Returns
        -------
        self
        """
        idx = self.componentType.getPositionByType(tagSet)
        if innerFlag:
            componentType = self.componentType.getTypeByPosition(idx)
            if componentType.tagSet:
                return self.setComponentByPosition(idx, value, verifyConstraints, matchTags, matchConstraints)
            else:
                componentType = self.getComponentByPosition(idx)
                return componentType.setComponentByType(tagSet,
                  value, verifyConstraints, matchTags, matchConstraints, innerFlag=innerFlag)
        else:
            return self.setComponentByPosition(idx, value, verifyConstraints, matchTags, matchConstraints)

    @property
    def componentTagMap(self):
        if self.componentType:
            return self.componentType.tagMapUnique


class Choice(Set):
    __doc__ = "Create |ASN.1| type.\n\n    |ASN.1| objects are mutable and duck-type Python :class:`dict` objects.\n\n    Keyword Args\n    ------------\n    componentType: :py:class:`~pyasn1.type.namedtype.NamedType`\n        Object holding named ASN.1 types allowed within this collection\n\n    tagSet: :py:class:`~pyasn1.type.tag.TagSet`\n        Object representing non-default ASN.1 tag(s)\n\n    subtypeSpec: :py:class:`~pyasn1.type.constraint.ConstraintsIntersection`\n        Object representing non-default ASN.1 subtype constraint(s)\n\n    sizeSpec: :py:class:`~pyasn1.type.constraint.ConstraintsIntersection`\n        Object representing collection size constraint\n\n    Examples\n    --------\n\n    .. code-block:: python\n\n        class Afters(Choice):\n            '''\n            ASN.1 specification:\n\n            Afters ::= CHOICE {\n                cheese  [0] IA5String,\n                dessert [1] IA5String\n            }\n            '''\n            componentType = NamedTypes(\n                NamedType('cheese', IA5String().subtype(\n                    implicitTag=Tag(tagClassContext, tagFormatSimple, 0)\n                ),\n                NamedType('dessert', IA5String().subtype(\n                    implicitTag=Tag(tagClassContext, tagFormatSimple, 1)\n                )\n            )\n\n        afters = Afters()\n        afters['cheese'] = 'Mascarpone'\n    "
    tagSet = tag.TagSet()
    componentType = namedtype.NamedTypes()
    subtypeSpec = constraint.ConstraintsIntersection()
    sizeSpec = constraint.ConstraintsIntersection(constraint.ValueSizeConstraint(1, 1))
    typeId = Set.getTypeId()
    _currentIdx = None

    def __eq__(self, other):
        if self._componentValues:
            return self._componentValues[self._currentIdx] == other
        else:
            return NotImplemented

    def __ne__(self, other):
        if self._componentValues:
            return self._componentValues[self._currentIdx] != other
        else:
            return NotImplemented

    def __lt__(self, other):
        if self._componentValues:
            return self._componentValues[self._currentIdx] < other
        else:
            return NotImplemented

    def __le__(self, other):
        if self._componentValues:
            return self._componentValues[self._currentIdx] <= other
        else:
            return NotImplemented

    def __gt__(self, other):
        if self._componentValues:
            return self._componentValues[self._currentIdx] > other
        else:
            return NotImplemented

    def __ge__(self, other):
        if self._componentValues:
            return self._componentValues[self._currentIdx] >= other
        else:
            return NotImplemented

    if sys.version_info[0] <= 2:

        def __nonzero__(self):
            return self._componentValues and True or False

    else:

        def __bool__(self):
            return self._componentValues and True or False

    def __len__(self):
        return self._currentIdx is not None and 1 or 0

    def __contains__(self, key):
        if self._currentIdx is None:
            return False
        else:
            return key == self.componentType[self._currentIdx].getName()

    def __iter__(self):
        if self._currentIdx is None:
            raise StopIteration
        yield self.componentType[self._currentIdx].getName()

    def values(self):
        if self._currentIdx is not None:
            yield self._componentValues[self._currentIdx]

    def keys(self):
        if self._currentIdx is not None:
            yield self.componentType[self._currentIdx].getName()

    def items(self):
        if self._currentIdx is not None:
            yield (
             self.componentType[self._currentIdx].getName(), self[self._currentIdx])

    def verifySizeSpec(self):
        if self._currentIdx is None:
            raise error.PyAsn1Error("Component not chosen")

    def _cloneComponentValues(self, myClone, cloneValueFlag):
        try:
            component = self.getComponent()
        except error.PyAsn1Error:
            pass
        else:
            if isinstance(component, Choice):
                tagSet = component.effectiveTagSet
            else:
                tagSet = component.tagSet
            if isinstance(component, base.AbstractConstructedAsn1Item):
                myClone.setComponentByType(tagSet, component.clone(cloneValueFlag=cloneValueFlag))
            else:
                myClone.setComponentByType(tagSet, component.clone())

    def getComponentByPosition(self, idx, default=noValue, instantiate=True):
        __doc__ = Set.__doc__
        if self._currentIdx is None or self._currentIdx != idx:
            return Set.getComponentByPosition(self, idx, default=default, instantiate=instantiate)
        else:
            return self._componentValues[idx]

    def setComponentByPosition(self, idx, value=noValue, verifyConstraints=True, matchTags=True, matchConstraints=True):
        """Assign |ASN.1| type component by position.

        Equivalent to Python sequence item assignment operation (e.g. `[]`).

        Parameters
        ----------
        idx: :class:`int`
            Component index (zero-based). Must either refer to existing
            component or to N+1 component. In the latter case a new component
            type gets instantiated (if *componentType* is set, or given ASN.1
            object is taken otherwise) and appended to the |ASN.1| sequence.

        Keyword Args
        ------------
        value: :class:`object` or :py:class:`~pyasn1.type.base.PyAsn1Item` derivative
            A Python value to initialize |ASN.1| component with (if *componentType* is set)
            or ASN.1 value object to assign to |ASN.1| component. Once a new value is
            set to *idx* component, previous value is dropped.

        verifyConstraints : :class:`bool`
            If `False`, skip constraints validation

        matchTags: :class:`bool`
            If `False`, skip component tags matching

        matchConstraints: :class:`bool`
            If `False`, skip component constraints matching

        Returns
        -------
        self
        """
        oldIdx = self._currentIdx
        Set.setComponentByPosition(self, idx, value, verifyConstraints, matchTags, matchConstraints)
        self._currentIdx = idx
        if oldIdx is not None:
            if oldIdx != idx:
                self._componentValues[oldIdx] = noValue
        return self

    @property
    def effectiveTagSet(self):
        """Return a :class:`~pyasn1.type.tag.TagSet` object of the currently initialized component or self (if |ASN.1| is tagged)."""
        if self.tagSet:
            return self.tagSet
        else:
            component = self.getComponent()
            return component.effectiveTagSet

    @property
    def tagMap(self):
        """"Return a :class:`~pyasn1.type.tagmap.TagMap` object mapping
            ASN.1 tags to ASN.1 objects contained within callee.
        """
        if self.tagSet:
            return Set.tagMap.fget(self)
        else:
            return self.componentType.tagMapUnique

    def getComponent(self, innerFlag=False):
        """Return currently assigned component of the |ASN.1| object.

        Returns
        -------
        : :py:class:`~pyasn1.type.base.PyAsn1Item`
            a PyASN1 object
        """
        if self._currentIdx is None:
            raise error.PyAsn1Error("Component not chosen")
        else:
            c = self._componentValues[self._currentIdx]
            if innerFlag:
                if isinstance(c, Choice):
                    return c.getComponent(innerFlag)
                return c

    def getName(self, innerFlag=False):
        """Return the name of currently assigned component of the |ASN.1| object.

        Returns
        -------
        : :py:class:`str`
            |ASN.1| component name
        """
        if self._currentIdx is None:
            raise error.PyAsn1Error("Component not chosen")
        elif innerFlag:
            c = self._componentValues[self._currentIdx]
            if isinstance(c, Choice):
                return c.getName(innerFlag)
            return self.componentType.getNameByPosition(self._currentIdx)

    @property
    def isValue(self):
        """Indicate that |ASN.1| object represents ASN.1 value.

        If *isValue* is `False` then this object represents just ASN.1 schema.

        If *isValue* is `True` then, in addition to its ASN.1 schema features,
        this object can also be used like a Python built-in object (e.g. `int`,
        `str`, `dict` etc.).

        Returns
        -------
        : :class:`bool`
            :class:`False` if object represents just ASN.1 schema.
            :class:`True` if object represents ASN.1 schema and can be used as a normal value.

        Note
        ----
        There is an important distinction between PyASN1 schema and value objects.
        The PyASN1 schema objects can only participate in ASN.1 schema-related
        operations (e.g. defining or testing the structure of the data). Most
        obvious uses of ASN.1 schema is to guide serialisation codecs whilst
        encoding/decoding serialised ASN.1 contents.

        The PyASN1 value objects can **additionally** participate in many operations
        involving regular Python objects (e.g. arithmetic, comprehension etc).
        """
        if self._currentIdx is None:
            return False
        else:
            componentValue = self._componentValues[self._currentIdx]
            return componentValue is not noValue and componentValue.isValue

    def clear(self):
        self._currentIdx = None
        Set.clear(self)

    def getMinTagSet(self):
        return self.minTagSet


class Any(OctetString):
    __doc__ = 'Create |ASN.1| schema or value object.\n\n    |ASN.1| objects are immutable and duck-type Python 2 :class:`str` or Python 3\n    :class:`bytes`. When used in Unicode context, |ASN.1| type assumes "|encoding|"\n    serialisation.\n\n    Keyword Args\n    ------------\n    value: :class:`str`, :class:`bytes` or |ASN.1| object\n        string (Python 2) or bytes (Python 3), alternatively unicode object\n        (Python 2) or string (Python 3) representing character string to be\n        serialised into octets (note `encoding` parameter) or |ASN.1| object.\n\n    tagSet: :py:class:`~pyasn1.type.tag.TagSet`\n        Object representing non-default ASN.1 tag(s)\n\n    subtypeSpec: :py:class:`~pyasn1.type.constraint.ConstraintsIntersection`\n        Object representing non-default ASN.1 subtype constraint(s)\n\n    encoding: :py:class:`str`\n        Unicode codec ID to encode/decode :class:`unicode` (Python 2) or\n        :class:`str` (Python 3) the payload when |ASN.1| object is used\n        in text string context.\n\n    binValue: :py:class:`str`\n        Binary string initializer to use instead of the *value*.\n        Example: \'10110011\'.\n\n    hexValue: :py:class:`str`\n        Hexadecimal string initializer to use instead of the *value*.\n        Example: \'DEADBEEF\'.\n\n    Raises\n    ------\n    :py:class:`~pyasn1.error.PyAsn1Error`\n        On constraint violation or bad initializer.\n\n    Examples\n    --------\n    .. code-block:: python\n\n        class Error(Sequence):\n            \'\'\'\n            ASN.1 specification:\n\n            Error ::= SEQUENCE {\n                code      INTEGER,\n                parameter ANY DEFINED BY code  -- Either INTEGER or REAL\n            }\n            \'\'\'\n            componentType=NamedTypes(\n                NamedType(\'code\', Integer()),\n                NamedType(\'parameter\', Any(),\n                          openType=OpenType(\'code\', {1: Integer(),\n                                                     2: Real()}))\n            )\n\n        error = Error()\n        error[\'code\'] = 1\n        error[\'parameter\'] = Integer(1234)\n    '
    tagSet = tag.TagSet()
    subtypeSpec = constraint.ConstraintsIntersection()
    typeId = OctetString.getTypeId()

    @property
    def tagMap(self):
        """"Return a :class:`~pyasn1.type.tagmap.TagMap` object mapping
            ASN.1 tags to ASN.1 objects contained within callee.
        """
        try:
            return self._tagMap
        except AttributeError:
            self._tagMap = tagmap.TagMap({(self.tagSet): self}, {(eoo.endOfOctets.tagSet): (eoo.endOfOctets)}, self)
            return self._tagMap