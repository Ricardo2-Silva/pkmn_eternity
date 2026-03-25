# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\font\win32.py
import math, warnings
from sys import byteorder
import pyglet
from pyglet.font import base
from pyglet.font import win32query
import pyglet.image
from pyglet.libs.win32.constants import *
from pyglet.libs.win32.types import *
from pyglet.libs.win32 import _gdi32 as gdi32, _user32 as user32
from pyglet.libs.win32 import _kernel32 as kernel32
from pyglet.util import asbytes
_debug_font = pyglet.options["debug_font"]

def str_ucs2(text):
    if byteorder == "big":
        text = text.encode("utf_16_be")
    else:
        text = text.encode("utf_16_le")
    return create_string_buffer(text + "\x00")


_debug_dir = "debug_font"

def _debug_filename(base, extension):
    import os
    if not os.path.exists(_debug_dir):
        os.makedirs(_debug_dir)
    name = "%s-%%d.%%s" % os.path.join(_debug_dir, base)
    num = 1
    while os.path.exists(name % (num, extension)):
        num += 1

    return name % (num, extension)


def _debug_image(image, name):
    filename = _debug_filename(name, "png")
    image.save(filename)
    _debug("Saved image %r to %s" % (image, filename))


_debug_logfile = None

def _debug(msg):
    global _debug_logfile
    if not _debug_logfile:
        _debug_logfile = open(_debug_filename("log", "txt"), "wt")
    _debug_logfile.write(msg + "\n")


class Win32GlyphRenderer(base.GlyphRenderer):

    def __init__(self, font):
        self._bitmap = None
        self._dc = None
        self._bitmap_rect = None
        super(Win32GlyphRenderer, self).__init__(font)
        self.font = font
        width = font.max_glyph_width
        height = font.ascent - font.descent
        width = (width | 3) + 1
        height = (height | 3) + 1
        self._create_bitmap(width, height)
        gdi32.SelectObject(self._dc, self.font.hfont)

    def _create_bitmap(self, width, height):
        return

    def render(self, text):
        raise NotImplementedError("abstract")


class GDIGlyphRenderer(Win32GlyphRenderer):

    def __del__(self):
        try:
            if self._dc:
                gdi32.DeleteDC(self._dc)
            if self._bitmap:
                gdi32.DeleteObject(self._bitmap)
        except:
            pass

    def render(self, text):
        abc = ABC()
        if gdi32.GetCharABCWidthsW(self._dc, ord(text), ord(text), byref(abc)):
            width = abc.abcB
            lsb = abc.abcA
            advance = abc.abcA + abc.abcB + abc.abcC
        else:
            width_buf = c_int()
            gdi32.GetCharWidth32W(self._dc, ord(text), ord(text), byref(width_buf))
            width = width_buf.value
            lsb = 0
            advance = width
        height = self._bitmap_height
        image = self._get_image(text, width, height, lsb)
        glyph = self.font.create_glyph(image)
        glyph.set_bearings(-self.font.descent, lsb, advance)
        if _debug_font:
            _debug("%r.render(%s)" % (self, text))
            _debug("abc.abcA = %r" % abc.abcA)
            _debug("abc.abcB = %r" % abc.abcB)
            _debug("abc.abcC = %r" % abc.abcC)
            _debug("width = %r" % width)
            _debug("height = %r" % height)
            _debug("lsb = %r" % lsb)
            _debug("advance = %r" % advance)
            _debug_image(image, "glyph_%s" % text)
            _debug_image(self.font.textures[0], "tex_%s" % text)
        return glyph

    def _get_image(self, text, width, height, lsb):
        gdi32.SelectObject(self._dc, self._bitmap)
        gdi32.SelectObject(self._dc, self.font.hfont)
        gdi32.SetBkColor(self._dc, 0)
        gdi32.SetTextColor(self._dc, 16777215)
        gdi32.SetBkMode(self._dc, OPAQUE)
        user32.FillRect(self._dc, byref(self._bitmap_rect), self._black)
        gdi32.ExtTextOutA(self._dc, -lsb, 0, 0, None, text, len(text), None)
        gdi32.GdiFlush()
        image = pyglet.image.ImageData(width, height, "AXXX", self._bitmap_data, self._bitmap_rect.right * 4)
        return image

    def _create_bitmap(self, width, height):
        self._black = gdi32.GetStockObject(BLACK_BRUSH)
        self._white = gdi32.GetStockObject(WHITE_BRUSH)
        if self._dc:
            gdi32.ReleaseDC(self._dc)
        if self._bitmap:
            gdi32.DeleteObject(self._bitmap)
        pitch = width * 4
        data = POINTER(c_byte * (height * pitch))()
        info = BITMAPINFO()
        info.bmiHeader.biSize = sizeof(info.bmiHeader)
        info.bmiHeader.biWidth = width
        info.bmiHeader.biHeight = height
        info.bmiHeader.biPlanes = 1
        info.bmiHeader.biBitCount = 32
        info.bmiHeader.biCompression = BI_RGB
        self._dc = gdi32.CreateCompatibleDC(None)
        self._bitmap = gdi32.CreateDIBSection(None, byref(info), DIB_RGB_COLORS, byref(data), None, 0)
        kernel32.SetLastError(0)
        self._bitmap_data = data.contents
        self._bitmap_rect = RECT()
        self._bitmap_rect.left = 0
        self._bitmap_rect.right = width
        self._bitmap_rect.top = 0
        self._bitmap_rect.bottom = height
        self._bitmap_height = height
        if _debug_font:
            _debug("%r._create_dc(%d, %d)" % (self, width, height))
            _debug("_dc = %r" % self._dc)
            _debug("_bitmap = %r" % self._bitmap)
            _debug("pitch = %r" % pitch)
            _debug("info.bmiHeader.biSize = %r" % info.bmiHeader.biSize)


