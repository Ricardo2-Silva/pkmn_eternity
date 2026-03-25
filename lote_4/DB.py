# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\data\DB.py
"""
Created on 22 juil. 2011

@author: Kami
"""
import os.path, time
from lxml import etree as ET
from twisted.internet import defer, reactor, threads
import pyglet
from client.control.service.session import sessionService
from client.control.world.map import MapRect
from client.data.world.map import GameMap
from pyglet.resource import ResourceNotFoundException
from shared.container.constants import ItemUsage, IdRange, TargetType, Element, WeatherFlag, ItemType, Messages
from shared.container.exp import ExpMethods
from shared.container.skill import SkillInfo
from shared.container.utils.store import DBIdName
from shared.service.cycle import dayNight
from .file import archive
from .settings import gameSettings
language = "english"

class MessageDB(DBIdName):
    FILENAME = f"lib/language/{language}.xml"

    def __init__(self):
        self.messages = {}
        DBIdName.__init__(self, "Messages", "Message DB")

    def _init(self):
        fileObj = archive.openFile(self.FILENAME)
        tree = ET.parse(fileObj)
        self.root = tree.getroot()
        for message in self.root.findall("message"):
            self.messages[message.attrib["id"]] = message.text.replace("\\n", "\n")

    def getMessageByValue(self, value):
        try:
            return self.messages[Messages(value).name]
        except ValueError:
            return f"Unknown message {value}"

    def __getitem__(self, item):
        try:
            return self.messages[item]
        except KeyError:
            return "Unknown"


class AccessoryTemplate:
    __doc__ = " This is the accessory data containing the template data for "
    __slots__ = ["id", "name", "restrictions", "description"]

    def __init__(self, accessoryId, name, restrictions, description):
        self.id = accessoryId
        self.name = name
        self.restrictions = restrictions
        self.description = description


class AppearanceDB:
    FILENAME = "lib/appearance_db.xml"

    def __init__(self):
        self.clothes = {}
        self.accessories = {}
        self._init()

    def _init(self):
        fileObj = archive.openFile(self.FILENAME)
        tree = ET.parse(fileObj)
        root = tree.getroot()
        for accessory in root.find("accessories"):
            data = AccessoryTemplate(int(accessory.attrib["id"]), accessory[0].text, int(accessory[1].text), accessory[2].text)
            self.accessories[data.id] = data

        for clothes in root.find("clothes"):
            data = AccessoryTemplate(int(clothes.attrib["id"]), clothes[0].text, int(clothes[1].text), clothes[2].text)
            self.clothes[data.id] = data

    def getClothesName(self, clothesId):
        try:
            return self.clothes[clothesId].name
        except KeyError:
            return "Default"

    def getAccessoryName(self, accessoryId):
        try:
            return self.accessories[accessoryId].name
        except KeyError:
            return "None"


appearanceDB = AppearanceDB()

class ItemDBTemplate:
    id = 0
    nameId = 0
    internal = "Unknown"
    formatted = "Unknown"
    description = "Unknown"
    useOutBattle = 0
    useInBattle = 0
    buy = 0
    target = 0
    coolDown = 0
    type = 0


