# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\gui\widget.py
""" Widgets """
from client.control.events.event import InterfaceDynamicEventListener
from client.control.utils.anchor import getAnchorOffsets
from client.data.gui import styleDB
from client.data.gui.padding import PaddingData
from client.data.utils.anchor import AnchorType
from client.render.gui.core import BasicRender, WidgetRender
from shared.container.constants import CursorMode
from shared.container.geometry import InterfacePositionable

class Widget(InterfaceDynamicEventListener, InterfacePositionable):
    renderClass = WidgetRender
    alwaysBehind = False
    alwaysOnTop = False
    maxDepth = 1
    focusEnabled = True
    push = True

    @property
    def name(self):
        return self.__class__.__name__

    def __init__(self, parent, position=(0, 0), size=(0, 0), draggable=False, visible=True, enableEvents=True):
        self.id = None
        self.parent = parent
        self.anchorWasSet = False
        self.visible = visible
        self.draggable = draggable
        self.anchor = False
        self.stackableAnchor = False
        self.eventsEnabled = enableEvents
        self.margins = None
        self.relativeX = 0
        self.relativeY = 0
        self._order = 0
        self.autoFit = False
        self.horStackableAnchor = False
        self.vertStackableAnchor = False
        if isinstance(position, int):
            self.anchor = position
            self._setStackableProperties()
            position = (0, 0)
        else:
            self.anchor = None
        (InterfacePositionable.__init__)(self, *position, *size)
        InterfaceDynamicEventListener.__init__(self)
        self._desktop = self.desktop
        self.root = self.getRoot()
        self.renderer = self.renderClass(self)
        (self.setPosition)(*position)
        if self.parent:
            self.parent.addChild(self)

    @property
    def order(self):
        """ Get the Z order of the widget, or it's parent """
        return self._order

    @order.setter
    def order(self, value):
        self._order = value
        self.renderer.order = value

    def setAlwaysBehind(self):
        """ The widget will never be pushed on top """
        self.alwaysBehind = True
        self.desktop.setAlwaysBehind(self)

    def setAlwaysOnTop(self):
        """ The widget will never be pushed on top """
        self.alwaysBehind = False
        self.desktop.setAlwaysOnTop(self)

    @property
    def desktop(self):
        root = self
        while root.parent:
            root = root.parent

        return root

    def getRoot(self):
        """Gets the very first parent that isn't the desktop of a widget.
           Required because widgets may be inside multiple containers down the chain.
        """
        if not self.parent:
            return self
        else:
            root = self
            while root.parent != self._desktop:
                root = root.parent

            return root

    def getVisibleState(self):
        """ This checks from base widget to root parent if any of it's parents are visible, if any aren't, hide it. """
        if self.visible is False:
            return False
        else:
            root = self
            while root.parent:
                if root.parent.visible is False:
                    return False
                root = root.parent

            return True

    @property
    def batch(self):
        return self.parent.batch

    @property
    def transparentBatch(self):
        return self._desktop.transparent

    @property
    def group(self):
        if self.parent:
            return self.parent.group
        else:
            return self._desktop.parent

    @group.setter
    def group(self, group):
        self.renderer.group = group

    def isContainer(self):
        return False

    def isAlwaysBehind(self):
        return self.alwaysBehind

    def isAlwaysOnTop(self):
        return self.alwaysOnTop

    def isFullAutosize(self):
        return self.autosize[0] and self.autosize[1]

    def getMargins(self):
        if not self.margins:
            return styleDB.noMargins
        else:
            return self.margins

    def setMargins(self, top, bottom, left, right):
        self.margins = PaddingData(top, bottom, left, right)
        self.parent.childChangedSize(self)

    def hasAnchor(self):
        return self.anchor

    def delAnchor(self):
        self.parent.delWidgetFromAnchorList(self)
        self.anchor = None

    def _setStackableProperties(self):
        self.horStackableAnchor = False
        self.vertStackableAnchor = False
        if self.anchor in AnchorType.HORIZONTAL_STACKABLE:
            self.horStackableAnchor = True
        if self.anchor in AnchorType.VERTICAL_STACKABLE:
            self.verStackableAnchor = True

    def setAnchor(self, anchor):
        if self.visible:
            if self.hasAnchor():
                self.parent.delWidgetFromAnchorList(self)
        self.anchor = anchor
        if self.visible:
            self.parent.addWidgetToAnchorList(self)
        self._setStackableProperties()

    def hasVerticalStackableAnchor(self):
        return self.vertStackableAnchor

    def hasHorizontalStackableAnchor(self):
        return self.horStackableAnchor

    def getAnchor(self):
        return self.anchor

    def setOnTop(self):
        if not self.visible:
            raise Exception("Trying to set on top invisible widget.", self.__class__.__name__, self.visible)

    def __str__(self):
        return self.__class__.__name__

    def setSize(self, width, height):
        self.width = width
        self.height = height
        self.parent.childChangedSize(self)

    def setWidth(self, width):
        self.width = width
        self.parent.childChangedSize(self)

    def setHeight(self, height):
        self.height = height
        self.parent.childChangedSize(self)

    def setId(self, widgetId):
        self.desktop.childGetId(self, widgetId)

    def setActive(self):
        """ tell desktop widget is active. """
        self.desktop.setActive(self)

    def setInactive(self):
        self.desktop.setInactive(self)

    def clone(self, parent=desktop):
        return Widget(parent, self.getRelativePosition(), self.size, self.draggable, True)

    def setParent(self, parent):
        self.parent.delChild(self)
        self.parent = parent
        self.parent.addChild(self)
        self.root = self.getRoot()

    def setOrigins(self):
        self.originX, self.originY = self.getRelativePosition()
        self.originGroup = self.group

    def isDraggable(self):
        """ Tells if a widget can be dragged or not. """
        return self.draggable

    def disableEvents(self):
        """ Make the widget ignore all type of events. """
        if self.eventsEnabled is False:
            raise "The widget does not react to events already."
        self.eventsEnabled = False
        self.parent.setChildIgnoreEvents(self)
        self.desktop.widgetGotDisabled(self)

    def enableEvents(self):
        """ Make the widget ignore all type of events. """
        if self.eventsEnabled is True:
            raise "The widget reacts to events already."
        self.eventsEnabled = True
        self.parent.setChildReactEvents(self)

    def getRelativePosition(self, offx=0, offy=0):
        return (
         self.relativeX + offx, self.relativeY + offy)

    def getRelativeCenter(self):
        px, py = self.parent.getCenter()
        x, y = self.getCenter()
        return (px - x, py - y)

    def setRelativePosition(self, x, y):
        self.relativeX = x
        self.relativeY = y
        self.updatePosition()

    def updatePosition(self):
        self.x, self.y = self.parent.getTopLeftPadded(offx=(self.relativeX), offy=(self.relativeY))

    def updatePositionDragging(self):
        self.x, self.y = self.parent.getTopLeftPadded(offx=(self.relativeX), offy=(self.relativeY))

    def updateRealPosition(self):
        Widget.setPosition(self, self.relativeX, self.relativeY)

    def isEventsEnabled(self):
        return self.eventsEnabled

    def getPadding(self):
        return styleDB.defaultPadding

    def setRealPosition(self, x, y):
        self._setX(x)
        self._setY(y)

    def setPosition(self, x, y):
        """ set the position of a widget, relatively to its parent's position. Add padding."""
        self.relativeX = x
        self.relativeY = y
        if self.parent:
            x, y = self.parent.getTopLeftPadded(offx=x, offy=y)
        self.x, self.y = x, y

    def setX(self, x):
        self.relativeX = x
        self.x, self.y = self.parent.getTopLeftPadded(offx=x, offy=(self.relativeY))

    def setY(self, y):
        self.relativeY = y
        self.x, self.y = self.parent.getTopLeftPadded(offx=(self.relativeX), offy=y)

    def getAnchorPosition(self, position):
        return getAnchorOffsets(self.parent, self, position, self.parent.getPadding())

    def _enable(self):
        """ Make the widget reacting. It appear """
        if self.visible == True:
            raise Exception(f"The widget is already enabled, you can't make it enabled again. {self.__class__.__name__}")
        self.visible = True

    def _disable(self):
        """ Make the widget not react to anything. It disappear. """
        if self.visible == False:
            raise Exception(f"The widget is already disabled, you can't make it disable again. {self.__class__.__name__}")
        self.visible = False

    def show(self):
        if not self.visible:
            self.unHide()

    def close(self):
        if self.visible:
            self.hide()

    def forceHide(self):
        if self.visible:
            self.hide()

    def forceUnHide(self):
        if not self.visible:
            self.unHide()

    def hide(self):
        """ Put the widget to an hidden state. """
        self._disable()
        self.parent.setChildHide(self)

    def unHide(self):
        """ This function is meant to be called from anywhere. But not from a container who wants to
        hide its childs, use setParentHasGotVisible instead. """
        self._enable()
        self.parent.setChildUnHide(self)
        self.updatePosition()

    def hasChilds(self):
        return False

    def onMouseDragBegin(self, widget, x, y, modifiers):
        self.setOrigins()
        self.desktop.cursor.mode = CursorMode.DRAGBEGIN
        if self.group.__class__.__name__ == "ClipGroup":
            self.group = self.desktop.group

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        """ Move a widget """
        self.drag(dx, -dy)
        self.desktop.cursor.mode = CursorMode.DRAGGING

    def drag(self, dx, dy):
        self.relativeX += dx
        self.relativeY += dy

    def onMouseDrop(self, widget, x, y, modifiers):
        self.setRelativePosition(self.originX, self.originY)
        if self.group != self.originGroup:
            self.group = self.originGroup

    def destroy(self):
        """ Destroy a widget, will permanently remove sprites and widget. """
        if self.visible:
            self.parent.setChildHide(self)
        self.visible = False
        self.parent.setChildDestroy(self)
        if self.desktop.overedWidget == self:
            self.desktop.overedWidget.runCallback("onMouseLeave", self)
            self.desktop.overedWidget = None
        self.renderer.delete()

    def ignoreContainerArea(self):
        """ Do not ignore the widget if we click on it"""
        return False


