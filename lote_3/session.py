# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\service\session.py
from client.data.world.eggs import TrainerIncubators, Daycare
from shared.container.constants import IdRange, TrainerGear
from client.data.container.char import charContainer
from client.data.cache import playerFileHandler
from client.data.gui.group import GroupData
from client.data.world.battle import BattleData
from client.data.gui.guild import GuildData
from client.data.gui.bag import BagData
from client.data.gui.pokedex import PokedexData
from shared.container.timing import ClientTickCheck
import time

class SessionService:
    __doc__ = " Store data pertaining to a single session in player, mostly helper functions. "

    def __init__(self):
        self.selected = None
        self.trainer = None
        self.shop = None
        self.trade = False
        self.bag = BagData()
        self.group = GroupData()
        self.guild = GuildData()
        self.pokedex = PokedexData()
        self.battle = BattleData()
        self.incubators = TrainerIncubators()
        self.daycare = Daycare()
        self.npc = None
        self.ticks = ClientTickCheck()
        self.npcId = 0
        self.pingTime = 0
        self.lastMoveSend = time.time()
        self.startMovePosition = (0, 0)
        self.swim = False
        self.ingame = False
        self.instanceId = 0
        self._waiting = False

    @property
    def waiting(self):
        return self._waiting

    @waiting.setter
    def waiting(self, value):
        self._waiting = value

    def canAccessStorage(self):
        if self.trade:
            return False
        else:
            if self.battle.isActive():
                return False
            return True

    def canSwim(self):
        return self.trainer.data.gear & TrainerGear.SWIM

    def reset(self):
        self.__init__()

    def isGroupLeader(self):
        return self.group.isLeader(self.getClientId())

    def trainerIsSelected(self):
        return self.selected == self.trainer

    def getClientChars(self):
        return self.getAllClientChars()

    def selectChar(self, char):
        if not char in self.getClientChars():
            raise AssertionError("Non-player in client chars.")
        else:
            assert char != self.selected, "Char is already selected."
            if self.selected:
                self.selected.deselected()
        self.selected = char
        self.selected.selected()

    def getSelectedPosition(self):
        if self.selected:
            return self.selected.getPosition()

    def isSelected(self, char):
        return self.selected == char

    def getSelectedChar(self):
        """ Return the char currently selected by the player. """
        return self.selected

    def setClientTrainer(self, trainer):
        self.trainer = trainer
        playerFileHandler.setTrainer(trainer.data.name)
        self.group.clientId = trainer.data.id
        self.guild.clientId = trainer.data.id

    def getClientTrainer(self):
        return self.trainer

    def getClientData(self):
        return self.trainer.data

    def getClientId(self):
        return self.trainer.data.id

    def getAllClientChars(self):
        return charContainer.getClientChars()

    def getClientPokemonByID(self, id):
        return charContainer.getDataById(id, IdRange.PC_POKEMON)

    def getClientPokemons(self):
        if self.trainer is None:
            return []
        else:
            return [x for x in charContainer.getClientChars() if x.data.idRange == IdRange.PC_POKEMON]

    def getClientPokemonsData(self):
        return charContainer.getDataByTrainerId(self.trainer.data.id, IdRange.PC_TRAINER)

    def isClientTrainer(self, trainer):
        return self.trainer == trainer

    def isClientChar(self, char):
        return self.isClientTrainer(char) or self.isClientPokemon(char)

    def isClientPokemon(self, pokemon):
        return pokemon in self.getClientPokemons()

    def isClientPokemonData(self, pokemonData):
        return pokemonData in self.getClientPokemonsData()

    def canPokedexScan(self, dexId):
        return self.pokedex.canScan(dexId)

    def isInBattle(self):
        return self.battle.isActive()

    def isCharInBattle(self, char):
        return self.battle.isInBattle(char)

    def canUseNPC(self):
        if self.npcId > 0:
            return False
        else:
            if self.trade:
                return False
            if self.battle.isActive():
                return False
            return True


sessionService = SessionService()
