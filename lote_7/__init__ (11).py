# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pigtwist\__init__.py
"""
This module provides Pyglet/Twisted integration using
the new (Pyglet v1.1) pyglet.app event loop.

See the README for usage information.

Padraig Kitterick <padraigkitterick@gmail.com>
"""
import queue as Queue, pyglet, warnings
from twisted.python import log, runtime
from twisted.internet import _threadedselect
try:
    from pyglet.app.base import EventLoop
    pyglet_event_loop = pyglet.app.base.EventLoop
except ImportError:
    pyglet_event_loop = pyglet.app.EventLoop

class EventLoop(pyglet_event_loop):

    def __init__(self, twisted_queue=None, call_interval=0.1):
        """Set up extra cruft to integrate Twisted calls."""
        pyglet_event_loop.__init__(self)
        if not hasattr(self, "clock"):
            self.clock = pyglet.clock.get_default()
        if twisted_queue is not None:
            self.register_twisted_queue(twisted_queue, call_interval)

    def register_twisted_queue(self, twisted_queue, call_interval):
        self._twisted_call_queue = twisted_queue
        self.clock.schedule_interval_soft(self._make_twisted_calls, call_interval)

    def _make_twisted_calls(self, dt):
        """Check if we need to make function calls for Twisted."""
        try:
            f = self._twisted_call_queue.get(False)
            f()
        except Queue.Empty:
            pass


class PygletReactor(_threadedselect.ThreadedSelectReactor):
    __doc__ = "\n    Pyglet reactor.\n\n    Twisted events are integrated into the Pyglet event loop.\n    "
    _stopping = False

    def registerPygletEventLoop(self, eventloop):
        """Register the pygletreactor.EventLoop instance
        if necessary, i.e. if you need to subclass it.
        """
        self.pygletEventLoop = eventloop

    def stop(self):
        """Stop Twisted."""
        if self._stopping:
            return
        self._stopping = True
        _threadedselect.ThreadedSelectReactor.stop(self)

    def _runInMainThread(self, f):
        """Schedule Twisted calls within the Pyglet event loop."""
        if hasattr(self, "pygletEventLoop"):
            self._twistedQueue.put(f)
        else:
            self._postQueue.put(f)

    def _stopPyglet(self):
        """Stop the pyglet event loop."""
        if hasattr(self, "pygletEventLoop"):
            self.pygletEventLoop.exit()

    def run(self, call_interval=0.1, installSignalHandlers=True):
        """Start the Pyglet event loop and Twisted reactor."""
        if call_interval is 0:
            warnings.warn("CALL INTERVAL SET TO 0. THIS WILL PREVENT WINDOWS FROM CLOSING OR UPDATING")
        else:
            self._postQueue = Queue.Queue()
            self._twistedQueue = Queue.Queue()
            if not hasattr(self, "pygletEventLoop"):
                self.registerPygletEventLoop(EventLoop(self._twistedQueue, call_interval))
            else:
                self.pygletEventLoop.register_twisted_queue(self._twistedQueue, call_interval)
        self.interleave((self._runInMainThread), installSignalHandlers=installSignalHandlers)
        self.addSystemEventTrigger("after", "shutdown", self._stopPyglet)
        self.addSystemEventTrigger("after", "shutdown", (lambda: self._postQueue.put(None)))
        self.pygletEventLoop.run()
        del self.pygletEventLoop
        if not self._stopping:
            self.stop()
            while True:
                try:
                    f = self._postQueue.get(timeout=0.01)
                except Queue.Empty:
                    continue
                else:
                    if f is None:
                        break
                    try:
                        f()
                    except:
                        log.err()


def install():
    """
    Setup Twisted+Pyglet integration based on the Pyglet event loop.
    """
    reactor = PygletReactor()
    from twisted.internet.main import installReactor
    installReactor(reactor)
    return reactor


__all__ = [
 "install"]
