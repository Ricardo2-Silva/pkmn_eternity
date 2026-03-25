# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\data\world\battle.py
"""
Created on 17 dec. 2011

@author: Kami
"""
from shared.container.constants import IdRange
import sys

class BattleAutoselectFlag:
    NEVER = 0
    ON_BATTLE_START = 1
    ON_BATTLE_END = 2
    BOTH = 3


class BattleData:
    __doc__ = " Store battle information client side. Stores only the chars different than ours."

    def __init__(self):
        self.active = False
        self.battleType = None
        self.chars = []

    def create(self, battleType):
        self.active = True
        self.battleType = battleType

    def start(self):
        self.active = True

    def end(self):
        self.active = False
        self.empty()

    def isActive(self):
        return self.active

    def addChar(self, char):
        if char in self.chars:
            sys.stderr.write("WARNING: Tried to add char into battle when he was already in it. {0}, {1}\n".format(char, [loopChar.data.name for loopChar in self.chars]))
            return
        self.chars.append(char)

    def delChar(self, char):
        print("DEL CHAR")
        try:
            self.chars.remove(char)
        except ValueError:
            print(f"Warning: Tried to remove {char} from battle, but is not in battle. Current chars: {self.chars}")

    def isInBattle(self, char):
        return char in self.chars

    def getPokemon(self):
        return [char for char in self.chars if char.data.idRange in IdRange.POKEMON]

    def getChars(self):
        return self.chars

    def empty(self):
        self.chars.clear()