class Win32Font(base.Font):
    glyph_renderer_class = GDIGlyphRenderer

    def __init__(self, name, size, bold=False, italic=False, stretch=False, dpi=None):
        super(Win32Font, self).__init__()
        self.logfont = self.get_logfont(name, size, bold, italic, dpi)
        self.hfont = gdi32.CreateFontIndirectA(byref(self.logfont))
        dc = user32.GetDC(0)
        metrics = TEXTMETRIC()
        gdi32.SelectObject(dc, self.hfont)
        gdi32.GetTextMetricsA(dc, byref(metrics))
        self.ascent = metrics.tmAscent
        self.descent = -metrics.tmDescent
        self.max_glyph_width = metrics.tmMaxCharWidth
        user32.ReleaseDC(0, dc)

    def __del__(self):
        gdi32.DeleteObject(self.hfont)

    @staticmethod
    def get_logfont(name, size, bold, italic, dpi):
        dc = user32.GetDC(0)
        if dpi is None:
            dpi = 96
        else:
            logpixelsy = dpi
            logfont = LOGFONT()
            logfont.lfHeight = int(-size * logpixelsy // 72)
            if bold:
                logfont.lfWeight = FW_BOLD
            else:
                logfont.lfWeight = FW_NORMAL
        logfont.lfItalic = italic
        logfont.lfFaceName = asbytes(name)
        logfont.lfQuality = ANTIALIASED_QUALITY
        user32.ReleaseDC(0, dc)
        return logfont

    @classmethod
    def have_font(cls, name):
        return win32query.have_font(name)

    @classmethod
    def add_font_data(cls, data):
        numfonts = c_uint32()
        gdi32.AddFontMemResourceEx(data, len(data), 0, byref(numfonts))


from pyglet.image.codecs.gdiplus import PixelFormat32bppARGB, gdiplus, Rect
from pyglet.image.codecs.gdiplus import ImageLockModeRead, BitmapData
DriverStringOptionsCmapLookup = 1
DriverStringOptionsRealizedAdvance = 4
TextRenderingHintAntiAlias = 4
TextRenderingHintAntiAliasGridFit = 3
StringFormatFlagsDirectionRightToLeft = 1
StringFormatFlagsDirectionVertical = 2
StringFormatFlagsNoFitBlackBox = 4
StringFormatFlagsDisplayFormatControl = 32
StringFormatFlagsNoFontFallback = 1024
StringFormatFlagsMeasureTrailingSpaces = 2048
StringFormatFlagsNoWrap = 4096
StringFormatFlagsLineLimit = 8192
StringFormatFlagsNoClip = 16384

class Rectf(ctypes.Structure):
    _fields_ = [
     (
      "x", ctypes.c_float),
     (
      "y", ctypes.c_float),
     (
      "width", ctypes.c_float),
     (
      "height", ctypes.c_float)]


class GDIPlusGlyphRenderer(Win32GlyphRenderer):

    def __del__(self):
        try:
            if self._matrix:
                res = gdiplus.GdipDeleteMatrix(self._matrix)
            else:
                if self._brush:
                    res = gdiplus.GdipDeleteBrush(self._brush)
                else:
                    if self._graphics:
                        res = gdiplus.GdipDeleteGraphics(self._graphics)
                    if self._bitmap:
                        res = gdiplus.GdipDisposeImage(self._bitmap)
                if self._dc:
                    res = user32.ReleaseDC(0, self._dc)
        except:
            pass

    def _create_bitmap(self, width, height):
        self._data = ctypes.c_byte * (4 * width * height)()
        self._bitmap = ctypes.c_void_p()
        self._format = PixelFormat32bppARGB
        gdiplus.GdipCreateBitmapFromScan0(width, height, width * 4, self._format, self._data, ctypes.byref(self._bitmap))
        self._graphics = ctypes.c_void_p()
        gdiplus.GdipGetImageGraphicsContext(self._bitmap, ctypes.byref(self._graphics))
        gdiplus.GdipSetPageUnit(self._graphics, UnitPixel)
        self._dc = user32.GetDC(0)
        gdi32.SelectObject(self._dc, self.font.hfont)
        gdiplus.GdipSetTextRenderingHint(self._graphics, TextRenderingHintAntiAliasGridFit)
        self._brush = ctypes.c_void_p()
        gdiplus.GdipCreateSolidFill(4294967295, ctypes.byref(self._brush))
        self._matrix = ctypes.c_void_p()
        gdiplus.GdipCreateMatrix(ctypes.byref(self._matrix))
        self._flags = DriverStringOptionsCmapLookup | DriverStringOptionsRealizedAdvance
        self._rect = Rect(0, 0, width, height)
        self._bitmap_height = height

    def render(self, text):
        ch = ctypes.create_unicode_buffer(text)
        len_ch = len(text)
        width = 10000
        height = self._bitmap_height
        rect = Rectf(0, self._bitmap_height - self.font.ascent + self.font.descent, width, height)
        generic = ctypes.c_void_p()
        gdiplus.GdipStringFormatGetGenericTypographic(ctypes.byref(generic))
        format = ctypes.c_void_p()
        gdiplus.GdipCloneStringFormat(generic, ctypes.byref(format))
        gdiplus.GdipDeleteStringFormat(generic)
        bbox = Rectf()
        flags = StringFormatFlagsMeasureTrailingSpaces | StringFormatFlagsNoClip | StringFormatFlagsNoFitBlackBox
        gdiplus.GdipSetStringFormatFlags(format, flags)
        gdiplus.GdipMeasureString(self._graphics, ch, len_ch, self.font._gdipfont, ctypes.byref(rect), format, ctypes.byref(bbox), None, None)
        lsb = 0
        advance = int(math.ceil(bbox.width))
        width = advance
        if self.font.italic:
            width += width // 2
            width = min(width, self._rect.Width)
        if text == "\r\n":
            text = "\r"
        abc = ABC()
        if gdi32.GetCharABCWidthsW(self._dc, ord(text), ord(text), byref(abc)):
            lsb = abc.abcA
            if lsb < 0:
                rect.x = -lsb
                width -= lsb
        gdiplus.GdipGraphicsClear(self._graphics, 0)
        gdiplus.GdipDrawString(self._graphics, ch, len_ch, self.font._gdipfont, ctypes.byref(rect), format, self._brush)
        gdiplus.GdipFlush(self._graphics, 1)
        gdiplus.GdipDeleteStringFormat(format)
        bitmap_data = BitmapData()
        gdiplus.GdipBitmapLockBits(self._bitmap, byref(self._rect), ImageLockModeRead, self._format, byref(bitmap_data))
        buffer = create_string_buffer(bitmap_data.Stride * bitmap_data.Height)
        memmove(buffer, bitmap_data.Scan0, len(buffer))
        gdiplus.GdipBitmapUnlockBits(self._bitmap, byref(bitmap_data))
        image = pyglet.image.ImageData(width, height, "BGRA", buffer, -bitmap_data.Stride)
        glyph = self.font.create_glyph(image)
        lsb = min(lsb, 0)
        glyph.set_bearings(-self.font.descent, lsb, advance)
        return glyph


FontStyleBold = 1
FontStyleItalic = 2
UnitPixel = 2
UnitPoint = 3

class GDIPlusFont(Win32Font):
    glyph_renderer_class = GDIPlusGlyphRenderer
    _private_fonts = None
    _default_name = "Arial"

    def __init__(self, name, size, bold=False, italic=False, stretch=False, dpi=None):
        if not name:
            name = self._default_name
        else:
            if stretch:
                warnings.warn("The current font render does not support stretching.")
            else:
                super().__init__(name, size, bold, italic, stretch, dpi)
                self._name = name
                family = ctypes.c_void_p()
                name = ctypes.c_wchar_p(name)
                if self._private_fonts:
                    gdiplus.GdipCreateFontFamilyFromName(name, self._private_fonts, ctypes.byref(family))
                if not family:
                    gdiplus.GdipCreateFontFamilyFromName(name, None, ctypes.byref(family))
                if not family:
                    self._name = self._default_name
                    gdiplus.GdipCreateFontFamilyFromName(ctypes.c_wchar_p(self._name), None, ctypes.byref(family))
                if dpi is None:
                    unit = UnitPoint
                    self.dpi = 96
                else:
                    unit = UnitPixel
                    size = size * dpi // 72
                    self.dpi = dpi
                style = 0
                if bold:
                    style |= FontStyleBold
            if italic:
                style |= FontStyleItalic
        self._gdipfont = ctypes.c_void_p()
        gdiplus.GdipCreateFont(family, ctypes.c_float(size), style, unit, ctypes.byref(self._gdipfont))
        gdiplus.GdipDeleteFontFamily(family)

    @property
    def name(self):
        return self._name

    def __del__(self):
        super(GDIPlusFont, self).__del__()
        gdiplus.GdipDeleteFont(self._gdipfont)

    @classmethod
    def add_font_data(cls, data):
        super(GDIPlusFont, cls).add_font_data(data)
        if not cls._private_fonts:
            cls._private_fonts = ctypes.c_void_p()
            gdiplus.GdipNewPrivateFontCollection(ctypes.byref(cls._private_fonts))
        gdiplus.GdipPrivateAddMemoryFont(cls._private_fonts, data, len(data))

    @classmethod
    def have_font(cls, name):
        family = ctypes.c_void_p()
        num_count = ctypes.c_int()
        gdiplus.GdipGetFontCollectionFamilyCount(cls._private_fonts, ctypes.byref(num_count))
        gpfamilies = ctypes.c_void_p * num_count.value()
        numFound = ctypes.c_int()
        gdiplus.GdipGetFontCollectionFamilyList(cls._private_fonts, num_count, gpfamilies, ctypes.byref(numFound))
        font_name = ctypes.create_unicode_buffer(32)
        for gpfamily in gpfamilies:
            gdiplus.GdipGetFamilyName(gpfamily, font_name, "\x00")
            if font_name.value == name:
                return True

        return super(GDIPlusFont, cls).have_font(name)
