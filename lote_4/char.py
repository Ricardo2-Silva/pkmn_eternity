# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\data\container\char.py
"""
Created on 23 juil. 2011

@author: Kami
"""
import operator, queue, rabbyt.collisions as collisions
from twisted.internet.task import LoopingCall
from shared.container.constants import IdRange, ObjectFlags, MapSettings
from shared.container.geometry import Point2D, createQuadRotated, Rect
from shared.service.geometry import convertPositionToRect

class ContentType:
    DATA = 1
    CONTROL = 2


class CharacterLoader:
    __doc__ = " A queue that loads players at a set time so as not to cause frame stutter.\n        Loads 2 per frame. Possible use in the future. "

    def __init__(self):
        self.loop = LoopingCall(self.createCharacters)
        self.queue = queue.Queue()
        self.start()

    def start(self):
        self.loop.start(0.005)

    def stop(self):
        self.loop.stop()

    def createCharacters(self):
        if not self.queue.empty():
            char, data = self.queue.get()
            char(data)

    def createCharacter(self, cls, data):
        self.queue.put([cls, data])


charLoader = CharacterLoader()

class CharContainer:
    __doc__ = " A reference to any Char controller in game. Pokemon, trainer, npcs, wild pokemons. "

    def __init__(self):
        self.charById = {}
        self.chars = {}
        self.charsByTrainerId = {}
        self.clientChars = []
        self.clientData = []
        self.allChars = []
        self.cleanAllChars()

    def reset(self):
        for char in self.allChars:
            char.delete()

        self.__init__()

    def addClientChar(self, char):
        self.clientChars.append(char)

    def addClientData(self, data):
        self.clientData.append(data)

    def getClientChars(self):
        return self.clientChars

    def delClientChar(self, char):
        self.clientChars.remove(char)

    def delClientData(self, data):
        self.clientData.remove(data)

    def cleanAllNonClient(self):
        for idRange in IdRange.ALL_TYPES:
            self.charById[idRange] = {(ContentType.DATA): {}, (ContentType.CONTROL): {}}
            self.chars[idRange] = {(ContentType.DATA): [], (ContentType.CONTROL): []}
            self.charsByTrainerId[idRange] = {(ContentType.DATA): {}, (ContentType.CONTROL): {}}

        self.allChars.clear()

    def cleanAllChars(self):
        for idRange in IdRange.ALL_TYPES:
            self.charById[idRange] = {(ContentType.DATA): {}, (ContentType.CONTROL): {}}
            self.chars[idRange] = {(ContentType.DATA): [], (ContentType.CONTROL): []}
            self.charsByTrainerId[idRange] = {(ContentType.DATA): {}, (ContentType.CONTROL): {}}

        self.allChars.clear()

    def wipeService(self):
        """ This wipes all chars except for clients.
            Client data in separate list. """
        for idRange in IdRange.ALL_TYPES:
            for char in self.chars[idRange][ContentType.CONTROL]:
                if char.visible:
                    char.hide()

        self.cleanAllChars()
        self.reAddClientPlayers()

    def reAddClientPlayers(self):
        for char in self.clientChars:
            self.addChar(char)

        for data in self.clientData:
            self.addDataIfNotExist(data)

    def cleanAllCharsExceptPlayers(self):
        for idRange in IdRange.ALL_NPC_TYPES:
            self.charById[idRange] = {(ContentType.DATA): {}, (ContentType.CONTROL): {}}
            self.chars[idRange] = {(ContentType.DATA): [], (ContentType.CONTROL): []}
            self.charsByTrainerId[idRange] = {(ContentType.DATA): {}, (ContentType.CONTROL): {}}

        del self.allChars[:]
        for idRange in IdRange.ALL_PC_TYPES:
            self.allChars += self.chars[idRange][ContentType.CONTROL]

    def getAllCharsInDirection(self, idRange, x, y, z, direction, distance, height=18):
        quad = createQuadRotated(x, y, distance, height, direction)
        return collisions.aabb_collide_single(quad, self.chars[idRange][ContentType.CONTROL])

    def getAllWildPokemonInArea(self, x, y, width, height):
        rect = Rect(x - width // 2, y - height // 2, width, height)
        return collisions.aabb_collide_single(rect, self.chars[IdRange.NPC_WILD_PKMN][ContentType.CONTROL])

    def getAllInteractablesInDirection(self, x, y, z, direction, distance, height=18):
        quad = createQuadRotated(x, y, distance, height, direction)
        return collisions.aabb_collide_single(quad, self.chars[IdRange.NPC_CHARACTER][ContentType.CONTROL] + self.chars[IdRange.NPC_OBJECT][ContentType.CONTROL] + self.chars[IdRange.NPC_ITEM][ContentType.CONTROL])

    def getAllCollidingObjects(self, x, y, width=1, height=1):
        t = [x for x in self.chars[IdRange.NPC_OBJECT][ContentType.CONTROL] if x.data.flags & ObjectFlags.COLLISION if x.visible]
        return collisions.aabb_collide_single(convertPositionToRect(width, height, x, y), t)

    def testCircle(self, x, y, radius=8):
        t = [x for x in self.chars[IdRange.NPC_OBJECT][ContentType.CONTROL] if x.data.flags & ObjectFlags.COLLISION if x.visible]
        return collisions.collide_single((x, y, radius), t)

    def getCharAtPosition(self, x, y):
        """ Return the first char at this position (Layer counts.) """
        collidingChars = collisions.aabb_collide_single(Point2D(x, y), self.allChars)
        if collidingChars:
            collidingChars = [x for x in collidingChars if x.visible if not x.renderer.fading]
            if collidingChars:
                collidingChars.sort(key=(operator.attrgetter("_realY_")))
                for char in collidingChars:
                    if char.data.isWorldObject():
                        if char.data.flags & ObjectFlags.NO_INTERACT:
                            continue
                    return char

        return False

    def positionToSquareIndex(self, x, y):
        return (
         int(y / MapSettings.SQUARE), int(x / MapSettings.SQUARE))

    def dataExists(self, id, idRange):
        if id in self.charById[idRange][ContentType.DATA]:
            return True
        else:
            return False

    def addDataIfNotExist(self, data):
        if not self.dataExists(data.id, data.idRange):
            self.addData(data)

    def addCharIfNotExist(self, char):
        data = char.data
        if not self.charExists(data.id, data.idRange):
            self.addChar(char)

    def charExists(self, id, idRange):
        if id in self.charById[idRange][ContentType.CONTROL]:
            return True
        else:
            return False

    def getDataByIdIfAny(self, id, idRange):
        """ Returns the data if it exists. If not then it returns None. """
        if self.dataExists(id, idRange):
            return self.charById[idRange][ContentType.DATA][id]
        else:
            return

    def getCharByIdIfAny(self, id, idRange):
        """ Returns the char if it exists. If not then it returns None. """
        if self.charExists(id, idRange):
            return self.charById[idRange][ContentType.CONTROL][id]
        else:
            return

    def getDataById(self, id, idRange):
        if self.dataExists(id, idRange):
            return self.charById[idRange][ContentType.DATA][id]
        raise Exception("There's no data for this id.")

    def getCharById(self, id, idRange):
        if self.dataExists(id, idRange):
            return self.charById[idRange][ContentType.CONTROL][id]
        raise Exception("There's no char for this char id.")

    def getCharsByTrainerId(self, id, idRange):
        if id in self.charsByTrainerId[idRange][ContentType.CONTROL]:
            return self.charsByTrainerId[idRange][ContentType.CONTROL][id]
        else:
            return []

    def getDataByTrainerId(self, id, idRange):
        if id in self.charsByTrainerId[idRange][ContentType.DATA]:
            return self.charsByTrainerId[idRange][ContentType.DATA][id]
        else:
            return []

    def getDatasByTrainerId(self, id, idRange):
        if id in self.charsByTrainerId[idRange][ContentType.DATA]:
            return self.charsByTrainerId[idRange][ContentType.DATA][id]
        raise Exception("There's no data for this trainer id.")

    def _addToTrainerId(self, data, idRange, contentType, trainerId):
        if trainerId not in self.charsByTrainerId[idRange][contentType]:
            self.charsByTrainerId[idRange][contentType][trainerId] = []
        if data in self.charsByTrainerId[idRange][contentType][trainerId]:
            raise Exception("This data is already registered for this trainer id.")
        self.charsByTrainerId[idRange][contentType][trainerId].append(data)

    def _delToTrainerId(self, data, idRange, contentType, trainerId):
        if trainerId not in self.charsByTrainerId[idRange][contentType]:
            raise Exception("Trainer doesn't exist")
        if data not in self.charsByTrainerId[idRange][contentType][trainerId]:
            raise Exception("This data is not registered for this trainer id.")
        self.charsByTrainerId[idRange][contentType][trainerId].remove(data)

    def addData(self, data):
        if not self.dataExists(data.id, data.idRange):
            self.chars[data.idRange][ContentType.DATA].append(data)
            self.charById[data.idRange][ContentType.DATA][data.id] = data
            if data.idRange in IdRange.ASSOC_TRAINER:
                self._addToTrainerId(data, IdRange.ASSOC_TRAINER[data.idRange], ContentType.DATA, data.trainerId)

    def delData(self, data):
        if not self.dataExists(data.id, data.idRange):
            raise Exception("This data doesn't exist, it can't be deleted.")
        self.chars[data.idRange][ContentType.DATA].remove(data)
        del self.charById[data.idRange][ContentType.DATA][data.id]
        if data.idRange in IdRange.ASSOC_TRAINER:
            self._delToTrainerId(data, IdRange.ASSOC_TRAINER[data.idRange], ContentType.DATA, data.trainerId)

    def delChar(self, char, deleteData=True):
        data = char.data
        if not self.charExists(data.id, data.idRange):
            raise Exception("This char doesn't exist in charservice.")
        self.chars[data.idRange][ContentType.CONTROL].remove(char)
        if char.followTarget:
            char.followTarget = None
        self.allChars.remove(char)
        del self.charById[data.idRange][ContentType.CONTROL][data.id]
        if data.idRange in IdRange.ASSOC_TRAINER:
            self._delToTrainerId(char, IdRange.ASSOC_TRAINER[data.idRange], ContentType.CONTROL, data.trainerId)
        if deleteData:
            self.delData(data)

    def addChar(self, char):
        data = char.data
        if self.charExists(data.id, data.idRange):
            raise Exception("This char exist already in charservice.")
        self.chars[data.idRange][ContentType.CONTROL].append(char)
        self.allChars.append(char)
        self.charById[data.idRange][ContentType.CONTROL][data.id] = char
        if data.idRange in IdRange.ASSOC_TRAINER:
            self._addToTrainerId(char, IdRange.ASSOC_TRAINER[data.idRange], ContentType.CONTROL, data.trainerId)
        if not self.dataExists(data.id, data.idRange):
            self.addData(data)


charContainer = CharContainer()
