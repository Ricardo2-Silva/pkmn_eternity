# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: shared\container\status.py
"""
Created on Oct 19, 2015

@author: Admin
"""
import time
from typing import List
from shared.container.constants import StatusEffect

class StatusEffectData:
    __doc__ = "Applies status effects to character.\n    Value is only applied to certain effects\n    EX: Poison value = Poison damage"

    def __init__(self, status, duration, value):
        self.status = status
        self.duration = duration
        self.value = value
        self.startTime = time.time()
        self.expired = False

    def getTimeLeft(self):
        return time.time() - self.startTime

    def hasTimeExpired(self):
        if self.expired is True:
            return True
        else:
            if time.time() - self.startTime > self.duration:
                return True
            return False

    def extendTime(self, seconds):
        self.startTime += seconds

    def __repr__(self):
        return f"StatusEffectData(status={self.status}, duration={self.duration}, expired={self.expired})"


class CharStatusData:

    def __init__(self):
        self.status = {}

    def hasStatus(self, status):
        return status in self.status

    def isAfflicted(self):
        """ Checks if we are afflicted by any status effects """
        return bool(self.status)

    def inflictStatus(self, statusData):
        self.status[statusData.status] = statusData

    def cureStatus(self, status):
        del self.status[status]

    def getStatusEffects(self) -> List[StatusEffectData]:
        return list(self.status.values())

    def getStatus(self, status):
        try:
            return self.status[status]
        except KeyError:
            return

    def isPoisoned(self):
        return self.getStatus(StatusEffect.POISON)

    def isSleeping(self):
        return self.getStatus(StatusEffect.SLEEP)

    def isFrozen(self):
        return self.getStatus(StatusEffect.FREEZE)

    def isRooted(self):
        return self.getStatus(StatusEffect.ROOT)
