# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\libs\darwin\cocoapy\cocoalibs.py
from ctypes import *
from ctypes import util
from .runtime import send_message, ObjCInstance
from .cocoatypes import *
lib = util.find_library("CoreFoundation")
if lib is None:
    lib = "/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation"
cf = cdll.LoadLibrary(lib)
kCFStringEncodingUTF8 = 134217984
CFAllocatorRef = c_void_p
CFStringEncoding = c_uint32
cf.CFStringCreateWithCString.restype = c_void_p
cf.CFStringCreateWithCString.argtypes = [CFAllocatorRef, c_char_p, CFStringEncoding]
cf.CFRelease.restype = c_void_p
cf.CFRelease.argtypes = [c_void_p]
cf.CFStringGetLength.restype = CFIndex
cf.CFStringGetLength.argtypes = [c_void_p]
cf.CFStringGetMaximumSizeForEncoding.restype = CFIndex
cf.CFStringGetMaximumSizeForEncoding.argtypes = [CFIndex, CFStringEncoding]
cf.CFStringGetCString.restype = c_bool
cf.CFStringGetCString.argtypes = [c_void_p, c_char_p, CFIndex, CFStringEncoding]
cf.CFStringGetTypeID.restype = CFTypeID
cf.CFStringGetTypeID.argtypes = []
cf.CFAttributedStringCreate.restype = c_void_p
cf.CFAttributedStringCreate.argtypes = [CFAllocatorRef, c_void_p, c_void_p]

def CFSTR(string):
    return ObjCInstance(c_void_p(cf.CFStringCreateWithCString(None, string.encode("utf8"), kCFStringEncodingUTF8)))


def get_NSString(string):
    """Autoreleased version of CFSTR"""
    return CFSTR(string).autorelease()


def cfstring_to_string(cfstring):
    length = cf.CFStringGetLength(cfstring)
    size = cf.CFStringGetMaximumSizeForEncoding(length, kCFStringEncodingUTF8)
    buffer = c_buffer(size + 1)
    result = cf.CFStringGetCString(cfstring, buffer, len(buffer), kCFStringEncodingUTF8)
    if result:
        return str(buffer.value, "utf-8")


cf.CFDataCreate.restype = c_void_p
cf.CFDataCreate.argtypes = [c_void_p, c_void_p, CFIndex]
cf.CFDataGetBytes.restype = None
cf.CFDataGetBytes.argtypes = [c_void_p, CFRange, c_void_p]
cf.CFDataGetLength.restype = CFIndex
cf.CFDataGetLength.argtypes = [c_void_p]
cf.CFDictionaryGetValue.restype = c_void_p
cf.CFDictionaryGetValue.argtypes = [c_void_p, c_void_p]
cf.CFDictionaryAddValue.restype = None
cf.CFDictionaryAddValue.argtypes = [c_void_p, c_void_p, c_void_p]
cf.CFDictionaryCreateMutable.restype = c_void_p
cf.CFDictionaryCreateMutable.argtypes = [CFAllocatorRef, CFIndex, c_void_p, c_void_p]
cf.CFNumberCreate.restype = c_void_p
cf.CFNumberCreate.argtypes = [CFAllocatorRef, CFNumberType, c_void_p]
cf.CFNumberGetType.restype = CFNumberType
cf.CFNumberGetType.argtypes = [c_void_p]
cf.CFNumberGetValue.restype = c_ubyte
cf.CFNumberGetValue.argtypes = [c_void_p, CFNumberType, c_void_p]
cf.CFNumberGetTypeID.restype = CFTypeID
cf.CFNumberGetTypeID.argtypes = []
cf.CFGetTypeID.restype = CFTypeID
cf.CFGetTypeID.argtypes = [c_void_p]
kCFNumberSInt8Type = 1
kCFNumberSInt16Type = 2
kCFNumberSInt32Type = 3
kCFNumberSInt64Type = 4
kCFNumberFloat32Type = 5
kCFNumberFloat64Type = 6
kCFNumberCharType = 7
kCFNumberShortType = 8
kCFNumberIntType = 9
kCFNumberLongType = 10
kCFNumberLongLongType = 11
kCFNumberFloatType = 12
kCFNumberDoubleType = 13
kCFNumberCFIndexType = 14
kCFNumberNSIntegerType = 15
kCFNumberCGFloatType = 16
kCFNumberMaxType = 16

