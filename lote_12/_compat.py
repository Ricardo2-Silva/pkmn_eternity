# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: zope\interface\_compat.py
"""Basic components support
"""
import sys, types
if sys.version_info[0] < 3:

    def _normalize_name(name):
        if isinstance(name, basestring):
            return unicode(name)
        raise TypeError("name must be a regular or unicode string")


    CLASS_TYPES = (
     type, types.ClassType)
    STRING_TYPES = (basestring,)
    _BUILTINS = "__builtin__"
    PYTHON3 = False
    PYTHON2 = True
else:

    def _normalize_name(name):
        if isinstance(name, bytes):
            name = str(name, "ascii")
        if isinstance(name, str):
            return name
        raise TypeError("name must be a string or ASCII-only bytes")


    CLASS_TYPES = (
     type,)
    STRING_TYPES = (str,)
    _BUILTINS = "builtins"
    PYTHON3 = True
    PYTHON2 = False

def _skip_under_py3k(test_method):
    import unittest
    return unittest.skipIf(sys.version_info[0] >= 3, "Only on Python 2")(test_method)


def _skip_under_py2(test_method):
    import unittest
    return unittest.skipIf(sys.version_info[0] < 3, "Only on Python 3")(test_method)
