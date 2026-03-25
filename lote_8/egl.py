# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\libs\egl\egl.py
"""Wrapper for /usr/include/EGL/egl

Generated with:
wrap.py -o lib_egl.py /usr/include/EGL/egl.h

Do not modify this file.
"""
__docformat__ = "restructuredtext"
__version__ = "$Id$"
import ctypes
from ctypes import *
import pyglet.lib
_lib = pyglet.lib.load_library("EGL")
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


__egl_h_ = 1
EGL_EGL_PROTOTYPES = 1
EGL_VERSION_1_0 = 1
EGLBoolean = c_uint
EGLDisplay = POINTER(None)
EGLConfig = POINTER(None)
EGLSurface = POINTER(None)
EGLContext = POINTER(None)
__eglMustCastToProperFunctionPointerType = CFUNCTYPE(None)
EGL_ALPHA_SIZE = 12321
EGL_BAD_ACCESS = 12290
EGL_BAD_ALLOC = 12291
EGL_BAD_ATTRIBUTE = 12292
EGL_BAD_CONFIG = 12293
EGL_BAD_CONTEXT = 12294
EGL_BAD_CURRENT_SURFACE = 12295
EGL_BAD_DISPLAY = 12296
EGL_BAD_MATCH = 12297
EGL_BAD_NATIVE_PIXMAP = 12298
EGL_BAD_NATIVE_WINDOW = 12299
EGL_BAD_PARAMETER = 12300
EGL_BAD_SURFACE = 12301
EGL_BLUE_SIZE = 12322
EGL_BUFFER_SIZE = 12320
EGL_CONFIG_CAVEAT = 12327
EGL_CONFIG_ID = 12328
EGL_CORE_NATIVE_ENGINE = 12379
EGL_DEPTH_SIZE = 12325
EGL_DRAW = 12377
EGL_EXTENSIONS = 12373
EGL_FALSE = 0
EGL_GREEN_SIZE = 12323
EGL_HEIGHT = 12374
EGL_LARGEST_PBUFFER = 12376
EGL_LEVEL = 12329
EGL_MAX_PBUFFER_HEIGHT = 12330
EGL_MAX_PBUFFER_PIXELS = 12331
EGL_MAX_PBUFFER_WIDTH = 12332
EGL_NATIVE_RENDERABLE = 12333
EGL_NATIVE_VISUAL_ID = 12334
EGL_NATIVE_VISUAL_TYPE = 12335
EGL_NONE = 12344
EGL_NON_CONFORMANT_CONFIG = 12369
EGL_NOT_INITIALIZED = 12289
EGL_PBUFFER_BIT = 1
EGL_PIXMAP_BIT = 2
EGL_READ = 12378
EGL_RED_SIZE = 12324
EGL_SAMPLES = 12337
EGL_SAMPLE_BUFFERS = 12338
EGL_SLOW_CONFIG = 12368
EGL_STENCIL_SIZE = 12326
EGL_SUCCESS = 12288
EGL_SURFACE_TYPE = 12339
EGL_TRANSPARENT_BLUE_VALUE = 12341
EGL_TRANSPARENT_GREEN_VALUE = 12342
EGL_TRANSPARENT_RED_VALUE = 12343
EGL_TRANSPARENT_RGB = 12370
EGL_TRANSPARENT_TYPE = 12340
EGL_TRUE = 1
EGL_VENDOR = 12371
EGL_VERSION = 12372
EGL_WIDTH = 12375
EGL_WINDOW_BIT = 4
khronos_int32_t = c_int32
EGLint = khronos_int32_t
PFNEGLCHOOSECONFIGPROC = CFUNCTYPE(EGLBoolean, EGLDisplay, POINTER(EGLint), POINTER(EGLConfig), EGLint, POINTER(EGLint))
XID = c_ulong
Pixmap = XID
EGLNativePixmapType = Pixmap
PFNEGLCOPYBUFFERSPROC = CFUNCTYPE(EGLBoolean, EGLDisplay, EGLSurface, EGLNativePixmapType)
PFNEGLCREATECONTEXTPROC = CFUNCTYPE(EGLContext, EGLDisplay, EGLConfig, EGLContext, POINTER(EGLint))
PFNEGLCREATEPBUFFERSURFACEPROC = CFUNCTYPE(EGLSurface, EGLDisplay, EGLConfig, POINTER(EGLint))
PFNEGLCREATEPIXMAPSURFACEPROC = CFUNCTYPE(EGLSurface, EGLDisplay, EGLConfig, EGLNativePixmapType, POINTER(EGLint))
Window = XID
EGLNativeWindowType = Window
PFNEGLCREATEWINDOWSURFACEPROC = CFUNCTYPE(EGLSurface, EGLDisplay, EGLConfig, EGLNativeWindowType, POINTER(EGLint))
PFNEGLDESTROYCONTEXTPROC = CFUNCTYPE(EGLBoolean, EGLDisplay, EGLContext)
PFNEGLDESTROYSURFACEPROC = CFUNCTYPE(EGLBoolean, EGLDisplay, EGLSurface)
PFNEGLGETCONFIGATTRIBPROC = CFUNCTYPE(EGLBoolean, EGLDisplay, EGLConfig, EGLint, POINTER(EGLint))
PFNEGLGETCONFIGSPROC = CFUNCTYPE(EGLBoolean, EGLDisplay, POINTER(EGLConfig), EGLint, POINTER(EGLint))
PFNEGLGETCURRENTDISPLAYPROC = CFUNCTYPE(EGLDisplay)
PFNEGLGETCURRENTSURFACEPROC = CFUNCTYPE(EGLSurface, EGLint)

