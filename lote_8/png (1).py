# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\image\codecs\png.py
"""Encoder and decoder for PNG files, using PyPNG (png.py).
"""
import array, itertools
from pyglet.image import ImageData, ImageDecodeException
from pyglet.image.codecs import ImageDecoder, ImageEncoder
import pyglet.extlibs.png as pypng

class PNGImageDecoder(ImageDecoder):

    def get_file_extensions(self):
        return [
         ".png"]

    def decode(self, file, filename):
        try:
            reader = pypng.Reader(file=file)
            width, height, pixels, metadata = reader.asDirect()
        except Exception as e:
            raise ImageDecodeException("PyPNG cannot read %r: %s" % (filename or file, e))

        if metadata["greyscale"]:
            if metadata["alpha"]:
                fmt = "LA"
            else:
                fmt = "L"
        elif metadata["alpha"]:
            fmt = "RGBA"
        else:
            fmt = "RGB"
        pitch = len(fmt) * width
        pixels = array.array("BH"[metadata["bitdepth"] > 8], (itertools.chain)(*pixels))
        return ImageData(width, height, fmt, pixels.tobytes(), -pitch)


class PNGImageEncoder(ImageEncoder):

    def get_file_extensions(self):
        return [
         ".png"]

    def encode(self, image, file, filename):
        image = image.get_image_data()
        has_alpha = "A" in image.format
        greyscale = len(image.format) < 3
        if has_alpha:
            if greyscale:
                image.format = "LA"
            else:
                image.format = "RGBA"
        elif greyscale:
            image.format = "L"
        else:
            image.format = "RGB"
        image.pitch = -(image.width * len(image.format))
        writer = pypng.Writer((image.width), (image.height), greyscale=greyscale, alpha=has_alpha)
        data = array.array("B")
        data.frombytes(image.get_data(image.format, image.pitch))
        writer.write_array(file, data)


def get_decoders():
    return [
     PNGImageDecoder()]


def get_encoders():
    return [
     PNGImageEncoder()]
