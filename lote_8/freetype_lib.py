# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\font\freetype_lib.py
from ctypes import *
from .base import FontException
import pyglet.lib
_libfreetype = pyglet.lib.load_library("freetype")
_font_data = {}

def _get_function(name, argtypes, rtype):
    try:
        func = getattr(_libfreetype, name)
        func.argtypes = argtypes
        func.restype = rtype
        return func
    except AttributeError as e:
        raise ImportError(e)


FT_Byte = c_char
FT_Bytes = POINTER(FT_Byte)
FT_Char = c_byte
FT_Int = c_int
FT_UInt = c_uint
FT_Int16 = c_int16
FT_UInt16 = c_uint16
FT_Int32 = c_int32
FT_UInt32 = c_uint32
FT_Int64 = c_int64
FT_UInt64 = c_uint64
FT_Short = c_short
FT_UShort = c_ushort
FT_Long = c_long
FT_ULong = c_ulong
FT_Bool = c_char
FT_Offset = c_size_t
FT_String = c_char
FT_String_Ptr = c_char_p
FT_Tag = FT_UInt32
FT_Error = c_int
FT_Fixed = c_long
FT_Pointer = c_void_p
FT_Pos = c_long

class FT_Vector(Structure):
    _fields_ = [
     (
      "x", FT_Pos),
     (
      "y", FT_Pos)]


class FT_BBox(Structure):
    _fields_ = [
     (
      "xMin", FT_Pos),
     (
      "yMin", FT_Pos),
     (
      "xMax", FT_Pos),
     (
      "yMax", FT_Pos)]


class FT_Matrix(Structure):
    _fields_ = [
     (
      "xx", FT_Fixed),
     (
      "xy", FT_Fixed),
     (
      "yx", FT_Fixed),
     (
      "yy", FT_Fixed)]


FT_FWord = c_short
FT_UFWord = c_ushort
FT_F2Dot14 = c_short

class FT_UnitVector(Structure):
    _fields_ = [
     (
      "x", FT_F2Dot14),
     (
      "y", FT_F2Dot14)]


FT_F26Dot6 = c_long

class FT_Data(Structure):
    _fields_ = [
     (
      "pointer", POINTER(FT_Byte)),
     (
      "length", FT_Int)]


FT_Generic_Finalizer = CFUNCTYPE(None, c_void_p)

class FT_Generic(Structure):
    _fields_ = [
     (
      "data", c_void_p),
     (
      "finalizer", FT_Generic_Finalizer)]


class FT_Bitmap(Structure):
    _fields_ = [
     (
      "rows", c_uint),
     (
      "width", c_uint),
     (
      "pitch", c_int),
     (
      "buffer", POINTER(c_ubyte)),
     (
      "num_grays", c_short),
     (
      "pixel_mode", c_ubyte),
     (
      "palette_mode", c_ubyte),
     (
      "palette", c_void_p)]


FT_PIXEL_MODE_NONE = 0
FT_PIXEL_MODE_MONO = 1
FT_PIXEL_MODE_GRAY = 2
FT_PIXEL_MODE_GRAY2 = 3
FT_PIXEL_MODE_GRAY4 = 4
FT_PIXEL_MODE_LCD = 5
FT_PIXEL_MODE_LCD_V = 6
FT_PIXEL_MODE_BGRA = 7

class FT_LibraryRec(Structure):
    _fields_ = [
     (
      "dummy", c_int)]

    def __del__(self):
        global _library
        try:
            print("FT_LibraryRec.__del__")
            FT_Done_FreeType(byref(self))
            _library = None
        except:
            pass


FT_Library = POINTER(FT_LibraryRec)

class FT_Bitmap_Size(Structure):
    _fields_ = [
     (
      "height", c_ushort),
     (
      "width", c_ushort),
     (
      "size", c_long),
     (
      "x_ppem", c_long),
     (
      "y_ppem", c_long)]


