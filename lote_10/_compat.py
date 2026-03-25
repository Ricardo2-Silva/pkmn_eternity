# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: service_identity\_compat.py
"""
Avoid depending on any particular Python 3 compatibility approach.
"""
import sys
PY3 = sys.version_info[0] == 3
if PY3:
    maketrans = bytes.maketrans
    text_type = str
else:
    import string
    maketrans = string.maketrans
    text_type = unicode
