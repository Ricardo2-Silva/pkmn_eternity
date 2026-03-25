# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\image\codecs\wic.py
import warnings
from pyglet.image import *
from pyglet.image.codecs import *
from pyglet import com
from pyglet.libs.win32.constants import *
from pyglet.libs.win32.types import *
from pyglet.libs.win32 import _kernel32 as kernel32
from pyglet.libs.win32 import _ole32 as ole32
CLSID_WICImagingFactory1 = com.GUID(3402297954, 37744, 17941, 161, 59, 159, 85, 57, 218, 76, 10)
CLSID_WICImagingFactory2 = com.GUID(830277352, 24356, 17213, 189, 247, 121, 206, 104, 216, 171, 194)
if WINDOWS_8_OR_GREATER:
    CLSID_WICImagingFactory = CLSID_WICImagingFactory2
else:
    CLSID_WICImagingFactory = CLSID_WICImagingFactory1
WICBitmapCreateCacheOption = UINT
WICBitmapNoCache = 0
WICBitmapCacheOnDemand = 1
WICBitmapCacheOnLoad = 2
WICBITMAPCREATECACHEOPTION_FORCE_DWORD = 2147483647
WICBitmapPaletteType = UINT
WICBitmapPaletteTypeCustom = 0
WICBitmapTransformOptions = UINT
WICBitmapTransformRotate0 = 0
WICBitmapTransformRotate90 = 1
WICBitmapTransformRotate180 = 2
WICBitmapTransformRotate270 = 3
WICBitmapTransformFlipHorizontal = 8
WICBitmapTransformFlipVertical = 16
WICBitmapDitherType = UINT
WICBitmapDitherTypeNone = 0
WICBitmapDitherTypeSolid = 0
WICBitmapDitherTypeOrdered4x4 = 1
WICBitmapDitherTypeOrdered8x8 = 2
WICBitmapDitherTypeOrdered16x16 = 3
WICBitmapDitherTypeSpiral4x4 = 4
WICBitmapDitherTypeSpiral8x8 = 5
WICBitmapDitherTypeDualSpiral4x4 = 6
WICBitmapDitherTypeDualSpiral8x8 = 7
WICBitmapDitherTypeErrorDiffusion = 8
WICBITMAPDITHERTYPE_FORCE_DWORD = 2147483647
WICBITMAPTRANSFORMOPTIONS_FORCE_DWORD = 2147483647
WICDecodeOptions = UINT
WICDecodeMetadataCacheOnDemand = 0
WICDecodeMetadataCacheOnLoad = 1
WICMETADATACACHEOPTION_FORCE_DWORD = 2147483647
REFWICPixelFormatGUID = com.GUID
GUID_WICPixelFormat1bppIndexed = com.GUID(1876804388, 19971, 19454, 177, 133, 61, 119, 118, 141, 201, 1)
GUID_WICPixelFormat2bppIndexed = com.GUID(1876804388, 19971, 19454, 177, 133, 61, 119, 118, 141, 201, 2)
GUID_WICPixelFormat4bppIndexed = com.GUID(1876804388, 19971, 19454, 177, 133, 61, 119, 118, 141, 201, 3)
GUID_WICPixelFormat8bppIndexed = com.GUID(1876804388, 19971, 19454, 177, 133, 61, 119, 118, 141, 201, 4)
GUID_WICPixelFormatBlackWhite = com.GUID(1876804388, 19971, 19454, 177, 133, 61, 119, 118, 141, 201, 5)
GUID_WICPixelFormat2bppGray = com.GUID(1876804388, 19971, 19454, 177, 133, 61, 119, 118, 141, 201, 6)
GUID_WICPixelFormat4bppGray = com.GUID(1876804388, 19971, 19454, 177, 133, 61, 119, 118, 141, 201, 7)
GUID_WICPixelFormat8bppGray = com.GUID(1876804388, 19971, 19454, 177, 133, 61, 119, 118, 141, 201, 8)
GUID_WICPixelFormat8bppAlpha = com.GUID(3872194838, 61114, 16737, 170, 133, 39, 221, 159, 179, 168, 149)
GUID_WICPixelFormat16bppBGR555 = com.GUID(1876804388, 19971, 19454, 177, 133, 61, 119, 118, 141, 201, 9)
GUID_WICPixelFormat16bppBGR565 = com.GUID(1876804388, 19971, 19454, 177, 133, 61, 119, 118, 141, 201, 10)
GUID_WICPixelFormat16bppBGRA5551 = com.GUID(99384363, 61926, 18785, 173, 70, 225, 204, 129, 10, 135, 210)
GUID_WICPixelFormat16bppGray = com.GUID(1876804388, 19971, 19454, 177, 133, 61, 119, 118, 141, 201, 11)
GUID_WICPixelFormat24bppBGR = com.GUID(1876804388, 19971, 19454, 177, 133, 61, 119, 118, 141, 201, 12)
GUID_WICPixelFormat24bppRGB = com.GUID(1876804388, 19971, 19454, 177, 133, 61, 119, 118, 141, 201, 13)
GUID_WICPixelFormat32bppBGR = com.GUID(1876804388, 19971, 19454, 177, 133, 61, 119, 118, 141, 201, 14)
GUID_WICPixelFormat32bppBGRA = com.GUID(1876804388, 19971, 19454, 177, 133, 61, 119, 118, 141, 201, 15)
GUID_WICPixelFormat32bppPBGRA = com.GUID(1876804388, 19971, 19454, 177, 133, 61, 119, 118, 141, 201, 16)
GUID_WICPixelFormat32bppRGB = com.GUID(3649858453, 16126, 18390, 187, 37, 235, 23, 72, 171, 12, 241)
GUID_WICPixelFormat32bppRGBA = com.GUID(4123503917, 27277, 17373, 167, 168, 162, 153, 53, 38, 26, 233)
GUID_WICPixelFormat32bppPRGBA = com.GUID(1019520592, 42279, 19767, 169, 22, 49, 66, 199, 235, 237, 186)
GUID_WICPixelFormat48bppRGB = com.GUID(1876804388, 19971, 19454, 177, 133, 61, 119, 118, 141, 201, 21)
GUID_WICPixelFormat48bppBGR = com.GUID(3859129220, 46184, 18126, 187, 46, 54, 241, 128, 230, 67, 19)

