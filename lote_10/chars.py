# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: shared\container\chars.py
"""
Created on Oct 19, 2015

@author: Admin
"""
from shared.container.constants import CharCategory, ControlType, IdRange

class Chars:
    __doc__ = " Contains map's chars and store them the most efficient way as possible. "

    def __init__(self):
        self.chars = {(IdRange.PC_TRAINER): {}, 
         (IdRange.PC_POKEMON): {}, 
         (IdRange.NPC_CHARACTER): {}, 
         (IdRange.NPC_BATTLE_PKMN): {}, 
         (IdRange.NPC_OBJECT): {}, 
         (IdRange.NPC_ITEM): {}, 
         (IdRange.NPC_WILD_PKMN): {}, 
         (IdRange.NPC_BERRY): {}}
        self.all = []

    def addChar(self, char):
        self.chars[char.idRange][char.id] = char
        if char not in self.all:
            self.all.append(char)
        else:
            raise Exception(f"<list.appendOnce on List chars.all> Couldn't add the value {char} : because it exists already.")

    def delChar(self, char):
        del self.chars[char.idRange][char.id]
        self.all.remove(char)

    def getPlayersFromPcTrainers(self, exclude=None):
        playersOfPcTrainers = set([x.getPlayer() for x in self.getPcTrainers()])
        players = playersOfPcTrainers
        if exclude:
            players = players - set(exclude)
        return players

    def getPlayerChars(self):
        return self.getPcPokemons() + self.getPcTrainers()

    def getAllPokemon(self):
        return self.getPcPokemons() + self.getWildPokemons() + self.getBattlerPokemons()

    def getPcTrainers(self):
        return list(self.chars[IdRange.PC_TRAINER].values())

    def getPcPokemons(self):
        return list(self.chars[IdRange.PC_POKEMON].values())

    def getNpcs(self):
        return list(self.chars[IdRange.NPC_CHARACTER].values())

    def getWildPokemons(self):
        return list(self.chars[IdRange.NPC_WILD_PKMN].values())

    def getBattlerPokemons(self):
        return list(self.chars[IdRange.NPC_BATTLE_PKMN].values())

    def getAllNpcTypes(self):
        return list(self.chars[IdRange.NPC_CHARACTER].values()) + list(self.chars[IdRange.NPC_WILD_PKMN].values()) + list([IdRange.NPC_BATTLE_PKMN].values())

    def getItems(self):
        return list(self.chars[IdRange.NPC_ITEM].values())

    def getObjects(self):
        return list(self.chars[IdRange.NPC_OBJECT].values()) + list(self.chars[IdRange.NPC_BERRY].values())

    def exists(self, charId, idRange):
        return charId in self.chars[idRange]

    def charExists(self, char):
        return char.id in self.chars[char.idRange]

    def getAllChars(self):
        return self.all
