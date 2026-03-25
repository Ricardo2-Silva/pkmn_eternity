# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\libs\egl\eglext.py
from ctypes import *
from pyglet.libs.egl import egl
from pyglet.libs.egl.lib import link_EGL as _link_function
EGL_PLATFORM_DEVICE_EXT = 12607
EGLDeviceEXT = POINTER(None)
eglGetPlatformDisplayEXT = _link_function("eglGetPlatformDisplayEXT", egl.EGLDisplay, [egl.EGLenum, POINTER(None), POINTER(egl.EGLint)], None)
eglQueryDevicesEXT = _link_function("eglQueryDevicesEXT", egl.EGLBoolean, [egl.EGLint, POINTER(EGLDeviceEXT), POINTER(egl.EGLint)], None)
__all__ = [
 "EGL_PLATFORM_DEVICE_EXT", "EGLDeviceEXT", "eglGetPlatformDisplayEXT", "eglQueryDevicesEXT"]