class IWICComponentInfo(com.pIUnknown):
    _methods_ = [
     (
      "GetComponentType",
      com.STDMETHOD()),
     (
      "GetCLSID",
      com.STDMETHOD()),
     (
      "GetSigningStatus",
      com.STDMETHOD()),
     (
      "GetAuthor",
      com.STDMETHOD()),
     (
      "GetVendorGUID",
      com.STDMETHOD()),
     (
      "GetVersion",
      com.STDMETHOD()),
     (
      "GetSpecVersion",
      com.STDMETHOD()),
     (
      "GetFriendlyName",
      com.STDMETHOD())]


class IWICPixelFormatInfo(IWICComponentInfo, com.pIUnknown):
    _methods_ = [
     (
      "GetFormatGUID",
      com.STDMETHOD(POINTER(com.GUID))),
     (
      "GetColorContext",
      com.STDMETHOD()),
     (
      "GetBitsPerPixel",
      com.STDMETHOD(POINTER(UINT))),
     (
      "GetChannelCount",
      com.STDMETHOD(POINTER(UINT))),
     (
      "GetChannelMask",
      com.STDMETHOD())]


class IWICBitmapSource(com.pIUnknown):
    _methods_ = [
     (
      "GetSize",
      com.STDMETHOD(POINTER(UINT), POINTER(UINT))),
     (
      "GetPixelFormat",
      com.STDMETHOD(POINTER(REFWICPixelFormatGUID))),
     (
      "GetResolution",
      com.STDMETHOD(POINTER(DOUBLE), POINTER(DOUBLE))),
     (
      "CopyPalette",
      com.STDMETHOD()),
     (
      "CopyPixels",
      com.STDMETHOD(c_void_p, UINT, UINT, c_void_p))]


class IWICFormatConverter(IWICBitmapSource, com.pIUnknown):
    _methods_ = [
     (
      "Initialize",
      com.STDMETHOD(IWICBitmapSource, POINTER(REFWICPixelFormatGUID), WICBitmapDitherType, c_void_p, DOUBLE, WICBitmapPaletteType)),
     (
      "CanConvert",
      com.STDMETHOD(POINTER(REFWICPixelFormatGUID), POINTER(REFWICPixelFormatGUID), POINTER(BOOL)))]


class IWICMetadataQueryReader(com.pIUnknown):
    _methods_ = [
     (
      "GetContainerFormat",
      com.STDMETHOD()),
     (
      "GetLocation",
      com.STDMETHOD()),
     (
      "GetMetadataByName",
      com.STDMETHOD(LPCWSTR, c_void_p)),
     (
      "GetEnumerator",
      com.STDMETHOD())]


