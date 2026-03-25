# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyasn1\compat\calling.py
from sys import version_info
__all__ = [
 "callable"]
if (2, 7) < version_info[:2] < (3, 2):
    import collections

    def callable(x):
        return isinstance(x, collections.Callable)


else:
    callable = callable
