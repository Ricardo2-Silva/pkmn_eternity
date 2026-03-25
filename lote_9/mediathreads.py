# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\media\mediathreads.py
import time, atexit, threading, pyglet
from pyglet.util import debug_print
_debug = debug_print("debug_media")

class MediaThread:
    __doc__ = "A thread that cleanly exits on interpreter shutdown, and provides\n    a sleep method that can be interrupted and a termination method.\n\n    :Ivariables:\n        `_condition` : threading.Condition\n            Lock _condition on all instance variables.\n        `_stopped` : bool\n            True if `stop` has been called.\n\n    "
    _threads = set()
    _threads_lock = threading.Lock()

    def __init__(self):
        self._thread = threading.Thread(target=(self._thread_run), daemon=True)
        self._condition = threading.Condition()
        self._stopped = False

    def run(self):
        raise NotImplementedError

    def _thread_run(self):
        if pyglet.options["debug_trace"]:
            pyglet._install_trace()
        with self._threads_lock:
            self._threads.add(self)
        self.run()
        with self._threads_lock:
            self._threads.remove(self)

    def start(self):
        self._thread.start()

    def stop(self):
        """Stop the thread and wait for it to terminate.

        The `stop` instance variable is set to ``True`` and the condition is
        notified.  It is the responsibility of the `run` method to check
        the value of `stop` after each sleep or wait and to return if set.
        """
        assert _debug("MediaThread.stop()")
        with self._condition:
            self._stopped = True
            self._condition.notify()
        self._thread.join()

    def sleep(self, timeout):
        """Wait for some amount of time, or until notified.

        :Parameters:
            `timeout` : float
                Time to wait, in seconds.

        """
        assert _debug("MediaThread.sleep(%r)" % timeout)
        with self._condition:
            if not self._stopped:
                self._condition.wait(timeout)

    def notify(self):
        """Interrupt the current sleep operation.

        If the thread is currently sleeping, it will be woken immediately,
        instead of waiting the full duration of the timeout.
        """
        assert _debug("MediaThread.notify()")
        with self._condition:
            self._condition.notify()

    @classmethod
    def atexit(cls):
        with cls._threads_lock:
            threads = list(cls._threads)
        for thread in threads:
            thread.stop()


atexit.register(MediaThread.atexit)

class PlayerWorkerThread(MediaThread):
    __doc__ = "Worker thread for refilling players."
    _nap_time = 0.05

    def __init__(self):
        super().__init__()
        self.players = set()

    def run(self):
        while True:
            with self._condition:
                if not _debug("PlayerWorkerThread: woke up @{}".format(time.time())):
                    raise AssertionError
                elif self._stopped:
                    break
                sleep_time = -1
                if self.players:
                    filled = False
                    for player in list(self.players):
                        write_size = player.get_write_size()
                        if write_size > player.min_buffer_size:
                            player.refill(write_size)
                            filled = True

                    if not filled:
                        sleep_time = self._nap_time
                    else:
                        assert _debug("PlayerWorkerThread: No active players")
                        sleep_time = None
                    if sleep_time != -1:
                        self.sleep(sleep_time)
                else:
                    self.sleep(self._nap_time)

    def add(self, player):
        if not player is not None:
            raise AssertionError
        elif not _debug("PlayerWorkerThread: player added"):
            raise AssertionError
        with self._condition:
            self.players.add(player)
            self._condition.notify()

    def remove(self, player):
        assert _debug("PlayerWorkerThread: player removed")
        with self._condition:
            if player in self.players:
                self.players.remove(player)
            self._condition.notify()
