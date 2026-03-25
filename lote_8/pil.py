# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\image\codecs\pil.py
import os.path
from pyglet.image import *
from pyglet.image.codecs import *
try:
    import Image
except ImportError:
    from PIL import Image, ImageSequence

class PILImageDecoder(ImageDecoder):

    def get_file_extensions(self):
        return [
         '.bmp', '.cur', '.gif', '.ico', '.jpg', '.jpeg', 
         '.pcx', '.png', 
         '.tga', '.tif', '.tiff', 
         '.xbm', '.xpm']

    def decode(self, file, filename):
        try:
            image = Image.open(file)
        except Exception as e:
            raise ImageDecodeException("PIL cannot read %r: %s" % (filename or file, e))

        try:
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
        except Exception as e:
            raise ImageDecodeException("PIL failed to transpose %r: %s" % (filename or file, e))

        if image.mode in ('1', 'P'):
            image = image.convert()
        if image.mode not in ('L', 'LA', 'RGB', 'RGBA'):
            raise ImageDecodeException('Unsupported mode "%s"' % image.mode)
        width, height = image.size
        try:
            image_data_fn = getattr(image, "tobytes")
        except AttributeError:
            image_data_fn = getattr(image, "tostring")

        return ImageData(width, height, image.mode, image_data_fn())


class PILImageEncoder(ImageEncoder):

    def get_file_extensions(self):
        return [
         '.bmp', '.eps', '.gif', '.jpg', '.jpeg', 
         '.pcx', 
         '.png', '.ppm', '.tiff', '.xbm']

    def encode(self, image, file, filename):
        pil_format = filename and os.path.splitext(filename)[1][1:] or "png"
        if pil_format.lower() == "jpg":
            pil_format = "JPEG"
        image = image.get_image_data()
        fmt = image.format
        if fmt != "RGB":
            fmt = "RGBA"
        pitch = -(image.width * len(fmt))
        try:
            image_from_fn = getattr(Image, "frombytes")
        except AttributeError:
            image_from_fn = getattr(Image, "fromstring")

        pil_image = image_from_fn(fmt, (image.width, image.height), image.get_data(fmt, pitch))
        try:
            pil_image.save(file, pil_format)
        except Exception as e:
            raise ImageEncodeException(e)


def get_decoders():
    return [
     PILImageDecoder()]


def get_encoders():
    return [
     PILImageEncoder()]
