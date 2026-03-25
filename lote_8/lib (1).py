# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\libs\egl\lib.py
from ctypes import *
import pyglet, pyglet.util
__all__ = [
 "link_EGL"]
egl_lib = pyglet.lib.load_library("EGL")
eglGetProcAddress = getattr(egl_lib, "eglGetProcAddress")
eglGetProcAddress.restype = POINTER(CFUNCTYPE(None))
eglGetProcAddress.argtypes = [POINTER(c_ubyte)]

def link_EGL(name, restype, argtypes, requires=None, suggestions=None):
    try:
        func = getattr(egl_lib, name)
        func.restype = restype
        func.argtypes = argtypes
        return func
    except AttributeError:
        bname = cast(pointer(create_string_buffer(pyglet.util.asbytes(name))), POINTER(c_ubyte))
        addr = eglGetProcAddress(bname)
        if addr:
            ftype = CFUNCTYPE(*(restype,) + tuple(argtypes))
            func = cast(addr, ftype)
            return func

    return pyglet.gl.lib.missing_function(name, requires, suggestions)
