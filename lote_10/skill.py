# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: shared\container\skill.py
"""
Created on 9 janv. 2012

@author: Kami
"""
from typing import List, Dict, Any, ValuesView
from twisted.internet.error import AlreadyCalled
import time, math
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from shared.container.constants import TargetType, SkillCategory, Element
from shared.container.stat import SkillStatModifierData
MELEE_RANGE = 15

class SkillInfo:
    buffs: List[SkillStatModifierData]
    debuffs: List[SkillStatModifierData]

    def __init__(self):
        self.id = 0
        self.name = "Unknown"
        self.target = TargetType.NONE
        self.category = SkillCategory.PHYSICAL
        self.range = 0
        self.energy = 0
        self.baseDamage = 0
        self.element = Element.NORMAL
        self.accuracy = 0
        self.effect = None
        self.effectChance = 0
        self.effect_duration = 0
        self.cooldown = 0
        self.duration = 0
        self.maxRange = 0
        self.friendlyFire = False
        self.graphicId = 0
        self.flags = 0
        self.contest = ""
        self.description = ""
        self.struct = ""
        self.castTime = 0
        self.interruptable = False
        self.channeled = False
        self.max_instances = 0
        self.allow_skills = False
        self.startup_delay = 0.3
        self.allow_movement = False
        self.debuffs = []
        self.buffs = []

    def isMelee(self):
        return self.maxRange < MELEE_RANGE and self.target

    def isRanged(self):
        return self.maxRange > MELEE_RANGE and self.target

    def isNoTarget(self):
        return self.target == 0

    def isPlayerTarget(self):
        return self.target in (TargetType.HUMAN, TargetType.OBJECT, TargetType.POKEMON)

    def isSelf(self):
        return self.target == TargetType.SELF

    def isPhysical(self) -> bool:
        return bool(self.category == SkillCategory.PHYSICAL)

    def isSpecial(self) -> bool:
        return bool(self.category == SkillCategory.SPECIAL)

    def isStatus(self) -> bool:
        return bool(self.category == SkillCategory.STATUS)

    def __repr__(self):
        return f"SkillInfo(id={self.id}, name={self.name}, duration={self.duration}, cooldown={self.cooldown})"


class PokemonSkill:
    __slots__ = [
     "cooldownTick", "skillInfo", "isSaved", "awaitingAck"]

    def __init__(self, skillInfo: SkillInfo):
        self.awaitingAck = False
        self.cooldownTick = 0
        self.skillInfo = skillInfo
        self.isSaved = 0

    def canUse(self) -> bool:
        return time.time() - self.cooldownTick > self.skillInfo.cooldown

    def setUsed(self, timestamp):
        self.cooldownTick = timestamp

    def __repr__(self):
        return f"PokemonSkill(id={self.skillInfo.id}, name={self.skillInfo.name}, saved={self.isSaved})"


class Skills:
    __doc__ = " The container that store the skill of a Pokemon. "
    active: Dict[(int, PokemonSkill)]
    pending: Dict[(int, PokemonSkill)]
    __slots__ = ["active", "pending"]

    def __init__(self):
        self.active = {}
        self.pending = {}

    def addSkill(self, skillData: PokemonSkill):
        if skillData.isSaved:
            self.pending[skillData.skillInfo.id] = skillData
        else:
            self.active[skillData.skillInfo.id] = skillData

    def getActiveSkills(self):
        return self.active.values()

    def hasActiveSkill(self, skillId):
        return skillId in self.active

    def getActiveSkill(self, skillId) -> PokemonSkill:
        return self.active[skillId]

    def delSkill(self, skillId):
        del self.active[skillId]

    def getPendingSkills(self) -> ValuesView[PokemonSkill]:
        return self.pending.values()

    def hasPendingSkill(self, skillId) -> bool:
        return skillId in self.pending

    def delPendingSkill(self, skillId):
        del self.pending[skillId]

    def getPaddedIds(self):
        return (list(self.active.keys()) + [0] * 6)[:6]

    def hasSkill(self, skillId):
        return skillId in self.active or skillId in self.pending

    def getAllSkills(self):
        """ For saving/sending all of the skills """
        return list(self.active.values()) + list(self.pending.values())


def getDistanceBetweenTwoPoints(point1, point2):
    x0, y0 = point1
    x1, y1 = point2
    return math.hypot(x1 - x0, y1 - y0)