class ItemDB(DBIdName):
    FILENAME = "lib/item_db.xml"

    def __init__(self):
        DBIdName.__init__(self, "ItemDB", "Item Name Id")

    def _init(self):
        fileObj = archive.openFile(self.FILENAME)
        dummyItem = ItemDBTemplate()
        for event, itemElement in ET.iterparse(fileObj, events=('start', 'end')):
            if event == "start":
                if itemElement.tag == "item":
                    itemData = ItemDBTemplate()
                    itemData.id = itemData.nameId = int(itemElement.attrib["id"])
                    itemData.internal = itemElement.attrib["nameId"]
                    if "graphicId" in itemElement.attrib:
                        itemData.graphicId = int(itemElement.attrib["graphicId"])
                    else:
                        itemData.graphicId = itemData.id
                if event == "end":
                    if itemElement.tag == "name":
                        itemData.formatted = itemElement.text
            elif itemElement.tag == "itemType":
                try:
                    itemData.type = int(itemElement.text)
                except ValueError:
                    itemData.type = ItemType.strToInt[itemElement.text]

            elif itemElement.tag == "description":
                itemData.description = itemElement.text
            elif itemElement.tag == "price":
                itemData.buy = int(itemElement.text)
            elif itemElement.tag == "useOutBattle":
                itemData.useOutBattle = int(itemElement.text)
            elif itemElement.tag == "useInBattle":
                itemData.useInBattle = int(itemElement.text)
            elif itemElement.tag == "target":
                itemData.target = TargetType.toInt[itemElement.text]
            elif itemElement.tag == "cooldown":
                itemData.coolDown = int(itemElement.text)
            else:
                if itemElement.tag == "item":
                    self._set(itemData.id, itemData.internal.upper(), itemData)
                    itemElement.clear()

    def getItem(self, nameId):
        item = self.getByIdIfAny(nameId)
        if not item:
            return
        else:
            return item

    def getItemGraphic(self, nameId):
        item = self.getByIdIfAny(nameId)
        if item:
            return item.graphicId
        else:
            return 0

    def name(self, nameId):
        item = self.getByIdIfAny(nameId)
        if not item:
            return "None"
        else:
            return item.formatted

    def canUse(self, target, nameId):
        itemData = self.getItem(nameId)
        if sessionService.isInBattle():
            flag = itemData.useInBattle
        else:
            flag = itemData.useOutBattle
        if flag == ItemUsage.NONE:
            return False
        else:
            if itemData.target & TargetType.SELF:
                if sessionService.getClientData() != target:
                    return False
            if itemData.target & TargetType.POKEMON:
                if target.idRange != IdRange.PC_POKEMON:
                    return False
            return itemData

    def description(self, nameId):
        return self.getById(nameId).description


class NatureDB:
    FILENAME = "lib/nature_db.txt"

    def __init__(self):
        self.t = {}
        file = archive.openFile(self.FILENAME)
        for line in file:
            line = line.decode()
            if "#" not in line[0] and "\n" not in line[0]:
                a = line.split(",")
                self.t[int(a[0])] = a[1]

        file.close()

    def name(self, natureId):
        if natureId in self.t:
            return self.t[natureId]
        else:
            return "Unknown"


class AbilityDB:

    def __init__(self):
        try:
            f = archive.openFile("lib/abilities.txt")
            self.t = {}
            for line in f:
                line = line.decode()
                if "#" not in line[0] and "\n" not in line[0]:
                    a = line.split(",")
                    self.t[int(a[0])] = (a[1], a[2], a[3].strip())

            f.close()
        except IOError as e:
            print(e)
            raise

    def name(self, id):
        try:
            return self.t[id][1]
        except Exception:
            return "None"

    def description(self, id):
        try:
            return self.t[id][2]
        except Exception:
            return "None"


class PokemonDBTemplate:
    return


class PokemonDB(DBIdName):
    FILENAME = "lib/pokemon.txt"

    def __init__(self):
        DBIdName.__init__(self, "PokemonDB", "Dex Id")

    def _init(self):
        fileObj = pyglet.resource.file("lib/pokemon.json")
        for pokemon in ujson.load(fileObj):
            p = PokemonDBTemplate()
            p.__dict__ = pokemon
            self._set(p.dexId, p.name, p)

    def getPokemon(self, dexId):
        return self.getByIdIfAny(dexId)

    def name(self, dexId):
        try:
            return self.getById(dexId).name
        except KeyError:
            return "Unknown"

    def internal(self, dexId):
        return self.getById(dexId).internal

    def species(self, dexId):
        return self.getById(dexId).species

    def growthRate(self, dexId):
        return self.getById(dexId).growthRate

    def pokedex(self, dexId):
        return self.getById(dexId).pokedex

    def type(self, dexId):
        pokemon = self.getById(dexId)
        return (pokemon.type1, pokemon.type2)

    def color(self, dexId):
        return self.getById(dexId).color

    def height(self, dexId):
        return self.getById(dexId).height

    def weight(self, dexId):
        return self.getById(dexId).weight

    def evolutions(self, dexId):
        return self.getById(dexId).pokedex

    def eggGroups(self):
        return


