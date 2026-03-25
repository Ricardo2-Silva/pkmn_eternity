# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\gui\container.py
""" Containers """
from client.control.gui.core import AbstractContainer
from client.control.gui.widget import Widget, InterfaceStylized
import sys, pyglet
from client.data.gui.padding import PaddingData
from client.data import exceptions
from client.render.utils.patch import PatchType
from client.data.utils.color import Color
from client.data.gui import styleDB
from client.data.gui.style import BackgroundData
from functools import reduce
from client.render.gui.core import ContainerRender, StylizedContainerRender

class Container(AbstractContainer, Widget):
    renderClass = ContainerRender

    def __init__(self, parent, position=(0, 0), size=(0, 0), draggable=False, visible=True, autosize=(True, True)):
        self.autosize = autosize
        self.width = size[0]
        self.height = size[1]
        self.minHeight = size[1]
        self.maxHeight = sys.maxsize
        self.minWidth = size[0]
        self.maxWidth = sys.maxsize
        self._contentWidth = 0
        self._contentHeight = 0
        self.padding = styleDB.defaultPadding
        AbstractContainer.__init__(self)
        Widget.__init__(self, parent, position, size, draggable, visible)

    def destroy(self):
        AbstractContainer.destroy(self)
        Widget.destroy(self)

    def updateContentSize(self):
        self.setAnchorSize()
        self._setContentHeight()
        self._setContentWidth()

    def setMaxWidth(self, value):
        self.maxWidth = value
        if self.isAutoFit():
            self.contentChangedSize()

    def setMaxHeight(self, value):
        self.maxHeight = value
        if self.isAutoFit():
            self.contentChangedSize()

    def setMinHeight(self, value):
        self.minHeight = value
        if self.isAutoFit():
            self.contentChangedSize()

    def setMinWidth(self, value):
        self.minWidth = value
        if self.isAutoFit():
            self.contentChangedSize()

    def setChildUnHide(self, widget):
        AbstractContainer.setChildUnHide(self, widget)
        if self.isAutoFit():
            self.contentChangedSize()

    def empty(self):
        AbstractContainer.empty(self)
        self.contentChangedSize()

    def emptyAndDestroy(self):
        AbstractContainer.emptyAndDestroy(self)
        if self.isAutoFit():
            self.contentChangedSize()

    def setAlpha(self, alpha):
        for child in self.widgets:
            child.setAlpha(alpha)

    def setColors(self, r, g, b):
        for child in self.widgets:
            child.setColors(r, g, b)

    def getPadding(self):
        return self.padding

    def hasChilds(self):
        return len(self.widgets) > 0

    def setPadding(self, top, bottom, left, right):
        self.padding = PaddingData(top, bottom, left, right)

    def getAutosize(self):
        return self.autosize

    def isAutosize(self):
        return self.autosize[0] + self.autosize[1]

    def _getMinHeight(self):
        return min(self.maxHeight, max(self.minHeight, self._getContentHeight() + self.getPadding().bottom))

    def _getMinWidth(self):
        return min(self.maxWidth, max(self.minWidth, self._getContentWidth() + self.getPadding().right))

    def contentChangedSize(self):
        """ When content changes, container must autosize. """
        self.updateContentSize()
        if self.autosize[0]:
            if self.autosize[1]:
                Widget.setSize(self, self._getMinWidth(), self._getMinHeight())
        if self.autosize[0]:
            Widget.setWidth(self, self._getMinWidth())
        else:
            if self.autosize[1]:
                Widget.setHeight(self, self._getMinHeight())
        self.replaceAnchoredWidgets()

    def _setContentWidth(self):
        d = [x for x in self.visibleWidgets if not x.hasAnchor() if not x.__class__.__name__ == "Header"]
        cWidth = reduce((lambda x, y: max(x, max(self.x + self.getPadding().left, y.x) + y.width - self.x)), d, 0)
        cWidth = max(cWidth, self.anchorWidth + self.getPadding().left)
        self._contentWidth = cWidth

    def setSize(self, width, height):
        raise Exception("A container has the size of its content, you can't set its size.")

    def setHeight(self, height):
        raise Exception("A container has the size of its content, you can't set its size.")

    def setWidth(self, width):
        raise Exception("A container has the size of its content, you can't set its size.")

    def getSize(self):
        return (
         self.width, self.height)

    def _getContentWidth(self):
        return self._contentWidth

    def _getContentHeight(self):
        return self._contentHeight

    def _setContentHeight(self):
        cHeight = reduce((lambda x, y: max(x, max(self.y + self.getPadding().top, y.y) + (y.height - self.y))), [widget for widget in self.visibleWidgets if not widget.hasAnchor()], 0)
        cHeight = max(cHeight, self.anchorHeight + self.getPadding().top)
        self._contentHeight = cHeight

    def setPosition(self, x, y):
        Widget.setPosition(self, x, y)
        self.updateChildsPosition()

    def updatePosition(self):
        Widget.updatePosition(self)
        self.updateChildsPosition()

    def updatePositionDragging(self):
        Widget.updatePositionDragging(self)
        for child in self.visibleWidgets:
            child.updatePositionDragging()

    def setX(self, x):
        Widget.setX(self, x)
        self.updateChildsPosition()

    def setY(self, y):
        Widget.setY(self, y)
        self.updateChildsPosition()

    def updateChildsPosition(self):
        """ Update the position of all childs """
        for child in self.visibleWidgets:
            child.updatePosition()

    def fitToContent(self):
        """ resize container to fit with the widgets inside """
        if self.isAutoFit():
            raise Exception("It's useless to fit to content if the widget is in autoFit mode.")
        else:
            self.updateContentSize()
            if self.autosize[0]:
                if self.autosize[1]:
                    Widget.setSize(self, self._getMinWidth(), self._getMinHeight())
                if self.autosize[0]:
                    Widget.setWidth(self, self._getMinWidth())
            elif self.autosize[1]:
                Widget.setHeight(self, self._getMinHeight())
        self.replaceAnchoredWidgets()

    def ignoreContainerArea(self):
        """ ignore Container if we click on it, only take care of the widgets inside. """
        return True

    def setOnTop(self):
        if not self.visible:
            raise Exception("Trying to put on top something invisible !")
        for i in range(len(self.visibleWidgets) - 1, -1, -1):
            self.visibleWidgets[i].setOnTop()

        Widget.setOnTop(self)

    def getRelativeTopLeft(self, offx=0, offy=0):
        return (
         self.relativeX + offx, self.relativeY + offy)

    def getRelativeTopLeftPadded(self, offx=0, offy=0):
        return self.getRelativeTopLeft(self.getPadding().left + offx, self.getPadding().top + offy)

    def getTopLeftPadded(self, offx=0, offy=0):
        return (
         self.x + self.getPadding().left + offx, self.y + self.getPadding().top + offy)

    def getPaddedWidth(self):
        return self.width - self.getPadding().left - self.getPadding().right

    def getPaddedHeight(self):
        return self.height - self.getPadding().top - self.getPadding().bottom

    def getTopRightPadded(self, offx=0, offy=0):
        return self.getTopRight(-self.getPadding().right + offx, self.getPadding().top + offy)

    def getBottomRightPadded(self, offx=0, offy=0):
        return self.getBottomRight(-self.getPadding().right + offx, -self.getPadding().bottom + offy)

    def getBottomLeftPadded(self, offx=0, offy=0):
        return self.getBottomRight(self.getPadding().left + offx, -self.getPadding().bottom + offy)


