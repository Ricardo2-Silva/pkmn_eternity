# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\font\__init__.py
"""Load fonts.

pyglet will automatically load any system-installed fonts.  You can add additional fonts
(for example, from your program resources) using :meth:`add_file` or
:meth:`add_directory`. These fonts are then available in the same way as system-installed fonts::

    from pyglet import font
    font.add_file('action_man.ttf')
    action_man = font.load('Action Man', 16)
    # or
    from pyglet import resource
    resource.add_font('action_man.ttf')
    action_man = font.load('Action Man')

See the :mod:`pyglet.font.base` module for documentation on the base classes used
by this package.
"""
import os, sys, weakref, pyglet
from pyglet import gl
if not getattr(sys, "is_pyglet_doc_run", False):
    if pyglet.compat_platform == "darwin":
        from pyglet.font.quartz import QuartzFont
        _font_class = QuartzFont
    elif pyglet.compat_platform in ('win32', 'cygwin'):
        from pyglet.libs.win32.constants import WINDOWS_7_OR_GREATER
        if WINDOWS_7_OR_GREATER:
            if pyglet.options["advanced_font_features"] is True:
                from pyglet.font.directwrite import Win32DirectWriteFont
                _font_class = Win32DirectWriteFont
            else:
                from pyglet.font.win32 import GDIPlusFont
                _font_class = GDIPlusFont
        else:
            from pyglet.font.win32 import GDIPlusFont
            _font_class = GDIPlusFont
    else:
        from pyglet.font.freetype import FreeTypeFont
        _font_class = FreeTypeFont

def have_font(name):
    """Check if specified system font name is available."""
    return _font_class.have_font(name)


def load(name=None, size=None, bold=False, italic=False, stretch=False, dpi=None):
    """Load a font for rendering.

    :Parameters:
        `name` : str, or list of str
            Font family, for example, "Times New Roman".  If a list of names
            is provided, the first one matching a known font is used.  If no
            font can be matched to the name(s), a default font is used.  In
            pyglet 1.1, the name may be omitted.
        `size` : float
            Size of the font, in points.  The returned font may be an exact
            match or the closest available.  In pyglet 1.1, the size may be
            omitted, and defaults to 12pt.
        `bold` : bool
            If True, a bold variant is returned, if one exists for the given
            family and size.
        `italic` : bool
            If True, an italic variant is returned, if one exists for the given
            family and size.
        `dpi` : float
            The assumed resolution of the display device, for the purposes of
            determining the pixel size of the font.  Defaults to 96.

    :rtype: `Font`
    """
    if size is None:
        size = 12
    else:
        if dpi is None:
            dpi = 96
        if type(name) in (tuple, list):
            for n in name:
                if _font_class.have_font(n):
                    name = n
                    break
            else:
                name = None

        shared_object_space = gl.current_context.object_space
        shared_object_space.pyglet_font_font_cache = hasattr(shared_object_space, "pyglet_font_font_cache") or weakref.WeakValueDictionary()
        shared_object_space.pyglet_font_font_hold = []
    font_cache = shared_object_space.pyglet_font_font_cache
    font_hold = shared_object_space.pyglet_font_font_hold
    descriptor = (
     name, size, bold, italic, stretch, dpi)
    if descriptor in font_cache:
        return font_cache[descriptor]
    else:
        font = _font_class(name, size, bold=bold, italic=italic, stretch=stretch, dpi=dpi)
        font.size = size
        font.bold = bold
        font.italic = italic
        font.stretch = stretch
        font.dpi = dpi
        font_cache[descriptor] = font
        del font_hold[3:]
        font_hold.insert(0, font)
        return font


def add_file(font):
    """Add a font to pyglet's search path.

    In order to load a font that is not installed on the system, you must
    call this method to tell pyglet that it exists.  You can supply
    either a filename or any file-like object.

    The font format is platform-dependent, but is typically a TrueType font
    file containing a single font face. Note that to use a font added with this method,
    you should pass the face name (not the file name) to :meth::py:func:`pyglet.font.load` or any
    other place where you normally specify a font.

    :Parameters:
        `font` : str or file-like object
            Filename or file-like object to load fonts from.

    """
    if isinstance(font, str):
        font = open(font, "rb")
    if hasattr(font, "read"):
        font = font.read()
    _font_class.add_font_data(font)


def add_directory(directory):
    """Add a directory of fonts to pyglet's search path.

    This function simply calls :meth:`pyglet.font.add_file` for each file with a ``.ttf``
    extension in the given directory. Subdirectories are not searched.

    :Parameters:
        `dir` : str
            Directory that contains font files.

    """
    for file in os.listdir(directory):
        if file[-4:].lower() == ".ttf":
            add_file(os.path.join(directory, file))


__all__ = ('add_file', 'add_directory', 'load', 'have_font')
