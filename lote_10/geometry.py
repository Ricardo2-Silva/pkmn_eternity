# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: shared\container\geometry.py
"""
Created on 30 juin 2011

@author: Kami
"""
import rabbyt, math
from shared.container.constants import RefPointType

class InterfacePositionable(object):

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    @property
    def position(self):
        return (self.x, self.y)

    @position.setter
    def position(self, pos):
        self.x, self.y = pos

    @property
    def size(self):
        return (self.width, self.height)

    @property
    def left(self):
        return self.x

    @property
    def right(self):
        return self.x + self.width

    @property
    def top(self):
        return self.y + self.height

    @property
    def bottom(self):
        return self.y

    @property
    def center_x(self):
        return self.x + self.width // 2

    @property
    def center_y(self):
        return self.y + self.height // 2


class InterfacePositionable2D(object):

    def __init__(self, *args, refPointType=RefPointType.BOTTOMLEFT):
        self.refPointType = refPointType
        if args:
            self._realX_, self._realY_, self._realHeight_, self._realWidth_ = args
        else:
            self._realX_, self._realY_, self._realHeight_, self._realWidth_ = (0, 0,
                                                                               0,
                                                                               0)
        self.left = self._convertToLeft(self._realX_)
        self.right = self.left + self._realWidth_
        self.bottom = self._convertBottom(self._realY_)
        self.top = self.bottom + self._realHeight_
        self.bounding_radius = self._realHeight_
        self.collision_radius = self._realHeight_

    @property
    def interfaceArea(self):
        """Returns the coordinates and dimensions of the area."""
        return (
         self._realX_, self._realY_, self._realWidth_, self._realHeight_)

    @property
    def position(self):
        return (self._realX_, self._realY_)

    def _convertToLeft(self, x):
        if self.refPointType & RefPointType.CENTERX:
            return x - self._realWidth_ / 2
        else:
            if self.refPointType & RefPointType.RIGHT:
                return x - self._realWidth_
            return x

    def _convertBottom(self, y):
        if self.refPointType & RefPointType.CENTERY:
            return y - self._realHeight_ / 2
        else:
            if self.refPointType & RefPointType.TOP:
                return y + self._realHeight_
            return y

    def setSize(self, width, height):
        self._setWidth(width)
        self._setHeight(height)

    def setPosition(self, x, y):
        self._setX(x)
        self._setY(y)

    def toString(self):
        return "Left: {0}, top: {1}, right: {6}, bottom: {7}, width: {2}, height: {3}, x: {4}, y: {5}".format(self.left, self.top, self.width, self.height, self.x, self.y, self.right, self.bottom)

    def getSize(self):
        return (
         self._realWidth_, self._realHeight_)

    def getPosition(self):
        return (
         self._realX_, self._realY_)

    def _setWidth(self, width):
        self._realWidth_ = width
        self.width = width
        self._setX(self._realX_)

    def setWidth(self, width):
        self._setWidth(width)

    def _setHeight(self, height):
        self._realHeight_ = height
        self.height = height
        self._setY(self._realY_)

    def setHeight(self, height):
        self._setHeight(height)

    def getWidth(self):
        return self._realWidth_

    def getHeight(self):
        return self._realHeight_

    def setX(self, x):
        self._setX(x)

    def setY(self, y):
        self._setY(y)

    def _setX(self, x):
        self._realX_ = x
        self.left = self._convertToLeft(x)
        self.right = self.left + self._realWidth_
        self.bounding_radius = self._realWidth_

    def _setY(self, y):
        self._realY_ = y
        self.bottom = self._convertBottom(y)
        self.top = self.bottom + self._realHeight_
        self.bounding_radius = self._realHeight_
        self.collision_radius = self._realHeight_

    def getX(self):
        return self._realX_

    def getY(self):
        return self._realY_

    def getTopLeft(self, offx=0, offy=0):
        return (
         self._realX_ + offx, self._realY_ + offy)

    def getBottomLeft(self, offx=0, offy=0):
        return (
         self._realX_ + offx, self._realY_ + self._realHeight_ + offy)

    def getTopRight(self, offx=0, offy=0):
        return (
         self._realX_ + self._realWidth_ + offx, self._realY_ + offy)

    def getBottomRight(self, offx=0, offy=0):
        return (
         self._realX_ + self._realWidth_ + offx, self._realY_ + self._realHeight_ + offy)

    def getBottomCenter(self):
        return (
         self.left + self.width // 2, self._realY_)

    def getTop(self):
        return self._realY_

    def getLeft(self):
        return self._realX_

    def getRight(self):
        return self._realX_ + self._realWidth_

    def getBottom(self):
        return self._realY_ + self._realHeight_

    def getCenter(self):
        return (
         self.left + self._realWidth_ // 2, self.bottom + self._realHeight_ // 2)

    def getRealTopCenter(self, offx=0, offy=0):
        """ Return the topcenter, without taking care of the 'refPointType.' """
        return (
         self.left + offx, self.bottom + offy)

    def getRealBottomCenter(self, offx=0, offy=0):
        """ Return the topcenter, without taking care of the 'refPointType.' """
        return (
         self.left + offx, self.top + offy)

    @property
    def vertices(self):
        return ((self.left, self.bottom),
         (
          self.right, self.bottom),
         (
          self.right, self.top),
         (
          self.left, self.top))


class InterfacePositionable3D(InterfacePositionable2D):
    __doc__ = " Simulation of the z position, as the height. "
    __slots__ = ["z"]

    def __init__(self, *args, refPointType=RefPointType.BOTTOMCENTER):
        (InterfacePositionable2D.__init__)(self, *args, **{"refPointType": refPointType})
        self.z = 0

    def getPositionInFront(self, direction, range=10, offsetX=0, offsetY=0):
        x, y, z = self.getPosition()
        nx = x + math.cos(math.radians(direction)) * range + offsetX
        ny = y + math.sin(math.radians(direction)) * range + offsetY
        return (
         nx, ny, z)

    def getOffsetInFront(self, direction, length=10, offsetX=0, offsetY=0):
        nx = math.cos(math.radians(direction)) * length + offsetX
        ny = math.sin(math.radians(direction)) * length + offsetY
        return (
         nx, ny)

    def setPosition(self, x, y, z=0):
        InterfacePositionable2D.setPosition(self, x, y)
        self.z = z

    def setPosition2D(self, x, y):
        InterfacePositionable2D.setPosition(self, x, y)

    def getPosition(self):
        """ Return the real mathematical position. """
        return (
         self._realX_, self._realY_, self.getZ())

    def getPosition2D(self):
        """ Return the simulated position """
        return (
         self._realX_, self._realY_)

    def getProjection2D(self):
        """ Return the simulated position on 2D plan"""
        return (
         self._realX_, self._realY_ + self.getZ())

    def _setY(self, y):
        self._realY_ = y
        self.bottom = self._convertBottom(y - self.z)
        self.top = self.bottom + self._realHeight_
        self.bounding_radius = self._realHeight_

    def _setZ(self, z):
        self.z = z

    def setZ(self, z):
        self._setZ(z)

    def getZ(self):
        return self.z


class Rect(object):
    __slots__ = [
     'left', 'right', 'top', 'bottom', 'collision_radius', 'width', 
     'height']

    def __init__(self, x, y, width, height):
        self.left = x
        self.right = x + width
        self.bottom = y
        self.top = y + height
        self.width = width
        self.height = height
        self.collision_radius = max(width, height)

    @property
    def position(self):
        return (self.left, self.bottom)

    @position.setter
    def position(self, value):
        self.left = value[0]
        self.right = value[0] + self.width
        self.bottom = value[1]
        self.top = value[1] + self.height

    def __repr__(self, *args, **kwargs):
        return f"Rect({self.left}, {self.top}, {self.right}, {self.bottom})"

    def corners(self):
        return (
         (
          self.left, self.bottom),
         (
          self.right, self.bottom),
         (
          self.right, self.top),
         (
          self.left, self.top))

    def spatial(self):
        """ X and Y """
        return (
         (
          self.left, self.right), (self.bottom, self.top))

    @property
    def vertices(self):
        return ((self.left, self.bottom),
         (
          self.right, self.bottom),
         (
          self.right, self.top),
         (
          self.left, self.top))

    @property
    def bottomleft(self):
        return (self.left, self.bottom)

    @property
    def bottomright(self):
        return (self.right, self.bottom)

    @property
    def topright(self):
        return (self.right, self.top)

    @property
    def topleft(self):
        return (self.left, self.top)


def Point2D(x, y):
    return rabbyt.Quad((x, y, x, y))


def Quad2D(left, top, right, bottom):
    return rabbyt.Quad((left, top, right, bottom))


class Quad2DClass(rabbyt.Quad):

    def __init__(self, quad):
        rabbyt.Quad.__init__(self, quad)


def createQuadRotated(x, y, width, height, degrees):
    r = math.radians(degrees)
    cr = math.cos(r)
    sr = math.sin(r)
    x1 = 0
    y1 = -height // 2
    x2 = x1 + width
    y2 = y1 + height
    ax = x1 * cr - y1 * sr + x
    ay = x1 * sr + y1 * cr + y
    bx = x2 * cr - y1 * sr + x
    by = x2 * sr + y1 * cr + y
    cx = x2 * cr - y2 * sr + x
    cy = x2 * sr + y2 * cr + y
    dx = x1 * cr - y2 * sr + x
    dy = x1 * sr + y2 * cr + y
    return rabbyt.Quad(((ax, ay), (bx, by), (cx, cy), (dx, dy)))


def createPolygon(x, y, width, height, degrees):
    r = math.radians(degrees)
    cr = math.cos(r)
    sr = math.sin(r)
    x1 = 0
    y1 = -height // 2
    x2 = x1 + width
    y2 = y1 + height
    ax = x1 * cr - y1 * sr + x
    ay = x1 * sr + y1 * cr + y
    bx = x2 * cr - y1 * sr + x
    by = x2 * sr + y1 * cr + y
    cx = x2 * cr - y2 * sr + x
    cy = x2 * sr + y2 * cr + y
    dx = x1 * cr - y2 * sr + x
    dy = x1 * sr + y2 * cr + y
    return [
     (
      ax, ay), (bx, by), (cx, cy), (dx, dy)]


def getConnectingPointsByRect(rect1, rect2, angle):
    if angle >= 0 and angle < 90 or angle >= 180 and angle < 270:
        points = (
         rect1.topleft, rect2.topleft, rect2.bottomright, rect1.bottomright)
    else:
        if angle >= 90 and angle < 180 or angle >= 270 and angle < 360:
            points = (
             rect1.topright, rect2.topright, rect2.bottomleft, rect1.bottomleft)
    return points


def connectingPointsToPolygon(x1, y1, x2, y2, size, angle):
    if angle >= 0 and angle < 90 or angle >= 180 and angle < 270:
        points = (
         (
          x1, y1 + size), (x2, y2 + size), (x2 + size, y2), (x1 + size, y1))
    else:
        if angle >= 90 and angle < 180 or angle >= 270 and angle < 360:
            points = (
             (
              x1 + size, y1 + size), (x2 + size, y2 + size), (x2, y2), (x1, y1))
    return points


class Polygon:
    __doc__ = " A polygon differs from Rect in that the vertices are not always aligned. "

    def __init__(self, x, y, width, height, vertices):
        self.position = (x, y)
        self.collision_radius = max(width, height)
        self.vertices = vertices
        self.left = min(self.vertices[0][0], self.vertices[1][0])
        self.right = max(self.vertices[2][0], self.vertices[3][0])
        self.top = max(self.vertices[0][1], self.vertices[1][1])
        self.bottom = min(self.vertices[2][1], self.vertices[3][1])

    def get_render_vertices(self):
        """ Flatten list so they can be used for rendering vertices. """
        return [axis for point in self.vertices for axis in iter(point)]

    def spatial(self):
        """ X and Y """
        return (
         (
          self.left, self.right), (self.bottom, self.top))

    def corners(self):
        return (
         (
          self.left, self.bottom),
         (
          self.right, self.bottom),
         (
          self.right, self.top),
         (
          self.left, self.top))
