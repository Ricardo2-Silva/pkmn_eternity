# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\world\load.py
"""
Created on 19 juil. 2011

@author: Kami
"""
from twisted.internet.defer import inlineCallbacks
from client.data.settings import gameSettings
from client.control.system.sound import mixerController, EnvironmentSound
from client.data.world.animation import Animation
from client.interface.cycle import bgDayNight, bgEffects
from client.control.system.light import Light, lightController
from client.control.world.weather import weatherController
import time, pyglet
from client.data.file import fileManager, archive
from client.control.world.map import Effect, MapGround, MapWall, MapObject, MapObjectShadow, MapEffect
from client.data.world.map import EffectData, MapObjectData, LightData
import client.data.exceptions as exceptions
from client.render.cache import textureCache
from client.control.events.event import eventManager
from client.data.layer import LayerType
from client.data.container.map import mapContainer
from client.interface.map.loading import loadingScreen
from shared.container.constants import MapSettings, RefPointType
from client.control.service.view import viewService
from client.control.camera import worldCamera
import ujson
from client.render.world.map import MapAutotile, MapTileset
from client.render.layer import worldLayer
from shared.service.cycle import dayNight
from client.data.container.char import charContainer
from twisted.internet.task import deferLater
from twisted.internet import reactor
from twisted.logger import Logger
logging = Logger()

def sleep(secs):
    return deferLater(reactor, secs, (lambda: None))


USE_CHUNKS = gameSettings.getGameChunks()
CHUNKS_SIZE = 128

