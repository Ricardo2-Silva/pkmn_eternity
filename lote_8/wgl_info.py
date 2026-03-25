# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\gl\wgl_info.py
"""Cached information about version and extensions of current WGL
implementation.
"""
from ctypes import *
import warnings
from pyglet.gl.lib import MissingFunctionException
from pyglet.gl.gl import *
from pyglet.gl import gl_info
from pyglet.gl.wgl import *
from pyglet.gl.wglext_arb import *
from pyglet.util import asstr

class WGLInfoException(Exception):
    return


class WGLInfo:

    def get_extensions(self):
        if not gl_info.have_context():
            warnings.warn("Can't query WGL until a context is created.")
            return []
        try:
            return asstr(wglGetExtensionsStringEXT()).split()
        except MissingFunctionException:
            return asstr(cast(glGetString(GL_EXTENSIONS), c_char_p).value).split()

    def have_extension(self, extension):
        return extension in self.get_extensions()


_wgl_info = WGLInfo()
get_extensions = _wgl_info.get_extensions
have_extension = _wgl_info.have_extension
