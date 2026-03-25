# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\gl\lib_agl.py
from ctypes import *
import pyglet.lib
from pyglet.gl.lib import missing_function, decorate_function
__all__ = [
 "link_GL", "link_GLU", "link_AGL"]
gl_lib = pyglet.lib.load_library(framework="OpenGL")
agl_lib = pyglet.lib.load_library(framework="AGL")

def link_GL(name, restype, argtypes, requires=None, suggestions=None):
    try:
        func = getattr(gl_lib, name)
        func.restype = restype
        func.argtypes = argtypes
        decorate_function(func, name)
        return func
    except AttributeError:
        return missing_function(name, requires, suggestions)


link_GLU = link_GL

def link_AGL(name, restype, argtypes, requires=None, suggestions=None):
    try:
        func = getattr(agl_lib, name)
        func.restype = restype
        func.argtypes = argtypes
        decorate_function(func, name)
        return func
    except AttributeError:
        return missing_function(name, requires, suggestions)
