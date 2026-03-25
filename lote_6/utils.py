# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: cryptography\hazmat\primitives\asymmetric\utils.py
from __future__ import absolute_import, division, print_function
from cryptography import utils
from cryptography.hazmat._der import DERReader, INTEGER, SEQUENCE, encode_der, encode_der_integer
from cryptography.hazmat.primitives import hashes

def decode_dss_signature(signature):
    with DERReader(signature).read_single_element(SEQUENCE) as seq:
        r = seq.read_element(INTEGER).as_integer()
        s = seq.read_element(INTEGER).as_integer()
        return (r, s)


def encode_dss_signature(r, s):
    return encode_der(SEQUENCE, encode_der(INTEGER, encode_der_integer(r)), encode_der(INTEGER, encode_der_integer(s)))


class Prehashed(object):

    def __init__(self, algorithm):
        if not isinstance(algorithm, hashes.HashAlgorithm):
            raise TypeError("Expected instance of HashAlgorithm.")
        self._algorithm = algorithm
        self._digest_size = algorithm.digest_size

    digest_size = utils.read_only_property("_digest_size")
