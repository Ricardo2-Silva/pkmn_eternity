# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyasn1\compat\integer.py
import sys
try:
    import platform
    implementation = platform.python_implementation()
except (ImportError, AttributeError):
    implementation = "CPython"

from pyasn1.compat.octets import oct2int, null, ensureString
if sys.version_info[0:2] < (3, 2) or implementation != "CPython":
    from binascii import a2b_hex, b2a_hex
    if sys.version_info[0] > 2:
        long = int

    def from_bytes(octets, signed=False):
        if not octets:
            return 0
        else:
            value = long(b2a_hex(ensureString(octets)), 16)
            if signed:
                if oct2int(octets[0]) & 128:
                    return value - (1 << len(octets) * 8)
            return value


    def to_bytes(value, signed=False, length=0):
        if value < 0:
            if signed:
                bits = bitLength(value)
                maxValue = 1 << bits
                valueToEncode = (value + maxValue) % maxValue
            else:
                raise OverflowError("can't convert negative int to unsigned")
        elif value == 0:
            if length == 0:
                return null
            bits = 0
            valueToEncode = value
        else:
            hexValue = hex(valueToEncode)[2:]
            if hexValue.endswith("L"):
                hexValue = hexValue[:-1]
            if len(hexValue) & 1:
                hexValue = "0" + hexValue
            if value != valueToEncode or length:
                hexLength = len(hexValue) * 4
                padLength = max(length, bits)
                if padLength > hexLength:
                    hexValue = "00" * ((padLength - hexLength - 1) // 8 + 1) + hexValue
                elif length:
                    if hexLength - length > 7:
                        raise OverflowError("int too big to convert")
            firstOctet = int(hexValue[:2], 16)
            if signed:
                if firstOctet & 128:
                    if value >= 0:
                        hexValue = "00" + hexValue
                elif value < 0:
                    hexValue = "ff" + hexValue
        octets_value = a2b_hex(hexValue)
        return octets_value


    def bitLength(number):
        hexValue = hex(abs(number))
        bits = len(hexValue) - 2
        if hexValue.endswith("L"):
            bits -= 1
        if bits & 1:
            bits += 1
        bits *= 4
        return bits


else:

    def from_bytes(octets, signed=False):
        return int.from_bytes((bytes(octets)), "big", signed=signed)


    def to_bytes(value, signed=False, length=0):
        length = max(value.bit_length(), length)
        if signed:
            if length % 8 == 0:
                length += 1
        return value.to_bytes((length // 8 + (length % 8 and 1 or 0)), "big", signed=signed)


    def bitLength(number):
        return int(number).bit_length()
