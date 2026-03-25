# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: asyncio\locks.py
"""Synchronization primitives."""
__all__ = [
 'Lock', 'Event', 'Condition', 'Semaphore', 'BoundedSemaphore']
import collections
from . import compat
from . import events
from . import futures
from .coroutines import coroutine

class _ContextManager:
    __doc__ = "Context manager.\n\n    This enables the following idiom for acquiring and releasing a\n    lock around a block:\n\n        with (yield from lock):\n            <block>\n\n    while failing loudly when accidentally using:\n\n        with lock:\n            <block>\n    "

    def __init__(self, lock):
        self._lock = lock

    def __enter__(self):
        return

    def __exit__(self, *args):
        try:
            self._lock.release()
        finally:
            self._lock = None


class _ContextManagerMixin:

    def __enter__(self):
        raise RuntimeError('"yield from" should be used as context manager expression')

    def __exit__(self, *args):
        return

    @coroutine
    def __iter__(self):
        yield from self.acquire()
        return _ContextManager(self)
        if False:
            yield None

    if compat.PY35:

        def __await__(self):
            yield from self.acquire()
            return _ContextManager(self)
            if False:
                yield None

        @coroutine
        def __aenter__(self):
            yield from self.acquire()
            return
            if False:
                yield None

        @coroutine
        def __aexit__(self, exc_type, exc, tb):
            self.release()


class Lock(_ContextManagerMixin):
    __doc__ = "Primitive lock objects.\n\n    A primitive lock is a synchronization primitive that is not owned\n    by a particular coroutine when locked.  A primitive lock is in one\n    of two states, 'locked' or 'unlocked'.\n\n    It is created in the unlocked state.  It has two basic methods,\n    acquire() and release().  When the state is unlocked, acquire()\n    changes the state to locked and returns immediately.  When the\n    state is locked, acquire() blocks until a call to release() in\n    another coroutine changes it to unlocked, then the acquire() call\n    resets it to locked and returns.  The release() method should only\n    be called in the locked state; it changes the state to unlocked\n    and returns immediately.  If an attempt is made to release an\n    unlocked lock, a RuntimeError will be raised.\n\n    When more than one coroutine is blocked in acquire() waiting for\n    the state to turn to unlocked, only one coroutine proceeds when a\n    release() call resets the state to unlocked; first coroutine which\n    is blocked in acquire() is being processed.\n\n    acquire() is a coroutine and should be called with 'yield from'.\n\n    Locks also support the context management protocol.  '(yield from lock)'\n    should be used as the context manager expression.\n\n    Usage:\n\n        lock = Lock()\n        ...\n        yield from lock\n        try:\n            ...\n        finally:\n            lock.release()\n\n    Context manager usage:\n\n        lock = Lock()\n        ...\n        with (yield from lock):\n             ...\n\n    Lock objects can be tested for locking state:\n\n        if not lock.locked():\n           yield from lock\n        else:\n           # lock is acquired\n           ...\n\n    "

    def __init__(self, *, loop=None):
        self._waiters = collections.deque()
        self._locked = False
        if loop is not None:
            self._loop = loop
        else:
            self._loop = events.get_event_loop()

    def __repr__(self):
        res = super().__repr__()
        extra = "locked" if self._locked else "unlocked"
        if self._waiters:
            extra = "{},waiters:{}".format(extra, len(self._waiters))
        return "<{} [{}]>".format(res[1:-1], extra)

    def locked(self):
        """Return True if lock is acquired."""
        return self._locked

    @coroutine
    def acquire(self):
        """Acquire a lock.

        This method blocks until the lock is unlocked, then sets it to
        locked and returns True.
        """
        if not self._locked and all(w.cancelled() for w in self._waiters):
            self._locked = True
            return True
        else:
            fut = self._loop.create_future()
            self._waiters.append(fut)
            try:
                try:
                    yield from fut
                finally:
                    self._waiters.remove(fut)

            except futures.CancelledError:
                if not self._locked:
                    self._wake_up_first()
                raise

            self._locked = True
            return True
        if False:
            yield None

    def release(self):
        """Release a lock.

        When the lock is locked, reset it to unlocked, and return.
        If any other coroutines are blocked waiting for the lock to become
        unlocked, allow exactly one of them to proceed.

        When invoked on an unlocked lock, a RuntimeError is raised.

        There is no return value.
        """
        if self._locked:
            self._locked = False
            self._wake_up_first()
        else:
            raise RuntimeError("Lock is not acquired.")

    def _wake_up_first(self):
        """Wake up the first waiter if it isn't done."""
        try:
            fut = next(iter(self._waiters))
        except StopIteration:
            return
        else:
            if not fut.done():
                fut.set_result(True)


