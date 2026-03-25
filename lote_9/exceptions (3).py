# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: service_identity\exceptions.py
"""
All exceptions and warnings thrown by ``service_identity``.

Separated into an own package for nicer tracebacks, you should still import
them from __init__.py.
"""
from __future__ import absolute_import, division, print_function
import attr

class SubjectAltNameWarning(DeprecationWarning):
    __doc__ = "\n    Server Certificate does not contain a ``SubjectAltName``.\n\n    Hostname matching is performed on the ``CommonName`` which is deprecated.\n    "


@attr.s
class VerificationError(Exception):
    __doc__ = "\n    Service identity verification failed.\n    "
    errors = attr.ib()

    def __str__(self):
        return self.__repr__()


@attr.s
class DNSMismatch(object):
    __doc__ = "\n    No matching DNSPattern could be found.\n    "
    mismatched_id = attr.ib()


@attr.s
class SRVMismatch(object):
    __doc__ = "\n    No matching SRVPattern could be found.\n    "
    mismatched_id = attr.ib()


@attr.s
class URIMismatch(object):
    __doc__ = "\n    No matching URIPattern could be found.\n    "
    mismatched_id = attr.ib()


@attr.s
class IPAddressMismatch(object):
    __doc__ = "\n    No matching IPAddressPattern could be found.\n    "
    mismatched_id = attr.ib()


class CertificateError(Exception):
    __doc__ = "\n    Certificate contains invalid or unexpected data.\n    "
