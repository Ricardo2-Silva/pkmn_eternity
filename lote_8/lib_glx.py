# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\gl\lib_glx.py
from ctypes import *
import pyglet.lib
from pyglet.gl.lib import missing_function, decorate_function
from pyglet.util import asbytes
__all__ = [
 "link_GL", "link_GLU", "link_GLX"]
gl_lib = pyglet.lib.load_library("GL")
glu_lib = pyglet.lib.load_library("GLU")
try:
    glXGetProcAddressARB = getattr(gl_lib, "glXGetProcAddressARB")
    glXGetProcAddressARB.restype = POINTER(CFUNCTYPE(None))
    glXGetProcAddressARB.argtypes = [POINTER(c_ubyte)]
    _have_getprocaddress = True
except AttributeError:
    _have_getprocaddress = False

def link_GL(name, restype, argtypes, requires=None, suggestions=None):
    try:
        func = getattr(gl_lib, name)
        func.restype = restype
        func.argtypes = argtypes
        decorate_function(func, name)
        return func
    except AttributeError:
        if _have_getprocaddress:
            bname = cast(pointer(create_string_buffer(asbytes(name))), POINTER(c_ubyte))
            addr = glXGetProcAddressARB(bname)
            if addr:
                ftype = CFUNCTYPE(*(restype,) + tuple(argtypes))
                func = cast(addr, ftype)
                decorate_function(func, name)
                return func

    return missing_function(name, requires, suggestions)


link_GLX = link_GL

def link_GLU(name, restype, argtypes, requires=None, suggestions=None):
    try:
        func = getattr(glu_lib, name)
        func.restype = restype
        func.argtypes = argtypes
        decorate_function(func, name)
        return func
    except AttributeError:
        return missing_function(name, requires, suggestions)
