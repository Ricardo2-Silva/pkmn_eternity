# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\window\cocoa\pyglet_textview.py
import unicodedata
from pyglet.window import key
from pyglet.libs.darwin.cocoapy import ObjCClass, ObjCSubclass, ObjCInstance
from pyglet.libs.darwin.cocoapy import PyObjectEncoding, send_super
from pyglet.libs.darwin.cocoapy import CFSTR, cfstring_to_string
NSArray = ObjCClass("NSArray")
NSApplication = ObjCClass("NSApplication")

class PygletTextView_Implementation:
    PygletTextView = ObjCSubclass("NSTextView", "PygletTextView")

    @PygletTextView.method(b'@' + PyObjectEncoding)
    def initWithCocoaWindow_(self, window):
        self = ObjCInstance(send_super(self, "init"))
        if not self:
            return
        else:
            self._window = window
            self.setFieldEditor_(False)
            self.empty_string = CFSTR("")
            return self

    @PygletTextView.method("v")
    def dealloc(self):
        self.empty_string.release()

    @PygletTextView.method("v@")
    def keyDown_(self, nsevent):
        array = NSArray.arrayWithObject_(nsevent)
        self.interpretKeyEvents_(array)

    @PygletTextView.method("v@")
    def insertText_(self, text):
        text = cfstring_to_string(text)
        self.setString_(self.empty_string)
        if unicodedata.category(text[0]) != "Cc":
            self._window.dispatch_event("on_text", text)

    @PygletTextView.method("v@")
    def insertNewline_(self, sender):
        event = NSApplication.sharedApplication().currentEvent()
        chars = event.charactersIgnoringModifiers()
        ch = chr(chars.characterAtIndex_(0))
        if ch == "\r":
            self._window.dispatch_event("on_text", "\r")

    @PygletTextView.method("v@")
    def moveUp_(self, sender):
        self._window.dispatch_event("on_text_motion", key.MOTION_UP)

    @PygletTextView.method("v@")
    def moveDown_(self, sender):
        self._window.dispatch_event("on_text_motion", key.MOTION_DOWN)

    @PygletTextView.method("v@")
    def moveLeft_(self, sender):
        self._window.dispatch_event("on_text_motion", key.MOTION_LEFT)

    @PygletTextView.method("v@")
    def moveRight_(self, sender):
        self._window.dispatch_event("on_text_motion", key.MOTION_RIGHT)

    @PygletTextView.method("v@")
    def moveWordLeft_(self, sender):
        self._window.dispatch_event("on_text_motion", key.MOTION_PREVIOUS_WORD)

    @PygletTextView.method("v@")
    def moveWordRight_(self, sender):
        self._window.dispatch_event("on_text_motion", key.MOTION_NEXT_WORD)

    @PygletTextView.method("v@")
    def moveToBeginningOfLine_(self, sender):
        self._window.dispatch_event("on_text_motion", key.MOTION_BEGINNING_OF_LINE)

    @PygletTextView.method("v@")
    def moveToEndOfLine_(self, sender):
        self._window.dispatch_event("on_text_motion", key.MOTION_END_OF_LINE)

    @PygletTextView.method("v@")
    def scrollPageUp_(self, sender):
        self._window.dispatch_event("on_text_motion", key.MOTION_PREVIOUS_PAGE)

    @PygletTextView.method("v@")
    def scrollPageDown_(self, sender):
        self._window.dispatch_event("on_text_motion", key.MOTION_NEXT_PAGE)

    @PygletTextView.method("v@")
    def scrollToBeginningOfDocument_(self, sender):
        self._window.dispatch_event("on_text_motion", key.MOTION_BEGINNING_OF_FILE)

    @PygletTextView.method("v@")
    def scrollToEndOfDocument_(self, sender):
        self._window.dispatch_event("on_text_motion", key.MOTION_END_OF_FILE)

    @PygletTextView.method("v@")
    def deleteBackward_(self, sender):
        self._window.dispatch_event("on_text_motion", key.MOTION_BACKSPACE)

    @PygletTextView.method("v@")
    def deleteForward_(self, sender):
        self._window.dispatch_event("on_text_motion", key.MOTION_DELETE)

    @PygletTextView.method("v@")
    def moveUpAndModifySelection_(self, sender):
        self._window.dispatch_event("on_text_motion_select", key.MOTION_UP)

    @PygletTextView.method("v@")
    def moveDownAndModifySelection_(self, sender):
        self._window.dispatch_event("on_text_motion_select", key.MOTION_DOWN)

    @PygletTextView.method("v@")
    def moveLeftAndModifySelection_(self, sender):
        self._window.dispatch_event("on_text_motion_select", key.MOTION_LEFT)

    @PygletTextView.method("v@")
    def moveRightAndModifySelection_(self, sender):
        self._window.dispatch_event("on_text_motion_select", key.MOTION_RIGHT)

    @PygletTextView.method("v@")
    def moveWordLeftAndModifySelection_(self, sender):
        self._window.dispatch_event("on_text_motion_select", key.MOTION_PREVIOUS_WORD)

    @PygletTextView.method("v@")
    def moveWordRightAndModifySelection_(self, sender):
        self._window.dispatch_event("on_text_motion_select", key.MOTION_NEXT_WORD)

    @PygletTextView.method("v@")
    def moveToBeginningOfLineAndModifySelection_(self, sender):
        self._window.dispatch_event("on_text_motion_select", key.MOTION_BEGINNING_OF_LINE)

    @PygletTextView.method("v@")
    def moveToEndOfLineAndModifySelection_(self, sender):
        self._window.dispatch_event("on_text_motion_select", key.MOTION_END_OF_LINE)

    @PygletTextView.method("v@")
    def pageUpAndModifySelection_(self, sender):
        self._window.dispatch_event("on_text_motion_select", key.MOTION_PREVIOUS_PAGE)

    @PygletTextView.method("v@")
    def pageDownAndModifySelection_(self, sender):
        self._window.dispatch_event("on_text_motion_select", key.MOTION_NEXT_PAGE)

    @PygletTextView.method("v@")
    def moveToBeginningOfDocumentAndModifySelection_(self, sender):
        self._window.dispatch_event("on_text_motion_select", key.MOTION_BEGINNING_OF_FILE)

    @PygletTextView.method("v@")
    def moveToEndOfDocumentAndModifySelection_(self, sender):
        self._window.dispatch_event("on_text_motion_select", key.MOTION_END_OF_FILE)


PygletTextView = ObjCClass("PygletTextView")
