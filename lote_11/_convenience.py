# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\_threads\_convenience.py
"""
Common functionality used within the implementation of various workers.
"""
from __future__ import absolute_import, division, print_function
from ._ithreads import AlreadyQuit

class Quit(object):
    __doc__ = "\n    A flag representing whether a worker has been quit.\n\n    @ivar isSet: Whether this flag is set.\n    @type isSet: L{bool}\n    "

    def __init__(self):
        """
        Create a L{Quit} un-set.
        """
        self.isSet = False

    def set(self):
        """
        Set the flag if it has not been set.

        @raise AlreadyQuit: If it has been set.
        """
        self.check()
        self.isSet = True

    def check(self):
        """
        Check if the flag has been set.

        @raise AlreadyQuit: If it has been set.
        """
        if self.isSet:
            raise AlreadyQuit()
