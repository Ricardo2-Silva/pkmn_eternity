# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\gl\cocoa.py
import platform
from ctypes import c_uint32, c_int, byref
from pyglet.gl.base import Config, CanvasConfig, Context
from pyglet.gl import ContextException
from pyglet.gl import gl
from pyglet.gl import agl
from pyglet.canvas.cocoa import CocoaCanvas
from pyglet.libs.darwin import cocoapy, quartz
NSOpenGLPixelFormat = cocoapy.ObjCClass("NSOpenGLPixelFormat")
NSOpenGLContext = cocoapy.ObjCClass("NSOpenGLContext")
os_x_release = {
 'pre-release': (0, 1), 
 'kodiak': (1, 2, 1), 
 'cheetah': (1, 3, 1), 
 'puma': (1, 4.1), 
 'jaguar': (6, 0, 1), 
 'panther': (7,), 
 'tiger': (8,), 
 'leopard': (9,), 
 'snow_leopard': (10,), 
 'lion': (11,), 
 'mountain_lion': (12,), 
 'mavericks': (13,), 
 'yosemite': (14,), 
 'el_capitan': (15,), 
 'sierra': (16,), 
 'high_sierra': (17,), 
 'mojave': (18,), 
 'catalina': (19,), 
 'big_sur': (20,)}

def os_x_version():
    version = tuple([int(v) for v in platform.release().split(".")])
    if len(version) > 0:
        return version
    else:
        return (
         version,)


_os_x_version = os_x_version()
_gl_attributes = {'double_buffer':cocoapy.NSOpenGLPFADoubleBuffer, 
 'stereo':cocoapy.NSOpenGLPFAStereo, 
 'buffer_size':cocoapy.NSOpenGLPFAColorSize, 
 'sample_buffers':cocoapy.NSOpenGLPFASampleBuffers, 
 'samples':cocoapy.NSOpenGLPFASamples, 
 'aux_buffers':cocoapy.NSOpenGLPFAAuxBuffers, 
 'alpha_size':cocoapy.NSOpenGLPFAAlphaSize, 
 'depth_size':cocoapy.NSOpenGLPFADepthSize, 
 'stencil_size':cocoapy.NSOpenGLPFAStencilSize, 
 'all_renderers':cocoapy.NSOpenGLPFAAllRenderers, 
 'fullscreen':cocoapy.NSOpenGLPFAFullScreen, 
 'minimum_policy':cocoapy.NSOpenGLPFAMinimumPolicy, 
 'maximum_policy':cocoapy.NSOpenGLPFAMaximumPolicy, 
 'screen_mask':cocoapy.NSOpenGLPFAScreenMask, 
 'color_float':cocoapy.NSOpenGLPFAColorFloat, 
 'offscreen':cocoapy.NSOpenGLPFAOffScreen, 
 'sample_alpha':cocoapy.NSOpenGLPFASampleAlpha, 
 'multisample':cocoapy.NSOpenGLPFAMultisample, 
 'supersample':cocoapy.NSOpenGLPFASupersample}
_boolean_gl_attributes = frozenset([
 cocoapy.NSOpenGLPFAAllRenderers,
 cocoapy.NSOpenGLPFADoubleBuffer,
 cocoapy.NSOpenGLPFAStereo,
 cocoapy.NSOpenGLPFAMinimumPolicy,
 cocoapy.NSOpenGLPFAMaximumPolicy,
 cocoapy.NSOpenGLPFAOffScreen,
 cocoapy.NSOpenGLPFAFullScreen,
 cocoapy.NSOpenGLPFAColorFloat,
 cocoapy.NSOpenGLPFAMultisample,
 cocoapy.NSOpenGLPFASupersample,
 cocoapy.NSOpenGLPFASampleAlpha])
_fake_gl_attributes = {
 'red_size': 0, 
 'green_size': 0, 
 'blue_size': 0, 
 'accum_red_size': 0, 
 'accum_green_size': 0, 
 'accum_blue_size': 0, 
 'accum_alpha_size': 0}

