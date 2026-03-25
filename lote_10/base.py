# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\internet\base.py
"""
Very basic functionality for a Reactor implementation.
"""
from __future__ import division, absolute_import
import socket
from zope.interface import implementer, classImplements
import sys, warnings
from heapq import heappush, heappop, heapify
import traceback
from twisted.internet.interfaces import IReactorCore, IReactorTime, IReactorThreads, IResolverSimple, IReactorPluggableResolver, IReactorPluggableNameResolver, IConnector, IDelayedCall, _ISupportsExitSignalCapturing
from twisted.internet import fdesc, main, error, abstract, defer, threads
from twisted.internet._resolver import GAIResolver as _GAIResolver, ComplexResolverSimplifier as _ComplexResolverSimplifier, SimpleResolverComplexifier as _SimpleResolverComplexifier
from twisted.python import log, failure, reflect
from twisted.python.compat import unicode, iteritems
from twisted.python.runtime import seconds as runtimeSeconds, platform
from twisted.internet.defer import Deferred, DeferredList
from twisted.python._oldstyle import _oldStyle
from twisted.python import threadable

@implementer(IDelayedCall)
@_oldStyle
class DelayedCall:
    debug = False
    _repr = None

    def __init__(self, time, func, args, kw, cancel, reset, seconds=runtimeSeconds):
        """
        @param time: Seconds from the epoch at which to call C{func}.
        @param func: The callable to call.
        @param args: The positional arguments to pass to the callable.
        @param kw: The keyword arguments to pass to the callable.
        @param cancel: A callable which will be called with this
            DelayedCall before cancellation.
        @param reset: A callable which will be called with this
            DelayedCall after changing this DelayedCall's scheduled
            execution time. The callable should adjust any necessary
            scheduling details to ensure this DelayedCall is invoked
            at the new appropriate time.
        @param seconds: If provided, a no-argument callable which will be
            used to determine the current time any time that information is
            needed.
        """
        self.time, self.func, self.args, self.kw = (
         time, func, args, kw)
        self.resetter = reset
        self.canceller = cancel
        self.seconds = seconds
        self.cancelled = self.called = 0
        self.delayed_time = 0
        if self.debug:
            self.creator = traceback.format_stack()[:-2]

    def getTime(self):
        """Return the time at which this call will fire

        @rtype: C{float}
        @return: The number of seconds after the epoch at which this call is
        scheduled to be made.
        """
        return self.time + self.delayed_time

    def cancel(self):
        """Unschedule this call

        @raise AlreadyCancelled: Raised if this call has already been
        unscheduled.

        @raise AlreadyCalled: Raised if this call has already been made.
        """
        if self.cancelled:
            raise error.AlreadyCancelled
        elif self.called:
            raise error.AlreadyCalled
        else:
            self.canceller(self)
            self.cancelled = 1
            if self.debug:
                self._repr = repr(self)
            del self.func
            del self.args
            del self.kw

    def reset(self, secondsFromNow):
        """Reschedule this call for a different time

        @type secondsFromNow: C{float}
        @param secondsFromNow: The number of seconds from the time of the
        C{reset} call at which this call will be scheduled.

        @raise AlreadyCancelled: Raised if this call has been cancelled.
        @raise AlreadyCalled: Raised if this call has already been made.
        """
        if self.cancelled:
            raise error.AlreadyCancelled
        elif self.called:
            raise error.AlreadyCalled
        else:
            newTime = self.seconds() + secondsFromNow
            if newTime < self.time:
                self.delayed_time = 0
                self.time = newTime
                self.resetter(self)
            else:
                self.delayed_time = newTime - self.time

    def delay(self, secondsLater):
        """Reschedule this call for a later time

        @type secondsLater: C{float}
        @param secondsLater: The number of seconds after the originally
        scheduled time for which to reschedule this call.

        @raise AlreadyCancelled: Raised if this call has been cancelled.
        @raise AlreadyCalled: Raised if this call has already been made.
        """
        if self.cancelled:
            raise error.AlreadyCancelled
        elif self.called:
            raise error.AlreadyCalled
        else:
            self.delayed_time += secondsLater
        if self.delayed_time < 0:
            self.activate_delay()
            self.resetter(self)

    def activate_delay(self):
        self.time += self.delayed_time
        self.delayed_time = 0

    def active(self):
        """Determine whether this call is still pending

        @rtype: C{bool}
        @return: True if this call has not yet been made or cancelled,
        False otherwise.
        """
        return not (self.cancelled or self.called)

    def __le__(self, other):
        """
        Implement C{<=} operator between two L{DelayedCall} instances.

        Comparison is based on the C{time} attribute (unadjusted by the
        delayed time).
        """
        return self.time <= other.time

    def __lt__(self, other):
        """
        Implement C{<} operator between two L{DelayedCall} instances.

        Comparison is based on the C{time} attribute (unadjusted by the
        delayed time).
        """
        return self.time < other.time

    def __repr__(self):
        """
        Implement C{repr()} for L{DelayedCall} instances.

        @rtype: C{str}
        @returns: String containing details of the L{DelayedCall}.
        """
        if self._repr is not None:
            return self._repr
        else:
            if hasattr(self, "func"):
                if hasattr(self.func, "__qualname__"):
                    func = self.func.__qualname__
            else:
                if hasattr(self.func, "__name__"):
                    func = self.func.func_name
                    if hasattr(self.func, "im_class"):
                        func = self.func.im_class.__name__ + "." + func
                    else:
                        func = reflect.safe_repr(self.func)
                else:
                    func = None
                now = self.seconds()
                L = [
                 "<DelayedCall 0x%x [%ss] called=%s cancelled=%s" % (
                  id(self), self.time - now, self.called,
                  self.cancelled)]
                if func is not None:
                    L.extend((" ", func, "("))
                    if self.args:
                        L.append(", ".join([reflect.safe_repr(e) for e in self.args]))
                        if self.kw:
                            L.append(", ")
                    if self.kw:
                        L.append(", ".join(["%s=%s" % (k, reflect.safe_repr(v)) for k, v in self.kw.items()]))
                    L.append(")")
                if self.debug:
                    L.append("\n\ntraceback at creation: \n\n%s" % "    ".join(self.creator))
                L.append(">")
            return "".join(L)


