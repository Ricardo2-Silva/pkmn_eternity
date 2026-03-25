# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\data\system\hotbar.py
import configparser, os, ujson
BAR_TRN = 0
BAR_PKMN = 1
BUTTON_NONE = 0
BUTTON_ITEM = 1
BUTTON_SKILL = 2
BUTTON_POKEMON = 3
MAX_SHARED = 4
MAX_POKEMON = 6
MAX_TRAINER = 6
defaultHotbarConfig = {'shared':[],  'trainer':[],  'pokemon':{}}
for i in range(MAX_SHARED):
    defaultHotbarConfig["shared"].append({'id':0,  'type':0})

class HotbarManager:

    def __init__(self):
        self.file = None
        self.filename = "hotbar.cfg"
        self.config = None

    def reset(self):
        self.save()
        self.config = None

    def setFilePath(self, path):
        self.file = os.path.join(path, self.filename)
        self.loadConfig()

    def loadConfig(self):
        try:
            with open(self.file, "r") as fp:
                self.config = ujson.load(fp)
        except ValueError:
            print("WARNING: Failed to load chat config, creating new one.")
            self._createDefault()
        except FileNotFoundError:
            print("WARNING: Chat config not found, creating new one.")
            self._createDefault()

    def _createDefault(self):
        self.config = defaultHotbarConfig.copy()
        with open(self.file, "w") as fp:
            ujson.dump(defaultHotbarConfig, fp)

    def clearItem(self, nameId):
        """ Searches trainer and shared for item and remove it """
        for button in self.config["trainer"] + self.config["shared"]:
            if button["type"] == BUTTON_ITEM and button["id"] == nameId:
                button["id"] = 0
                button["type"] = 0

        self.save()

    def clearPokemon(self, pokemonId):
        """ Remove Pokemon entirely, should only happen on trade or release """
        pokemonId = str(pokemonId)
        if pokemonId in self.config["pokemon"]:
            del self.config["pokemon"][pokemonId]
            self.save()

    def getPokemon(self, pokemonData):
        pokemonId = str(pokemonData.id)
        if pokemonId not in self.config["pokemon"]:
            self.createPokemon(pokemonData)
        return self.config["pokemon"][pokemonId]

    def getTrainer(self, trainerData):
        if not self.config["trainer"]:
            self.createTrainer(trainerData)
        return self.config["trainer"]

    def getShared(self):
        return self.config["shared"]

    def save(self):
        with open(self.file, "w") as fp:
            ujson.dump(self.config, fp)

    def createPokemon(self, pokemonData):
        pokemonId = str(pokemonData.id)
        self.config["pokemon"][pokemonId] = []
        for _ in range(MAX_POKEMON):
            self.config["pokemon"][pokemonId].append({'id':0,  'type':0})

        for idx, skillData in enumerate(pokemonData.skills.getActiveSkills()):
            self.config["pokemon"][pokemonId][idx]["id"] = skillData.skillInfo.id
            self.config["pokemon"][pokemonId][idx]["type"] = BUTTON_SKILL

        self.save()

    def createTrainer(self, trainerData):
        for _ in range(MAX_TRAINER):
            self.config["trainer"].append({'id':0,  'type':0})

        self.save()


hotbarConfig = HotbarManager()
# global hotbarConfig ## Warning: Unused global