class IWICBitmapFrameDecode(IWICBitmapSource, com.pIUnknown):
    _methods_ = [
     (
      "GetMetadataQueryReader",
      com.STDMETHOD(POINTER(IWICMetadataQueryReader))),
     (
      "GetColorContexts",
      com.STDMETHOD()),
     (
      "GetThumbnail",
      com.STDMETHOD(POINTER(IWICBitmapSource)))]


class IWICBitmapFlipRotator(IWICBitmapSource, com.pIUnknown):
    _methods_ = [
     (
      "Initialize",
      com.STDMETHOD(IWICBitmapSource, WICBitmapTransformOptions))]


class IWICBitmap(IWICBitmapSource, com.pIUnknown):
    _methods_ = [
     (
      "Lock",
      com.STDMETHOD()),
     (
      "SetPalette",
      com.STDMETHOD()),
     (
      "SetResolution",
      com.STDMETHOD())]


class IWICBitmapDecoder(com.pIUnknown):
    _methods_ = [
     (
      "QueryCapability",
      com.STDMETHOD()),
     (
      "Initialize",
      com.STDMETHOD()),
     (
      "GetContainerFormat",
      com.STDMETHOD()),
     (
      "GetDecoderInfo",
      com.STDMETHOD()),
     (
      "CopyPalette",
      com.STDMETHOD()),
     (
      "GetMetadataQueryReader",
      com.STDMETHOD(POINTER(IWICMetadataQueryReader))),
     (
      "GetPreview",
      com.STDMETHOD()),
     (
      "GetColorContexts",
      com.STDMETHOD()),
     (
      "GetThumbnail",
      com.STDMETHOD()),
     (
      "GetFrameCount",
      com.STDMETHOD(POINTER(UINT))),
     (
      "GetFrame",
      com.STDMETHOD(UINT, POINTER(IWICBitmapFrameDecode)))]


IID_IWICImagingFactory1 = com.GUID(3965634729, 50069, 17172, 156, 119, 84, 215, 169, 53, 255, 112)
IID_IWICImagingFactory2 = com.GUID(2072079173, 6550, 17526, 177, 50, 222, 158, 36, 124, 138, 240)
if WINDOWS_8_OR_GREATER:
    IID_IWICImagingFactory = IID_IWICImagingFactory2
else:
    IID_IWICImagingFactory = IID_IWICImagingFactory1
IID_IWICPixelFormatInfo = com.GUID(3907888641, 15688, 17178, 171, 68, 105, 5, 155, 232, 139, 190)

class IWICImagingFactory(com.pIUnknown):
    _methods_ = [
     (
      "CreateDecoderFromFilename",
      com.STDMETHOD(LPCWSTR, com.GUID, DWORD, WICDecodeOptions, POINTER(IWICBitmapDecoder))),
     (
      "CreateDecoderFromStream",
      com.STDMETHOD(com.pIUnknown, c_void_p, WICDecodeOptions, POINTER(IWICBitmapDecoder))),
     (
      "CreateDecoderFromFileHandle",
      com.STDMETHOD()),
     (
      "CreateComponentInfo",
      com.STDMETHOD(com.GUID, POINTER(IWICComponentInfo))),
     (
      "CreateDecoder",
      com.STDMETHOD()),
     (
      "CreateEncoder",
      com.STDMETHOD()),
     (
      "CreatePalette",
      com.STDMETHOD()),
     (
      "CreateFormatConverter",
      com.STDMETHOD(POINTER(IWICFormatConverter))),
     (
      "CreateBitmapScaler",
      com.STDMETHOD()),
     (
      "CreateBitmapClipper",
      com.STDMETHOD()),
     (
      "CreateBitmapFlipRotator",
      com.STDMETHOD(POINTER(IWICBitmapFlipRotator))),
     (
      "CreateStream",
      com.STDMETHOD()),
     (
      "CreateColorContext",
      com.STDMETHOD()),
     (
      "CreateColorTransformer",
      com.STDMETHOD()),
     (
      "CreateBitmap",
      com.STDMETHOD(UINT, UINT, POINTER(REFWICPixelFormatGUID), WICBitmapCreateCacheOption, POINTER(IWICBitmap))),
     (
      "CreateBitmapFromSource",
      com.STDMETHOD()),
     (
      "CreateBitmapFromSourceRect",
      com.STDMETHOD()),
     (
      "CreateBitmapFromMemory",
      com.STDMETHOD()),
     (
      "CreateBitmapFromHBITMAP",
      com.STDMETHOD()),
     (
      "CreateBitmapFromHICON",
      com.STDMETHOD()),
     (
      "CreateComponentEnumerator",
      com.STDMETHOD()),
     (
      "CreateFastMetadataEncoderFromDecoder",
      com.STDMETHOD()),
     (
      "CreateFastMetadataEncoderFromFrameDecode",
      com.STDMETHOD()),
     (
      "CreateQueryWriter",
      com.STDMETHOD()),
     (
      "CreateQueryWriterFromReader",
      com.STDMETHOD())]


