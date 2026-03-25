# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\python\systemd.py
"""
Integration with systemd.

Currently only the minimum APIs necessary for using systemd's socket activation
feature are supported.
"""
from __future__ import division, absolute_import
__all__ = [
 "ListenFDs"]
from os import getpid

class ListenFDs(object):
    __doc__ = '\n    L{ListenFDs} provides access to file descriptors inherited from systemd.\n\n    Typically L{ListenFDs.fromEnvironment} should be used to construct a new\n    instance of L{ListenFDs}.\n\n    @cvar _START: File descriptors inherited from systemd are always\n        consecutively numbered, with a fixed lowest "starting" descriptor.  This\n        gives the default starting descriptor.  Since this must agree with the\n        value systemd is using, it typically should not be overridden.\n    @type _START: C{int}\n\n    @ivar _descriptors: A C{list} of C{int} giving the descriptors which were\n        inherited.\n    '
    _START = 3

    def __init__(self, descriptors):
        """
        @param descriptors: The descriptors which will be returned from calls to
            C{inheritedDescriptors}.
        """
        self._descriptors = descriptors

    @classmethod
    def fromEnvironment(cls, environ=None, start=None):
        """
        @param environ: A dictionary-like object to inspect to discover
            inherited descriptors.  By default, L{None}, indicating that the
            real process environment should be inspected.  The default is
            suitable for typical usage.

        @param start: An integer giving the lowest value of an inherited
            descriptor systemd will give us.  By default, L{None}, indicating
            the known correct (that is, in agreement with systemd) value will be
            used.  The default is suitable for typical usage.

        @return: A new instance of C{cls} which can be used to look up the
            descriptors which have been inherited.
        """
        if environ is None:
            from os import environ
        if start is None:
            start = cls._START
        descriptors = []
        try:
            pid = int(environ["LISTEN_PID"])
        except (KeyError, ValueError):
            pass
        else:
            if pid == getpid():
                try:
                    count = int(environ["LISTEN_FDS"])
                except (KeyError, ValueError):
                    pass
                else:
                    descriptors = range(start, start + count)
                    del environ["LISTEN_PID"]
                    del environ["LISTEN_FDS"]
            return cls(descriptors)

    def inheritedDescriptors(self):
        """
        @return: The configured list of descriptors.
        """
        return list(self._descriptors)