class CocoaConfig(Config):

    def match(self, canvas):
        attrs = []
        for name, value in self.get_gl_attributes():
            attr = _gl_attributes.get(name)
            if not not attr:
                if not value:
                    pass
                else:
                    attrs.append(attr)
                    if attr not in _boolean_gl_attributes:
                        attrs.append(int(value))

        attrs.append(cocoapy.NSOpenGLPFAAllRenderers)
        attrs.append(cocoapy.NSOpenGLPFAMaximumPolicy)
        if _os_x_version < os_x_release["snow_leopard"]:
            attrs.append(cocoapy.NSOpenGLPFAFullScreen)
            attrs.append(cocoapy.NSOpenGLPFAScreenMask)
            attrs.append(quartz.CGDisplayIDToOpenGLDisplayMask(quartz.CGMainDisplayID()))
        elif _os_x_version >= os_x_release["lion"]:
            version = (
             getattr(self, "major_version", None) or 2,
             getattr(self, "minor_version", None))
            attrs.append(cocoapy.NSOpenGLPFAOpenGLProfile)
            if version[0] >= 4 and _os_x_version >= os_x_release["mavericks"]:
                attrs.append(int(cocoapy.NSOpenGLProfileVersion4_1Core))
        elif version[0] >= 3:
            attrs.append(int(cocoapy.NSOpenGLProfileVersion3_2Core))
        else:
            attrs.append(int(cocoapy.NSOpenGLProfileVersionLegacy))
        attrs.append(0)
        attrsArrayType = c_uint32 * len(attrs)
        attrsArray = attrsArrayType(*attrs)
        pixel_format = NSOpenGLPixelFormat.alloc().initWithAttributes_(attrsArray)
        if pixel_format is None:
            return []
        else:
            return [
             CocoaCanvasConfig(canvas, self, pixel_format)]


class CocoaCanvasConfig(CanvasConfig):

    def __init__(self, canvas, config, pixel_format):
        super(CocoaCanvasConfig, self).__init__(canvas, config)
        self._pixel_format = pixel_format
        for name, attr in _gl_attributes.items():
            vals = c_int()
            self._pixel_format.getValues_forAttribute_forVirtualScreen_(byref(vals), attr, 0)
            setattr(self, name, vals.value)

        for name, value in _fake_gl_attributes.items():
            setattr(self, name, value)

        if _os_x_version >= os_x_release["lion"]:
            vals = c_int()
            profile = self._pixel_format.getValues_forAttribute_forVirtualScreen_(byref(vals), cocoapy.NSOpenGLPFAOpenGLProfile, 0)
            if vals.value == cocoapy.NSOpenGLProfileVersion4_1Core:
                setattr(self, "major_version", 4)
                setattr(self, "minor_version", 1)
            elif vals.value == cocoapy.NSOpenGLProfileVersion3_2Core:
                setattr(self, "major_version", 3)
                setattr(self, "minor_version", 2)
            else:
                setattr(self, "major_version", 2)
                setattr(self, "minor_version", 1)

    def create_context(self, share):
        if share:
            share_context = share._nscontext
        else:
            share_context = None
        nscontext = NSOpenGLContext.alloc().initWithFormat_shareContext_(self._pixel_format, share_context)
        return CocoaContext(self, nscontext, share)

    def compatible(self, canvas):
        return isinstance(canvas, CocoaCanvas)


class CocoaContext(Context):

    def __init__(self, config, nscontext, share):
        super(CocoaContext, self).__init__(config, share)
        self.config = config
        self._nscontext = nscontext

    def attach(self, canvas):
        if _os_x_version < os_x_release["lion"]:
            if self.config.requires_gl_3():
                raise ContextException("OpenGL 3 not supported")
        super(CocoaContext, self).attach(canvas)
        self._nscontext.setView_(canvas.nsview)
        self._nscontext.view().setWantsBestResolutionOpenGLSurface_(1)
        self.set_current()

    def detach(self):
        super(CocoaContext, self).detach()
        self._nscontext.clearDrawable()

    def set_current(self):
        self._nscontext.makeCurrentContext()
        super(CocoaContext, self).set_current()

    def update_geometry(self):
        self._nscontext.update()

    def set_full_screen(self):
        self._nscontext.makeCurrentContext()
        self._nscontext.setFullScreen()

    def destroy(self):
        super(CocoaContext, self).destroy()
        self._nscontext.release()
        self._nscontext = None

    def set_vsync(self, vsync=True):
        vals = c_int(vsync)
        self._nscontext.setValues_forParameter_(byref(vals), cocoapy.NSOpenGLCPSwapInterval)

    def get_vsync(self):
        vals = c_int()
        self._nscontext.getValues_forParameter_(byref(vals), cocoapy.NSOpenGLCPSwapInterval)
        return vals.value

    def flip(self):
        self._nscontext.flushBuffer()