class StylizedContainer(InterfaceStylized, Container):
    renderClass = StylizedContainerRender

    def __init__(self, style, parent, position, size, draggable, visible, autosize):
        InterfaceStylized.__init__(self, style)
        Container.__init__(self, parent, position, size, draggable, visible, autosize)
        self.setPosition(self.relativeX, self.relativeY)
        (self.setSize)(*self.size)

    def setBackground(self, image=None, color=None, alpha=None):
        size_changed = False
        if image:
            if self.getStyle().background is None:
                self.getStyle().background = BackgroundData(image=image)
                self.renderer.createBackgroundAndAdd()
        elif self.getStyle().background.image:
            if self.getStyle().background.image.width != image.width or self.getStyle().background.image.height != image.height:
                size_changed = True
            self.getStyle().background.image = image
            self.getStyle().background.patchType = PatchType.NOPATCH
        elif color:
            if self.getStyle().background is None:
                self.getStyle().background = BackgroundData(color=color)
                self.renderer.createBackgroundAndAdd()
            else:
                self.getStyle().background.color = color
        if alpha:
            self.getStyle().background.alpha = alpha
        self.renderer.refreshBackground()
        if size_changed:
            self.renderer.updateSize()
            self.renderer.updatePosition()

    def setBackgroundAnchor(self, anchor):
        self.getStyle().background.anchor = anchor
        self.renderer.refreshBackgroundPosition()

    def setAlpha(self, alpha):
        InterfaceStylized.setAlpha(self, alpha)
        Container.setAlpha(self, alpha)

    def setColor(self, r, g, b):
        InterfaceStylized.setColor(self, r, g, b)

    def setOnTop(self):
        Container.setOnTop(self)

    def setPosition(self, x, y):
        Container.setPosition(self, x, y)
        self.renderer.updatePosition()

    def setX(self, x):
        Container.setX(self, x)
        self.renderer.updatePosition()

    def setY(self, y):
        Container.setY(self, y)
        self.renderer.updatePosition()

    def setWidth(self, width):
        if self.autosize[0]:
            self.minWidth = width
            Widget.setWidth(self, self._getMinWidth())
        else:
            Widget.setWidth(self, width)
        self.renderer.updateSize()

    def setMinHeight(self, value):
        Container.setMinHeight(self, value)
        self.renderer.updateSize()

    def setMaxHeight(self, value):
        Container.setMaxHeight(self, value)
        self.renderer.updateSize()

    def setMaxWidth(self, value):
        Container.setMaxWidth(self, value)
        self.renderer.updateSize()

    def setMinWidth(self, value):
        Container.setMinWidth(self, value)
        self.renderer.updateSize()

    def setHeight(self, height):
        if self.autosize[1]:
            self.minHeight = height
            Widget.setHeight(self, self._getMinHeight())
        else:
            Widget.setHeight(self, height)
        self.renderer.updateSize()

    def setSize(self, width, height):
        if self.isFullAutosize():
            self.minWidth, self.minHeight = width, height
            Widget.setSize(self, self._getMinWidth(), self._getMinHeight())
        elif self.autosize[0]:
            self.minWidth = width
            Widget.setWidth(self, self._getMinWidth())
        else:
            Widget.setWidth(self, width)
        if self.autosize[1]:
            self.minHeight = height
            Widget.setHeight(self, self._getMinHeight())
        else:
            Widget.setHeight(self, height)
        self.renderer.updateSize()

    def fitToContent(self):
        """ resize container to fit with the widgets inside """
        Container.fitToContent(self)
        self.renderer.updateSize()

    def contentChangedSize(self):
        Container.contentChangedSize(self)
        self.renderer.updateSize()

    def updatePosition(self):
        Container.updatePosition(self)
        self.renderer.updatePosition()

    def updatePositionDragging(self):
        Container.updatePositionDragging(self)
        self.renderer.updatePosition()


