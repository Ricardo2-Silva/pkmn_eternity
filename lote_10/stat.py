# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: shared\container\stat.py
"""
Created on 2 oct. 2011

@author: Kami
"""
from typing import List, Any
from shared.container.constants import StatType
import time
from shared.service.utils import clamp

class SkillStatModifierData:
    __doc__ = "To be used to load de/buff data."

    def __init__(self, statType, chance, duration, value, modifier, stacks, target):
        self.statType = statType
        self.chance = chance
        self.duration = duration
        self.value = value
        self.modifier = modifier
        self.stacks = stacks
        self.target = target


class EnergyData:
    lastModified = time.time()
    tempRate = 0
    tempRateTime = 0
    tempRateDuration = 0
    permRate = 10


class StatModifierType:
    PERCENTAGE = 0
    OVER_TIME = 1
    STATIC = 2


class Stack:
    __slots__ = [
     "duration", "startTime"]

    def __init__(self, duration, startTime=time.time()):
        self.duration = duration
        self.startTime = startTime

    def getDuration(self):
        return self.duration

    def getTimeLeft(self):
        return time.time() - self.startTime

    def hasTimeExpired(self):
        if time.time() - self.startTime > self.duration:
            return True
        else:
            return False

    def __repr__(self):
        return f"Stack(duration={self.duration}, start={self.startTime}, timeleft={self.getTimeLeft()})"


class StatModifier:
    __doc__ = " De/buffs apply to stats "

    def __init__(self, fromId, fromType, statType, modifierType, value, totalDuration, maxStacks=1, startTime=time.time()):
        self.fromId = fromId
        self.fromType = fromType
        self.statType = statType
        self.type = modifierType
        self.stacks = []
        self.value = value
        self.maxStacks = maxStacks
        self.applyStack(totalDuration, startTime)

    def __repr__(self):
        return f"StatModifier(value={self.value}, stacks={len(self.stacks)}, max_stacks={self.maxStacks})"

    def purgeExpiredStacks(self):
        """ Modifies the stacks so that it only contains active and non-expired stacks. Done before every expiration check.
            Returns True if any actually expired."""
        before = len(self.stacks)
        self.stacks[:] = [stack for stack in self.stacks if stack.hasTimeExpired() is False]
        return before != len(self.stacks)

    def hasTimeExpired(self):
        """ If all stacks are expired, the entire modifier is expired."""
        for stack in self.stacks:
            if not stack.hasTimeExpired():
                return False

        return True

    def applyStack(self, duration, startTime=time.time()):
        if self.atMaxStacks():
            return False
        else:
            self.stacks.append(Stack(duration, startTime))
            return True

    def atMaxStacks(self):
        return self.getStackCount() >= self.maxStacks

    def removeStack(self):
        self.stacks.pop(0)

    def getStacks(self):
        return self.stacks

    def getStackCount(self):
        count = 0
        for stack in self.stacks:
            if not stack.hasTimeExpired():
                count += 1

        return count

    def getLatestStartTime(self):
        startTime = 0
        for stack in self.stacks:
            if stack.startTime > startTime:
                startTime = stack.startTime

        return startTime

    def getMaxStackDuration(self):
        duration = 0
        for stack in self.stacks:
            if stack.duration > duration:
                duration = stack.duration

        return duration

    def getCombinedStackModifier(self):
        if self.type == StatModifierType.OVER_TIME:
            value = self.value * self.getStackCount() / 100.0 / self.getMaxStackDuration()
        elif self.type == StatModifierType.PERCENTAGE:
            value = self.value * self.getStackCount() / 100.0
        else:
            value = self.getStackCount() * self.value
        return value


