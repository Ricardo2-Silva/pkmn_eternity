# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\world\action\buffs.py
"""
Created on May 17, 2017

@author: Admin
"""
import sys
from client.control.world.effects import effectManager
from client.data.container.char import charContainer
from client.interface.pokemon.info import infoBar
from shared.container.constants import StatType
from shared.container.chars import Chars

class BuffTimeHandler:

    def __init__(self):
        self.chars = Chars()

    def reset(self):
        self.chars = Chars()

    def _exists(self, char):
        return self.chars.charExists(char)

    def _add(self, char):
        self.chars.addChar(char)

    def _delete(self, char):
        self.chars.delChar(char)

    def applyBuff(self, charId, charType, fromId, fromType, statType, modifierType, statValue, duration, maxStacks, startTime):
        charData = charContainer.getDataByIdIfAny(charId, charType)
        if charData:
            modifier = charData.stats.buff(fromId, fromType, statType, modifierType, statValue, duration, maxStacks, startTime)
            if modifier:
                infoBar.onBuffUpdate(charData, modifier)
                if not self._exists(charData):
                    self._add(charData)
                self._updateMod(charData, statType)
                char = charContainer.getCharByIdIfAny(charId, charType)
                if char:
                    effectManager.buff(char, statType)
                else:
                    sys.stderr.write("WARNING: Buff could not be applied, reached maximum stacks allowable. {0}, {1}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}\n".format(charId, charType, fromId, fromType, statType, modifierType, statValue, duration, maxStacks, startTime))
        else:
            sys.stderr.write("WARNING: Buff could not be applied, no data for character found. Sync issue. {0}, {1}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}\n".format(charId, charType, fromId, fromType, statType, modifierType, statValue, duration, maxStacks, startTime))

    def applyDebuff(self, charId, charType, fromId, fromType, statType, modifierType, statValue, duration, maxStacks, startTime):
        charData = charContainer.getDataByIdIfAny(charId, charType)
        if charData:
            modifier = charData.stats.debuff(fromId, fromType, statType, modifierType, statValue, duration, maxStacks, startTime)
            if modifier:
                infoBar.onDebuffUpdate(charData, modifier)
                if not self._exists(charData):
                    self._add(charData)
                self._updateMod(charData, statType)
                char = charContainer.getCharByIdIfAny(charId, charType)
                if char:
                    effectManager.debuff(char, statType)
                else:
                    sys.stderr.write("WARNING: Debuff could not be applied, reached maximum stacks allowable. {0}, {1}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}\n".format(charId, charType, fromId, fromType, statType, modifierType, statValue, duration, maxStacks, startTime))
        else:
            sys.stderr.write("WARNING: Debuff could not be applied, no data for character found. Sync issue. {0}, {1}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}\n".format(charId, charType, fromId, fromType, statType, modifierType, statValue, duration, maxStacks, startTime))

    def _updateAllMods(self, charData):
        """These are secondary effects that mods can affect. EX: Speed to movement speed. May change."""
        charData.setWalkingSpeed(charData.stats.speed.permanent, charData.stats.speed.getModifiedCurrent())

    def _updateMod(self, charData, modifier):
        if modifier == StatType.SPEED:
            charData.setWalkingSpeed(charData.stats.speed.permanent, charData.stats.speed.getModifiedCurrent())

    def update(self, dt):
        for char in self.chars.getAllChars():
            update = False
            for statList in char.stats.getDebuffs():
                for statModifier in statList:
                    if statModifier.purgeExpiredStacks():
                        update = True
                    if statModifier.hasTimeExpired():
                        char.stats.removeDebuff(statModifier)
                        update = True

            for statList in char.stats.getBuffs():
                for statModifier in statList:
                    if statModifier.purgeExpiredStacks():
                        update = True
                    if statModifier.hasTimeExpired():
                        char.stats.removeBuff(statModifier)
                        update = True

            if update:
                self._updateAllMods(char)
            if not char.stats.hasModifiers():
                self._delete(char)


buffTimeHandler = BuffTimeHandler()