@implementer(IResolverSimple)
class ThreadedResolver(object):
    __doc__ = "\n    L{ThreadedResolver} uses a reactor, a threadpool, and\n    L{socket.gethostbyname} to perform name lookups without blocking the\n    reactor thread.  It also supports timeouts indepedently from whatever\n    timeout logic L{socket.gethostbyname} might have.\n\n    @ivar reactor: The reactor the threadpool of which will be used to call\n        L{socket.gethostbyname} and the I/O thread of which the result will be\n        delivered.\n    "

    def __init__(self, reactor):
        self.reactor = reactor
        self._runningQueries = {}

    def _fail(self, name, err):
        err = error.DNSLookupError("address %r not found: %s" % (name, err))
        return failure.Failure(err)

    def _cleanup(self, name, lookupDeferred):
        userDeferred, cancelCall = self._runningQueries[lookupDeferred]
        del self._runningQueries[lookupDeferred]
        userDeferred.errback(self._fail(name, "timeout error"))

    def _checkTimeout(self, result, name, lookupDeferred):
        try:
            userDeferred, cancelCall = self._runningQueries[lookupDeferred]
        except KeyError:
            pass
        else:
            del self._runningQueries[lookupDeferred]
            cancelCall.cancel()
            if isinstance(result, failure.Failure):
                userDeferred.errback(self._fail(name, result.getErrorMessage()))
            else:
                userDeferred.callback(result)

    def getHostByName(self, name, timeout=(1, 3, 11, 45)):
        """
        See L{twisted.internet.interfaces.IResolverSimple.getHostByName}.

        Note that the elements of C{timeout} are summed and the result is used
        as a timeout for the lookup.  Any intermediate timeout or retry logic
        is left up to the platform via L{socket.gethostbyname}.
        """
        if timeout:
            timeoutDelay = sum(timeout)
        else:
            timeoutDelay = 60
        userDeferred = defer.Deferred()
        lookupDeferred = threads.deferToThreadPool(self.reactor, self.reactor.getThreadPool(), socket.gethostbyname, name)
        cancelCall = self.reactor.callLater(timeoutDelay, self._cleanup, name, lookupDeferred)
        self._runningQueries[lookupDeferred] = (userDeferred, cancelCall)
        lookupDeferred.addBoth(self._checkTimeout, name, lookupDeferred)
        return userDeferred


@implementer(IResolverSimple)
@_oldStyle
class BlockingResolver:

    def getHostByName(self, name, timeout=(1, 3, 11, 45)):
        try:
            address = socket.gethostbyname(name)
        except socket.error:
            msg = "address %r not found" % (name,)
            err = error.DNSLookupError(msg)
            return defer.fail(err)
        else:
            return defer.succeed(address)


