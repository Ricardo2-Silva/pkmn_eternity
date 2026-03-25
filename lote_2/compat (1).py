# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: chardet\compat.py
import sys
if sys.version_info < (3, 0):
    PY2 = True
    PY3 = False
    base_str = (str, unicode)
    text_type = unicode
else:
    PY2 = False
    PY3 = True
    base_str = (bytes, str)
    text_type = str
