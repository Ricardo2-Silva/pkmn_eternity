# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\gl\glxext_mesa.py
"""This file is currently hand-coded; I don't have a MESA header file to build
off.
"""
from ctypes import *
from pyglet.gl.lib import link_GLX as _link_function
glXSwapIntervalMESA = _link_function("glXSwapIntervalMESA", c_int, [c_int], "MESA_swap_control")
