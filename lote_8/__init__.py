# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\__init__.py
"""pyglet is a cross-platform games and multimedia package.

Detailed documentation is available at http://www.pyglet.org
"""
import os, sys
from typing import TYPE_CHECKING
if "sphinx" in sys.modules:
    setattr(sys, "is_pyglet_doc_run", True)
_is_pyglet_doc_run = hasattr(sys, "is_pyglet_doc_run") and sys.is_pyglet_doc_run
version = "1.5.19"
if sys.version_info < (3, 6):
    raise Exception("pyglet %s requires Python 3.6 or newer." % version)
compat_platform = sys.platform
if "bsd" in compat_platform:
    compat_platform = "linux-compat"
_enable_optimisations = not True
if getattr(sys, "frozen", None):
    _enable_optimisations = True
options = {'audio':('xaudio2', 'directsound', 'openal', 'pulse', 'silent'), 
 'debug_font':False, 
 'debug_gl':not _enable_optimisations, 
 'debug_gl_trace':False, 
 'debug_gl_trace_args':False, 
 'debug_graphics_batch':False, 
 'debug_lib':False, 
 'debug_media':False, 
 'debug_texture':False, 
 'debug_trace':False, 
 'debug_trace_args':False, 
 'debug_trace_depth':1, 
 'debug_trace_flush':True, 
 'debug_win32':False, 
 'debug_x11':False, 
 'graphics_vbo':True, 
 'shadow_window':True, 
 'vsync':None, 
 'xsync':True, 
 'xlib_fullscreen_override_redirect':False, 
 'darwin_cocoa':True, 
 'search_local_libs':True, 
 'advanced_font_features':False, 
 'headless':False, 
 'headless_device':0}
_option_types = {
 'audio': tuple, 
 'debug_font': bool, 
 'debug_gl': bool, 
 'debug_gl_trace': bool, 
 'debug_gl_trace_args': bool, 
 'debug_graphics_batch': bool, 
 'debug_lib': bool, 
 'debug_media': bool, 
 'debug_texture': bool, 
 'debug_trace': bool, 
 'debug_trace_args': bool, 
 'debug_trace_depth': int, 
 'debug_trace_flush': bool, 
 'debug_win32': bool, 
 'debug_x11': bool, 
 'graphics_vbo': bool, 
 'shadow_window': bool, 
 'vsync': bool, 
 'xsync': bool, 
 'xlib_fullscreen_override_redirect': bool, 
 'advanced_font_features': bool, 
 'headless': bool, 
 'headless_device': int}

def _read_environment():
    """Read defaults for options from environment"""
    for key in options:
        env = "PYGLET_%s" % key.upper()
        try:
            value = os.environ[env]
            if _option_types[key] is tuple:
                options[key] = value.split(",")
            elif _option_types[key] is bool:
                options[key] = value in ('true', 'TRUE', 'True', '1')
            else:
                if _option_types[key] is int:
                    options[key] = int(value)
        except KeyError:
            pass


_read_environment()
if compat_platform == "cygwin":
    import ctypes
    ctypes.windll = ctypes.cdll
    ctypes.oledll = ctypes.cdll
    ctypes.WINFUNCTYPE = ctypes.CFUNCTYPE
    ctypes.HRESULT = ctypes.c_long
