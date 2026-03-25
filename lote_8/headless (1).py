# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\gl\headless.py
import warnings
from ctypes import *
from .base import Config, CanvasConfig, Context
from pyglet.canvas.headless import HeadlessCanvas
from pyglet.libs.egl import egl
from pyglet.libs.egl.egl import *
from pyglet import gl
_fake_gl_attributes = {
 'double_buffer': 0, 
 'stereo': 0, 
 'aux_buffers': 0, 
 'accum_red_size': 0, 
 'accum_green_size': 0, 
 'accum_blue_size': 0, 
 'accum_alpha_size': 0}

class HeadlessConfig(Config):

    def match(self, canvas):
        if not isinstance(canvas, HeadlessCanvas):
            raise RuntimeError("Canvas must be an instance of HeadlessCanvas")
        display_connection = canvas.display._display_connection
        attrs = []
        for name, value in self.get_gl_attributes():
            if name == "double_buffer":
                pass
            else:
                attr = HeadlessCanvasConfig.attribute_ids.get(name, None)
                if attr and value is not None:
                    attrs.extend([attr, int(value)])

        attrs.extend([EGL_SURFACE_TYPE, EGL_PBUFFER_BIT])
        attrs.extend([EGL_RENDERABLE_TYPE, EGL_OPENGL_BIT])
        attrs.extend([EGL_NONE])
        attrs_list = (egl.EGLint * len(attrs))(*attrs)
        num_config = egl.EGLint()
        egl.eglChooseConfig(display_connection, attrs_list, None, 0, byref(num_config))
        configs = egl.EGLConfig * num_config.value()
        egl.eglChooseConfig(display_connection, attrs_list, configs, num_config.value, byref(num_config))
        result = [HeadlessCanvasConfig(canvas, c, self) for c in configs]
        return result


class HeadlessCanvasConfig(CanvasConfig):
    attribute_ids = {'buffer_size':egl.EGL_BUFFER_SIZE, 
     'level':egl.EGL_LEVEL, 
     'red_size':egl.EGL_RED_SIZE, 
     'green_size':egl.EGL_GREEN_SIZE, 
     'blue_size':egl.EGL_BLUE_SIZE, 
     'alpha_size':egl.EGL_ALPHA_SIZE, 
     'depth_size':egl.EGL_DEPTH_SIZE, 
     'stencil_size':egl.EGL_STENCIL_SIZE, 
     'sample_buffers':egl.EGL_SAMPLE_BUFFERS, 
     'samples':egl.EGL_SAMPLES}

    def __init__(self, canvas, egl_config, config):
        super(HeadlessCanvasConfig, self).__init__(canvas, config)
        self._egl_config = egl_config
        context_attribs = (EGL_CONTEXT_MAJOR_VERSION, config.major_version or 2,
         EGL_CONTEXT_MINOR_VERSION, config.minor_version or 0,
         EGL_CONTEXT_OPENGL_FORWARD_COMPATIBLE, config.forward_compatible or 0,
         EGL_CONTEXT_OPENGL_DEBUG, config.debug or 0,
         EGL_NONE)
        self._context_attrib_array = (egl.EGLint * len(context_attribs))(*context_attribs)
        for name, attr in self.attribute_ids.items():
            value = egl.EGLint()
            egl.eglGetConfigAttrib(canvas.display._display_connection, egl_config, attr, byref(value))
            setattr(self, name, value.value)

        for name, value in _fake_gl_attributes.items():
            setattr(self, name, value)

    def compatible(self, canvas):
        return isinstance(canvas, HeadlessCanvas)

    def create_context(self, share):
        return HeadlessContext(self, share)


class HeadlessContext(Context):

    def __init__(self, config, share):
        super(HeadlessContext, self).__init__(config, share)
        self.display_connection = config.canvas.display._display_connection
        self.egl_context = self._create_egl_context(share)
        if not self.egl_context:
            raise gl.ContextException("Could not create GL context")

    def _create_egl_context(self, share):
        if share:
            share_context = share.egl_context
        else:
            share_context = None
        egl.eglBindAPI(egl.EGL_OPENGL_API)
        return egl.eglCreateContext(self.config.canvas.display._display_connection, self.config._egl_config, share_context, self.config._context_attrib_array)

    def attach(self, canvas):
        if canvas is self.canvas:
            return
        super(HeadlessContext, self).attach(canvas)
        self.egl_surface = canvas.egl_surface
        self.set_current()

    def set_current(self):
        egl.eglMakeCurrent(self.display_connection, self.egl_surface, self.egl_surface, self.egl_context)
        super(HeadlessContext, self).set_current()

    def detach(self):
        if not self.canvas:
            return
        self.set_current()
        gl.glFlush()
        super(HeadlessContext, self).detach()
        egl.eglMakeCurrent(self.display_connection, 0, 0, None)
        self.egl_surface = None

    def destroy(self):
        super(HeadlessContext, self).destroy()
        if self.egl_context:
            egl.eglDestroyContext(self.display_connection, self.egl_context)
            self.egl_context = None

    def flip(self):
        if not self.egl_surface:
            return
        egl.eglSwapBuffers(self.display_connection, self.egl_surface)