class _ThreePhaseEvent(object):
    __doc__ = "\n    Collection of callables (with arguments) which can be invoked as a group in\n    a particular order.\n\n    This provides the underlying implementation for the reactor's system event\n    triggers.  An instance of this class tracks triggers for all phases of a\n    single type of event.\n\n    @ivar before: A list of the before-phase triggers containing three-tuples\n        of a callable, a tuple of positional arguments, and a dict of keyword\n        arguments\n\n    @ivar finishedBefore: A list of the before-phase triggers which have\n        already been executed.  This is only populated in the C{'BEFORE'} state.\n\n    @ivar during: A list of the during-phase triggers containing three-tuples\n        of a callable, a tuple of positional arguments, and a dict of keyword\n        arguments\n\n    @ivar after: A list of the after-phase triggers containing three-tuples\n        of a callable, a tuple of positional arguments, and a dict of keyword\n        arguments\n\n    @ivar state: A string indicating what is currently going on with this\n        object.  One of C{'BASE'} (for when nothing in particular is happening;\n        this is the initial value), C{'BEFORE'} (when the before-phase triggers\n        are in the process of being executed).\n    "

    def __init__(self):
        self.before = []
        self.during = []
        self.after = []
        self.state = "BASE"

    def addTrigger(self, phase, callable, *args, **kwargs):
        """
        Add a trigger to the indicate phase.

        @param phase: One of C{'before'}, C{'during'}, or C{'after'}.

        @param callable: An object to be called when this event is triggered.
        @param *args: Positional arguments to pass to C{callable}.
        @param **kwargs: Keyword arguments to pass to C{callable}.

        @return: An opaque handle which may be passed to L{removeTrigger} to
            reverse the effects of calling this method.
        """
        if phase not in ('before', 'during', 'after'):
            raise KeyError("invalid phase")
        getattr(self, phase).append((callable, args, kwargs))
        return (phase, callable, args, kwargs)

    def removeTrigger(self, handle):
        """
        Remove a previously added trigger callable.

        @param handle: An object previously returned by L{addTrigger}.  The
            trigger added by that call will be removed.

        @raise ValueError: If the trigger associated with C{handle} has already
            been removed or if C{handle} is not a valid handle.
        """
        return getattr(self, "removeTrigger_" + self.state)(handle)

    def removeTrigger_BASE(self, handle):
        """
        Just try to remove the trigger.

        @see: removeTrigger
        """
        try:
            phase, callable, args, kwargs = handle
        except (TypeError, ValueError):
            raise ValueError("invalid trigger handle")
        else:
            if phase not in ('before', 'during', 'after'):
                raise KeyError("invalid phase")
            getattr(self, phase).remove((callable, args, kwargs))

    def removeTrigger_BEFORE(self, handle):
        """
        Remove the trigger if it has yet to be executed, otherwise emit a
        warning that in the future an exception will be raised when removing an
        already-executed trigger.

        @see: removeTrigger
        """
        phase, callable, args, kwargs = handle
        if phase != "before":
            return self.removeTrigger_BASE(handle)
        elif (
         callable, args, kwargs) in self.finishedBefore:
            warnings.warn("Removing already-fired system event triggers will raise an exception in a future version of Twisted.",
              category=DeprecationWarning,
              stacklevel=3)
        else:
            self.removeTrigger_BASE(handle)

    def fireEvent(self):
        """
        Call the triggers added to this event.
        """
        self.state = "BEFORE"
        self.finishedBefore = []
        beforeResults = []
        while self.before:
            callable, args, kwargs = self.before.pop(0)
            self.finishedBefore.append((callable, args, kwargs))
            try:
                result = callable(*args, **kwargs)
            except:
                log.err()

            if isinstance(result, Deferred):
                beforeResults.append(result)

        DeferredList(beforeResults).addCallback(self._continueFiring)

    def _continueFiring(self, ignored):
        """
        Call the during and after phase triggers for this event.
        """
        self.state = "BASE"
        self.finishedBefore = []
        for phase in (self.during, self.after):
            while phase:
                callable, args, kwargs = phase.pop(0)
                try:
                    callable(*args, **kwargs)
                except:
                    log.err()