class Stat:
    __doc__ = "Base value for all Stats. You can apply things to this stat as well as the current and permanent values."
    debuffs: List[StatModifier]
    buffs: List[StatModifier]

    def __init__(self, statType, defaultValue=0):
        self.statType = statType
        self.current = defaultValue
        self.permanent = defaultValue
        self.debuffs = []
        self.buffs = []

    @property
    def values(self):
        return (self.current, self.permanent)

    def set(self, val1, val2=None):
        """ Here we can set the values. If both, set individually, if one, set both as the same """
        self.current = val1
        self.permanent = val1 if val2 is None else val2

    def getModifiedCurrent(self):
        multipliers, static = self._getModifiedValues()
        return max(0, int((self.current + static) * multipliers))

    def _getModifiedValues(self):
        """Returns the values of all of the stacks for buffs and debuffs.
        Separates into multipliers and static additions.
        """
        multipliers = 0
        static = 0
        if self.buffs or self.debuffs:
            for buff in self.buffs + self.debuffs:
                if buff.type == StatModifierType.STATIC:
                    static += buff.getCombinedStackModifier()
                else:
                    multipliers += buff.getCombinedStackModifier()

        return (
         1 + multipliers, static)

    def getMaxDebuffs(self):
        """ Return the values of all of the stacks """
        if self.debuffs:
            return max([db.getCombinedStackModifier() for db in self.debuffs])
        else:
            return 1

    def getMaxBuffs(self):
        """ These should be modifiers. AKA percent based """
        if self.buffs:
            return max([db.getCombinedStackModifier() for db in self.buffs])
        else:
            return 1

    def clearBuffs(self):
        del self.buffs[:]

    def clearDebuffs(self):
        del self.debuffs[:]

    def buff(self, fromId, fromType, modifierType, value, duration, maxStacks=1, startTime=time.time()):
        for buff in self.buffs:
            if buff.type == modifierType:
                if buff.value == value:
                    if buff.maxStacks == maxStacks:
                        if buff.applyStack(duration, startTime):
                            return buff
                        else:
                            return False

        buff = StatModifier(fromId, fromType, self.statType, modifierType, value, duration, maxStacks, startTime)
        self.buffs.append(buff)
        return buff

    def debuff(self, fromId, fromType, modifierType, value, duration, maxStacks=1, startTime=time.time()):
        for debuff in self.debuffs:
            if debuff.value == value:
                if debuff.maxStacks == maxStacks:
                    if debuff.applyStack(duration, startTime):
                        return debuff
                    else:
                        return False

        debuff = StatModifier(fromId, fromType, self.statType, modifierType, value, duration, maxStacks, startTime)
        self.debuffs.append(debuff)
        return debuff


