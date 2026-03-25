# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\gui\core.py
from client.data.settings import gameSettings
from client.data.utils.anchor import AnchorType
from rabbyt import collisions
from shared.container.geometry import Point2D
from functools import reduce
scale = gameSettings.getUIScale()

class Size:
    WIDTH = 0
    HEIGHT = 1
    SIZES = [WIDTH, HEIGHT]


class AnchorWidgetsInterface:

    def __init__(self):
        """ Initialize anchor lists & dicts """
        self.anchors = {}
        self.anchorSizes = {}
        self.anchorLastPositions = {(AnchorType.TOP): 0, 
         (AnchorType.LEFT): 0, 
         (AnchorType.BOTTOM): (self.getPaddedHeight()), 
         (AnchorType.RIGHT): (self.getPaddedWidth())}
        for anchor1 in AnchorType.VERTICAL + AnchorType.HORIZONTAL_LINKS:
            self.anchors[anchor1] = {}
            self.anchorSizes[anchor1] = {(Size.WIDTH): {}, (Size.HEIGHT): {}}
            for anchor2 in AnchorType.VERTICAL_LINKS:
                self.anchors[anchor1][anchor2] = []
                self.anchorSizes[anchor1][Size.WIDTH][anchor2] = 0
                self.anchorSizes[anchor1][Size.HEIGHT][anchor2] = 0

        for anchor1 in AnchorType.HORIZONTAL + AnchorType.VERTICAL_LINKS:
            self.anchors[anchor1] = {}
            self.anchorSizes[anchor1] = {(Size.WIDTH): {}, (Size.HEIGHT): {}}
            for anchor2 in AnchorType.HORIZONTAL_LINKS:
                self.anchors[anchor1][anchor2] = []
                self.anchorSizes[anchor1][Size.WIDTH][anchor2] = 0
                self.anchorSizes[anchor1][Size.HEIGHT][anchor2] = 0

        self.anchorWidth, self.anchorHeight = (0, 0)

    def calculateAnchorSize(self, anchor1, anchor2):
        """ Calculate height and width for specified anchors """
        if anchor1 not in self.anchors:
            raise Exception("Anchor 1 does not exists.", AnchorType.toStr[anchor1])
        if anchor2 not in self.anchors[anchor1]:
            raise Exception("Anchor 2 doest not exists.", AnchorType.toStr[anchor1], AnchorType.toStr[anchor2])
        for anchor in (anchor1, anchor2):
            if anchor in AnchorType.VERTICAL:
                height = reduce((lambda zero, widget: zero + widget.height + widget.getMargins().top + widget.getMargins().bottom), self.anchors[anchor1][anchor2], 0)
            elif anchor in AnchorType.HORIZONTAL:
                width = reduce((lambda zero, widget: zero + widget.width + widget.getMargins().left + widget.getMargins().right), self.anchors[anchor1][anchor2], 0)
            elif anchor in AnchorType.VERTICAL_LINKS:
                width = reduce((lambda zero, widget: max(zero, widget.width + widget.getMargins().left + widget.getMargins().right)), self.anchors[anchor1][anchor2], 0)
            else:
                if anchor in AnchorType.HORIZONTAL_LINKS:
                    height = reduce((lambda zero, widget: max(zero, widget.height + widget.getMargins().top + widget.getMargins().bottom)), self.anchors[anchor1][anchor2], 0)

        self.anchorSizes[anchor1][Size.WIDTH][anchor2] = width
        self.anchorSizes[anchor1][Size.HEIGHT][anchor2] = height

    def setWidgetAnchoredPosition(self, widget, anchor):
        """ Replace widget on specified anchors. This function can only be called when
        The anchor sizes have been calculated.  """
        widget.anchorWasSet = True
        if anchor & AnchorType.TOP:
            y = self.anchorLastPositions[AnchorType.TOP]
            y += widget.getMargins().top
            widget.setY(y)
            y += widget.height
            y += widget.getMargins().bottom
            self.anchorLastPositions[AnchorType.TOP] = y
        if anchor & AnchorType._TOP_FIXED:
            y = widget.getMargins().top
            widget.setY(y)
        if anchor & AnchorType.BOTTOM:
            y = self.anchorLastPositions[AnchorType.BOTTOM]
            y -= widget.getMargins().bottom
            y -= widget.height
            widget.setY(y)
            y -= widget.getMargins().top
            self.anchorLastPositions[AnchorType.BOTTOM] = y
        if anchor & AnchorType._BOTTOM_FIXED:
            y = self.getPaddedHeight() - widget.height - widget.getMargins().bottom
            widget.setY(y)
        if anchor & AnchorType._CENTERY_FIXED:
            y = self.getPaddedHeight() // 2 - (widget.height + widget.getMargins().bottom + widget.getMargins().top) // 2
            widget.setY(y + widget.getMargins().top)
        if anchor & AnchorType.LEFT:
            x = self.anchorLastPositions[AnchorType.LEFT]
            x += widget.getMargins().left
            widget.setX(x)
            x += widget.width
            x += widget.getMargins().right
            self.anchorLastPositions[AnchorType.LEFT] = x
        if anchor & AnchorType._LEFT_FIXED:
            x = widget.getMargins().left
            widget.setX(x)
        if anchor & AnchorType.RIGHT:
            x = self.anchorLastPositions[AnchorType.RIGHT]
            x -= widget.getMargins().right
            x -= widget.width
            widget.setX(x)
            x -= widget.getMargins().left
            self.anchorLastPositions[AnchorType.RIGHT] = x
        if anchor & AnchorType._RIGHT_FIXED:
            x = self.getPaddedWidth() - widget.getMargins().right - widget.width
            widget.setX(x)
        if anchor & AnchorType._CENTERX_FIXED:
            x = self.getPaddedWidth() // 2 - (widget.width + widget.getMargins().left + widget.getMargins().right) // 2
            widget.setX(x + widget.getMargins().left)

    def replaceWidgets(self, anchor1, anchor2):
        """ Replace widget on specified anchors. This function can only be called when
        The anchor sizes have been calculated.  """
        widgets = self.anchors[anchor1][anchor2]
        for anchor in (anchor1, anchor2):
            if anchor == AnchorType.TOP:
                y = 0
                for widget in widgets:
                    y += widget.getMargins().top
                    widget.setY(y)
                    y += widget.height
                    y += widget.getMargins().bottom

                self.anchorLastPositions[AnchorType.TOP] = y
            elif anchor == AnchorType._TOP_FIXED:
                for widget in widgets:
                    y = widget.getMargins().top
                    widget.setY(y)

            elif anchor == AnchorType.BOTTOM:
                y = self.getPaddedHeight()
                for widget in widgets:
                    y -= widget.getMargins().bottom
                    y -= widget.height
                    widget.setY(y)
                    y -= widget.getMargins().top

                self.anchorLastPositions[AnchorType.BOTTOM] = y
            elif anchor == AnchorType._BOTTOM_FIXED:
                for widget in widgets:
                    y = self.getPaddedHeight() - widget.height - widget.getMargins().bottom
                    widget.setY(y)

            elif anchor == AnchorType.CENTERY == anchor1:
                winCentery = self.getPaddedHeight() // 2 - self.anchorSizes[anchor1][Size.HEIGHT][anchor2] // 2
                y = winCentery
                for widget in widgets:
                    y += widget.getMargins().top
                    widget.setY(y)
                    y += widget.height
                    y += widget.getMargins().bottom

            elif anchor == AnchorType._CENTERY_FIXED:
                for widget in widgets:
                    y = self.getPaddedHeight() // 2 - (widget.height + widget.getMargins().bottom + widget.getMargins().top) // 2
                    widget.setY(y + widget.getMargins().top)

            elif anchor == AnchorType.LEFT:
                x = 0
                for widget in widgets:
                    x += widget.getMargins().left
                    widget.setX(x)
                    x += widget.width
                    x += widget.getMargins().right

                self.anchorLastPositions[AnchorType.LEFT] = x
            elif anchor == AnchorType._LEFT_FIXED:
                for widget in widgets:
                    x = widget.getMargins().left
                    widget.setX(x)

            elif anchor == AnchorType.RIGHT:
                x = self.getPaddedWidth()
                for widget in widgets:
                    x -= widget.getMargins().right
                    x -= widget.width
                    widget.setX(x)
                    x -= widget.getMargins().left

                self.anchorLastPositions[AnchorType.RIGHT] = x
            elif anchor == AnchorType._RIGHT_FIXED:
                for widget in widgets:
                    x = self.getPaddedWidth() - widget.getMargins().right - widget.width
                    widget.setX(x)

            elif anchor == AnchorType.CENTERX == anchor1:
                winCenterx = self.getPaddedWidth() // 2 - self.anchorSizes[anchor1][Size.WIDTH][anchor2] // 2
                x = winCenterx
                for widget in widgets:
                    x += widget.getMargins().left
                    widget.setX(x)
                    x += widget.width + widget.getMargins().right

            else:
                if anchor == AnchorType._CENTERX_FIXED:
                    for widget in widgets:
                        x = self.getPaddedWidth() // 2 - (widget.width + widget.getMargins().left + widget.getMargins().right) // 2
                        widget.setX(x + widget.getMargins().left)

    def _calculateAllSizes(self):
        for anchor1 in AnchorType.VERTICAL + AnchorType.HORIZONTAL_LINKS:
            for anchor2 in AnchorType.VERTICAL_LINKS:
                self.calculateAnchorSize(anchor1, anchor2)

        for anchor1 in AnchorType.HORIZONTAL + AnchorType.VERTICAL_LINKS:
            for anchor2 in AnchorType.HORIZONTAL_LINKS:
                self.calculateAnchorSize(anchor1, anchor2)

    def replaceAnchoredWidgets(self):
        """ This function must be called once the windows size has been set. """
        for anchor1 in AnchorType.VERTICAL + AnchorType.HORIZONTAL_LINKS:
            for anchor2 in AnchorType.VERTICAL_LINKS:
                self.replaceWidgets(anchor1, anchor2)

        for anchor1 in AnchorType.HORIZONTAL + AnchorType.VERTICAL_LINKS:
            for anchor2 in AnchorType.HORIZONTAL_LINKS:
                self.replaceWidgets(anchor1, anchor2)

    def _setAnchorSize(self):
        height = 0
        for anchor1 in AnchorType.VERTICAL:
            height += max(self.anchorSizes[anchor1][Size.HEIGHT].values())

        width = 0
        for anchor1 in AnchorType.HORIZONTAL:
            v = max(self.anchorSizes[anchor1][Size.WIDTH].values())
            width += v

        for anchor1 in AnchorType.VERTICAL + AnchorType.HORIZONTAL_LINKS:
            for anchor2 in AnchorType.VERTICAL_LINKS:
                width = max(width, self.anchorSizes[anchor1][Size.WIDTH][anchor2])

        for anchor1 in AnchorType.HORIZONTAL + AnchorType.VERTICAL_LINKS:
            for anchor2 in AnchorType.HORIZONTAL_LINKS:
                height = max(height, self.anchorSizes[anchor1][Size.HEIGHT][anchor2])

        self.anchorHeight = height
        self.anchorWidth = width

    def setAnchorSize(self):
        """ Must be called to set the content size """
        self._calculateAllSizes()
        self._setAnchorSize()

    def addWidgetToAnchorList(self, widget):
        """ Must be called after adding a widget with an anchor """
        anchor = widget.getAnchor()
        found = 0
        for anchor1 in AnchorType.ALL_NORMAL:
            if anchor & anchor1:
                anchor2 = anchor ^ anchor1
                if widget in self.anchors[anchor1][anchor2]:
                    raise Exception("Widget already anchored there.")
                self.anchors[anchor1][anchor2].append(widget)
                found = 1

        if not found:
            for anchor1 in AnchorType.ALL_FIXED:
                if anchor & anchor1:
                    anchor2 = anchor ^ anchor1
                    if anchor2 not in AnchorType.ALL_FIXED:
                        raise Exception("The anchoring is wrong.")
                    if widget in self.anchors[anchor1][anchor2]:
                        raise Exception("Widget already anchored there.")
                    self.anchors[anchor1][anchor2].append(widget)
                    found = 1

        if not found:
            raise Exception("(Adding widget to anchor list) The anchoring is wrong.")
        if not widget.anchorWasSet:
            self.setWidgetAnchoredPosition(widget, anchor)

    def delWidgetFromAnchorList(self, widget):
        """ Must be called after adding a widget with an anchor """
        anchor = widget.getAnchor()
        found = 0
        for anchor1 in AnchorType.ALL_NORMAL:
            if anchor & anchor1:
                anchor2 = anchor ^ anchor1
                self.anchors[anchor1][anchor2].remove(widget)
                found = 1

        if not found:
            for anchor1 in AnchorType.ALL_FIXED:
                if anchor & anchor1:
                    anchor2 = anchor ^ anchor1
                    if anchor2 not in AnchorType.ALL_FIXED:
                        raise Exception("The anchoring is wrong.")
                    self.anchors[anchor1][anchor2].remove(widget)
                    found = 1

        if not found:
            raise Exception("The anchoring is wrong.")


