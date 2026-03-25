# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\font\quartz.py
import math, warnings
from ctypes import c_void_p, c_int32, byref, c_byte
from pyglet.font import base
import pyglet.image
from pyglet.libs.darwin import cocoapy
cf = cocoapy.cf
ct = cocoapy.ct
quartz = cocoapy.quartz

class QuartzGlyphRenderer(base.GlyphRenderer):

    def __init__(self, font):
        super().__init__(font)
        self.font = font

    def render(self, text):
        ctFont = self.font.ctFont
        attributes = c_void_p(cf.CFDictionaryCreateMutable(None, 1, cf.kCFTypeDictionaryKeyCallBacks, cf.kCFTypeDictionaryValueCallBacks))
        cf.CFDictionaryAddValue(attributes, cocoapy.kCTFontAttributeName, ctFont)
        string = c_void_p(cf.CFAttributedStringCreate(None, cocoapy.CFSTR(text), attributes))
        line = c_void_p(ct.CTLineCreateWithAttributedString(string))
        cf.CFRelease(string)
        cf.CFRelease(attributes)
        count = len(text)
        chars = (cocoapy.UniChar * count)(*list(map(ord, str(text))))
        glyphs = cocoapy.CGGlyph * count()
        ct.CTFontGetGlyphsForCharacters(ctFont, chars, glyphs, count)
        rect = ct.CTFontGetBoundingRectsForGlyphs(ctFont, 0, glyphs, None, count)
        advance = ct.CTFontGetAdvancesForGlyphs(ctFont, 0, glyphs, None, count)
        width = max(int(math.ceil(rect.size.width) + 2), 1)
        height = max(int(math.ceil(rect.size.height) + 2), 1)
        baseline = -int(math.floor(rect.origin.y)) + 1
        lsb = int(math.floor(rect.origin.x)) - 1
        advance = int(round(advance))
        bitsPerComponent = 8
        bytesPerRow = 4 * width
        colorSpace = c_void_p(quartz.CGColorSpaceCreateDeviceRGB())
        bitmap = c_void_p(quartz.CGBitmapContextCreate(None, width, height, bitsPerComponent, bytesPerRow, colorSpace, cocoapy.kCGImageAlphaPremultipliedLast))
        quartz.CGContextSetShouldAntialias(bitmap, True)
        quartz.CGContextSetTextPosition(bitmap, -lsb, baseline)
        ct.CTLineDraw(line, bitmap)
        cf.CFRelease(line)
        imageRef = c_void_p(quartz.CGBitmapContextCreateImage(bitmap))
        bytesPerRow = quartz.CGImageGetBytesPerRow(imageRef)
        dataProvider = c_void_p(quartz.CGImageGetDataProvider(imageRef))
        imageData = c_void_p(quartz.CGDataProviderCopyData(dataProvider))
        buffersize = cf.CFDataGetLength(imageData)
        buffer = c_byte * buffersize()
        byteRange = cocoapy.CFRange(0, buffersize)
        cf.CFDataGetBytes(imageData, byteRange, buffer)
        quartz.CGImageRelease(imageRef)
        quartz.CGDataProviderRelease(imageData)
        cf.CFRelease(bitmap)
        cf.CFRelease(colorSpace)
        glyph_image = pyglet.image.ImageData(width, height, "RGBA", buffer, bytesPerRow)
        glyph = self.font.create_glyph(glyph_image)
        glyph.set_bearings(baseline, lsb, advance)
        t = list(glyph.tex_coords)
        glyph.tex_coords = t[9:12] + t[6:9] + t[3:6] + t[:3]
        return glyph