class SkillEventSource:
    __doc__ = " Base class for controllable skill events. Damage, buffs, debuffs."

    def __init__(self, skillInstance, x, y, z, duration):
        """

        :type skillInstance: SkillUseInstance
        """
        self.skillInstance = skillInstance
        self._totalDistance = 0
        self._x = x
        self._y = y
        self._z = z
        self.initialPosition = (x, y, z)
        self.duration = duration
        self._startTime = None
        self.active = False
        self.damaged = []
        self.skillInstance.events.append(self)

    def start(self):
        self._startTime = time.time()
        self.active = True

    def stop(self, expiration):
        """ Destroy the damage source.
        @type expiration: bool
            If True then expired gracefully, automatically remove it from skill instance.
             if False, terminated prematurely, and other means will remove the event.
        """
        self.active = False
        (self.skillInstance.onSourceStop)(self, expiration, *self.position)
        if expiration is True:
            self.skillInstance.eventFinished(self)

    @property
    def position(self):
        return (self._x, self._y, self._z)


class LinearEventSource(SkillEventSource):
    __doc__ = " This is a linear damage source, it will move from initial position towards direction for a specific distance.\n        Usually a projectile of some sort.\n    "

    def __init__(self, skillInstance, x, y, z, direction, speed, distance, loopStep=0.016666666666666666):
        duration = distance / speed
        super().__init__(skillInstance, x, y, z, duration)
        self.direction = direction
        self.angle = math.radians(direction)
        self.speed = speed
        self._loop = False
        self._loopStep = loopStep
        self._elapsedTime = 0
        self._oldTime = 0

    def onMoveEvent(self, x, y, z):
        """ Event called every tick of loopStep if it's moving."""
        return

    def stop(self, expiration=True):
        if self._loop:
            self._loop.stop()
            self._loop = False
        super().stop(expiration)

    def start(self):
        if self._loop:
            raise Exception("There is already a loop for this.", self.skillInstance)
        self.skillInstance.onSourceActivate(self, self._x, self._y, self._z, 1)
        self._loop = LoopingCall(self.move)
        super().start()
        self._oldTime = self._startTime
        self._loop.start(self._loopStep)

    def move(self):
        dt = time.time() - self._oldTime
        if self._elapsedTime >= self.duration:
            self.stop(True)
            return
        self._x += math.cos(self.angle) * self.speed * dt
        self._y += math.sin(self.angle) * self.speed * dt
        self.skillInstance.onSourceMove(self, self._x, self._y)
        self._elapsedTime += dt
        self._oldTime = time.time()


class LinearPositionEventSource(SkillEventSource):
    __doc__ = " This is a linear damage source, it will move from initial position towards target position for a specific distance.\n        Usually a projectile of some sort.\n    "

    def __init__(self, skillInstance, x, y, z, target_x, target_y, speed, distance, loopStep=0.016666666666666666):
        duration = distance / speed
        super().__init__(skillInstance, x, y, z, duration)
        self.start_x = x
        self.start_y = y
        self.target_x = target_x
        self.target_y = target_y
        self.speed = speed
        self._loop = False
        self._loopStep = loopStep
        self._elapsedTime = 0
        self._oldTime = 0

    def onMoveEvent(self, x, y, z):
        """ Event called every tick of loopStep if it's moving."""
        return

    @staticmethod
    def lerp(a, b, t):
        return a * (1.0 - t) + b * t

    def stop(self, expiration=True):
        if self._loop:
            self._loop.stop()
            self._loop = False
        super().stop(expiration)

    def start(self):
        if self._loop:
            raise Exception("There is already a loop for this.", self.skillInstance)
        self.skillInstance.onSourceActivate(self, self._x, self._y, self._z, 1)
        self._loop = LoopingCall(self.move)
        super().start()
        self._oldTime = self._startTime
        self._loop.start(self._loopStep)

    def move(self):
        dt = time.time() - self._oldTime
        if self._elapsedTime >= self.duration:
            self.stop(True)
            return
        t = min(1, self._elapsedTime / self.duration)
        self._x = self.lerp(self.start_x, self.target_x, t)
        self._y = self.lerp(self.start_y, self.target_y, t)
        self.skillInstance.onSourceMove(self, self._x, self._y)
        self._elapsedTime += dt
        self._oldTime = time.time()


