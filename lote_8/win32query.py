# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\font\win32query.py
"""
Query system Windows fonts with pure Python.

Public domain work by anatoly techtonik <techtonik@gmail.com>
Use MIT License if public domain doesn't make sense for you.

The task: Get monospace font for an application in the order of
preference.

A problem: Font ID in Windows is its name. Windows doesn't provide
any information about filenames they contained in. From two different
files with the same font name you can get only one.

Windows also doesn't have a clear concept of _generic font family_
familiar from CSS specification. Here is how fontquery maps Windows
LOGFONT properties to generic CSS font families:

  serif      -   (LOGFONT.lfPitchAndFamily >> 4) == FF_ROMAN
  sans-serif -   (LOGFONT.lfPitchAndFamily >> 4) == FF_SWISS
  cursive    -   (LOGFONT.lfPitchAndFamily >> 4) == FF_SCRIPT
  fantasy    -   (LOGFONT.lfPitchAndFamily >> 4) == FF_DECORATIVE
  monospace  -   (lf.lfPitchAndFamily & 0b11) == FIXED_PITCH

NOTE: ATM, May 2015, the Microsoft documentation related to monospace
is misleading due to poor wording:
 - FF_MODERN in the description of LOGFONT structure tells
   "Fonts with constant stroke width (monospace), with or without serifs.
    Monospace fonts are usually modern.
    Pica, Elite, and CourierNew are examples.
   "
   
   Stroke width is the 'pen width', not glyph width. It should read

   "Fonts with constant stroke width, with or without serifs.
    Monospace fonts are usually modern, but not all modern are monospace
   "

PYGLET NOTE:
Examination of all fonts in a windows xp machine shows that all fonts
with

  fontentry.vector and fontentry.family != FF_DONTCARE

are rendered fine.

Use cases:
 [x] get the list of all available system font names
 [ ] get the list of all fonts for generic family
 [ ] get the list of all fonts for specific charset
 [ ] check if specific font is available

Considerations:
 - performance of querying all system fonts is not measured
 - Windows doesn't allow to get filenames of the fonts, so if there
   are two fonts with the same name, one will be missing

MSDN:

    If you request a font named Palatino, but no such font is available
on the system, the font mapper will substitute a font that has similar
attributes but a different name.

   [ ] check if font chosen by the system has required family

    To get the appropriate font, call EnumFontFamiliesEx with the
desired font characteristics in the LOGFONT structure, then retrieve the
appropriate typeface name and create the font using CreateFont or
CreateFontIndirect.

"""
DEBUG = False
__all__ = [
 "have_font", "font_list"]
__version__ = "0.3"
__url__ = "https://bitbucket.org/techtonik/fontquery"

class FontEntry:
    __doc__ = "\n    Font classification.\n    Level 0:\n    - name\n    - vector (True if font is vector, False for raster fonts)\n    - format: ttf | ...\n    "

    def __init__(self, name, vector, format, monospace, family):
        self.name = name
        self.vector = vector
        self.format = format
        self.monospace = monospace
        self.family = family


FONTDB = []
import ctypes
from ctypes import wintypes
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
CHAR = ctypes.c_char
TCHAR = CHAR
BYTE = ctypes.c_ubyte
ANSI_CHARSET = 0
ARABIC_CHARSET = 178
BALTIC_CHARSET = 186
CHINESEBIG5_CHARSET = 136
DEFAULT_CHARSET = 1
EASTEUROPE_CHARSET = 238
GB2312_CHARSET = 134
GREEK_CHARSET = 161
HANGUL_CHARSET = 129
HEBREW_CHARSET = 177
JOHAB_CHARSET = 130
MAC_CHARSET = 77
OEM_CHARSET = 255
RUSSIAN_CHARSET = 204
SHIFTJIS_CHARSET = 128
SYMBOL_CHARSET = 2
THAI_CHARSET = 222
TURKISH_CHARSET = 162
VIETNAMESE_CHARSET = 163
CHARSET_NAMES = {}
for name, value in locals().copy().items():
    if name.endswith("_CHARSET"):
        CHARSET_NAMES[value] = name

DEFAULT_PITCH = 0
FIXED_PITCH = 1
VARIABLE_PITCH = 2
FF_DONTCARE = 0
FF_ROMAN = 1
FF_SWISS = 2
FF_MODERN = 3
FF_SCRIPT = 4
FF_DECORATIVE = 5

class LOGFONT(ctypes.Structure):
    _fields_ = [
     (
      "lfHeight", wintypes.LONG),
     (
      "lfWidth", wintypes.LONG),
     (
      "lfEscapement", wintypes.LONG),
     (
      "lfOrientation", wintypes.LONG),
     (
      "lfWeight", wintypes.LONG),
     (
      "lfItalic", BYTE),
     (
      "lfUnderline", BYTE),
     (
      "lfStrikeOut", BYTE),
     (
      "lfCharSet", BYTE),
     (
      "lfOutPrecision", BYTE),
     (
      "lfClipPrecision", BYTE),
     (
      "lfQuality", BYTE),
     (
      "lfPitchAndFamily", BYTE),
     (
      "lfFaceName", TCHAR * 32)]


class FONTSIGNATURE(ctypes.Structure):
    _fields_ = [
     (
      "sUsb", wintypes.DWORD * 4),
     (
      "sCsb", wintypes.DWORD * 2)]


