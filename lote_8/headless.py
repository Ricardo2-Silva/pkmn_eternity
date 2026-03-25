# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\canvas\headless.py
import pyglet, warnings
from .base import Display, Screen, ScreenMode, Canvas
from ctypes import *
from pyglet.libs.egl import egl
from pyglet.libs.egl import eglext

class HeadlessDisplay(Display):

    def __init__(self):
        super().__init__()
        self._screens = [
         HeadlessScreen(self, 0, 0, 1920, 1080)]
        num_devices = egl.EGLint()
        eglext.eglQueryDevicesEXT(0, None, byref(num_devices))
        if num_devices.value > 0:
            headless_device = pyglet.options["headless_device"]
            if headless_device < 0 or headless_device >= num_devices.value:
                raise ValueError("Invalid EGL devide id: %d" % headless_device)
            devices = eglext.EGLDeviceEXT * num_devices.value()
            eglext.eglQueryDevicesEXT(num_devices.value, devices, byref(num_devices))
            self._display_connection = eglext.eglGetPlatformDisplayEXT(eglext.EGL_PLATFORM_DEVICE_EXT, devices[headless_device], None)
        else:
            warnings.warn("No device available for EGL device platform. Using native display type.")
            display = egl.EGLNativeDisplayType()
            self._display_connection = egl.eglGetDisplay(display)
        egl.eglInitialize(self._display_connection, None, None)

    def get_screens(self):
        return self._screens

    def __del__(self):
        egl.eglTerminate(self._display_connection)


class HeadlessCanvas(Canvas):

    def __init__(self, display, egl_surface):
        super().__init__(display)
        self.egl_surface = egl_surface


class HeadlessScreen(Screen):

    def __init__(self, display, x, y, width, height):
        super().__init__(display, x, y, width, height)

    def get_matching_configs(self, template):
        canvas = HeadlessCanvas(self.display, None)
        configs = template.match(canvas)
        for config in configs:
            config.screen = self

        return configs

    def get_modes(self):
        return

    def get_mode(self):
        return

    def set_mode(self, mode):
        return

    def restore_mode(self):
        return
