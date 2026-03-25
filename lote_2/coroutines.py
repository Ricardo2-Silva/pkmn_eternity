# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: asyncio\coroutines.py
__all__ = [
 "coroutine",
 "iscoroutinefunction", "iscoroutine"]
import functools, inspect, opcode, os, sys, traceback, types
from . import compat
from . import constants
from . import events
from . import base_futures
from .log import logger
_YIELD_FROM = opcode.opmap["YIELD_FROM"]
_DEBUG = not sys.flags.ignore_environment and bool(os.environ.get("PYTHONASYNCIODEBUG"))
try:
    _types_coroutine = types.coroutine
    _types_CoroutineType = types.CoroutineType
except AttributeError:
    _types_coroutine = None
    _types_CoroutineType = None

try:
    _inspect_iscoroutinefunction = inspect.iscoroutinefunction
except AttributeError:
    _inspect_iscoroutinefunction = lambda func: False

try:
    from collections.abc import Coroutine as _CoroutineABC, Awaitable as _AwaitableABC
except ImportError:
    _CoroutineABC = _AwaitableABC = None

def has_yield_from_bug():

    class MyGen:

        def __init__(self):
            self.send_args = None

        def __iter__(self):
            return self

        def __next__(self):
            return 42

        def send(self, *what):
            self.send_args = what
            return

    def yield_from_gen(gen):
        yield from gen
        if False:
            yield None

    value = (1, 2, 3)
    gen = MyGen()
    coro = yield_from_gen(gen)
    next(coro)
    coro.send(value)
    return gen.send_args != (value,)


_YIELD_FROM_BUG = has_yield_from_bug()
del has_yield_from_bug

def debug_wrapper(gen):
    return CoroWrapper(gen, None)


class CoroWrapper:

    def __init__(self, gen, func=None):
        if not inspect.isgenerator(gen):
            if not inspect.iscoroutine(gen):
                raise AssertionError(gen)
        self.gen = gen
        self.func = func
        self._source_traceback = events.extract_stack(sys._getframe(1))
        self.__name__ = getattr(gen, "__name__", None)
        self.__qualname__ = getattr(gen, "__qualname__", None)

    def __repr__(self):
        coro_repr = _format_coroutine(self)
        if self._source_traceback:
            frame = self._source_traceback[-1]
            coro_repr += ", created at %s:%s" % (frame[0], frame[1])
        return "<%s %s>" % (self.__class__.__name__, coro_repr)

    def __iter__(self):
        return self

    def __next__(self):
        return self.gen.send(None)

    if _YIELD_FROM_BUG:

        def send(self, *value):
            frame = sys._getframe()
            caller = frame.f_back
            assert caller.f_lasti >= 0
            if caller.f_code.co_code[caller.f_lasti] != _YIELD_FROM:
                value = value[0]
            return self.gen.send(value)

    else:

        def send(self, value):
            return self.gen.send(value)

    def throw(self, type, value=None, traceback=None):
        return self.gen.throw(type, value, traceback)

    def close(self):
        return self.gen.close()

    @property
    def gi_frame(self):
        return self.gen.gi_frame

    @property
    def gi_running(self):
        return self.gen.gi_running

    @property
    def gi_code(self):
        return self.gen.gi_code

    if compat.PY35:

        def __await__(self):
            cr_await = getattr(self.gen, "cr_await", None)
            if cr_await is not None:
                raise RuntimeError("Cannot await on coroutine {!r} while it's awaiting for {!r}".format(self.gen, cr_await))
            return self

        @property
        def gi_yieldfrom(self):
            return self.gen.gi_yieldfrom

        @property
        def cr_await(self):
            return self.gen.cr_await

        @property
        def cr_running(self):
            return self.gen.cr_running

        @property
        def cr_code(self):
            return self.gen.cr_code

        @property
        def cr_frame(self):
            return self.gen.cr_frame

    def __del__(self):
        gen = getattr(self, "gen", None)
        frame = getattr(gen, "gi_frame", None)
        if frame is None:
            frame = getattr(gen, "cr_frame", None)
        else:
            if frame is not None:
                if frame.f_lasti == -1:
                    msg = "%r was never yielded from" % self
                    tb = getattr(self, "_source_traceback", ())
                    if tb:
                        tb = "".join(traceback.format_list(tb))
                        msg += f"\nCoroutine object created at (most recent call last, truncated to {constants.DEBUG_STACK_DEPTH} last lines):\n"
                        msg += tb.rstrip()
                    logger.error(msg)


