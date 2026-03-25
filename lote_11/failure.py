# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\python\failure.py
"""
Asynchronous-friendly error mechanism.

See L{Failure}.
"""
from __future__ import division, absolute_import, print_function
import copy, sys, linecache, inspect, opcode
from inspect import getmro
from twisted.python import reflect
from twisted.python.compat import _PY3, NativeStringIO as StringIO
count = 0
traceupLength = 4

class DefaultException(Exception):
    return


def format_frames(frames, write, detail='default'):
    """
    Format and write frames.

    @param frames: is a list of frames as used by Failure.frames, with
        each frame being a list of
        (funcName, fileName, lineNumber, locals.items(), globals.items())
    @type frames: list
    @param write: this will be called with formatted strings.
    @type write: callable
    @param detail: Four detail levels are available:
        default, brief, verbose, and verbose-vars-not-captured.
        C{Failure.printDetailedTraceback} uses the latter when the caller asks
        for verbose, but no vars were captured, so that an explicit warning
        about the missing data is shown.
    @type detail: string
    """
    if detail not in ('default', 'brief', 'verbose', 'verbose-vars-not-captured'):
        raise ValueError("Detail must be default, brief, verbose, or verbose-vars-not-captured. (not %r)" % (
         detail,))
    w = write
    if detail == "brief":
        for method, filename, lineno, localVars, globalVars in frames:
            w("%s:%s:%s\n" % (filename, lineno, method))

    elif detail == "default":
        for method, filename, lineno, localVars, globalVars in frames:
            w('  File "%s", line %s, in %s\n' % (filename, lineno, method))
            w("    %s\n" % linecache.getline(filename, lineno).strip())

    elif detail == "verbose-vars-not-captured":
        for method, filename, lineno, localVars, globalVars in frames:
            w("%s:%d: %s(...)\n" % (filename, lineno, method))

        w(" [Capture of Locals and Globals disabled (use captureVars=True)]\n")
    elif detail == "verbose":
        for method, filename, lineno, localVars, globalVars in frames:
            w("%s:%d: %s(...)\n" % (filename, lineno, method))
            w(" [ Locals ]\n")
            for name, val in localVars:
                w("  %s : %s\n" % (name, repr(val)))

            w(" ( Globals )\n")
            for name, val in globalVars:
                w("  %s : %s\n" % (name, repr(val)))


EXCEPTION_CAUGHT_HERE = "--- <exception caught here> ---"

class NoCurrentExceptionError(Exception):
    __doc__ = "\n    Raised when trying to create a Failure from the current interpreter\n    exception state and there is no current exception state.\n    "


def _Traceback(stackFrames, tbFrames):
    """
    Construct a fake traceback object using a list of frames. Note that
    although frames generally include locals and globals, this information
    is not kept by this method, since locals and globals are not used in
    standard tracebacks.

    @param stackFrames: [(methodname, filename, lineno, locals, globals), ...]
    @param tbFrames: [(methodname, filename, lineno, locals, globals), ...]
    """
    assert len(tbFrames) > 0, "Must pass some frames"
    stack = None
    for sf in stackFrames:
        stack = _Frame(sf, stack)

    stack = _Frame(tbFrames[0], stack)
    firstTb = tb = _TracebackFrame(stack)
    for sf in tbFrames[1:]:
        stack = _Frame(sf, stack)
        tb.tb_next = _TracebackFrame(stack)
        tb = tb.tb_next

    return firstTb


class _TracebackFrame(object):
    __doc__ = "\n    Fake traceback object which can be passed to functions in the standard\n    library L{traceback} module.\n    "

    def __init__(self, frame):
        """
        @param frame: _Frame object
        """
        self.tb_frame = frame
        self.tb_lineno = frame.f_lineno
        self.tb_next = None


