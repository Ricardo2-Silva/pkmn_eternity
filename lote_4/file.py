# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\data\file.py
"""
Created on 15 juil. 2011

@author: Kami
"""
from client.data.utils.utils import DynamicObject, checkFolder
from client.data.world.animation import AnimationSpeed
from shared.container.constants import PokemonColor, Gender, CreatureAction, Element
import os, re, sys, zipfile, shutil
from shared.service.utils import inRange
import time, pyglet, subprocess
from client.data.patcher import PatchSettings
from twisted.python import log
BASE_LIBRARY = "lib.pe"
NEW_LIBRARY = "lib_new.pe"

def checkForOldClient():
    if getattr(sys, "frozen", False):
        old_filename = f"{sys.argv[0]}.old"
        if os.path.exists(old_filename):
            try:
                os.remove(old_filename)
            except OSError:
                log.err()


def checkForNewLibraryVersion():
    if os.path.exists(NEW_LIBRARY):
        absPath = os.path.abspath("./")
        if os.path.exists(BASE_LIBRARY):
            os.remove(os.path.join(absPath, BASE_LIBRARY))
        os.rename(os.path.join(absPath, NEW_LIBRARY), os.path.join(absPath, BASE_LIBRARY))


checkForOldClient()
checkForNewLibraryVersion()

class FolderName:
    EFFECT = "lib/effects/"
    SKILL_EFFECTS = "lib/skills/effects/"
    EMOTE = "lib/emotes/"
    POKEMON = "lib/pokemon/"
    TRAINER = "lib/trainer/"
    ITEMS = "lib/items/"
    POKEMON_BEHIND = "lib/pokemon/backs/"
    POKEMON_FRONT = "lib/pokemon/fronts/"
    POKEMON_ICONS = "lib/pokemon/icons/"
    POKEMON_SKILL = "lib/skills/pokemon/"
    AUTOTILE = "lib/autotiles/"
    TILESET = "lib/tilesets/"
    MAPOBJECT = "lib/objects/"
    BG = "lib/bg/"
    PICTURE = "lib/pics/"
    BACKGROUND = "lib/bg/"
    BALL = "lib/balls/"
    MAPS = "lib/maps/"
    CURSOR = "lib/system/"
    ELEMENTS = "lib/pokemon/elements/"
    FOOTPRINTS = "lib/pokemon/footprints/"
    LIGHTS = "lib/lights/"
    PARTICLES = "lib/skills/particles/"
    TRAINER_HAIR = "lib/trainer/hair"
    TRAINER_BODY = "lib/trainer/body"
    TRAINER_HEADGEAR = "lib/trainer/headgear"
    TRAINER_CLOTHES = "lib/trainer/cloth"
    DATA = pyglet.resource.get_settings_path("Pokemon Eternity")
    GLOBAL = os.path.join(DATA, "global")
    TILE_CACHE = os.path.join(DATA, "cache")


class Archive:

    def __init__(self):
        t = time.time()
        pyglet.resource.path.append(BASE_LIBRARY)
        checkFolder(FolderName.DATA)
        checkFolder(FolderName.GLOBAL)
        checkFolder(FolderName.TILE_CACHE)
        pyglet.resource.path.append(FolderName.TILE_CACHE)
        pyglet.resource.reindex()
        print("TIME TO LOAD LIBRARY", time.time() - t, "COUNT:", len(self.nameList()))
        self.zipFile = pyglet.resource.location("lib/appearance_db.xml").zip

    def buildObjectMap(self):
        """This converts an object to the proper path if it has one"""
        object_map = {}
        for filename in self.listDir("lib/objects/"):
            if os.path.splitext(filename)[1] == ".png":
                object_map[os.path.basename(filename)[:-4]] = "lib/objects/" + filename

        return object_map

    def nameList(self):
        return pyglet.resource._default_loader._index

    def listDir(self, folder, zipfile=BASE_LIBRARY):
        """ Returns all the filename from a specific folder """
        return [filename[len(folder):] for filename in pyglet.resource._default_loader._index if folder in filename]

    def getFile(self, path, zipfile=BASE_LIBRARY):
        return self.zipFile.getinfo(path)

    def extractFile(self, fileInfo, path, zipfile=BASE_LIBRARY):
        self.zipFile.extract(fileInfo, path)

    def openFile(self, filename, mode="rb", zipfile=BASE_LIBRARY):
        return pyglet.resource.file(filename, mode)

    def readFile(self, filename, zipfile=BASE_LIBRARY):
        return pyglet.resource.file(filename).read()


archive = Archive()
import zlib

