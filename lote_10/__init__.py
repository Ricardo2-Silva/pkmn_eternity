# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: service_identity\__init__.py
"""
Verify service identities.
"""
from __future__ import absolute_import, division, print_function
from . import cryptography, pyopenssl
from .exceptions import CertificateError, SubjectAltNameWarning, VerificationError
__version__ = "18.1.0"
__title__ = "service_identity"
__description__ = "Service identity verification for pyOpenSSL & cryptography."
__uri__ = "https://service-identity.readthedocs.io/"
__author__ = "Hynek Schlawack"
__email__ = "hs@ox.cx"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2014 Hynek Schlawack"
__all__ = [
 'CertificateError', 
 'SubjectAltNameWarning', 
 'VerificationError', 
 'cryptography', 
 'pyopenssl']
