# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\gl\lib_wgl.py
import ctypes
from ctypes import *
import pyglet
from pyglet.gl.lib import missing_function, decorate_function
from pyglet.util import asbytes
__all__ = [
 "link_GL", "link_GLU", "link_WGL"]
_debug_trace = pyglet.options["debug_trace"]
gl_lib = ctypes.windll.opengl32
glu_lib = ctypes.windll.glu32
wgl_lib = gl_lib
if _debug_trace:
    from pyglet.lib import _TraceLibrary
    gl_lib = _TraceLibrary(gl_lib)
    glu_lib = _TraceLibrary(glu_lib)
    wgl_lib = _TraceLibrary(wgl_lib)
try:
    wglGetProcAddress = wgl_lib.wglGetProcAddress
    wglGetProcAddress.restype = CFUNCTYPE(POINTER(c_int))
    wglGetProcAddress.argtypes = [c_char_p]
    _have_get_proc_address = True
except AttributeError:
    _have_get_proc_address = False

class_slots = ['name', 'requires', 'suggestions', 'ftype', 'func']

def makeWGLFunction(func):

    class WGLFunction:
        __slots__ = class_slots
        __call__ = func

    return WGLFunction


class WGLFunctionProxy:
    __slots__ = class_slots

    def __init__(self, name, ftype, requires, suggestions):
        assert _have_get_proc_address
        self.name = name
        self.ftype = ftype
        self.requires = requires
        self.suggestions = suggestions
        self.func = None

    def __call__(self, *args, **kwargs):
        from pyglet.gl import current_context
        if not current_context:
            raise Exception('Call to function "%s" before GL context created' % self.name)
        else:
            address = wglGetProcAddress(asbytes(self.name))
            if cast(address, POINTER(c_int)):
                self.func = cast(address, self.ftype)
                decorate_function(self.func, self.name)
            else:
                self.func = missing_function(self.name, self.requires, self.suggestions)
        self.__class__ = makeWGLFunction(self.func)
        return (self.func)(*args, **kwargs)


def link_GL(name, restype, argtypes, requires=None, suggestions=None):
    try:
        func = getattr(gl_lib, name)
        func.restype = restype
        func.argtypes = argtypes
        decorate_function(func, name)
        return func
    except AttributeError:
        try:
            fargs = (
             restype,) + tuple(argtypes)
            ftype = (ctypes.WINFUNCTYPE)(*fargs)
            if _have_get_proc_address:
                from pyglet.gl import gl_info
                if gl_info.have_context():
                    address = wglGetProcAddress(name)
                    if address:
                        func = cast(address, ftype)
                        decorate_function(func, name)
                        return func
                else:
                    return WGLFunctionProxy(name, ftype, requires, suggestions)
        except:
            pass

        return missing_function(name, requires, suggestions)


def link_GLU(name, restype, argtypes, requires=None, suggestions=None):
    try:
        func = getattr(glu_lib, name)
        func.restype = restype
        func.argtypes = argtypes
        decorate_function(func, name)
        return func
    except AttributeError:
        try:
            fargs = (
             restype,) + tuple(argtypes)
            ftype = (ctypes.WINFUNCTYPE)(*fargs)
            if _have_get_proc_address:
                from pyglet.gl import gl_info
                if gl_info.have_context():
                    address = wglGetProcAddress(name)
                    if address:
                        func = cast(address, ftype)
                        decorate_function(func, name)
                        return func
                else:
                    return WGLFunctionProxy(name, ftype, requires, suggestions)
        except:
            pass

        return missing_function(name, requires, suggestions)


link_WGL = link_GL
