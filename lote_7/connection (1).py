# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: multiprocessing\dummy\connection.py
__all__ = [
 "Client", "Listener", "Pipe"]
from queue import Queue
families = [
 None]

class Listener(object):

    def __init__(self, address=None, family=None, backlog=1):
        self._backlog_queue = Queue(backlog)

    def accept(self):
        return Connection(*self._backlog_queue.get())

    def close(self):
        self._backlog_queue = None

    address = property((lambda self: self._backlog_queue))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()


def Client(address):
    _in, _out = Queue(), Queue()
    address.put((_out, _in))
    return Connection(_in, _out)


def Pipe(duplex=True):
    a, b = Queue(), Queue()
    return (Connection(a, b), Connection(b, a))


class Connection(object):

    def __init__(self, _in, _out):
        self._out = _out
        self._in = _in
        self.send = self.send_bytes = _out.put
        self.recv = self.recv_bytes = _in.get

    def poll(self, timeout=0.0):
        if self._in.qsize() > 0:
            return True
        else:
            if timeout <= 0.0:
                return False
            with self._in.not_empty:
                self._in.not_empty.wait(timeout)
            return self._in.qsize() > 0

    def close(self):
        return

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()
