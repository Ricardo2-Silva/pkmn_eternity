# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\_threads\_pool.py
"""
Top level thread pool interface, used to implement
L{twisted.python.threadpool}.
"""
from __future__ import absolute_import, division, print_function
from threading import Thread, Lock, local as LocalStorage
try:
    from Queue import Queue
except ImportError:
    from queue import Queue

from twisted.python.log import err
from ._threadworker import LockWorker
from ._team import Team
from ._threadworker import ThreadWorker

def pool(currentLimit, threadFactory=Thread):
    """
    Construct a L{Team} that spawns threads as a thread pool, with the given
    limiting function.

    @note: Future maintainers: while the public API for the eventual move to
        twisted.threads should look I{something} like this, and while this
        function is necessary to implement the API described by
        L{twisted.python.threadpool}, I am starting to think the idea of a hard
        upper limit on threadpool size is just bad (turning memory performance
        issues into correctness issues well before we run into memory
        pressure), and instead we should build something with reactor
        integration for slowly releasing idle threads when they're not needed
        and I{rate} limiting the creation of new threads rather than just
        hard-capping it.

    @param currentLimit: a callable that returns the current limit on the
        number of workers that the returned L{Team} should create; if it
        already has more workers than that value, no new workers will be
        created.
    @type currentLimit: 0-argument callable returning L{int}

    @param reactor: If passed, the L{IReactorFromThreads} / L{IReactorCore} to
        be used to coordinate actions on the L{Team} itself.  Otherwise, a
        L{LockWorker} will be used.

    @return: a new L{Team}.
    """

    def startThread(target):
        return threadFactory(target=target).start()

    def limitedWorkerCreator():
        stats = team.statistics()
        if stats.busyWorkerCount + stats.idleWorkerCount >= currentLimit():
            return
        else:
            return ThreadWorker(startThread, Queue())

    team = Team(coordinator=(LockWorker(Lock(), LocalStorage())), createWorker=limitedWorkerCreator,
      logException=err)
    return team
