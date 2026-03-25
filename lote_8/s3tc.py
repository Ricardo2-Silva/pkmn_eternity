# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\image\codecs\s3tc.py
"""Software decoder for S3TC compressed texture (i.e., DDS).

http://oss.sgi.com/projects/ogl-sample/registry/EXT/texture_compression_s3tc.txt
"""
import ctypes, re
from pyglet.gl import *
from pyglet.gl import gl_info
from pyglet.image import AbstractImage, Texture
split_8byte = re.compile("........", flags=(re.DOTALL))
split_16byte = re.compile("................", flags=(re.DOTALL))

class PackedImageData(AbstractImage):
    _current_texture = None

    def __init__(self, width, height, format, packed_format, data):
        super(PackedImageData, self).__init__(width, height)
        self.format = format
        self.packed_format = packed_format
        self.data = data

    def unpack(self):
        if self.packed_format == GL_UNSIGNED_SHORT_5_6_5:
            i = 0
            out = ctypes.c_ubyte * (self.width * self.height * 3)()
            for c in self.data:
                out[i + 2] = (c & 31) << 3
                out[i + 1] = (c & 2016) >> 3
                out[i] = (c & 63488) >> 8
                i += 3

            self.data = out
            self.packed_format = GL_UNSIGNED_BYTE

    def _get_texture(self):
        if self._current_texture:
            return self._current_texture
        else:
            texture = Texture.create_for_size(GL_TEXTURE_2D, self.width, self.height)
            glBindTexture(texture.target, texture.id)
            glTexParameteri(texture.target, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            if not gl_info.have_version(1, 2) or True:
                self.unpack()
            glTexImage2D(texture.target, texture.level, self.format, self.width, self.height, 0, self.format, self.packed_format, self.data)
            self._current_texture = texture
            return texture

    texture = property(_get_texture)

    def get_texture(self, rectangle=False, force_rectangle=False):
        """The parameters 'rectangle' and 'force_rectangle' are ignored.
           See the documentation of the method 'AbstractImage.get_texture' for
           a more detailed documentation of the method. """
        return self._get_texture()


def decode_dxt1_rgbParse error at or near `POP_JUMP_IF_TRUE' instruction at offset 480_482


def decode_dxt1_rgbaParse error at or near `POP_JUMP_IF_TRUE' instruction at offset 520_522


def decode_dxt3Parse error at or near `POP_JUMP_IF_TRUE' instruction at offset 628_630


def decode_dxt5Parse error at or near `POP_JUMP_IF_TRUE' instruction at offset 620_622