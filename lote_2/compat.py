# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: asyncio\compat.py
"""Compatibility helpers for the different Python versions."""
import sys
PY34 = sys.version_info >= (3, 4)
PY35 = sys.version_info >= (3, 5)
PY352 = sys.version_info >= (3, 5, 2)

def flatten_list_bytes(list_of_data):
    """Concatenate a sequence of bytes-like objects."""
    if not PY34:
        list_of_data = (bytes(data) if isinstance(data, memoryview) else data for data in list_of_data)
    return (b'').join(list_of_data)
