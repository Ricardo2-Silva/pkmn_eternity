# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\media\codecs\__init__.py
from pyglet.util import Codecs, Decoder, Encoder
from .base import *
import pyglet
_debug = pyglet.options["debug_media"]
_codecs = Codecs()
add_decoders = _codecs.add_decoders
get_decoders = _codecs.get_decoders
add_encoders = _codecs.add_encoders
get_encoders = _codecs.get_encoders

class MediaDecoder(Decoder):

    def decode(self, file, filename, streaming):
        """Read the given file object and return an instance of `Source`
        or `StreamingSource`. 
        Throws MediaDecodeException if there is an error.  `filename`
        can be a file type hint.
        """
        raise NotImplementedError()


class MediaEncoder(Encoder):

    def encode(self, source, file, filename):
        """Encode the given source to the given file.  `filename`
        provides a hint to the file format desired.  options are
        encoder-specific, and unknown options should be ignored or
        issue warnings.
        """
        raise NotImplementedError()


def add_default_media_codecs():
    try:
        from . import wave
        add_decoders(wave)
        add_encoders(wave)
    except ImportError:
        pass

    if pyglet.compat_platform.startswith("linux"):
        try:
            from . import gstreamer
            add_decoders(gstreamer)
        except ImportError:
            pass

    try:
        if pyglet.compat_platform in ('win32', 'cygwin'):
            from pyglet.libs.win32.constants import WINDOWS_VISTA_OR_GREATER
            if WINDOWS_VISTA_OR_GREATER:
                from . import wmf
                add_decoders(wmf)
    except ImportError:
        pass

    try:
        if have_ffmpeg():
            from . import ffmpeg
            add_decoders(ffmpeg)
    except ImportError:
        pass


def have_ffmpeg():
    """Check if FFmpeg library is available.

    Returns:
        bool: True if FFmpeg is found.

    .. versionadded:: 1.4
    """
    try:
        from . import ffmpeg_lib
        if _debug:
            print("FFmpeg available, using to load media files.")
        return True
    except (ImportError, FileNotFoundError):
        if _debug:
            print("FFmpeg not available.")
        return False
