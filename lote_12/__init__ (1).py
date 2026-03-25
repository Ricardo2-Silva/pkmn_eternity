# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: urllib3\packages\ssl_match_hostname\__init__.py
import sys
try:
    if sys.version_info < (3, 5):
        raise ImportError("Fallback to vendored code")
    from ssl import CertificateError, match_hostname
except ImportError:
    try:
        from backports.ssl_match_hostname import CertificateError, match_hostname
    except ImportError:
        from ._implementation import CertificateError, match_hostname

__all__ = ('CertificateError', 'match_hostname')