class LinearConstantEventSource(SkillEventSource):
    __doc__ = " This is a linear damage source, it will move from initial position towards direction for a specific distance.\n        Usually a projectile of some sort.\n    "

    def __init__(self, skillInstance, x, y, z, target_x, target_y, speed, duration, loopStep=0.016666666666666666):
        super().__init__(skillInstance, x, y, z, duration)
        self.start_x = x
        self.start_y = y
        self.target_x = target_x
        self.target_y = target_y
        self.speed = speed
        self._loop = False
        self._loopStep = loopStep
        self._elapsedTime = 0
        self._oldTime = 0

    def onMoveEvent(self, x, y, z):
        """ Event called every tick of loopStep if it's moving."""
        return

    def _calcMoveTowards(self, current, target, distanceDelta):
        distance = getDistanceBetweenTwoPoints((self._x, self._y), (self.target_x, self.target_y))
        if distance <= distanceDelta or distance == 0:
            return target
        else:
            x0, y0 = current
            x1, y1 = target
            diffx = x1 - x0
            diffy = y1 - y0
            return (x0 + diffx / distance * distanceDelta,
             y0 + diffy / distance * distanceDelta)

    def stop(self, expiration=True):
        if self._loop:
            self._loop.stop()
            self._loop = False
        super().stop(expiration)

    def start(self):
        if self._loop:
            raise Exception("There is already a loop for this.", self.skillInstance)
        self.skillInstance.onSourceActivate(self, self._x, self._y, self._z, 1)
        self._loop = LoopingCall(self.move)
        super().start()
        self._oldTime = self._startTime
        self._loop.start(self._loopStep)

    def move(self):
        dt = time.time() - self._oldTime
        if self._elapsedTime >= self.duration:
            self.stop(True)
            return
        self._x, self._y = self._calcMoveTowards((self._x, self._y), (self.target_x, self.target_y), self.speed)
        self.skillInstance.onSourceMove(self, self._x, self._y)
        self._elapsedTime += dt
        self._oldTime = time.time()


class CastEventSource(SkillEventSource):
    __doc__ = "Helper class, this will only call onSourceActivate when duration expires."

    def __init__(self, skillInstance, x, y, z, duration):
        super().__init__(skillInstance, x, y, z, duration)
        self.callback = None

    def stop(self, expiration=True):
        if expiration is True:
            self.skillInstance.onSourceActivate(self, self._x, self._y, self._z, 1)
        if self.callback:
            try:
                self.callback.cancel()
            except AlreadyCalled:
                pass

            self.callback = None
        super().stop(expiration)

    def start(self):
        super().start()
        if self.active:
            self.callback = reactor.callLater(self.duration, self.stop, True)


class StaticEventSource(SkillEventSource):
    __doc__ = " This is a source of damage that cannot move. Activates immediately and destroys itself after duration.\n        Examples: A once hitting attack at a specific spot such as melee or bolt.\n    "

    def __init__(self, skillInstance, x, y, z, duration=0):
        super().__init__(skillInstance, x, y, z, duration)
        self.callback = None

    def stop(self, expiration=True):
        if self.duration:
            if self.callback:
                try:
                    self.callback.cancel()
                except AlreadyCalled:
                    pass

                self.callback = None
        super().stop(expiration)

    def start(self):
        super().start()
        self.skillInstance.onSourceActivate(self, self._x, self._y, self._z, 1)
        if self.active:
            if self.duration:
                self.callback = reactor.callLater(self.duration, self.stop, True)
            else:
                self.stop(True)


class StaticTickEventSource(SkillEventSource):
    __doc__ = " A helper function for calling Static Tick multiple times.\n        count = How many times the onActivate will be called.\n        onActivate will return the current number.\n        # EXAMPLE: duration=1, count=2. Every 1 second, activate. A total of 2 times = 2 seconds.\n    "

    def __init__(self, skillInstance, x, y, z, duration, count=1):
        super().__init__(skillInstance, x, y, z, duration)
        self._current_count = 0
        self.count = count
        self.callback = None

    def start(self):
        super().start()
        self.tick()

    def stop(self, expiration=True):
        if self.callback:
            self.callback.cancel()
            self.callback = None
        super().stop(expiration)

    def tick(self):
        self.callback = None
        if not self.active:
            return
        self._current_count += 1
        self.skillInstance.onSourceActivate(self, self._x, self._y, self._z, self._current_count)
        if self.active:
            if self._current_count < self.count:
                self.callback = reactor.callLater(self.duration, self.tick)
            if self._current_count == self.count:
                self.callback = None
                self.stop(True)


