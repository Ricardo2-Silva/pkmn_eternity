# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\cred\credentials.py
"""
This module defines L{ICredentials}, an interface for objects that represent
authentication credentials to provide, and also includes a number of useful
implementations of that interface.
"""
from __future__ import division, absolute_import
from zope.interface import implementer, Interface
import base64, hmac, random, re, time
from binascii import hexlify
from hashlib import md5
from twisted.python.randbytes import secureRandom
from twisted.python.compat import networkString, nativeString
from twisted.python.compat import intToBytes, unicode
from twisted.cred._digest import calcResponse, calcHA1, calcHA2
from twisted.cred import error

class ICredentials(Interface):
    __doc__ = "\n    I check credentials.\n\n    Implementors I{must} specify the sub-interfaces of ICredentials\n    to which it conforms, using L{zope.interface.declarations.implementer}.\n    "


class IUsernameDigestHash(ICredentials):
    __doc__ = "\n    This credential is used when a CredentialChecker has access to the hash\n    of the username:realm:password as in an Apache .htdigest file.\n    "

    def checkHash(digestHash):
        """
        @param digestHash: The hashed username:realm:password to check against.

        @return: C{True} if the credentials represented by this object match
            the given hash, C{False} if they do not, or a L{Deferred} which
            will be called back with one of these values.
        """
        return


class IUsernameHashedPassword(ICredentials):
    __doc__ = "\n    I encapsulate a username and a hashed password.\n\n    This credential is used when a hashed password is received from the\n    party requesting authentication.  CredentialCheckers which check this\n    kind of credential must store the passwords in plaintext (or as\n    password-equivalent hashes) form so that they can be hashed in a manner\n    appropriate for the particular credentials class.\n\n    @type username: L{bytes}\n    @ivar username: The username associated with these credentials.\n    "

    def checkPassword(password):
        """
        Validate these credentials against the correct password.

        @type password: L{bytes}
        @param password: The correct, plaintext password against which to
        check.

        @rtype: C{bool} or L{Deferred}
        @return: C{True} if the credentials represented by this object match the
            given password, C{False} if they do not, or a L{Deferred} which will
            be called back with one of these values.
        """
        return


class IUsernamePassword(ICredentials):
    __doc__ = "\n    I encapsulate a username and a plaintext password.\n\n    This encapsulates the case where the password received over the network\n    has been hashed with the identity function (That is, not at all).  The\n    CredentialsChecker may store the password in whatever format it desires,\n    it need only transform the stored password in a similar way before\n    performing the comparison.\n\n    @type username: L{bytes}\n    @ivar username: The username associated with these credentials.\n\n    @type password: L{bytes}\n    @ivar password: The password associated with these credentials.\n    "

    def checkPassword(password):
        """
        Validate these credentials against the correct password.

        @type password: L{bytes}
        @param password: The correct, plaintext password against which to
        check.

        @rtype: C{bool} or L{Deferred}
        @return: C{True} if the credentials represented by this object match the
            given password, C{False} if they do not, or a L{Deferred} which will
            be called back with one of these values.
        """
        return


class IAnonymous(ICredentials):
    __doc__ = "\n    I am an explicitly anonymous request for access.\n\n    @see: L{twisted.cred.checkers.AllowAnonymousAccess}\n    "


@implementer(IUsernameHashedPassword, IUsernameDigestHash)
class DigestedCredentials(object):
    __doc__ = "\n    Yet Another Simple HTTP Digest authentication scheme.\n    "

    def __init__(self, username, method, realm, fields):
        self.username = username
        self.method = method
        self.realm = realm
        self.fields = fields

    def checkPassword(self, password):
        """
        Verify that the credentials represented by this object agree with the
        given plaintext C{password} by hashing C{password} in the same way the
        response hash represented by this object was generated and comparing
        the results.
        """
        response = self.fields.get("response")
        uri = self.fields.get("uri")
        nonce = self.fields.get("nonce")
        cnonce = self.fields.get("cnonce")
        nc = self.fields.get("nc")
        algo = self.fields.get("algorithm", b'md5').lower()
        qop = self.fields.get("qop", b'auth')
        expected = calcResponse(calcHA1(algo, self.username, self.realm, password, nonce, cnonce), calcHA2(algo, self.method, uri, qop, None), algo, nonce, nc, cnonce, qop)
        return expected == response

    def checkHash(self, digestHash):
        """
        Verify that the credentials represented by this object agree with the
        credentials represented by the I{H(A1)} given in C{digestHash}.

        @param digestHash: A precomputed H(A1) value based on the username,
            realm, and password associate with this credentials object.
        """
        response = self.fields.get("response")
        uri = self.fields.get("uri")
        nonce = self.fields.get("nonce")
        cnonce = self.fields.get("cnonce")
        nc = self.fields.get("nc")
        algo = self.fields.get("algorithm", b'md5').lower()
        qop = self.fields.get("qop", b'auth')
        expected = calcResponse(calcHA1(algo, None, None, None, nonce, cnonce, preHA1=digestHash), calcHA2(algo, self.method, uri, qop, None), algo, nonce, nc, cnonce, qop)
        return expected == response


