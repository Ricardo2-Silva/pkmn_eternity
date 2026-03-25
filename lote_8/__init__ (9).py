# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\image\codecs\__init__.py
"""Collection of image encoders and decoders.

Modules must subclass ImageDecoder and ImageEncoder for each method of
decoding/encoding they support.

Modules must also implement the two functions::

    def get_decoders():
        # Return a list of ImageDecoder instances or []
        return []

    def get_encoders():
        # Return a list of ImageEncoder instances or []
        return []

"""
import os.path
from pyglet.util import Codecs, Decoder, Encoder, DecodeException, EncodeException
from pyglet import compat_platform

class _ImageCodecs(Codecs):
    __doc__ = "Subclass of Codecs that adds support for animation methods."

    def __init__(self):
        self._decoder_animation_extensions = {}
        super().__init__()

    def add_decoders(self, module):
        """Override the default method to also add animation decoders.
        """
        super().add_decoders(module)
        for decoder in module.get_decoders():
            for extension in decoder.get_animation_file_extensions():
                if extension not in self._decoder_animation_extensions:
                    self._decoder_animation_extensions[extension] = []
                self._decoder_animation_extensions[extension].append(decoder)

    def get_animation_decoders(self, filename=None):
        """Get an ordered list of all animation decoders. If a `filename` is
        provided, decoders supporting that extension will be ordered first
        in the list.
        """
        decoders = []
        if filename:
            extension = os.path.splitext(filename)[1].lower()
            decoders += self._decoder_animation_extensions.get(extension, [])
        decoders += [e for e in self._decoders if e not in decoders]
        return decoders


_codecs = _ImageCodecs()
add_decoders = _codecs.add_decoders
get_decoders = _codecs.get_decoders
add_encoders = _codecs.add_encoders
get_encoders = _codecs.get_encoders
get_animation_decoders = _codecs.get_animation_decoders

class ImageDecodeException(DecodeException):
    return


class ImageEncodeException(EncodeException):
    return


class ImageDecoder(Decoder):

    def get_animation_file_extensions(self):
        """Return a list of accepted file extensions, e.g. ['.gif', '.flc']
        Lower-case only.
        """
        return []

    def decode(self, file, filename):
        """Decode the given file object and return an instance of `Image`.
        Throws ImageDecodeException if there is an error.  filename
        can be a file type hint.
        """
        raise NotImplementedError()

    def decode_animation(self, file, filename):
        """Decode the given file object and return an instance of :py:class:`~pyglet.image.Animation`.
        Throws ImageDecodeException if there is an error.  filename
        can be a file type hint.
        """
        raise ImageDecodeException("This decoder cannot decode animations.")

    def __repr__(self):
        return "{0}{1}".format(self.__class__.__name__, self.get_animation_file_extensions() + self.get_file_extensions())


class ImageEncoder(Encoder):

    def encode(self, image, file, filename):
        """Encode the given image to the given file.  filename
        provides a hint to the file format desired.
        """
        raise NotImplementedError()

    def __repr__(self):
        return "{0}{1}".format(self.__class__.__name__, self.get_file_extensions())


def add_default_image_codecs():
    try:
        from pyglet.image.codecs import dds
        add_encoders(dds)
        add_decoders(dds)
    except ImportError:
        pass

    if compat_platform == "darwin":
        try:
            from pyglet.image.codecs import quartz
            add_encoders(quartz)
            add_decoders(quartz)
        except ImportError:
            pass

    if compat_platform in ('win32', 'cygwin'):
        from pyglet.libs.win32.constants import WINDOWS_7_OR_GREATER
        if WINDOWS_7_OR_GREATER:
            try:
                from pyglet.image.codecs import wic
                add_encoders(wic)
                print("ADDING 1?")
                add_decoders(wic)
            except ImportError:
                pass

    if compat_platform in ('win32', 'cygwin'):
        try:
            from pyglet.image.codecs import gdiplus
            add_encoders(gdiplus)
            add_decoders(gdiplus)
        except ImportError:
            pass

    if compat_platform.startswith("linux"):
        try:
            from pyglet.image.codecs import gdkpixbuf2
            add_encoders(gdkpixbuf2)
            add_decoders(gdkpixbuf2)
        except ImportError:
            pass

    try:
        from pyglet.image.codecs import pil
        add_encoders(pil)
        add_decoders(pil)
    except ImportError:
        pass

    try:
        from pyglet.image.codecs import png
        add_encoders(png)
        add_decoders(png)
    except ImportError:
        pass

    try:
        from pyglet.image.codecs import bmp
        add_encoders(bmp)
        add_decoders(bmp)
    except ImportError:
        pass