class AnimationSequence:

    def __init__(self):
        self.frames = []


class AnimFrameInfo:
    return


class AnimGroup:

    def __init__(self):
        self.directions = []


import ujson
from json import JSONEncoder
from twisted.internet.task import cooperate, coiterate

class AsyncJSON(object):

    def __init__(self, value):
        self._value = value

    def beginProducing(self, consumer):
        self._consumer = consumer
        self._iterable = JSONEncoder().iterencode(self._value)
        self._consumer.registerProducer(self, True)
        self._task = cooperate(self._produce())
        d = self._task.whenDone()
        d.addBoth(self._unregister)
        return d

    def pauseProducing(self):
        self._task.pause()

    def resumeProducing(self):
        self._task.resume()

    def stopProducing(self):
        self._task.stop()

    def _produce(self):
        for chunk in self._iterable:
            self._consumer.write(chunk)
            yield

    def _unregister(self, passthrough):
        self._consumer.unregisterProducer()
        return passthrough


def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]


class FrameData:

    def __init__(self):
        self.pokemon = {}
        self.default = ujson.load(pyglet.resource.file("lib/pokemon/frame_data/000.json"))

    def getPokemon(self, dexId, gender='m', form=0):
        """Data stripped down to 1-3 characters to reduce load times.
        Frames: "fr"
        Directions: "dir"

        Frame Data:
        Rush Point: "rp"
        Hit Point: "hp"
        Return Point: "rp"

        frame:
            Index: "i"
            Sprite Offset: "o"
            Shadow Offset: "s"
            Flip: "f"
            Frame Duration: "d"

        Total Duration: "t"

        """
        frame_key = (
         dexId, gender, form)
        if frame_key in self.pokemon:
            return self.pokemon[frame_key]
        else:
            additional = ""
            if gender == "f":
                additional += "-f"
            else:
                if form != 0:
                    additional += f"-{form}"
                try:
                    new_file = pyglet.resource.file(f"lib/pokemon/frame_data/{str(dexId).zfill(3)}{additional}.json")
                except ResourceNotFoundException:
                    new_file = pyglet.resource.file(f"lib/pokemon/frame_data/{str(dexId).zfill(3)}.json")

            self.pokemon[frame_key] = ujson.load(new_file)
            return self.pokemon[frame_key]

    def _fetchFrameData(self, dexId):
        self.pokemon[dexId] = ujson.load(pyglet.resource.file(f"lib/pokemon/frame_data/{str(dexId).zfill(3)}.json"))
        return self.pokemon[dexId]

    def _fetchFrameDataCallback(self, deferred, dexId):
        f = pyglet.resource.file(f"lib/pokemon/frame_data/{str(dexId).zfill(3)}.json")
        deferred.callback(f)

    def getPokemonAsync(self, dexId):
        deferred = defer.Deferred()
        reactor.callLater(0.01, self._fetchFrameDataCallback, deferred, dexId)
        return deferred

    def getPokemonThread(self, dexId):
        deferred = threads.deferToThread(self._fetchFrameData, dexId)
        return deferred

    def preloadPokemon(self):
        if gameSettings.getAdditionalPreload():

            def _preload(count=300):
                t = time.time()
                for i in range(count):
                    self.getPokemon(i)

                print(f"Time to preload #{count} frame data files was {time.time() - t}")
                return True

            deferred = threads.deferToThread(_preload)
            return deferred
        else:
            return False

    def getPokemonXML(self, dexId):
        if dexId in self.pokemon:
            print("GOT A SECOND TIME")
            return self.pokemon[dexId]
        else:
            test = ET.XMLParser()
            data = pyglet.resource.file(f"lib/pokemon/frame_data_xml/{str(dexId).zfill(3)}.xml")

            def parse_XML_Chunks(data, context):
                for line in batch(data, 200):
                    test.feed(line)
                    yield

                context["result"] = test.close()

            t1 = time.time()
            context = {}
            d = coiterate(parse_XML_Chunks(data.read(), context))
            d.addCallback(self._getPokemonAsync, context, dexId, t1)
            self.pokemon[dexId] = d
            return d

    def _getPokemonAsync(self, ignored, context, dexId, t1):
        sequenceList = []
        for sequence in context["result"].find("AnimSequenceTable"):
            sequenceInfo = AnimationSequence()
            sequenceInfo.totalDuration = 0
            for element in sequence:
                if element.tag == "RushPoint":
                    sequenceInfo.rushPoint = int(element.text)
                elif element.tag == "HitPoint":
                    sequenceInfo.hitPoint = int(element.text)
                elif element.tag == "ReturnPoint":
                    sequenceInfo.returnPoint = int(element.text)
                else:
                    if element.tag == "AnimFrame":
                        frameData = AnimFrameInfo()
                        for frame in element:
                            if frame.tag == "MetaFrameGroupIndex":
                                frameData.frameIndex = int(frame.text)
                            elif frame.tag == "Sprite":
                                frameData.offset = []
                                for offset in frame:
                                    frameData.offset.append(int(offset.text))

                            elif frame.tag == "HFlip":
                                frameData.flip = int(frame.text)
                            else:
                                if frame.tag == "Duration":
                                    sequenceInfo.totalDuration += int(frame.text)
                            frameData.duration = sequenceInfo.totalDuration

                        sequenceInfo.frames.append(frameData)

            sequenceList.append(sequenceInfo)

        actions = []
        for animGroupElements in context["result"].find("AnimGroupTable"):
            group = AnimGroup()
            for sequenceIndex in animGroupElements:
                group.directions.append(sequenceList[int(sequenceIndex.text)])

            actions.append(group)

        self.pokemon[dexId] = actions
        print("FINISHED PARSING", dexId, time.time() - t1)
        return actions

    def getPokemon2(self, dexId):
        t1 = time.time()
        if dexId in self.pokemon:
            return self.pokemon[dexId]
        else:
            tree = ET.parse(pyglet.resource.file(f"lib/pokemon/frame_data_xml/{str(dexId).zfill(3)}.xml"))
            root = tree.getroot()
            sequenceList = []
            for sequence in root.find("AnimSequenceTable"):
                sequenceInfo = AnimationSequence()
                sequenceInfo.totalDuration = 0
                for element in sequence:
                    if element.tag == "RushPoint":
                        sequenceInfo.rushPoint = int(element.text)
                    elif element.tag == "HitPoint":
                        sequenceInfo.hitPoint = int(element.text)
                    elif element.tag == "ReturnPoint":
                        sequenceInfo.returnPoint = int(element.text)
                    else:
                        if element.tag == "AnimFrame":
                            frameData = AnimFrameInfo()
                            for frame in element:
                                if frame.tag == "MetaFrameGroupIndex":
                                    frameData.frameIndex = int(frame.text)
                                elif frame.tag == "Sprite":
                                    frameData.offset = []
                                    for offset in frame:
                                        frameData.offset.append(int(offset.text))

                                elif frame.tag == "HFlip":
                                    frameData.flip = int(frame.text)
                                else:
                                    if frame.tag == "Duration":
                                        sequenceInfo.totalDuration += int(frame.text)
                                frameData.duration = sequenceInfo.totalDuration

                            sequenceInfo.frames.append(frameData)

                sequenceList.append(sequenceInfo)

            actions = []
            for animGroupElements in root.find("AnimGroupTable"):
                group = AnimGroup()
                for sequenceIndex in animGroupElements:
                    group.directions.append(sequenceList[int(sequenceIndex.text)])

                actions.append(group)

            self.pokemon[dexId] = actions
            return actions


