# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: cryptography\hazmat\primitives\asymmetric\__init__.py
from __future__ import absolute_import, division, print_function
import abc, six

@six.add_metaclass(abc.ABCMeta)
class AsymmetricSignatureContext(object):

    @abc.abstractmethod
    def update(self, data):
        """
        Processes the provided bytes and returns nothing.
        """
        return

    @abc.abstractmethod
    def finalize(self):
        """
        Returns the signature as bytes.
        """
        return


@six.add_metaclass(abc.ABCMeta)
class AsymmetricVerificationContext(object):

    @abc.abstractmethod
    def update(self, data):
        """
        Processes the provided bytes and returns nothing.
        """
        return

    @abc.abstractmethod
    def verify(self):
        """
        Raises an exception if the bytes provided to update do not match the
        signature or the signature does not match the public key.
        """
        return
