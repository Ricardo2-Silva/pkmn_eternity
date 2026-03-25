# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\data\cache.py
"""
Created on Oct 27, 2011

@author: Ragnarok
"""
import ujson
from pyglet.image.codecs.png import PNGImageEncoder
from client.control.events import eventManager
from shared.container.constants import IdRange
import os, base64, pyglet
from client.data.system.hotbar import hotbarConfig
from client.data.system.storage import storageConfig
from client.data.system.chat import chatConfig
from client.data.utils.utils import checkFolder
from client.data.file import FolderName
from twisted.python import log
from pyglet.resource import FileLocation
import zlib
from client.data.system.help import helpConfig

class Cache(object):

    def __init__(self, folder, filename):
        self.folder = folder
        self.filePath = os.path.join(folder, filename)
        self.data = ""

    def getWriteableFile(self):
        checkFolder(self.folder)
        try:
            file = open(self.filePath, "w")
        except IOError:
            print("~~~FAILED TO WRITE TO FILE")
            return
        else:
            return file

    def encryptData(self, data):
        try:
            encrypted = base64.b64encode(data.encode())
        except Exception:
            encrypted = b''

        return encrypted.decode()

    def decryptData(self, data):
        decrypted = base64.b64decode(data)
        return decrypted


class AutoTile(Cache):

    def __init__(self):
        Cache.__init__(self, FolderName.TILE_CACHE, "pokedex.ec")
        self.autoTileCache = {}
        self.preloadCache = False
        if self.preloadCache:
            self.loadCache()

    def loadCache(self):
        for path in os.listdir(self.folder):
            if not os.path.isdir(path):
                filename, ext = os.path.splitext(path)
                filename = self.decryptData(filename)
                if filename:
                    self.autoTileCache[filename] = pyglet.resource.image(path)

    def _getSingleCache(self, filename):
        filename = self.encryptData(filename)
        path = os.path.join(self.folder, filename)
        if os.path.isfile(path):
            try:
                return pyglet.resource.image(filename)
            except OSError:
                log.msg(f"Failed to decode: {filename}, attempting to rebuild.")
                return False

        return False

    def getCache(self, filename, size):
        filename = f"{size}x{filename}"
        if filename in self.autoTileCache:
            return self.autoTileCache[filename]
        else:
            cacheFile = self._getSingleCache(filename)
            if cacheFile:
                self.autoTileCache[filename] = cacheFile
                return self.autoTileCache[filename]
            return

    def saveToCache(self, name, size, atlas):
        checkFolder(self.folder)
        name = self.encryptData(f"{size}x{name}")
        atlas.texture.save((os.path.join(self.folder, name)), encoder=(PNGImageEncoder()))
        pyglet.resource._default_loader._index[name] = FileLocation(self.folder)

    def getFile(self, name, size):
        filename = self.encryptData(f"{0}x{1}".format(size, name))
        self.autoTileCache[filename] = pyglet.resource.image(filename)


class Pokedex(Cache):

    def __init__(self):
        self.pokedex = []

    def setFilePath(self, path):
        Cache.__init__(self, path, "pokedex.ec")
        self.loadFile()

    def loadFile(self):
        try:
            with open(self.filePath, "rb") as file:
                self.pokedex = list(file.read())
        except IOError:
            pass

    def getPokedex(self):
        return self.pokedex

    def setPokedex(self, pokedex):
        self.pokedex = pokedex
        self.save()

    def save(self):
        with open(self.filePath, "wb") as file:
            file.write(bytes(self.pokedex))

    def setPokemon(self, dexId, num):
        self.pokedex[dexId] = num
        self.save()

    def getPokemon(self, dexId):
        return self.pokedex[dexId]

    def getChecksum(self):
        return zlib.crc32(bytes(self.pokedex))


class PlayerCacheData:

    def __init__(self, playerId, idRange, name):
        self.id = playerId
        self.idRange = idRange
        self.name = name


class Name(Cache):

    def __init__(self):
        Cache.__init__(self, FolderName.GLOBAL, "trainers.ec")
        self.players = {}
        self.idsToQuery = {}
        for idRange in IdRange.ALL_TYPES:
            self.players[idRange] = {}
            self.idsToQuery[idRange] = []

        eventManager.registerListener(self)
        self.loadFile()

    def loadFile(self):
        try:
            with open(self.filePath, "r") as fp:
                decrypted = self.decryptData(fp.read())
                if decrypted:
                    try:
                        data = ujson.loads(decrypted)
                    except Exception as err:
                        file = self.getWriteableFile()
                        if not file:
                            return
                        file.close()
                        return

                    for idRange in data:
                        iIdRange = int(idRange)
                        for charId in data[idRange]:
                            self.players[iIdRange][int(charId)] = data[idRange][charId]

        except FileNotFoundError:
            file = self.getWriteableFile()
            if not file:
                return
            file.close()

    def setTrainer(self, trainerId, name):
        self.setPlayer(trainerId, IdRange.PC_TRAINER, name)

    def getTrainer(self, trainerId):
        return self.getPlayer(trainerId, IdRange.PC_TRAINER)

    def getPlayer(self, playerId, idRange):
        if playerId in self.players[idRange]:
            return self.players[idRange][playerId]
        else:
            return

    def addIdToGet(self, playerId, idRange):
        if playerId not in self.idsToQuery[idRange]:
            self.idsToQuery[idRange].append(playerId)

    def getIdsToGet(self, idRange):
        return self.idsToQuery[idRange]

    def clearIdsToGet(self, idRange):
        self.idsToQuery[idRange].clear()

    def setPlayer(self, playerId, idRange, name):
        if playerId not in self.players[idRange]:
            self.players[idRange][playerId] = name
        else:
            cached_name = self.players[idRange][playerId]
        if cached_name == name:
            return

    def onQuitGame(self):
        self.save()

    def save(self):
        file = self.getWriteableFile()
        if not file:
            return
        data_to_save = ujson.dumps(self.players)
        towrite = self.encryptData(data_to_save.strip())
        file.write(towrite)
        file.close()


class PlayerDataHandler:

    def __init__(self):
        """ Handles organization of each trainer data, allowing different configurations per character. """
        self.trainers = {}
        self.path = None
        self.loadFolders()

    def loadFolders(self):
        """ Load all player configurations we have """
        for file in os.listdir(FolderName.DATA):
            path = os.path.join(FolderName.DATA, file)
            if os.path.isdir(path):
                self.trainers[file] = path

    def setTrainer(self, trainerName):
        """ We choose the trainer name as the key, if it doesn't exist, the folder doesn't. """
        try:
            self.path = self.trainers[trainerName]
        except KeyError:
            path = os.path.join(FolderName.DATA, trainerName)
            checkFolder(path)
            self.path = self.trainers[trainerName] = path

        chatConfig.setFilePath(self.path)
        hotbarConfig.setFilePath(self.path)
        storageConfig.setFilePath(self.path)
        pokedexCache.setFilePath(self.path)
        helpConfig.setFilePath(self.path)


playerFileHandler = PlayerDataHandler()
nameCache = Name()
pokedexCache = Pokedex()
tileCache = AutoTile()