class struct__XDisplay(Structure):
    __slots__ = []


struct__XDisplay._fields_ = [
 (
  "_opaque_struct", c_int)]

class struct__XDisplay(Structure):
    __slots__ = []


struct__XDisplay._fields_ = [
 (
  "_opaque_struct", c_int)]
Display = struct__XDisplay
EGLNativeDisplayType = POINTER(Display)
PFNEGLGETDISPLAYPROC = CFUNCTYPE(EGLDisplay, EGLNativeDisplayType)
PFNEGLGETERRORPROC = CFUNCTYPE(EGLint)
PFNEGLGETPROCADDRESSPROC = CFUNCTYPE(__eglMustCastToProperFunctionPointerType, c_char_p)
PFNEGLINITIALIZEPROC = CFUNCTYPE(EGLBoolean, EGLDisplay, POINTER(EGLint), POINTER(EGLint))
PFNEGLMAKECURRENTPROC = CFUNCTYPE(EGLBoolean, EGLDisplay, EGLSurface, EGLSurface, EGLContext)
PFNEGLQUERYCONTEXTPROC = CFUNCTYPE(EGLBoolean, EGLDisplay, EGLContext, EGLint, POINTER(EGLint))
PFNEGLQUERYSTRINGPROC = CFUNCTYPE(c_char_p, EGLDisplay, EGLint)
PFNEGLQUERYSURFACEPROC = CFUNCTYPE(EGLBoolean, EGLDisplay, EGLSurface, EGLint, POINTER(EGLint))
PFNEGLSWAPBUFFERSPROC = CFUNCTYPE(EGLBoolean, EGLDisplay, EGLSurface)
PFNEGLTERMINATEPROC = CFUNCTYPE(EGLBoolean, EGLDisplay)
PFNEGLWAITGLPROC = CFUNCTYPE(EGLBoolean)
PFNEGLWAITNATIVEPROC = CFUNCTYPE(EGLBoolean, EGLint)
eglChooseConfig = _lib.eglChooseConfig
eglChooseConfig.restype = EGLBoolean
eglChooseConfig.argtypes = [EGLDisplay, POINTER(EGLint), POINTER(EGLConfig), EGLint, POINTER(EGLint)]
eglCopyBuffers = _lib.eglCopyBuffers
eglCopyBuffers.restype = EGLBoolean
eglCopyBuffers.argtypes = [EGLDisplay, EGLSurface, EGLNativePixmapType]
eglCreateContext = _lib.eglCreateContext
eglCreateContext.restype = EGLContext
eglCreateContext.argtypes = [EGLDisplay, EGLConfig, EGLContext, POINTER(EGLint)]
eglCreatePbufferSurface = _lib.eglCreatePbufferSurface
eglCreatePbufferSurface.restype = EGLSurface
eglCreatePbufferSurface.argtypes = [EGLDisplay, EGLConfig, POINTER(EGLint)]
eglCreatePixmapSurface = _lib.eglCreatePixmapSurface
eglCreatePixmapSurface.restype = EGLSurface
eglCreatePixmapSurface.argtypes = [EGLDisplay, EGLConfig, EGLNativePixmapType, POINTER(EGLint)]
eglCreateWindowSurface = _lib.eglCreateWindowSurface
eglCreateWindowSurface.restype = EGLSurface
eglCreateWindowSurface.argtypes = [EGLDisplay, EGLConfig, EGLNativeWindowType, POINTER(EGLint)]
eglDestroyContext = _lib.eglDestroyContext
eglDestroyContext.restype = EGLBoolean
eglDestroyContext.argtypes = [EGLDisplay, EGLContext]
eglDestroySurface = _lib.eglDestroySurface
eglDestroySurface.restype = EGLBoolean
eglDestroySurface.argtypes = [EGLDisplay, EGLSurface]
eglGetConfigAttrib = _lib.eglGetConfigAttrib
eglGetConfigAttrib.restype = EGLBoolean
eglGetConfigAttrib.argtypes = [EGLDisplay, EGLConfig, EGLint, POINTER(EGLint)]
eglGetConfigs = _lib.eglGetConfigs
eglGetConfigs.restype = EGLBoolean
eglGetConfigs.argtypes = [EGLDisplay, POINTER(EGLConfig), EGLint, POINTER(EGLint)]
eglGetCurrentDisplay = _lib.eglGetCurrentDisplay
eglGetCurrentDisplay.restype = EGLDisplay
eglGetCurrentDisplay.argtypes = []
eglGetCurrentSurface = _lib.eglGetCurrentSurface
eglGetCurrentSurface.restype = EGLSurface
eglGetCurrentSurface.argtypes = [EGLint]
eglGetDisplay = _lib.eglGetDisplay
eglGetDisplay.restype = EGLDisplay
eglGetDisplay.argtypes = [EGLNativeDisplayType]
eglGetError = _lib.eglGetError
eglGetError.restype = EGLint
eglGetError.argtypes = []
eglGetProcAddress = _lib.eglGetProcAddress
eglGetProcAddress.restype = __eglMustCastToProperFunctionPointerType
eglGetProcAddress.argtypes = [c_char_p]
eglInitialize = _lib.eglInitialize
eglInitialize.restype = EGLBoolean
eglInitialize.argtypes = [EGLDisplay, POINTER(EGLint), POINTER(EGLint)]
eglMakeCurrent = _lib.eglMakeCurrent
eglMakeCurrent.restype = EGLBoolean
eglMakeCurrent.argtypes = [EGLDisplay, EGLSurface, EGLSurface, EGLContext]
eglQueryContext = _lib.eglQueryContext
eglQueryContext.restype = EGLBoolean
eglQueryContext.argtypes = [EGLDisplay, EGLContext, EGLint, POINTER(EGLint)]
eglQueryString = _lib.eglQueryString
eglQueryString.restype = c_char_p
eglQueryString.argtypes = [EGLDisplay, EGLint]
eglQuerySurface = _lib.eglQuerySurface
eglQuerySurface.restype = EGLBoolean
eglQuerySurface.argtypes = [EGLDisplay, EGLSurface, EGLint, POINTER(EGLint)]
eglSwapBuffers = _lib.eglSwapBuffers
eglSwapBuffers.restype = EGLBoolean
eglSwapBuffers.argtypes = [EGLDisplay, EGLSurface]
eglTerminate = _lib.eglTerminate
eglTerminate.restype = EGLBoolean
eglTerminate.argtypes = [EGLDisplay]
eglWaitGL = _lib.eglWaitGL
eglWaitGL.restype = EGLBoolean
eglWaitGL.argtypes = []
eglWaitNative = _lib.eglWaitNative
eglWaitNative.restype = EGLBoolean
eglWaitNative.argtypes = [EGLint]
EGL_VERSION_1_1 = 1
EGL_BACK_BUFFER = 12420
EGL_BIND_TO_TEXTURE_RGB = 12345
EGL_BIND_TO_TEXTURE_RGBA = 12346
EGL_CONTEXT_LOST = 12302
EGL_MIN_SWAP_INTERVAL = 12347
EGL_MAX_SWAP_INTERVAL = 12348
EGL_MIPMAP_TEXTURE = 12418
EGL_MIPMAP_LEVEL = 12419
EGL_NO_TEXTURE = 12380
EGL_TEXTURE_2D = 12383
EGL_TEXTURE_FORMAT = 12416
EGL_TEXTURE_RGB = 12381
EGL_TEXTURE_RGBA = 12382
EGL_TEXTURE_TARGET = 12417
PFNEGLBINDTEXIMAGEPROC = CFUNCTYPE(EGLBoolean, EGLDisplay, EGLSurface, EGLint)
PFNEGLRELEASETEXIMAGEPROC = CFUNCTYPE(EGLBoolean, EGLDisplay, EGLSurface, EGLint)
PFNEGLSURFACEATTRIBPROC = CFUNCTYPE(EGLBoolean, EGLDisplay, EGLSurface, EGLint, EGLint)
PFNEGLSWAPINTERVALPROC = CFUNCTYPE(EGLBoolean, EGLDisplay, EGLint)
eglBindTexImage = _lib.eglBindTexImage
eglBindTexImage.restype = EGLBoolean
eglBindTexImage.argtypes = [EGLDisplay, EGLSurface, EGLint]
eglReleaseTexImage = _lib.eglReleaseTexImage
eglReleaseTexImage.restype = EGLBoolean
eglReleaseTexImage.argtypes = [EGLDisplay, EGLSurface, EGLint]
eglSurfaceAttrib = _lib.eglSurfaceAttrib
eglSurfaceAttrib.restype = EGLBoolean
eglSurfaceAttrib.argtypes = [EGLDisplay, EGLSurface, EGLint, EGLint]
eglSwapInterval = _lib.eglSwapInterval
eglSwapInterval.restype = EGLBoolean
eglSwapInterval.argtypes = [EGLDisplay, EGLint]
EGL_VERSION_1_2 = 1
EGLenum = c_uint
EGLClientBuffer = POINTER(None)
EGL_ALPHA_FORMAT = 12424
EGL_ALPHA_FORMAT_NONPRE = 12427
EGL_ALPHA_FORMAT_PRE = 12428
EGL_ALPHA_MASK_SIZE = 12350
EGL_BUFFER_PRESERVED = 12436
EGL_BUFFER_DESTROYED = 12437
EGL_CLIENT_APIS = 12429
EGL_COLORSPACE = 12423
EGL_COLORSPACE_sRGB = 12425
EGL_COLORSPACE_LINEAR = 12426
EGL_COLOR_BUFFER_TYPE = 12351
EGL_CONTEXT_CLIENT_TYPE = 12439
EGL_DISPLAY_SCALING = 10000
EGL_HORIZONTAL_RESOLUTION = 12432
EGL_LUMINANCE_BUFFER = 12431
EGL_LUMINANCE_SIZE = 12349
EGL_OPENGL_ES_BIT = 1
EGL_OPENVG_BIT = 2
EGL_OPENGL_ES_API = 12448
EGL_OPENVG_API = 12449
EGL_OPENVG_IMAGE = 12438
EGL_PIXEL_ASPECT_RATIO = 12434
EGL_RENDERABLE_TYPE = 12352
EGL_RENDER_BUFFER = 12422
EGL_RGB_BUFFER = 12430
EGL_SINGLE_BUFFER = 12421
EGL_SWAP_BEHAVIOR = 12435
EGL_VERTICAL_RESOLUTION = 12433
PFNEGLBINDAPIPROC = CFUNCTYPE(EGLBoolean, EGLenum)
PFNEGLQUERYAPIPROC = CFUNCTYPE(EGLenum)
PFNEGLCREATEPBUFFERFROMCLIENTBUFFERPROC = CFUNCTYPE(EGLSurface, EGLDisplay, EGLenum, EGLClientBuffer, EGLConfig, POINTER(EGLint))
PFNEGLRELEASETHREADPROC = CFUNCTYPE(EGLBoolean)
PFNEGLWAITCLIENTPROC = CFUNCTYPE(EGLBoolean)
eglBindAPI = _lib.eglBindAPI
eglBindAPI.restype = EGLBoolean
eglBindAPI.argtypes = [EGLenum]
eglQueryAPI = _lib.eglQueryAPI
eglQueryAPI.restype = EGLenum
eglQueryAPI.argtypes = []
eglCreatePbufferFromClientBuffer = _lib.eglCreatePbufferFromClientBuffer
eglCreatePbufferFromClientBuffer.restype = EGLSurface
eglCreatePbufferFromClientBuffer.argtypes = [EGLDisplay, EGLenum, EGLClientBuffer, EGLConfig, POINTER(EGLint)]
eglReleaseThread = _lib.eglReleaseThread
eglReleaseThread.restype = EGLBoolean
eglReleaseThread.argtypes = []
eglWaitClient = _lib.eglWaitClient
eglWaitClient.restype = EGLBoolean
eglWaitClient.argtypes = []
EGL_VERSION_1_3 = 1
EGL_CONFORMANT = 12354
EGL_CONTEXT_CLIENT_VERSION = 12440
EGL_MATCH_NATIVE_PIXMAP = 12353
EGL_OPENGL_ES2_BIT = 4
EGL_VG_ALPHA_FORMAT = 12424
EGL_VG_ALPHA_FORMAT_NONPRE = 12427
EGL_VG_ALPHA_FORMAT_PRE = 12428
EGL_VG_ALPHA_FORMAT_PRE_BIT = 64
EGL_VG_COLORSPACE = 12423
EGL_VG_COLORSPACE_sRGB = 12425
EGL_VG_COLORSPACE_LINEAR = 12426
EGL_VG_COLORSPACE_LINEAR_BIT = 32
EGL_VERSION_1_4 = 1
EGL_MULTISAMPLE_RESOLVE_BOX_BIT = 512
EGL_MULTISAMPLE_RESOLVE = 12441
EGL_MULTISAMPLE_RESOLVE_DEFAULT = 12442
EGL_MULTISAMPLE_RESOLVE_BOX = 12443
EGL_OPENGL_API = 12450
EGL_OPENGL_BIT = 8
EGL_SWAP_BEHAVIOR_PRESERVED_BIT = 1024
PFNEGLGETCURRENTCONTEXTPROC = CFUNCTYPE(EGLContext)
eglGetCurrentContext = _lib.eglGetCurrentContext
eglGetCurrentContext.restype = EGLContext
eglGetCurrentContext.argtypes = []
EGL_VERSION_1_5 = 1
EGLSync = POINTER(None)
intptr_t = c_long
EGLAttrib = intptr_t
khronos_uint64_t = c_uint64
khronos_utime_nanoseconds_t = khronos_uint64_t
EGLTime = khronos_utime_nanoseconds_t
EGLImage = POINTER(None)
EGL_CONTEXT_MAJOR_VERSION = 12440
EGL_CONTEXT_MINOR_VERSION = 12539
EGL_CONTEXT_OPENGL_PROFILE_MASK = 12541
EGL_CONTEXT_OPENGL_RESET_NOTIFICATION_STRATEGY = 12733
EGL_NO_RESET_NOTIFICATION = 12734
EGL_LOSE_CONTEXT_ON_RESET = 12735
EGL_CONTEXT_OPENGL_CORE_PROFILE_BIT = 1
EGL_CONTEXT_OPENGL_COMPATIBILITY_PROFILE_BIT = 2
EGL_CONTEXT_OPENGL_DEBUG = 12720
EGL_CONTEXT_OPENGL_FORWARD_COMPATIBLE = 12721
EGL_CONTEXT_OPENGL_ROBUST_ACCESS = 12722
EGL_OPENGL_ES3_BIT = 64
EGL_CL_EVENT_HANDLE = 12444
EGL_SYNC_CL_EVENT = 12542
EGL_SYNC_CL_EVENT_COMPLETE = 12543
EGL_SYNC_PRIOR_COMMANDS_COMPLETE = 12528
EGL_SYNC_TYPE = 12535
EGL_SYNC_STATUS = 12529
EGL_SYNC_CONDITION = 12536
EGL_SIGNALED = 12530
EGL_UNSIGNALED = 12531
EGL_SYNC_FLUSH_COMMANDS_BIT = 1
EGL_FOREVER = 18446744073709551615
EGL_TIMEOUT_EXPIRED = 12533
EGL_CONDITION_SATISFIED = 12534
EGL_SYNC_FENCE = 12537
EGL_GL_COLORSPACE = 12445
EGL_GL_COLORSPACE_SRGB = 12425
EGL_GL_COLORSPACE_LINEAR = 12426
EGL_GL_RENDERBUFFER = 12473
EGL_GL_TEXTURE_2D = 12465
EGL_GL_TEXTURE_LEVEL = 12476
EGL_GL_TEXTURE_3D = 12466
EGL_GL_TEXTURE_ZOFFSET = 12477
EGL_GL_TEXTURE_CUBE_MAP_POSITIVE_X = 12467
EGL_GL_TEXTURE_CUBE_MAP_NEGATIVE_X = 12468
EGL_GL_TEXTURE_CUBE_MAP_POSITIVE_Y = 12469
EGL_GL_TEXTURE_CUBE_MAP_NEGATIVE_Y = 12470
EGL_GL_TEXTURE_CUBE_MAP_POSITIVE_Z = 12471
EGL_GL_TEXTURE_CUBE_MAP_NEGATIVE_Z = 12472
EGL_IMAGE_PRESERVED = 12498
PFNEGLCREATESYNCPROC = CFUNCTYPE(EGLSync, EGLDisplay, EGLenum, POINTER(EGLAttrib))
PFNEGLDESTROYSYNCPROC = CFUNCTYPE(EGLBoolean, EGLDisplay, EGLSync)
PFNEGLCLIENTWAITSYNCPROC = CFUNCTYPE(EGLint, EGLDisplay, EGLSync, EGLint, EGLTime)
PFNEGLGETSYNCATTRIBPROC = CFUNCTYPE(EGLBoolean, EGLDisplay, EGLSync, EGLint, POINTER(EGLAttrib))
PFNEGLCREATEIMAGEPROC = CFUNCTYPE(EGLImage, EGLDisplay, EGLContext, EGLenum, EGLClientBuffer, POINTER(EGLAttrib))
PFNEGLDESTROYIMAGEPROC = CFUNCTYPE(EGLBoolean, EGLDisplay, EGLImage)
PFNEGLGETPLATFORMDISPLAYPROC = CFUNCTYPE(EGLDisplay, EGLenum, POINTER(None), POINTER(EGLAttrib))
PFNEGLCREATEPLATFORMWINDOWSURFACEPROC = CFUNCTYPE(EGLSurface, EGLDisplay, EGLConfig, POINTER(None), POINTER(EGLAttrib))
PFNEGLCREATEPLATFORMPIXMAPSURFACEPROC = CFUNCTYPE(EGLSurface, EGLDisplay, EGLConfig, POINTER(None), POINTER(EGLAttrib))
PFNEGLWAITSYNCPROC = CFUNCTYPE(EGLBoolean, EGLDisplay, EGLSync, EGLint)
eglCreateSync = _lib.eglCreateSync
eglCreateSync.restype = EGLSync
eglCreateSync.argtypes = [EGLDisplay, EGLenum, POINTER(EGLAttrib)]
eglDestroySync = _lib.eglDestroySync
eglDestroySync.restype = EGLBoolean
eglDestroySync.argtypes = [EGLDisplay, EGLSync]
eglClientWaitSync = _lib.eglClientWaitSync
eglClientWaitSync.restype = EGLint
eglClientWaitSync.argtypes = [EGLDisplay, EGLSync, EGLint, EGLTime]
eglGetSyncAttrib = _lib.eglGetSyncAttrib
eglGetSyncAttrib.restype = EGLBoolean
eglGetSyncAttrib.argtypes = [EGLDisplay, EGLSync, EGLint, POINTER(EGLAttrib)]
eglCreateImage = _lib.eglCreateImage
eglCreateImage.restype = EGLImage
eglCreateImage.argtypes = [EGLDisplay, EGLContext, EGLenum, EGLClientBuffer, POINTER(EGLAttrib)]
eglDestroyImage = _lib.eglDestroyImage
eglDestroyImage.restype = EGLBoolean
eglDestroyImage.argtypes = [EGLDisplay, EGLImage]
eglGetPlatformDisplay = _lib.eglGetPlatformDisplay
eglGetPlatformDisplay.restype = EGLDisplay
eglGetPlatformDisplay.argtypes = [EGLenum, POINTER(None), POINTER(EGLAttrib)]
eglCreatePlatformWindowSurface = _lib.eglCreatePlatformWindowSurface
eglCreatePlatformWindowSurface.restype = EGLSurface
eglCreatePlatformWindowSurface.argtypes = [EGLDisplay, EGLConfig, POINTER(None), POINTER(EGLAttrib)]
eglCreatePlatformPixmapSurface = _lib.eglCreatePlatformPixmapSurface
eglCreatePlatformPixmapSurface.restype = EGLSurface
eglCreatePlatformPixmapSurface.argtypes = [EGLDisplay, EGLConfig, POINTER(None), POINTER(EGLAttrib)]
eglWaitSync = _lib.eglWaitSync
eglWaitSync.restype = EGLBoolean
eglWaitSync.argtypes = [EGLDisplay, EGLSync, EGLint]
__all__ = [
 '__egl_h_', 'EGL_EGL_PROTOTYPES', 'EGL_VERSION_1_0', 'EGLBoolean', 
 'EGLDisplay', 
 'EGLConfig', 'EGLSurface', 'EGLContext', 
 '__eglMustCastToProperFunctionPointerType', 
 'EGL_ALPHA_SIZE', 
 'EGL_BAD_ACCESS', 'EGL_BAD_ALLOC', 'EGL_BAD_ATTRIBUTE', 
 'EGL_BAD_CONFIG', 
 'EGL_BAD_CONTEXT', 'EGL_BAD_CURRENT_SURFACE', 'EGL_BAD_DISPLAY', 
 'EGL_BAD_MATCH', 
 'EGL_BAD_NATIVE_PIXMAP', 'EGL_BAD_NATIVE_WINDOW', 
 'EGL_BAD_PARAMETER', 'EGL_BAD_SURFACE', 
 'EGL_BLUE_SIZE', 'EGL_BUFFER_SIZE', 
 'EGL_CONFIG_CAVEAT', 'EGL_CONFIG_ID', 
 'EGL_CORE_NATIVE_ENGINE', 
 'EGL_DEPTH_SIZE', 'EGL_DRAW', 'EGL_EXTENSIONS', 
 'EGL_FALSE', 'EGL_GREEN_SIZE', 
 'EGL_HEIGHT', 'EGL_LARGEST_PBUFFER', 'EGL_LEVEL', 
 'EGL_MAX_PBUFFER_HEIGHT', 
 'EGL_MAX_PBUFFER_PIXELS', 'EGL_MAX_PBUFFER_WIDTH', 
 'EGL_NATIVE_RENDERABLE', 
 'EGL_NATIVE_VISUAL_ID', 'EGL_NATIVE_VISUAL_TYPE', 
 'EGL_NONE', 
 'EGL_NON_CONFORMANT_CONFIG', 'EGL_NOT_INITIALIZED', 'EGL_PBUFFER_BIT', 
 'EGL_PIXMAP_BIT', 
 'EGL_READ', 'EGL_RED_SIZE', 'EGL_SAMPLES', 
 'EGL_SAMPLE_BUFFERS', 'EGL_SLOW_CONFIG', 
 'EGL_STENCIL_SIZE', 'EGL_SUCCESS', 
 'EGL_SURFACE_TYPE', 'EGL_TRANSPARENT_BLUE_VALUE', 
 'EGL_TRANSPARENT_GREEN_VALUE', 
 'EGL_TRANSPARENT_RED_VALUE', 
 'EGL_TRANSPARENT_RGB', 'EGL_TRANSPARENT_TYPE', 
 'EGL_TRUE', 'EGL_VENDOR', 
 'EGL_VERSION', 'EGL_WIDTH', 'EGL_WINDOW_BIT', 
 'PFNEGLCHOOSECONFIGPROC', 
 'PFNEGLCOPYBUFFERSPROC', 'PFNEGLCREATECONTEXTPROC', 
 'PFNEGLCREATEPBUFFERSURFACEPROC', 
 'PFNEGLCREATEPIXMAPSURFACEPROC', 
 'PFNEGLCREATEWINDOWSURFACEPROC', 'PFNEGLDESTROYCONTEXTPROC', 
 'PFNEGLDESTROYSURFACEPROC', 
 'PFNEGLGETCONFIGATTRIBPROC', 
 'PFNEGLGETCONFIGSPROC', 'PFNEGLGETCURRENTDISPLAYPROC', 
 'PFNEGLGETCURRENTSURFACEPROC', 
 'PFNEGLGETDISPLAYPROC', 'PFNEGLGETERRORPROC', 
 'PFNEGLGETPROCADDRESSPROC', 
 'PFNEGLINITIALIZEPROC', 'PFNEGLMAKECURRENTPROC', 
 'PFNEGLQUERYCONTEXTPROC', 
 'PFNEGLQUERYSTRINGPROC', 'PFNEGLQUERYSURFACEPROC', 
 'PFNEGLSWAPBUFFERSPROC', 
 'PFNEGLTERMINATEPROC', 'PFNEGLWAITGLPROC', 
 'PFNEGLWAITNATIVEPROC', 'eglChooseConfig', 
 'eglCopyBuffers', 
 'eglCreateContext', 'eglCreatePbufferSurface', 'eglCreatePixmapSurface', 
 'eglCreateWindowSurface', 
 'eglDestroyContext', 'eglDestroySurface', 
 'eglGetConfigAttrib', 'eglGetConfigs', 
 'eglGetCurrentDisplay', 
 'eglGetCurrentSurface', 'eglGetDisplay', 'eglGetError', 
 'eglGetProcAddress', 
 'eglInitialize', 'eglMakeCurrent', 'eglQueryContext', 
 'eglQueryString', 
 'eglQuerySurface', 'eglSwapBuffers', 'eglTerminate', 
 'eglWaitGL', 
 'eglWaitNative', 'EGL_VERSION_1_1', 'EGL_BACK_BUFFER', 
 'EGL_BIND_TO_TEXTURE_RGB', 
 'EGL_BIND_TO_TEXTURE_RGBA', 'EGL_CONTEXT_LOST', 
 'EGL_MIN_SWAP_INTERVAL', 
 'EGL_MAX_SWAP_INTERVAL', 'EGL_MIPMAP_TEXTURE', 
 'EGL_MIPMAP_LEVEL', 'EGL_NO_TEXTURE', 
 'EGL_TEXTURE_2D', 'EGL_TEXTURE_FORMAT', 
 'EGL_TEXTURE_RGB', 'EGL_TEXTURE_RGBA', 
 'EGL_TEXTURE_TARGET', 
 'PFNEGLBINDTEXIMAGEPROC', 'PFNEGLRELEASETEXIMAGEPROC', 
 'PFNEGLSURFACEATTRIBPROC', 
 'PFNEGLSWAPINTERVALPROC', 'eglBindTexImage', 
 'eglReleaseTexImage', 'eglSurfaceAttrib', 
 'eglSwapInterval', 
 'EGL_VERSION_1_2', 'EGLenum', 'EGLClientBuffer', 'EGL_ALPHA_FORMAT', 
 'EGL_ALPHA_FORMAT_NONPRE', 
 'EGL_ALPHA_FORMAT_PRE', 'EGL_ALPHA_MASK_SIZE', 
 'EGL_BUFFER_PRESERVED', 'EGL_BUFFER_DESTROYED', 
 'EGL_CLIENT_APIS', 
 'EGL_COLORSPACE', 'EGL_COLORSPACE_sRGB', 'EGL_COLORSPACE_LINEAR', 
 'EGL_COLOR_BUFFER_TYPE', 
 'EGL_CONTEXT_CLIENT_TYPE', 'EGL_DISPLAY_SCALING', 
 'EGL_HORIZONTAL_RESOLUTION', 
 'EGL_LUMINANCE_BUFFER', 'EGL_LUMINANCE_SIZE', 
 'EGL_OPENGL_ES_BIT', 'EGL_OPENVG_BIT', 
 'EGL_OPENGL_ES_API', 'EGL_OPENVG_API', 
 'EGL_OPENVG_IMAGE', 'EGL_PIXEL_ASPECT_RATIO', 
 'EGL_RENDERABLE_TYPE', 
 'EGL_RENDER_BUFFER', 'EGL_RGB_BUFFER', 'EGL_SINGLE_BUFFER', 
 'EGL_SWAP_BEHAVIOR', 
 'EGL_VERTICAL_RESOLUTION', 'PFNEGLBINDAPIPROC', 
 'PFNEGLQUERYAPIPROC', 'PFNEGLCREATEPBUFFERFROMCLIENTBUFFERPROC', 
 'PFNEGLRELEASETHREADPROC', 
 'PFNEGLWAITCLIENTPROC', 'eglBindAPI', 
 'eglQueryAPI', 'eglCreatePbufferFromClientBuffer', 
 'eglReleaseThread', 
 'eglWaitClient', 'EGL_VERSION_1_3', 'EGL_CONFORMANT', 
 'EGL_CONTEXT_CLIENT_VERSION', 
 'EGL_MATCH_NATIVE_PIXMAP', 'EGL_OPENGL_ES2_BIT', 
 'EGL_VG_ALPHA_FORMAT', 
 'EGL_VG_ALPHA_FORMAT_NONPRE', 
 'EGL_VG_ALPHA_FORMAT_PRE', 'EGL_VG_ALPHA_FORMAT_PRE_BIT', 
 'EGL_VG_COLORSPACE', 
 'EGL_VG_COLORSPACE_sRGB', 'EGL_VG_COLORSPACE_LINEAR', 
 'EGL_VG_COLORSPACE_LINEAR_BIT', 
 'EGL_VERSION_1_4', 
 'EGL_MULTISAMPLE_RESOLVE_BOX_BIT', 'EGL_MULTISAMPLE_RESOLVE', 
 'EGL_MULTISAMPLE_RESOLVE_DEFAULT', 
 'EGL_MULTISAMPLE_RESOLVE_BOX', 
 'EGL_OPENGL_API', 'EGL_OPENGL_BIT', 'EGL_SWAP_BEHAVIOR_PRESERVED_BIT', 
 'PFNEGLGETCURRENTCONTEXTPROC', 
 'eglGetCurrentContext', 'EGL_VERSION_1_5', 
 'EGLSync', 'EGLAttrib', 'EGLTime', 
 'EGLImage', 'EGL_CONTEXT_MAJOR_VERSION', 
 'EGL_CONTEXT_MINOR_VERSION', 'EGL_CONTEXT_OPENGL_PROFILE_MASK', 
 'EGL_CONTEXT_OPENGL_RESET_NOTIFICATION_STRATEGY', 
 'EGL_NO_RESET_NOTIFICATION', 
 'EGL_LOSE_CONTEXT_ON_RESET', 'EGL_CONTEXT_OPENGL_CORE_PROFILE_BIT', 
 'EGL_CONTEXT_OPENGL_COMPATIBILITY_PROFILE_BIT', 
 'EGL_CONTEXT_OPENGL_DEBUG', 
 'EGL_CONTEXT_OPENGL_FORWARD_COMPATIBLE', 'EGL_CONTEXT_OPENGL_ROBUST_ACCESS', 
 'EGL_OPENGL_ES3_BIT', 
 'EGL_CL_EVENT_HANDLE', 'EGL_SYNC_CL_EVENT', 
 'EGL_SYNC_CL_EVENT_COMPLETE', 
 'EGL_SYNC_PRIOR_COMMANDS_COMPLETE', 
 'EGL_SYNC_TYPE', 'EGL_SYNC_STATUS', 
 'EGL_SYNC_CONDITION', 'EGL_SIGNALED', 
 'EGL_UNSIGNALED', 'EGL_SYNC_FLUSH_COMMANDS_BIT', 
 'EGL_FOREVER', 
 'EGL_TIMEOUT_EXPIRED', 'EGL_CONDITION_SATISFIED', 'EGL_SYNC_FENCE', 
 'EGL_GL_COLORSPACE', 
 'EGL_GL_COLORSPACE_SRGB', 'EGL_GL_COLORSPACE_LINEAR', 
 'EGL_GL_RENDERBUFFER', 
 'EGL_GL_TEXTURE_2D', 'EGL_GL_TEXTURE_LEVEL', 
 'EGL_GL_TEXTURE_3D', 'EGL_GL_TEXTURE_ZOFFSET', 
 'EGL_GL_TEXTURE_CUBE_MAP_POSITIVE_X', 
 'EGL_GL_TEXTURE_CUBE_MAP_NEGATIVE_X', 
 'EGL_GL_TEXTURE_CUBE_MAP_POSITIVE_Y', 
 'EGL_GL_TEXTURE_CUBE_MAP_NEGATIVE_Y', 
 'EGL_GL_TEXTURE_CUBE_MAP_POSITIVE_Z', 
 'EGL_GL_TEXTURE_CUBE_MAP_NEGATIVE_Z', 
 'EGL_IMAGE_PRESERVED', 'PFNEGLCREATESYNCPROC', 
 'PFNEGLDESTROYSYNCPROC', 
 'PFNEGLCLIENTWAITSYNCPROC', 'PFNEGLGETSYNCATTRIBPROC', 
 'PFNEGLCREATEIMAGEPROC', 
 'PFNEGLDESTROYIMAGEPROC', 
 'PFNEGLGETPLATFORMDISPLAYPROC', 'PFNEGLCREATEPLATFORMWINDOWSURFACEPROC', 
 'PFNEGLCREATEPLATFORMPIXMAPSURFACEPROC', 
 'PFNEGLWAITSYNCPROC', 
 'eglCreateSync', 'eglDestroySync', 'eglClientWaitSync', 
 'eglGetSyncAttrib', 
 'eglCreateImage', 'eglDestroyImage', 'eglGetPlatformDisplay', 
 'eglCreatePlatformWindowSurface', 
 'eglCreatePlatformPixmapSurface', 
 'eglWaitSync']
