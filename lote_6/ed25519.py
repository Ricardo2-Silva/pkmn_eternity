# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: cryptography\hazmat\primitives\asymmetric\ed25519.py
from __future__ import absolute_import, division, print_function
import abc, six
from cryptography.exceptions import UnsupportedAlgorithm, _Reasons
_ED25519_KEY_SIZE = 32
_ED25519_SIG_SIZE = 64

@six.add_metaclass(abc.ABCMeta)
class Ed25519PublicKey(object):

    @classmethod
    def from_public_bytes(cls, data):
        from cryptography.hazmat.backends.openssl.backend import backend
        if not backend.ed25519_supported():
            raise UnsupportedAlgorithm("ed25519 is not supported by this version of OpenSSL.", _Reasons.UNSUPPORTED_PUBLIC_KEY_ALGORITHM)
        return backend.ed25519_load_public_bytes(data)

    @abc.abstractmethod
    def public_bytes(self, encoding, format):
        """
        The serialized bytes of the public key.
        """
        return

    @abc.abstractmethod
    def verify(self, signature, data):
        """
        Verify the signature.
        """
        return


@six.add_metaclass(abc.ABCMeta)
class Ed25519PrivateKey(object):

    @classmethod
    def generate(cls):
        from cryptography.hazmat.backends.openssl.backend import backend
        if not backend.ed25519_supported():
            raise UnsupportedAlgorithm("ed25519 is not supported by this version of OpenSSL.", _Reasons.UNSUPPORTED_PUBLIC_KEY_ALGORITHM)
        return backend.ed25519_generate_key()

    @classmethod
    def from_private_bytes(cls, data):
        from cryptography.hazmat.backends.openssl.backend import backend
        if not backend.ed25519_supported():
            raise UnsupportedAlgorithm("ed25519 is not supported by this version of OpenSSL.", _Reasons.UNSUPPORTED_PUBLIC_KEY_ALGORITHM)
        return backend.ed25519_load_private_bytes(data)

    @abc.abstractmethod
    def public_key(self):
        """
        The Ed25519PublicKey derived from the private key.
        """
        return

    @abc.abstractmethod
    def private_bytes(self, encoding, format, encryption_algorithm):
        """
        The serialized bytes of the private key.
        """
        return

    @abc.abstractmethod
    def sign(self, data):
        """
        Signs the data.
        """
        return
