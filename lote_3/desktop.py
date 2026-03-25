# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\gui\desktop.py
"""
Created on 27 juil. 2011

@author: Kami
"""
from client.control.events import eventManager
from client.data.gui.padding import defaultPadding
from client.data.layer import LayerType
from client.data.settings import gameSettings
from shared.container.geometry import InterfacePositionable2D, InterfacePositionable
from client.control.gui.core import AbstractContainer
import pyglet
from pyglet.window import mouse, key
from pyglet.window.key import KeyStateHandler
from client.scene.manager import sceneManager
from client.data.utils.anchor import AnchorType
from client.control.gui.container import Container
from shared.container.constants import CursorMode
from pyglet.gl import *
from client.render.gui.caret import Caret, TextSelection
UI_SCALE = gameSettings.getUIScale()

class Desktop(AbstractContainer, InterfacePositionable):

    def __init__(self):
        width, height = gameSettings.getScaledUIWindowResolution()
        self.scale = UI_SCALE
        InterfacePositionable.__init__(self, 0, 0, width, height)
        AbstractContainer.__init__(self)
        eventManager.registerListener(self)
        self.keys = KeyStateHandler()
        self._focusWidget = None
        self.overedWidget = None
        self._dragging = False
        self.visible = True
        self.enabled = True
        self._widgetDown = None
        self.widgetById = {}
        self.parent = None
        self.batch = pyglet.graphics.Batch()
        self.group = pyglet.graphics.Group()
        self.transparent = pyglet.graphics.Batch()
        self.cursor = None
        self.minimizeArea = Container(self, position=(AnchorType.TOPRIGHTFIXED), size=(width, height))
        self.minimizeArea.setAutoFit()
        self.highlight = TextSelection(group=(self.group), batch=(self.transparent))
        self.caret = Caret(15, group=(self.group), batch=(self.transparent))
        if self.scale != 1.0:
            self.render = self.scale_render

    @property
    def order(self):
        return LayerType.GUI

    @order.setter
    def order(self, value):
        self._order = value

    @property
    def id(self):
        return self.__class__.__name__

    def setAlwaysOnTop(self, widget):
        if widget.visible:
            self.widgetsAlwaysOnTop.insert(0, widget)

    def setAlwaysBehind(self, widget):
        if widget.parent == self:
            if widget.visible:
                self.visibleWidgets.remove(widget)
                self.visibleWidgets.insert(0, widget)
            if widget.visible:
                if widget.isEventsEnabled():
                    self.reactingWidgets.remove(widget)
                    self.reactingWidgets.append(widget)

    def reOrder(self):
        """ Reorders all child widgets to new order values. """
        order = self.order
        for widget in self.visibleWidgets + self.widgetsAlwaysOnTop:
            widget.order = order
            order += widget.maxDepth

        self.maxDepth = order + 1

    @property
    def name(self):
        return "Desktop"

    def widgetAdded(self):
        return

    def widgetDeleted(self):
        return

    def childChangedSize(self, child):
        return

    def fitToContent(self):
        self.replaceAnchoredWidgets()
        return

    def contentChangedSize(self):
        return

    def isAutosize(self):
        return False

    def isFullAutosize(self):
        return False

    def widgetGotDisabled(self, widget):
        if widget == self._focusWidget:
            self._lostFocus()

    def childGetId(self, child, id):
        self.widgetById[id] = child

    def getTopLeftPadded(self, offx=0, offy=0):
        return (
         offx, offy)

    def getPaddedWidth(self):
        return self.width - self.getPadding().left - self.getPadding().right

    def getPaddedHeight(self):
        return self.height - self.getPadding().top - self.getPadding().right

    def getTopRightPadded(self, offx=0, offy=0):
        return (0, 0)

    def getBottomRightPadded(self, offx=0, offy=0):
        return (
         offx + gameSettings.getWindowResolution()[0], offy + +gameSettings.getWindowResolution()[1])

    def getBottomLeftPadded(self, offx=0, offy=0):
        return (
         offx, offy + gameSettings.getWindowResolution()[1])

    def getAutosize(self):
        return (False, False)

    def getVisibleState(self):
        return True

    def hasFocus(self):
        """ If a widget is focused through events, will return focus to None if hidden."""
        if self._focusWidget is not None:
            if self._focusWidget.getRoot().visible is False:
                self._focusWidget = None
        return bool(self._focusWidget)

    def onInputUnblocked(self):
        self.lostFocus()

    def getPadding(self):
        return defaultPadding

    def onWidgetHide(self, widgetId):
        if widgetId not in self.widgetById:
            raise Exception("The widget you want to hide have no Id. Give it an Id with .setId(id)")
        self.widgetById[widgetId].forceHide()

    def onWidgetShow(self, widgetId):
        if widgetId not in self.widgetById:
            raise Exception("The widget you want to show have no Id. Give it an Id with .setId(id)")
        self.widgetById[widgetId].forceUnHide()

    def on_mouse_motion(self, x, y, dx, dy):
        """ Always on mouse over to tell which widget, return false for input manager coords. """
        x, y = sceneManager.convert(x, y)
        widget = self.getCollidingWidget(x, y)
        if widget:
            if self.overedWidget == widget:
                return pyglet.event.EVENT_UNHANDLED
            if self.overedWidget:
                if widget != self.overedWidget:
                    self.overedWidget.runCallback("onMouseLeave", self.overedWidget)
            widget.runCallback("onMouseOver", widget, x // UI_SCALE, y // UI_SCALE)
            self.overedWidget = widget
        else:
            if self.overedWidget:
                self.overedWidget.runCallback("onMouseLeave", self.overedWidget)
            self.overedWidget = None
        return pyglet.event.EVENT_UNHANDLED

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if buttons == pyglet.window.mouse.LEFT:
            if self._dragging:
                self._dragging.on_mouse_drag(x // UI_SCALE, y // UI_SCALE, dx / UI_SCALE, dy / UI_SCALE, buttons, modifiers)
                return pyglet.event.EVENT_HANDLED
            handled = (self.on_mouse_drag_start)(*sceneManager.convert(x, y), *(dx, dy, buttons, modifiers))
            return handled
        else:
            return pyglet.event.EVENT_UNHANDLED

    def on_mouse_release(self, x, y, button, modifiers):
        """ Occurs when mouse is pressed up (released) """
        if not self.visible:
            return pyglet.event.EVENT_UNHANDLED
        else:
            if self._dragging:
                if button == pyglet.window.mouse.LEFT:
                    self.on_mouse_drop(x, y, button, modifiers)
                return pyglet.event.EVENT_HANDLED
            else:
                x, y = sceneManager.convert(x, y)
                widget = self.getCollidingWidget(x, y)
                if widget:
                    if widget.isEventIgnored("onMouseLeftClick") or widget.isEventIgnored("onMouseRightClick"):
                        return
                    else:
                        self.setFocusWidget(widget)
                        if button == mouse.LEFT:
                            widget.runCallback("onMouseLeftClick", widget, x, y, modifiers)
                        else:
                            if button == mouse.RIGHT:
                                widget.runCallback("onMouseRightClick", widget, x, y, modifiers)
                        return pyglet.event.EVENT_HANDLED
            self.lostFocus()
            return pyglet.event.EVENT_UNHANDLED

    def on_mouse_press(self, x, y, button, modifiers):
        """ Occurs when mouse is pressed down """
        if not self.visible:
            return pyglet.event.EVENT_UNHANDLED
        else:
            if self._dragging:
                return pyglet.event.EVENT_HANDLED
            else:
                x, y = sceneManager.convert(x, y)
                new_widget = self.getCollidingWidget(x, y)
                if new_widget:
                    if new_widget.isEventIgnored("onMouseLeftDown") or new_widget.isEventIgnored("onMouseRightDown"):
                        return pyglet.event.EVENT_HANDLED
                    else:
                        self.setFocusWidget(new_widget)
                        if button == mouse.LEFT:
                            new_widget.runCallback("onMouseLeftDown", new_widget, x, y, modifiers)
                        else:
                            if button == mouse.RIGHT:
                                new_widget.runCallback("onMouseRightDown", new_widget, x, y, modifiers)
                        return pyglet.event.EVENT_HANDLED
            return pyglet.event.EVENT_UNHANDLED

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if not self.overedWidget:
            return pyglet.event.EVENT_UNHANDLED
        else:
            cwidget = self.overedWidget
            while not cwidget.hasCallbackOnEvent("onMouseScroll"):
                cwidget = cwidget.parent
                if cwidget == self:
                    return pyglet.event.EVENT_UNHANDLED

            if scroll_y < 0:
                val = 1
            else:
                if scroll_y > 0:
                    val = -1
            cwidget.runCallback("onMouseScroll", x, y, val)
            return pyglet.event.EVENT_HANDLED

    def on_mouse_drag_start(self, x, y, dx, dy, buttons, modifiers):
        """ Called once, when we start to drag """
        widget = self.overedWidget
        if self.overedWidget:
            if widget.isContainer():
                while widget.parent != self:
                    widget = widget.parent

            else:
                if not widget.isDraggable() or widget.isEventIgnored("onMouseDragBegin"):
                    return pyglet.event.EVENT_UNHANDLED
                self._dragging = widget
                self.setFocusWidget(widget)
                parent = widget.parent
                if parent.__class__.__name__ == "Datatable" or parent.__class__.__name__ == "PageDatatable":
                    parent.pushToTop(widget)
            widget.runCallback("onMouseDragBegin", widget, x // UI_SCALE, y // UI_SCALE, modifiers)
            return pyglet.event.EVENT_HANDLED
        else:
            return pyglet.event.EVENT_UNHANDLED

    def on_mouse_drop(self, x, y, button, modifiers):
        """ Called when we release the mouse after dragging """
        cx, cy = sceneManager.convert(x, y)
        self._dragging = False
        self.cursor.mode = CursorMode.DEFAULT
        draggedWidget = self._focusWidget
        if draggedWidget:
            draggedWidget.runCallback("onMouseDrop", draggedWidget, cx, cy, modifiers)
            widgetDroppedOn = self.getCollidingWidget(cx, cy, exclude=[draggedWidget])
            if widgetDroppedOn:
                draggedWidget.runCallback("onWidgetDroppedOn", draggedWidget, widgetDroppedOn, cx, cy, modifiers)
            else:
                draggedWidget.runCallback("onWidgetDroppedOn", draggedWidget, self, cx, cy, modifiers)
            self.on_mouse_motion(x, y, 0, 0)

    def reset(self):
        if self._dragging:
            self.cursor.mode = CursorMode.DEFAULT
            draggedWidget = self._focusWidget
            self._dragging = False
            if draggedWidget:
                draggedWidget.runCallback("onMouseDrop", draggedWidget, 0, 0, 0)
            self.overedWidget = None
        self._focusWidget = None

    def on_key_tab(self):
        if self.hasFocus():
            widgets = self._focusWidget.parent.widgets
            index = widgets.index(self._focusWidget) + 1
            if index == len(widgets):
                index = 0
            while not (widgets[index].visible and widgets[index].visible):
                index += 1
                if index == len(widgets):
                    index = 0

            self.setActive(widgets[index])
            return pyglet.event.EVENT_HANDLED
        else:
            return pyglet.event.EVENT_UNHANDLED

    def on_key_press(self, symbol, modifiers):
        if self.hasFocus():
            shift_bypass = False
            if symbol == key.LSHIFT or symbol == key.RSHIFT:
                shift_bypass = True
            if self._dragging:
                if not shift_bypass:
                    self.reset()
                    return pyglet.event.EVENT_HANDLED
            if symbol == key.RETURN or symbol == key.NUM_ENTER:
                self._focusWidget.runCallback("onKeyReturn")
            elif symbol == key.TAB:
                self.on_key_tab()
            elif symbol == key.ESCAPE:
                self.lostFocus()
            else:
                self._focusWidget.runCallback("onKeyDown", symbol, modifiers)
            return pyglet.event.EVENT_HANDLED
        else:
            return pyglet.event.EVENT_UNHANDLED

    def on_key_release(self, symbol, modifiers):
        if self.hasFocus():
            return pyglet.event.EVENT_HANDLED
        else:
            return pyglet.event.EVENT_UNHANDLED

    def on_text(self, text):
        if self.hasFocus():
            self._focusWidget.runCallback("onKeyText", text)
            return pyglet.event.EVENT_HANDLED
        else:
            return pyglet.event.EVENT_UNHANDLED

    def on_text_motion(self, motion):
        if self.hasFocus() and self._focusWidget.__class__.__name__ == "Textbox":
            self._focusWidget.on_text_motion(motion)
            return pyglet.event.EVENT_HANDLED
        else:
            return pyglet.event.EVENT_UNHANDLED

    def on_text_motion_select(self, motion):
        if self.hasFocus() and self._focusWidget.__class__.__name__ == "Textbox":
            self._focusWidget.on_text_motion_select(motion)
            return pyglet.event.EVENT_HANDLED
        else:
            return pyglet.event.EVENT_UNHANDLED

    def _lostFocus(self):
        self.reset()
        eventManager.notify("onDesktopLostFocus")

    def lostFocus(self):
        if self._focusWidget:
            self._focusWidget.runCallback("onLostFocus", self._focusWidget)
        self._lostFocus()

    def setActive(self, widget):
        self.setFocusWidget(widget)

    def setInactive(self, widget):
        if self._focusWidget == widget:
            self.lostFocus()

    def setFocusWidget(self, widget):
        if not widget.visible:
            raise Exception("The widget that we want to set on top on is not visible !", widget.name)
        if widget != self._focusWidget:
            ancestor = widget.getRoot()
            if not ancestor.isAlwaysBehind():
                if ancestor != self:
                    self.pushToTop(ancestor)
                widget.setOnTop()
                if self._focusWidget:
                    self._focusWidget.runCallback("onLostFocus", widget)
            else:
                if widget.focusEnabled is True:
                    eventManager.notify("onDesktopGetFocus")
            self._focusWidget = widget
            self._focusWidget.runCallback("onGainFocus", widget)

    def getFocusWidget(self):
        return self._focusWidget

    def onToggleGui(self):
        self.visible = not self.visible

    def onHideGui(self):
        self.visible = False

    def onShowGui(self):
        self.visible = True

    def update(self, dt):
        """ Scheduled updates"""
        if self._dragging:
            self._dragging.updatePositionDragging()

    def scale_render(self):
        if self.visible:
            glScalef(self.scale, self.scale, 1.0)
            glTranslatef(0, -self.height, 0)
            self.batch.draw()
            glDepthMask(GL_FALSE)
            self.transparent.draw()
            glDepthMask(GL_TRUE)
            glTranslatef(0, self.height, 0)
            glScalef(1 / self.scale, 1.0 / self.scale, 1.0)

    def render(self):
        if self.visible:
            self.batch.draw()
            glDepthMask(GL_FALSE)
            self.transparent.draw()
            glDepthMask(GL_TRUE)
