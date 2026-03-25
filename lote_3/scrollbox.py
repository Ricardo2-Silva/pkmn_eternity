# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\gui\scrollbox.py
from client.control.gui.container import Container, AbstractContainer
import client.render.gui as iCoreRender
from client.data.gui import styleDB
from client.control.gui.picture import Picture
from client.control.gui.button import Button
from client.control.gui.widget import Widget
from client.data import exceptions
from functools import reduce
from shared.service.utils import clamp
import pyglet
from pyglet.gl import *
from client.data.settings import gameSettings
import rabbyt
from client.render.cache import textureCache
from shared.container.geometry import Rect
scaled_width, scaled_height = gameSettings.getScaledUIWindowResolution()
g_width, g_height = gameSettings.getWindowResolution()
scale = gameSettings.getUIScale()

class ClipGroup(pyglet.graphics.Group):

    def __init__(self, widget, parent=None):
        pyglet.graphics.Group.__init__(self, parent=parent)
        self._visible = False
        self.widget = widget

    def set_state(self):
        glEnable(GL_SCISSOR_TEST)
        glScissor(int(self.widget.parent.x * scale), int(g_height - self.widget.parent.top * scale), int(self.widget.parent.width * scale), int(self.widget.parent.height * scale))
        glTranslatef(0, -self.widget.offsetY, 0)

    def unset_state(self):
        glTranslatef(0, self.widget.offsetY, 0)
        glDisable(GL_SCISSOR_TEST)

    def __hash__(self):
        return hash(id(self))

    def __eq__(self, other):
        return False


class ClipArea(Container):
    renderClass = iCoreRender.ContainerRender


SPACE_BETWEEN_CONTENT_AND_BAR = 25

class ScrollContent(Container):
    __doc__ = " The special container that contains the things inside. "
    renderClass = iCoreRender.ContainerRender

    def __init__(self, *args, **kwargs):
        self.offsetY = 0
        self.inAreaWidgets = set()
        (Container.__init__)(self, *args, **kwargs)
        self.setManualFit()
        self._group = ClipGroup(self, self.desktop.group)

    @property
    def group(self):
        return self._group

    def setSize(self, width, height):
        return Container.setSize(self, width, height)

    def _setContentHeight(self):
        cHeight = reduce((lambda x, y: max(x, y.y + y.height - self.y)), [x for x in self.widgets if not x.hasAnchor()], 0)
        cHeight = max(cHeight, self.anchorHeight)
        self._contentHeight = cHeight

    def _setContentWidth(self):
        Container._setContentWidth(self)
        self._contentWidth += SPACE_BETWEEN_CONTENT_AND_BAR

    def clean(self):
        return

    def updateOffscreen(self):
        """ On drop we need to update all of the widgets to new position, even if not in view. """
        self.updateChildsPosition()

    def getCollidingWidget(self, x, y, exclude=[]):
        """ Override hit detection because glTranslate will push widgets out of normal bound areas. """
        return Container.getCollidingWidget(self, x, (y - self.offsetY), exclude=exclude)

    def updatePositionDragging(self):
        """ Only update positions of those in view when dragging, reduced calls."""
        Widget.updatePositionDragging(self)
        self.inAreaWidgets = self.getWidgetsInArea(Rect(self.x, self.y - self.offsetY, self.parent.width, self.parent.height))
        for widget in self.inAreaWidgets:
            widget.updatePositionDragging()

    def setChildDestroy(self, widget):
        AbstractContainer.setChildDestroy(self, widget)
        if widget in self.inAreaWidgets:
            self.inAreaWidgets.remove(widget)

    def getMaxHeight(self):
        return -(self.height - self.parent.height)

    def drag(self, dy):
        """ Move a widget """
        self.offsetY = clamp(self.offsetY + dy, self.getMaxHeight(), 0)


BUTTON_WIDTH = 22
BUTTON_HEIGHT = 16