@implementer(IReactorPluggableNameResolver, IReactorPluggableResolver)
class PluggableResolverMixin(object):
    __doc__ = "\n    A mixin which implements the pluggable resolver reactor interfaces.\n\n    @ivar resolver: The installed L{IResolverSimple}.\n    @ivar _nameResolver: The installed L{IHostnameResolver}.\n    "
    resolver = BlockingResolver()
    _nameResolver = _SimpleResolverComplexifier(resolver)

    def installResolver(self, resolver):
        """
        See L{IReactorPluggableResolver}.

        @param resolver: see L{IReactorPluggableResolver}.

        @return: see L{IReactorPluggableResolver}.
        """
        assert IResolverSimple.providedBy(resolver)
        oldResolver = self.resolver
        self.resolver = resolver
        self._nameResolver = _SimpleResolverComplexifier(resolver)
        return oldResolver

    def installNameResolver(self, resolver):
        """
        See L{IReactorPluggableNameResolver}.

        @param resolver: See L{IReactorPluggableNameResolver}.

        @return: see L{IReactorPluggableNameResolver}.
        """
        previousNameResolver = self._nameResolver
        self._nameResolver = resolver
        self.resolver = _ComplexResolverSimplifier(resolver)
        return previousNameResolver

    @property
    def nameResolver(self):
        """
        Implementation of read-only
        L{IReactorPluggableNameResolver.nameResolver}.
        """
        return self._nameResolver