class SkillUseInstance:

    def __init__(self, skillInfo: SkillInfo, char, data, instanceId=None, duration=0):
        """ When a skill is called for the first time. """
        self.instanceId = instanceId
        self.char = char
        self.skillInfo = skillInfo
        self.data = data
        self.loopingTime = 0
        self.startTime = time.time()
        self.duration = skillInfo.duration if not duration else duration
        self.active = False
        self.events = []
        self.process()

    @property
    def name(self):
        return self.__class__.__name__.lower().title()

    def start(self):
        self.startTime = time.time()
        self._save()
        if self.duration:
            self.active = reactor.callLater(self.duration, self.stop, True)
        self.onStart()
        for event in self.events:
            event.start()

    def interrupt(self, damage=False, movement=False):
        if damage:
            return self.onUserDamage()
        if movement:
            return self.onUserMove()

    def getId(self):
        return self.skillInfo.id

    def _save(self):
        """ Store the skill in the char states. """
        self.char.skillStates.save(self)

    def _delete(self):
        """ Store the skill in the char states. """
        self.char.skillStates.delete(self)

    def stop(self, expiration=False):
        if expiration is True:
            self.onExpired()
        else:
            for event in self.events:
                event.stop(False)

            self.onDestroyed()
        if self.active:
            if self.active.active():
                self.active.cancel()
        self._delete()
        self.active = False

    @staticmethod
    def callAgain(skillInfo, char, data):
        """ When a skill already exist and is called again. Default action is to create a new instance of it."""
        return

    def process(self):
        raise Exception("Process method of skills must be implemented")

    def eventFinished(self, event):
        self.events.remove(event)
        if not self.events:
            self.stop(True)

    def onTargetCollision(self, target, x, y, z, timeStamp):
        """ Skill has encountered a collision with the target. """
        return

    def onEnvironmentCollision(self, x, y, z, timeStamp):
        """ Skill has encountered a collision with the environment."""
        return

    def onPositionUpdate(self, x, y):
        """ A position update that came from the server or client pertaining to this skill."""
        return

    def onUserDamage(self):
        """ Should skill be cancelled when user takes damage.
            Implement at skill level to cancel movement, attacks, etc.
            :rtype: bool
            Must return True if it stops"""
        return False

    def onUserMove(self):
        """ Should skill be cancelled when user moves.
            :rtype: bool
            Stop skill if return True.
        """
        return False

    def onStart(self):
        return

    def onDestroyed(self):
        """ Called when the skill instance is removed forcefully. (Expected early termination)
            By default same behavior as expired, but can allow more functionality per skill.
        """
        self.onExpired()

    def onExpired(self):
        """ Called when the skill instance is removed by normal means. (Expected completion)"""
        return

    def onTargetDamage(self, char, x, y, z):
        """ Called when target takes damage, if no char is specified, coordinates are given instead or vice versa."""
        return

    def onSourceMove(self, source, x, y):
        """ Tells you which source is moving and their position. """
        return

    def onSourceActivate(self, source, x, y, z, count):
        """ Called when damage source is activated. """
        return

    def onSourceStop(self, source, result, x, y, z):
        """ Called when damage source expires by normal means."""
        return


class SkillState:
    __doc__ = " Store the class of every skills in use. each skill has a class that stores informations\n    about the skill and the pokemon using it.\n    Stored in a pokemon.\n    Used in game_server and client.\n\n    Example:\n\n    class Roulade:\n        - multiplier\n        - collision_check()\n\n    self.set(Roulade())\n    "

    def __init__(self):
        self.skills = {}

    def save(self, skillUseInstance: SkillUseInstance, instanceId=None):
        self.set(skillUseInstance)

    def wipe(self):
        self.stopAll()
        self.skills.clear()

    def stopAll(self):
        """ Force stops all instances. Usually on warp, or faint.
            Note: We make into a list as stopping an instance could remove it from the dict.
        """
        for skill in list(self.skills.values()):
            for instance in list(skill.values()):
                instance.stop()

    def generateId(self, skillUseInstance: SkillUseInstance):
        """ Assume there is already an element of the same skill. """
        instances = self.skills[skillUseInstance.skillInfo.id]
        instanceId = list(instances.values())[-1].instanceId + 1
        if instanceId > 255:
            instanceId = 0
        return instanceId

    def delete(self, skillUseInstance: SkillUseInstance):
        try:
            instances = self.skills[skillUseInstance.skillInfo.id]
            del instances[skillUseInstance.instanceId]
            if len(instances) == 0:
                del self.skills[skillUseInstance.skillInfo.id]
        except KeyError:
            pass

    def set(self, skillUseInstance: SkillUseInstance):
        """ Store a new instance of a skill. """
        skillId = skillUseInstance.skillInfo.id
        if skillId in self.skills:
            if not skillUseInstance.instanceId:
                instanceId = self.generateId(skillUseInstance)
                skillUseInstance.instanceId = instanceId
        else:
            if skillUseInstance.instanceId is None:
                skillUseInstance.instanceId = 0
            self.skills[skillId] = {}
        self.skills[skillId][skillUseInstance.instanceId] = skillUseInstance

    def get(self, skillUseInstance: SkillUseInstance):
        return self.getIfAny(skillUseInstance.skillInfo.id, skillUseInstance.instanceId)

    def getAllSkills(self):
        return [list(skillInstance.values()) for skillInstance in self.skills.values()]

    def getIfAny(self, skillId, instanceId):
        skillInstances = self.skills.get(skillId)
        if skillInstances:
            return skillInstances.get(instanceId)

    def getSkill(self, skillInfo, instanceId=0):
        return self.getIfAny(skillInfo.id, instanceId)

    def getInstancesOfSkill(self, skillInfo):
        return self.skills.get(skillInfo.id)

    def getSkillByName(self, skillName, instanceId=0):
        return self.getIfAny(skillName, instanceId)

    def inUse(self):
        return bool(self.skills)
