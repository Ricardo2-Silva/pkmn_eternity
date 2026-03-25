# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: shared\container\exp.py
"""
Created on 26 sept. 2011

@author: Chuck (Cleaned by Kami)

"""
import math

class ExpMethods:

    def __init__(self, pokedex):
        self.pokedexDB = pokedex
        self.nameToExpFunc = {'Fluctuating':self.fluctuatingExp, 
         'Medium':self.mediumExp, 
         'Fast':self.fastExp, 
         'Slow':self.slowExp, 
         'Erratic':self.erraticExp, 
         'Parabolic':self.parabolicExp}

    def calcExpByLevel(self, dexId, level):
        if level == 1:
            return 0
        else:
            pokemon = self.pokedexDB.getPokemon(dexId)
            exp = self.nameToExpFunc[pokemon.growthRate](level)
            return int(exp)

    def fluctuatingExp(self, level):
        if level <= 15:
            return math.floor(level ** 3 * (((level + 1) / 3 + 24) / 50))
        else:
            if 15 <= level <= 36:
                return math.floor(level ** 3 * ((level + 14) / 50))
            if 36 <= level <= 100:
                return math.floor(level ** 3 * ((level / 2 + 32) / 50))
            return math.floor(level ** 3 * ((level / 2 + 32) / 50))

    def mediumExp(self, level):
        return math.floor(level ** 3)

    def slowExp(self, level):
        return math.floor(5 * level ** 3 / 4)

    def fastExp(self, level):
        return math.floor(4 * level ** 3 / 5)

    def erraticExp(self, level):
        if level <= 50:
            return math.floor(level ** 3 * (100 - level) / 50)
        else:
            if 50 <= level <= 68:
                return math.floor(level ** 3 * (150 - level) / 100)
            else:
                if 68 <= level <= 98:
                    return math.floor(level ** 3 * ((1911 - 10 * level) / 3) / 500)
                if 98 <= level <= 100:
                    return math.floor(level ** 3 * (160 - level) / 100)
            return math.floor(level ** 3 * (160 - level) / 100)

    def parabolicExp(self, level):
        return math.floor(1.2 * level ** 3 - 15 * level ** 2 + 100 * level - 140)