def cfnumber_to_number(cfnumber):
    """Convert CFNumber to python int or float."""
    numeric_type = cf.CFNumberGetType(cfnumber)
    cfnum_to_ctype = {kCFNumberSInt8Type: c_int8, kCFNumberSInt16Type: c_int16, 
     kCFNumberSInt32Type: c_int32, kCFNumberSInt64Type: c_int64, 
     kCFNumberFloat32Type: c_float, kCFNumberFloat64Type: c_double, 
     kCFNumberCharType: c_byte, kCFNumberShortType: c_short, 
     kCFNumberIntType: c_int, kCFNumberLongType: c_long, 
     kCFNumberLongLongType: c_longlong, kCFNumberFloatType: c_float, 
     kCFNumberDoubleType: c_double, kCFNumberCFIndexType: CFIndex, 
     kCFNumberCGFloatType: CGFloat}
    if numeric_type in cfnum_to_ctype:
        t = cfnum_to_ctype[numeric_type]
        result = t()
        if cf.CFNumberGetValue(cfnumber, numeric_type, byref(result)):
            return result.value
    else:
        raise Exception("cfnumber_to_number: unhandled CFNumber type %d" % numeric_type)


known_cftypes = {(cf.CFStringGetTypeID()): cfstring_to_string, 
 (cf.CFNumberGetTypeID()): cfnumber_to_number}

def cftype_to_value(cftype):
    """Convert a CFType into an equivalent python type.
    The convertible CFTypes are taken from the known_cftypes
    dictionary, which may be added to if another library implements
    its own conversion methods."""
    if not cftype:
        return
    else:
        typeID = cf.CFGetTypeID(cftype)
        if typeID in known_cftypes:
            convert_function = known_cftypes[typeID]
            return convert_function(cftype)
        return cftype


cf.CFSetGetCount.restype = CFIndex
cf.CFSetGetCount.argtypes = [c_void_p]
cf.CFSetGetValues.restype = None
cf.CFSetGetValues.argtypes = [
 c_void_p, c_void_p]

def cfset_to_set(cfset):
    """Convert CFSet to python set."""
    count = cf.CFSetGetCount(cfset)
    buffer = c_void_p * count()
    cf.CFSetGetValues(cfset, byref(buffer))
    return set([cftype_to_value(c_void_p(buffer[i])) for i in range(count)])


cf.CFArrayGetCount.restype = CFIndex
cf.CFArrayGetCount.argtypes = [c_void_p]
cf.CFArrayGetValueAtIndex.restype = c_void_p
cf.CFArrayGetValueAtIndex.argtypes = [c_void_p, CFIndex]

def cfarray_to_list(cfarray):
    """Convert CFArray to python list."""
    count = cf.CFArrayGetCount(cfarray)
    return [cftype_to_value(c_void_p(cf.CFArrayGetValueAtIndex(cfarray, i))) for i in range(count)]


kCFRunLoopDefaultMode = c_void_p.in_dll(cf, "kCFRunLoopDefaultMode")
cf.CFRunLoopGetCurrent.restype = c_void_p
cf.CFRunLoopGetCurrent.argtypes = []
cf.CFRunLoopGetMain.restype = c_void_p
cf.CFRunLoopGetMain.argtypes = []
lib = util.find_library("AppKit")
if lib is None:
    lib = "/System/Library/Frameworks/AppKit.framework/AppKit"
