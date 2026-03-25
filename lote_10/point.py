# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: shared\container\db\point.py
"""
Created on 11 janv. 2012

@author: Kami
"""
from shared.container.utils.store import DBId
from shared.container.db._point import points
import math

class PointDB(DBId):

    def __init__(self):
        DBId.__init__(self, "Points Value Dict", "Name of Data")
        self.idToData = points

    def _init(self):
        return


pointDB = PointDB()

class PointCombination:

    def __init__(self, *pointHandlers):
        self.pointsHandlers = pointHandlers

    def isOver(self, time):
        for pointHandler in self.pointsHandlers:
            if pointHandler.isOver():
                return True

        return False

    def getMultiply(self, time):
        x, y = self.pointsHandlers[0].get(time)
        for dx, dy in self.pointsHandlers[1:]:
            x = x * dx
            y = y * dy

        return (x, y)

    def getAdd(self, time):
        x, y = self.pointsHandlers[0].get(time)
        for dx, dy in self.pointsHandlers[1:]:
            x = x + dx
            y = y + dy

        return (x, y)


class PointHandler:

    def __init__(self, id, speed=50, direction=0, scaleX=1, scaleY=1, reversed=False, invertY=False, repeat=False, end=0):
        self.points, self.len = pointDB.getById(id)
        if end:
            self.len = end
        self.scaleX = scaleX
        self.scaleY = scaleY
        self.invertY = invertY
        self.reversed = reversed
        self.repeat = repeat
        self.speed = speed
        self.direction = direction
        self.rdirection = math.radians(direction)
        self.cos = math.cos(self.rdirection)
        self.sin = math.sin(self.rdirection)
        self.distanceIndice = scaleX * self.len

    def getDistanceIndice(self):
        return self.distanceIndice

    def setScale(self, scaleX=1, scaleY=1):
        self.scaleX = scaleX
        self.scaleY = scaleY
        self.distanceIndice = scaleX * self.len

    def setReversed(self, val):
        self.reversed = val

    def last(self):
        return self.getByInd(self.len - 1)

    def isOver(self, time):
        if self.repeat:
            return False
        else:
            ind = time * self.speed
            return int(ind) > self.len - 1

    def getByInd(self, ind):
        if self.repeat:
            ind = ind % self.len
        else:
            if self.reversed:
                ind = self.len - 1 - ind
            x, y = self.points[ind]
            x = x * self.scaleX
            y = y * self.scaleY
            if self.invertY:
                y = -y
        rx, ry = x * self.cos - y * self.sin, y * self.cos + x * self.sin
        return (
         rx, ry)

    def get(self, dtime):
        ind = int(dtime * self.speed)
        return self.getByInd(ind)