class Event:
    __doc__ = "Asynchronous equivalent to threading.Event.\n\n    Class implementing event objects. An event manages a flag that can be set\n    to true with the set() method and reset to false with the clear() method.\n    The wait() method blocks until the flag is true. The flag is initially\n    false.\n    "

    def __init__(self, *, loop=None):
        self._waiters = collections.deque()
        self._value = False
        if loop is not None:
            self._loop = loop
        else:
            self._loop = events.get_event_loop()

    def __repr__(self):
        res = super().__repr__()
        extra = "set" if self._value else "unset"
        if self._waiters:
            extra = "{},waiters:{}".format(extra, len(self._waiters))
        return "<{} [{}]>".format(res[1:-1], extra)

    def is_set(self):
        """Return True if and only if the internal flag is true."""
        return self._value

    def set(self):
        """Set the internal flag to true. All coroutines waiting for it to
        become true are awakened. Coroutine that call wait() once the flag is
        true will not block at all.
        """
        if not self._value:
            self._value = True
            for fut in self._waiters:
                if not fut.done():
                    fut.set_result(True)

    def clear(self):
        """Reset the internal flag to false. Subsequently, coroutines calling
        wait() will block until set() is called to set the internal flag
        to true again."""
        self._value = False

    @coroutine
    def wait(self):
        """Block until the internal flag is true.

        If the internal flag is true on entry, return True
        immediately.  Otherwise, block until another coroutine calls
        set() to set the flag to true, then return True.
        """
        if self._value:
            return True
        fut = self._loop.create_future()
        self._waiters.append(fut)
        try:
            yield from fut
            return True
        finally:
            self._waiters.remove(fut)

        if False:
            yield None


class Condition(_ContextManagerMixin):
    __doc__ = "Asynchronous equivalent to threading.Condition.\n\n    This class implements condition variable objects. A condition variable\n    allows one or more coroutines to wait until they are notified by another\n    coroutine.\n\n    A new Lock object is created and used as the underlying lock.\n    "

    def __init__(self, lock=None, *, loop=None):
        if loop is not None:
            self._loop = loop
        else:
            self._loop = events.get_event_loop()
        if lock is None:
            lock = Lock(loop=(self._loop))
        else:
            if lock._loop is not self._loop:
                raise ValueError("loop argument must agree with lock")
        self._lock = lock
        self.locked = lock.locked
        self.acquire = lock.acquire
        self.release = lock.release
        self._waiters = collections.deque()

    def __repr__(self):
        res = super().__repr__()
        extra = "locked" if self.locked() else "unlocked"
        if self._waiters:
            extra = "{},waiters:{}".format(extra, len(self._waiters))
        return "<{} [{}]>".format(res[1:-1], extra)

    @coroutine
    def wait(self):
        """Wait until notified.

        If the calling coroutine has not acquired the lock when this
        method is called, a RuntimeError is raised.

        This method releases the underlying lock, and then blocks
        until it is awakened by a notify() or notify_all() call for
        the same condition variable in another coroutine.  Once
        awakened, it re-acquires the lock and returns True.
        """
        if not self.locked():
            raise RuntimeError("cannot wait on un-acquired lock")
        self.release()
        try:
            fut = self._loop.create_future()
            self._waiters.append(fut)
            try:
                yield from fut
                return True
            finally:
                self._waiters.remove(fut)

        finally:
            cancelled = False
            while True:
                try:
                    yield from self.acquire()
                    break
                except futures.CancelledError:
                    cancelled = True

            if cancelled:
                raise futures.CancelledError

        if False:
            yield None

    @coroutine
    def wait_for(self, predicate):
        """Wait until a predicate becomes true.

        The predicate should be a callable which result will be
        interpreted as a boolean value.  The final predicate value is
        the return value.
        """
        result = predicate()
        while not result:
            yield from self.wait()
            result = predicate()

        return result
        if False:
            yield None

    def notify(self, n=1):
        """By default, wake up one coroutine waiting on this condition, if any.
        If the calling coroutine has not acquired the lock when this method
        is called, a RuntimeError is raised.

        This method wakes up at most n of the coroutines waiting for the
        condition variable; it is a no-op if no coroutines are waiting.

        Note: an awakened coroutine does not actually return from its
        wait() call until it can reacquire the lock. Since notify() does
        not release the lock, its caller should.
        """
        if not self.locked():
            raise RuntimeError("cannot notify on un-acquired lock")
        idx = 0
        for fut in self._waiters:
            if idx >= n:
                break
            if not fut.done():
                idx += 1
                fut.set_result(False)

    def notify_all(self):
        """Wake up all threads waiting on this condition. This method acts
        like notify(), but wakes up all waiting threads instead of one. If the
        calling thread has not acquired the lock when this method is called,
        a RuntimeError is raised.
        """
        self.notify(len(self._waiters))