sheetExperiment = FrameData()

class SkillDB(DBIdName):
    FILENAME = "lib/moves_db.xml"

    def __init__(self):
        DBIdName.__init__(self, "SkillDB", "Skill Id")

    def _init(self):
        fileObj = archive.openFile(self.FILENAME)
        for event, skill in ET.iterparse(fileObj, events=('start', 'end')):
            if event == "start":
                if skill.tag == "skill":
                    skillData = SkillInfo()
                    skillData.id = int(skill.attrib["id"])
                    skillData.nameId = skill.attrib["nameId"]
                    if "graphicId" in skill.attrib:
                        skillData.graphicId = int(skill.attrib["graphicId"])
                    else:
                        skillData.graphicId = skillData.id
                if event == "end":
                    if skill.tag == "name":
                        skillData.name = skill.text
            elif skill.tag == "baseDamage":
                skillData.baseDamage = int(skill.text)
            elif skill.tag == "element":
                skillData.elementName = skill.text
                skillData.element = Element.toInt[skillData.elementName]
            elif skill.tag == "category":
                skillData.category = skill.text
            elif skill.tag == "accuracy":
                skillData.category = int(skill.text)
            elif skill.tag == "energy":
                skillData.energy = int(skill.text)
            elif skill.tag == "status":
                skillData.effectChance = int(skill.attrib["chance"])
                skillData.effect = skill.text
            elif skill.tag == "contest":
                skillData.contest = skill.text
            elif skill.tag == "description":
                skillData.description = skill.text
            elif skill.tag == "target":
                split_targets = skill.text.split("|")
                for tg in split_targets:
                    target_int = TargetType.toInt[tg]
                    skillData.target |= target_int
                    skillData.struct += TargetType.toStruct[target_int]

            elif skill.tag == "cooldown":
                skillData.cooldown = int(skill.text)
            elif skill.tag == "flags":
                skillData.flags = skill.text
            elif skill.tag == "range":
                skillData.maxRange = int(skill.text)
            elif skill.tag == "radius":
                skillData.radius = int(skill.text)
            elif skill.tag == "cast":
                skillData.castTime = int(skill.text)
                try:
                    skillData.interruptible = bool(skill.attrib["interruptible"])
                except KeyError:
                    pass

                try:
                    skillData.channeled = bool(skill.attrib["channeled"])
                except KeyError:
                    pass

                try:
                    skillData.allow_movement = False if skill.attrib["movement"] == "False" else True
                except KeyError:
                    pass

            elif skill.tag == "startup_delay":
                skillData.startup_delay = float(skill.text)
            elif skill.tag == "duration":
                skillData.duration = float(skill.text)
                try:
                    skillData.allow_movement = False if skill.attrib["movement"] == "False" else True
                except KeyError:
                    pass

                try:
                    skillData.allow_skills = False if skill.attrib["skills"] == "False" else True
                except KeyError:
                    pass

            else:
                if skill.tag == "skill":
                    self._set(skillData.id, skillData.nameId.upper(), skillData)
                    skill.clear()

    def getSkill(self, skillId):
        return self.getById(skillId)

    def name(self, skillId):
        return self.getById(skillId).name

    def description(self, skillId):
        return self.getById(skillId).description

    def getElement(self, skillId):
        return self.getById(skillId).element

    def getCategory(self, skillId):
        return self.getById(skillId).category

    def getAccuracy(self, skillId):
        return self.getById(skillId).accuracy


