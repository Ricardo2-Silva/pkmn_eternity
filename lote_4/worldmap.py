# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\interface\map\worldmap.py
"""
Created on Nov 11, 2017

@author: Admin
"""
from client.control.gui.windows import Window, Header, Button
from client.game import desktop
from client.data.gui import styleDB
from client.control.gui.container import Container
from client.control.gui.scrollbox import ScrollContent, ScrollableContainer
from client.render.cache import textureCache
from client.control.gui.picture import Picture
from client.control.camera import SimpleCamera
from client.control.events.event import eventManager
from client.interface import tooltip
import pyglet
from client.data.settings import gameSettings

def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))


class WorldBackground(Picture):

    def __init__(self, parent):
        image = textureCache.getBackground("worldmap")
        Picture.__init__(self, parent, picture=image, size=(image.width, image.height), autosize=(False,
                                                                                                  False), visible=True)


class WorldContainer(ScrollableContainer):

    def __init__(self, parent):
        ScrollableContainer.__init__(self, parent, position=(0, 0), size=(250, 250), visible=False, autosize=(False,
                                                                                                              False), mouseScroll=False, draggable=True)
        self.camera = SimpleCamera(250, 250)
        self.camera.updateBounds = self.updateBounds

    def isContainer(self):
        return False

    def updateBounds(self):
        """ Update the current bounds of the camera. """
        self.updateValues()
        squareBounds = self._getSquareBounds(self.offsetX, self.offsetX + self._realWidth / self.zoom, self.offsetY + self._realHeight / self.zoom, self.offsetY)
        if squareBounds != self._oldSquareBounds:
            self._oldSquareBounds = squareBounds

    def setRelativePosition(self, x, y):
        ScrollableContainer.setRelativePosition(self, x, y)

    def manageOverflow(self):
        for widget in self.content.widgets:
            widget.updatePosition()

        self.content.inAreaWidgets = self.content.getWidgetsInArea(self)
        for widget in self.content.inAreaWidgets:
            widget.updatePosition()

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        nx, ny = self.content.getRelativePosition()
        xValue = clamp(nx + dx, -self.parent.mapImg.width + self.width, 0)
        yValue = clamp(ny - dy, -self.parent.mapImg.height + self.height, 0)
        if xValue >= 0 or xValue <= -self.parent.mapImg.width + self.width:
            dx = 0
        if yValue >= 0 or yValue <= -self.parent.mapImg.height + self.height:
            dy = 0
        if dx != 0 or dy != 0:
            self.moveContentWidgets(dx, -dy)
            self.parent.setMapPosition(self.parent.currentPosition[0] - dx * self.parent.zoom, self.parent.currentPosition[1] - -dy * self.parent.zoom)

    def updateMapPosition(self):
        self.parent.mapImg.updatePosition()

    def moveContentWidgets(self, diffx, diffy):
        self.content.setRelativePosition(self.content.relativeX + diffx, self.content.relativeY + diffy)


class WorldMapWindow(Window):
    database = [
     ('Aster Town', (517, 1223), (24, 24)), 
     ('Magnolia Village', (530, 1090), (24, 24)), 
     ('Mt. Crescent', (511, 1046), (50, 40)), 
     ('Mt. Crescent', (616, 1095), (41, 26)), 
     ('Albite Town', (646, 1056), (51, 27)), 
     ('Crystalline Mine', (710, 1054), (83, 62)), 
     ('Route 1', (486, 1123), (121, 83)), 
     ('Route 2', (504, 1079), (25, 44))]

    def __init__(self):
        Window.__init__(self, desktop, position=(150, 150), size=(250, 270), style=(styleDB.windowsDefaultStyleNoPadding), visible=False, autosize=(False,
                                                                                                                                                    False))
        self.zoom = 1.0
        self.locations = []
        self.screen = WorldContainer(self)
        self.mapImg = WorldBackground(self.screen.content)
        self.mapImg.setSize(self.mapImg.picture.width / self.zoom, self.mapImg.picture.height / self.zoom)
        self.screen.addCallback("onMouseScroll", self.zoomMap)
        for value in self.database:
            name, position, size = value
            button = Button((self.screen.content), text="", position=position, size=size, autosize=(False,
                                                                                                    False), style=(styleDB.simpleButtonStyle))
            button.location = name
            button.addCallback("onMouseOver", self.showTooltip)
            button.addCallback("onMouseLeave", self.hideTooltip)

        self.screen.fitToContent()
        self.currentPosition = [
         517, 1223]
        (self.setMapPosition)(*self.currentPosition)
        Header(self, "World Map", close=True)

    def show(self):
        super().show()
        self.screen.show()

    def hide(self):
        super().hide()
        self.screen.hide()

    def showTooltip(self, widget, x, y):
        eventManager.notify("onShowTooltip", widget.location, x, y)

    def hideTooltip(self, widget):
        eventManager.notify("onCloseTooltip")

    def convertPositionCenter(self, x, y):
        width, height = self.screen.size
        nx = x - width / 2.0
        ny = y - height / 2.0
        return self.keepRectInMap(nx, ny)

    def keepRectInMap(self, x, y):
        x = clamp(x, 0, self.mapImg.width - self.screen.width)
        y = clamp(y, 0, self.mapImg.height - self.screen.height)
        return (
         x, y)

    def zoomMap(self, x, y, value):
        if value < 0:
            value = -1.0
        else:
            value = 1.0
        zoom = max(1.0, min(3.0, self.zoom + value))
        self.mapImg.setSize(self.mapImg.picture.width / zoom, self.mapImg.picture.height / zoom)
        for button in self.locations:
            button.setSize(int(22.0 / zoom), int(22.0 / zoom))
            x, y = button.originalPosition
            button.setPosition(x / zoom, y / zoom)

        self.zoom = zoom
        (self.setMapPosition)(*self.currentPosition)

    def setMapPosition(self, x, y):
        self.currentPosition = [
         x, y]
        x, y = self.convertPositionCenter(x / self.zoom, y / self.zoom)
        self.screen.content.setRelativePosition(-x, -y)


class WorldMap:

    def __init__(self):
        self.window = WorldMapWindow()
        eventManager.registerListener(self)

    def onHotkeyPress(self, hotkeyName):
        if hotkeyName == "worldmap":
            self.window.toggle()


worldMap = WorldMap()
