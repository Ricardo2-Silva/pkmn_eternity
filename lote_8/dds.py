# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\image\codecs\dds.py
"""DDS texture loader.

Reference: http://msdn2.microsoft.com/en-us/library/bb172993.aspx
"""
import struct, itertools
from pyglet.gl import *
from pyglet.image import CompressedImageData
from pyglet.image import codecs
from pyglet.image.codecs import s3tc, ImageDecodeException
DDSD_CAPS = 1
DDSD_HEIGHT = 2
DDSD_WIDTH = 4
DDSD_PITCH = 8
DDSD_PIXELFORMAT = 4096
DDSD_MIPMAPCOUNT = 131072
DDSD_LINEARSIZE = 524288
DDSD_DEPTH = 8388608
DDPF_ALPHAPIXELS = 1
DDPF_FOURCC = 4
DDPF_RGB = 64
DDSCAPS_COMPLEX = 8
DDSCAPS_TEXTURE = 4096
DDSCAPS_MIPMAP = 4194304
DDSCAPS2_CUBEMAP = 512
DDSCAPS2_CUBEMAP_POSITIVEX = 1024
DDSCAPS2_CUBEMAP_NEGATIVEX = 2048
DDSCAPS2_CUBEMAP_POSITIVEY = 4096
DDSCAPS2_CUBEMAP_NEGATIVEY = 8192
DDSCAPS2_CUBEMAP_POSITIVEZ = 16384
DDSCAPS2_CUBEMAP_NEGATIVEZ = 32768
DDSCAPS2_VOLUME = 2097152

class _FileStruct:
    _fields = []

    def __init__(self, data):
        if len(data) < self.get_size():
            raise ImageDecodeException("Not a DDS file")
        items = struct.unpack(self.get_format(), data)
        for field, value in itertools.zip_longest((self._fields), items, fillvalue=None):
            setattr(self, field[0], value)

    def __repr__(self):
        name = self.__class__.__name__
        return "%s(%s)" % (name,
         (", \n%s" % (" " * (len(name) + 1))).join(["%s = %s" % (field[0], repr(getattr(self, field[0]))) for field in self._fields]))

    @classmethod
    def get_format(cls):
        return "<" + "".join([f[1] for f in cls._fields])

    @classmethod
    def get_size(cls):
        return struct.calcsize(cls.get_format())


class DDSURFACEDESC2(_FileStruct):
    _fields = [
     ('dwMagic', '4s'), 
     ('dwSize', 'I'), 
     ('dwFlags', 'I'), 
     ('dwHeight', 'I'), 
     ('dwWidth', 'I'), 
     ('dwPitchOrLinearSize', 'I'), 
     ('dwDepth', 'I'), 
     ('dwMipMapCount', 'I'), 
     ('dwReserved1', '44s'), 
     ('ddpfPixelFormat', '32s'), 
     ('dwCaps1', 'I'), 
     ('dwCaps2', 'I'), 
     ('dwCapsReserved', '8s'), 
     ('dwReserved2', 'I')]

    def __init__(self, data):
        super(DDSURFACEDESC2, self).__init__(data)
        self.ddpfPixelFormat = DDPIXELFORMAT(self.ddpfPixelFormat)


class DDPIXELFORMAT(_FileStruct):
    _fields = [
     ('dwSize', 'I'), 
     ('dwFlags', 'I'), 
     ('dwFourCC', '4s'), 
     ('dwRGBBitCount', 'I'), 
     ('dwRBitMask', 'I'), 
     ('dwGBitMask', 'I'), 
     ('dwBBitMask', 'I'), 
     ('dwRGBAlphaBitMask', 'I')]


_compression_formats = {(b'DXT1', False): (GL_COMPRESSED_RGB_S3TC_DXT1_EXT, s3tc.decode_dxt1_rgb), 
 (b'DXT1', True): (GL_COMPRESSED_RGBA_S3TC_DXT1_EXT, s3tc.decode_dxt1_rgba), 
 (b'DXT3', False): (GL_COMPRESSED_RGBA_S3TC_DXT3_EXT, s3tc.decode_dxt3), 
 (b'DXT3', True): (GL_COMPRESSED_RGBA_S3TC_DXT3_EXT, s3tc.decode_dxt3), 
 (b'DXT5', False): (GL_COMPRESSED_RGBA_S3TC_DXT5_EXT, s3tc.decode_dxt5), 
 (b'DXT5', True): (GL_COMPRESSED_RGBA_S3TC_DXT5_EXT, s3tc.decode_dxt5)}

class DDSImageDecoder(codecs.ImageDecoder):

    def get_file_extensions(self):
        return [
         ".dds"]

    def decode(self, file, filename):
        header = file.read(DDSURFACEDESC2.get_size())
        desc = DDSURFACEDESC2(header)
        if desc.dwMagic != b'DDS ' or desc.dwSize != 124:
            raise ImageDecodeException("Invalid DDS file (incorrect header).")
        width = desc.dwWidth
        height = desc.dwHeight
        mipmaps = 1
        if desc.dwFlags & DDSD_DEPTH:
            raise ImageDecodeException("Volume DDS files unsupported")
        if desc.dwFlags & DDSD_MIPMAPCOUNT:
            mipmaps = desc.dwMipMapCount
        if desc.ddpfPixelFormat.dwSize != 32:
            raise ImageDecodeException("Invalid DDS file (incorrect pixel format).")
        if desc.dwCaps2 & DDSCAPS2_CUBEMAP:
            raise ImageDecodeException("Cubemap DDS files unsupported")
        if not desc.ddpfPixelFormat.dwFlags & DDPF_FOURCC:
            raise ImageDecodeException("Uncompressed DDS textures not supported.")
        else:
            has_alpha = desc.ddpfPixelFormat.dwRGBAlphaBitMask != 0
            selector = (
             desc.ddpfPixelFormat.dwFourCC, has_alpha)
            if selector not in _compression_formats:
                raise ImageDecodeException("Unsupported texture compression %s" % desc.ddpfPixelFormat.dwFourCC)
            dformat, decoder = _compression_formats[selector]
            if dformat == GL_COMPRESSED_RGB_S3TC_DXT1_EXT:
                block_size = 8
            else:
                block_size = 16
        datas = []
        w, h = width, height
        for i in range(mipmaps):
            if not w:
                if not h:
                    break
            else:
                if not w:
                    w = 1
                h = h or 1
            size = (w + 3) // 4 * ((h + 3) // 4) * block_size
            data = file.read(size)
            datas.append(data)
            w >>= 1
            h >>= 1

        image = CompressedImageData(width, height, dformat, datas[0], "GL_EXT_texture_compression_s3tc", decoder)
        level = 0
        for data in datas[1:]:
            level += 1
            image.set_mipmap_data(level, data)

        return image


def get_decoders():
    return [
     DDSImageDecoder()]


def get_encoders():
    return []
