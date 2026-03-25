# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\_threads\_ithreads.py
"""
Interfaces related to threads.
"""
from __future__ import absolute_import, division, print_function
from zope.interface import Interface

class AlreadyQuit(Exception):
    __doc__ = "\n    This worker worker is dead and cannot execute more instructions.\n    "


class IWorker(Interface):
    __doc__ = "\n    A worker that can perform some work concurrently.\n\n    All methods on this interface must be thread-safe.\n    "

    def do(task):
        """
        Perform the given task.

        As an interface, this method makes no specific claims about concurrent
        execution.  An L{IWorker}'s C{do} implementation may defer execution
        for later on the same thread, immediately on a different thread, or
        some combination of the two.  It is valid for a C{do} method to
        schedule C{task} in such a way that it may never be executed.

        It is important for some implementations to provide specific properties
        with respect to where C{task} is executed, of course, and client code
        may rely on a more specific implementation of C{do} than L{IWorker}.

        @param task: a task to call in a thread or other concurrent context.
        @type task: 0-argument callable

        @raise AlreadyQuit: if C{quit} has been called.
        """
        return

    def quit():
        """
        Free any resources associated with this L{IWorker} and cause it to
        reject all future work.

        @raise: L{AlreadyQuit} if this method has already been called.
        """
        return


class IExclusiveWorker(IWorker):
    __doc__ = "\n    Like L{IWorker}, but with the additional guarantee that the callables\n    passed to C{do} will not be called exclusively with each other.\n    "
