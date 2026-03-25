# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\libs\win32\types.py
import sys, ctypes
from ctypes import *
from ctypes.wintypes import *
_int_types = (
 c_int16, c_int32)
if hasattr(ctypes, "c_int64"):
    _int_types += (c_int64,)
for t in _int_types:
    if sizeof(t) == sizeof(c_size_t):
        c_ptrdiff_t = t

del t
del _int_types
if sys.version_info < (3, 2)[:2]:
    PUINT = POINTER(UINT)

class c_void(Structure):
    _fields_ = [
     (
      "dummy", c_int)]


def POINTER_(obj):
    p = ctypes.POINTER(obj)
    if not isinstance(p.from_param, classmethod):

        def from_param(cls, x):
            if x is None:
                return cls()
            else:
                return x

        p.from_param = classmethod(from_param)
    return p


c_void_p = POINTER_(c_void)
INT = c_int
LPVOID = c_void_p
HCURSOR = HANDLE
LRESULT = LPARAM
COLORREF = DWORD
PVOID = c_void_p
WCHAR = c_wchar
BCHAR = c_wchar
LPRECT = POINTER(RECT)
LPPOINT = POINTER(POINT)
LPMSG = POINTER(MSG)
UINT_PTR = HANDLE
LONG_PTR = HANDLE
HDROP = HANDLE
LPTSTR = LPWSTR
LPSTREAM = c_void_p
LF_FACESIZE = 32
CCHDEVICENAME = 32
CCHFORMNAME = 32
WNDPROC = WINFUNCTYPE(LRESULT, HWND, UINT, WPARAM, LPARAM)
TIMERPROC = WINFUNCTYPE(None, HWND, UINT, POINTER(UINT), DWORD)
TIMERAPCPROC = WINFUNCTYPE(None, PVOID, DWORD, DWORD)
MONITORENUMPROC = WINFUNCTYPE(BOOL, HMONITOR, HDC, LPRECT, LPARAM)

def MAKEINTRESOURCE(i):
    return cast(ctypes.c_void_p(i & 65535), c_wchar_p)


class WNDCLASS(Structure):
    _fields_ = [
     (
      "style", UINT),
     (
      "lpfnWndProc", WNDPROC),
     (
      "cbClsExtra", c_int),
     (
      "cbWndExtra", c_int),
     (
      "hInstance", HINSTANCE),
     (
      "hIcon", HICON),
     (
      "hCursor", HCURSOR),
     (
      "hbrBackground", HBRUSH),
     (
      "lpszMenuName", c_char_p),
     (
      "lpszClassName", c_wchar_p)]


class SECURITY_ATTRIBUTES(Structure):
    _fields_ = [
     (
      "nLength", DWORD),
     (
      "lpSecurityDescriptor", c_void_p),
     (
      "bInheritHandle", BOOL)]
    __slots__ = [f[0] for f in _fields_]


class PIXELFORMATDESCRIPTOR(Structure):
    _fields_ = [
     (
      "nSize", WORD),
     (
      "nVersion", WORD),
     (
      "dwFlags", DWORD),
     (
      "iPixelType", BYTE),
     (
      "cColorBits", BYTE),
     (
      "cRedBits", BYTE),
     (
      "cRedShift", BYTE),
     (
      "cGreenBits", BYTE),
     (
      "cGreenShift", BYTE),
     (
      "cBlueBits", BYTE),
     (
      "cBlueShift", BYTE),
     (
      "cAlphaBits", BYTE),
     (
      "cAlphaShift", BYTE),
     (
      "cAccumBits", BYTE),
     (
      "cAccumRedBits", BYTE),
     (
      "cAccumGreenBits", BYTE),
     (
      "cAccumBlueBits", BYTE),
     (
      "cAccumAlphaBits", BYTE),
     (
      "cDepthBits", BYTE),
     (
      "cStencilBits", BYTE),
     (
      "cAuxBuffers", BYTE),
     (
      "iLayerType", BYTE),
     (
      "bReserved", BYTE),
     (
      "dwLayerMask", DWORD),
     (
      "dwVisibleMask", DWORD),
     (
      "dwDamageMask", DWORD)]


class RGBQUAD(Structure):
    _fields_ = [
     (
      "rgbBlue", BYTE),
     (
      "rgbGreen", BYTE),
     (
      "rgbRed", BYTE),
     (
      "rgbReserved", BYTE)]
    __slots__ = [f[0] for f in _fields_]


class CIEXYZ(Structure):
    _fields_ = [
     (
      "ciexyzX", DWORD),
     (
      "ciexyzY", DWORD),
     (
      "ciexyzZ", DWORD)]
    __slots__ = [f[0] for f in _fields_]


class CIEXYZTRIPLE(Structure):
    _fields_ = [
     (
      "ciexyzRed", CIEXYZ),
     (
      "ciexyzBlue", CIEXYZ),
     (
      "ciexyzGreen", CIEXYZ)]
    __slots__ = [f[0] for f in _fields_]


