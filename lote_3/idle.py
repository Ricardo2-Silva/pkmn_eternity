# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\world\action\idle.py
"""
Created on 21 juil. 2011

@author: Kami
"""
import random, time

class IdleCharManager:
    __doc__ = " Every seconds, make the idle char do an action, sometimes. Anything...."

    def __init__(self):
        self.idleChars = {}
        self.duration = 1
        self._last_time = time.time()

    def isIdle(self, char):
        return char in self.idleChars

    def charEnteredBattle(self, char):
        if char in self.idleChars:
            self.delete(char)

    def reset(self):
        self.idleChars.clear()
        self._last_time = time.time()

    def charExitBattle(self, char):
        if char not in self.idleChars:
            self.add(char)

    def update(self, dt):
        if time.time() - self._last_time > self.duration:
            for char, timeStamp in self.idleChars.items():
                isIdle = random.randint(0, 100)
                if isIdle <= 40:
                    idleTime = time.time() - timeStamp
                    if idleTime > random.randint(8, 15):
                        char.isFainted() or char.idleReaction()
                        self.idleChars[char] = time.time()

            self._last_time = time.time()

    def add(self, idleChar):
        if idleChar in self.idleChars:
            raise Exception("Warning: Idle Char already exists")
        self.idleChars[idleChar] = time.time()

    def delete(self, idleChar):
        del self.idleChars[idleChar]


idleCharManager = IdleCharManager()
