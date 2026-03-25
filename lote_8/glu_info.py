# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\gl\glu_info.py
"""Information about version and extensions of current GLU implementation.

Usage::

    from pyglet.gl import glu_info

    if glu_info.have_extension('GLU_EXT_nurbs_tessellator'):
        # ...

If multiple contexts are in use you can use a separate GLUInfo object for each
context.  Call `set_active_context` after switching to the desired context for
each GLUInfo::

    from pyglet.gl.glu_info import GLUInfo

    info = GLUInfo()
    info.set_active_context()
    if info.have_version(1, 3):
        # ...

Note that GLUInfo only returns meaningful information if a context has been
created.
"""
from ctypes import *
import warnings
from pyglet.gl.glu import *
from pyglet.util import asstr

class GLUInfo:
    __doc__ = "Information interface for the GLU library. \n\n    A default instance is created automatically when the first OpenGL context\n    is created.  You can use the module functions as a convenience for \n    this default instance's methods.\n\n    If you are using more than one context, you must call `set_active_context`\n    when the context is active for this `GLUInfo` instance.\n    "
    have_context = False
    version = "0.0.0"
    extensions = []
    _have_info = False

    def set_active_context(self):
        """Store information for the currently active context.

        This method is called automatically for the default context.
        """
        self.have_context = True
        if not self._have_info:
            self.extensions = asstr(cast(gluGetString(GLU_EXTENSIONS), c_char_p).value).split()
            self.version = asstr(cast(gluGetString(GLU_VERSION), c_char_p).value)
            self._have_info = True

    def have_version(self, major, minor=0, release=0):
        """Determine if a version of GLU is supported.

        :Parameters:
            `major` : int
                The major revision number (typically 1).
            `minor` : int
                The minor revision number.
            `release` : int
                The release number.  

        :rtype: bool
        :return: True if the requested or a later version is supported.
        """
        if not self.have_context:
            warnings.warn("No GL context created yet.")
        ver = "%s.0.0" % self.version.split(" ", 1)[0]
        imajor, iminor, irelease = [int(v) for v in ver.split(".", 3)[:3]]
        return imajor > major or imajor == major and iminor > minor or imajor == major and iminor == minor and irelease >= release

    def get_version(self):
        """Get the current GLU version.

        :return: the GLU version
        :rtype: str
        """
        if not self.have_context:
            warnings.warn("No GL context created yet.")
        return self.version

    def have_extension(self, extension):
        """Determine if a GLU extension is available.

        :Parameters:
            `extension` : str
                The name of the extension to test for, including its
                ``GLU_`` prefix.

        :return: True if the extension is provided by the implementation.
        :rtype: bool
        """
        if not self.have_context:
            warnings.warn("No GL context created yet.")
        return extension in self.extensions

    def get_extensions(self):
        """Get a list of available GLU extensions.

        :return: a list of the available extensions.
        :rtype: list of str
        """
        if not self.have_context:
            warnings.warn("No GL context created yet.")
        return self.extensions


_glu_info = GLUInfo()
set_active_context = _glu_info.set_active_context
have_version = _glu_info.have_version
get_version = _glu_info.get_version
have_extension = _glu_info.have_extension
get_extensions = _glu_info.get_extensions
