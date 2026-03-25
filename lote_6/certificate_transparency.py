# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: cryptography\x509\certificate_transparency.py
from __future__ import absolute_import, division, print_function
import abc
from enum import Enum
import six

class LogEntryType(Enum):
    X509_CERTIFICATE = 0
    PRE_CERTIFICATE = 1


class Version(Enum):
    v1 = 0


@six.add_metaclass(abc.ABCMeta)
class SignedCertificateTimestamp(object):

    @abc.abstractproperty
    def version(self):
        """
        Returns the SCT version.
        """
        return

    @abc.abstractproperty
    def log_id(self):
        """
        Returns an identifier indicating which log this SCT is for.
        """
        return

    @abc.abstractproperty
    def timestamp(self):
        """
        Returns the timestamp for this SCT.
        """
        return

    @abc.abstractproperty
    def entry_type(self):
        """
        Returns whether this is an SCT for a certificate or pre-certificate.
        """
        return
