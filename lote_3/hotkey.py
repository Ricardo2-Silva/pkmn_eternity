# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\service\hotkey.py
import pyglet.event
from client.control.events import eventManager
from client.data.settings import gameSettings

class HotkeyManager:

    def __init__(self, desktop):
        self.desktop = desktop

    def on_key_press(self, symbol, modifiers):
        if self.desktop.getFocusWidget().__class__.__name__ not in ('Textbox', 'ControlTextbox'):
            if self.desktop._dragging:
                return pyglet.event.EVENT_UNHANDLED
            hotkeyName = gameSettings.getHotkeyPressed(symbol)
            if hotkeyName:
                eventManager.notify("onHotkeyPress", hotkeyName)
