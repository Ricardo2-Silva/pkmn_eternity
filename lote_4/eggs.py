# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\data\world\eggs.py
import time
from typing import List, Optional, Any
from attr import dataclass

@dataclass
class PokemonEggParent:
    dexId: int
    ivs: List[int]
    moves: List[int]
    item: int
    ability: int

    def getSQLData(self):
        return (
         
          self.dexId, *self.ivs, *self.moves, self.item, self.ability)


@dataclass
class PokemonEgg:
    id: int
    parentOne: int
    parentTwo: int
    laidTime: float
    state: int
    group: int
    stored: int
    incubatorId: int

    def getSQLData(self):
        return (
         
          self.id, self.parentOne, *self.parentOne.getSQLData(), *self.parentTwo.getSQLData(),
         
          self.laidTime, self.hatchTime, self.group)

    def getState(self):
        return 0

    def getClientData(self):
        return (
         self.id, self.parentOne.dexId, self.parentTwo.dexId, self.laidTime, self.getState(), self.group, self.slot)


@dataclass
class EggIncubator:
    incubatorId: int
    egg: Optional[PokemonEgg]
    startTime: float
    currentUses: int = 0
    maxUses: int = 0


class TrainerIncubators:

    def __init__(self):
        self._incubators = {}
        self.hatching = False
        self.waiting = []

    def addIncubator(self, incubator: EggIncubator):
        """Adds an existing Incubator to data."""
        assert incubator.incubatorId not in self._incubators, f"Incubator ID {incubator.incubatorId} already exists."
        self._incubators[incubator.incubatorId] = incubator

    def isIncubatorAvailable(self):
        for incubator in self._incubators.values():
            if incubator.egg is None:
                return True

        return False

    def getIncubator(self, incubatorId):
        return self._incubators[incubatorId]

    def deleteIncubator(self, incubatorId):
        del self._incubators[incubatorId]

    def getAvailableId(self):
        for i in range(5):
            if i not in self._incubators:
                return i

        return

    @property
    def incubators(self):
        return self._incubators

    @property
    def count(self):
        return len(self._incubators)


@dataclass
class PokemonDaycareSpot:
    pokemonId: int
    dexId: int
    addedTime: float
    stopTime: float
    eggTime: float
    accruingDebt: bool
    pokemon: Optional


class Daycare:
    EGG_TIME = 10
    slots: List[PokemonDaycareSpot]

    def __init__(self):
        self.slots = []

    def clear(self):
        self.slots.clear()

    def hasPokemon(self, pokemon) -> bool:
        for daycareSpot in self.slots:
            if daycareSpot.pokemonId == pokemon.id:
                return True

        return False

    def getPokemon(self, pokemonId: int) -> Optional[PokemonDaycareSpot]:
        for daycareSpot in self.slots:
            if daycareSpot.pokemonId == pokemonId:
                return daycareSpot

        return

    def addPokemon(self, pokemonId, dexId, startTime, eggTime, pokemonData):
        self.slots.append(PokemonDaycareSpot(pokemonId, dexId, startTime, 0, eggTime, True, pokemonData))

    def deletePokemon(self, spot, pokemon):
        return

    def addSpot(self, pokemon, slot):
        return

    def eggPossible(self):
        """Returns if an egg is possible"""
        if len(self.slots) < 2:
            return False
        else:
            ts = time.time()
            for slot in self.slots:
                if ts - slot.eggTime < self.EGG_TIME:
                    return False

            if self.slots[0].pokemon.gender == self.slots[1].pokemon.gender:
                return False
            return True


class PokemonDropper:

    def __init__(self):
        return
