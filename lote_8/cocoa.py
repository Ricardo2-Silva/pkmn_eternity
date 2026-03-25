# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\app\cocoa.py
from pyglet.app.base import PlatformEventLoop
from pyglet.libs.darwin import cocoapy
NSApplication = cocoapy.ObjCClass("NSApplication")
NSMenu = cocoapy.ObjCClass("NSMenu")
NSMenuItem = cocoapy.ObjCClass("NSMenuItem")
NSAutoreleasePool = cocoapy.ObjCClass("NSAutoreleasePool")
NSDate = cocoapy.ObjCClass("NSDate")
NSEvent = cocoapy.ObjCClass("NSEvent")
NSUserDefaults = cocoapy.ObjCClass("NSUserDefaults")

class AutoReleasePool:

    def __enter__(self):
        self.pool = NSAutoreleasePool.alloc().init()
        return self.pool

    def __exit__(self, exc_type, exc_value, traceback):
        self.pool.drain()
        del self.pool


def add_menu_item(menu, title, action, key):
    with AutoReleasePool():
        title = cocoapy.CFSTR(title)
        action = cocoapy.get_selector(action)
        key = cocoapy.CFSTR(key)
        menuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(title, action, key)
        menu.addItem_(menuItem)
        title.release()
        key.release()
        menuItem.release()


def create_menu():
    with AutoReleasePool():
        appMenu = NSMenu.alloc().init()
        add_menu_item(appMenu, "Hide!", "hide:", "h")
        appMenu.addItem_(NSMenuItem.separatorItem())
        add_menu_item(appMenu, "Quit!", "terminate:", "q")
        menubar = NSMenu.alloc().init()
        appMenuItem = NSMenuItem.alloc().init()
        appMenuItem.setSubmenu_(appMenu)
        menubar.addItem_(appMenuItem)
        NSApp = NSApplication.sharedApplication()
        NSApp.setMainMenu_(menubar)
        appMenu.release()
        menubar.release()
        appMenuItem.release()


class CocoaEventLoop(PlatformEventLoop):

    def __init__(self):
        super(CocoaEventLoop, self).__init__()
        with AutoReleasePool():
            self.NSApp = NSApplication.sharedApplication()
            if self.NSApp.isRunning():
                return
            if not self.NSApp.mainMenu():
                create_menu()
            self.NSApp.setActivationPolicy_(cocoapy.NSApplicationActivationPolicyRegular)
            defaults = NSUserDefaults.standardUserDefaults()
            ignoreState = cocoapy.CFSTR("ApplePersistenceIgnoreState")
            if not defaults.objectForKey_(ignoreState):
                defaults.setBool_forKey_(True, ignoreState)
            self._finished_launching = False

    def start(self):
        with AutoReleasePool():
            if not self.NSApp.isRunning():
                if not self._finished_launching:
                    self.NSApp.finishLaunching()
                    self.NSApp.activateIgnoringOtherApps_(True)
                    self._finished_launching = True

    def step(self, timeout=None):
        with AutoReleasePool():
            self.dispatch_posted_events()
            if timeout is None:
                timeout_date = NSDate.distantFuture()
            else:
                timeout_date = NSDate.dateWithTimeIntervalSinceNow_(timeout)
            self._is_running.set()
            event = self.NSApp.nextEventMatchingMask_untilDate_inMode_dequeue_(cocoapy.NSAnyEventMask, timeout_date, cocoapy.NSDefaultRunLoopMode, True)
            if event is not None:
                event_type = event.type()
                if event_type != cocoapy.NSApplicationDefined:
                    self.NSApp.sendEvent_(event)
                    if event_type == cocoapy.NSKeyDown:
                        if not event.isARepeat():
                            self.NSApp.sendAction_to_from_(cocoapy.get_selector("pygletKeyDown:"), None, event)
                        if event_type == cocoapy.NSKeyUp:
                            self.NSApp.sendAction_to_from_(cocoapy.get_selector("pygletKeyUp:"), None, event)
                    elif event_type == cocoapy.NSFlagsChanged:
                        self.NSApp.sendAction_to_from_(cocoapy.get_selector("pygletFlagsChanged:"), None, event)
                self.NSApp.updateWindows()
                did_time_out = False
            else:
                did_time_out = True
            self._is_running.clear()
            return did_time_out

    def stop(self):
        return

    def notify(self):
        with AutoReleasePool():
            notifyEvent = NSEvent.otherEventWithType_location_modifierFlags_timestamp_windowNumber_context_subtype_data1_data2_(cocoapy.NSApplicationDefined, cocoapy.NSPoint(0.0, 0.0), 0, 0, 0, None, 0, 0, 0)
            self.NSApp.postEvent_atStart_(notifyEvent, False)
