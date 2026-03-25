# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: shared\controller\utils.py
import threading

class Thread(threading.Thread):

    def __init__(self, daemon=True):
        threading.Thread.__init__(self, daemon=daemon)
        self._stop = threading.Event()
        self.keepAlive = False

    def start(self):
        self.keepAlive = True
        threading.Thread.start(self)

    def restart(self):
        """Restart thread if we stop it."""
        self._stop.set()

    def stop(self):
        """ Block thread from continuing. Will only unblock from set()."""
        self._stop.wait()
        self._stop.clear()

    def kill(self):
        """ Have the threads run through one final time before terminating themselves."""
        self.keepAlive = False
        self.restart()