class QuartzFont(base.Font):
    glyph_renderer_class = QuartzGlyphRenderer
    _loaded_CGFont_table = {}

    def _lookup_font_with_family_and_traits(self, family, traits):
        if family not in self._loaded_CGFont_table:
            return
        else:
            fonts = self._loaded_CGFont_table[family]
            if not fonts:
                return
            if traits in fonts:
                return fonts[traits]
            for t, f in fonts.items():
                if traits & t:
                    return f

            if 0 in fonts:
                return fonts[0]
            return list(fonts.values())[0]

    def _create_font_descriptor(self, family_name, traits):
        attributes = c_void_p(cf.CFDictionaryCreateMutable(None, 0, cf.kCFTypeDictionaryKeyCallBacks, cf.kCFTypeDictionaryValueCallBacks))
        cfname = cocoapy.CFSTR(family_name)
        cf.CFDictionaryAddValue(attributes, cocoapy.kCTFontFamilyNameAttribute, cfname)
        cf.CFRelease(cfname)
        itraits = c_int32(traits)
        symTraits = c_void_p(cf.CFNumberCreate(None, cocoapy.kCFNumberSInt32Type, byref(itraits)))
        if symTraits:
            traitsDict = c_void_p(cf.CFDictionaryCreateMutable(None, 0, cf.kCFTypeDictionaryKeyCallBacks, cf.kCFTypeDictionaryValueCallBacks))
            if traitsDict:
                cf.CFDictionaryAddValue(traitsDict, cocoapy.kCTFontSymbolicTrait, symTraits)
                cf.CFDictionaryAddValue(attributes, cocoapy.kCTFontTraitsAttribute, traitsDict)
                cf.CFRelease(traitsDict)
            cf.CFRelease(symTraits)
        descriptor = c_void_p(ct.CTFontDescriptorCreateWithAttributes(attributes))
        cf.CFRelease(attributes)
        return descriptor

    def __init__(self, name, size, bold=False, italic=False, stretch=False, dpi=None):
        if stretch:
            warnings.warn("The current font render does not support stretching.")
        else:
            super().__init__()
            name = name or "Helvetica"
            dpi = dpi or 96
            size = size * dpi / 72.0
            traits = 0
            if bold:
                traits |= cocoapy.kCTFontBoldTrait
            if italic:
                traits |= cocoapy.kCTFontItalicTrait
            name = str(name)
            cgFont = self._lookup_font_with_family_and_traits(name, traits)
            if cgFont:
                self.ctFont = c_void_p(ct.CTFontCreateWithGraphicsFont(cgFont, size, None, None))
            else:
                descriptor = self._create_font_descriptor(name, traits)
                self.ctFont = c_void_p(ct.CTFontCreateWithFontDescriptor(descriptor, size, None))
                cf.CFRelease(descriptor)
                if not self.ctFont:
                    raise AssertionError("Couldn't load font: " + name)
        string = c_void_p(ct.CTFontCopyFamilyName(self.ctFont))
        self._family_name = str(cocoapy.cfstring_to_string(string))
        cf.CFRelease(string)
        self.ascent = int(math.ceil(ct.CTFontGetAscent(self.ctFont)))
        self.descent = -int(math.ceil(ct.CTFontGetDescent(self.ctFont)))

    @property
    def name(self):
        return self._family_name

    def __del__(self):
        cf.CFRelease(self.ctFont)

    @classmethod
    def have_font(cls, name):
        name = str(name)
        if name in cls._loaded_CGFont_table:
            return True
        else:
            cfstring = cocoapy.CFSTR(name)
            cgfont = c_void_p(quartz.CGFontCreateWithFontName(cfstring))
            cf.CFRelease(cfstring)
            if cgfont:
                cf.CFRelease(cgfont)
                return True
            return False

    @classmethod
    def add_font_data(cls, data):
        dataRef = c_void_p(cf.CFDataCreate(None, data, len(data)))
        provider = c_void_p(quartz.CGDataProviderCreateWithCFData(dataRef))
        cgFont = c_void_p(quartz.CGFontCreateWithDataProvider(provider))
        cf.CFRelease(dataRef)
        quartz.CGDataProviderRelease(provider)
        ctFont = c_void_p(ct.CTFontCreateWithGraphicsFont(cgFont, 1, None, None))
        string = c_void_p(ct.CTFontCopyFamilyName(ctFont))
        familyName = str(cocoapy.cfstring_to_string(string))
        cf.CFRelease(string)
        string = c_void_p(ct.CTFontCopyFullName(ctFont))
        fullName = str(cocoapy.cfstring_to_string(string))
        cf.CFRelease(string)
        traits = ct.CTFontGetSymbolicTraits(ctFont)
        cf.CFRelease(ctFont)
        if familyName not in cls._loaded_CGFont_table:
            cls._loaded_CGFont_table[familyName] = {}
        cls._loaded_CGFont_table[familyName][traits] = cgFont
        if fullName not in cls._loaded_CGFont_table:
            cls._loaded_CGFont_table[fullName] = {}
        cls._loaded_CGFont_table[fullName][traits] = cgFont
