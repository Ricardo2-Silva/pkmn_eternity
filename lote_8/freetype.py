# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\font\freetype.py
import ctypes, warnings
from collections import namedtuple
from pyglet.util import asbytes, asstr
from pyglet.font import base
from pyglet import image
from pyglet.font.fontconfig import get_fontconfig
from pyglet.font.freetype_lib import *

class FreeTypeGlyphRenderer(base.GlyphRenderer):

    def __init__(self, font):
        super().__init__(font)
        self.font = font
        self._glyph_slot = None
        self._bitmap = None
        self._width = None
        self._height = None
        self._mode = None
        self._pitch = None
        self._baseline = None
        self._lsb = None
        self._advance_x = None
        self._data = None

    def _get_glyph(self, character):
        if not self.font:
            raise AssertionError
        elif not len(character) == 1:
            raise AssertionError
        self._glyph_slot = self.font.get_glyph_slot(character)
        self._bitmap = self._glyph_slot.bitmap

    def _get_glyph_metrics(self):
        self._width = self._glyph_slot.bitmap.width
        self._height = self._glyph_slot.bitmap.rows
        self._mode = self._glyph_slot.bitmap.pixel_mode
        self._pitch = self._glyph_slot.bitmap.pitch
        self._baseline = self._height - self._glyph_slot.bitmap_top
        self._lsb = self._glyph_slot.bitmap_left
        self._advance_x = int(f26p6_to_float(self._glyph_slot.advance.x))

    def _get_bitmap_data(self):
        if self._mode == FT_PIXEL_MODE_MONO:
            self._convert_mono_to_gray_bitmap()
        elif self._mode == FT_PIXEL_MODE_GRAY:
            assert self._glyph_slot.bitmap.num_grays == 256
            self._data = self._glyph_slot.bitmap.buffer
        else:
            raise base.FontException("Unsupported render mode for this glyph")

    def _convert_mono_to_gray_bitmap(self):
        bitmap_data = cast(self._bitmap.buffer, POINTER(c_ubyte * (self._pitch * self._height))).contents
        data = c_ubyte * (self._pitch * 8 * self._height)()
        data_i = 0
        for byte in bitmap_data:
            data[data_i + 0] = byte & 128 and 255 or 0
            data[data_i + 1] = byte & 64 and 255 or 0
            data[data_i + 2] = byte & 32 and 255 or 0
            data[data_i + 3] = byte & 16 and 255 or 0
            data[data_i + 4] = byte & 8 and 255 or 0
            data[data_i + 5] = byte & 4 and 255 or 0
            data[data_i + 6] = byte & 2 and 255 or 0
            data[data_i + 7] = byte & 1 and 255 or 0
            data_i += 8

        self._data = data
        self._pitch <<= 3

    def _create_glyph(self):
        img = image.ImageData(self._width, self._height, "A", self._data, abs(self._pitch))
        glyph = self.font.create_glyph(img)
        glyph.set_bearings(self._baseline, self._lsb, self._advance_x)
        if self._pitch > 0:
            t = list(glyph.tex_coords)
            glyph.tex_coords = t[9:12] + t[6:9] + t[3:6] + t[:3]
        return glyph

    def render(self, text):
        self._get_glyph(text[0])
        self._get_glyph_metrics()
        self._get_bitmap_data()
        return self._create_glyph()


FreeTypeFontMetrics = namedtuple("FreeTypeFontMetrics", ["ascent", "descent"])

class MemoryFaceStore:

    def __init__(self):
        self._dict = {}

    def add(self, face):
        self._dict[(face.name.lower(), face.bold, face.italic)] = face

    def contains(self, name):
        lname = name and name.lower() or ""
        return len([name for name, _, _ in self._dict.keys() if name == lname]) > 0

    def get(self, name, bold, italic):
        lname = name and name.lower() or ""
        return self._dict.get((lname, bold, italic), None)