class _Frame(object):
    __doc__ = "\n    A fake frame object, used by L{_Traceback}.\n\n    @ivar f_code: fake L{code<types.CodeType>} object\n    @ivar f_lineno: line number\n    @ivar f_globals: fake f_globals dictionary (usually empty)\n    @ivar f_locals: fake f_locals dictionary (usually empty)\n    @ivar f_back: previous stack frame (towards the caller)\n    "

    def __init__(self, frameinfo, back):
        """
        @param frameinfo: (methodname, filename, lineno, locals, globals)
        @param back: previous (older) stack frame
        @type back: C{frame}
        """
        name, filename, lineno, localz, globalz = frameinfo
        self.f_code = _Code(name, filename)
        self.f_lineno = lineno
        self.f_globals = {}
        self.f_locals = {}
        self.f_back = back


class _Code(object):
    __doc__ = "\n    A fake code object, used by L{_Traceback} via L{_Frame}.\n    "

    def __init__(self, name, filename):
        self.co_name = name
        self.co_filename = filename


_inlineCallbacksExtraneous = []

def _extraneous(f):
    """
    Mark the given callable as extraneous to inlineCallbacks exception
    reporting; don't show these functions.

    @param f: a function that you NEVER WANT TO SEE AGAIN in ANY TRACEBACK
        reported by Failure.

    @type f: function

    @return: f
    """
    _inlineCallbacksExtraneous.append(f.__code__)
    return f