class BITMAPINFOHEADER(Structure):
    _fields_ = [
     (
      "biSize", DWORD),
     (
      "biWidth", LONG),
     (
      "biHeight", LONG),
     (
      "biPlanes", WORD),
     (
      "biBitCount", WORD),
     (
      "biCompression", DWORD),
     (
      "biSizeImage", DWORD),
     (
      "biXPelsPerMeter", LONG),
     (
      "biYPelsPerMeter", LONG),
     (
      "biClrUsed", DWORD),
     (
      "biClrImportant", DWORD)]


class BITMAPV5HEADER(Structure):
    _fields_ = [
     (
      "bV5Size", DWORD),
     (
      "bV5Width", LONG),
     (
      "bV5Height", LONG),
     (
      "bV5Planes", WORD),
     (
      "bV5BitCount", WORD),
     (
      "bV5Compression", DWORD),
     (
      "bV5SizeImage", DWORD),
     (
      "bV5XPelsPerMeter", LONG),
     (
      "bV5YPelsPerMeter", LONG),
     (
      "bV5ClrUsed", DWORD),
     (
      "bV5ClrImportant", DWORD),
     (
      "bV5RedMask", DWORD),
     (
      "bV5GreenMask", DWORD),
     (
      "bV5BlueMask", DWORD),
     (
      "bV5AlphaMask", DWORD),
     (
      "bV5CSType", DWORD),
     (
      "bV5Endpoints", CIEXYZTRIPLE),
     (
      "bV5GammaRed", DWORD),
     (
      "bV5GammaGreen", DWORD),
     (
      "bV5GammaBlue", DWORD),
     (
      "bV5Intent", DWORD),
     (
      "bV5ProfileData", DWORD),
     (
      "bV5ProfileSize", DWORD),
     (
      "bV5Reserved", DWORD)]


class BITMAPINFO(Structure):
    _fields_ = [
     (
      "bmiHeader", BITMAPINFOHEADER),
     (
      "bmiColors", RGBQUAD * 1)]
    __slots__ = [f[0] for f in _fields_]


class LOGFONT(Structure):
    _fields_ = [
     (
      "lfHeight", LONG),
     (
      "lfWidth", LONG),
     (
      "lfEscapement", LONG),
     (
      "lfOrientation", LONG),
     (
      "lfWeight", LONG),
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
      "lfFaceName", c_char * LF_FACESIZE)]


class TRACKMOUSEEVENT(Structure):
    _fields_ = [
     (
      "cbSize", DWORD),
     (
      "dwFlags", DWORD),
     (
      "hwndTrack", HWND),
     (
      "dwHoverTime", DWORD)]
    __slots__ = [f[0] for f in _fields_]


class MINMAXINFO(Structure):
    _fields_ = [
     (
      "ptReserved", POINT),
     (
      "ptMaxSize", POINT),
     (
      "ptMaxPosition", POINT),
     (
      "ptMinTrackSize", POINT),
     (
      "ptMaxTrackSize", POINT)]
    __slots__ = [f[0] for f in _fields_]


class ABC(Structure):
    _fields_ = [
     (
      "abcA", c_int),
     (
      "abcB", c_uint),
     (
      "abcC", c_int)]
    __slots__ = [f[0] for f in _fields_]


class TEXTMETRIC(Structure):
    _fields_ = [
     (
      "tmHeight", c_long),
     (
      "tmAscent", c_long),
     (
      "tmDescent", c_long),
     (
      "tmInternalLeading", c_long),
     (
      "tmExternalLeading", c_long),
     (
      "tmAveCharWidth", c_long),
     (
      "tmMaxCharWidth", c_long),
     (
      "tmWeight", c_long),
     (
      "tmOverhang", c_long),
     (
      "tmDigitizedAspectX", c_long),
     (
      "tmDigitizedAspectY", c_long),
     (
      "tmFirstChar", c_char),
     (
      "tmLastChar", c_char),
     (
      "tmDefaultChar", c_char),
     (
      "tmBreakChar", c_char),
     (
      "tmItalic", c_byte),
     (
      "tmUnderlined", c_byte),
     (
      "tmStruckOut", c_byte),
     (
      "tmPitchAndFamily", c_byte),
     (
      "tmCharSet", c_byte)]
    __slots__ = [f[0] for f in _fields_]


class MONITORINFOEX(Structure):
    _fields_ = [
     (
      "cbSize", DWORD),
     (
      "rcMonitor", RECT),
     (
      "rcWork", RECT),
     (
      "dwFlags", DWORD),
     (
      "szDevice", WCHAR * CCHDEVICENAME)]
    __slots__ = [f[0] for f in _fields_]


class _DUMMYSTRUCTNAME(Structure):
    _fields_ = [
     (
      "dmOrientation", c_short),
     (
      "dmPaperSize", c_short),
     (
      "dmPaperLength", c_short),
     (
      "dmPaperWidth", c_short),
     (
      "dmScale", c_short),
     (
      "dmCopies", c_short),
     (
      "dmDefaultSource", c_short),
     (
      "dmPrintQuality", c_short)]


