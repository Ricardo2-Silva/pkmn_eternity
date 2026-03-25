# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: multiprocessing\popen_forkserver.py
import io, os
from .context import reduction, set_spawning_popen
if not reduction.HAVE_SEND_HANDLE:
    raise ImportError("No support for sending fds between processes")
from . import forkserver
from . import popen_fork
from . import spawn
from . import util
__all__ = [
 "Popen"]

class _DupFd(object):

    def __init__(self, ind):
        self.ind = ind

    def detach(self):
        return forkserver.get_inherited_fds()[self.ind]


class Popen(popen_fork.Popen):
    method = "forkserver"
    DupFd = _DupFd

    def __init__(self, process_obj):
        self._fds = []
        super().__init__(process_obj)

    def duplicate_for_child(self, fd):
        self._fds.append(fd)
        return len(self._fds) - 1

    def _launch(self, process_obj):
        prep_data = spawn.get_preparation_data(process_obj._name)
        buf = io.BytesIO()
        set_spawning_popen(self)
        try:
            reduction.dump(prep_data, buf)
            reduction.dump(process_obj, buf)
        finally:
            set_spawning_popen(None)

        self.sentinel, w = forkserver.connect_to_new_process(self._fds)
        util.Finalize(self, os.close, (self.sentinel,))
        with open(w, "wb", closefd=True) as f:
            f.write(buf.getbuffer())
        self.pid = forkserver.read_unsigned(self.sentinel)

    def poll(self, flag=os.WNOHANG):
        if self.returncode is None:
            from multiprocessing.connection import wait
            timeout = 0 if flag == os.WNOHANG else None
            return wait([self.sentinel], timeout) or None
        else:
            try:
                self.returncode = forkserver.read_unsigned(self.sentinel)
            except (OSError, EOFError):
                self.returncode = 255

            return self.returncode