appkit = cdll.LoadLibrary(lib)
NSDefaultRunLoopMode = c_void_p.in_dll(appkit, "NSDefaultRunLoopMode")
NSEventTrackingRunLoopMode = c_void_p.in_dll(appkit, "NSEventTrackingRunLoopMode")
NSApplicationDidHideNotification = c_void_p.in_dll(appkit, "NSApplicationDidHideNotification")
NSApplicationDidUnhideNotification = c_void_p.in_dll(appkit, "NSApplicationDidUnhideNotification")
NSAnyEventMask = 4294967295
NSKeyDown = 10
NSKeyUp = 11
NSFlagsChanged = 12
NSApplicationDefined = 15
NSAlphaShiftKeyMask = 65536
NSShiftKeyMask = 131072
NSControlKeyMask = 262144
NSAlternateKeyMask = 524288
NSCommandKeyMask = 1048576
NSNumericPadKeyMask = 2097152
NSHelpKeyMask = 4194304
NSFunctionKeyMask = 8388608
NSInsertFunctionKey = 63271
NSDeleteFunctionKey = 63272
NSHomeFunctionKey = 63273
NSBeginFunctionKey = 63274
NSEndFunctionKey = 63275
NSPageUpFunctionKey = 63276
NSPageDownFunctionKey = 63277
NSBorderlessWindowMask = 0
NSTitledWindowMask = 1
NSClosableWindowMask = 2
NSMiniaturizableWindowMask = 4
NSResizableWindowMask = 8
NSUtilityWindowMask = 16
NSBackingStoreRetained = 0
NSBackingStoreNonretained = 1
NSBackingStoreBuffered = 2
NSTrackingMouseEnteredAndExited = 1
NSTrackingMouseMoved = 2
NSTrackingCursorUpdate = 4
NSTrackingActiveInActiveApp = 64
NSOpenGLPFAAllRenderers = 1
NSOpenGLPFADoubleBuffer = 5
NSOpenGLPFAStereo = 6
NSOpenGLPFAAuxBuffers = 7
NSOpenGLPFAColorSize = 8
NSOpenGLPFAAlphaSize = 11
NSOpenGLPFADepthSize = 12
NSOpenGLPFAStencilSize = 13
NSOpenGLPFAAccumSize = 14
NSOpenGLPFAMinimumPolicy = 51
NSOpenGLPFAMaximumPolicy = 52
NSOpenGLPFAOffScreen = 53
NSOpenGLPFAFullScreen = 54
NSOpenGLPFASampleBuffers = 55
NSOpenGLPFASamples = 56
NSOpenGLPFAAuxDepthStencil = 57
NSOpenGLPFAColorFloat = 58
NSOpenGLPFAMultisample = 59
NSOpenGLPFASupersample = 60
NSOpenGLPFASampleAlpha = 61
NSOpenGLPFARendererID = 70
NSOpenGLPFASingleRenderer = 71
NSOpenGLPFANoRecovery = 72
NSOpenGLPFAAccelerated = 73
NSOpenGLPFAClosestPolicy = 74
NSOpenGLPFARobust = 75
NSOpenGLPFABackingStore = 76
NSOpenGLPFAMPSafe = 78
NSOpenGLPFAWindow = 80
NSOpenGLPFAMultiScreen = 81
NSOpenGLPFACompliant = 83
NSOpenGLPFAScreenMask = 84
NSOpenGLPFAPixelBuffer = 90
NSOpenGLPFARemotePixelBuffer = 91
NSOpenGLPFAAllowOfflineRenderers = 96
NSOpenGLPFAAcceleratedCompute = 97
NSOpenGLPFAOpenGLProfile = 99
NSOpenGLPFAVirtualScreenCount = 128
NSOpenGLProfileVersionLegacy = 4096
NSOpenGLProfileVersion3_2Core = 12800
NSOpenGLProfileVersion4_1Core = 16640
NSOpenGLCPSwapInterval = 222
kCGImageAlphaNone = 0
kCGImageAlphaPremultipliedLast = 1
kCGImageAlphaPremultipliedFirst = 2
kCGImageAlphaLast = 3
kCGImageAlphaFirst = 4
kCGImageAlphaNoneSkipLast = 5
kCGImageAlphaNoneSkipFirst = 6
kCGImageAlphaOnly = 7
kCGImageAlphaPremultipliedLast = 1
kCGBitmapAlphaInfoMask = 31
kCGBitmapFloatComponents = 256
kCGBitmapByteOrderMask = 28672
kCGBitmapByteOrderDefault = 0
kCGBitmapByteOrder16Little = 4096
kCGBitmapByteOrder32Little = 8192
kCGBitmapByteOrder16Big = 12288
kCGBitmapByteOrder32Big = 16384
NSApplicationPresentationDefault = 0
NSApplicationPresentationHideDock = 2
NSApplicationPresentationHideMenuBar = 8
NSApplicationPresentationDisableProcessSwitching = 32
NSApplicationPresentationDisableHideApplication = 256
NSApplicationActivationPolicyRegular = 0
NSApplicationActivationPolicyAccessory = 1
NSApplicationActivationPolicyProhibited = 2
lib = util.find_library("Quartz")
if lib is None:
    lib = "/System/Library/Frameworks/Quartz.framework/Quartz"
