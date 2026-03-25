# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\internet\stdio.py
"""
Standard input/out/err support.

This module exposes one name, StandardIO, which is a factory that takes an
IProtocol provider as an argument.  It connects that protocol to standard input
and output on the current process.

It should work on any UNIX and also on Win32 (with some caveats: due to
platform limitations, it will perform very poorly on Win32).

Future Plans::

    support for stderr, perhaps
    Rewrite to use the reactor instead of an ad-hoc mechanism for connecting
        protocols to transport.

Maintainer: James Y Knight
"""
from __future__ import absolute_import, division
from twisted.python.runtime import platform
if platform.isWindows():
    from twisted.internet import _win32stdio
    StandardIO = _win32stdio.StandardIO
    PipeAddress = _win32stdio.Win32PipeAddress
else:
    from twisted.internet._posixstdio import StandardIO, PipeAddress
__all__ = [
 "StandardIO", "PipeAddress"]
