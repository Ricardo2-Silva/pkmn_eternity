# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\internet\_idna.py
"""
Shared interface to IDNA encoding and decoding, using the C{idna} PyPI package
if available, otherwise the stdlib implementation.
"""

def _idnaBytes(text):
    """
    Convert some text typed by a human into some ASCII bytes.

    This is provided to allow us to use the U{partially-broken IDNA
    implementation in the standard library <http://bugs.python.org/issue17305>}
    if the more-correct U{idna <https://pypi.python.org/pypi/idna>} package is
    not available; C{service_identity} is somewhat stricter about this.

    @param text: A domain name, hopefully.
    @type text: L{unicode}

    @return: The domain name's IDNA representation, encoded as bytes.
    @rtype: L{bytes}
    """
    try:
        import idna
    except ImportError:
        return text.encode("idna")
    else:
        return idna.encode(text)


def _idnaText(octets):
    """
    Convert some IDNA-encoded octets into some human-readable text.

    Currently only used by the tests.

    @param octets: Some bytes representing a hostname.
    @type octets: L{bytes}

    @return: A human-readable domain name.
    @rtype: L{unicode}
    """
    try:
        import idna
    except ImportError:
        return octets.decode("idna")
    else:
        return idna.decode(octets)
