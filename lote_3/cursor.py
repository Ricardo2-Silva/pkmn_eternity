# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\system\cursor.py
from client.control.events.event import eventManager
from client.scene.manager import sceneManager
from client.render.system.cursor import CustomImageCursor
from client.data.settings import gameSettings

class Cursor(object):
    __doc__ = " The cursor has a position, and a size. It also have a mode that describes\n    it's appareance. "
    hardware = gameSettings.getCursorAcceleration()

    def __init__(self):
        self._dragging = False
        self.targeting = False
        eventManager.registerListener(self)
        self.cursor = CustomImageCursor(self.hardware)
        sceneManager.window.set_mouse_cursor(self.cursor.cursors[self.cursor.mode])

    def hide(self):
        sceneManager.window.set_mouse_visible(False)

    def show(self):
        sceneManager.window.set_mouse_visible(True)

    def onShowLoadingScreen(self, text, steps=5):
        self.hide()

    def onHideLoadingScreen(self):
        self.show()

    @property
    def label(self):
        return self.cursor.label

    @property
    def mode(self):
        return self.cursor.mode

    @mode.setter
    def mode(self, mode_type):
        if self.targeting is True:
            return
        self.cursor.mode = mode_type
        sceneManager.window.set_mouse_cursor(self.cursor.cursors[self.cursor.mode])

    @property
    def text(self):
        return self.cursor.label.text

    @text.setter
    def text(self, text):
        self.cursor.label.text = text
        self.cursor.labelShadow.text = text


cursor = Cursor()
