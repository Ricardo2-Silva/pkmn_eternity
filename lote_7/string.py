# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyasn1\compat\string.py
from sys import version_info
if version_info[:2] <= (2, 5):

    def partition(string, sep):
        try:
            a, c = string.split(sep, 1)
        except ValueError:
            a, b, c = string, "", ""
        else:
            b = sep
        return (a, b, c)


else:

    def partition(string, sep):
        return string.partition(sep)
