# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\gui\checkbox.py
import client.render.gui as iCoreRender
from client.control.gui.button import Button, InterfaceSelectableButton
from client.control.gui.widget import Widget
from client.data.gui.button import ButtonState
from client.data.gui import styleDB
from client.data.utils.anchor import AnchorType
from shared.container.constants import CursorMode

class Checkbox(InterfaceSelectableButton, Button):
    renderClass = iCoreRender.CheckboxRender

    def __init__(self, parent, text="Check me", style=styleDB.checkboxButtonStyle, position=(0, 0), size=(0, 0), draggable=False, visible=True, autosize=(True, True), enableEvents=True):
        Button.__init__(self, parent, text, style, position, size, draggable, visible, autosize, enableEvents)
        InterfaceSelectableButton.__init__(self)

    def disableEvents(self):
        Widget.disableEvents(self)

    def enableEvents(self):
        Widget.enableEvents(self)

    def onMouseDrop(self, widget, x, y, modifiers):
        return


class Tab(Checkbox):

    def onMouseLeftClick(self, widget, x, y, modifiers):
        if not self.isSelected():
            self.setSelected(True)

    def onMouseOver(self, widget, x, y):
        if not self.verifySelected():
            if not self.state == ButtonState.OVER:
                self.setState(ButtonState.OVER)
                self.desktop.cursor.mode = CursorMode.POINTER
