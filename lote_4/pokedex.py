# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\data\gui\pokedex.py
"""
Created on Dec 19, 2011

@author: Ragnarok
"""

class PokedexData:
    UNSEEN = 0
    SEEN = 1
    CAPTURED = 2
    CAPTURED_BUT_RELEASED = 3

    def __init__(self):
        self.enabled = True
        self.dex = []
        self.seen = 0
        self.caught = 0

    def appendPokemon(self, value):
        self.dex.append(value)

    def setPokemon(self, dexId, value):
        self.dex[dexId] = value
        if value == self.SEEN:
            self.calcSeen()
        else:
            self.calcCaught()

    def setPokedex(self, dexList):
        self.dex = dexList
        self.calcSeen()
        self.calcCaught()

    def getRevealed(self):
        return [idx for idx, dexId in enumerate(self.dex) if dexId != 0]

    def getPokemon(self, dexId):
        return self.dex[dexId]

    def getPokedex(self):
        return self.dex

    def hasSeen(self, dexId):
        return self.dex[dexId] == self.SEEN

    def hasCaught(self, dexId):
        return self.dex[dexId] in (self.CAPTURED, self.CAPTURED_BUT_RELEASED)

    def canScan(self, dexId):
        return self.dex[dexId] == 0

    def calcSeen(self):
        self.seen = self.dex.count(self.SEEN)

    def calcCaught(self):
        self.caught = self.dex.count(self.CAPTURED)
