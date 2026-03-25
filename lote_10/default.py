# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\internet\default.py
"""
The most suitable default reactor for the current platform.

Depending on a specific application's needs, some other reactor may in
fact be better.
"""
from __future__ import division, absolute_import
__all__ = [
 "install"]
from twisted.python.runtime import platform

def _getInstallFunction(platform):
    """
    Return a function to install the reactor most suited for the given platform.

    @param platform: The platform for which to select a reactor.
    @type platform: L{twisted.python.runtime.Platform}

    @return: A zero-argument callable which will install the selected
        reactor.
    """
    try:
        if platform.isLinux():
            try:
                from twisted.internet.epollreactor import install
            except ImportError:
                from twisted.internet.pollreactor import install

        elif platform.getType() == "posix":
            if not platform.isMacOSX():
                from twisted.internet.pollreactor import install
            else:
                from twisted.internet.selectreactor import install
    except ImportError:
        from twisted.internet.selectreactor import install

    return install


install = _getInstallFunction(platform)