@implementer(IReactorCore, IReactorTime, _ISupportsExitSignalCapturing)
class ReactorBase(PluggableResolverMixin):
    __doc__ = "\n    Default base class for Reactors.\n\n    @type _stopped: C{bool}\n    @ivar _stopped: A flag which is true between paired calls to C{reactor.run}\n        and C{reactor.stop}.  This should be replaced with an explicit state\n        machine.\n\n    @type _justStopped: C{bool}\n    @ivar _justStopped: A flag which is true between the time C{reactor.stop}\n        is called and the time the shutdown system event is fired.  This is\n        used to determine whether that event should be fired after each\n        iteration through the mainloop.  This should be replaced with an\n        explicit state machine.\n\n    @type _started: C{bool}\n    @ivar _started: A flag which is true from the time C{reactor.run} is called\n        until the time C{reactor.run} returns.  This is used to prevent calls\n        to C{reactor.run} on a running reactor.  This should be replaced with\n        an explicit state machine.\n\n    @ivar running: See L{IReactorCore.running}\n\n    @ivar _registerAsIOThread: A flag controlling whether the reactor will\n        register the thread it is running in as the I/O thread when it starts.\n        If C{True}, registration will be done, otherwise it will not be.\n\n    @ivar _exitSignal: See L{_ISupportsExitSignalCapturing._exitSignal}\n    "
    _registerAsIOThread = True
    _stopped = True
    installed = False
    usingThreads = False
    _exitSignal = None
    __name__ = "twisted.internet.reactor"

    def __init__(self):
        super(ReactorBase, self).__init__()
        self.threadCallQueue = []
        self._eventTriggers = {}
        self._pendingTimedCalls = []
        self._newTimedCalls = []
        self._cancellations = 0
        self.running = False
        self._started = False
        self._justStopped = False
        self._startedBefore = False
        self._internalReaders = set()
        self.waker = None
        self.addSystemEventTrigger("during", "startup", self._reallyStartRunning)
        self.addSystemEventTrigger("during", "shutdown", self.crash)
        self.addSystemEventTrigger("during", "shutdown", self.disconnectAll)
        if platform.supportsThreads():
            self._initThreads()
        self.installWaker()

    _lock = None

    def installWaker(self):
        raise NotImplementedError(reflect.qual(self.__class__) + " did not implement installWaker")

    def wakeUp(self):
        """
        Wake up the event loop.
        """
        if self.waker:
            self.waker.wakeUp()

    def doIteration(self, delay):
        """
        Do one iteration over the readers and writers which have been added.
        """
        raise NotImplementedError(reflect.qual(self.__class__) + " did not implement doIteration")

    def addReader(self, reader):
        raise NotImplementedError(reflect.qual(self.__class__) + " did not implement addReader")

    def addWriter(self, writer):
        raise NotImplementedError(reflect.qual(self.__class__) + " did not implement addWriter")

    def removeReader(self, reader):
        raise NotImplementedError(reflect.qual(self.__class__) + " did not implement removeReader")

    def removeWriter(self, writer):
        raise NotImplementedError(reflect.qual(self.__class__) + " did not implement removeWriter")

    def removeAll(self):
        raise NotImplementedError(reflect.qual(self.__class__) + " did not implement removeAll")

    def getReaders(self):
        raise NotImplementedError(reflect.qual(self.__class__) + " did not implement getReaders")

    def getWriters(self):
        raise NotImplementedError(reflect.qual(self.__class__) + " did not implement getWriters")

    def resolve(self, name, timeout=(1, 3, 11, 45)):
        """Return a Deferred that will resolve a hostname.
        """
        if not name:
            return defer.succeed("0.0.0.0")
        else:
            if abstract.isIPAddress(name):
                return defer.succeed(name)
            return self.resolver.getHostByName(name, timeout)

    def stop(self):
        """
        See twisted.internet.interfaces.IReactorCore.stop.
        """
        if self._stopped:
            raise error.ReactorNotRunning("Can't stop reactor that isn't running.")
        self._stopped = True
        self._justStopped = True
        self._startedBefore = True

    def crash(self):
        """
        See twisted.internet.interfaces.IReactorCore.crash.

        Reset reactor state tracking attributes and re-initialize certain
        state-transition helpers which were set up in C{__init__} but later
        destroyed (through use).
        """
        self._started = False
        self.running = False
        self.addSystemEventTrigger("during", "startup", self._reallyStartRunning)

    def sigInt(self, *args):
        """
        Handle a SIGINT interrupt.

        @param args: See handler specification in L{signal.signal}
        """
        log.msg("Received SIGINT, shutting down.")
        self.callFromThread(self.stop)
        self._exitSignal = args[0]

    def sigBreak(self, *args):
        """
        Handle a SIGBREAK interrupt.

        @param args: See handler specification in L{signal.signal}
        """
        log.msg("Received SIGBREAK, shutting down.")
        self.callFromThread(self.stop)
        self._exitSignal = args[0]

    def sigTerm(self, *args):
        """
        Handle a SIGTERM interrupt.

        @param args: See handler specification in L{signal.signal}
        """
        log.msg("Received SIGTERM, shutting down.")
        self.callFromThread(self.stop)
        self._exitSignal = args[0]

    def disconnectAll(self):
        """Disconnect every reader, and writer in the system.
        """
        selectables = self.removeAll()
        for reader in selectables:
            log.callWithLogger(reader, reader.connectionLost, failure.Failure(main.CONNECTION_LOST))

    def iterate(self, delay=0):
        """See twisted.internet.interfaces.IReactorCore.iterate.
        """
        self.runUntilCurrent()
        self.doIteration(delay)

    def fireSystemEvent(self, eventType):
        """See twisted.internet.interfaces.IReactorCore.fireSystemEvent.
        """
        event = self._eventTriggers.get(eventType)
        if event is not None:
            event.fireEvent()

    def addSystemEventTrigger(self, _phase, _eventType, _f, *args, **kw):
        """See twisted.internet.interfaces.IReactorCore.addSystemEventTrigger.
        """
        assert callable(_f), "%s is not callable" % _f
        if _eventType not in self._eventTriggers:
            self._eventTriggers[_eventType] = _ThreePhaseEvent()
        return (
         _eventType,
         (self._eventTriggers[_eventType].addTrigger)(
 _phase, _f, *args, **kw))

    def removeSystemEventTrigger(self, triggerID):
        """See twisted.internet.interfaces.IReactorCore.removeSystemEventTrigger.
        """
        eventType, handle = triggerID
        self._eventTriggers[eventType].removeTrigger(handle)

    def callWhenRunning(self, _callable, *args, **kw):
        """See twisted.internet.interfaces.IReactorCore.callWhenRunning.
        """
        if self.running:
            _callable(*args, **kw)
        else:
            return (self.addSystemEventTrigger)("after", "startup",
 _callable, *args, **kw)

    def startRunning(self):
        """
        Method called when reactor starts: do some initialization and fire
        startup events.

        Don't call this directly, call reactor.run() instead: it should take
        care of calling this.

        This method is somewhat misnamed.  The reactor will not necessarily be
        in the running state by the time this method returns.  The only
        guarantee is that it will be on its way to the running state.
        """
        if self._started:
            raise error.ReactorAlreadyRunning()
        elif self._startedBefore:
            raise error.ReactorNotRestartable()
        self._started = True
        self._stopped = False
        if self._registerAsIOThread:
            threadable.registerAsIOThread()
        self.fireSystemEvent("startup")

    def _reallyStartRunning(self):
        """
        Method called to transition to the running state.  This should happen
        in the I{during startup} event trigger phase.
        """
        self.running = True

    seconds = staticmethod(runtimeSeconds)

    def callLater(self, _seconds, _f, *args, **kw):
        """See twisted.internet.interfaces.IReactorTime.callLater.
        """
        if not callable(_f):
            raise AssertionError("%s is not callable" % _f)
        elif not _seconds >= 0:
            raise AssertionError("%s is not greater than or equal to 0 seconds" % (_seconds,))
        tple = DelayedCall((self.seconds() + _seconds), _f, args, kw, (self._cancelCallLater),
          (self._moveCallLaterSooner),
          seconds=(self.seconds))
        self._newTimedCalls.append(tple)
        return tple

    def _moveCallLaterSooner(self, tple):
        heap = self._pendingTimedCalls
        try:
            pos = heap.index(tple)
            elt = heap[pos]
            while pos != 0:
                parent = (pos - 1) // 2
                if heap[parent] <= elt:
                    break
                heap[pos] = heap[parent]
                pos = parent

            heap[pos] = elt
        except ValueError:
            pass

    def _cancelCallLater(self, tple):
        self._cancellations += 1

    def getDelayedCalls(self):
        """
        Return all the outstanding delayed calls in the system.
        They are returned in no particular order.
        This method is not efficient -- it is really only meant for
        test cases.

        @return: A list of outstanding delayed calls.
        @type: L{list} of L{DelayedCall}
        """
        return [x for x in self._pendingTimedCalls + self._newTimedCalls if not x.cancelled]

    def _insertNewDelayedCalls(self):
        for call in self._newTimedCalls:
            if call.cancelled:
                self._cancellations -= 1
            else:
                call.activate_delay()
                heappush(self._pendingTimedCalls, call)

        self._newTimedCalls = []

    def timeout(self):
        """
        Determine the longest time the reactor may sleep (waiting on I/O
        notification, perhaps) before it must wake up to service a time-related
        event.

        @return: The maximum number of seconds the reactor may sleep.
        @rtype: L{float}
        """
        self._insertNewDelayedCalls()
        if not self._pendingTimedCalls:
            return
        else:
            delay = self._pendingTimedCalls[0].time - self.seconds()
            longest = 2147483
            return max(0, min(longest, delay))

    def runUntilCurrent(self):
        """
        Run all pending timed calls.
        """
        if self.threadCallQueue:
            count = 0
            total = len(self.threadCallQueue)
            for f, a, kw in self.threadCallQueue:
                try:
                    f(*a, **kw)
                except:
                    log.err()

                count += 1
                if count == total:
                    break

            del self.threadCallQueue[:count]
            if self.threadCallQueue:
                self.wakeUp()
        else:
            self._insertNewDelayedCalls()
            now = self.seconds()
            while self._pendingTimedCalls and self._pendingTimedCalls[0].time <= now:
                call = heappop(self._pendingTimedCalls)
                if call.cancelled:
                    self._cancellations -= 1
                elif call.delayed_time > 0:
                    call.activate_delay()
                    heappush(self._pendingTimedCalls, call)
                else:
                    try:
                        call.called = 1
                        (call.func)(*call.args, **call.kw)
                    except:
                        log.deferr()
                        if hasattr(call, "creator"):
                            e = "\n"
                            e += " C: previous exception occurred in a DelayedCall created here:\n"
                            e += " C:"
                            e += "".join(call.creator).rstrip().replace("\n", "\n C:")
                            e += "\n"
                            log.msg(e)

            if self._cancellations > 50:
                if self._cancellations > len(self._pendingTimedCalls) >> 1:
                    self._cancellations = 0
                    self._pendingTimedCalls = [x for x in self._pendingTimedCalls if not x.cancelled]
                    heapify(self._pendingTimedCalls)
            if self._justStopped:
                self._justStopped = False
                self.fireSystemEvent("shutdown")

    def _checkProcessArgs(self, args, env):
        """
        Check for valid arguments and environment to spawnProcess.

        @return: A two element tuple giving values to use when creating the
        process.  The first element of the tuple is a C{list} of C{bytes}
        giving the values for argv of the child process.  The second element
        of the tuple is either L{None} if C{env} was L{None} or a C{dict}
        mapping C{bytes} environment keys to C{bytes} environment values.
        """
        defaultEncoding = sys.getfilesystemencoding()

        def argChecker(arg):
            """
            Return either L{bytes} or L{None}.  If the given value is not
            allowable for some reason, L{None} is returned.  Otherwise, a
            possibly different object which should be used in place of arg is
            returned.  This forces unicode encoding to happen now, rather than
            implicitly later.
            """
            if isinstance(arg, unicode):
                try:
                    arg = arg.encode(defaultEncoding)
                except UnicodeEncodeError:
                    return

            if isinstance(arg, bytes):
                if b'\x00' not in arg:
                    return arg
            return

        if not isinstance(args, (tuple, list)):
            raise TypeError("Arguments must be a tuple or list")
        outputArgs = []
        for arg in args:
            arg = argChecker(arg)
            if arg is None:
                raise TypeError("Arguments contain a non-string value")
            else:
                outputArgs.append(arg)

        outputEnv = None
        if env is not None:
            outputEnv = {}
            for key, val in iteritems(env):
                key = argChecker(key)
                if key is None:
                    raise TypeError("Environment contains a non-string key")
                val = argChecker(val)
                if val is None:
                    raise TypeError("Environment contains a non-string value")
                outputEnv[key] = val

        return (
         outputArgs, outputEnv)

    if platform.supportsThreads():
        threadpool = None
        _threadpoolStartupID = None
        threadpoolShutdownID = None

        def _initThreads(self):
            self.installNameResolver(_GAIResolver(self, self.getThreadPool))
            self.usingThreads = True

        def callFromThread(self, f, *args, **kw):
            """
            See
            L{twisted.internet.interfaces.IReactorFromThreads.callFromThread}.
            """
            assert callable(f), "%s is not callable" % (f,)
            self.threadCallQueue.append((f, args, kw))
            self.wakeUp()

        def _initThreadPool(self):
            """
            Create the threadpool accessible with callFromThread.
            """
            from twisted.python import threadpool
            self.threadpool = threadpool.ThreadPool(0, 10, "twisted.internet.reactor")
            self._threadpoolStartupID = self.callWhenRunning(self.threadpool.start)
            self.threadpoolShutdownID = self.addSystemEventTrigger("during", "shutdown", self._stopThreadPool)

        def _uninstallHandler(self):
            return

        def _stopThreadPool(self):
            """
            Stop the reactor threadpool.  This method is only valid if there
            is currently a threadpool (created by L{_initThreadPool}).  It
            is not intended to be called directly; instead, it will be
            called by a shutdown trigger created in L{_initThreadPool}.
            """
            triggers = [
             self._threadpoolStartupID, self.threadpoolShutdownID]
            for trigger in filter(None, triggers):
                try:
                    self.removeSystemEventTrigger(trigger)
                except ValueError:
                    pass

            self._threadpoolStartupID = None
            self.threadpoolShutdownID = None
            self.threadpool.stop()
            self.threadpool = None

        def getThreadPool(self):
            """
            See L{twisted.internet.interfaces.IReactorThreads.getThreadPool}.
            """
            if self.threadpool is None:
                self._initThreadPool()
            return self.threadpool

        def callInThread(self, _callable, *args, **kwargs):
            """
            See L{twisted.internet.interfaces.IReactorInThreads.callInThread}.
            """
            (self.getThreadPool().callInThread)(_callable, *args, **kwargs)

        def suggestThreadPoolSize(self, size):
            """
            See L{twisted.internet.interfaces.IReactorThreads.suggestThreadPoolSize}.
            """
            self.getThreadPool().adjustPoolsize(maxthreads=size)

    else:

        def callFromThread(self, f, *args, **kw):
            assert callable(f), "%s is not callable" % (f,)
            self.threadCallQueue.append((f, args, kw))