class FT_Glyph_Metrics(Structure):
    _fields_ = [
     (
      "width", FT_Pos),
     (
      "height", FT_Pos),
     (
      "horiBearingX", FT_Pos),
     (
      "horiBearingY", FT_Pos),
     (
      "horiAdvance", FT_Pos),
     (
      "vertBearingX", FT_Pos),
     (
      "vertBearingY", FT_Pos),
     (
      "vertAdvance", FT_Pos)]

    def dump(self):
        for name, type in self._fields_:
            print("FT_Glyph_Metrics", name, repr(getattr(self, name)))


FT_Glyph_Format = c_ulong

def FT_IMAGE_TAG(tag):
    return ord(tag[0]) << 24 | ord(tag[1]) << 16 | ord(tag[2]) << 8 | ord(tag[3])


FT_GLYPH_FORMAT_NONE = 0
FT_GLYPH_FORMAT_COMPOSITE = FT_IMAGE_TAG("comp")
FT_GLYPH_FORMAT_BITMAP = FT_IMAGE_TAG("bits")
FT_GLYPH_FORMAT_OUTLINE = FT_IMAGE_TAG("outl")
FT_GLYPH_FORMAT_PLOTTER = FT_IMAGE_TAG("plot")

class FT_Outline(Structure):
    _fields_ = [
     (
      "n_contours", c_short),
     (
      "n_points", c_short),
     (
      "points", POINTER(FT_Vector)),
     (
      "tags", c_char_p),
     (
      "contours", POINTER(c_short)),
     (
      "flags", c_int)]


FT_SubGlyph = c_void_p

class FT_GlyphSlotRec(Structure):
    _fields_ = [
     (
      "library", FT_Library),
     (
      "face", c_void_p),
     (
      "next", c_void_p),
     (
      "reserved", FT_UInt),
     (
      "generic", FT_Generic),
     (
      "metrics", FT_Glyph_Metrics),
     (
      "linearHoriAdvance", FT_Fixed),
     (
      "linearVertAdvance", FT_Fixed),
     (
      "advance", FT_Vector),
     (
      "format", FT_Glyph_Format),
     (
      "bitmap", FT_Bitmap),
     (
      "bitmap_left", FT_Int),
     (
      "bitmap_top", FT_Int),
     (
      "outline", FT_Outline),
     (
      "num_subglyphs", FT_UInt),
     (
      "subglyphs", FT_SubGlyph),
     (
      "control_data", c_void_p),
     (
      "control_len", c_long),
     (
      "lsb_delta", FT_Pos),
     (
      "rsb_delta", FT_Pos),
     (
      "other", c_void_p),
     (
      "internal", c_void_p)]


FT_GlyphSlot = POINTER(FT_GlyphSlotRec)

class FT_Size_Metrics(Structure):
    _fields_ = [
     (
      "x_ppem", FT_UShort),
     (
      "y_ppem", FT_UShort),
     (
      "x_scale", FT_Fixed),
     (
      "y_scale", FT_Fixed),
     (
      "ascender", FT_Pos),
     (
      "descender", FT_Pos),
     (
      "height", FT_Pos),
     (
      "max_advance", FT_Pos)]


class FT_SizeRec(Structure):
    _fields_ = [
     (
      "face", c_void_p),
     (
      "generic", FT_Generic),
     (
      "metrics", FT_Size_Metrics),
     (
      "internal", c_void_p)]


FT_Size = POINTER(FT_SizeRec)

