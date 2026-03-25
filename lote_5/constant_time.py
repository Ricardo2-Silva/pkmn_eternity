# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: cryptography\hazmat\primitives\constant_time.py
from __future__ import absolute_import, division, print_function
import hmac

def bytes_eq(a, b):
    if not isinstance(a, bytes) or not isinstance(b, bytes):
        raise TypeError("a and b must be bytes.")
    return hmac.compare_digest(a, b)