START = 0
LOOP = 1
DAY = 0
NIGHT = 1

class BGMData:

    def __init__(self, bgmType, filename, timeOfDay):
        self.bgmType = bgmType
        self.fileName = filename
        self.timeOfDay = timeOfDay


class MapInformation:

    def __init__(self, mapId, filename, elementData):
        self.id = mapId
        self.name = filename
        self.fileName = filename
        self.bgms = []
        self.effects = []
        self.inside = True if elementData.find("inside").text == "True" else False
        self.weather = True if elementData.find("weather").text == "True" else False
        self.weatherType = WeatherFlag.NONE
        self.flags = 0
        self.loadEffects(elementData)
        self.is_cave = "cave" in self.effects

    def __repr__(self):
        return f"MapInformation(id={self.id}, filename={self.fileName})"

    def loadEffects(self, element):
        for effect in element.findall("effect"):
            self.effects.append(effect.attrib["name"])

    def getEffects(self):
        return self.effects


class MapArea(MapRect):

    def __init__(self, *args):
        (MapRect.__init__)(self, *args)
        self.bgms = []

    def getStartBGM(self, timeOfDay=False):
        if timeOfDay:
            bgms = [x for x in self.bgms if x.bgmType == "start" if x.timeOfDay == timeOfDay]
            if bgms:
                return bgms
        return [x for x in self.bgms if x.bgmType == "start"]

    def getLoopBGM(self, timeOfDay=False):
        if timeOfDay:
            if dayNight.isDay():
                timeOfDay = "day"
        elif dayNight.isNight():
            timeOfDay = "night"
        bgms = [x for x in self.bgms if x.bgmType == "loop" if x.timeOfDay == timeOfDay]
        if bgms:
            return bgms
        return [x for x in self.bgms if x.bgmType == "loop"]


