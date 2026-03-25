# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: shared\container\timing.py
"""
Created on Dec 25, 2011

@author: Chuck
"""
import time
JUMP_COOLDOWN = 1
SPAWN_COOLDOWN = 3
RECALL_COOLDOWN = 30
RELEASE_COOLDOWN = 30
GLOBAL_SKILL_COOLDOWN = 0.5
AFTER_SKILL_STUN = 0.5
POISON_TIME = 2
CHAT_COOLDOWN = 1
ITEM_COOLDOWN = 0.5

class CharTickCheck:
    __doc__ = " Manages the time and interval ticks for one session/player. "

    def __init__(self):
        self.skill = 0
        self.jump = 0
        self.poison = 0

    def canJump(self):
        return time.time() - self.jump > JUMP_COOLDOWN

    def canUseSkill(self):
        return time.time() - self.skill > GLOBAL_SKILL_COOLDOWN

    def canTakePoisonDamage(self):
        return time.time() - self.poison > POISON_TIME

    def setJump(self):
        self.jump = time.time()

    def setSkill(self):
        self.skill = time.time()

    def setPoison(self):
        self.poison = time.time()


class GlobalTickCheck:
    __doc__ = " Manages the time and interval ticks for one session/player. "

    def __init__(self):
        self.item = 0
        self.recall = 0
        self.release = 0
        self.spawn = 0
        self.skill = 0
        self.chat = 0
        super().__init__()

    def canChat(self):
        return time.time() - self.chat > CHAT_COOLDOWN

    def canSpawn(self):
        return time.time() - self.spawn > SPAWN_COOLDOWN

    def canUseItem(self):
        return time.time() - self.item > ITEM_COOLDOWN

    def canRelease(self):
        return time.time() - self.release > RELEASE_COOLDOWN

    def canRecall(self):
        return time.time() - self.recall > RECALL_COOLDOWN

    def canUseSkill(self):
        return time.time() - self.skill > GLOBAL_SKILL_COOLDOWN

    def setChat(self):
        self.chat = time.time()

    def setSpawn(self):
        self.spawn = time.time()

    def setRelease(self):
        self.release = time.time()

    def setItem(self):
        self.item = time.time()

    def setRecall(self):
        self.recall = time.time()


class ClientTickCheck(GlobalTickCheck, CharTickCheck):

    def __init__(self):
        super().__init__()
        self.moveCheck = 0
