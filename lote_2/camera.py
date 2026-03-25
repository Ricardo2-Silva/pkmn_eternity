# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\camera.py
import math, sys, pyglet, rabbyt
from client.control.events.event import eventManager, eventDispatcher
from client.data.container.map import mapContainer
from client.data.settings import gameSettings
from shared.container.constants import MapSettings, RefPointType
from shared.container.geometry import InterfacePositionable2D
from client.control.system.sound import gameListener
from shared.controller.maths.maths import lerp, interpolate, interpolatePosition2D
from shared.service.geometry import getDistanceBetweenTwoPoints
CHUNK_SIZE = 64

class SimpleCamera(InterfacePositionable2D):

    def __init__(self, width, height):
        self._oldOffsetY = 0
        self._oldOffsetX = 0
        self._oldZoom = 0
        self.zoom = 1
        self._offsetX = 0
        self._offsetY = 0
        self.offsetX = 0
        self.offsetY = 0
        InterfacePositionable2D.__init__(self)
        self.setSize(width, height)

    def _isChanged(self):
        return self.offsetX != self._oldOffsetX or self.offsetY != self._oldOffsetY or self.zoom != self._oldZoom

    def setOffset(self, x, y):
        self.offsetX = x
        self.offsetY = y

    def getOffset(self):
        """ current offset of the camera, topleft-wise"""
        return (
         self.offsetX, self.offsetY)

    def updateValues(self):
        self._oldOffsetX = self.offsetX
        self._oldOffsetY = self.offsetY
        self._oldZoom = self.zoom

    def getRealSize(self):
        return self.getSize()

    def getBounds(self):
        return (
         self.left * self.zoom, self.top * self.zoom, self.right * self.zoom, self.bottom * self.zoom)

    def onZoom(self, value):
        value = max(0.25, min(1.0, self.zoom * value))
        self.setZoom(value)

    def setZoom(self, val):
        return


