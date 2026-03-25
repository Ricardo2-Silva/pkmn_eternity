# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: cryptography\hazmat\backends\openssl\poly1305.py
from __future__ import absolute_import, division, print_function
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import constant_time
_POLY1305_TAG_SIZE = 16
_POLY1305_KEY_SIZE = 32

class _Poly1305Context(object):

    def __init__(self, backend, key):
        self._backend = backend
        key_ptr = self._backend._ffi.from_buffer(key)
        evp_pkey = self._backend._lib.EVP_PKEY_new_raw_private_key(self._backend._lib.NID_poly1305, self._backend._ffi.NULL, key_ptr, len(key))
        self._backend.openssl_assert(evp_pkey != self._backend._ffi.NULL)
        self._evp_pkey = self._backend._ffi.gc(evp_pkey, self._backend._lib.EVP_PKEY_free)
        ctx = self._backend._lib.Cryptography_EVP_MD_CTX_new()
        self._backend.openssl_assert(ctx != self._backend._ffi.NULL)
        self._ctx = self._backend._ffi.gc(ctx, self._backend._lib.Cryptography_EVP_MD_CTX_free)
        res = self._backend._lib.EVP_DigestSignInit(self._ctx, self._backend._ffi.NULL, self._backend._ffi.NULL, self._backend._ffi.NULL, self._evp_pkey)
        self._backend.openssl_assert(res == 1)

    def update(self, data):
        data_ptr = self._backend._ffi.from_buffer(data)
        res = self._backend._lib.EVP_DigestSignUpdate(self._ctx, data_ptr, len(data))
        self._backend.openssl_assert(res != 0)

    def finalize(self):
        buf = self._backend._ffi.new("unsigned char[]", _POLY1305_TAG_SIZE)
        outlen = self._backend._ffi.new("size_t *")
        res = self._backend._lib.EVP_DigestSignFinal(self._ctx, buf, outlen)
        self._backend.openssl_assert(res != 0)
        self._backend.openssl_assert(outlen[0] == _POLY1305_TAG_SIZE)
        return self._backend._ffi.buffer(buf)[:outlen[0]]

    def verify(self, tag):
        mac = self.finalize()
        if not constant_time.bytes_eq(mac, tag):
            raise InvalidSignature("Value did not match computed tag.")
