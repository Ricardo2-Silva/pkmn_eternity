# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: asyncio\base_futures.py
__all__ = []
import concurrent.futures._base, reprlib
from . import events
Error = concurrent.futures._base.Error
CancelledError = concurrent.futures.CancelledError
TimeoutError = concurrent.futures.TimeoutError

class InvalidStateError(Error):
    __doc__ = "The operation is not allowed in this state."


_PENDING = "PENDING"
_CANCELLED = "CANCELLED"
_FINISHED = "FINISHED"

def isfuture(obj):
    """Check for a Future.

    This returns True when obj is a Future instance or is advertising
    itself as duck-type compatible by setting _asyncio_future_blocking.
    See comment in Future for more details.
    """
    return hasattr(obj.__class__, "_asyncio_future_blocking") and obj._asyncio_future_blocking is not None


def _format_callbacks(cb):
    """helper function for Future.__repr__"""
    size = len(cb)
    if not size:
        cb = ""

    def format_cb(callback):
        return events._format_callback_source(callback, ())

    if size == 1:
        cb = format_cb(cb[0])
    elif size == 2:
        cb = "{}, {}".format(format_cb(cb[0]), format_cb(cb[1]))
    else:
        if size > 2:
            cb = "{}, <{} more>, {}".format(format_cb(cb[0]), size - 2, format_cb(cb[-1]))
    return "cb=[%s]" % cb


def _future_repr_info(future):
    """helper function for Future.__repr__"""
    info = [
     future._state.lower()]
    if future._state == _FINISHED:
        if future._exception is not None:
            info.append("exception={!r}".format(future._exception))
        else:
            result = reprlib.repr(future._result)
            info.append("result={}".format(result))
    if future._callbacks:
        info.append(_format_callbacks(future._callbacks))
    if future._source_traceback:
        frame = future._source_traceback[-1]
        info.append("created at %s:%s" % (frame[0], frame[1]))
    return info