class WICDecoder(ImageDecoder):
    __doc__ = "Windows Imaging Component.\n    This decoder is a replacement for GDI and GDI+ starting with Windows 7 with more features up to Windows 10."

    def __init__(self):
        super(ImageDecoder, self).__init__()
        self._factory = IWICImagingFactory()
        try:
            ole32.CoInitializeEx(None, COINIT_MULTITHREADED)
        except OSError as err:
            warnings.warn(str(err))

        ole32.CoCreateInstance(CLSID_WICImagingFactory, None, CLSCTX_INPROC_SERVER, IID_IWICImagingFactory, byref(self._factory))

    def get_file_extensions(self):
        return [
         '.bmp', '.jpg', '.jpeg', '.png', '.tif', '.tiff', 
         '.ico', '.jxr', '.hdp', '.wdp']

    def _load_bitmap_decoder(self, file, filename):
        data = file.read()
        hglob = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(data))
        ptr = kernel32.GlobalLock(hglob)
        memmove(ptr, data, len(data))
        kernel32.GlobalUnlock(hglob)
        stream = com.pIUnknown()
        ole32.CreateStreamOnHGlobal(hglob, True, byref(stream))
        decoder = IWICBitmapDecoder()
        status = self._factory.CreateDecoderFromStream(stream, None, WICDecodeMetadataCacheOnDemand, byref(decoder))
        if status != 0:
            stream.Release()
            raise ImageDecodeException("WIC cannot load %r" % (filename or file))
        return (decoder, stream)

    def _get_bitmap_frame(self, bitmap_decoder, frame_index):
        bitmap = IWICBitmapFrameDecode()
        bitmap_decoder.GetFrame(frame_index, byref(bitmap))
        return bitmap

    def get_image(self, bitmap, target_fmt=GUID_WICPixelFormat32bppBGRA):
        """Get's image from bitmap, specifying target format, bitmap is released before returning."""
        width = UINT()
        height = UINT()
        bitmap.GetSize(byref(width), byref(height))
        width = int(width.value)
        height = int(height.value)
        pf = com.GUID(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        bitmap.GetPixelFormat(byref(pf))
        fmt = "BGRA"
        if pf != target_fmt:
            converter = IWICFormatConverter()
            self._factory.CreateFormatConverter(byref(converter))
            conversion_possible = BOOL()
            converter.CanConvert(pf, target_fmt, byref(conversion_possible))
            if not conversion_possible:
                target_fmt = GUID_WICPixelFormat24bppBGR
                fmt = "BGR"
            converter.Initialize(bitmap, target_fmt, WICBitmapDitherTypeNone, None, 0, WICBitmapPaletteTypeCustom)
            bitmap.Release()
            bitmap = converter
        flipper = IWICBitmapFlipRotator()
        self._factory.CreateBitmapFlipRotator(byref(flipper))
        flipper.Initialize(bitmap, WICBitmapTransformFlipVertical)
        stride = len(fmt) * width
        buffer_size = stride * height
        buffer = BYTE * buffer_size()
        flipper.CopyPixels(None, stride, buffer_size, byref(buffer))
        flipper.Release()
        bitmap.Release()
        return ImageData(width, height, fmt, buffer)

    def _delete_bitmap_decoder(self, bitmap_decoder, stream):
        bitmap_decoder.Release()
        stream.Release()

    def decode(self, file, filename):
        bitmap_decoder, stream = self._load_bitmap_decoder(file, filename)
        bitmap = self._get_bitmap_frame(bitmap_decoder, 0)
        image = self.get_image(bitmap)
        self._delete_bitmap_decoder(bitmap_decoder, stream)
        return image

    @staticmethod
    def get_property_value(reader, metadata_name):
        """
            Uses a metadata name and reader to return a single value. Can be used to get metadata from images.
            If failure, returns 0.
            Also handles cleanup of PROPVARIANT.
        """
        try:
            prop = PROPVARIANT()
            reader.GetMetadataByName(metadata_name, byref(prop))
            value = prop.llVal
            ole32.PropVariantClear(byref(prop))
        except OSError:
            value = 0

        return value


def get_decoders():
    return [
     WICDecoder()]


def get_encoders():
    return []