class BackgroundContainer(StylizedContainer):

    def __init__(self, parent, bgImg, position=(0, 0), size=(0, 0), style=styleDB.windowsNoStyle, visible=True, alpha=255, autosize=(False, False)):
        StylizedContainer.__init__(self, style, parent, position, size, False, visible, autosize)
        self.setBackground(image=bgImg, alpha=alpha)


class AreaContainer(StylizedContainer):

    def __init__(self, parent, position, size, styleNormal, styleColor, alpha, color, visible=True, autosize=(True, True)):
        if color != Color.TRANSPARENT:
            StylizedContainer.__init__(self, styleColor, parent, position, size, False, visible, autosize)
            (self.setColor)(*color)
        else:
            StylizedContainer.__init__(self, styleNormal, parent, position, size, False, visible, autosize)
        if alpha != 255:
            self.setAlpha(alpha)


class ShadowContainer(AreaContainer):

    def __init__(self, parent, position, size, alpha=20, color=Color.TRANSPARENT, visible=True, autosize=(True, True)):
        AreaContainer.__init__(self, parent, position, size, (styleDB.shadowWidgetStyle), (styleDB.shadowColorWidgetStyle), alpha, color, visible=visible, autosize=autosize)


class LineRoundedContainer(AreaContainer):

    def __init__(self, parent, position, size, alpha=255, color=Color.TRANSPARENT, visible=True, autosize=(True, True)):
        AreaContainer.__init__(self, parent, position, size, (styleDB.lineRoundedStyle), (styleDB.lineFullRoundedStyle), alpha, color, visible=visible, autosize=autosize)