class MapDataLoader:

    def __init__(self):
        self._temp_size = {}

    def preloadTextures(self, gameMap):
        """ Used for chunk loading only, when you are using chunks, still load
        all of the textures as it will reduce stuttering as objects are created. """
        if "autotile" in gameMap.data:
            for size in gameMap.data["autotile"]["files"]:
                for filename in gameMap.data["autotile"]["files"][size]:
                    textureCache.getAutotile(filename, int(size))

        else:
            if "tileset" in gameMap.data:
                for size in gameMap.data["tileset"]["files"]:
                    for filename in gameMap.data["tileset"]["files"][size]:
                        textureCache.getTileset(filename, int(size))

            else:
                if "objects" in gameMap.data:
                    for filename in gameMap.data["objects"]["files"]:
                        sheet = textureCache.getMapObject(filename, 5)
                        if sheet.texture.width >= CHUNKS_SIZE or sheet.texture.height >= CHUNKS_SIZE:
                            self._temp_size[filename] = (
                             sheet.texture.width, sheet.texture.height)

                if "effects" in gameMap.data:
                    for filename in gameMap.data["effects"]["files"]:
                        print("filename", filename)
                        effect = textureCache.getEffect(filename, referencePoint=(RefPointType.CENTER))
                        print("EFFECT", effect)

            if "lights" in gameMap.data:
                for filename in gameMap.data["lights"]["files"]:
                    textureCache.getLight(filename)

    def loadTiles(self, gameMap):
        """ Load all tiles from a string. """
        if USE_CHUNKS:
            if gameSettings.getAutotilesValue():
                self._loadAutoTileChunks(gameMap)
            if gameSettings.getTilesetsValue():
                self._loadTilesetChunks(gameMap)
        else:
            self._loadAllTiles(gameMap)

    def _loadAllTiles(self, gameMap):
        for layer in gameMap.data["layers"]:
            sortedTileset = [tile for tile in gameMap.data["tileset"]["objects"] if tile["layer"] == layer]
            for tileset in sortedTileset:
                self._loadTilesetChunk(gameMap, tileset)

            sortedAutotiles = [tile for tile in gameMap.data["autotile"]["objects"] if tile["layer"] == layer]
            for autotile in sortedAutotiles:
                self._loadAutotileChunk(gameMap, autotile)

    def _loadAllAutotiles(self, gameMap):
        for tile in gameMap.data["autotile"]["objects"]:
            self._loadAutotileChunk(gameMap, tile)

    def _loadAllTilesets(self, gameMap):
        for tile in gameMap.data["tileset"]["objects"]:
            self._loadTilesetChunk(gameMap, tile)

    def _loadAutoTileChunks(self, gameMap):
        for tile in gameMap.data["autotile"]["objects"]:
            x, y = gameMap.get_world_coordinate(tile["pos"])
            col, row = int(x / CHUNKS_SIZE), int(y / CHUNKS_SIZE)
            gameMap.chunks.autotiles.append(tile, row, col)

    def _loadTilesetChunks(self, gameMap):
        for tile in gameMap.data["tileset"]["objects"]:
            x, y = gameMap.get_world_coordinate(tile["pos"])
            col, row = int(x / CHUNKS_SIZE), int(y / CHUNKS_SIZE)
            gameMap.chunks.tilesets.append(tile, row, col)

    def loadAutotileChunk(self, gameMap, row, col):
        for chunk in gameMap.chunks.autotiles.get(row, col):
            self._loadAutotileChunk(gameMap, chunk)

    def _loadAutotileChunk(self, gameMap, chunkData):
        sheet = textureCache.getAutocase(gameMap.data["autotile"]["files"][str(chunkData["size"])][chunkData["file_id"]], chunkData["size"], tuple(chunkData["case"]))
        x, y = chunkData["pos"][0], chunkData["pos"][1]
        tile = MapAutotile(sheet, gameMap, (chunkData["layer"]), x=x, y=y)
        if tile.isAnimated():
            gameMap.animated.append(tile)
        gameMap.tiles.append(tile)

    def loadTilesetChunk(self, gameMap, row, col):
        for chunk in gameMap.chunks.tilesets.get(row, col):
            self._loadTilesetChunk(gameMap, chunk)

    def _loadTilesetChunk(self, gameMap, tileData):
        sheet = textureCache.getTileset(gameMap.data["tileset"]["files"][str(tileData["size"])][tileData["file_id"]], tileData["size"])
        image = sheet[(self.convertToImageGrid)(sheet, *tileData["coord"])]
        if "flip" in tileData:
            image = image.get_transform(flip_x=(tileData["flip"][1]), flip_y=(tileData["flip"][0]))
            image.anchor_x = 0
            image.anchor_y = 0
        x, y = tileData["pos"][0], tileData["pos"][1]
        tile = MapTileset(gameMap, (tileData["layer"]), image, x=x, y=y)
        gameMap.tiles.append(tile)

    def convertToImageGrid(self, sheet, column, row):
        return (
         sheet.rows - 1 - row, column)

    def loadObjects(self, gameMap):
        if "objects" in gameMap.data:
            if USE_CHUNKS is True:
                self._loadObjectChunks(gameMap)
            else:
                for mapObject in gameMap.data["objects"]["objects"]:
                    self._loadObjectChunk(gameMap, mapObject)

    def _night_object(self, name):
        if dayNight.isNight():
            if name == "lamp_04":
                return "lamp_04_night"
        return name

    def _loadObjectChunk(self, gameMap, mapObject):
        if USE_CHUNKS:
            if mapObject["loaded"]:
                return
        else:
            fileId = gameMap.data["objects"]["files"][mapObject["file_id"]]
            position = mapObject["pos"]
            renderingOrder = position[1] - mapObject["order"] if "order" in mapObject else position[1]
            fileId = self._night_object(fileId)
            if "shadow" in mapObject:
                shadow = False
                classObject = MapObject
            else:
                shadow = True
                classObject = MapObjectShadow
            if "flip" in mapObject:
                vertical, horizontal = mapObject["flip"]
            else:
                vertical = False
                horizontal = False
            worldMapObject = classObject(MapObjectData(gameMap, fileId,
              position,
              haveShadow=shadow,
              renderingOrder=renderingOrder,
              flipX=horizontal,
              flipY=vertical))
            if "color" in mapObject:
                (worldMapObject.renderer.setColor)(*mapObject["color"])
            gameMap.objects.append(worldMapObject)
            if worldMapObject.isAnimated():
                gameMap.animated.append(worldMapObject)
        mapObject["loaded"] = True

    def _loadObjectChunks(self, gameMap):
        for map_object in gameMap.data["objects"]["objects"]:
            x, y = gameMap.get_world_coordinate(map_object["pos"])
            col, row = int(x / CHUNKS_SIZE), int(y / CHUNKS_SIZE)
            map_object["loaded"] = False
            filename = gameMap.data["objects"]["files"][map_object["file_id"]]
            if filename in self._temp_size:
                w, h = self._temp_size[filename]
                corners = {(int(x / CHUNKS_SIZE), int((y + h) / CHUNKS_SIZE)),
                 (
                  int((x + w) / CHUNKS_SIZE), int((y + h) / CHUNKS_SIZE)),
                 (
                  int((x + w) / CHUNKS_SIZE), int(y / CHUNKS_SIZE))}
                for corner in corners:
                    gameMap.chunks.objects.append(map_object, corner[1], corner[0])

            gameMap.chunks.objects.append(map_object, row, col)

    def loadObjectChunk(self, gameMap, row, col):
        for chunk in gameMap.chunks.objects.get(row, col):
            self._loadObjectChunk(gameMap, chunk)

    def loadEffects(self, gameMap):
        if "effects" in gameMap.data:
            for effect in gameMap.data["effects"]["objects"]:
                data = EffectData((gameMap.data["effects"]["files"][effect["file_id"]]), (effect["pos"]),
                  animation=Animation(duration=0),
                  renderingOrder=(effect["order"] if "order" in effect else 1),
                  layerType=(LayerType.LAYERED_FIXED))
                data.permanent = True
                effect = MapEffect(data)
                effect.setAlpha(254)
                gameMap.effects.append(effect)
                gameMap.animated.append(effect)

    def loadLights(self, gameMap):
        if "lights" in gameMap.data:
            for light in gameMap.data["lights"]["objects"]:
                gameMap.lights.append(Light(LightData(gameMap.data["lights"]["files"][light["file_id"]], light["pos"], light["rgb"], light["size"], light["mode"])))

    def loadSound(self, gameMap):
        if "sound" in gameMap.data:
            for sound in gameMap.data["sound"]["objects"]:
                gameMap.sound.append(EnvironmentSound(gameMap.data["sound"]["files"][sound["file_id"]], sound["pos"][0], sound["pos"][1], sound["volume"], sound["distance"] if "distance" in sound else None, sound["gain"] if "gain" in sound else None))

    def loadWalls(self, gameMap):
        if "walls" in gameMap.data:
            wall_list = []
            for wallLevel, walls in gameMap.data["walls"].items():
                wallLevel = int(wallLevel)
                for wall in walls:
                    wall_list.append(MapWall(wall["pos"][0], wall["pos"][1], wall["size"][0], wall["size"][1], wallLevel))

            mapContainer.addWalls(gameMap, wall_list)

    def loadGrounds(self, gameMap):
        if "grounds" in gameMap.data:
            ground_list = []
            for groundType, grounds in gameMap.data["grounds"].items():
                groundType = int(groundType)
                for ground in grounds:
                    ground_list.append(MapGround(ground["pos"][0], ground["pos"][1], ground["size"][0], ground["size"][1], groundType))

            mapContainer.addGroundTypes(gameMap, ground_list)