class AbstractContainer(AnchorWidgetsInterface):

    def __init__(self):
        self.widgets = []
        self.visibleWidgets = []
        self.widgetsAlwaysOnTop = []
        self.hiddenWidgets = []
        self.widgetById = {}
        self._order = 0
        self.reactingWidgets = []
        self.autoFit = True
        AnchorWidgetsInterface.__init__(self)

    def isContainer(self):
        return True

    @property
    def order(self):
        """ Get the Z order of the widget, or it's parent """
        return self._order

    @order.setter
    def order(self, value):
        self._order = value
        self.renderer.order = value
        self.reOrder()

    def hidevisibleWidgets(self):
        while self.visibleWidgets:
            self.visibleWidgets[0].hide()

    def widgetAdded(self):
        if self.isAutoFit():
            self.contentChangedSize()

    def widgetDeleted(self):
        if self.isAutoFit():
            self.contentChangedSize()

    def contentChangedSize(self):
        raise Exception("Content changed must be implemented !")

    def childChangedSize(self, child):
        if self.isAutoFit():
            self.contentChangedSize()

    def fitToContent(self):
        raise Exception("Fit To Content must be implemented !")

    def getVisibleWidgets(self):
        return self.visibleWidgets

    def getInvisibleWidgets(self):
        return self.hiddenWidgets

    def getWidgets(self):
        return self.widgets

    def _addChild(self, widget):
        self.widgets.append(widget)
        if widget.visible:
            self.visibleWidgets.append(widget)
            if widget.getVisibleState():
                self.reOrder()
        else:
            self.hiddenWidgets.append(widget)
        if widget.isEventsEnabled():
            if widget.visible:
                self.reactingWidgets.insert(0, widget)
        if widget.isAlwaysOnTop():
            self.widgetsAlwaysOnTop.append(widget)

    def reOrder(self):
        """ Reorders all child widgets to new order values. """
        order = self.order + 2
        for widget in self.visibleWidgets:
            widget.order = order
            order += widget.maxDepth

        self.maxDepth = order - self.order + 1

    def addChild(self, widget):
        self._addChild(widget)
        if widget.visible:
            if widget.hasAnchor():
                self.addWidgetToAnchorList(widget)
        self.widgetAdded()

    def setAutoFit(self):
        self.autoFit = True
        self.contentChangedSize()

    def setManualFit(self):
        self.autoFit = False

    def setFit(self, fit):
        if fit == True:
            self.setAutoFit()
        else:
            self.setManualFit()

    def setFitSilent(self, fit):
        self.autoFit = fit

    def getFit(self):
        return self.autoFit

    def isAutoFit(self):
        return self.autoFit

    def pushToTop(self, widget, parent=None):
        if self.visibleWidgets[-1] == widget:
            return
        self._delChild(widget)
        self._addChild(widget)
        if widget.parent != self:
            raise Exception("Not same parent.")

    def empty(self):
        """ delete all widget of container.."""
        while len(self.widgets) > 0:
            self.widgets[0].setParent(self.parent)

    def emptyAndDestroy(self):
        """ delete all widget of container and destroy them.."""
        while len(self.widgets) > 0:
            w = self.widgets[0]
            w.destroy()

    def _delChild(self, widget):
        if widget not in self.widgets:
            raise Exception("The widget can not be deleted because it's not in the widget list", widget.name, self.name)
        else:
            self.widgets.remove(widget)
            if widget in self.visibleWidgets:
                self.visibleWidgets.remove(widget)
            else:
                self.hiddenWidgets.remove(widget)
            if widget in self.reactingWidgets:
                self.reactingWidgets.remove(widget)
            if widget.isAlwaysOnTop():
                self.widgetsAlwaysOnTop.remove(widget)

    def delChild(self, widget):
        self._delChild(widget)
        if widget.visible:
            if widget.hasAnchor():
                self.delWidgetFromAnchorList(widget)
        self.widgetDeleted()

    def setChildIgnoreEvents(self, widget):
        if widget in self.reactingWidgets:
            self.reactingWidgets.remove(widget)

    def setChildReactEvents(self, widget):
        if widget not in self.reactingWidgets:
            self.reactingWidgets.insert(0, widget)

    def setChildHide(self, widget):
        self.visibleWidgets.remove(widget)
        self.hiddenWidgets.append(widget)
        if widget in self.reactingWidgets:
            self.reactingWidgets.remove(widget)
        if widget.hasAnchor():
            self.delWidgetFromAnchorList(widget)
        widget.renderer.visible = False

    def setChildDestroy(self, widget):
        self.widgets.remove(widget)
        self.hiddenWidgets.remove(widget)

    def setChildUnHide(self, widget):
        if widget in self.visibleWidgets:
            raise Exception("Can not be unhidden and be already in the enabledWidget list", widget.getName())
        else:
            if widget not in self.hiddenWidgets:
                raise Exception("Can not be unhidden and not be in the disabledWidget list", widget.getName())
            else:
                self.hiddenWidgets.remove(widget)
                self.visibleWidgets.append(widget)
                if widget.isEventsEnabled():
                    self.reactingWidgets.insert(0, widget)
                if widget.hasAnchor():
                    self.addWidgetToAnchorList(widget)
            if self.getVisibleState():
                widget.renderer.visible = True
                self.reOrder()

    def getCollidingWidget(self, x, y, exclude=[]):
        """ returns None if there is no widget at this position.
        it looks for the deepest widget that the mouse touch. windows->container->button..."""
        collidingWidgets = collisions.aabb_collide_single(Point2D(x // scale, y // scale), self.reactingWidgets)
        for c in [widget for widget in collidingWidgets if widget not in exclude]:
            if c:
                if c.hasChilds():
                    nc = c.getCollidingWidget(x, y)
                    if nc:
                        if not nc.ignoreContainerArea():
                            return nc
                if c:
                    if not c.ignoreContainerArea():
                        return c

        return

    def getWidgetsInArea(self, area):
        """ returns None if there is no widget at this position.
        it looks for the deepest widget that the mouse touch. windows->container->button..."""
        return collisions.aabb_collide_single(area, self.visibleWidgets)

    def destroy(self):
        """ Make sure all of its widget are destroyed. """
        while len(self.widgets) > 0:
            w = self.widgets[0]
            w.destroy()