quartz = cdll.LoadLibrary(lib)
CGDirectDisplayID = c_uint32
CGError = c_int32
CGBitmapInfo = c_uint32
kCGImagePropertyGIFDictionary = c_void_p.in_dll(quartz, "kCGImagePropertyGIFDictionary")
kCGImagePropertyGIFDelayTime = c_void_p.in_dll(quartz, "kCGImagePropertyGIFDelayTime")
kCGRenderingIntentDefault = 0
quartz.CGDisplayIDToOpenGLDisplayMask.restype = c_uint32
quartz.CGDisplayIDToOpenGLDisplayMask.argtypes = [c_uint32]
quartz.CGMainDisplayID.restype = CGDirectDisplayID
quartz.CGMainDisplayID.argtypes = []
quartz.CGShieldingWindowLevel.restype = c_int32
quartz.CGShieldingWindowLevel.argtypes = []
quartz.CGCursorIsVisible.restype = c_bool
quartz.CGDisplayCopyAllDisplayModes.restype = c_void_p
quartz.CGDisplayCopyAllDisplayModes.argtypes = [CGDirectDisplayID, c_void_p]
quartz.CGDisplaySetDisplayMode.restype = CGError
quartz.CGDisplaySetDisplayMode.argtypes = [CGDirectDisplayID, c_void_p, c_void_p]
quartz.CGDisplayCapture.restype = CGError
quartz.CGDisplayCapture.argtypes = [CGDirectDisplayID]
quartz.CGDisplayRelease.restype = CGError
quartz.CGDisplayRelease.argtypes = [CGDirectDisplayID]
quartz.CGDisplayCopyDisplayMode.restype = c_void_p
quartz.CGDisplayCopyDisplayMode.argtypes = [CGDirectDisplayID]
quartz.CGDisplayModeGetRefreshRate.restype = c_double
quartz.CGDisplayModeGetRefreshRate.argtypes = [c_void_p]
quartz.CGDisplayModeRetain.restype = c_void_p
quartz.CGDisplayModeRetain.argtypes = [c_void_p]
quartz.CGDisplayModeRelease.restype = None
quartz.CGDisplayModeRelease.argtypes = [c_void_p]
quartz.CGDisplayModeGetWidth.restype = c_size_t
quartz.CGDisplayModeGetWidth.argtypes = [c_void_p]
quartz.CGDisplayModeGetHeight.restype = c_size_t
quartz.CGDisplayModeGetHeight.argtypes = [c_void_p]
quartz.CGDisplayModeCopyPixelEncoding.restype = c_void_p
quartz.CGDisplayModeCopyPixelEncoding.argtypes = [c_void_p]
quartz.CGGetActiveDisplayList.restype = CGError
quartz.CGGetActiveDisplayList.argtypes = [c_uint32, POINTER(CGDirectDisplayID), POINTER(c_uint32)]
quartz.CGDisplayBounds.restype = CGRect
quartz.CGDisplayBounds.argtypes = [CGDirectDisplayID]
quartz.CGImageSourceCreateWithData.restype = c_void_p
quartz.CGImageSourceCreateWithData.argtypes = [c_void_p, c_void_p]
quartz.CGImageSourceCreateImageAtIndex.restype = c_void_p
quartz.CGImageSourceCreateImageAtIndex.argtypes = [c_void_p, c_size_t, c_void_p]
quartz.CGImageSourceCopyPropertiesAtIndex.restype = c_void_p
quartz.CGImageSourceCopyPropertiesAtIndex.argtypes = [c_void_p, c_size_t, c_void_p]
quartz.CGImageGetDataProvider.restype = c_void_p
quartz.CGImageGetDataProvider.argtypes = [c_void_p]
quartz.CGDataProviderCopyData.restype = c_void_p
quartz.CGDataProviderCopyData.argtypes = [c_void_p]
quartz.CGDataProviderCreateWithCFData.restype = c_void_p
quartz.CGDataProviderCreateWithCFData.argtypes = [c_void_p]
quartz.CGImageCreate.restype = c_void_p
quartz.CGImageCreate.argtypes = [c_size_t, c_size_t, c_size_t, c_size_t, c_size_t, c_void_p, c_uint32, c_void_p, 
 c_void_p, c_bool, c_int]
