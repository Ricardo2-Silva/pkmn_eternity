# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\render\cache.py
import client.render.utils.patch as patch
from client.render.utils.patch import PatchType
from client.data.file import fileManager
from client.data.sprite import Sheet, AutocaseSheet, PokemonSheet, getAnchorPosition, setAnchorPoint, XmlSheet
from shared.container.constants import PokemonColor, Gender, RefPointType
import pyglet, time, math, re
from client.data.cache import tileCache
from twisted.internet import defer, reactor
import ujson
from pyglet.resource import ResourceNotFoundException
from twisted.logger import Logger
from client.data.gui.button import ButtonData, ButtonPatchData
from client.data.gui.padding import PaddingData
from shared.service.utils import clamp
logging = Logger()
t = time.time()

def convertPos(position, xxx_todo_changeme):
    maxRows, maxCols = xxx_todo_changeme
    maxRows -= 1
    maxCols -= 1
    row, col = position
    return (maxRows - row, col)


def arrangeInOrder(obj, maxRow, maxCol):
    new = []
    for row in range(maxRow):
        for col in range(maxCol):
            new.append(obj[convertPos((row, col), (maxRow, maxCol))])

    return new


class AutoCacheInfo:

    def __init__(self, image, caseList, animFrames):
        self.image = image
        self.caseList = caseList
        self.animFrames = animFrames
        self.caseCache = {}

    def getCaseData(self, case):
        if case not in self.caseCache:
            self.caseCache[case] = AutocaseSheet(0, self.image[self.caseList.index(case)], self.animFrames)
        return self.caseCache[case]

    def setCaseData(self, case, caseData):
        self.caseCache[case] = caseData


