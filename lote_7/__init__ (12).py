# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyasn1\__init__.py
import sys
__version__ = "0.4.4"
if sys.version_info[:2] < (2, 4):
    raise RuntimeError("PyASN1 requires Python 2.4 or later")
