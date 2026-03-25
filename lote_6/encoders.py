# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: email\encoders.py
"""Encodings and related functions."""
__all__ = [
 "encode_7or8bit",
 "encode_base64",
 "encode_noop",
 "encode_quopri"]
from base64 import encodebytes as _bencode
from quopri import encodestring as _encodestring

def _qencode(s):
    enc = _encodestring(s, quotetabs=True)
    return enc.replace(b' ', b'=20')


def encode_base64(msg):
    """Encode the message's payload in Base64.

    Also, add an appropriate Content-Transfer-Encoding header.
    """
    orig = msg.get_payload(decode=True)
    encdata = str(_bencode(orig), "ascii")
    msg.set_payload(encdata)
    msg["Content-Transfer-Encoding"] = "base64"


def encode_quopri(msg):
    """Encode the message's payload in quoted-printable.

    Also, add an appropriate Content-Transfer-Encoding header.
    """
    orig = msg.get_payload(decode=True)
    encdata = _qencode(orig)
    msg.set_payload(encdata)
    msg["Content-Transfer-Encoding"] = "quoted-printable"


def encode_7or8bit(msg):
    """Set the Content-Transfer-Encoding header to 7bit or 8bit."""
    orig = msg.get_payload(decode=True)
    if orig is None:
        msg["Content-Transfer-Encoding"] = "7bit"
        return
    try:
        orig.decode("ascii")
    except UnicodeError:
        msg["Content-Transfer-Encoding"] = "8bit"
    else:
        msg["Content-Transfer-Encoding"] = "7bit"


def encode_noop(msg):
    """Do nothing."""
    return