quartz.CGImageRelease.restype = None
quartz.CGImageRelease.argtypes = [c_void_p]
quartz.CGImageGetBytesPerRow.restype = c_size_t
quartz.CGImageGetBytesPerRow.argtypes = [c_void_p]
quartz.CGImageGetWidth.restype = c_size_t
quartz.CGImageGetWidth.argtypes = [c_void_p]
quartz.CGImageGetHeight.restype = c_size_t
quartz.CGImageGetHeight.argtypes = [c_void_p]
quartz.CGImageGetBitsPerPixel.restype = c_size_t
quartz.CGImageGetBitsPerPixel.argtypes = [c_void_p]
quartz.CGImageGetBitmapInfo.restype = CGBitmapInfo
quartz.CGImageGetBitmapInfo.argtypes = [c_void_p]
quartz.CGColorSpaceCreateDeviceRGB.restype = c_void_p
quartz.CGColorSpaceCreateDeviceRGB.argtypes = []
quartz.CGDataProviderRelease.restype = None
quartz.CGDataProviderRelease.argtypes = [c_void_p]
quartz.CGColorSpaceRelease.restype = None
quartz.CGColorSpaceRelease.argtypes = [c_void_p]
quartz.CGWarpMouseCursorPosition.restype = CGError
quartz.CGWarpMouseCursorPosition.argtypes = [CGPoint]
quartz.CGDisplayMoveCursorToPoint.restype = CGError
quartz.CGDisplayMoveCursorToPoint.argtypes = [CGDirectDisplayID, CGPoint]
quartz.CGAssociateMouseAndMouseCursorPosition.restype = CGError
quartz.CGAssociateMouseAndMouseCursorPosition.argtypes = [c_bool]
quartz.CGBitmapContextCreate.restype = c_void_p
quartz.CGBitmapContextCreate.argtypes = [c_void_p, c_size_t, c_size_t, c_size_t, c_size_t, c_void_p, CGBitmapInfo]
quartz.CGBitmapContextCreateImage.restype = c_void_p
quartz.CGBitmapContextCreateImage.argtypes = [c_void_p]
quartz.CGFontCreateWithDataProvider.restype = c_void_p
quartz.CGFontCreateWithDataProvider.argtypes = [c_void_p]
quartz.CGFontCreateWithFontName.restype = c_void_p
quartz.CGFontCreateWithFontName.argtypes = [c_void_p]
quartz.CGContextDrawImage.restype = None
quartz.CGContextDrawImage.argtypes = [c_void_p, CGRect, c_void_p]
quartz.CGContextRelease.restype = None
quartz.CGContextRelease.argtypes = [c_void_p]
quartz.CGContextSetTextPosition.restype = None
quartz.CGContextSetTextPosition.argtypes = [c_void_p, CGFloat, CGFloat]
quartz.CGContextSetShouldAntialias.restype = None
quartz.CGContextSetShouldAntialias.argtypes = [c_void_p, c_bool]
lib = util.find_library("CoreText")
if lib is None:
    lib = "/System/Library/Frameworks/CoreText.framework/CoreText"
