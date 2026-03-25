# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\python\randbytes.py
"""
Cryptographically secure random implementation, with fallback on normal random.
"""
from __future__ import division, absolute_import
import warnings, os, random, string
from twisted.python.compat import _PY3
getrandbits = getattr(random, "getrandbits", None)
if _PY3:
    _fromhex = bytes.fromhex
else:

    def _fromhex(hexBytes):
        return hexBytes.decode("hex")


class SecureRandomNotAvailable(RuntimeError):
    __doc__ = "\n    Exception raised when no secure random algorithm is found.\n    "


class SourceNotAvailable(RuntimeError):
    __doc__ = "\n    Internal exception used when a specific random source is not available.\n    "


class RandomFactory(object):
    __doc__ = "\n    Factory providing L{secureRandom} and L{insecureRandom} methods.\n\n    You shouldn't have to instantiate this class, use the module level\n    functions instead: it is an implementation detail and could be removed or\n    changed arbitrarily.\n    "
    randomSources = ()
    getrandbits = getrandbits

    def _osUrandom(self, nbytes):
        """
        Wrapper around C{os.urandom} that cleanly manage its absence.
        """
        try:
            return os.urandom(nbytes)
        except (AttributeError, NotImplementedError) as e:
            raise SourceNotAvailable(e)

    def secureRandom(self, nbytes, fallback=False):
        """
        Return a number of secure random bytes.

        @param nbytes: number of bytes to generate.
        @type nbytes: C{int}
        @param fallback: Whether the function should fallback on non-secure
            random or not.  Default to C{False}.
        @type fallback: C{bool}

        @return: a string of random bytes.
        @rtype: C{str}
        """
        try:
            return self._osUrandom(nbytes)
        except SourceNotAvailable:
            pass

        if fallback:
            warnings.warn("urandom unavailable - proceeding with non-cryptographically secure random source",
              category=RuntimeWarning,
              stacklevel=2)
            return self.insecureRandom(nbytes)
        raise SecureRandomNotAvailable("No secure random source available")

    def _randBits(self, nbytes):
        """
        Wrapper around C{os.getrandbits}.
        """
        if self.getrandbits is not None:
            n = self.getrandbits(nbytes * 8)
            hexBytes = "%%0%dx" % (nbytes * 2) % n
            return _fromhex(hexBytes)
        raise SourceNotAvailable("random.getrandbits is not available")

    if _PY3:
        _maketrans = bytes.maketrans

        def _randModule(self, nbytes):
            """
            Wrapper around the C{random} module.
            """
            return (b'').join([bytes([random.choice(self._BYTES)]) for i in range(nbytes)])

    else:
        _maketrans = string.maketrans

        def _randModule(self, nbytes):
            """
            Wrapper around the C{random} module.
            """
            return (b'').join([random.choice(self._BYTES) for i in range(nbytes)])

    _BYTES = _maketrans(b'', b'')

    def insecureRandom(self, nbytes):
        """
        Return a number of non secure random bytes.

        @param nbytes: number of bytes to generate.
        @type nbytes: C{int}

        @return: a string of random bytes.
        @rtype: C{str}
        """
        for src in ('_randBits', '_randModule'):
            try:
                return getattr(self, src)(nbytes)
            except SourceNotAvailable:
                pass


factory = RandomFactory()
secureRandom = factory.secureRandom
insecureRandom = factory.insecureRandom
del factory
__all__ = [
 "secureRandom", "insecureRandom", "SecureRandomNotAvailable"]
