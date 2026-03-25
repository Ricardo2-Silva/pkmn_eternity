# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\canvas\cocoa.py
from ctypes import *
from .base import Display, Screen, ScreenMode, Canvas
from pyglet.libs.darwin.cocoapy import CGDirectDisplayID, quartz, cf
from pyglet.libs.darwin.cocoapy import cfstring_to_string, cfarray_to_list

class CocoaDisplay(Display):

    def get_screens(self):
        maxDisplays = 256
        activeDisplays = CGDirectDisplayID * maxDisplays()
        count = c_uint32()
        quartz.CGGetActiveDisplayList(maxDisplays, activeDisplays, byref(count))
        return [CocoaScreen(self, displayID) for displayID in list(activeDisplays)[:count.value]]


class CocoaScreen(Screen):

    def __init__(self, display, displayID):
        bounds = quartz.CGDisplayBounds(displayID)
        x, y = bounds.origin.x, bounds.origin.y
        width, height = bounds.size.width, bounds.size.height
        super(CocoaScreen, self).__init__(display, int(x), int(y), int(width), int(height))
        self._cg_display_id = displayID
        self._default_mode = self.get_mode()

    def get_matching_configs(self, template):
        canvas = CocoaCanvas(self.display, self, None)
        return template.match(canvas)

    def get_modes(self):
        cgmodes = c_void_p(quartz.CGDisplayCopyAllDisplayModes(self._cg_display_id, None))
        modes = [CocoaScreenMode(self, cgmode) for cgmode in cfarray_to_list(cgmodes)]
        cf.CFRelease(cgmodes)
        return modes

    def get_mode(self):
        cgmode = c_void_p(quartz.CGDisplayCopyDisplayMode(self._cg_display_id))
        mode = CocoaScreenMode(self, cgmode)
        quartz.CGDisplayModeRelease(cgmode)
        return mode

    def set_mode(self, mode):
        assert mode.screen is self
        quartz.CGDisplayCapture(self._cg_display_id)
        quartz.CGDisplaySetDisplayMode(self._cg_display_id, mode.cgmode, None)
        self.width = mode.width
        self.height = mode.height

    def restore_mode(self):
        quartz.CGDisplaySetDisplayMode(self._cg_display_id, self._default_mode.cgmode, None)
        quartz.CGDisplayRelease(self._cg_display_id)

    def capture_display(self):
        quartz.CGDisplayCapture(self._cg_display_id)

    def release_display(self):
        quartz.CGDisplayRelease(self._cg_display_id)


class CocoaScreenMode(ScreenMode):

    def __init__(self, screen, cgmode):
        super(CocoaScreenMode, self).__init__(screen)
        quartz.CGDisplayModeRetain(cgmode)
        self.cgmode = cgmode
        self.width = int(quartz.CGDisplayModeGetWidth(cgmode))
        self.height = int(quartz.CGDisplayModeGetHeight(cgmode))
        self.depth = self.getBitsPerPixel(cgmode)
        self.rate = quartz.CGDisplayModeGetRefreshRate(cgmode)

    def __del__(self):
        quartz.CGDisplayModeRelease(self.cgmode)
        self.cgmode = None

    def getBitsPerPixel(self, cgmode):
        IO8BitIndexedPixels = "PPPPPPPP"
        IO16BitDirectPixels = "-RRRRRGGGGGBBBBB"
        IO32BitDirectPixels = "--------RRRRRRRRGGGGGGGGBBBBBBBB"
        cfstring = c_void_p(quartz.CGDisplayModeCopyPixelEncoding(cgmode))
        pixelEncoding = cfstring_to_string(cfstring)
        cf.CFRelease(cfstring)
        if pixelEncoding == IO8BitIndexedPixels:
            return 8
        if pixelEncoding == IO16BitDirectPixels:
            return 16
        else:
            if pixelEncoding == IO32BitDirectPixels:
                return 32
            return 0


class CocoaCanvas(Canvas):

    def __init__(self, display, screen, nsview):
        super(CocoaCanvas, self).__init__(display)
        self.screen = screen
        self.nsview = nsview