class AutotileCache:
    __doc__ = " Manage autotiles, cut it in tiles, etc..."

    def __init__(self):
        self.caseArrangement = ((13, 18, 43, 48), (37, 42, 43, 48), (17, 18, 47, 48),
                                (13, 14, 43, 44), (13, 18, 19, 24), (5, 42, 47, 48),
                                (37, 6, 43, 44), (13, 14, 19, 12), (17, 18, 11, 24),
                                (25, 30, 31, 36), (15, 16, 45, 46), (41, 42, 47, 48),
                                (37, 38, 43, 44), (13, 14, 19, 20), (17, 18, 23, 24),
                                (5, 6, 45, 46), (25, 6, 31, 12), (15, 16, 11, 12),
                                (5, 30, 11, 36), (39, 6, 45, 46), (5, 40, 45, 46),
                                (39, 40, 45, 46), (25, 26, 31, 12), (25, 6, 31, 32),
                                (25, 26, 31, 32), (15, 16, 21, 12), (15, 16, 11, 22),
                                (15, 16, 21, 22), (29, 30, 11, 36), (5, 30, 35, 36),
                                (29, 30, 35, 36), (5, 6, 11, 12), (27, 6, 11, 12),
                                (5, 28, 11, 12), (5, 6, 33, 12), (5, 6, 11, 34),
                                (27, 28, 11, 12), (27, 6, 33, 12), (27, 6, 11, 34),
                                (5, 28, 33, 12), (5, 6, 33, 34), (5, 28, 11, 34),
                                (27, 28, 11, 34), (27, 28, 33, 12), (27, 6, 33, 34),
                                (5, 28, 33, 34), (27, 28, 33, 34))
        self.caseArrangementExtra = ((49, 50, 55, 56), (53, 54, 59, 60), (51, 52, 57, 58),
                                     (3, 4, 9, 10))
        self.tiles = {}
        self.tiles[32] = {}
        self.tiles[16] = {}
        self.splitTile = {}
        self.splitTile[32] = {}
        self.splitTile[16] = {}
        self.maxWidth = 1024

    def cacheTextureSize(self, caseCount, tileWidth, tileHeight):
        texturesPerRow = caseCount
        while texturesPerRow * tileWidth > self.maxWidth:
            texturesPerRow -= 1

        return (texturesPerRow * tileWidth, int(math.ceil(caseCount / float(texturesPerRow))) * tileHeight)

    def _cutAutotile(self, name, size):
        """ Creates all the cases for an autotile, and stores them
        This is for pyglet only.
        NOTE: BLITTING IS SUPER SLOW
        """
        t = time.time()
        x = 0
        filename = fileManager.getAutotile(name, size)
        autoTileTexture = pyglet.image.load(filename, file=(pyglet.resource.file(filename)))
        animFrames = int(int(autoTileTexture.width) / int(3 * size))
        allCases = {}
        mode = 1 * bool(autoTileTexture.height > 4 * size)
        lw = size // 2
        splitAnims = pyglet.image.ImageGrid(autoTileTexture, 1, animFrames)
        if autoTileTexture.height > 4 * size:
            caseList = self.caseArrangement + self.caseArrangementExtra
        else:
            caseList = self.caseArrangement
        pieces = {}
        for i in range(0, animFrames):
            frame = splitAnims[i]
            maxRow, maxCol = frame.height // (size // 2), frame.width // (size // 2)
            frameImage = pyglet.image.ImageGrid(frame, frame.height // (size // 2), frame.width // (size // 2))
            pieces[i] = arrangeInOrder(frameImage, maxRow, maxCol)

        atlasTest = (pyglet.image.atlas.TextureAtlas)(*self.cacheTextureSize(len(caseList), size * animFrames, size))
        for case in caseList:
            newPuzzle = pyglet.image.Texture.create(size * animFrames, size)
            for an in range(0, animFrames):
                x += 4
                newPuzzle.blit_into(pieces[an][case[0] - 1], 0 + size * an, lw, 0)
                newPuzzle.blit_into(pieces[an][case[1] - 1], lw + size * an, lw, 0)
                newPuzzle.blit_into(pieces[an][case[2] - 1], 0 + size * an, 0, 0)
                newPuzzle.blit_into(pieces[an][case[3] - 1], lw + size * an, 0, 0)

            atlasTest.add(newPuzzle.get_image_data())

        tileCache.saveToCache(name, size, atlasTest)
        del atlasTest

    def loadAutoTileTest(self, name, size):
        autoTileTexture = tileCache.getCache(name, size)
        if not autoTileTexture:
            self._cutAutotile(name, size)
            autoTileTexture = tileCache.getCache(name, size)
        else:
            findFrames = re.search("\\[(\\d+)\\]", name)
            if findFrames:
                animFrames = int(findFrames.group(1))
            else:
                animFrames = 1
            splitAnims = pyglet.image.ImageGrid(autoTileTexture, autoTileTexture.height // size, autoTileTexture.width // (size * animFrames))
            if len(splitAnims) > len(self.caseArrangement):
                caseList = self.caseArrangement + self.caseArrangementExtra
            else:
                caseList = self.caseArrangement
        self.tiles[size][name] = AutoCacheInfo(splitAnims.get_texture_sequence(), caseList, animFrames)

    def getAutotile(self, name, size):
        if name not in self.tiles[size]:
            self.loadAutoTileTest(name, size)
        return self.tiles[size][name]

    def getAutocase(self, name, size, case):
        autotile = self.getAutotile(name, size)
        try:
            return autotile.getCaseData(case)
        except IndexError:
            print("Something went wrong. Case not found. Recut it.")
            self.loadAutoTileTest(name, size)
            return self.tiles[size][name].getCaseData(case)


autotileCache = AutotileCache()
import sys

class TextureCache:
    __doc__ = " Keep in memory all texture request we make. When a request has been done, he returns it instead of loading it again. "
    default_folder = "trainer_debug" if "-creation" in sys.argv else "lib/trainer"

    def __init__(self):
        self.allReferences = {}
        self.particles = {}
        self.cache = {}
        self.tileset_slices = {}
        self.atlas = {}
        texture_size = clamp(pyglet.image.get_max_texture_size(), 2048, 4096)
        self._createAtlas("player", texture_size, texture_size)
        self._createAtlas("tileset", texture_size, texture_size)
        self._createAtlas("pokemon_portraits", texture_size, texture_size)
        self._createAtlas("lights", texture_size, texture_size)

    def _createAtlas(self, name, width=2048, height=2048):
        if name in self.atlas:
            raise Exception(f"Creating {name} atlas that already exists.")
        self.atlas[name] = pyglet.image.atlas.TextureBin(width, height)
        return self.atlas[name]

    def loadCustomAtlas(self, filename, atlas, border=0):
        file = pyglet.resource.file(filename)
        try:
            img = pyglet.image.load(filename, file=file)
        finally:
            file.close()

        self.cache[filename] = self.atlas[atlas].add(img, border)
        return self.cache[filename]

    def getImageData(self, filename):
        """Differs in that it returns image data, not a texture."""
        file = pyglet.resource.file(filename)
        try:
            img = pyglet.image.load(filename, file=file)
        finally:
            file.close()

        return img

    def _getFromAtlas(self, filename, atlas):
        return atlas.getFile(filename)

    def _getFile(self, filename, atlas=True):
        return pyglet.resource.image(filename, atlas=atlas)

    def getPicture(self, name):
        filename = fileManager.getPicture(name)
        return self._getFile(filename)

    def getBackground(self, name):
        filename = fileManager.getBackground(name)
        return pyglet.resource.image(filename)

    def getGuiImage(self, filename) -> pyglet.image.Texture:
        return self._getFromAtlas(filename, atlasLoader.gui)

    def getImageFile(self, filename, atlas=True):
        return self._getFile(filename, atlas)

    def getPokemonFootprint(self, dexId):
        filename = fileManager.getPokemonFootprint(dexId)
        return self._getFile(filename)

    def getItemIcon(self, itemId):
        return self._getFromAtlas(format(itemId, "03"), atlasLoader.items)

    def getItemSheet(self, id):
        texture = self.getItemIcon(id)
        return Sheet(texture)

    def getPokemonIcon(self, id, special=''):
        filename = fileManager.getPokemonIcon(id, special)
        return self._getFile(filename)

    def getPokemonFront(self, id, version, shiny=PokemonColor.NORMAL, gender=Gender.MALE, special=""):
        filename = fileManager.getPokemonFront(id, version, shiny, gender, special)
        if filename in self.cache:
            return self.cache[filename]
        else:
            image = self.loadCustomAtlas(filename, "pokemon_portraits")
            self.cache[filename] = image
            return image

    def getPokemonBack(self, dexId, shiny=PokemonColor.NORMAL, gender=Gender.MALE):
        filename = fileManager.getPokemonBack(dexId, shiny, gender)
        if filename in self.cache:
            return self.cache[filename]
        else:
            image = self.loadCustomAtlas(filename, "pokemon_portraits")
            self.cache[filename] = image
            return image

    def getElementIcon(self, element):
        filename = fileManager.getElementIcon(element)
        return self._getFile(filename)

    def getAutotile(self, name, size):
        global autotileCache
        return autotileCache.getAutotile(name, size)

    def getAutocase(self, name, size, case):
        return autotileCache.getAutocase(name, size, case)

    def _convertToImageGrid(self, sheet, column, row):
        return (
         sheet.rows - 1 - row, column)

    def getTileset(self, name, size):
        filename = fileManager.getTileset(name, size)
        if filename not in self.cache:
            imageFile = pyglet.resource.image(filename)
            self.cache[filename] = pyglet.image.ImageGrid(imageFile, imageFile.height // size, imageFile.width // size)
            self.tileset_slices[filename] = {}
        return self.cache[filename]

    def getTilesetSlice(self, name, size, coordinates):
        filename = fileManager.getTileset(name, size)
        if filename in self.tileset_slices:
            if coordinates in self.tileset_slices[filename]:
                return self.tileset_slices[filename][coordinates]
        if filename not in self.cache:
            self.getTileset(name, size)
        grid = self.cache[filename]
        image = grid[(self._convertToImageGrid)(grid, *coordinates)]
        added_img = self.atlas["tileset"].add(image, 4)
        self.tileset_slices[filename][coordinates] = added_img
        return added_img

    def getPokemonSkillIcon(self, skillId):
        try:
            filename = fileManager.getPokemonSkillIcon(skillId)
            image = self._getFile(filename)
        except ResourceNotFoundException:
            filename = fileManager.getPokemonSkillIcon(0)
            image = self._getFile(filename)

        return image

    def getBackgroundColor(self, color):
        if color in self.cache:
            return self.cache[color]
        else:
            if color == (255, 0, 255):
                rcolor = (0, 0, 0, 0)
            else:
                rcolor = (
                 color[0], color[1], color[2], 255)
            img = pyglet.image.SolidColorImagePattern(rcolor).create_image(1, 1)
            bin = pyglet.resource._default_loader._get_texture_atlas_bin(1, 1, 1)
            if bin is None:
                self.cache[color] = img.get_texture(False)
            self.cache[color] = bin.add(img)
            return self.cache[color]

    def getButtonBackground(self, filename, patchType=PatchType.FOUR_IMAGE):
        if filename in self.cache:
            return self.cache[filename]
        else:
            imageTexture = pyglet.resource.image(filename)
            if patchType in [PatchType.NINE, PatchType.THREE, PatchType.THREE_VERT]:
                self.cache[filename] = ButtonPatchData(patch.NinePatchImage(imageTexture, PaddingData(5, 5, 8, 8), 4))
            elif patchType == PatchType.FOUR_IMAGE:
                self.cache[filename] = patch.loadButtonBackground(imageTexture)
            else:
                self.cache[filename] = patch.loadOneButtonBackground(imageTexture)
            return self.cache[filename]

    def getButtonBackgroundGUI(self, filename, patchType=PatchType.FOUR_IMAGE, padding=None):
        if filename in self.cache:
            return self.cache[filename]
        else:
            imageTexture = self.getGuiImage(filename)
            if patchType in [PatchType.NINE, PatchType.THREE, PatchType.THREE_VERT]:
                self.cache[filename] = ButtonPatchData(patch.NinePatchImage(imageTexture, padding, 4))
            elif patchType == PatchType.FOUR_IMAGE:
                self.cache[filename] = patch.loadButtonBackground(imageTexture)
            else:
                self.cache[filename] = patch.loadOneButtonBackground(imageTexture)
            return self.cache[filename]

    def getBorder(self, filename, stretch=PaddingData(5, 5, 9, 9)):
        if filename in self.cache:
            return self.cache[filename]
        else:
            image = pyglet.resource.image(filename)
            self.cache[filename] = patch.NinePatchImage(image, stretch)
            return self.cache[filename]

    def getBorderGUI(self, filename, stretch=PaddingData(5, 5, 9, 9)):
        if filename in self.cache:
            return self.cache[filename]
        else:
            imageTexture = self.getGuiImage(filename)
            self.cache[filename] = patch.NinePatchImage(imageTexture, stretch)
            return self.cache[filename]

    def getBorderFromImage(self, filename, image, stretch=PaddingData(5, 5, 9, 9)):
        if filename in self.cache:
            return self.cache[filename]
        else:
            self.cache[filename] = patch.NinePatchImage(image, stretch)
            return self.cache[filename]

    def getPokemon(self, dexId, gender, subspecies):
        filename = "lib/pokemon/{0}_{1}_{2}".format(dexId, gender, subspecies)
        if filename in self.cache:
            return self.cache[filename]
        else:
            dexId, frames = pokemonAtlas.getPokemonImageFrames(dexId, gender, subspecies)
            self.cache[filename] = PokemonSheet(dexId, frames,
              referencePoint=(RefPointType.CENTER))
            return self.cache[filename]

    def preloadTrainers(self):
        for filename, region in atlasLoader.trainers.getAll():
            self.cache[filename] = Sheet(region, frames=(12, 1), referencePoint=(RefPointType.BOTTOMCENTER))

    def getTrainer(self, trainerId):
        filename = "{0}_walk_[12]".format(trainerId)
        if filename in self.cache:
            return self.cache[filename]
        else:
            if not isinstance(trainerId, str):
                raise Exception("Wrong ID to access Trainer Texture Data.")
            self.cache[filename] = Sheet((atlasLoader.trainers.getFile(filename)), frames=(12,
                                                                                           1), referencePoint=(RefPointType.BOTTOMCENTER))
            return self.cache[filename]

    def getTrainerHair(self, gender, hairId):
        filename = f"{self.default_folder}/hair/hair_{str(hairId).zfill(2)}_{gender}.png"
        if filename in self.cache:
            return self.cache[filename]
        else:
            try:
                texture = self.loadCustomAtlas(filename, "player")
            except pyglet.resource.ResourceNotFoundException:
                print("Error: Failed to find:", filename)
                texture = self.loadCustomAtlas(f"{self.default_folder}/hair/hair_01_{gender}.png", "player")

            charSheet = Sheet(texture, frames=(24, 1), referencePoint=(RefPointType.BOTTOMCENTER))
            self.cache[filename] = charSheet
            return charSheet

    def getTrainerClothes(self, body, gender, clothId):
        """ Returns the texture of the clothes as well as the mask """
        filename = f"{self.default_folder}/cloth/cloth_{body}_{str(clothId).zfill(2)}_{gender}"
        if filename in self.cache:
            return self.cache[filename]
        else:
            try:
                clothTexture = self.loadCustomAtlas(f"{filename}.png", "player")
                maskTexture = self.loadCustomAtlas(f"{filename}_mask.png", "player")
            except pyglet.resource.ResourceNotFoundException:
                filename = f"{self.default_folder}/cloth/cloth_{body}_{str(clothId).zfill(2)}"
                if filename in self.cache:
                    return self.cache[filename]
                clothTexture = self.loadCustomAtlas(f"{filename}.png", "player")
                maskTexture = self.loadCustomAtlas(f"{filename}_mask.png", "player")

            clothSheet = Sheet(clothTexture, frames=(6, 12), referencePoint=(RefPointType.BOTTOMCENTER))
            maskSheet = Sheet(maskTexture, frames=(6, 12), referencePoint=(RefPointType.BOTTOMCENTER))
            self.cache[filename] = (
             clothSheet, maskSheet)
            return (
             clothSheet, maskSheet)

    def getTrainerSwimSheet(self):
        filename = f"{self.default_folder}/body/swim_default"
        if filename in self.cache:
            return self.cache[filename]
        else:
            swimTexture = self.loadCustomAtlas(f"{filename}.png", "player")
            swimSheet = Sheet(swimTexture, frames=(6, 4), referencePoint=(RefPointType.BOTTOMCENTER))
            self.cache[filename] = swimSheet
            return swimSheet

    def getTrainerAccessory(self, accessoryId):
        """ Returns the texture of the clothes as well as the mask """
        filename = f"{self.default_folder}/accessory/accessory_{str(accessoryId).zfill(2)}"
        if filename in self.cache:
            return self.cache[filename]
        else:
            accessoryTexture = self.loadCustomAtlas(f"{filename}.png", "player")
            maskTexture = self.loadCustomAtlas(f"{filename}_mask.png", "player")
            accessorySheet = Sheet(accessoryTexture, frames=(24, 1), referencePoint=(RefPointType.BOTTOMCENTER))
            maskSheet = Sheet(maskTexture, frames=(24, 1), referencePoint=(RefPointType.BOTTOMCENTER))
            self.cache[filename] = (
             accessorySheet, maskSheet)
            return (accessorySheet, maskSheet)

    def getTrainerBody(self, bodyId, gender):
        filename = f"{self.default_folder}/body/body_{bodyId}_{gender}.png"
        if filename in self.cache:
            return self.cache[filename]
        else:
            try:
                texture = self.loadCustomAtlas(filename, "player")
            except pyglet.resource.ResourceNotFoundException:
                filename = f"{self.default_folder}/body/body_{bodyId}.png"
                if filename in self.cache:
                    return self.cache[filename]
                texture = self.loadCustomAtlas(filename, "player")

            charSheet = Sheet(texture, frames=(6, 12), referencePoint=(RefPointType.BOTTOMCENTER))
            frameData = ujson.loads(pyglet.resource.file(f"{self.default_folder}/body/body_{bodyId}_frames.json").read())
            self.cache[filename] = (
             charSheet, frameData)
            return self.cache[filename]

    def getTrainerEyes(self, bodyId, eyeId):
        filename = f"{self.default_folder}/body/eyes_{bodyId}_{str(eyeId).zfill(2)}.png"
        if filename in self.cache:
            return self.cache[filename]
        else:
            texture = self.loadCustomAtlas(filename, "player")
            self.cache[filename] = Sheet(texture, frames=(6, 1), referencePoint=(RefPointType.BOTTOMCENTER))
            return self.cache[filename]

    def getLight(self, name):
        filename = fileManager.getLight(name)
        image = self.loadCustomAtlas(filename, "lights", 2)
        setAnchorPoint(image, RefPointType.CENTER)
        return image

    def _getSheet(self, filename, animationDelay=0, referencePoint=None, atlas=True):
        """ Get a sheet from a name, a function in FileManager to get frames """
        if filename in self.cache:
            return self.cache[filename]
        else:
            frames = fileManager._extractNumber(filename)
            if animationDelay:
                animationDelay = fileManager._extractAnimationSpeed(filename)
            self.cache[filename] = Sheet(pyglet.resource.image(filename, atlas=atlas), (frames, 1), animationDelay, referencePoint)
            return self.cache[filename]

    def getParticleEffect(self, name):
        return self._getFile((fileManager.getParticleEffect(name)), atlas=False)

    def getEffect(self, name, referencePoint):
        return self._getSheet((fileManager.getEffect(name)), animationDelay=True, referencePoint=referencePoint)

    def getMapEffect(self, name, referencePoint, delay=False):
        return self._getSheet((fileManager.getEffect(name)), animationDelay=delay, referencePoint=referencePoint)

    def getSkillEffect(self, name, referencePoint, atlas=True):
        return self._getSheet((fileManager.getSkillEffect(name)), referencePoint=referencePoint, atlas=atlas)

    def getSkillXml(self, name, referencePoint):
        return sheetCache.getSheet((fileManager.getSkillEffectXml(name)), referencePoint=referencePoint)

    def getEffectXml(self, name, referencePoint):
        return sheetCache.getSheet(f"lib/{name}", referencePoint=referencePoint)

    def getBall(self, ballId, referencePoint=RefPointType.CENTER):
        return self._getSheet((fileManager.getBall(ballId)), referencePoint=referencePoint)

    def getEmote(self, name):
        return self._getSheet((fileManager.getEmote(name)), referencePoint=(RefPointType.BOTTOMCENTER))

    def getMapObject(self, name, referencePoint):
        return self._getSheet((fileManager.getMapObject(name)), animationDelay=1, referencePoint=referencePoint)

    def getInteractObject(self, name, referencePoint):
        """Differs from map object as this will search all object directories for filename."""
        return self._getSheet((fileManager.getInteractObject(name)), animationDelay=1, referencePoint=referencePoint)


textureCache = TextureCache()
from lxml import etree as ET

class FrameDataCache(object):

    def __init__(self):
        self.files = {}

    def getSheet(self, filename, referencePoint):
        if filename not in self.files:
            tree = ET.parse(pyglet.resource.file(filename + ".xml"))
            imageFile = pyglet.resource.image(filename + ".png")
            frames = []
            for sprite in tree.getroot():
                frame = imageFile.get_region(int(sprite.attrib["x"]), imageFile.height - int(sprite.attrib["y"]) - int(sprite.attrib["h"]), int(sprite.attrib["w"]), int(sprite.attrib["h"]))
                frames.append(frame)

            self.files[filename] = XmlSheet(frames, referencePoint=referencePoint)
        return self.files[filename]


sheetCache = FrameDataCache()
PRELOAD = False

class Atlas(object):

    def __init__(self, filename, default=None):
        self._cache = {}
        tree = ET.parse(pyglet.resource.file(filename + ".xml"))
        self.xml = tree.getroot().findall("sprite")
        self.imageFile = pyglet.resource.image((filename + ".png"), atlas=False)
        self.defaultValue = self.getFile(default) if default else None

    def getAll(self):
        return [(sprite.attrib["n"], self.imageFile.get_region(int(sprite.attrib["x"]), self.imageFile.height - int(sprite.attrib["y"]) - int(sprite.attrib["h"]), int(sprite.attrib["w"]), int(sprite.attrib["h"]))) for sprite in self.xml]

    def getFile(self, name):
        if name in self._cache:
            return self._cache[name]
        for sprite in self.xml:
            if sprite.attrib["n"] == name:
                region = self.imageFile.get_region(int(sprite.attrib["x"]), self.imageFile.height - int(sprite.attrib["y"]) - int(sprite.attrib["h"]), int(sprite.attrib["w"]), int(sprite.attrib["h"]))
                if "oX" in sprite.attrib:
                    region.anchor_x = -int(sprite.attrib["oX"])
                    region.anchor_y = int(sprite.attrib["oH"]) - int(sprite.attrib["oY"]) - int(sprite.attrib["h"])
                    region.oW = int(sprite.attrib["oW"])
                    region.oH = int(sprite.attrib["oH"])
                    region.oY = int(sprite.attrib["oY"])
                    region.oX = int(sprite.attrib["oX"])
                self._cache[name] = region
                return region

        if self.defaultValue:
            return self.defaultValue
        raise Exception(f"Warning {name} not found in {self}. No default specified.")


class MultiAtlas(object):

    def __init__(self, files, default=None):
        self.xml = []
        self.images = []
        for filename in files:
            tree = ET.parse(pyglet.resource.file(filename + ".xml"))
            self.xml.append(tree.getroot().findall("sprite"))
            self.images.append(pyglet.resource.image(filename + ".png"))

        self.defaultValue = self.getFile(default) if default else None

    def getAll(self):
        return [(sprite.attrib["n"], self.imageFile.get_region(int(sprite.attrib["x"]), self.imageFile.height - int(sprite.attrib["y"]) - int(sprite.attrib["h"]), int(sprite.attrib["w"]), int(sprite.attrib["h"]))) for xml in self.xml for sprite in iter(xml)]

    def getFile(self, name):
        for xml in self.xml:
            for sprite in xml:
                if sprite.attrib["n"] == name:
                    imageFile = self.images[self.xml.index(xml)]
                    region = imageFile.get_region(int(sprite.attrib["x"]), imageFile.height - int(sprite.attrib["y"]) - int(sprite.attrib["h"]), int(sprite.attrib["w"]), int(sprite.attrib["h"]))
                    return region

        return self.defaultValue


class PokemonFrames:

    def __init__(self):
        self.default = []
        self.female = []
        self.subspecies = {}

    def getPokemon(self, gender, subspecie):
        """ HEre we attempt to get the subspecie and gender sprite if exists
            If we have a subspecie, see if we have a sprite.
            If no subspecie or subspecie found, check gender, if it's female and we have a female sprite, return it.
            If all else fails, we have the default gender.

        """
        if subspecie:
            try:
                return self.subspecies[subspecie]
            except KeyError:
                pass

        if gender == Gender.FEMALE:
            if self.female:
                return self.female
        return self.default


class PokemonAtlas(MultiAtlas):

    def __init__(self, files, default=None):
        MultiAtlas.__init__(self, files, default)
        self.dexId = {}
        for x in range(301):
            self.dexId[x] = PokemonFrames()

        self.genderMatch = re.compile("\\d+-\\d+-\\d+-\\d+")
        self.subspeciesMatch = re.compile("\\d{3}-\\d+-[A-z]")
        self.buildFrames()

    def buildFrames(self):
        for xml in self.xml:
            for sprite in xml:
                imageFile = self.images[self.xml.index(xml)]
                region = imageFile.get_region(int(sprite.attrib["x"]), imageFile.height - int(sprite.attrib["y"]) - int(sprite.attrib["h"]), int(sprite.attrib["w"]), int(sprite.attrib["h"]))
                frames = self.dexId[int(sprite.attrib["n"][:3])]
                region.trimmed = True
                region.oX = int(sprite.attrib["oX"])
                region.oY = int(sprite.attrib["oY"])
                region.oW = int(sprite.attrib["oW"])
                region.oH = int(sprite.attrib["oH"])
                subspecies = self.subspeciesMatch.search(sprite.attrib["n"])
                if subspecies:
                    if subspecies not in frames.subspecies:
                        frames.subspecies[subspecies] = [
                         region]
                else:
                    frames.subspecies[subspecies].append(region)
                    continue
                    female = self.genderMatch.search(sprite.attrib["n"])
                    if female:
                        frames.female.append(region)
                        continue
                        frames.default.append(region)

    def getPokemonImageFrames(self, dexId, gender, subspecies):
        """This returns the dex ID and the images so we can be sure to get proper frame data on failure."""
        try:
            return (
             dexId, self.dexId[dexId].getPokemon(gender, subspecies))
        except KeyError:
            return (
             0, self.dexId[0].default)

    def getPokemonFramesAsync(self, dexId, gender, subspecies):
        deferred = defer.Deferred()
        reactor.callLater(0, deferred.callback, self.dexId[dexId].getPokemon(gender, subspecies))
        return deferred


pokemonAtlas = PokemonAtlas(('lib/pokemon/overworld/100', 'lib/pokemon/overworld/200',
                             'lib/pokemon/overworld/300'))

class AtlasLoader(object):

    def __init__(self):
        global textureCache
        self.trainers = Atlas("lib/trainer/npcs/trainers", "am01_walk_[12]")
        self.items = Atlas("lib/items/items", "000")
        self.gui = Atlas("lib/gui/gui")
        self.autotiles = []
        PRELOAD_TRAINERS = False
        if PRELOAD_TRAINERS:
            t1 = time.time()
            logging.info("Preloading all NPC Trainers")
            textureCache.preloadTrainers()
            logging.info(f"Preloading NPC Trainers - Complete: {time.time() - t1}")

    def getTile16(self, filename):
        return self.tile16.getFile(filename)

    def getTile(self, filename):
        return self.tile.getFile(filename)

    def getGui(self, filename):
        return self.gui.getFile(filename)

    def getPokemon(self, id):
        return self.pokemon.getFile(id)

    def getItem(self, id):
        return self.items.getFile(id)

    def getTrainer(self, name):
        return self.trainers.getFile(name)


atlasLoader = AtlasLoader()
