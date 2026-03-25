# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\data\container\map.py
"""
Created on 10 oct. 2011

@author: Kami
"""
import math, random
from typing import Optional
import rabbyt
from twisted.internet import reactor
from client.control.service.session import sessionService
from client.data.world.map import GameMap
from shared.container.constants import MapSettings, GroundType
from shared.container.geometry import Rect, Polygon, connectingPointsToPolygon
from shared.controller.maths.maths import interpolate
from shared.service.collision import check_for_collision_with_list
from shared.service.direction import directionService
from shared.service.geometry import convertPositionToRect, roundPosition, getDistanceBetweenTwoPoints, getAngleBetweenTwoPoints
from shared.service.utils import clamp
specialCollisions = [
 100]
specialMarkers = [-1, -2]
import math

def SweptAABBParse error at or near `POP_JUMP_IF_TRUE' instruction at offset 290_292


class BattleCollisions:

    def __init__(self):
        self.collisionId = 0
        self.collisions = {}

    def addCollision(self, quad, duration=25):
        self.collisionId += 1
        self.collisions[self.collisionId] = quad
        reactor.callLater(duration, self.removeCollision, self.collisionId)

    def removeCollision(self, collisionId):
        if collisionId in self.collisions:
            del self.collisions[collisionId]

    def clean(self):
        self.collisions.clear()
        self.collisionId = 0

    def getCollisionAtPosition(self, x, y, radius=8):
        wallHeight = 0
        if self.collisions:
            case = convertPositionToRect(radius, radius, x, y)
            x, y = roundPosition(MapSettings.SQUARE, x, y)
            collision = rabbyt.collisions.aabb_collide_single(case, list(self.collisions.values()))
            if collision:
                wallHeight = collision[0].wallHeight
        return wallHeight


class MapContainer:
    __doc__ = " Contains map and useful informations about it. (Is the map data basically.)"
    game_map: Optional[GameMap]

    def __init__(self):
        self.game_map = None
        self._currentAnimations = set()
        self.battleWalls = BattleCollisions()

    @property
    def width(self):
        return self.game_map.size[0]

    @property
    def height(self):
        return self.game_map.size[1]

    def clampRow(self, row):
        return clamp(row, 0, self.maxRows + 1)

    def clampCol(self, col):
        return clamp(col, 0, self.maxCols + 1)

    def mapRangeRow(self, row, rangeNum=MapSettings.RANGEY):
        return list(range(max(0, row - rangeNum), min(self.maxRows, row + rangeNum + 1)))

    def mapRangeCol(self, col, rangeNum=MapSettings.RANGEX):
        return list(range(max(0, col - rangeNum), min(self.maxCols, col + rangeNum + 1)))

    @property
    def maxCols(self):
        return int(math.ceil(self.width / MapSettings.SQUARE))

    @property
    def maxRows(self):
        return int(math.ceil(self.height / MapSettings.SQUARE))

    def updateAnimations(self, area):
        """This will stop or start animations based on if the area is in view."""
        animatedInView = rabbyt.collisions.aabb_collide_single(area, self.game_map.animated)
        new = set(animatedInView)
        outOfView = self._currentAnimations - new
        newInView = new - self._currentAnimations
        for obj in outOfView:
            obj.stopAnimation()

        for obj in newInView:
            obj.startAnimation()

        self._currentAnimations = new

    def loadFromCache(self, gameMap):
        if gameMap.data:
            self.cleanMap()
            self.game_map = gameMap
            self.battleWalls = BattleCollisions()
            for mapObject in gameMap.objects:
                mapObject.renderer.addSprites()

            for mapObject in gameMap.effects:
                mapObject.renderer.addSprites()

            return True
        else:
            return False

    def cleanMap(self):
        self.battleWalls.clean()
        self._currentAnimations.clear()
        if self.game_map:
            for obj in self.game_map.animated:
                obj.stopAnimation()

    def addWalls(self, gameMap, rectList):
        """ Add a rect to every ScreenTile that touches it."""
        for indX in range(0, self.getMaxHorizontalTileNumber()):
            for indY in range(0, self.getMaxVerticalTileNumber()):
                tile = Rect(indX * MapSettings.SQUARE, indY * MapSettings.SQUARE, MapSettings.SQUARE, MapSettings.SQUARE)
                colliding = rabbyt.collisions.aabb_collide_single(tile, rectList)
                gameMap.basicWalls.set([x for x in colliding if x.wallHeight not in specialCollisions], indY, indX)
                gameMap.specialWalls.set([x for x in colliding if x.wallHeight in specialCollisions + specialMarkers], indY, indX)

    def addGroundTypes(self, gameMap, rectList):
        """ Add a rect to every ScreenTile that touches it."""
        for indX in range(0, self.getMaxHorizontalTileNumber()):
            for indY in range(0, self.getMaxVerticalTileNumber()):
                tile = Rect(indX * MapSettings.SQUARE, indY * MapSettings.SQUARE, MapSettings.SQUARE, MapSettings.SQUARE)
                colliding = rabbyt.collisions.aabb_collide_single(tile, rectList)
                gameMap.grounds.set(colliding, indY, indX)

    def getGroundTypeAtPosition(self, gameMap, x, y, radius=8):
        case = Rect(x - radius // 2, y, radius, radius)
        indexX, indexY = int(x / MapSettings.SQUARE), int(y / MapSettings.SQUARE)
        collisions = rabbyt.collisions.aabb_collide_single(case, gameMap.grounds.get(indexY, indexX))
        if not collisions:
            return GroundType.NOTHING_DEFAULT
        else:
            return set([rect.groundType for rect in collisions])

    def getAccumulatedGroundTypeAtPosition(self, gameMap, x, y, radius=8):
        """This differs in that instead of a list, we """
        case = Rect(x - radius // 2, y, radius, radius)
        indexX, indexY = int(x / MapSettings.SQUARE), int(y / MapSettings.SQUARE)
        collisions = rabbyt.collisions.aabb_collide_single(case, gameMap.grounds.get(indexY, indexX))
        if not collisions:
            return GroundType.NOTHING
        else:
            grounds = 0
            for rect in collisions:
                grounds |= rect.groundType

            return grounds

    def getAccumulatedGroundTypeFromRect(self, gameMap, rect, squares):
        """For players. Since grounds can intersect such as grass and cliffs."""
        for indexX, indexY in squares:
            collisions = rabbyt.collisions.aabb_collide_single(rect, gameMap.grounds.get(indexY, indexX))
            if collisions:
                grounds = 0
                for rect in collisions:
                    grounds |= rect.groundType

                return grounds

        return GroundType.NOTHING

    def getAreasAtPosition(self, gameMap, x, y, radius=8):
        case = convertPositionToRect(radius, radius, x, y)
        return rabbyt.collisions.aabb_collide_single(case, gameMap.areas)

    def getAreasAtPosition(self, gameMap, x, y, radius=8):
        case = convertPositionToRect(radius, radius, x, y)
        return rabbyt.collisions.aabb_collide_single(case, gameMap.areas)

    def isPositionWalkable(self, charData, gameMap, x, y, radius=18):
        """Only use for selecting to check all of these."""
        wallHeight = self.getWallHeightAtPosition(gameMap, x, y, radius)
        groundTypes = self.getGroundTypeAtPosition(gameMap, x, y, radius)
        walkable = self.isPositionInBounds(gameMap, x, y)
        if not walkable:
            return False
        else:
            if wallHeight > 0:
                return False
            else:
                allowed = GroundType.GROUND_WALKABLE
                if sessionService.canSwim():
                    allowed |= GroundType.ALL_WATER
                if not self._verifyGrounds(groundTypes, allowed):
                    return False
            return True

    def isXYWalkableForChar(self, char, x, y, radius=18):
        """Only use for selecting to check all of these."""
        wallHeight = self.getWallHeightAtPosition(char.data.map, x, y, radius)
        groundTypes = self.getGroundTypeAtPosition(char.data.map, x, y, radius)
        walkable = self.isPositionInBounds(char.data.map, x, y)
        if not walkable:
            return False
        else:
            if char.getZ() < wallHeight:
                return False
            else:
                allowed = GroundType.GROUND_WALKABLE
                if sessionService.canSwim():
                    allowed |= GroundType.ALL_WATER
                if not self._verifyGrounds(groundTypes, allowed):
                    return False
            return True

    def isPositionWalkableForChar(self, char, radius=18):
        """Only use for selecting to check all of these."""
        x, y = char.getPosition2D()
        wallHeight = self.getWallHeightAtPosition(char.data.map, x, y, radius)
        groundTypes = self.getGroundTypeAtPosition(char.data.map, x, y, radius)
        walkable = self.isPositionInBounds(char.data.map, x, y)
        if not walkable:
            return False
        else:
            if char.getZ() < wallHeight:
                return False
            else:
                allowed = GroundType.GROUND_WALKABLE
                if sessionService.canSwim():
                    allowed |= GroundType.ALL_WATER
                if not self._verifyGrounds(groundTypes, allowed):
                    return False
            return True

    def addBattleCollision(self, quad, duration=25):
        self.battleWalls.addCollision(quad, duration)

    def getWallHeightAtPosition(self, gameMap, x, y, radius=8, specialOnly=False):
        """"Return the wall height at this position. 0 means no height (or walkable)"""
        case = Rect(x - radius // 2, y, radius, radius)
        for indexX, indexY in set([(int(cX / MapSettings.SQUARE), int(cY / MapSettings.SQUARE)) for cX, cY in case.corners()]):
            collisions = rabbyt.collisions.aabb_collide_single(case, gameMap.basicWalls.get(indexY, indexX))
            if collisions:
                return min([rect.wallHeight for rect in collisions])

        return 0

    def getWallHeightFromQuad(self, gameMap, quad, specialOnly):
        """ Get wallheights from Quad, supports rotation. """
        xAxis, yAxis = quad.spatial()
        for indexX in range(int(xAxis[0] / MapSettings.SQUARE), int(xAxis[1] / MapSettings.SQUARE) + 1):
            for indexY in range(int(yAxis[0] / MapSettings.SQUARE), int(yAxis[1] / MapSettings.SQUARE) + 1):
                collisions = check_for_collision_with_list(quad, gameMap.basicWalls.get(indexY, indexX))
                if collisions:
                    return min([rect.wallHeight for rect in collisions])

        return 0

    def getGroundTypeFromQuad(self, gameMap, quad):
        """ Get groudn types from Quad, supports rotation. """
        xAxis, yAxis = quad.spatial()
        for indexX in range(int(xAxis[0] / MapSettings.SQUARE), int(xAxis[1] / MapSettings.SQUARE + 1)):
            for indexY in range(int(yAxis[0] / MapSettings.SQUARE), int(yAxis[1] / MapSettings.SQUARE + 1)):
                collisions = check_for_collision_with_list(quad, gameMap.grounds.get(indexY, indexX))
                if collisions:
                    return set([rect.groundType for rect in collisions])

        return GroundType.NOTHING_DEFAULT

    def getWallHeightFromRect(self, gameMap, rect, squares, specialOnly):
        """ Get wallheights from Rect, does not support rotation. """
        for indexX, indexY in squares:
            collisions = rabbyt.collisions.aabb_collide_single(rect, gameMap.basicWalls.get(indexY, indexX))
            if collisions:
                return min([rect.wallHeight for rect in collisions])

        return 0

    def getGroundTypeFromRect(self, gameMap, rect, squares):
        """ Get ground types from Rect, does not support rotation. """
        for indexX, indexY in squares:
            collisions = rabbyt.collisions.aabb_collide_single(rect, gameMap.grounds.get(indexY, indexX))
            if collisions:
                return set([rect.groundType for rect in collisions])

        return GroundType.NOTHING_DEFAULT

    def getEnvironmentValuesFromQuad(self, gameMap, quad, specialOnly=False):
        return (
         self.getWallHeightFromQuad(gameMap, quad, specialOnly), self.getGroundTypeFromQuad(gameMap, quad))

    def getEnvironmentValuesFromRect(self, gameMap, rect, specialOnly=False):
        squares = set([(int(cX / MapSettings.SQUARE), int(cY / MapSettings.SQUARE)) for cX, cY in rect.corners()])
        return (self.getWallHeightFromRect(gameMap, rect, squares, specialOnly),
         self.getGroundTypeFromRect(gameMap, rect, squares))

    def getPlayerEnvironmentValuesFromRect(self, gameMap, rect, specialOnly=False):
        squares = set([(int(cX / MapSettings.SQUARE), int(cY / MapSettings.SQUARE)) for cX, cY in rect.corners()])
        return (self.getWallHeightFromRect(gameMap, rect, squares, specialOnly),
         self.getAccumulatedGroundTypeFromRect(gameMap, rect, squares))

    def _verifyGrounds(self, groundTypes, allowedGroundTypes):
        for groundType in groundTypes:
            if groundType & GroundType.ALL_WATER:
                if GroundType.BRIDGE in groundTypes:
                    return True
                if not groundType & allowedGroundTypes:
                    return False

        return True

    def quadIsWalkable(self, gameMap, quad, allowedWallHeight=0, allowedGroundTypes=4294967295):
        wallHeight, groundTypes = self.getEnvironmentValuesFromQuad(gameMap, quad)
        if wallHeight > allowedWallHeight:
            return False
        else:
            if not self._verifyGrounds(groundTypes, allowedGroundTypes):
                return False
            return True

    def rectIsWalkable(self, gameMap, rect, allowedWallHeight=0, allowedGroundTypes=4294967295):
        wallHeight, groundTypes = self.getEnvironmentValuesFromRect(gameMap, rect)
        if wallHeight > allowedWallHeight:
            return False
        else:
            if not self._verifyGrounds(groundTypes, allowedGroundTypes):
                return False
            return True

    def isPathWalkable(self, gameMap, position_one, position_two, allowedWallHeight=0, allowedGroundTypes=4294967295, radius=18):
        """ Create Rect and beginning and end of positions, then create a polygon to get everything inbetween."""
        angle = getAngleBetweenTwoPoints(position_one, position_two)
        distance = getDistanceBetweenTwoPoints(position_one, position_two)
        if distance == 0:
            return True
        else:
            sX, sY = position_one
            eX, eY = position_two
            betweenPolygon = Polygon(*position_one, *(
             distance,
             radius,
             connectingPointsToPolygon(sX - radius // 2, sY, eX - radius // 2, eY, radius, angle)))
            if angle in directionService.NO_DIAGONAL:
                return self.rectIsWalkable(gameMap, betweenPolygon, allowedWallHeight, allowedGroundTypes)
            startRect = Rect(sX - radius // 2, sY, radius, radius)
            endRect = Rect(eX - radius // 2, eY, radius, radius)
            for rect in (startRect, endRect):
                if not self.rectIsWalkable(gameMap, rect, allowedWallHeight, allowedGroundTypes):
                    return False

            return self.quadIsWalkable(gameMap, betweenPolygon, allowedWallHeight, allowedGroundTypes)

    def charIsPathWalkable(self, char, position_one, position_two, allowedWallHeight=0, allowedGroundTypes=4294967295, radius=18):
        """ Create Rect and beginning and end of positions, then create a polygon to get everything inbetween."""
        return self.isPathWalkable(char.data.map, position_one, position_two, allowedWallHeight, allowedGroundTypes, radius)

    def getRandomValidPathNearChar(self, char, range=300):
        """ ONLY TO BE USED FOR WILD WANDERING OTHERWISE SERVER CAN HANG """
        position = False
        while not position:
            x, y, z = char.getPosition()
            x1 = random.randint(int(x) - range, int(x) + range)
            y1 = random.randint(int(y) - range, int(y) + range)
            position = self.charIsPathWalkable(char, (x, y), (x1, y1))

        return (
         int(x1), int(y1))

    def getClosestPosition(self, char, positionOne, positionTwo, radius=18):
        """ Do a simple interpolation between the two points. (Faster I guess.)"""
        x0, y0 = positionOne
        x1, y1 = positionTwo
        if not self.isPositionInBounds(char.data.map, x1, y1):
            return (
             x0, y0)
        distance = getDistanceBetweenTwoPoints((x0, y0), (x1, y1))
        if distance == 0:
            return (
             x0, y0)
        else:
            step = radius / float(distance)
            xOld = x = x0
            yOld = y0
            dstep = 0.0
            while dstep < 1.0:
                x = interpolate(x0, x1, dstep)
                y = interpolate(y0, y1, dstep)
                if not self.charIsPathWalkable(char, (x0, y0), (x, y), radius):
                    print("FAILURE", x, y, xOld, yOld)
                    return (xOld, yOld)
                xOld = x
                yOld = y
                dstep += step

            if not self.isXYWalkableForChar(char, x1, y1, radius):
                return (xOld, yOld)
            return (
             x1, y1)

    def setSize(self, width, height):
        self.width = width
        self.height = height

    def getMaxHorizontalTileNumber(self):
        return int(math.ceil(self.width / MapSettings.SQUARE))

    def getMaxVerticalTileNumber(self):
        return int(math.ceil(self.height / MapSettings.SQUARE))

    def getMapSize(self):
        return self.game_map.size

    def keepRectInMap(self, x, y, width, height):
        """ Make sure the rect is in map's bounds """
        if width <= self.getMapSize()[0]:
            x = clamp(x, 0, mapContainer.getMapSize()[0] - width)
        if height <= self.getMapSize()[1]:
            y = clamp(y, 0, mapContainer.getMapSize()[1] - height)
        return (x, y)

    def positionInBounds(self, x, y):
        width, height = self.getMapSize()
        if x < 0 or x > width:
            return False
        else:
            if y < 0 or y > height:
                return False
            return True

    def isPositionInBounds(self, gameMap, x, y):
        if x < 0 or x > gameMap.width:
            return False
        else:
            if y < 0 or y > gameMap.height:
                return False
            return True

    def getEnvironmentValuesAtPosition(self, gameMap, x, y, radius=18, specialOnly=False):
        case = Rect(x - radius // 2, y, radius, radius)
        return self.getPlayerEnvironmentValuesFromRect(gameMap, case, specialOnly)


mapContainer = MapContainer()