if platform.supportsThreads():
    classImplements(ReactorBase, IReactorThreads)

@implementer(IConnector)
@_oldStyle
class BaseConnector:
    __doc__ = 'Basic implementation of connector.\n\n    State can be: "connecting", "connected", "disconnected"\n    '
    timeoutID = None
    factoryStarted = 0

    def __init__(self, factory, timeout, reactor):
        self.state = "disconnected"
        self.reactor = reactor
        self.factory = factory
        self.timeout = timeout

    def disconnect(self):
        """Disconnect whatever our state is."""
        if self.state == "connecting":
            self.stopConnecting()
        elif self.state == "connected":
            self.transport.loseConnection()

    def connect(self):
        """Start connection to remote server."""
        if self.state != "disconnected":
            raise RuntimeError("can't connect in this state")
        else:
            self.state = "connecting"
            if not self.factoryStarted:
                self.factory.doStart()
                self.factoryStarted = 1
            self.transport = transport = self._makeTransport()
            if self.timeout is not None:
                self.timeoutID = self.reactor.callLater(self.timeout, transport.failIfNotConnected, error.TimeoutError())
        self.factory.startedConnecting(self)

    def stopConnecting(self):
        """Stop attempting to connect."""
        if self.state != "connecting":
            raise error.NotConnectingError("we're not trying to connect")
        self.state = "disconnected"
        self.transport.failIfNotConnected(error.UserError())
        del self.transport

    def cancelTimeout(self):
        if self.timeoutID is not None:
            try:
                self.timeoutID.cancel()
            except ValueError:
                pass

            del self.timeoutID

    def buildProtocol(self, addr):
        self.state = "connected"
        self.cancelTimeout()
        return self.factory.buildProtocol(addr)

    def connectionFailed(self, reason):
        self.cancelTimeout()
        self.transport = None
        self.state = "disconnected"
        self.factory.clientConnectionFailed(self, reason)
        if self.state == "disconnected":
            self.factory.doStop()
            self.factoryStarted = 0

    def connectionLost(self, reason):
        self.state = "disconnected"
        self.factory.clientConnectionLost(self, reason)
        if self.state == "disconnected":
            self.factory.doStop()
            self.factoryStarted = 0

    def getDestination(self):
        raise NotImplementedError(reflect.qual(self.__class__) + " did not implement getDestination")

    def __repr__(self):
        return "<%s instance at 0x%x %s %s>" % (
         reflect.qual(self.__class__), id(self), self.state,
         self.getDestination())


