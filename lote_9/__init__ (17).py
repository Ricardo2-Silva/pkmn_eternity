# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\window\headless\__init__.py
from pyglet.window import BaseWindow, _PlatformEventHandler, _ViewEventHandler
from pyglet.window import WindowException, NoSuchDisplayException, MouseCursorException
from pyglet.window import MouseCursor, DefaultMouseCursor, ImageMouseCursor
from pyglet.libs.egl import egl
from pyglet.canvas.headless import HeadlessCanvas
from pyglet.event import EventDispatcher
HeadlessEventHandler = _PlatformEventHandler
ViewEventHandler = _ViewEventHandler

class HeadlessWindow(BaseWindow):
    _egl_display_connection = None
    _egl_surface = None

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)

    def _recreate(self, changes):
        return

    def flip(self):
        if self.context:
            self.context.flip()

    def switch_to(self):
        if self.context:
            self.context.set_current()

    def set_caption(self, caption):
        return

    def set_minimum_size(self, width, height):
        return

    def set_maximum_size(self, width, height):
        return

    def set_size(self, width, height):
        return

    def get_size(self):
        return (
         self._width, self._height)

    def set_location(self, x, y):
        return

    def get_location(self):
        return

    def activate(self):
        return

    def set_visible(self, visible=True):
        return

    def minimize(self):
        return

    def maximize(self):
        return

    def set_vsync(self, vsync):
        return

    def set_mouse_platform_visible(self, platform_visible=None):
        return

    def set_exclusive_mouse(self, exclusive=True):
        return

    def set_exclusive_keyboard(self, exclusive=True):
        return

    def get_system_mouse_cursor(self, name):
        return

    def dispatch_events(self):
        while self._event_queue:
            (EventDispatcher.dispatch_event)(self, *self._event_queue.pop(0))

    def dispatch_pending_events(self):
        return

    def _create(self):
        self._egl_display_connection = self.display._display_connection
        if not self._egl_surface:
            pbuffer_attribs = (
             egl.EGL_WIDTH, self._width, egl.EGL_HEIGHT, self._height, egl.EGL_NONE)
            pbuffer_attrib_array = (egl.EGLint * len(pbuffer_attribs))(*pbuffer_attribs)
            self._egl_surface = egl.eglCreatePbufferSurface(self._egl_display_connection, self.config._egl_config, pbuffer_attrib_array)
            self.canvas = HeadlessCanvas(self.display, self._egl_surface)
            self.context.attach(self.canvas)
            self.dispatch_event("on_resize", self._width, self._height)
