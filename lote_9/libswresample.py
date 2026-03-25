# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\media\codecs\ffmpeg_lib\libswresample.py
"""Wrapper for include/libswresample/swresample.h
"""
from ctypes import c_int, c_uint16, c_int32, c_int64, c_uint32, c_uint64
from ctypes import c_uint8, c_uint, c_double, c_float, c_ubyte, c_size_t, c_char, c_char_p
from ctypes import c_void_p, addressof, byref, cast, POINTER, CFUNCTYPE, Structure, Union
from ctypes import create_string_buffer, memmove
import pyglet, pyglet.lib
swresample = pyglet.lib.load_library("swresample",
  win32="swresample-3",
  darwin="swresample.3")
SWR_CH_MAX = 32

class SwrContext(Structure):
    return


swresample.swr_alloc_set_opts.restype = POINTER(SwrContext)
swresample.swr_alloc_set_opts.argtypes = [POINTER(SwrContext),
 c_int64, c_int, c_int, c_int64,
 c_int, c_int, c_int, c_void_p]
swresample.swr_init.restype = c_int
swresample.swr_init.argtypes = [POINTER(SwrContext)]
swresample.swr_free.argtypes = [POINTER(POINTER(SwrContext))]
swresample.swr_convert.restype = c_int
swresample.swr_convert.argtypes = [POINTER(SwrContext),
 POINTER(c_uint8) * SWR_CH_MAX,
 c_int,
 POINTER(POINTER(c_uint8)),
 c_int]
swresample.swr_set_compensation.restype = c_int
swresample.swr_set_compensation.argtypes = [POINTER(SwrContext),
 c_int, c_int]
swresample.swr_get_out_samples.restype = c_int
swresample.swr_get_out_samples.argtypes = [POINTER(SwrContext), c_int]
__all__ = [
 "swresample",
 "SWR_CH_MAX",
 "SwrContext"]