class Failure(BaseException):
    __doc__ = "\n    A basic abstraction for an error that has occurred.\n\n    This is necessary because Python's built-in error mechanisms are\n    inconvenient for asynchronous communication.\n\n    The C{stack} and C{frame} attributes contain frames.  Each frame is a tuple\n    of (funcName, fileName, lineNumber, localsItems, globalsItems), where\n    localsItems and globalsItems are the contents of\n    C{locals().items()}/C{globals().items()} for that frame, or an empty tuple\n    if those details were not captured.\n\n    @ivar value: The exception instance responsible for this failure.\n    @ivar type: The exception's class.\n    @ivar stack: list of frames, innermost last, excluding C{Failure.__init__}.\n    @ivar frames: list of frames, innermost first.\n    "
    pickled = 0
    stack = None
    if _PY3:
        _yieldOpcode = opcode.opmap["YIELD_VALUE"]
    else:
        _yieldOpcode = chr(opcode.opmap["YIELD_VALUE"])

    def __init__(self, exc_value=None, exc_type=None, exc_tb=None, captureVars=False):
        """
        Initialize me with an explanation of the error.

        By default, this will use the current C{exception}
        (L{sys.exc_info}()).  However, if you want to specify a
        particular kind of failure, you can pass an exception as an
        argument.

        If no C{exc_value} is passed, then an "original" C{Failure} will
        be searched for. If the current exception handler that this
        C{Failure} is being constructed in is handling an exception
        raised by L{raiseException}, then this C{Failure} will act like
        the original C{Failure}.

        For C{exc_tb} only L{traceback} instances or L{None} are allowed.
        If L{None} is supplied for C{exc_value}, the value of C{exc_tb} is
        ignored, otherwise if C{exc_tb} is L{None}, it will be found from
        execution context (ie, L{sys.exc_info}).

        @param captureVars: if set, capture locals and globals of stack
            frames.  This is pretty slow, and makes no difference unless you
            are going to use L{printDetailedTraceback}.
        """
        global count
        count = count + 1
        self.count = count
        self.type = self.value = tb = None
        self.captureVars = captureVars
        if isinstance(exc_value, str):
            if exc_type is None:
                raise TypeError("Strings are not supported by Failure")
        stackOffset = 0
        if exc_value is None:
            exc_value = self._findFailure()
        elif exc_value is None:
            self.type, self.value, tb = sys.exc_info()
            if self.type is None:
                raise NoCurrentExceptionError()
            stackOffset = 1
        elif exc_type is None:
            if isinstance(exc_value, Exception):
                self.type = exc_value.__class__
            else:
                self.type = type(exc_value)
            self.value = exc_value
        else:
            self.type = exc_type
            self.value = exc_value
        if isinstance(self.value, Failure):
            self._extrapolate(self.value)
            return
        else:
            if hasattr(self.value, "__failure__"):
                self._extrapolate(self.value.__failure__)
                del self.value.__failure__
                return
            else:
                if tb is None:
                    if exc_tb:
                        tb = exc_tb
                    elif getattr(self.value, "__traceback__", None):
                        tb = self.value.__traceback__
                frames = self.frames = []
                stack = self.stack = []
                self.tb = tb
                if tb:
                    f = tb.tb_frame
                else:
                    if not isinstance(self.value, Failure):
                        f = stackOffset = None
                while stackOffset and f:
                    f = f.f_back
                    stackOffset -= 1

                while f:
                    if captureVars:
                        localz = f.f_locals.copy()
                        if f.f_locals is f.f_globals:
                            globalz = {}
                        else:
                            globalz = f.f_globals.copy()
                        for d in (globalz, localz):
                            if "__builtins__" in d:
                                del d["__builtins__"]

                        localz = localz.items()
                        globalz = globalz.items()
                    else:
                        localz = globalz = ()
                    stack.insert(0, (
                     f.f_code.co_name,
                     f.f_code.co_filename,
                     f.f_lineno,
                     localz,
                     globalz))
                    f = f.f_back

                while tb is not None:
                    f = tb.tb_frame
                    if captureVars:
                        localz = f.f_locals.copy()
                        if f.f_locals is f.f_globals:
                            globalz = {}
                        else:
                            globalz = f.f_globals.copy()
                        for d in (globalz, localz):
                            if "__builtins__" in d:
                                del d["__builtins__"]

                        localz = list(localz.items())
                        globalz = list(globalz.items())
                    else:
                        localz = globalz = ()
                    frames.append((
                     f.f_code.co_name,
                     f.f_code.co_filename,
                     tb.tb_lineno,
                     localz,
                     globalz))
                    tb = tb.tb_next

                if inspect.isclass(self.type) and issubclass(self.type, Exception):
                    parentCs = getmro(self.type)
                    self.parents = list(map(reflect.qual, parentCs))
            self.parents = [
             self.type]

    def _extrapolate(self, otherFailure):
        """
        Extrapolate from one failure into another, copying its stack frames.

        @param otherFailure: Another L{Failure}, whose traceback information,
            if any, should be preserved as part of the stack presented by this
            one.
        @type otherFailure: L{Failure}
        """
        self.__dict__ = copy.copy(otherFailure.__dict__)
        _, _, tb = sys.exc_info()
        frames = []
        while tb is not None:
            f = tb.tb_frame
            if f.f_code not in _inlineCallbacksExtraneous:
                frames.append((
                 f.f_code.co_name,
                 f.f_code.co_filename,
                 tb.tb_lineno, (), ()))
            tb = tb.tb_next

        frames.extend(self.frames)
        self.frames = frames

    def trap(self, *errorTypes):
        """
        Trap this failure if its type is in a predetermined list.

        This allows you to trap a Failure in an error callback.  It will be
        automatically re-raised if it is not a type that you expect.

        The reason for having this particular API is because it's very useful
        in Deferred errback chains::

            def _ebFoo(self, failure):
                r = failure.trap(Spam, Eggs)
                print('The Failure is due to either Spam or Eggs!')
                if r == Spam:
                    print('Spam did it!')
                elif r == Eggs:
                    print('Eggs did it!')

        If the failure is not a Spam or an Eggs, then the Failure will be
        'passed on' to the next errback. In Python 2 the Failure will be
        raised; in Python 3 the underlying exception will be re-raised.

        @type errorTypes: L{Exception}
        """
        error = (self.check)(*errorTypes)
        if not error:
            if _PY3:
                self.raiseException()
            else:
                raise self
        return error

    def check(self, *errorTypes):
        """
        Check if this failure's type is in a predetermined list.

        @type errorTypes: list of L{Exception} classes or
                          fully-qualified class names.
        @returns: the matching L{Exception} type, or None if no match.
        """
        for error in errorTypes:
            err = error
            if inspect.isclass(error):
                if issubclass(error, Exception):
                    err = reflect.qual(error)
                elif err in self.parents:
                    return error

        return

    if getattr(BaseException, "with_traceback", None):

        def raiseException(self):
            raise self.value.with_traceback(self.tb)

    else:
        exec("def raiseException(self):\n    raise self.type, self.value, self.tb")
    raiseException.__doc__ = "\n        raise the original exception, preserving traceback\n        information if available.\n        "

    @_extraneous
    def throwExceptionIntoGenerator(self, g):
        """
        Throw the original exception into the given generator,
        preserving traceback information if available.

        @return: The next value yielded from the generator.
        @raise StopIteration: If there are no more values in the generator.
        @raise anything else: Anything that the generator raises.
        """
        return g.throw(self.type, self.value, self.tb)

    def _findFailure(cls):
        """
        Find the failure that represents the exception currently in context.
        """
        tb = sys.exc_info()[-1]
        if not tb:
            return
        secondLastTb = None
        lastTb = tb
        while lastTb.tb_next:
            secondLastTb = lastTb
            lastTb = lastTb.tb_next

        lastFrame = lastTb.tb_frame
        if lastFrame.f_code is cls.raiseException.__code__:
            return lastFrame.f_locals.get("self")
        if not lastFrame.f_code.co_code or lastFrame.f_code.co_code[lastTb.tb_lasti] != cls._yieldOpcode:
            return
        if secondLastTb:
            frame = secondLastTb.tb_frame
            if frame.f_code is cls.throwExceptionIntoGenerator.__code__:
                return frame.f_locals.get("self")
        frame = tb.tb_frame.f_back
        if frame:
            if frame.f_code is cls.throwExceptionIntoGenerator.__code__:
                return frame.f_locals.get("self")

    _findFailure = classmethod(_findFailure)

    def __repr__(self):
        return "<%s %s: %s>" % (reflect.qual(self.__class__),
         reflect.qual(self.type),
         self.getErrorMessage())

    def __str__(self):
        return "[Failure instance: %s]" % self.getBriefTraceback()

    def __getstate__(self):
        """Avoid pickling objects in the traceback.
        """
        if self.pickled:
            return self.__dict__
        else:
            c = self.__dict__.copy()
            c["frames"] = [[v[0], v[1], v[2], _safeReprVars(v[3]), _safeReprVars(v[4])] for v in self.frames]
            c["tb"] = None
            if self.stack is not None:
                c["stack"] = [[v[0], v[1], v[2], _safeReprVars(v[3]), _safeReprVars(v[4])] for v in self.stack]
            c["pickled"] = 1
            return c

    def cleanFailure(self):
        """
        Remove references to other objects, replacing them with strings.

        On Python 3, this will also set the C{__traceback__} attribute of the
        exception instance to L{None}.
        """
        self.__dict__ = self.__getstate__()
        if getattr(self.value, "__traceback__", None):
            self.value.__traceback__ = None

    def getTracebackObject(self):
        """
        Get an object that represents this Failure's stack that can be passed
        to traceback.extract_tb.

        If the original traceback object is still present, return that. If this
        traceback object has been lost but we still have the information,
        return a fake traceback object (see L{_Traceback}). If there is no
        traceback information at all, return None.
        """
        if self.tb is not None:
            return self.tb
        else:
            if len(self.frames) > 0:
                return _Traceback(self.stack, self.frames)
            return

    def getErrorMessage(self):
        """
        Get a string of the exception which caused this Failure.
        """
        if isinstance(self.value, Failure):
            return self.value.getErrorMessage()
        else:
            return reflect.safe_str(self.value)

    def getBriefTraceback(self):
        io = StringIO()
        self.printBriefTraceback(file=io)
        return io.getvalue()

    def getTraceback(self, elideFrameworkCode=0, detail='default'):
        io = StringIO()
        self.printTraceback(file=io, elideFrameworkCode=elideFrameworkCode, detail=detail)
        return io.getvalue()

    def printTraceback(self, file=None, elideFrameworkCode=False, detail='default'):
        """
        Emulate Python's standard error reporting mechanism.

        @param file: If specified, a file-like object to which to write the
            traceback.

        @param elideFrameworkCode: A flag indicating whether to attempt to
            remove uninteresting frames from within Twisted itself from the
            output.

        @param detail: A string indicating how much information to include
            in the traceback.  Must be one of C{'brief'}, C{'default'}, or
            C{'verbose'}.
        """
        if file is None:
            from twisted.python import log
            file = log.logerr
        else:
            w = file.write
            if detail == "verbose" and not self.captureVars:
                formatDetail = "verbose-vars-not-captured"
            else:
                formatDetail = detail
            if detail == "verbose":
                w("*--- Failure #%d%s---\n" % (
                 self.count,
                 self.pickled and " (pickled) " or " "))
            elif detail == "brief":
                if self.frames:
                    hasFrames = "Traceback"
                else:
                    hasFrames = "Traceback (failure with no frames)"
                w("%s: %s: %s\n" % (
                 hasFrames,
                 reflect.safe_str(self.type),
                 reflect.safe_str(self.value)))
            else:
                w("Traceback (most recent call last):\n")
            if self.frames:
                if not elideFrameworkCode:
                    format_frames(self.stack[-traceupLength:], w, formatDetail)
                    w("%s\n" % (EXCEPTION_CAUGHT_HERE,))
                format_frames(self.frames, w, formatDetail)
            else:
                if not detail == "brief":
                    w("Failure: ")
            if not detail == "brief":
                w("%s: %s\n" % (reflect.qual(self.type),
                 reflect.safe_str(self.value)))
            if isinstance(self.value, Failure):
                file.write(" (chained Failure)\n")
                self.value.printTraceback(file, elideFrameworkCode, detail)
            if detail == "verbose":
                w("*--- End of Failure #%d ---\n" % self.count)

    def printBriefTraceback(self, file=None, elideFrameworkCode=0):
        """
        Print a traceback as densely as possible.
        """
        self.printTraceback(file, elideFrameworkCode, detail="brief")

    def printDetailedTraceback(self, file=None, elideFrameworkCode=0):
        """
        Print a traceback with detailed locals and globals information.
        """
        self.printTraceback(file, elideFrameworkCode, detail="verbose")


