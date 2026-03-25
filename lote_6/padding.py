# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: cryptography\hazmat\primitives\asymmetric\padding.py
from __future__ import absolute_import, division, print_function
import abc, six
from cryptography import utils
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa

@six.add_metaclass(abc.ABCMeta)
class AsymmetricPadding(object):

    @abc.abstractproperty
    def name(self):
        """
        A string naming this padding (e.g. "PSS", "PKCS1").
        """
        return


@utils.register_interface(AsymmetricPadding)
class PKCS1v15(object):
    name = "EMSA-PKCS1-v1_5"


@utils.register_interface(AsymmetricPadding)
class PSS(object):
    MAX_LENGTH = object()
    name = "EMSA-PSS"

    def __init__(self, mgf, salt_length):
        self._mgf = mgf
        if not isinstance(salt_length, six.integer_types):
            if salt_length is not self.MAX_LENGTH:
                raise TypeError("salt_length must be an integer.")
        if salt_length is not self.MAX_LENGTH:
            if salt_length < 0:
                raise ValueError("salt_length must be zero or greater.")
        self._salt_length = salt_length


@utils.register_interface(AsymmetricPadding)
class OAEP(object):
    name = "EME-OAEP"

    def __init__(self, mgf, algorithm, label):
        if not isinstance(algorithm, hashes.HashAlgorithm):
            raise TypeError("Expected instance of hashes.HashAlgorithm.")
        self._mgf = mgf
        self._algorithm = algorithm
        self._label = label


class MGF1(object):
    MAX_LENGTH = object()

    def __init__(self, algorithm):
        if not isinstance(algorithm, hashes.HashAlgorithm):
            raise TypeError("Expected instance of hashes.HashAlgorithm.")
        self._algorithm = algorithm


def calculate_max_pss_salt_length(key, hash_algorithm):
    if not isinstance(key, (rsa.RSAPrivateKey, rsa.RSAPublicKey)):
        raise TypeError("key must be an RSA public or private key")
    else:
        emlen = (key.key_size + 6) // 8
        salt_length = emlen - hash_algorithm.digest_size - 2
        assert salt_length >= 0
    return salt_length
