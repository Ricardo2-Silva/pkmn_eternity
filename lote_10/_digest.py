# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\cred\_digest.py
"""
Calculations for HTTP Digest authentication.

@see: U{http://www.faqs.org/rfcs/rfc2617.html}
"""
from __future__ import division, absolute_import
from binascii import hexlify
from hashlib import md5, sha1
algorithms = {b'md5':md5, 
 b'md5-sess':md5, 
 b'sha':sha1}

def calcHA1(pszAlg, pszUserName, pszRealm, pszPassword, pszNonce, pszCNonce, preHA1=None):
    """
    Compute H(A1) from RFC 2617.

    @param pszAlg: The name of the algorithm to use to calculate the digest.
        Currently supported are md5, md5-sess, and sha.
    @param pszUserName: The username
    @param pszRealm: The realm
    @param pszPassword: The password
    @param pszNonce: The nonce
    @param pszCNonce: The cnonce

    @param preHA1: If available this is a str containing a previously
       calculated H(A1) as a hex string.  If this is given then the values for
       pszUserName, pszRealm, and pszPassword must be L{None} and are ignored.
    """
    if preHA1:
        if pszUserName or pszRealm or pszPassword:
            raise TypeError("preHA1 is incompatible with the pszUserName, pszRealm, and pszPassword arguments")
        if preHA1 is None:
            m = algorithms[pszAlg]()
            m.update(pszUserName)
            m.update(b':')
            m.update(pszRealm)
            m.update(b':')
            m.update(pszPassword)
            HA1 = hexlify(m.digest())
    else:
        HA1 = preHA1
    if pszAlg == b'md5-sess':
        m = algorithms[pszAlg]()
        m.update(HA1)
        m.update(b':')
        m.update(pszNonce)
        m.update(b':')
        m.update(pszCNonce)
        HA1 = hexlify(m.digest())
    return HA1


def calcHA2(algo, pszMethod, pszDigestUri, pszQop, pszHEntity):
    """
    Compute H(A2) from RFC 2617.

    @param pszAlg: The name of the algorithm to use to calculate the digest.
        Currently supported are md5, md5-sess, and sha.
    @param pszMethod: The request method.
    @param pszDigestUri: The request URI.
    @param pszQop: The Quality-of-Protection value.
    @param pszHEntity: The hash of the entity body or L{None} if C{pszQop} is
        not C{'auth-int'}.
    @return: The hash of the A2 value for the calculation of the response
        digest.
    """
    m = algorithms[algo]()
    m.update(pszMethod)
    m.update(b':')
    m.update(pszDigestUri)
    if pszQop == b'auth-int':
        m.update(b':')
        m.update(pszHEntity)
    return hexlify(m.digest())


def calcResponse(HA1, HA2, algo, pszNonce, pszNonceCount, pszCNonce, pszQop):
    """
    Compute the digest for the given parameters.

    @param HA1: The H(A1) value, as computed by L{calcHA1}.
    @param HA2: The H(A2) value, as computed by L{calcHA2}.
    @param pszNonce: The challenge nonce.
    @param pszNonceCount: The (client) nonce count value for this response.
    @param pszCNonce: The client nonce.
    @param pszQop: The Quality-of-Protection value.
    """
    m = algorithms[algo]()
    m.update(HA1)
    m.update(b':')
    m.update(pszNonce)
    m.update(b':')
    if pszNonceCount:
        if pszCNonce:
            m.update(pszNonceCount)
            m.update(b':')
            m.update(pszCNonce)
            m.update(b':')
            m.update(pszQop)
            m.update(b':')
    m.update(HA2)
    respHash = hexlify(m.digest())
    return respHash