class PatchFileManager:

    def __init__(self):
        self.deletedList = []
        self.addedList = []
        self.patches = {}
        self.ommitFromZip = []
        self.ommitFromFld = []
        self.filesToAdd = {}
        self.archiveZip = pyglet.resource.location("lib/appearance_db.xml").zip
        self.cleanPatchDirectory = True

    def closePatches(self):
        for zips in self.patches:
            self.patches[zips][0].close()

    def openFileFromPatch(self, file, zipfile=BASE_LIBRARY):
        return self.patches[zipfile][0].open(file, "r")

    def readFileFromPatch(self, file, zipfile=BASE_LIBRARY):
        return self.patches[zipfile][0].read(file, "r")

    def writeFileToPatch(self, file, zipfile=BASE_LIBRARY):
        self.patches[zipfile][0].write(file)

    def checkCorruption(self, filename):
        """ Checks if ZIP is corrupt, if Corrupt, will return None, otherwise will return zipfile object """
        try:
            z = zipfile.ZipFile(filename, "r")
            z.read(z.namelist()[0])
            return z
        except zipfile.BadZipfile:
            return

    def cleanPatches(self):
        """ Deletes the folder for the patches once we successfully finish it all. """
        try:
            shutil.rmtree(PatchSettings.patchStorage)
        except OSError:
            log.err()

    def updateBuild(self, patchInfoList):
        """This takes care of updating the build, including adding folders, replacing files, updating the library.
           You cannot delete existing items from a zip, you must create a new one.
        """
        archive_file = pyglet.resource.location("lib/appearance_db.xml").zip
        new_library_required = False
        cached_archive = None
        current_files = archive_file.namelist()
        library_to_add = {}
        library_to_del = []
        new_library_required = False
        for patchInfo in patchInfoList:
            for filename in patchInfo.add_files:
                path = os.path.join(PatchSettings.patchStorage, filename)
                zipObj = self.checkCorruption(path)
                if zipObj:
                    all_patch_files = zipObj.infolist()
                    for fileInfo in all_patch_files:
                        if fileInfo.filename.startswith("lib/"):
                            if not fileInfo.is_dir():
                                if not new_library_required:
                                    if fileInfo.filename in current_files:
                                        new_library_required = True
                                library_to_add[fileInfo.filename] = zipObj.read(fileInfo)
                        else:
                            if fileInfo.filename.endswith(".exe"):
                                if getattr(sys, "frozen", False):
                                    try:
                                        shutil.move(fileInfo.filename, f"{fileInfo.filename}.old")
                                    except OSError:
                                        log.err()

                                    zipObj.extract(fileInfo)
                                else:
                                    zipObj.extract(fileInfo)

                else:
                    os.remove(path)

            zipObj.close()
            for filename in patchInfo.del_files:
                truepath = (os.path.join)(os.curdir, *filename.split("/"))
                folder, ext = os.path.splitext(truepath)
                if not ext:
                    shutil.rmtree(folder)
                else:
                    os.remove(truepath)

            for filename in patchInfo.del_library:
                if not new_library_required:
                    new_library_required = True
                library_to_del.append(filename)

        if new_library_required:
            new_library = zipfile.ZipFile("lib_new.pe", "w")
            omitt_files = library_to_del + list(library_to_add.keys())
            for fileInfo in self.archiveZip.infolist():
                if fileInfo.filename not in omitt_files:
                    new_library.writestr(fileInfo, (self.archiveZip.read(fileInfo)), compress_type=(zipfile.ZIP_DEFLATED))

            for filename, data in library_to_add.items():
                new_library.writestr(filename, data, compress_type=(zipfile.ZIP_DEFLATED))

            new_library.close()
            archive_file.close()
            try:
                shutil.move("lib.pe", "lib.bak")
                os.rename("lib_new.pe", "lib.pe")
            except IOError:
                log.err()

        else:
            archive_file.close()
            archive_file = zipfile.ZipFile("lib.pe", "a")
            for filename, data in library_to_add.items():
                archive_file.writestr(filename, data, compress_type=(zipfile.ZIP_DEFLATED))

        archive_file.close()
        if self.cleanPatchDirectory:
            self.cleanPatches()
        return True


patchFileManager = PatchFileManager()

class SheetFile:
    __slots__ = [
     "name", "frames", "animationDelay"]

    def __init__(self, name, framesHor, framesVert=1, animationDelay=0):
        self.name = name
        self.frames = (framesHor, framesVert)
        self.animationDelay = animationDelay


