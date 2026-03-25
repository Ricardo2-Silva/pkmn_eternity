# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\python\threadpool.py
"""
twisted.python.threadpool: a pool of threads to which we dispatch tasks.

In most cases you can just use C{reactor.callInThread} and friends
instead of creating a thread pool directly.
"""
from __future__ import division, absolute_import
import threading
from twisted._threads import pool as _pool
from twisted.python import log, context
from twisted.python.failure import Failure
from twisted.python._oldstyle import _oldStyle
WorkerStop = object()

@_oldStyle
class ThreadPool:
    __doc__ = "\n    This class (hopefully) generalizes the functionality of a pool of threads\n    to which work can be dispatched.\n\n    L{callInThread} and L{stop} should only be called from a single thread.\n\n    @ivar started: Whether or not the thread pool is currently running.\n    @type started: L{bool}\n\n    @ivar threads: List of workers currently running in this thread pool.\n    @type threads: L{list}\n\n    @ivar _pool: A hook for testing.\n    @type _pool: callable compatible with L{_pool}\n    "
    min = 5
    max = 20
    joined = False
    started = False
    workers = 0
    name = None
    threadFactory = threading.Thread
    currentThread = staticmethod(threading.currentThread)
    _pool = staticmethod(_pool)

    def __init__(self, minthreads=5, maxthreads=20, name=None):
        """
        Create a new threadpool.

        @param minthreads: minimum number of threads in the pool
        @type minthreads: L{int}

        @param maxthreads: maximum number of threads in the pool
        @type maxthreads: L{int}

        @param name: The name to give this threadpool; visible in log messages.
        @type name: native L{str}
        """
        if not minthreads >= 0:
            raise AssertionError("minimum is negative")
        elif not minthreads <= maxthreads:
            raise AssertionError("minimum is greater than maximum")
        self.min = minthreads
        self.max = maxthreads
        self.name = name
        self.threads = []

        def trackingThreadFactory(*a, **kw):
            thread = (self.threadFactory)(a, name=self._generateName(), **kw)
            self.threads.append(thread)
            return thread

        def currentLimit():
            if not self.started:
                return 0
            else:
                return self.max

        self._team = self._pool(currentLimit, trackingThreadFactory)

    @property
    def workers(self):
        """
        For legacy compatibility purposes, return a total number of workers.

        @return: the current number of workers, both idle and busy (but not
            those that have been quit by L{ThreadPool.adjustPoolsize})
        @rtype: L{int}
        """
        stats = self._team.statistics()
        return stats.idleWorkerCount + stats.busyWorkerCount

    @property
    def working(self):
        """
        For legacy compatibility purposes, return the number of busy workers as
        expressed by a list the length of that number.

        @return: the number of workers currently processing a work item.
        @rtype: L{list} of L{None}
        """
        return [
         None] * self._team.statistics().busyWorkerCount

    @property
    def waiters(self):
        """
        For legacy compatibility purposes, return the number of idle workers as
        expressed by a list the length of that number.

        @return: the number of workers currently alive (with an allocated
            thread) but waiting for new work.
        @rtype: L{list} of L{None}
        """
        return [
         None] * self._team.statistics().idleWorkerCount

    @property
    def _queue(self):
        """
        For legacy compatibility purposes, return an object with a C{qsize}
        method that indicates the amount of work not yet allocated to a worker.

        @return: an object with a C{qsize} method.
        """

        class NotAQueue(object):

            def qsize(q):
                """
                Pretend to be a Python threading Queue and return the
                number of as-yet-unconsumed tasks.

                @return: the amount of backlogged work not yet dispatched to a
                    worker.
                @rtype: L{int}
                """
                return self._team.statistics().backloggedWorkCount

        return NotAQueue()

    q = _queue

    def start(self):
        """
        Start the threadpool.
        """
        self.joined = False
        self.started = True
        self.adjustPoolsize()
        backlog = self._team.statistics().backloggedWorkCount
        if backlog:
            self._team.grow(backlog)

    def startAWorker(self):
        """
        Increase the number of available workers for the thread pool by 1, up
        to the maximum allowed by L{ThreadPool.max}.
        """
        self._team.grow(1)

    def _generateName(self):
        """
        Generate a name for a new pool thread.

        @return: A distinctive name for the thread.
        @rtype: native L{str}
        """
        return "PoolThread-%s-%s" % (self.name or id(self), self.workers)

    def stopAWorker(self):
        """
        Decrease the number of available workers by 1, by quitting one as soon
        as it's idle.
        """
        self._team.shrink(1)

    def __setstate__(self, state):
        setattr(self, "__dict__", state)
        ThreadPool.__init__(self, self.min, self.max)

    def __getstate__(self):
        state = {}
        state["min"] = self.min
        state["max"] = self.max
        return state

    def callInThread(self, func, *args, **kw):
        """
        Call a callable object in a separate thread.

        @param func: callable object to be called in separate thread

        @param args: positional arguments to be passed to C{func}

        @param kw: keyword args to be passed to C{func}
        """
        (self.callInThreadWithCallback)(None, func, *args, **kw)

    def callInThreadWithCallback(self, onResult, func, *args, **kw):
        """
        Call a callable object in a separate thread and call C{onResult} with
        the return value, or a L{twisted.python.failure.Failure} if the
        callable raises an exception.

        The callable is allowed to block, but the C{onResult} function must not
        block and should perform as little work as possible.

        A typical action for C{onResult} for a threadpool used with a Twisted
        reactor would be to schedule a L{twisted.internet.defer.Deferred} to
        fire in the main reactor thread using C{.callFromThread}.  Note that
        C{onResult} is called inside the separate thread, not inside the
        reactor thread.

        @param onResult: a callable with the signature C{(success, result)}.
            If the callable returns normally, C{onResult} is called with
            C{(True, result)} where C{result} is the return value of the
            callable.  If the callable throws an exception, C{onResult} is
            called with C{(False, failure)}.

            Optionally, C{onResult} may be L{None}, in which case it is not
            called at all.

        @param func: callable object to be called in separate thread

        @param args: positional arguments to be passed to C{func}

        @param kw: keyword arguments to be passed to C{func}
        """
        if self.joined:
            return
        ctx = context.theContextTracker.currentContext().contexts[-1]

        def inContext():
            try:
                result = inContext.theWork()
                ok = True
            except:
                result = Failure()
                ok = False

            inContext.theWork = None
            if inContext.onResult is not None:
                inContext.onResult(ok, result)
                inContext.onResult = None
            elif not ok:
                log.err(result)

        inContext.theWork = lambda: (context.call)(ctx, func, *args, **kw)
        inContext.onResult = onResult
        self._team.do(inContext)

    def stop(self):
        """
        Shutdown the threads in the threadpool.
        """
        self.joined = True
        self.started = False
        self._team.quit()
        for thread in self.threads:
            thread.join()

    def adjustPoolsize(self, minthreads=None, maxthreads=None):
        """
        Adjust the number of available threads by setting C{min} and C{max} to
        new values.

        @param minthreads: The new value for L{ThreadPool.min}.

        @param maxthreads: The new value for L{ThreadPool.max}.
        """
        if minthreads is None:
            minthreads = self.min
        else:
            if maxthreads is None:
                maxthreads = self.max
            else:
                if not minthreads >= 0:
                    raise AssertionError("minimum is negative")
                else:
                    assert minthreads <= maxthreads, "minimum is greater than maximum"
                    self.min = minthreads
                    self.max = maxthreads
                    if not self.started:
                        return
                if self.workers > self.max:
                    self._team.shrink(self.workers - self.max)
            if self.workers < self.min:
                self._team.grow(self.min - self.workers)

    def dumpStats(self):
        """
        Dump some plain-text informational messages to the log about the state
        of this L{ThreadPool}.
        """
        log.msg("waiters: %s" % (self.waiters,))
        log.msg("workers: %s" % (self.working,))
        log.msg("total: %s" % (self.threads,))