class FT_FaceRec(Structure):
    _fields_ = [
     (
      "num_faces", FT_Long),
     (
      "face_index", FT_Long),
     (
      "face_flags", FT_Long),
     (
      "style_flags", FT_Long),
     (
      "num_glyphs", FT_Long),
     (
      "family_name", FT_String_Ptr),
     (
      "style_name", FT_String_Ptr),
     (
      "num_fixed_sizes", FT_Int),
     (
      "available_sizes", POINTER(FT_Bitmap_Size)),
     (
      "num_charmaps", FT_Int),
     (
      "charmaps", c_void_p),
     (
      "generic", FT_Generic),
     (
      "bbox", FT_BBox),
     (
      "units_per_EM", FT_UShort),
     (
      "ascender", FT_Short),
     (
      "descender", FT_Short),
     (
      "height", FT_Short),
     (
      "max_advance_width", FT_Short),
     (
      "max_advance_height", FT_Short),
     (
      "underline_position", FT_Short),
     (
      "underline_thickness", FT_Short),
     (
      "glyph", FT_GlyphSlot),
     (
      "size", FT_Size),
     (
      "charmap", c_void_p),
     (
      "driver", c_void_p),
     (
      "memory", c_void_p),
     (
      "stream", c_void_p),
     (
      "sizes_list", c_void_p),
     (
      "autohint", FT_Generic),
     (
      "extensions", c_void_p),
     (
      "internal", c_void_p)]

    def dump(self):
        for name, type in self._fields_:
            print("FT_FaceRec", name, repr(getattr(self, name)))

    def has_kerning(self):
        return self.face_flags & FT_FACE_FLAG_KERNING


FT_Face = POINTER(FT_FaceRec)
FT_FACE_FLAG_SCALABLE = 1
FT_FACE_FLAG_FIXED_SIZES = 2
FT_FACE_FLAG_FIXED_WIDTH = 4
FT_FACE_FLAG_SFNT = 8
FT_FACE_FLAG_HORIZONTAL = 16
FT_FACE_FLAG_VERTICAL = 32
FT_FACE_FLAG_KERNING = 64
FT_FACE_FLAG_FAST_GLYPHS = 128
FT_FACE_FLAG_MULTIPLE_MASTERS = 256
FT_FACE_FLAG_GLYPH_NAMES = 512
FT_FACE_FLAG_EXTERNAL_STREAM = 1024
FT_FACE_FLAG_HINTER = 2048
FT_STYLE_FLAG_ITALIC = 1
FT_STYLE_FLAG_BOLD = 2
FT_RENDER_MODE_NORMAL, FT_RENDER_MODE_LIGHT, FT_RENDER_MODE_MONO, FT_RENDER_MODE_LCD, FT_RENDER_MODE_LCD_V = range(5)

def FT_LOAD_TARGET_(x):
    return (x & 15) << 16


FT_LOAD_TARGET_NORMAL = FT_LOAD_TARGET_(FT_RENDER_MODE_NORMAL)
FT_LOAD_TARGET_LIGHT = FT_LOAD_TARGET_(FT_RENDER_MODE_LIGHT)
FT_LOAD_TARGET_MONO = FT_LOAD_TARGET_(FT_RENDER_MODE_MONO)
FT_LOAD_TARGET_LCD = FT_LOAD_TARGET_(FT_RENDER_MODE_LCD)
FT_LOAD_TARGET_LCD_V = FT_LOAD_TARGET_(FT_RENDER_MODE_LCD_V)
FT_PIXEL_MODE_NONE, FT_PIXEL_MODE_MONO, FT_PIXEL_MODE_GRAY, FT_PIXEL_MODE_GRAY2, FT_PIXEL_MODE_GRAY4, FT_PIXEL_MODE_LCD, FT_PIXEL_MODE_LCD_V = range(7)

def f16p16_to_float(value):
    return float(value) / 65536


def float_to_f16p16(value):
    return int(value * 65536)


def f26p6_to_float(value):
    return float(value) / 64


def float_to_f26p6(value):
    return int(value * 64)