class StatData:

    def __init__(self):
        self.__dict__ = {(StatType.toString[StatType.HP]): (Stat(StatType.HP)), 
         (StatType.toString[StatType.ATK]): (Stat(StatType.ATK)), 
         (StatType.toString[StatType.SPATK]): (Stat(StatType.SPATK)), 
         (StatType.toString[StatType.DEF]): (Stat(StatType.DEF)), 
         (StatType.toString[StatType.SPDEF]): (Stat(StatType.SPDEF)), 
         (StatType.toString[StatType.SPEED]): (Stat(StatType.SPEED)), 
         (StatType.toString[StatType.ENERGY]): (Stat(StatType.ENERGY)), 
         (StatType.toString[StatType.EXP]): (Stat(StatType.EXP)), 
         (StatType.toString[StatType.CRIT_CHANCE]): (Stat(StatType.CRIT_CHANCE, 5)), 
         (StatType.toString[StatType.EVASION]): (Stat(StatType.EVASION, 100)), 
         (StatType.toString[StatType.ACCURACY]): (Stat(StatType.ACCURACY, 100))}
        self.energyData = EnergyData()

    def hasModifiers(self) -> bool:
        for statType in StatType.ALL_STATS:
            stat = self.__dict__[StatType.toString[statType]]
            if stat.buffs or stat.debuffs:
                return True

        return False

    def getBuffs(self) -> List[StatType]:
        return [self.__dict__[StatType.toString[stat]].buffs for stat in StatType.ALL_STATS]

    def getDebuffs(self) -> List[StatType]:
        return [self.__dict__[StatType.toString[stat]].debuffs for stat in StatType.ALL_STATS]

    def removeDebuff(self, debuff: StatModifier):
        self.__dict__[StatType.toString[debuff.statType]].debuffs.remove(debuff)

    def removeBuff(self, buff: StatModifier):
        self.__dict__[StatType.toString[buff.statType]].buffs.remove(buff)

    def buff(self, fromId, fromType, stat, modifierType, value, duration, maxStacks=1, startTime=time.time()):
        return self.__dict__[StatType.toString[stat]].buff(fromId, fromType, modifierType, value, duration, maxStacks, startTime)

    def debuff(self, fromId, fromType, stat, modifierType, value, duration, maxStacks=1, startTime=time.time()):
        return self.__dict__[StatType.toString[stat]].debuff(fromId, fromType, modifierType, value, duration, maxStacks, startTime)

    def clearDebuffs(self):
        for stat in StatType.ALL_STATS:
            self.__dict__[StatType.toString[stat]].clearDebuffs()

    def clearBuffs(self):
        for stat in StatType.ALL_STATS:
            self.__dict__[StatType.toString[stat]].clearBuffs()

    def clearAllModifiers(self, stat):
        self.__dict__[StatType.toString[stat]].clearBuffs()
        self.__dict__[StatType.toString[stat]].clearDebuffs()

    def clearEveryModifierStat(self):
        """ Completely wipe all modifiers to every stat """
        for stat in StatType.ALL_STATS:
            self.clearAllModifiers(stat)

    def get(self, stat):
        return self.__dict__[StatType.toString[stat]]

    def isAlive(self):
        return self.hp.current > 0

    def isFainted(self):
        return self.hp.current == 0

    def fullHeal(self):
        self.hp.set(self.hp.permanent)
        self.clearEveryModifierStat()

    def copy(self):
        s = StatData()
        for stat in StatType.ALL_STATS:
            (s.get(stat).set)(*self.get(stat).values)

        return s

    def canUseEnergy(self, amount):
        self.calculateEnergyTick()
        if amount <= self.energy.current:
            return True
        else:
            return False

    def useEnergy(self, amount):
        """ Calculate how much energy we have gained. If we have enough use it.
            Returns true if it succeeds, returns false if failed.
        """
        self.calculateEnergyTick()
        if amount <= self.energy.current:
            self.energy.current -= amount
            self.energyData.lastModified = time.time()
            return True
        else:
            return False

    def getEnergyRate(self):
        if self.energyData.tempRate > 0:
            return self.energyData.tempRate
        else:
            return self.energyData.permRate

    def calculateEnergyTick(self):
        minEnergy, maxEnergy = self.energy.values
        if minEnergy == maxEnergy:
            return False
        else:
            seconds = time.time() - self.energyData.lastModified
            energyGained = seconds * self.getEnergyRate()
            if minEnergy + energyGained > maxEnergy:
                self.energy.current = maxEnergy
            else:
                self.energy.current += round(energyGained)
            self.energyData.lastModified = time.time()
            return True


class Ivs:

    def __init__(self):
        self.__dict__ = {(StatType.toString[StatType.HP]): 1, 
         (StatType.toString[StatType.ATK]): 1, 
         (StatType.toString[StatType.SPATK]): 1, 
         (StatType.toString[StatType.DEF]): 1, 
         (StatType.toString[StatType.SPDEF]): 1, 
         (StatType.toString[StatType.SPEED]): 1}

    def __iter__(self):
        yield self.hp
        yield self.atk
        yield self.spatk
        yield self.defense
        yield self.spdef
        yield self.speed

    def get(self, stat):
        return self.__dict__[StatType.toString[stat]]

    def set(self, stat, value):
        self.__dict__[StatType.toString[stat]] = value

    def copy(self):
        s = Ivs()
        for stat in StatType.ALL_STATS:
            (s.set)(stat, *self.get(stat))

        return s
