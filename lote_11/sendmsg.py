# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\python\sendmsg.py
"""
sendmsg(2) and recvmsg(2) support for Python.
"""
from __future__ import absolute_import, division
from collections import namedtuple
from twisted.python.compat import _PY3
__all__ = [
 "sendmsg", "recvmsg", "getSocketFamily", "SCM_RIGHTS"]
if not _PY3:
    from twisted.python._sendmsg import send1msg, recv1msg
    from twisted.python._sendmsg import getsockfam, SCM_RIGHTS
    __all__ += ["send1msg", "recv1msg", "getsockfam"]
else:
    from socket import SCM_RIGHTS, CMSG_SPACE
RecievedMessage = namedtuple("RecievedMessage", ["data", "ancillary", "flags"])

def sendmsg(socket, data, ancillary=[], flags=0):
    """
    Send a message on a socket.

    @param socket: The socket to send the message on.
    @type socket: L{socket.socket}

    @param data: Bytes to write to the socket.
    @type data: bytes

    @param ancillary: Extra data to send over the socket outside of the normal
        datagram or stream mechanism.  By default no ancillary data is sent.
    @type ancillary: C{list} of C{tuple} of C{int}, C{int}, and C{bytes}.

    @param flags: Flags to affect how the message is sent.  See the C{MSG_}
        constants in the sendmsg(2) manual page.  By default no flags are set.
    @type flags: C{int}

    @return: The return value of the underlying syscall, if it succeeds.
    """
    if _PY3:
        return socket.sendmsg([data], ancillary, flags)
    else:
        return send1msg(socket.fileno(), data, flags, ancillary)


def recvmsg(socket, maxSize=8192, cmsgSize=4096, flags=0):
    """
    Receive a message on a socket.

    @param socket: The socket to receive the message on.
    @type socket: L{socket.socket}

    @param maxSize: The maximum number of bytes to receive from the socket using
        the datagram or stream mechanism. The default maximum is 8192.
    @type maxSize: L{int}

    @param cmsgSize: The maximum number of bytes to receive from the socket
        outside of the normal datagram or stream mechanism. The default maximum
        is 4096.
    @type cmsgSize: L{int}

    @param flags: Flags to affect how the message is sent.  See the C{MSG_}
        constants in the sendmsg(2) manual page. By default no flags are set.
    @type flags: L{int}

    @return: A named 3-tuple of the bytes received using the datagram/stream
        mechanism, a L{list} of L{tuple}s giving ancillary received data, and
        flags as an L{int} describing the data received.
    """
    if _PY3:
        data, ancillary, flags = socket.recvmsg(maxSize, CMSG_SPACE(cmsgSize), flags)[0:3]
    else:
        data, flags, ancillary = recv1msg(socket.fileno(), flags, maxSize, cmsgSize)
    return RecievedMessage(data=data, ancillary=ancillary, flags=flags)


def getSocketFamily(socket):
    """
    Return the family of the given socket.

    @param socket: The socket to get the family of.
    @type socket: L{socket.socket}

    @rtype: L{int}
    """
    if _PY3:
        return socket.family
    else:
        return getsockfam(socket.fileno())