class DigestCredentialFactory(object):
    __doc__ = "\n    Support for RFC2617 HTTP Digest Authentication\n\n    @cvar CHALLENGE_LIFETIME_SECS: The number of seconds for which an\n        opaque should be valid.\n\n    @type privateKey: L{bytes}\n    @ivar privateKey: A random string used for generating the secure opaque.\n\n    @type algorithm: L{bytes}\n    @param algorithm: Case insensitive string specifying the hash algorithm to\n        use.  Must be either C{'md5'} or C{'sha'}.  C{'md5-sess'} is B{not}\n        supported.\n\n    @type authenticationRealm: L{bytes}\n    @param authenticationRealm: case sensitive string that specifies the realm\n        portion of the challenge\n    "
    _parseparts = re.compile(b'([^= ]+)=(?:"([^"]*)"|([^,]+)),?')
    CHALLENGE_LIFETIME_SECS = 900
    scheme = b'digest'

    def __init__(self, algorithm, authenticationRealm):
        self.algorithm = algorithm
        self.authenticationRealm = authenticationRealm
        self.privateKey = secureRandom(12)

    def getChallenge(self, address):
        """
        Generate the challenge for use in the WWW-Authenticate header.

        @param address: The client address to which this challenge is being
            sent.

        @return: The L{dict} that can be used to generate a WWW-Authenticate
            header.
        """
        c = self._generateNonce()
        o = self._generateOpaque(c, address)
        return {'nonce':c, 
         'opaque':o, 
         'qop':b'auth', 
         'algorithm':self.algorithm, 
         'realm':self.authenticationRealm}

    def _generateNonce(self):
        """
        Create a random value suitable for use as the nonce parameter of a
        WWW-Authenticate challenge.

        @rtype: L{bytes}
        """
        return hexlify(secureRandom(12))

    def _getTime(self):
        """
        Parameterize the time based seed used in C{_generateOpaque}
        so we can deterministically unittest it's behavior.
        """
        return time.time()

    def _generateOpaque(self, nonce, clientip):
        """
        Generate an opaque to be returned to the client.  This is a unique
        string that can be returned to us and verified.
        """
        now = intToBytes(int(self._getTime()))
        if not clientip:
            clientip = b''
        else:
            if isinstance(clientip, unicode):
                clientip = clientip.encode("ascii")
        key = (b',').join((nonce, clientip, now))
        digest = hexlify(md5(key + self.privateKey).digest())
        ekey = base64.b64encode(key)
        return (b'-').join((digest, ekey.replace(b'\n', b'')))

    def _verifyOpaque(self, opaque, nonce, clientip):
        """
        Given the opaque and nonce from the request, as well as the client IP
        that made the request, verify that the opaque was generated by us.
        And that it's not too old.

        @param opaque: The opaque value from the Digest response
        @param nonce: The nonce value from the Digest response
        @param clientip: The remote IP address of the client making the request
            or L{None} if the request was submitted over a channel where this
            does not make sense.

        @return: C{True} if the opaque was successfully verified.

        @raise error.LoginFailed: if C{opaque} could not be parsed or
            contained the wrong values.
        """
        opaqueParts = opaque.split(b'-')
        if len(opaqueParts) != 2:
            raise error.LoginFailed("Invalid response, invalid opaque value")
        if not clientip:
            clientip = b''
        else:
            if isinstance(clientip, unicode):
                clientip = clientip.encode("ascii")
        key = base64.b64decode(opaqueParts[1])
        keyParts = key.split(b',')
        if len(keyParts) != 3:
            raise error.LoginFailed("Invalid response, invalid opaque value")
        if keyParts[0] != nonce:
            raise error.LoginFailed("Invalid response, incompatible opaque/nonce values")
        if keyParts[1] != clientip:
            raise error.LoginFailed("Invalid response, incompatible opaque/client values")
        try:
            when = int(keyParts[2])
        except ValueError:
            raise error.LoginFailed("Invalid response, invalid opaque/time values")

        if int(self._getTime()) - when > DigestCredentialFactory.CHALLENGE_LIFETIME_SECS:
            raise error.LoginFailed("Invalid response, incompatible opaque/nonce too old")
        digest = hexlify(md5(key + self.privateKey).digest())
        if digest != opaqueParts[0]:
            raise error.LoginFailed("Invalid response, invalid opaque value")
        return True

    def decode(self, response, method, host):
        """
        Decode the given response and attempt to generate a
        L{DigestedCredentials} from it.

        @type response: L{bytes}
        @param response: A string of comma separated key=value pairs

        @type method: L{bytes}
        @param method: The action requested to which this response is addressed
            (GET, POST, INVITE, OPTIONS, etc).

        @type host: L{bytes}
        @param host: The address the request was sent from.

        @raise error.LoginFailed: If the response does not contain a username,
            a nonce, an opaque, or if the opaque is invalid.

        @return: L{DigestedCredentials}
        """
        response = (b' ').join(response.splitlines())
        parts = self._parseparts.findall(response)
        auth = {}
        for key, bare, quoted in parts:
            value = (quoted or bare).strip()
            auth[nativeString(key.strip())] = value

        username = auth.get("username")
        if not username:
            raise error.LoginFailed("Invalid response, no username given.")
        if "opaque" not in auth:
            raise error.LoginFailed("Invalid response, no opaque given.")
        if "nonce" not in auth:
            raise error.LoginFailed("Invalid response, no nonce given.")
        if self._verifyOpaque(auth.get("opaque"), auth.get("nonce"), host):
            return DigestedCredentials(username, method, self.authenticationRealm, auth)


