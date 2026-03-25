# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: shared\service\geometry.py
"""
Created on 30 juin 2011

@author: Kami
"""
import rabbyt, math
from shared.container.geometry import Point2D, Quad2D

def getPositionInFront(self, x, y, direction, range=10, offsetX=0, offsetY=0):
    nx = x + math.cos(math.radians(direction)) * range + offsetX
    ny = y + math.sin(math.radians(direction)) * range - offsetY
    return (
     nx, ny)


def getAngleBetweenTwoPoints(xxx_todo_changeme, xxx_todo_changeme1):
    x1, y1 = xxx_todo_changeme
    x2, y2 = xxx_todo_changeme1
    dx = x2 - x1
    dy = y2 - y1
    rads = math.atan2(dy, dx)
    rads %= 2 * math.pi
    return math.degrees(rads)


def getDistanceBetweenTwoPoints(point1, point2):
    x0, y0 = point1
    x1, y1 = point2
    return math.hypot(x1 - x0, y1 - y0)


def inCircle(center_x, center_y, radius, x, y):
    square_dist = (center_x - x) ** 2 + (center_y - y) ** 2
    return square_dist <= radius ** 2


def inElipse(center_x, center_y, x, y, radius_hor, radius_ver):
    p = (x - center_x) ** 2 / radius_hor ** 2 + (y - center_y) ** 2 / radius_ver ** 2
    return p <= 1


def getPositionOnDirection(position, angle, distance):
    x, y = position
    x += math.cos(math.radians(angle)) * distance
    y += math.sin(math.radians(angle)) * distance
    return (x, y)


def getPositionOnDirectionInt(position, angle, distance):
    x, y = position
    x += math.cos(math.radians(angle)) * distance
    y += math.sin(math.radians(angle)) * distance
    return (int(x), int(y))


def isNear(position1, position2, tol):
    if getDistanceBetweenTwoPoints(position1, position2) > tol:
        return False
    else:
        return True


def convertPosition(toNumber, x, y):
    return (
     int(x / toNumber), int(y / toNumber))


def roundPosition(toNumber, x, y):
    return (
     int(x / toNumber) * toNumber, int(y / toNumber) * toNumber)


def roundTwoPosition(toNumber, toNumber2, x, y):
    return (
     int(x / toNumber) * toNumber, int(y / toNumber2) * toNumber2)


def convertPositionToRect(width, height, x, y):
    left, top = roundTwoPosition(width, height, x, y)
    quad = Quad2D(left, top, left + width, top + height)
    return quad


def convertPositionToRectNoRound(width, height, x, y):
    return Quad2D(x, y, x + width, y + height)