class FileManager:
    __doc__ = " Stores filenames or sheetFiles, Make the link between IDs, folders and absolute filename."

    def __init__(self):
        """ Creating references on filenames. """
        self.frameCountRegEx = re.compile("\\[(\\d+)\\]")
        self.frameAnimRegEx = re.compile("\\((\\w+)\\)")
        self._worldInit()

    def _worldInit(self):
        """ This loads everything needed for the world """
        global archive
        t = time.time()
        self.emotes = self._listDir(FolderName.EMOTE)
        t1 = time.time()
        self.object_map = archive.buildObjectMap()
        self.sheets = {}
        print("BUILD FILE MANAGER:", time.time() - t, "OBJECT MAP", time.time() - t1)

    def _listDir(self, folder):
        try:
            return archive.listDir(folder)
        except Exception:
            return os.listdir(folder)

    def _extractNumber(self, filename):
        """ Extract the number of frames in the filename. """
        match = self.frameCountRegEx.search(filename)
        if match:
            return int(match.group(1))
        else:
            return 1

    def _extractAnimationSpeed(self, filename):
        """ Try to find an animation speed inside the filename. """
        match = self.frameAnimRegEx.search(filename)
        if match:
            return AnimationSpeed.strToSpeed[match.group(1)]
        else:
            return AnimationSpeed.NORMALFAST

    def _createNameList(self, folder):
        """ In the folders, names are blah[#](anim).png, and we don't know what # can be.
        We make a dict which does the link between blah and blah[#](anim).png """
        fileNameList = self._listDir(folder)
        assocNames = {}
        for filename in fileNameList:
            try:
                filesplit = filename.split("[")
                name = filesplit[0]
                assocNames[name] = SheetFile((folder + filename), (self._extractNumber(filename)), animationDelay=(self._extractAnimationSpeed(filename)))
            except Exception:
                pass

        return assocNames

    def getPokemonIcon(self, id, special=''):
        return "".join([FolderName.POKEMON_ICONS, str(id).zfill(3), special if special else "", ".png"])

    def getPokemonFront(self, id, version, shiny=PokemonColor.NORMAL, gender=Gender.MALE, special=""):
        if not inRange(version, 0, 6):
            raise Exception("Version not in range 0..5")
        return "".join([FolderName.POKEMON_FRONT, "v", str(version), "/", PokemonColor.toString[shiny], "/", str(id).zfill(3), special, ".png"])

    def getPokemonBack(self, id, shiny=PokemonColor.NORMAL, gender=Gender.MALE):
        return "".join([FolderName.POKEMON_BEHIND, PokemonColor.toString[shiny], "/", Gender.toString[gender], "/", str(id).zfill(3), ".png"])

    def getTrainer(self, id):
        return self.trainers[id]

    def getPicture(self, name):
        return "".join([FolderName.PICTURE, name, ".png"])

    def getBackground(self, name):
        return "".join([FolderName.BACKGROUND, name, ".png"])

    def getLight(self, name):
        return "".join([FolderName.LIGHTS, name, ".png"])

    def getEffect(self, name):
        return "".join([FolderName.EFFECT, name, ".png"])

    def getParticleEffect(self, name):
        return "".join([FolderName.PARTICLES, name, ".png"])

    def getSkillEffect(self, name):
        return "".join([FolderName.SKILL_EFFECTS, name, ".png"])

    def getSkillEffectXml(self, name):
        return FolderName.SKILL_EFFECTS + name

    def getBall(self, ballId):
        return "".join([FolderName.BALL, str(ballId).zfill(2), "_[3].png"])

    def getEmote(self, name):
        for emote in self.emotes:
            if emote.startswith(name):
                return "".join([FolderName.EMOTE, emote])

    def getPokemonFootprint(self, dexId):
        return "".join([FolderName.FOOTPRINTS, str(dexId).zfill(3), ".png"])

    def getMap(self, name):
        return "".join([FolderName.MAPS, name, ".emap"])

    def getElementIcon(self, element):
        if isinstance(element, str):
            element = Element.toInt[element]
        return "".join([FolderName.ELEMENTS, str(element).zfill(2), ".png"])

    def getAutotile(self, name, size):
        return "".join([FolderName.AUTOTILE, str(size), "/", name, ".png"])

    def getTileset(self, name, size):
        return "".join([FolderName.TILESET, str(size), "/", name, ".png"])

    def getMapObject(self, name):
        return "".join([FolderName.MAPOBJECT, name, ".png"])

    def getInteractObject(self, name):
        return self.object_map[name]

    def getPokemonSkillIcon(self, skillId):
        return "".join([FolderName.POKEMON_SKILL, str(skillId), ".png"])


fileManager = FileManager()
# global fileManager ## Warning: Unused global
# global patchFileManager ## Warning: Unused global