class FreeTypeError(FontException):

    def __init__(self, message, errcode):
        self.message = message
        self.errcode = errcode

    def __str__(self):
        return "%s: %s (%s)" % (self.__class__.__name__, self.message,
         self._ft_errors.get(self.errcode, "unknown error"))

    @classmethod
    def check_and_raise_on_error(cls, errcode):
        if errcode != 0:
            raise cls(None, errcode)

    _ft_errors = {
     0: '"no error"', 
     1: '"cannot open resource"', 
     2: '"unknown file format"', 
     3: '"broken file"', 
     4: '"invalid FreeType version"', 
     5: '"module version is too low"', 
     6: '"invalid argument"', 
     7: '"unimplemented feature"', 
     8: '"broken table"', 
     9: '"broken offset within table"', 
     16: '"invalid glyph index"', 
     17: '"invalid character code"', 
     18: '"unsupported glyph image format"', 
     19: '"cannot render this glyph format"', 
     20: '"invalid outline"', 
     21: '"invalid composite glyph"', 
     22: '"too many hints"', 
     23: '"invalid pixel size"', 
     32: '"invalid object handle"', 
     33: '"invalid library handle"', 
     34: '"invalid module handle"', 
     35: '"invalid face handle"', 
     36: '"invalid size handle"', 
     37: '"invalid glyph slot handle"', 
     38: '"invalid charmap handle"', 
     39: '"invalid cache manager handle"', 
     40: '"invalid stream handle"', 
     48: '"too many modules"', 
     49: '"too many extensions"', 
     64: '"out of memory"', 
     65: '"unlisted object"', 
     81: '"cannot open stream"', 
     82: '"invalid stream seek"', 
     83: '"invalid stream skip"', 
     84: '"invalid stream read"', 
     85: '"invalid stream operation"', 
     86: '"invalid frame operation"', 
     87: '"nested frame access"', 
     88: '"invalid frame read"', 
     96: '"raster uninitialized"', 
     97: '"raster corrupted"', 
     98: '"raster overflow"', 
     99: '"negative height while rastering"', 
     112: '"too many registered caches"', 
     128: '"invalid opcode"', 
     129: '"too few arguments"', 
     130: '"stack overflow"', 
     131: '"code overflow"', 
     132: '"bad argument"', 
     133: '"division by zero"', 
     134: '"invalid reference"', 
     135: '"found debug opcode"', 
     136: '"found ENDF opcode in execution stream"', 
     137: '"nested DEFS"', 
     138: '"invalid code range"', 
     139: '"execution context too long"', 
     140: '"too many function definitions"', 
     141: '"too many instruction definitions"', 
     142: '"SFNT font table missing"', 
     143: '"horizontal header (hhea, table missing"', 
     144: '"locations (loca, table missing"', 
     145: '"name table missing"', 
     146: '"character map (cmap, table missing"', 
     147: '"horizontal metrics (hmtx, table missing"', 
     148: '"PostScript (post, table missing"', 
     149: '"invalid horizontal metrics"', 
     150: '"invalid character map (cmap, format"', 
     151: '"invalid ppem value"', 
     152: '"invalid vertical metrics"', 
     153: '"could not find context"', 
     154: '"invalid PostScript (post, table format"', 
     155: '"invalid PostScript (post, table"', 
     160: '"opcode syntax error"', 
     161: '"argument stack underflow"', 
     162: '"ignore"', 
     176: '"`STARTFONT\' field missing"', 
     177: '"`FONT\' field missing"', 
     178: '"`SIZE\' field missing"', 
     179: '"`CHARS\' field missing"', 
     180: '"`STARTCHAR\' field missing"', 
     181: '"`ENCODING\' field missing"', 
     182: '"`BBX\' field missing"', 
     183: '"`BBX\' too big"'}


def _get_function_with_error_handling(name, argtypes, rtype):
    func = _get_function(name, argtypes, rtype)

    def _error_handling(*args, **kwargs):
        err = func(*args, **kwargs)
        FreeTypeError.check_and_raise_on_error(err)

    return _error_handling


FT_LOAD_RENDER = 4
FT_Init_FreeType = _get_function_with_error_handling("FT_Init_FreeType", [
 POINTER(FT_Library)], FT_Error)
