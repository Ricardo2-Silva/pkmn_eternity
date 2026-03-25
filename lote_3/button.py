# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\gui\button.py
from client.data.gui.button import ButtonState
from client.control.gui.label import Label
import client.render.gui as iCoreRender
from client.control.gui.widget import Widget
from client.data.gui.icon import IconData, IconDataAll
from client.data.gui import styleDB
from client.data.utils.anchor import AnchorType, Alignment
from shared.container.constants import CursorMode

class InterfaceSelectableButton:

    def __init__(self):
        self.selected = False
        self.state = ButtonState.NORMAL

    def isSelected(self):
        return self.selected

    def setSelected(self, val):
        if val == True:
            if not self.isSelected():
                self.selected = True
                self.setState(ButtonState.DOWN)
        if val == False:
            if self.isSelected():
                self.selected = False
                self.setState(ButtonState.NORMAL)

    def unSelect(self):
        self.setSelected(False)

    def select(self):
        self.setSelected(True)

    def verifySelected(self):
        if self.isSelected():
            if not self.state == ButtonState.DOWN:
                self.setState(ButtonState.DOWN)
            return True
        else:
            return False

    def onMouseOver(self, widget, x, y):
        if not self.verifySelected():
            if not self.state == ButtonState.OVER:
                self.setState(ButtonState.OVER)

    def onMouseLeftClick(self, widget, x, y, modifiers):
        if self.isSelected():
            self.setSelected(False)
        else:
            self.setSelected(True)

    def onMouseRightClick(self, widget, x, y, modifiers):
        return

    def onMouseLeftDown(self, widget, x, y, modifiers):
        if not self.verifySelected():
            if not self.state == ButtonState.DOWN:
                self.setState(ButtonState.DOWN)

    def onMouseLeave(self, button):
        if not self.verifySelected():
            if not self.state == ButtonState.NORMAL:
                self.setState(ButtonState.NORMAL)
            self.desktop.cursor.mode = CursorMode.DEFAULT

    def onMouseClickOut(self, event):
        if not self.verifySelected():
            if not self.state == ButtonState.NORMAL:
                self.setState(ButtonState.NORMAL)


class Button(Label):
    renderClass = iCoreRender.ButtonRender

    def __init__(self, parent, text="Button", style=styleDB.blueButtonStyle, position=(0, 0), size=(0, 0), draggable=False, visible=True, autosize=(True, True), enableEvents=True, clickSound=None, overSound=None):
        self.buttonStyle = style
        self.state = ButtonState.NORMAL
        self.clickSound = clickSound
        self.overSound = overSound
        self.customState = None
        self.styleCopied = False
        Label.__init__(self, parent, text, self.buttonStyle.getStyle(ButtonState.NORMAL), position, size, draggable, visible, autosize, Alignment.LEFT, "left", "baseline", False, enableEvents)

    def clone(self, parent):
        return Button(parent, self.text, self.buttonStyle, self.getRelativePosition(), self.size, self.draggable, True, self.autosize, self.isEventsEnabled())

    def setTextAnchor(self, anchor):
        self.buttonStyle = self.buttonStyle.copy()
        self.buttonStyle.setTextAnchor(anchor)
        self.renderer.setTextAnchorPosition()
        self.renderer.refresh()

    def setBackgroundImage(self, images):
        if not self.styleCopied:
            self.buttonStyle = self.buttonStyle.copy()
            self.styleCopied = True
        currentStyle = self.getStyle().background
        self.buttonStyle.setBackgroundImage(images)
        if currentStyle is None:
            self.renderer.createBackgroundAndAdd()
        self.renderer.refresh()

    def getStyle(self):
        return self.buttonStyle.getStyle(self.getState())

    def setState(self, state, custom=False):
        """ Custom state overrides event states, this way you can force it to one state for effect purposes.
            Set to none to revert to normal behavior. """
        self.state = state
        self.customState = custom
        self.renderer.basicRefresh()

    def setStyle(self, buttonStyle):
        self.buttonStyle = buttonStyle
        self.renderer.refresh()

    def getState(self):
        return self.state

    def disableEvents(self):
        Widget.disableEvents(self)
        self.setState(ButtonState.DISABLED)

    def enableEvents(self):
        Widget.enableEvents(self)
        self.setState(ButtonState.NORMAL)

    def onMouseLeftDown(self, widget, x, y, modifiers):
        if not self.state == ButtonState.DOWN:
            self.setState(ButtonState.DOWN)

    def onMouseOver(self, widget, x, y):
        if not self.state == ButtonState.OVER:
            if not self.customState:
                self.setState(ButtonState.OVER)
                self.desktop.cursor.mode = CursorMode.POINTER

    def onMouseLeftClick(self, widget, x, y, modifiers):
        if not self.state == ButtonState.NORMAL:
            if not self.customState:
                self.setState(ButtonState.NORMAL)
                self.desktop.cursor.mode = CursorMode.DEFAULT

    def onMouseRightClick(self, widget, x, y, modifiers):
        if not self.state == ButtonState.NORMAL or not self.customState:
            self.setState(ButtonState.NORMAL)

    def onMouseLeave(self, button):
        if not (self.state == ButtonState.NORMAL and self.eventsEnabled):
            if not self.customState:
                self.setState(ButtonState.NORMAL)
                self.desktop.cursor.mode = CursorMode.DEFAULT

    def onMouseDrop(self, widget, x, y, modifiers):
        Widget.onMouseDrop(self, widget, x, y, modifiers)
        if not self.state == ButtonState.NORMAL:
            if not self.customState:
                self.setState(ButtonState.NORMAL)


