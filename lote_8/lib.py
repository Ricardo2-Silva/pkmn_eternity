# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\gl\lib.py
import ctypes, pyglet
__all__ = [
 'link_GL', 'link_GLU', 'link_AGL', 'link_GLX', 'link_WGL', 
 'GLException', 
 'missing_function', 'decorate_function']
_debug_gl = pyglet.options["debug_gl"]
_debug_gl_trace = pyglet.options["debug_gl_trace"]
_debug_gl_trace_args = pyglet.options["debug_gl_trace_args"]

class MissingFunctionException(Exception):

    def __init__(self, name, requires=None, suggestions=None):
        msg = "%s is not exported by the available OpenGL driver." % name
        if requires:
            msg += "  %s is required for this functionality." % requires
        if suggestions:
            msg += "  Consider alternative(s) %s." % ", ".join(suggestions)
        Exception.__init__(self, msg)


def missing_function(name, requires=None, suggestions=None):

    def MissingFunction(*args, **kwargs):
        raise MissingFunctionException(name, requires, suggestions)

    return MissingFunction


_int_types = (
 ctypes.c_int16, ctypes.c_int32)
if hasattr(ctypes, "c_int64"):
    _int_types += (ctypes.c_int64,)
else:
    for t in _int_types:
        if ctypes.sizeof(t) == ctypes.sizeof(ctypes.c_size_t):
            c_ptrdiff_t = t

    class c_void(ctypes.Structure):
        _fields_ = [
         (
          "dummy", ctypes.c_int)]


    class GLException(Exception):
        return


    def errcheck(result, func, arguments):
        if _debug_gl_trace:
            try:
                name = func.__name__
            except AttributeError:
                name = repr(func)

            if _debug_gl_trace_args:
                trace_args = ", ".join([repr(arg)[:20] for arg in arguments])
                print("%s(%s)" % (name, trace_args))
            else:
                print(name)
        from pyglet import gl
        context = gl.current_context
        if not context:
            raise GLException("No GL context; create a Window first")
        if not context._gl_begin:
            error = gl.glGetError()
            if error:
                msg = ctypes.cast(gl.gluErrorString(error), ctypes.c_char_p).value
                raise GLException(msg)
            return result


    def errcheck_glbegin(result, func, arguments):
        from pyglet import gl
        context = gl.current_context
        if not context:
            raise GLException("No GL context; create a Window first")
        context._gl_begin = True
        return result


    def errcheck_glend(result, func, arguments):
        from pyglet import gl
        context = gl.current_context
        if not context:
            raise GLException("No GL context; create a Window first")
        context._gl_begin = False
        return errcheck(result, func, arguments)


    def decorate_function(func, name):
        if _debug_gl:
            if name == "glBegin":
                func.errcheck = errcheck_glbegin
            elif name == "glEnd":
                func.errcheck = errcheck_glend
            elif name not in ('glGetError', 'gluErrorString'):
                if name[:3] not in ('glX', 'agl', 'wgl'):
                    func.errcheck = errcheck


    link_AGL = None
    link_GLX = None
    link_WGL = None
    if pyglet.compat_platform in ('win32', 'cygwin'):
        from pyglet.gl.lib_wgl import link_GL, link_GLU, link_WGL
    elif pyglet.compat_platform == "darwin":
        from pyglet.gl.lib_agl import link_GL, link_GLU, link_AGL
    else:
        from pyglet.gl.lib_glx import link_GL, link_GLU, link_GLX