class Semaphore(_ContextManagerMixin):
    __doc__ = "A Semaphore implementation.\n\n    A semaphore manages an internal counter which is decremented by each\n    acquire() call and incremented by each release() call. The counter\n    can never go below zero; when acquire() finds that it is zero, it blocks,\n    waiting until some other thread calls release().\n\n    Semaphores also support the context management protocol.\n\n    The optional argument gives the initial value for the internal\n    counter; it defaults to 1. If the value given is less than 0,\n    ValueError is raised.\n    "

    def __init__(self, value=1, *, loop=None):
        if value < 0:
            raise ValueError("Semaphore initial value must be >= 0")
        else:
            self._value = value
            self._waiters = collections.deque()
            if loop is not None:
                self._loop = loop
            else:
                self._loop = events.get_event_loop()

    def __repr__(self):
        res = super().__repr__()
        extra = "locked" if self.locked() else "unlocked,value:{}".format(self._value)
        if self._waiters:
            extra = "{},waiters:{}".format(extra, len(self._waiters))
        return "<{} [{}]>".format(res[1:-1], extra)

    def _wake_up_next(self):
        while self._waiters:
            waiter = self._waiters.popleft()
            if not waiter.done():
                waiter.set_result(None)
                return

    def locked(self):
        """Returns True if semaphore can not be acquired immediately."""
        return self._value == 0

    @coroutine
    def acquire(self):
        """Acquire a semaphore.

        If the internal counter is larger than zero on entry,
        decrement it by one and return True immediately.  If it is
        zero on entry, block, waiting until some other coroutine has
        called release() to make it larger than 0, and then return
        True.
        """
        while self._value <= 0:
            fut = self._loop.create_future()
            self._waiters.append(fut)
            try:
                yield from fut
            except:
                fut.cancel()
                if self._value > 0:
                    if not fut.cancelled():
                        self._wake_up_next()
                raise

        self._value -= 1
        return True
        if False:
            yield None

    def release(self):
        """Release a semaphore, incrementing the internal counter by one.
        When it was zero on entry and another coroutine is waiting for it to
        become larger than zero again, wake up that coroutine.
        """
        self._value += 1
        self._wake_up_next()


class BoundedSemaphore(Semaphore):
    __doc__ = "A bounded semaphore implementation.\n\n    This raises ValueError in release() if it would increase the value\n    above the initial value.\n    "

    def __init__(self, value=1, *, loop=None):
        self._bound_value = value
        super().__init__(value, loop=loop)

    def release(self):
        if self._value >= self._bound_value:
            raise ValueError("BoundedSemaphore released too many times")
        super().release()