def coroutine(func):
    """Decorator to mark coroutines.

    If the coroutine is not yielded from before it is destroyed,
    an error message is logged.
    """
    if _inspect_iscoroutinefunction(func):
        return func
    else:
        if inspect.isgeneratorfunction(func):
            coro = func
        else:

            @functools.wraps(func)
            def coro(*args, **kw):
                res = func(*args, **kw)
                if base_futures.isfuture(res) or inspect.isgenerator(res) or isinstance(res, CoroWrapper):
                    res = yield from res
                elif _AwaitableABC is not None:
                    pass
                try:
                    await_meth = res.__await__
                except AttributeError:
                    pass
                else:
                    if isinstance(res, _AwaitableABC):
                        res = yield from await_meth()
                    return res
                if False:
                    yield None

        if not _DEBUG:
            if _types_coroutine is None:
                wrapper = coro
            else:
                wrapper = _types_coroutine(coro)
        else:

            @functools.wraps(func)
            def wrapper(*args, **kwds):
                w = CoroWrapper(coro(*args, **kwds), func=func)
                if w._source_traceback:
                    del w._source_traceback[-1]
                w.__name__ = getattr(func, "__name__", None)
                w.__qualname__ = getattr(func, "__qualname__", None)
                return w

        wrapper._is_coroutine = _is_coroutine
        return wrapper


_is_coroutine = object()

def iscoroutinefunction(func):
    """Return True if func is a decorated coroutine function."""
    return getattr(func, "_is_coroutine", None) is _is_coroutine or _inspect_iscoroutinefunction(func)


_COROUTINE_TYPES = (
 types.GeneratorType, CoroWrapper)
if _CoroutineABC is not None:
    _COROUTINE_TYPES += (_CoroutineABC,)
if _types_CoroutineType is not None:
    _COROUTINE_TYPES = (
     _types_CoroutineType,) + _COROUTINE_TYPES

def iscoroutine(obj):
    """Return True if obj is a coroutine object."""
    return isinstance(obj, _COROUTINE_TYPES)


def _format_coroutine(coro):
    assert iscoroutine(coro)
    if not hasattr(coro, "cr_code") and not hasattr(coro, "gi_code"):
        coro_name = getattr(coro, "__qualname__", getattr(coro, "__name__", type(coro).__name__))
        coro_name = "{}()".format(coro_name)
        running = False
        try:
            running = coro.cr_running
        except AttributeError:
            try:
                running = coro.gi_running
            except AttributeError:
                pass

        if running:
            return "{} running".format(coro_name)
        return coro_name
    else:
        coro_name = None
        if isinstance(coro, CoroWrapper):
            func = coro.func
            coro_name = coro.__qualname__
            if coro_name is not None:
                coro_name = "{}()".format(coro_name)
            else:
                func = coro
            if coro_name is None:
                coro_name = events._format_callback(func, (), {})
            coro_code = None
            if hasattr(coro, "cr_code") and coro.cr_code:
                coro_code = coro.cr_code
        elif hasattr(coro, "gi_code"):
            pass
        if coro.gi_code:
            coro_code = coro.gi_code
        coro_frame = None
        if hasattr(coro, "cr_frame"):
            if coro.cr_frame:
                coro_frame = coro.cr_frame
        if hasattr(coro, "gi_frame"):
            if coro.gi_frame:
                coro_frame = coro.gi_frame
        filename = "<empty co_filename>"
        if coro_code:
            if coro_code.co_filename:
                filename = coro_code.co_filename
        lineno = 0
        coro_repr = coro_name
        if isinstance(coro, CoroWrapper) and not inspect.isgeneratorfunction(coro.func):
            if coro.func is not None:
                source = events._get_function_source(coro.func)
                if source is not None:
                    filename, lineno = source
                if coro_frame is None:
                    coro_repr = "%s done, defined at %s:%s" % (
                     coro_name, filename, lineno)
                else:
                    coro_repr = "%s running, defined at %s:%s" % (
                     coro_name, filename, lineno)
            if coro_frame is not None:
                lineno = coro_frame.f_lineno
                coro_repr = "%s running at %s:%s" % (
                 coro_name, filename, lineno)
        else:
            if coro_code:
                lineno = coro_code.co_firstlineno
                coro_repr = "%s done, defined at %s:%s" % (
                 coro_name, filename, lineno)
        return coro_repr
