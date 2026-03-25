# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: shared\service\direction.py
from shared.container.constants import Direction
import random
from shared.service.utils import inRange
import math

class DirectionService:
    RIGHT = 0
    UP_RIGHT = 45
    UP = 90
    UP_LEFT = 135
    LEFT = 180
    DOWN_LEFT = 225
    DOWN = 270
    DOWN_RIGHT = 315
    RADIANS = {RIGHT: (math.radians(RIGHT)), 
     UP_RIGHT: (math.radians(UP_RIGHT)), 
     UP: (math.radians(UP)), 
     UP_LEFT: (math.radians(UP_LEFT)), 
     LEFT: (math.radians(LEFT)), 
     DOWN_LEFT: (math.radians(DOWN_LEFT)), 
     DOWN: (math.radians(DOWN)), 
     DOWN_RIGHT: (math.radians(DOWN_RIGHT))}
    VECTORS = {RIGHT: (1, 0), 
     UP_RIGHT: (1, 1), 
     UP: (0, 1), 
     UP_LEFT: (-1, 1), 
     LEFT: (-1, 0), 
     DOWN_LEFT: (-1, -1), 
     DOWN: (0, -1), 
     DOWN_RIGHT: (1, -1)}
    VECTOR_LIST = list(VECTORS.values())
    ALL_DIRECTIONS = (
     RIGHT, UP_RIGHT, UP, UP_LEFT, LEFT, DOWN_LEFT, DOWN, DOWN_RIGHT)
    LEFT_FACING = (
     UP_LEFT, LEFT, DOWN_LEFT)
    DIAGONAL = (
     UP_RIGHT, UP_LEFT, DOWN_LEFT, DOWN_RIGHT)
    MIRRORS = (
     UP_LEFT, LEFT, DOWN_LEFT)
    NO_DIAGONAL = (
     UP, DOWN, LEFT, RIGHT)
    FRAME_DATA = (
     DOWN, DOWN_LEFT, LEFT, UP_LEFT, UP, UP_RIGHT, RIGHT, DOWN_RIGHT)
    STRING_DIR = ('RIGHT', 'UP_RIGHT', 'UP', 'UP_LEFT', 'LEFT', 'DOWN_LEFT', 'DOWN',
                  'DOWN_RIGHT')

    def vectorToDirection(self, vector):
        return self.ALL_DIRECTIONS[self.VECTOR_LIST.index(vector)]

    def stringToInt(self, value):
        return self.ALL_DIRECTIONS[self.STRING_DIR.index(value)]

    def intToString(self, value):
        return self.STRING_DIR[self.ALL_DIRECTIONS.index(value)]

    def facingToIndex(self, facing):
        return self.FRAME_DATA.index(facing)

    def opposite(self, direction):
        return (direction + 180) % 360

    def getDirectionsNextTo(self, direction, amount=1):
        dirIndex = self.ALL_DIRECTIONS.index(self.getNear(direction))
        dirCount = len(self.ALL_DIRECTIONS)
        left = dirIndex - amount
        if left < 0:
            left = dirCount - 1
        right = dirIndex + amount
        if right >= dirCount:
            right = 0
        return (self.ALL_DIRECTIONS[left], self.ALL_DIRECTIONS[dirIndex], self.ALL_DIRECTIONS[right])

    def intToDeg(self, i):
        return Direction.toDeg[i % 10]

    def isIntValid(self, i):
        return i % 10 in Direction.toDeg

    def getRandom(self):
        return random.randint(0, 360)

    def degToInt(self, deg):
        return Direction.toInt[self.getNear(deg)]

    def getNextRight(self, direction):
        try:
            return self.ALL_DIRECTIONS[self.ALL_DIRECTIONS.index(direction) - 1]
        except Exception:
            return self.DOWN_RIGHT

    def getNextLeft(self, direction):
        try:
            return self.ALL_DIRECTIONS[self.ALL_DIRECTIONS.index(direction) + 1]
        except Exception:
            return self.RIGHT

    def getNear(self, degree):
        """ Get the nearest direction """
        degree = int(degree) % 360
        degree = int(degree * 10)
        dlist = (
         [
          0, 225, 0], [225, 675, 45], [675, 1125, 90],
         [
          1125, 1575, 135], [1575, 2025, 180], [2025, 2475, 225],
         [
          2475, 2925, 270], [2925, 3375, 315], [3375, 3600, 0])
        for minN, maxN, res in dlist:
            if inRange(degree, minN, maxN):
                return res


directionService = DirectionService()