def _safeReprVars(varsDictItems):
    """
    Convert a list of (name, object) pairs into (name, repr) pairs.

    L{twisted.python.reflect.safe_repr} is used to generate the repr, so no
    exceptions will be raised by faulty C{__repr__} methods.

    @param varsDictItems: a sequence of (name, value) pairs as returned by e.g.
        C{locals().items()}.
    @returns: a sequence of (name, repr) pairs.
    """
    return [(name, reflect.safe_repr(obj)) for name, obj in varsDictItems]


DO_POST_MORTEM = True

def _debuginit(self, exc_value=None, exc_type=None, exc_tb=None, captureVars=False, Failure__init__=Failure.__init__):
    """
    Initialize failure object, possibly spawning pdb.
    """
    if (
     exc_value, exc_type, exc_tb) == (None, None, None):
        exc = sys.exc_info()
        if not exc[0] == self.__class__:
            if DO_POST_MORTEM:
                try:
                    strrepr = str(exc[1])
                except:
                    strrepr = "broken str"

                print("Jumping into debugger for post-mortem of exception '%s':" % (
                 strrepr,))
                import pdb
                pdb.post_mortem(exc[2])
    Failure__init__(self, exc_value, exc_type, exc_tb, captureVars)


def startDebugMode():
    """
    Enable debug hooks for Failures.
    """
    Failure.__init__ = _debuginit