else:
    _trace_filename_abbreviations = {}

    def _trace_repr(value, size=40):
        value = repr(value)
        if len(value) > size:
            value = value[:size // 2 - 2] + "..." + value[-size // 2 - 1:]
        return value


    def _trace_frame(thread, frame, indent):
        from pyglet import lib
        if frame.f_code is lib._TraceFunction.__call__.__code__:
            is_ctypes = True
            func = frame.f_locals["self"]._func
            name = func.__name__
            location = "[ctypes]"
        else:
            is_ctypes = False
            code = frame.f_code
            name = code.co_name
            path = code.co_filename
            line = code.co_firstlineno
            try:
                filename = _trace_filename_abbreviations[path]
            except KeyError:
                dir = ""
                path, filename = os.path.split(path)
                while len(dir + filename) < 30:
                    filename = os.path.join(dir, filename)
                    path, dir = os.path.split(path)
                    if not dir:
                        filename = os.path.join("", filename)
                        break
                else:
                    filename = os.path.join("...", filename)

                _trace_filename_abbreviations[path] = filename

            location = "(%s:%d)" % (filename, line)
        if indent:
            name = "Called from %s" % name
        else:
            print("[%d] %s%s %s" % (thread, indent, name, location))
            if _trace_args:
                if is_ctypes:
                    args = [_trace_repr(arg) for arg in frame.f_locals["args"]]
                    print("  %sargs=(%s)" % (indent, ", ".join(args)))
                else:
                    for argname in code.co_varnames[:code.co_argcount]:
                        try:
                            argvalue = _trace_repr(frame.f_locals[argname])
                            print("  %s%s=%s" % (indent, argname, argvalue))
                        except:
                            pass

        if _trace_flush:
            sys.stdout.flush()


    def _thread_trace_func(thread):

        def _trace_func(frame, event, arg):
            if event == "call":
                indent = ""
                for i in range(_trace_depth):
                    _trace_frame(thread, frame, indent)
                    indent += "  "
                    frame = frame.f_back
                    if not frame:
                        break

            elif event == "exception":
                exception, value, traceback = arg
                print("First chance exception raised:", repr(exception))

        return _trace_func


    def _install_trace():
        global _trace_thread_count
        sys.setprofile(_thread_trace_func(_trace_thread_count))
        _trace_thread_count += 1


    _trace_thread_count = 0
    _trace_args = options["debug_trace_args"]
    _trace_depth = options["debug_trace_depth"]
    _trace_flush = options["debug_trace_flush"]
    if options["debug_trace"]:
        _install_trace()

    class _ModuleProxy:
        _module = None

        def __init__(self, name):
            self.__dict__["_module_name"] = name

        def __getattr__(self, name):
            try:
                return getattr(self._module, name)
            except AttributeError:
                if self._module is not None:
                    raise
                import_name = "pyglet.%s" % self._module_name
                __import__(import_name)
                module = sys.modules[import_name]
                object.__setattr__(self, "_module", module)
                globals()[self._module_name] = module
                return getattr(module, name)

        def __setattr__(self, name, value):
            try:
                setattr(self._module, name, value)
            except AttributeError:
                if self._module is not None:
                    raise
                import_name = "pyglet.%s" % self._module_name
                __import__(import_name)
                module = sys.modules[import_name]
                object.__setattr__(self, "_module", module)
                globals()[self._module_name] = module
                setattr(module, name, value)


    if TYPE_CHECKING:
        from . import app
        from . import canvas
        from . import clock
        from . import com
        from . import event
        from . import font
        from . import gl
        from . import graphics
        from . import gui
        from . import input
        from . import image
        from . import lib
        from . import math
        from . import media
        from . import model
        from . import resource
        from . import sprite
        from . import shapes
        from . import text
        from . import window
    else:
        app = _ModuleProxy("app")
    canvas = _ModuleProxy("canvas")
    clock = _ModuleProxy("clock")
    com = _ModuleProxy("com")
    event = _ModuleProxy("event")
    font = _ModuleProxy("font")
    gl = _ModuleProxy("gl")
    graphics = _ModuleProxy("graphics")
    gui = _ModuleProxy("gui")
    image = _ModuleProxy("image")
    input = _ModuleProxy("input")
    lib = _ModuleProxy("lib")
    math = _ModuleProxy("math")
    media = _ModuleProxy("media")
    model = _ModuleProxy("model")
    resource = _ModuleProxy("resource")
    sprite = _ModuleProxy("sprite")
    shapes = _ModuleProxy("shapes")
    text = _ModuleProxy("text")
    window = _ModuleProxy("window")
