# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\media\codecs\ffmpeg_lib\libswscale.py
"""Wrapper for include/libswscale/swscale.h
"""
from ctypes import c_int, c_uint16, c_int32, c_int64, c_uint32, c_uint64
from ctypes import c_uint8, c_uint, c_double, c_float, c_ubyte, c_size_t, c_char, c_char_p
from ctypes import c_void_p, addressof, byref, cast, POINTER, CFUNCTYPE, Structure, Union
from ctypes import create_string_buffer, memmove
import pyglet, pyglet.lib
swscale = pyglet.lib.load_library("swscale",
  win32="swscale-5",
  darwin="swscale.5")
SWS_FAST_BILINEAR = 1

class SwsContext(Structure):
    return


class SwsFilter(Structure):
    return


swscale.sws_getCachedContext.restype = POINTER(SwsContext)
swscale.sws_getCachedContext.argtypes = [POINTER(SwsContext),
 c_int, c_int, c_int, c_int,
 c_int, c_int, c_int,
 POINTER(SwsFilter), POINTER(SwsFilter),
 POINTER(c_double)]
swscale.sws_freeContext.argtypes = [POINTER(SwsContext)]
swscale.sws_scale.restype = c_int
swscale.sws_scale.argtypes = [POINTER(SwsContext),
 POINTER(POINTER(c_uint8)),
 POINTER(c_int),
 c_int, c_int,
 POINTER(POINTER(c_uint8)),
 POINTER(c_int)]
__all__ = [
 "swscale",
 "SWS_FAST_BILINEAR",
 "SwsContext",
 "SwsFilter"]
