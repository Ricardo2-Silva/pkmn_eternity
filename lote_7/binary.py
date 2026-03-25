# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyasn1\compat\binary.py
from sys import version_info
if version_info[0:2] < (2, 6):

    def bin(value):
        bitstring = []
        if value > 0:
            prefix = "0b"
        elif value < 0:
            prefix = "-0b"
            value = abs(value)
        else:
            prefix = "0b0"
        while value:
            if value & 1 == 1:
                bitstring.append("1")
            else:
                bitstring.append("0")
            value >>= 1

        bitstring.reverse()
        return prefix + "".join(bitstring)


else:
    bin = bin
