# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\window\cocoa\systemcursor.py
from pyglet.libs.darwin import cocoapy

class SystemCursor:
    cursor_is_hidden = False

    @classmethod
    def hide(cls):
        if not cls.cursor_is_hidden:
            cocoapy.send_message("NSCursor", "hide")
            cls.cursor_is_hidden = True

    @classmethod
    def unhide(cls):
        if cls.cursor_is_hidden:
            cocoapy.send_message("NSCursor", "unhide")
            cls.cursor_is_hidden = False