class _DUMMYSTRUCTNAME2(Structure):
    _fields_ = [
     (
      "dmPosition", POINTL),
     (
      "dmDisplayOrientation", DWORD),
     (
      "dmDisplayFixedOutput", DWORD)]


class _DUMMYDEVUNION(Union):
    _anonymous_ = ('_dummystruct1', '_dummystruct2')
    _fields_ = [
     (
      "_dummystruct1", _DUMMYSTRUCTNAME),
     (
      "dmPosition", POINTL),
     (
      "_dummystruct2", _DUMMYSTRUCTNAME2)]


class DEVMODE(Structure):
    _anonymous_ = ('_dummyUnion', )
    _fields_ = [
     (
      "dmDeviceName", BCHAR * CCHDEVICENAME),
     (
      "dmSpecVersion", WORD),
     (
      "dmDriverVersion", WORD),
     (
      "dmSize", WORD),
     (
      "dmDriverExtra", WORD),
     (
      "dmFields", DWORD),
     (
      "_dummyUnion", _DUMMYDEVUNION),
     (
      "dmColor", c_short),
     (
      "dmDuplex", c_short),
     (
      "dmYResolution", c_short),
     (
      "dmTTOption", c_short),
     (
      "dmCollate", c_short),
     (
      "dmFormName", BCHAR * CCHFORMNAME),
     (
      "dmLogPixels", WORD),
     (
      "dmBitsPerPel", DWORD),
     (
      "dmPelsWidth", DWORD),
     (
      "dmPelsHeight", DWORD),
     (
      "dmDisplayFlags", DWORD),
     (
      "dmDisplayFrequency", DWORD),
     (
      "dmICMMethod", DWORD),
     (
      "dmICMIntent", DWORD),
     (
      "dmDitherType", DWORD),
     (
      "dmReserved1", DWORD),
     (
      "dmReserved2", DWORD),
     (
      "dmPanningWidth", DWORD),
     (
      "dmPanningHeight", DWORD)]


class ICONINFO(Structure):
    _fields_ = [
     (
      "fIcon", BOOL),
     (
      "xHotspot", DWORD),
     (
      "yHotspot", DWORD),
     (
      "hbmMask", HBITMAP),
     (
      "hbmColor", HBITMAP)]
    __slots__ = [f[0] for f in _fields_]


class RAWINPUTDEVICE(Structure):
    _fields_ = [
     (
      "usUsagePage", USHORT),
     (
      "usUsage", USHORT),
     (
      "dwFlags", DWORD),
     (
      "hwndTarget", HWND)]


PCRAWINPUTDEVICE = POINTER(RAWINPUTDEVICE)
HRAWINPUT = HANDLE

class RAWINPUTHEADER(Structure):
    _fields_ = [
     (
      "dwType", DWORD),
     (
      "dwSize", DWORD),
     (
      "hDevice", HANDLE),
     (
      "wParam", WPARAM)]


class _Buttons(Structure):
    _fields_ = [
     (
      "usButtonFlags", USHORT),
     (
      "usButtonData", USHORT)]


class _U(Union):
    _anonymous_ = ('_buttons', )
    _fields_ = [
     (
      "ulButtons", ULONG),
     (
      "_buttons", _Buttons)]


class RAWMOUSE(Structure):
    _anonymous_ = ('u', )
    _fields_ = [
     (
      "usFlags", USHORT),
     (
      "u", _U),
     (
      "ulRawButtons", ULONG),
     (
      "lLastX", LONG),
     (
      "lLastY", LONG),
     (
      "ulExtraInformation", ULONG)]


class RAWKEYBOARD(Structure):
    _fields_ = [
     (
      "MakeCode", USHORT),
     (
      "Flags", USHORT),
     (
      "Reserved", USHORT),
     (
      "VKey", USHORT),
     (
      "Message", UINT),
     (
      "ExtraInformation", ULONG)]


class RAWHID(Structure):
    _fields_ = [
     (
      "dwSizeHid", DWORD),
     (
      "dwCount", DWORD),
     (
      "bRawData", POINTER(BYTE))]


class _RAWINPUTDEVICEUNION(Union):
    _fields_ = [
     (
      "mouse", RAWMOUSE),
     (
      "keyboard", RAWKEYBOARD),
     (
      "hid", RAWHID)]


class RAWINPUT(Structure):
    _fields_ = [
     (
      "header", RAWINPUTHEADER),
     (
      "data", _RAWINPUTDEVICEUNION)]


class _VarTable(ctypes.Union):
    __doc__ = "Must be in an anonymous union or values will not work across various VT's."
    _fields_ = [
     (
      "llVal", ctypes.c_longlong),
     (
      "pwszVal", LPWSTR)]


class PROPVARIANT(ctypes.Structure):
    _anonymous_ = [
     "union"]
    _fields_ = [
     (
      "vt", ctypes.c_ushort),
     (
      "wReserved1", ctypes.c_ubyte),
     (
      "wReserved2", ctypes.c_ubyte),
     (
      "wReserved3", ctypes.c_ulong),
     (
      "union", _VarTable)]