class NEWTEXTMETRIC(ctypes.Structure):
    _fields_ = [
     (
      "tmHeight", wintypes.LONG),
     (
      "tmAscent", wintypes.LONG),
     (
      "tmDescent", wintypes.LONG),
     (
      "tmInternalLeading", wintypes.LONG),
     (
      "tmExternalLeading", wintypes.LONG),
     (
      "tmAveCharWidth", wintypes.LONG),
     (
      "tmMaxCharWidth", wintypes.LONG),
     (
      "tmWeight", wintypes.LONG),
     (
      "tmOverhang", wintypes.LONG),
     (
      "tmDigitizedAspectX", wintypes.LONG),
     (
      "tmDigitizedAspectY", wintypes.LONG),
     (
      "mFirstChar", TCHAR),
     (
      "mLastChar", TCHAR),
     (
      "mDefaultChar", TCHAR),
     (
      "mBreakChar", TCHAR),
     (
      "tmItalic", BYTE),
     (
      "tmUnderlined", BYTE),
     (
      "tmStruckOut", BYTE),
     (
      "tmPitchAndFamily", BYTE),
     (
      "tmCharSet", BYTE),
     (
      "tmFlags", wintypes.DWORD),
     (
      "ntmSizeEM", wintypes.UINT),
     (
      "ntmCellHeight", wintypes.UINT),
     (
      "ntmAvgWidth", wintypes.UINT)]


class NEWTEXTMETRICEX(ctypes.Structure):
    _fields_ = [
     (
      "ntmTm", NEWTEXTMETRIC),
     (
      "ntmFontSig", FONTSIGNATURE)]


FONTENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.POINTER(LOGFONT), ctypes.POINTER(NEWTEXTMETRICEX), wintypes.DWORD, wintypes.LPARAM)
gdi32.EnumFontFamiliesExA.argtypes = [
 wintypes.HDC,
 ctypes.POINTER(LOGFONT),
 FONTENUMPROC,
 wintypes.LPARAM,
 wintypes.DWORD]

def _enum_font_names(logfont, textmetricex, fonttype, param):
    """callback function to be executed during EnumFontFamiliesEx
       call for each font name. it stores names in global variable
    """
    global FONTDB
    lf = logfont.contents
    name = lf.lfFaceName.decode("utf-8")
    if fonttype & 4:
        vector = True
        fmt = "ttf"
    else:
        vector = False
        fmt = "unknown"
    pitch = lf.lfPitchAndFamily & 3
    family = lf.lfPitchAndFamily >> 4
    monospace = pitch == FIXED_PITCH
    charset = lf.lfCharSet
    FONTDB.append(FontEntry(name, vector, fmt, monospace, family))
    if DEBUG:
        info = ""
        if pitch == FIXED_PITCH:
            info += "FP "
    elif pitch == VARIABLE_PITCH:
        info += "VP "
    else:
        info += "   "
    info += "%s " % {0:"U",  1:"R",  4:"T"}[fonttype]
    if monospace:
        info += "M  "
    else:
        info += "NM "
    style = [" "] * 3
    if lf.lfItalic:
        style[0] = "I"
    if lf.lfUnderline:
        style[1] = "U"
    if lf.lfStrikeOut:
        style[2] = "S"
    info += "".join(style)
    info += " %s" % lf.lfWeight
    print("%s CHARSET: %3s  %s" % (info, lf.lfCharSet, lf.lfFaceName))
    return 1


enum_font_names = FONTENUMPROC(_enum_font_names)

def query(charset=DEFAULT_CHARSET):
    """
    Prepare and call EnumFontFamiliesEx.

    query()
      - return tuple with sorted list of all available system fonts
    query(charset=ANSI_CHARSET)
      - return tuple sorted list of system fonts supporting ANSI charset

    """
    global FONTDB
    hdc = user32.GetDC(None)
    logfont = LOGFONT(0, 0, 0, 0, 0, 0, 0, 0, charset, 0, 0, 0, 0, b'\x00')
    FONTDB = []
    res = gdi32.EnumFontFamiliesExA(hdc, ctypes.byref(logfont), enum_font_names, 0, 0)
    user32.ReleaseDC(None, hdc)
    return FONTDB


def have_font(name, refresh=False):
    """
    Return True if font with specified `name` is present. The result
    of querying system font names is cached. Set `refresh` parameter
    to True to purge cache and reload font information.
    """
    if not FONTDB or refresh:
        query()
    if any(f.name == name for f in FONTDB):
        return True
    else:
        return False


def font_list(vector_only=False, monospace_only=False):
    """Return list of system installed font names."""
    if not FONTDB:
        query()
    else:
        fonts = FONTDB
        if vector_only:
            fonts = [f for f in fonts if f.vector]
        if monospace_only:
            fonts = [f for f in fonts if f.monospace]
    return sorted([f.name for f in fonts])


if __name__ == "__main__":
    import sys
    if sys.argv[1:] == ["debug"]:
        DEBUG = True
    if sys.argv[1:] == ["test"] or DEBUG:
        print("Running tests..")
        test_arial = have_font("Arial")
        print('Have font "Arial"? %s' % test_arial)
        print('Have font "missing-one"? %s' % have_font("missing-one"))
        FONTDB = [
         FontEntry("stub", False, "", False, FF_MODERN)]
        assert have_font("Arial") != test_arial
        assert have_font("Arial", refresh=True) == test_arial
        if not DEBUG:
            sys.exit()
    if sys.argv[1:] == ["vector"]:
        fonts = font_list(vector_only=True)
elif sys.argv[1:] == ["mono"]:
    fonts = font_list(monospace_only=True)
elif sys.argv[1:] == ["vector", "mono"]:
    fonts = font_list(vector_only=True, monospace_only=True)
else:
    fonts = font_list()
print("\n".join(fonts))
if DEBUG:
    print("Total: %s" % len(font_list()))