class ScrollBar(Button):

    def __init__(self, parent, *args, **kwargs):
        (Button.__init__)(self, parent, *args, **kwargs)
        self.container = parent

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.container.scroll(-dy)

    def updatePosition(self):
        Button.updatePosition(self)

    def minButtonHeight(self):
        return BUTTON_HEIGHT

    def maxButtonHeight(self):
        return self.container.height - self.height - BUTTON_HEIGHT

    def drag(self, dy):
        self.relativeY = clamp(self.relativeY + dy, self.minButtonHeight(), self.maxButtonHeight())

    def onKeyDown(self, symbol, modifiers):
        step = self.container.height / self.height
        if symbol == pyglet.window.key.UP:
            self.container.scroll(-step)
        else:
            if symbol == pyglet.window.key.DOWN:
                self.container.scroll(step)
        self.updatePosition()


class ScrollableContainer(Container):
    renderClass = iCoreRender.ContainerRender

    def __init__(self, parent, position=(0, 0), size=(100, 100), visible=True, autosize=(True, False), draggable=False, mouseScroll=True, content=ScrollContent):
        self.state = 0
        if size[0] < 20 or size[1] < 20:
            raise Exception("The size must be above 20 for both width and height")
        if autosize[1]:
            raise Exception("A scroll container can not be autosize in height.")
        self.pixelStep = 1.0
        Container.__init__(self, parent, position, size, draggable, visible, autosize=(autosize[0], False))
        self.upButton = Button(self, "", style=(styleDB.scrollUpButtonStyle), size=(20,
                                                                                    20), position=(size[0] - BUTTON_WIDTH, 0), autosize=(False,
                                                                                                                                         False))
        self.downButton = Button(self, "", style=(styleDB.scrollDownButtonStyle), size=(20,
                                                                                        20), position=(size[0] - BUTTON_WIDTH, size[1] - BUTTON_HEIGHT), autosize=(False,
                                                                                                                                                                   False))
        self.upButton.addCallback("onMouseLeftDown", self.scrollEvent, -1)
        self.downButton.addCallback("onMouseLeftDown", self.scrollEvent, 1)
        self.upButton.addCallback("onKeyDown", self.keyEvent)
        self.downButton.addCallback("onKeyDown", self.keyEvent)
        self.barBehindPicture = Picture(self, (textureCache.getBackgroundColor((234,
                                                                                239,
                                                                                244))), position=(size[0] - BUTTON_WIDTH + 3, BUTTON_HEIGHT), size=(16, size[1] - BUTTON_HEIGHT * 2), autosize=(False,
                                                                                                                                                                                                False))
        self.barButton = ScrollBar(self, "", style=(styleDB.scrollBarButtonStyle), size=(20, BUTTON_HEIGHT), position=(size[0] - BUTTON_WIDTH + 1, BUTTON_HEIGHT), draggable=True, autosize=(False,
                                                                                                                                                                                             False))
        self.barButton.preventDefault("onMouseDragging", "onMouseDrop")

        def _onMouseScroll(x, y, value):
            self.scroll(self.height / self.barButton.height * value)
            self.barButton.updatePosition()

        if mouseScroll:
            self.addCallback("onMouseScroll", _onMouseScroll)
        self.content = content(self, size=(size[0] - SPACE_BETWEEN_CONTENT_AND_BAR, size[1]))
        if self.parent != self.desktop:
            self.parent.addCallbackEnd("onMouseDrop", (lambda widget, x, y, modifiers: self.content.updateOffscreen()))
        (Widget.setSize)(self, *size)
        self.state = 1

    def keyEvent(self, symbol, modifiers):
        step = self.height / self.barButton.height
        if symbol == pyglet.window.key.UP:
            self.scroll(-step)
        else:
            if symbol == pyglet.window.key.DOWN:
                self.scroll(step)
        self.updatePosition()

    def showBar(self):
        """ Only show bar if the content needs to, otherwise no need."""
        try:
            self.upButton.show()
            self.downButton.show()
            self.barBehindPicture.show()
            self.barButton.show()
        except Exception:
            pass

    def hideBar(self):
        """ Hide bar if the content is not large enough to warrant it"""
        try:
            self.upButton.hide()
            self.downButton.hide()
            self.barBehindPicture.hide()
            self.barButton.hide()
        except Exception:
            pass

    def updateContentPosition(self):
        """ Place the scrollbar at the correct position """
        self.upButton.setPosition(self.width - BUTTON_WIDTH, 0)
        self.downButton.setPosition(self.width - BUTTON_WIDTH, self.height - BUTTON_HEIGHT)
        self.barBehindPicture.setPosition(self.width - BUTTON_WIDTH + 3, BUTTON_HEIGHT)
        self.barButton.setX(self.width - BUTTON_WIDTH + 1)

    def scrollEvent(self, widget, x, y, modifiers, scrollY):
        self.scroll(scrollY)
        self.barButton.updatePosition()

    def scroll(self, diffy):
        self.barButton.drag(diffy)
        self.content.drag(self.pixelStep * -diffy)

    def pathOfbar(self):
        return self.height - BUTTON_HEIGHT * 2 - self.barButton.height

    def contentSize(self):
        return self.content.height - self.height

    def ignoreContainerArea(self):
        """ ignore Container if we click on it, only take care of the widgets inside. """
        return False

    def pushToTop(self):
        """ Put the scroll to up """
        self.content.offsetY = 0
        self.barButton.setPosition(self.barButton.relativeX, BUTTON_HEIGHT)

    def pushToBottom(self):
        """ Put the scroll to up """
        self.content.offsetY = self.content.getMaxHeight()
        self.barButton.setPosition(self.barButton.relativeX, self.barButton.maxButtonHeight())

    def pushToDiff(self, diff):
        self.content.drag(diff)
        if self.pixelStep != 0:
            self.barButton.setPosition(self.barButton.relativeX, min(self.barButton.maxButtonHeight(), self.barButton.relativeY - round(diff / self.pixelStep)))

    def onMouseDrop(self, widget, x, y, modifiers):
        if self.parent != self.desktop:
            self.parent.runCallback("onMouseDrop", widget, x, y, modifiers)

    def addChild(self, widget):
        try:
            _ = self.content
            raise Exception("Do not add widget to scroll. Add it to scroll.content as parent.")
        except Exception:
            pass

        Container.addChild(self, widget)

    def getPathHeight(self):
        return self.height - BUTTON_HEIGHT * 2

    def setBarSize(self):
        contentHeight = self.content.height
        if contentHeight == 0:
            self.hideBar()
            self.barButton.setHeight(self.height - BUTTON_HEIGHT * 2)
            self.pixelStep = 0
        else:
            pixelStep = min(1.0, float(self.height) / float(contentHeight))
            size = max(14, int(self.getPathHeight()) * pixelStep)
            self.barButton.setHeight(size)
            if pixelStep == 1.0:
                self.hideBar()
                self.pixelStep = 0
                return
            self.showBar()
            path = self.getPathHeight() - self.barButton.height
            move = contentHeight - self.height
            self.pixelStep = float(move) / float(path)

    def getContentHeight(self):
        return self.content.height

    def contentAdded(self):
        self.fitToContent()
        self.pushToBottom()

    def contentChangedSize(self):
        fit = self.getFit()
        self.setManualFit()
        self.content.clean()
        self.setBarSize()
        Container.contentChangedSize(self)
        self.updateContentPosition()
        self.pushToTop()
        self.setFitSilent(fit)

    def fitToContent(self):
        self.content.fitToContent()
        Container.fitToContent(self)
        self.content.clean()
        self.updateContentPosition()
        self.setBarSize()

    def fitToContentChange(self):
        """ A new content fit, but also readjusts the scroll bar based on the content change.
            This should fix issues with content not moving after being deleted.
        """
        beforeChange = self.content.height
        self.content.fitToContent()
        Container.fitToContent(self)
        self.content.clean()
        self.updateContentPosition()
        self.setBarSize()
        diff = beforeChange - self.content.height
        self.pushToDiff(diff)

    def hide(self):
        Container.hide(self)
        self.content.group.visible = False

    def show(self):
        Container.show(self)
        self.setOnTop()
        self.setActive()
        self.content.group.visible = True

    def setAutoFit(self):
        self.content.setAutoFit()
        Container.setAutoFit(self)

    def setManualFit(self):
        self.content.setManualFit()
        Container.setManualFit(self)
