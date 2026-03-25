# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\internet\main.py
"""
Backwards compatibility, and utility functions.

In general, this module should not be used, other than by reactor authors
who need to use the 'installReactor' method.
"""
from __future__ import division, absolute_import
from twisted.internet import error
CONNECTION_DONE = error.ConnectionDone("Connection done")
CONNECTION_LOST = error.ConnectionLost("Connection lost")

def installReactor(reactor):
    """
    Install reactor C{reactor}.

    @param reactor: An object that provides one or more IReactor* interfaces.
    """
    import twisted.internet, sys
    if "twisted.internet.reactor" in sys.modules:
        raise error.ReactorAlreadyInstalledError("reactor already installed")
    twisted.internet.reactor = reactor
    sys.modules["twisted.internet.reactor"] = reactor


__all__ = [
 "CONNECTION_LOST", "CONNECTION_DONE", "installReactor"]
