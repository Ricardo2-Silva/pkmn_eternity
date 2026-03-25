# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\libs\x11\xinerama.py
"""Wrapper for Xinerama

Generated with:
tools/genwrappers.py xinerama

Do not modify this file.
"""
import ctypes
from ctypes import *
import pyglet.lib
_lib = pyglet.lib.load_library("Xinerama")
_int_types = (
 c_int16, c_int32)
if hasattr(ctypes, "c_int64"):
    _int_types += (ctypes.c_int64,)
for t in _int_types:
    if sizeof(t) == sizeof(c_size_t):
        c_ptrdiff_t = t

class c_void(Structure):
    _fields_ = [
     (
      "dummy", c_int)]


import pyglet.libs.x11.xlib

class struct_anon_93(Structure):
    __slots__ = [
     'screen_number', 
     'x_org', 
     'y_org', 
     'width', 
     'height']


struct_anon_93._fields_ = [
 (
  "screen_number", c_int),
 (
  "x_org", c_short),
 (
  "y_org", c_short),
 (
  "width", c_short),
 (
  "height", c_short)]
XineramaScreenInfo = struct_anon_93
Display = pyglet.libs.x11.xlib.Display
XineramaQueryExtension = _lib.XineramaQueryExtension
XineramaQueryExtension.restype = c_int
XineramaQueryExtension.argtypes = [POINTER(Display), POINTER(c_int), POINTER(c_int)]
XineramaQueryVersion = _lib.XineramaQueryVersion
XineramaQueryVersion.restype = c_int
XineramaQueryVersion.argtypes = [POINTER(Display), POINTER(c_int), POINTER(c_int)]
XineramaIsActive = _lib.XineramaIsActive
XineramaIsActive.restype = c_int
XineramaIsActive.argtypes = [POINTER(Display)]
XineramaQueryScreens = _lib.XineramaQueryScreens
XineramaQueryScreens.restype = POINTER(XineramaScreenInfo)
XineramaQueryScreens.argtypes = [POINTER(Display), POINTER(c_int)]
__all__ = [
 'XineramaScreenInfo', 'XineramaQueryExtension', 
 'XineramaQueryVersion', 'XineramaIsActive', 
 'XineramaQueryScreens']