class InterfaceStylized(object):
    __doc__ = " Make a widget having a render. "

    def __init__(self, style):
        self.style = style.copy()

    def getMargins(self):
        if not self.margins:
            return self.style.margins
        else:
            return self.margins

    def getStyle(self):
        """ returns the style of the Widget being rendered. must be implemented """
        return self.style

    def getPadding(self):
        padding = self.getStyle().padding
        if padding:
            return padding
        else:
            return styleDB.defaultPadding

    def getPaddedWidth(self):
        """ returns the widget width, without its padding. """
        return self.width - self.getStyle().padding.left - self.getStyle().padding.right

    def getPaddedHeight(self):
        """ returns the widget height, without its padding. """
        return self.height - self.getStyle().padding.top - self.getStyle().padding.bottom

    def getPaddedSize(self):
        return (
         self.getPaddedWidth(), self.getPaddedHeight())

    def setColor(self, r, g, b):
        """ Colors must be between 0 and 255 """
        self.renderer.setColor(r, g, b)

    def setAlpha(self, alpha):
        """ Alpha must be between 0 and 255 """
        self.renderer.setAlpha(alpha)

    def fadeOut(self, duration):
        self.renderer.fadeOut(duration)

    def fadeTo(self, duration, alpha):
        self.renderer.fadeTo(duration, alpha)

    def setBackgroundColor(self, r, g, b):
        self.getStyle().background.color = (
         r, g, b)
        self.renderer.setBackgroundColor(r, b, b)

    def updateRenderSize(self):
        """ Only updates the render's size. """
        self.renderer.updateSize()

    def updateRenderPosition(self):
        """ Only updates the render's size. """
        self.renderer.updatePosition()


