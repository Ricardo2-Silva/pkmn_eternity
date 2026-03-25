# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\window\cocoa\pyglet_delegate.py
from pyglet.libs.darwin.cocoapy import ObjCClass, ObjCSubclass, ObjCInstance
from pyglet.libs.darwin.cocoapy import NSApplicationDidHideNotification
from pyglet.libs.darwin.cocoapy import NSApplicationDidUnhideNotification
from pyglet.libs.darwin.cocoapy import send_super, get_selector
from pyglet.libs.darwin.cocoapy import PyObjectEncoding
from pyglet.libs.darwin.cocoapy import quartz
from .systemcursor import SystemCursor
NSNotificationCenter = ObjCClass("NSNotificationCenter")
NSApplication = ObjCClass("NSApplication")

class PygletDelegate_Implementation:
    PygletDelegate = ObjCSubclass("NSObject", "PygletDelegate")

    @PygletDelegate.method(b'@' + PyObjectEncoding)
    def initWithWindow_(self, window):
        self = ObjCInstance(send_super(self, "init"))
        if not self:
            return
        else:
            self._window = window
            window._nswindow.setDelegate_(self)
            notificationCenter = NSNotificationCenter.defaultCenter()
            notificationCenter.addObserver_selector_name_object_(self, get_selector("applicationDidHide:"), NSApplicationDidHideNotification, None)
            notificationCenter.addObserver_selector_name_object_(self, get_selector("applicationDidUnhide:"), NSApplicationDidUnhideNotification, None)
            self.did_pause_exclusive_mouse = False
            return self

    @PygletDelegate.method("v")
    def dealloc(self):
        notificationCenter = NSNotificationCenter.defaultCenter()
        notificationCenter.removeObserver_(self)
        self._window = None
        send_super(self, "dealloc")

    @PygletDelegate.method("v@")
    def applicationDidHide_(self, notification):
        self._window.dispatch_event("on_hide")

    @PygletDelegate.method("v@")
    def applicationDidUnhide_(self, notification):
        if self._window._is_mouse_exclusive:
            if quartz.CGCursorIsVisible():
                SystemCursor.unhide()
                SystemCursor.hide()
        self._window.dispatch_event("on_show")

    @PygletDelegate.method("B@")
    def windowShouldClose_(self, notification):
        self._window.dispatch_event("on_close")
        return False

    @PygletDelegate.method("v@")
    def windowDidMove_(self, notification):
        x, y = self._window.get_location()
        self._window.dispatch_event("on_move", x, y)

    @PygletDelegate.method("v@")
    def windowDidBecomeKey_(self, notification):
        if self.did_pause_exclusive_mouse:
            self._window.set_exclusive_mouse(True)
            self.did_pause_exclusive_mouse = False
            self._window._nswindow.setMovable_(True)
        self._window.set_mouse_platform_visible()
        self._window.dispatch_event("on_activate")

    @PygletDelegate.method("v@")
    def windowDidResignKey_(self, notification):
        if self._window._is_mouse_exclusive:
            self._window.set_exclusive_mouse(False)
            self.did_pause_exclusive_mouse = True
            self._window._nswindow.setMovable_(False)
        self._window.set_mouse_platform_visible(True)
        self._window.dispatch_event("on_deactivate")

    @PygletDelegate.method("v@")
    def windowDidMiniaturize_(self, notification):
        self._window.dispatch_event("on_hide")

    @PygletDelegate.method("v@")
    def windowDidDeminiaturize_(self, notification):
        if self._window._is_mouse_exclusive:
            if quartz.CGCursorIsVisible():
                SystemCursor.unhide()
                SystemCursor.hide()
        self._window.dispatch_event("on_show")

    @PygletDelegate.method("v@")
    def windowDidExpose_(self, notification):
        self._window.dispatch_event("on_expose")

    @PygletDelegate.method("v@")
    def terminate_(self, sender):
        NSApp = NSApplication.sharedApplication()
        NSApp.terminate_(self)

    @PygletDelegate.method("B@")
    def validateMenuItem_(self, menuitem):
        if menuitem.action() == get_selector("terminate:"):
            return not self._window._is_keyboard_exclusive
        else:
            return True


PygletDelegate = ObjCClass("PygletDelegate")
