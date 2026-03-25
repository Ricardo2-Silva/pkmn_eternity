# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\spread\interfaces.py
"""
Twisted Spread Interfaces.
"""
from zope.interface import Interface

class IJellyable(Interface):

    def jellyFor(jellier):
        """
        Jelly myself for jellier.
        """
        return


class IUnjellyable(Interface):

    def unjellyFor(jellier, jellyList):
        """
        Unjelly myself for the jellier.

        @param jellier: A stateful object which exists for the lifetime of a
        single call to L{unjelly}.

        @param jellyList: The C{list} which represents the jellied state of the
        object to be unjellied.

        @return: The object which results from unjellying.
        """
        return