class StylizedWidget(InterfaceStylized, Widget):
    renderClass = BasicRender

    def __init__(self, style, parent, position=(0, 0), size=(0, 0), draggable=False, visible=True, enableEvents=True):
        InterfaceStylized.__init__(self, style)
        Widget.__init__(self, parent, position, size, draggable, visible, enableEvents)
        (self.setSize)(*self.size)
        if isinstance(position, int):
            self.setAnchor(position)
            (self.setPosition)(*self.getAnchorPosition(position))
        else:
            self.setPosition(self.relativeX, self.relativeY)

    def resetRenderState(self):
        self.renderer.resetRenderState()

    def setPositionNoRender(self, x, y, z=0):
        Widget.setPosition(self, x, y)

    def setRenderPosition(self, interp):
        self.renderer.setRenderPosition(interp)

    def setPosition(self, x, y):
        Widget.setPosition(self, x, y)
        self.renderer.updatePosition()

    def setX(self, x):
        Widget.setX(self, x)
        self.renderer.updatePosition()

    def setY(self, y):
        Widget.setY(self, y)
        self.renderer.updatePosition()

    def setSize(self, width, height):
        Widget.setSize(self, width, height)
        self.renderer.updateSize()

    def setHeight(self, height):
        Widget.setHeight(self, height)
        self.renderer.updateSize()

    def setWidth(self, width):
        Widget.setWidth(self, width)
        self.renderer.updateSize()

    def destroy(self):
        """ Block the widget from being rendered """
        Widget.destroy(self)
        self.renderer.delete()

    def refresh(self):
        self.renderer.refresh()

    def updatePosition(self):
        Widget.updatePosition(self)
        self.renderer.updatePosition()

    def updatePositionDragging(self):
        Widget.updatePositionDragging(self)
        self.renderer.updatePosition()
