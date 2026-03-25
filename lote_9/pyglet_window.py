# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\window\cocoa\pyglet_window.py
from ctypes import c_void_p, c_bool
from pyglet.libs.darwin.cocoapy import ObjCClass, ObjCSubclass, send_super
from pyglet.libs.darwin.cocoapy import NSUInteger, NSUIntegerEncoding
from pyglet.libs.darwin.cocoapy import NSRectEncoding

class PygletWindow_Implementation:
    PygletWindow = ObjCSubclass("NSWindow", "PygletWindow")

    @PygletWindow.method("B")
    def canBecomeKeyWindow(self):
        return True

    @PygletWindow.method(b'@' + NSUIntegerEncoding + b'@@B')
    def nextEventMatchingMask_untilDate_inMode_dequeue_(self, mask, date, mode, dequeue):
        if self.inLiveResize():
            from pyglet import app
            if app.event_loop is not None:
                app.event_loop.idle()
        event = send_super(self, "nextEventMatchingMask:untilDate:inMode:dequeue:", mask,
          date, mode, dequeue, superclass_name="NSWindow",
          argtypes=[
         NSUInteger, c_void_p, c_void_p, c_bool])
        if event.value is None:
            return 0
        else:
            return event.value

    @PygletWindow.method(b'd' + NSRectEncoding)
    def animationResizeTime_(self, newFrame):
        return 0.0


class PygletToolWindow_Implementation:
    PygletToolWindow = ObjCSubclass("NSPanel", "PygletToolWindow")

    @PygletToolWindow.method(b'@' + NSUIntegerEncoding + b'@@B')
    def nextEventMatchingMask_untilDate_inMode_dequeue_(self, mask, date, mode, dequeue):
        if self.inLiveResize():
            from pyglet import app
            if app.event_loop is not None:
                app.event_loop.idle()
        event = send_super(self, "nextEventMatchingMask:untilDate:inMode:dequeue:", mask,
          date, mode, dequeue, argtypes=[NSUInteger, c_void_p, c_void_p, c_bool])
        if event.value == None:
            return 0
        else:
            return event.value

    @PygletToolWindow.method(b'd' + NSRectEncoding)
    def animationResizeTime_(self, newFrame):
        return 0.0


PygletWindow = ObjCClass("PygletWindow")
PygletToolWindow = ObjCClass("PygletToolWindow")