class MapDB(DBIdName):

    def __init__(self):
        DBIdName.__init__(self, "Maps", "Map id")

    def getMapNameById(self, mapId):
        mapData = self.getByIdIfAny(mapId)
        if mapData:
            return mapData.areas[0].name
        else:
            return "Unknown"

    def _init(self):
        for filename in archive.listDir("lib/maps/"):
            if filename.endswith(".xml"):
                fileObj = archive.openFile("lib/maps/" + filename)
                tree = ET.parse(fileObj)
                root = tree.getroot()
                mapId = int(root.find("id").text)
                mapName, _ = os.path.splitext(filename)
                gameMap = GameMap(MapInformation(mapId, mapName, root))
                for areaElement in root.findall("area"):
                    areaId = areaElement.attrib["id"]
                    name = areaElement.find("name").text
                    if areaId == "default":
                        areaData = MapArea(0, 0, 0, 0)
                    else:
                        element = areaElement.find("coordinates")
                        x, y = int(element.attrib["x"]), int(element.attrib["y"])
                        element = areaElement.find("size")
                        width, height = size = (int(element.attrib["width"]), int(element.attrib["height"]))
                        areaData = MapArea(x, y, width, height)
                    areaData.areaId = areaId
                    areaData.name = name
                    for bgm in areaElement.findall("bgm"):
                        if not bgm.text[0].isspace():
                            areaData.bgms.append(BGMData(bgm.attrib["type"], bgm.text, "alltimes"))
                        else:
                            for timeOfDay in bgm:
                                areaData.bgms.append(BGMData(bgm.attrib["type"], timeOfDay.text, timeOfDay.tag))

                    gameMap.areas.append(areaData)

                self._set(mapId, mapName.upper(), gameMap)


mapDB = MapDB()

class TextStorageDB:

    def __init__(self):
        self.text = {}

    def store(self, textId, text):
        self.text[textId] = text

    def get(self, textId):
        if textId in self.text:
            return self.text[textId]
        else:
            return


pokemonDB = PokemonDB()
itemDB = ItemDB()
abilityDB = AbilityDB()
skillDB = SkillDB()
messageDB = MessageDB()
textDB = TextStorageDB()
natureDB = NatureDB()
expDB = ExpMethods(pokemonDB)
