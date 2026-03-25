# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\world\action\status.py
"""
Created on Sep 10, 2015

@author: Admin
Module is for status effect handling
"""
from client.control.events import eventManager
from shared.container.constants import StatusEffect, IdRange
from shared.container.status import StatusEffectData
import pyglet
from client.control.service.session import sessionService
from client.data.container.char import charContainer
from client.control.events.world import worldInputManager

class StatusTimeHandler:

    def __init__(self):
        self.chars = {(IdRange.PC_POKEMON): {}, 
         (IdRange.PC_TRAINER): {}, 
         (IdRange.NPC_WILD_PKMN): {}, 
         (IdRange.NPC_BATTLE_PKMN): {}, 
         (IdRange.NPC_CHARACTER): {}}

    def reset(self):
        self.__init__()

    def exists(self, char):
        if char.id in self.chars[char.idRange]:
            return True
        else:
            return False

    def add(self, char):
        self.chars[char.idRange][char.id] = char

    def delete(self, char):
        del self.chars[char.idRange][char.id]

    def update(self, dt):
        for idRange in self.chars:
            for char in list(self.chars[idRange].values()):
                charObj = charContainer.getCharByIdIfAny(char.id, char.idRange)
                for statusData in char.status.getStatusEffects():
                    if statusData.hasTimeExpired() or char.isFainted():
                        char.status.cureStatus(statusData.status)
                        if charObj:
                            charObj.cureStatusEffect(statusData.status)
                    else:
                        if not sessionService.battle:
                            if not statusData.status != StatusEffect.POISON:
                                char.status.cureStatus(statusData.status)

                if not char.status.isAfflicted():
                    self.delete(char)


statusTimeHandler = StatusTimeHandler()

class StatusEffectService:

    def __init__(self):
        return

    def cureAll(self, charData):
        for statusData in charData.status.getStatusEffects():
            self.cureStatus(charData, statusData.status)

        if statusTimeHandler.exists(charData):
            statusTimeHandler.delete(charData)

    def cureStatus(self, char, status):
        if char.status.hasStatus(status):
            char.status.cureStatus(status)
            if not char.status.isAfflicted():
                statusTimeHandler.delete(char)
            charObj = charContainer.getCharByIdIfAny(char.id, char.idRange)
            if charObj:
                charObj.cureStatusEffect(status)
                eventManager.notify("onCharPlayEffect", charObj, "Cure", status)
            if status in StatusEffect.MOVEMENT_RESTRICT:
                worldInputManager.attemptAutoMove()

    def inflictStatus(self, char, status, duration, value):
        data = char.data
        if not self.hasStatus(data, status):
            statusData = StatusEffectData(status, duration, value)
            data.status.inflictStatus(statusData)
            if not statusTimeHandler.exists(data):
                statusTimeHandler.add(data)
            self.applyCharEffects(char, status, duration)

    def applyCharEffects(self, char, status, duration):
        char.showStatusEffect(status, duration)
        if status == StatusEffect.SLEEP or status == StatusEffect.ROOT or status == StatusEffect.FREEZE:
            if char.isWalking():
                char.stopWalking()
                char.clearAllOrders()
        elif status == StatusEffect.STUN:
            char.setStunDuration(duration)

    def hasStatus(self, char, status):
        return char.status.getStatus(status)

    def determineDamage(self, char, status):
        return

    def isSleeping(self, char):
        return char.status.hasStatus(StatusEffect.SLEEP)

    def isPoisoned(self, char):
        return char.status.hasStatus(StatusEffect.POISON)

    def getPoisonDamage(self, char):
        return char.status.getStatus(StatusEffect.POISON).value

    def isBurning(self, char):
        return char.status.hasStatus(StatusEffect.BURN)

    def isConfused(self, char):
        return char.status.getStatus(StatusEffect.CONFUSED)

    def isFrozen(self, char):
        return char.status.hasStatus(StatusEffect.FREEZE)

    def isParalyzed(self, char):
        return char.status.hasStatus(StatusEffect.PARALYSIS)

    def isSilenced(self, char):
        return char.status.hasStatus(StatusEffect.SILENCE)

    def isRooted(self, char):
        return char.status.hasStatus(StatusEffect.ROOT)


statusEffectController = StatusEffectService()