@implementer(IUsernameHashedPassword)
class CramMD5Credentials(object):
    __doc__ = "\n    An encapsulation of some CramMD5 hashed credentials.\n\n    @ivar challenge: The challenge to be sent to the client.\n    @type challenge: L{bytes}\n\n    @ivar response: The hashed response from the client.\n    @type response: L{bytes}\n\n    @ivar username: The username from the response from the client.\n    @type username: L{bytes} or L{None} if not yet provided.\n    "
    username = None
    challenge = b''
    response = b''

    def __init__(self, host=None):
        self.host = host

    def getChallenge(self):
        if self.challenge:
            return self.challenge
        else:
            r = random.randrange(2147483647)
            t = time.time()
            self.challenge = networkString("<%d.%d@%s>" % (
             r, t, nativeString(self.host) if self.host else None))
            return self.challenge

    def setResponse(self, response):
        self.username, self.response = response.split(None, 1)

    def moreChallenges(self):
        return False

    def checkPassword(self, password):
        verify = hexlify(hmac.HMAC(password, self.challenge).digest())
        return verify == self.response


@implementer(IUsernameHashedPassword)
class UsernameHashedPassword:

    def __init__(self, username, hashed):
        self.username = username
        self.hashed = hashed

    def checkPassword(self, password):
        return self.hashed == password


@implementer(IUsernamePassword)
class UsernamePassword:

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def checkPassword(self, password):
        return self.password == password


@implementer(IAnonymous)
class Anonymous:
    return


class ISSHPrivateKey(ICredentials):
    __doc__ = "\n    L{ISSHPrivateKey} credentials encapsulate an SSH public key to be checked\n    against a user's private key.\n\n    @ivar username: The username associated with these credentials.\n    @type username: L{bytes}\n\n    @ivar algName: The algorithm name for the blob.\n    @type algName: L{bytes}\n\n    @ivar blob: The public key blob as sent by the client.\n    @type blob: L{bytes}\n\n    @ivar sigData: The data the signature was made from.\n    @type sigData: L{bytes}\n\n    @ivar signature: The signed data.  This is checked to verify that the user\n        owns the private key.\n    @type signature: L{bytes} or L{None}\n    "


@implementer(ISSHPrivateKey)
class SSHPrivateKey:

    def __init__(self, username, algName, blob, sigData, signature):
        self.username = username
        self.algName = algName
        self.blob = blob
        self.sigData = sigData
        self.signature = signature
