# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\gl\gl_info.py
"""Information about version and extensions of current GL implementation.

Usage::
    
    from pyglet.gl import gl_info

    if gl_info.have_extension('GL_NV_register_combiners'):
        # ...

If you are using more than one context, you can set up a separate GLInfo
object for each context.  Call `set_active_context` after switching to the
context::

    from pyglet.gl.gl_info import GLInfo

    info = GLInfo()
    info.set_active_context()

    if info.have_version(2, 1):
        # ...

"""
from ctypes import c_char_p, cast
import warnings
from pyglet.gl.gl import GL_EXTENSIONS, GL_RENDERER, GL_VENDOR, GL_VERSION, GLint, glGetIntegerv, glGetString
from pyglet.util import asstr

class GLInfo:
    __doc__ = "Information interface for a single GL context.\n\n    A default instance is created automatically when the first OpenGL context\n    is created.  You can use the module functions as a convenience for\n    this default instance's methods.\n\n    If you are using more than one context, you must call `set_active_context`\n    when the context is active for this `GLInfo` instance.\n    "
    have_context = False
    version = "0.0.0"
    vendor = ""
    renderer = ""
    extensions = set()
    _have_info = False

    def set_active_context(self):
        """Store information for the currently active context.

        This method is called automatically for the default context.
        """
        self.have_context = True
        if not self._have_info:
            self.vendor = asstr(cast(glGetString(GL_VENDOR), c_char_p).value)
            self.renderer = asstr(cast(glGetString(GL_RENDERER), c_char_p).value)
            self.version = asstr(cast(glGetString(GL_VERSION), c_char_p).value)
            if self.have_version(3):
                from pyglet.gl.glext_arb import glGetStringi, GL_NUM_EXTENSIONS
                num_extensions = GLint()
                glGetIntegerv(GL_NUM_EXTENSIONS, num_extensions)
                self.extensions = (asstr(cast(glGetStringi(GL_EXTENSIONS, i), c_char_p).value) for i in range(num_extensions.value))
            else:
                self.extensions = asstr(cast(glGetString(GL_EXTENSIONS), c_char_p).value).split()
            if self.extensions:
                self.extensions = set(self.extensions)
            self._have_info = True

    def remove_active_context(self):
        self.have_context = False
        self._have_info = False

    def have_extension(self, extension):
        """Determine if an OpenGL extension is available.

        :Parameters:
            `extension` : str
                The name of the extension to test for, including its
                ``GL_`` prefix.

        :return: True if the extension is provided by the driver.
        :rtype: bool
        """
        if not self.have_context:
            warnings.warn("No GL context created yet.")
        return extension in self.extensions

    def get_extensions(self):
        """Get a list of available OpenGL extensions.

        :return: a list of the available extensions.
        :rtype: list of str
        """
        if not self.have_context:
            warnings.warn("No GL context created yet.")
        return self.extensions

    def get_version(self):
        """Get the current OpenGL version.

        :return: the OpenGL version
        :rtype: str
        """
        if not self.have_context:
            warnings.warn("No GL context created yet.")
        return self.version

    def have_version(self, major, minor=0, release=0):
        """Determine if a version of OpenGL is supported.

        :Parameters:
            `major` : int
                The major revision number (typically 1 or 2).
            `minor` : int
                The minor revision number.
            `release` : int
                The release number.
                :deprecated: No longer used

        :rtype: bool
        :return: True if the requested or a later version is supported.
        """
        if not self.have_context:
            warnings.warn("No GL context created yet.")
        if not self.version or "None" in self.version:
            return False
        else:
            ver = "%s.0.0" % self.version.strip().split(" ", 1)[0]
            imajor, iminor, irelease = [int(v) for v in ver.split(".", 3)[:3]]
            return imajor > major or imajor == major and iminor >= minor or imajor == major and iminor == minor

    def get_renderer(self):
        """Determine the renderer string of the OpenGL context.

        :rtype: str
        """
        if not self.have_context:
            warnings.warn("No GL context created yet.")
        return self.renderer

    def get_vendor(self):
        """Determine the vendor string of the OpenGL context.

        :rtype: str
        """
        if not self.have_context:
            warnings.warn("No GL context created yet.")
        return self.vendor


_gl_info = GLInfo()
set_active_context = _gl_info.set_active_context
remove_active_context = _gl_info.remove_active_context
have_extension = _gl_info.have_extension
get_extensions = _gl_info.get_extensions
get_version = _gl_info.get_version
have_version = _gl_info.have_version
get_renderer = _gl_info.get_renderer
get_vendor = _gl_info.get_vendor

def have_context():
    """Determine if a default OpenGL context has been set yet.

    :rtype: bool
    """
    return _gl_info.have_context