class MapLoader(object):

    def __init__(self):
        eventManager.registerListener(self)
        self.loaded = {}
        self.currentMap = None
        self.loader = MapDataLoader()
        self.currentChunk = None

    def onChunkChange(self):
        if USE_CHUNKS:
            self.loadChunks()

    def onChunkInitialLoad(self):
        if USE_CHUNKS:
            self.loadInitialChunk()

    def setLoaded(self, row, col, objectType=None):
        if row not in self.currentMap.chunks.loaded:
            self.currentMap.chunks.loaded[row] = {}
        self.currentMap.chunks.loaded[row][col] = True

    def isLoaded(self, row, col):
        try:
            return self.currentMap.chunks.loaded[row][col]
        except KeyError:
            return False

    def loadChunks(self):
        x, y = worldCamera.offsetX, worldCamera.offsetY
        chunk = (x // CHUNKS_SIZE, y // CHUNKS_SIZE)
        if chunk != self.currentChunk:
            self._asyncLoadChunk(chunk)
            self.currentChunk = chunk

    def loadInitialChunk(self):
        x, y = worldCamera.offsetX, worldCamera.offsetY
        chunk = (
         x // CHUNKS_SIZE, y // CHUNKS_SIZE)
        self.currentChunk = chunk
        draw_width = round(worldCamera.width / CHUNKS_SIZE) + 1
        draw_height = round(worldCamera.height / CHUNKS_SIZE) + 1
        left = int(chunk[0])
        right = int(chunk[0] + draw_width)
        bottom = int(chunk[1])
        top = int(chunk[1] + draw_height)
        i = 0
        for chunkRowIdx in range(bottom - 1, top):
            for chunkColIdx in range(left - 1, right):
                if not self.isLoaded(chunkRowIdx, chunkColIdx):
                    self.loader.loadAutotileChunk(self.currentMap, chunkRowIdx, chunkColIdx)
                    self.loader.loadTilesetChunk(self.currentMap, chunkRowIdx, chunkColIdx)
                    self.loader.loadObjectChunk(self.currentMap, chunkRowIdx, chunkColIdx)
                    self.setLoaded(chunkRowIdx, chunkColIdx)
                    i += 1

    @inlineCallbacks
    def _asyncLoadChunk(self, chunk):
        """ Asynchronously load each chunk. """
        draw_width = round(worldCamera.width / CHUNKS_SIZE) + 1
        draw_height = round(worldCamera.height / CHUNKS_SIZE) + 1
        left = int(chunk[0])
        right = int(chunk[0] + draw_width)
        bottom = int(chunk[1])
        top = int(chunk[1] + draw_height)
        for chunkRowIdx in range(bottom - 1, top + 1):
            for chunkColIdx in range(left - 1, right + 1):
                if not self.isLoaded(chunkRowIdx, chunkColIdx):
                    self.loader.loadAutotileChunk(self.currentMap, chunkRowIdx, chunkColIdx)
                    self.loader.loadTilesetChunk(self.currentMap, chunkRowIdx, chunkColIdx)
                    self.loader.loadObjectChunk(self.currentMap, chunkRowIdx, chunkColIdx)
                    self.setLoaded(chunkRowIdx, chunkColIdx)
                    yield sleep(0)

    def load(self, gameMap, position):
        filename = fileManager.getMap(gameMap.information.fileName)
        t = time.time()
        logging.info(f"Loading Map: {gameMap.information.fileName}")
        if mapContainer.game_map:
            worldLayer.gameMaps.remove(mapContainer.game_map)
        elif not mapContainer.loadFromCache(gameMap):
            t2 = time.time()
            gameMap.load(ujson.loads(archive.readFile(filename)))
            for area in gameMap.areas:
                if area.areaId == "default":
                    (area.setSize)(*gameMap.data["map_size"])
                    break

            if USE_CHUNKS:
                self.loader.preloadTextures(gameMap)
            mapContainer.game_map = gameMap
            (worldCamera.setCenter)(*position)
            if gameSettings.getObjectsValue():
                self.loader.loadObjects(gameMap)
            loadingScreen.updateLoadingBar()
            self.loader.loadTiles(gameMap)
            loadingScreen.updateLoadingBar()
            if gameSettings.getEffectsValue():
                self.loader.loadEffects(gameMap)
            loadingScreen.updateLoadingBar()
            if gameSettings.getWallsValue():
                self.loader.loadWalls(gameMap)
            loadingScreen.updateLoadingBar()
            if gameSettings.getGroundsValue():
                self.loader.loadGrounds(gameMap)
            self.loader.loadLights(gameMap)
            self.loader.loadSound(gameMap)
            worldLayer.gameMaps.append(gameMap)
        else:
            (worldCamera.setCenter)(*position)
            worldLayer.gameMaps.append(gameMap)
        logging.info(f"Loading Map Time Taken: {time.time() - t}")

    def clean(self):
        """ Clean the current map. """
        mapContainer.cleanMap()

    def onBeforeMapLoad(self):
        lightController.changingMap(mapContainer.game_map)
        weatherController.changingMap()

    def onLogout(self):
        self.onBeforeMapLoad()

    def onMapLoad(self, mapData, position):
        self.clean()
        if self.currentMap is not None:
            if self.currentMap.information.inside is True:
                if mapData.information.inside is False:
                    mixerController.playSound("ExitInside")
            elif mapData.information.inside is True:
                mixerController.playSound("EnterInside")
        self.currentMap = mapData
        logging.info(f"Map Load Start: {mapData.information.fileName} {position}")
        self.load(mapData, position)
        logging.info(f"Map Load End: {mapData.information.fileName}")
        bgDayNight.mapCheck(mapData)
        bgEffects.mapCheck(mapData)
        weatherController.mapCheck(mapData)


mapLoader = MapLoader()
