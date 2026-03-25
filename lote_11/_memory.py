# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\_threads\_memory.py
"""
Implementation of an in-memory worker that defers execution.
"""
from __future__ import absolute_import, division, print_function
from zope.interface import implementer
from . import IWorker
from ._convenience import Quit
NoMoreWork = object()

@implementer(IWorker)
class MemoryWorker(object):
    __doc__ = "\n    An L{IWorker} that queues work for later performance.\n\n    @ivar _quit: a flag indicating\n    @type _quit: L{Quit}\n    "

    def __init__(self, pending=list):
        """
        Create a L{MemoryWorker}.
        """
        self._quit = Quit()
        self._pending = pending()

    def do(self, work):
        """
        Queue some work for to perform later; see L{createMemoryWorker}.

        @param work: The work to perform.
        """
        self._quit.check()
        self._pending.append(work)

    def quit(self):
        """
        Quit this worker.
        """
        self._quit.set()
        self._pending.append(NoMoreWork)


def createMemoryWorker():
    """
    Create an L{IWorker} that does nothing but defer work, to be performed
    later.

    @return: a worker that will enqueue work to perform later, and a callable
        that will perform one element of that work.
    @rtype: 2-L{tuple} of (L{IWorker}, L{callable})
    """

    def perform():
        if not worker._pending:
            return False
        else:
            if worker._pending[0] is NoMoreWork:
                return False
            worker._pending.pop(0)()
            return True

    worker = MemoryWorker()
    return (worker, perform)