ct = cdll.LoadLibrary(lib)
CTFontOrientation = c_uint32
CTFontSymbolicTraits = c_uint32
kCTFontAttributeName = c_void_p.in_dll(ct, "kCTFontAttributeName")
kCTFontFamilyNameAttribute = c_void_p.in_dll(ct, "kCTFontFamilyNameAttribute")
kCTFontSymbolicTrait = c_void_p.in_dll(ct, "kCTFontSymbolicTrait")
kCTFontWeightTrait = c_void_p.in_dll(ct, "kCTFontWeightTrait")
kCTFontTraitsAttribute = c_void_p.in_dll(ct, "kCTFontTraitsAttribute")
kCTFontItalicTrait = 1
kCTFontBoldTrait = 2
ct.CTLineCreateWithAttributedString.restype = c_void_p
ct.CTLineCreateWithAttributedString.argtypes = [c_void_p]
ct.CTLineDraw.restype = None
ct.CTLineDraw.argtypes = [c_void_p, c_void_p]
ct.CTFontGetBoundingRectsForGlyphs.restype = CGRect
ct.CTFontGetBoundingRectsForGlyphs.argtypes = [c_void_p, CTFontOrientation, POINTER(CGGlyph), POINTER(CGRect), CFIndex]
ct.CTFontGetAdvancesForGlyphs.restype = c_double
ct.CTFontGetAdvancesForGlyphs.argtypes = [c_void_p, CTFontOrientation, POINTER(CGGlyph), POINTER(CGSize), CFIndex]
ct.CTFontGetAscent.restype = CGFloat
ct.CTFontGetAscent.argtypes = [c_void_p]
ct.CTFontGetDescent.restype = CGFloat
ct.CTFontGetDescent.argtypes = [c_void_p]
ct.CTFontGetSymbolicTraits.restype = CTFontSymbolicTraits
ct.CTFontGetSymbolicTraits.argtypes = [c_void_p]
ct.CTFontGetGlyphsForCharacters.restype = c_bool
ct.CTFontGetGlyphsForCharacters.argtypes = [c_void_p, POINTER(UniChar), POINTER(CGGlyph), CFIndex]
ct.CTFontCreateWithGraphicsFont.restype = c_void_p
ct.CTFontCreateWithGraphicsFont.argtypes = [c_void_p, CGFloat, c_void_p, c_void_p]
ct.CTFontCopyFamilyName.restype = c_void_p
ct.CTFontCopyFamilyName.argtypes = [c_void_p]
ct.CTFontCopyFullName.restype = c_void_p
ct.CTFontCopyFullName.argtypes = [c_void_p]
ct.CTFontCreateWithFontDescriptor.restype = c_void_p
ct.CTFontCreateWithFontDescriptor.argtypes = [c_void_p, CGFloat, c_void_p]
ct.CTFontDescriptorCreateWithAttributes.restype = c_void_p
ct.CTFontDescriptorCreateWithAttributes.argtypes = [c_void_p]
lib = util.find_library("Foundation")
if lib is None:
    lib = "/System/Library/Frameworks/Foundation.framework/Foundation"
foundation = cdll.LoadLibrary(lib)
foundation.NSMouseInRect.restype = c_bool
foundation.NSMouseInRect.argtypes = [NSPoint, NSRect, c_bool]