class IconButton(Button):
    __doc__ = " Creates a button with an icon. icon can be either a texture or an IconData class. "
    renderClass = iCoreRender.IconButtonRender
    maxDepth = 4

    def __init__(self, parent, icon=None, iconAnchor=AnchorType.CENTER, text="", style=styleDB.blueButtonStyle, position=(0, 0), size=(0, 0), draggable=False, visible=True, autosize=(True, True), enableEvents=True, clickSound=None, overSound=None):
        self.state = ButtonState.NORMAL
        if isinstance(icon, IconData) or isinstance(icon, IconDataAll):
            self.iconData = icon
        elif icon is not None:
            self.iconData = IconData(icon)
        else:
            self.iconData = None
        self.iconAlwaysBottom = False
        self.iconAnchor = iconAnchor
        self._copiedIcon = False
        Button.__init__(self, parent, text, style, position, size, draggable, visible, autosize, enableEvents, clickSound, overSound)

    @property
    def icon(self):
        return self.iconData

    def tintColor(self, rgb, alpha=255):
        (self.renderer.setColor)(*rgb)

    def hasIcon(self):
        if self.iconData.hasIcon():
            return True
        else:
            return False

    def iconMatches(self, texture):
        if self.iconData:
            if self.iconData.textureMatches(texture):
                return True
        return False

    def removeIcon(self):
        if self.iconData:
            self.iconData = None
            self.renderer.removeIcon()
            self.updateSize()

    def getIcon(self):
        return self.iconData

    def setIconDefault(self, iconData):
        """ set an icon for all states. """
        if not isinstance(iconData, IconData):
            iconData = IconData(iconData)
        elif not self.iconData:
            self.iconData = iconData
            self.renderer.createAndAdd()
        else:
            self.iconData = iconData
            self.renderer.updateIconSprite()
        self.updateSize()

    def setIcon(self, **kwargs):
        for state in ButtonState.ALLSTATE:
            if state in kwargs:
                self.iconData.set(state, kwargs[state])

        self.renderer.updateIconSprite()
        self.updateSize()

    def setIconAnchor(self, anchor):
        self.iconAnchor = anchor
        self.renderer.updateIconPosition()

    def _setIconState(self, texture, state):
        self.iconData.set(state, texture)
        self.renderer.updateIconSprite()
        self.updateSize()

    def setIconNormal(self, texture):
        state = ButtonState.NORMAL
        self._setIconState(texture, state)

    def setIconOver(self, texture):
        self._setIconState(texture, ButtonState.OVER)

    def setIconDown(self, texture):
        self._setIconState(texture, ButtonState.DOWN)

    def setIconDisabled(self, texture):
        self._setIconState(texture, ButtonState.DISABLED)

    def setIconSize(self, width, height):
        self.renderer.setIconSize(width, height)

    def clone(self, parent):
        return IconButton(parent, self.iconData, self.text, self.ButtonStyle, self.getRelativePosition(), self.size, self.draggable, True, self.autosize, self.isEventsEnabled())

    def setState(self, state, custom=None):
        Button.setState(self, state, custom)
        self.renderer.updateIconSprite()


class SelectableIconButton(InterfaceSelectableButton, IconButton):

    def __init__(self, parent, icon=None, iconAnchor=None, text="", style=styleDB.blueButtonStyle, position=(0, 0), size=(0, 0), draggable=False, visible=True, autosize=(True, True), enableEvents=True):
        IconButton.__init__(self, parent, icon, iconAnchor, text, style, position, size, draggable, visible, autosize, enableEvents)
        InterfaceSelectableButton.__init__(self)