class BasePort(abstract.FileDescriptor):
    __doc__ = "Basic implementation of a ListeningPort.\n\n    Note: This does not actually implement IListeningPort.\n    "
    addressFamily = None
    socketType = None

    def createInternetSocket(self):
        s = socket.socket(self.addressFamily, self.socketType)
        s.setblocking(0)
        fdesc._setCloseOnExec(s.fileno())
        return s

    def doWrite(self):
        """Raises a RuntimeError"""
        raise RuntimeError("doWrite called on a %s" % reflect.qual(self.__class__))


class _SignalReactorMixin(object):
    __doc__ = "\n    Private mixin to manage signals: it installs signal handlers at start time,\n    and define run method.\n\n    It can only be used mixed in with L{ReactorBase}, and has to be defined\n    first in the inheritance (so that method resolution order finds\n    startRunning first).\n\n    @type _installSignalHandlers: C{bool}\n    @ivar _installSignalHandlers: A flag which indicates whether any signal\n        handlers will be installed during startup.  This includes handlers for\n        SIGCHLD to monitor child processes, and SIGINT, SIGTERM, and SIGBREAK\n        to stop the reactor.\n    "
    _installSignalHandlers = False

    def _handleSignals(self):
        """
        Install the signal handlers for the Twisted event loop.
        """
        try:
            import signal
        except ImportError:
            log.msg("Warning: signal module unavailable -- not installing signal handlers.")
            return
        else:
            if signal.getsignal(signal.SIGINT) == signal.default_int_handler:
                signal.signal(signal.SIGINT, self.sigInt)
            signal.signal(signal.SIGTERM, self.sigTerm)
            if hasattr(signal, "SIGBREAK"):
                signal.signal(signal.SIGBREAK, self.sigBreak)

    def startRunning(self, installSignalHandlers=True):
        """
        Extend the base implementation in order to remember whether signal
        handlers should be installed later.

        @type installSignalHandlers: C{bool}
        @param installSignalHandlers: A flag which, if set, indicates that
            handlers for a number of (implementation-defined) signals should be
            installed during startup.
        """
        self._installSignalHandlers = installSignalHandlers
        ReactorBase.startRunning(self)

    def _reallyStartRunning(self):
        """
        Extend the base implementation by also installing signal handlers, if
        C{self._installSignalHandlers} is true.
        """
        ReactorBase._reallyStartRunning(self)
        if self._installSignalHandlers:
            self._handleSignals()

    def run(self, installSignalHandlers=True):
        self.startRunning(installSignalHandlers=installSignalHandlers)
        self.mainLoop()

    def mainLoop(self):
        while self._started:
            try:
                while self._started:
                    self.runUntilCurrent()
                    t2 = self.timeout()
                    t = self.running and t2
                    self.doIteration(t)

            except:
                log.msg("Unexpected error in main loop.")
                log.err()
            else:
                log.msg("Main loop terminated.")


__all__ = []