FT_Done_FreeType = _get_function_with_error_handling("FT_Done_FreeType", [
 FT_Library], FT_Error)
FT_New_Face = _get_function_with_error_handling("FT_New_Face", [
 FT_Library, c_char_p, FT_Long, POINTER(FT_Face)], FT_Error)
FT_Done_Face = _get_function_with_error_handling("FT_Done_Face", [
 FT_Face], FT_Error)
FT_Reference_Face = _get_function_with_error_handling("FT_Reference_Face", [
 FT_Face], FT_Error)
FT_New_Memory_Face = _get_function_with_error_handling("FT_New_Memory_Face", [
 FT_Library, POINTER(FT_Byte), FT_Long, FT_Long, POINTER(FT_Face)], FT_Error)
FT_Set_Char_Size = _get_function_with_error_handling("FT_Set_Char_Size", [
 FT_Face, FT_F26Dot6, FT_F26Dot6, FT_UInt, FT_UInt], FT_Error)
FT_Set_Pixel_Sizes = _get_function_with_error_handling("FT_Set_Pixel_Sizes", [
 FT_Face, FT_UInt, FT_UInt], FT_Error)
FT_Load_Glyph = _get_function_with_error_handling("FT_Load_Glyph", [
 FT_Face, FT_UInt, FT_Int32], FT_Error)
FT_Get_Char_Index = _get_function_with_error_handling("FT_Get_Char_Index", [
 FT_Face, FT_ULong], FT_Error)
FT_Load_Char = _get_function_with_error_handling("FT_Load_Char", [
 FT_Face, FT_ULong, FT_Int32], FT_Error)
FT_Get_Kerning = _get_function_with_error_handling("FT_Get_Kerning", [
 FT_Face, FT_UInt, FT_UInt, FT_UInt, POINTER(FT_Vector)], FT_Error)

class FT_SfntName(Structure):
    _fields_ = [
     (
      "platform_id", FT_UShort),
     (
      "encoding_id", FT_UShort),
     (
      "language_id", FT_UShort),
     (
      "name_id", FT_UShort),
     (
      "string", POINTER(FT_Byte)),
     (
      "string_len", FT_UInt)]


FT_Get_Sfnt_Name_Count = _get_function("FT_Get_Sfnt_Name_Count", [
 FT_Face], FT_UInt)
FT_Get_Sfnt_Name = _get_function_with_error_handling("FT_Get_Sfnt_Name", [
 FT_Face, FT_UInt, POINTER(FT_SfntName)], FT_Error)
TT_PLATFORM_MICROSOFT = 3
TT_MS_ID_UNICODE_CS = 1
TT_NAME_ID_COPYRIGHT = 0
TT_NAME_ID_FONT_FAMILY = 1
TT_NAME_ID_FONT_SUBFAMILY = 2
TT_NAME_ID_UNIQUE_ID = 3
TT_NAME_ID_FULL_NAME = 4
TT_NAME_ID_VERSION_STRING = 5
TT_NAME_ID_PS_NAME = 6
TT_NAME_ID_TRADEMARK = 7
TT_NAME_ID_MANUFACTURER = 8
TT_NAME_ID_DESIGNER = 9
TT_NAME_ID_DESCRIPTION = 10
TT_NAME_ID_VENDOR_URL = 11
TT_NAME_ID_DESIGNER_URL = 12
TT_NAME_ID_LICENSE = 13
TT_NAME_ID_LICENSE_URL = 14
TT_NAME_ID_PREFERRED_FAMILY = 16
TT_NAME_ID_PREFERRED_SUBFAMILY = 17
TT_NAME_ID_MAC_FULL_NAME = 18
TT_NAME_ID_CID_FINDFONT_NAME = 20
_library = None

def ft_get_library():
    global _library
    if not _library:
        _library = FT_Library()
        error = FT_Init_FreeType(byref(_library))
        if error:
            raise FontException("an error occurred during library initialization", error)
    return _library
