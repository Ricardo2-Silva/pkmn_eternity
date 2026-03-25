# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: cryptography\hazmat\backends\__init__.py
from __future__ import absolute_import, division, print_function
_default_backend = None

def default_backend():
    global _default_backend
    if _default_backend is None:
        from cryptography.hazmat.backends.openssl.backend import backend
        _default_backend = backend
    return _default_backend


def _get_backend(backend):
    if backend is None:
        return default_backend()
    else:
        return backend