class WorldCamera(SimpleCamera):

    def __init__(self, width, height, virtual_width=0, virtual_height=0):
        SimpleCamera.__init__(self, width, height)
        self._windowWidth, self._windowHeight = width, height
        if virtual_width == 0 or virtual_height == 0:
            self._realWidth, self._realHeight = width, height
        else:
            self._realWidth, self._realHeight = virtual_width, virtual_height
        self.cullSquare = InterfacePositionable2D()
        self.cullSquare.setSize(self._realWidth, self._realHeight)
        self._realPosition = (0, 0)
        self.setSize(self._realWidth, self._realHeight)
        self.setPosition(0, 0)
        self._oldSquareBounds = (0, 0, 0, 0)
        self.referenceObject = None
        self.previous_state = (0, 0)
        self.next_state = (0, 0)
        self.slow_camera = True
        self.camera_func = None
        self.setCameraConfig()
        self.velocity = 8
        self.velocity_test = 2

    def setCameraConfig(self):
        if gameSettings.getCameraSpeed():
            self.camera_func = self._slow_camera
            self.slow_camera = True
        else:
            self.camera_func = self._instant_camera
            self.slow_camera = False

    def setZoomConfig(self):
        self.zoom = gameSettings.getZoom()

    def getRealSize(self):
        return (
         self._realWidth, self._realHeight)

    def setReferenceObject(self, object):
        if self.referenceObject is object:
            raise Exception("Its already the reference object of the camera.")
        if self.referenceObject:
            self.referenceObject.setNotFollowedByCamera()
        self.referenceObject = object
        object.setFollowedByCamera(self)

    def get_virtual_coordinates(self, x, y):
        x_diff = self._realWidth / float(self._windowWidth)
        y_diff = self._realHeight / float(self._windowHeight)
        adjust_x = (self._windowWidth * x_diff - self._realWidth) / 2
        adjust_y = (self._windowHeight * y_diff - self._realHeight) / 2
        return (
         int(x_diff * x) - adjust_x, int(y_diff * y) - adjust_y)

    def toMapPosition(self, x, y):
        """ From a screen position, return the map position.
        This now returns based on bottom left matrix. Mostly for render. See toMapPositionTopLeft for old """
        x, y = self.get_virtual_coordinates(x, y)
        return (
         self.offsetX + x / self.zoom,
         self.offsetY + y / self.zoom)

    def toScreenPosition(self, x, y):
        """ from a map position, return the screen position. """
        th = (self._realHeight - self._realHeight / self.zoom) / 2
        tw = (self._realWidth - self._realWidth / self.zoom) / 2
        sx = (x - self.offsetX - tw) / self.zoom
        sy = (y - self.offsetY - th) / self.zoom
        return (
         sx, sy)

    def setZoom(self, val):
        if self.zoom == val:
            return
        gameSettings["Screen"]["zoom"] = str(val)
        gameSettings.saveConfig()
        x, y = self.getFollowPosition(val)
        self.offsetX = x
        self.offsetY = y
        self.previous_state = (x, y)
        self.next_state = (x, y)
        self.cullSquare.setPosition(x, y)
        self.updateBounds()
        eventManager.notify("onChunkChange")
        self.zoom = val

    def getCullBounds(self):
        return (
         self.cullSquare.left, self.cullSquare.bottom, self.cullSquare.right, self.cullSquare.top)

    def _getSquareBounds(self, l, r, t, b):
        return (
         int(math.floor(l / MapSettings.SQUARE) * MapSettings.SQUARE),
         int(math.floor(b / MapSettings.SQUARE) * MapSettings.SQUARE),
         int(math.ceil(r / MapSettings.SQUARE) * MapSettings.SQUARE),
         int(math.ceil(t / MapSettings.SQUARE) * MapSettings.SQUARE))

    def getSquareBounds(self):
        return self._oldSquareBounds

    def setListenerPosition(self, x, y):
        x, y = int(x), int(y)
        if gameListener.position[0] != x or gameListener.position[2] != y:
            gameListener.position = (
             x, 0, y)

    def setCenter(self, x, y):
        """ Used on map transition, mostly to make sure sprites load within the correct bounds """
        x, y = self.convertPositionToCameraCenter(x, y)
        self.setOffset(x, y)
        self.cullSquare.setPosition(x, y)
        self.updateBounds()

    def lerp(self, a, b, t):
        return a * (1 - t) + b * t

    def _slow_camera(self, x, y):
        return (
         self.lerp(self.offsetX, x, (self.velocity - self.zoom / 2) * 0.016),
         self.lerp(self.offsetY, y, (self.velocity - self.zoom / 2) * 0.016))

    def _instant_camera(self, x, y):
        return (
         x, y)

    def update(self, dt):
        self.previous_state = (
         self.offsetX, self.offsetY)
        x, y = self.getFollowPosition(self.zoom)
        self.next_state = self.camera_func(x, y)
        self.offsetX = x
        self.offsetY = y
        self.cullSquare.setPosition(x, y)
        self.updateBounds()
        eventManager.notify("onChunkChange")

    def draw(self, interp):
        if self.previous_state != self.next_state:
            x, y = interpolatePosition2D(self.previous_state, self.next_state, interp)
            self.offsetX, self.offsetY = x, y

    def updateBounds(self):
        """ Update the current bounds of the camera. """
        self.updateValues()
        squareBounds = self._getSquareBounds(self.offsetX, self.offsetX + self._realWidth / self.zoom, self.offsetY + self._realHeight / self.zoom, self.offsetY)
        if squareBounds != self._oldSquareBounds:
            self._oldSquareBounds = squareBounds
            mapContainer.updateAnimations(self.cullSquare)

    def convertPositionToCameraCenter(self, x, y, zoom=1.0):
        nx = x - self._realWidth / 2.0 / zoom
        ny = y - self._realHeight / 2.0 / zoom
        return mapContainer.keepRectInMap(nx, ny, self._realWidth / zoom, self._realHeight / zoom)

    def getFollowPosition(self, zoom=1.0):
        return self.convertPositionToCameraCenter(self.referenceObject.getX(), self.referenceObject.getY(), zoom)

    def onBeforeMapLoad(self):
        return

    def onAfterMapLoad(self):
        if self.referenceObject:
            x, y = self.getFollowPosition(self.zoom)
            self.setOffset(x, y)
            self.previous_state = (x, y)
            self.next_state = (x, y)
            (self.cullSquare.setPosition)(*self.getFollowPosition())
            eventManager.notify("onChunkInitialLoad")
        self._oldSquareBounds = None
        self.updateBounds()

    def onCharSelection(self, char):
        self.setReferenceObject(char)

    def onZoom(self, value):
        value = max(1.0, min(3.0, self.zoom + value))
        self.setZoom(value)

    def reset(self):
        self.referenceObject = None
        self.offsetX = 0
        self.offsetY = 0


simpleCamera = SimpleCamera(*gameSettings.getWindowResolution())
worldCamera = WorldCamera(*gameSettings.getWindowResolution(), virtual_width=gameSettings.getWorldResolution()[0], virtual_height=gameSettings.getWorldResolution()[1])
worldCamera.setZoomConfig()
eventManager.registerListener(worldCamera)
eventDispatcher.push_handlers(worldCamera)
guiCamera = SimpleCamera(*gameSettings.getWindowResolution())