class FreeTypeFont(base.Font):
    glyph_renderer_class = FreeTypeGlyphRenderer
    _memory_faces = MemoryFaceStore()

    def __init__(self, name, size, bold=False, italic=False, stretch=False, dpi=None):
        if stretch:
            warnings.warn("The current font render does not support stretching.")
        super().__init__()
        self._name = name
        self.size = size
        self.bold = bold
        self.italic = italic
        self.dpi = dpi or 96
        self._load_font_face()
        self.metrics = self.face.get_font_metrics(self.size, self.dpi)

    @property
    def name(self):
        return self.face.family_name

    @property
    def ascent(self):
        return self.metrics.ascent

    @property
    def descent(self):
        return self.metrics.descent

    def get_glyph_slot(self, character):
        glyph_index = self.face.get_character_index(character)
        self.face.set_char_size(self.size, self.dpi)
        return self.face.get_glyph_slot(glyph_index)

    def _load_font_face(self):
        self.face = self._memory_faces.get(self._name, self.bold, self.italic)
        if self.face is None:
            self._load_font_face_from_system()

    def _load_font_face_from_system(self):
        match = get_fontconfig().find_font(self._name, self.size, self.bold, self.italic)
        if not match:
            raise base.FontException('Could not match font "%s"' % self._name)
        self.face = FreeTypeFace.from_fontconfig(match)

    @classmethod
    def have_font(cls, name):
        if cls._memory_faces.contains(name):
            return True
        else:
            return get_fontconfig().have_font(name)

    @classmethod
    def add_font_data(cls, data):
        face = FreeTypeMemoryFace(data)
        cls._memory_faces.add(face)


class FreeTypeFace:
    __doc__ = "FreeType typographic face object.\n\n    Keeps the reference count to the face at +1 as long as this object exists. If other objects\n    want to keep a face without a reference to this object, they should increase the reference\n    counter themselves and decrease it again when done.\n    "

    def __init__(self, ft_face):
        assert ft_face is not None
        self.ft_face = ft_face
        self._get_best_name()

    @classmethod
    def from_file(cls, file_name):
        ft_library = ft_get_library()
        ft_face = FT_Face()
        FT_New_Face(ft_library, asbytes(file_name), 0, byref(ft_face))
        return cls(ft_face)

    @classmethod
    def from_fontconfig(cls, match):
        if match.face is not None:
            FT_Reference_Face(match.face)
            return cls(match.face)
        else:
            if not match.file:
                raise base.FontException('No filename for "%s"' % match.name)
            return cls.from_file(match.file)

    @property
    def name(self):
        return self._name

    @property
    def family_name(self):
        return asstr(self.ft_face.contents.family_name)

    @property
    def style_flags(self):
        return self.ft_face.contents.style_flags

    @property
    def bold(self):
        return self.style_flags & FT_STYLE_FLAG_BOLD != 0

    @property
    def italic(self):
        return self.style_flags & FT_STYLE_FLAG_ITALIC != 0

    @property
    def face_flags(self):
        return self.ft_face.contents.face_flags

    def __del__(self):
        if self.ft_face is not None:
            FT_Done_Face(self.ft_face)
            self.ft_face = None

    def set_char_size(self, size, dpi):
        face_size = float_to_f26p6(size)
        try:
            FT_Set_Char_Size(self.ft_face, 0, face_size, dpi, dpi)
            return True
        except FreeTypeError as e:
            if e.errcode == 23:
                return False
            raise

    def get_character_index(self, character):
        return get_fontconfig().char_index(self.ft_face, character)

    def get_glyph_slot(self, glyph_index):
        FT_Load_Glyph(self.ft_face, glyph_index, FT_LOAD_RENDER)
        return self.ft_face.contents.glyph.contents

    def get_font_metrics(self, size, dpi):
        if self.set_char_size(size, dpi):
            metrics = self.ft_face.contents.size.contents.metrics
            if metrics.ascender == 0:
                if metrics.descender == 0:
                    return self._get_font_metrics_workaround()
            return FreeTypeFontMetrics(ascent=(int(f26p6_to_float(metrics.ascender))), descent=(int(f26p6_to_float(metrics.descender))))
        else:
            return self._get_font_metrics_workaround()

    def _get_font_metrics_workaround(self):
        i = self.get_character_index("X")
        self.get_glyph_slot(i)
        ascent = self.ft_face.contents.available_sizes.contents.height
        return FreeTypeFontMetrics(ascent=ascent, descent=(-ascent // 4))

    def _get_best_name(self):
        self._name = asstr(self.ft_face.contents.family_name)
        self._get_font_family_from_ttf

    def _get_font_family_from_ttfParse error at or near `FOR_ITER' instruction at offset 4


class FreeTypeMemoryFace(FreeTypeFace):

    def __init__(self, data):
        self._copy_font_data(data)
        super().__init__(self._create_font_face())

    def _copy_font_data(self, data):
        self.font_data = FT_Byte * len(data)()
        ctypes.memmove(self.font_data, data, len(data))

    def _create_font_face(self):
        ft_library = ft_get_library()
        ft_face = FT_Face()
        FT_New_Memory_Face(ft_library, self.font_data, len(self.font_data), 0, byref(ft_face))
        return ft_face