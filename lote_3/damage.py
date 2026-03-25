# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\world\action\damage.py
"""
Created on 9 janv. 2012

@author: Kami
"""
from shared.container.skill import SkillUseInstance
from client.control.service.session import sessionService
from shared.container.constants import RefPointType, DamageNotificationTags
from client.control.events.event import eventManager
from client.control.world.map import Effect, SkillEffect, DamageNotificationIcon
from client.data.world.map import EffectData
from client.data.world.animation import Animation, AnimationEnd

class DamageController:

    def __init__(self):
        eventManager.registerListener(self)

    def updateHp(self, char, data, amount):
        """ Update the HP of a pokemon. If the pokemon is our, we know the exact amount.
        If it's not we modify only the bar if in battle"""
        if data:
            data.stats.hp.current = amount
        if char:
            if sessionService.isClientPokemon(char):
                char.setHp(amount)
            else:
                char.setHpPer(amount / 100.0)
            data = char.data
        eventManager.notify("onPokemonHpUpdate", data)

    def onCharDamage(self, char, attacker, skill, instanceId, damageType, amount, damageTags, extraData, timeStamp):
        self.damageTaken(char, char.data, attacker, skill, instanceId, damageType, amount, damageTags, extraData, timeStamp)

    def onDamage(self, char, data, skill, damageType, amount, extraData, timeStamp):
        self.damageTaken(char, data, None, skill, 0, damageType, amount, 0, extraData, timeStamp)

    def damageTaken(self, char, data, attacker, skill, instanceId, damageType, amount, damageTags, extraData, timeStamp):
        if char:
            self.onSkillDamage(skill, char, attacker, damageType, instanceId, extraData, timeStamp)
            self.showDamageTags(char, damageTags)
        self.updateHp(char, data, amount)

    def onSkillDamage(self, skillInfo, char, attacker, damageType, instanceId, extraData, timeStamp):
        """
        @param skillInfo:
        @param char: Char object that took damage.
        @param attacker: Attacking character if there is one.
        @param damageType: Type of damage taken.
        @param instanceId: Instance ID needed if you need to pull damage or skill instances.
        @param timeStamp: Timestamp on when damage was applied.
        """
        if attacker:
            skillState = attacker.skillStates.getSkill(skillInfo, instanceId)
            if skillState:
                if hasattr(skillState, "onSkillDamage"):
                    char.getHurt()
                    skillState.onSkillDamage(char, attacker, timeStamp, extraData)
                    return
        self.GenericDamage(char, damageType)

    def GenericDamage(self, char, damageType):
        if char.visible:
            Effect(EffectData("normal_hit_[3]", position=(char.getPosition2D()), animation=Animation(delay=0.1, end=(AnimationEnd.STOP)), refPointType=(RefPointType.BOTTOMCENTER)))
            char.getHurt()

    def showDamageTags(self, char, damageTags):
        if damageTags:
            if damageTags & DamageNotificationTags.CRITICAL:
                DamageNotificationIcon(char, DamageNotificationTags.CRITICAL)
            else:
                if damageTags & DamageNotificationTags.IMMUNE:
                    DamageNotificationIcon(char, DamageNotificationTags.IMMUNE)
                else:
                    if damageTags & DamageNotificationTags.MISS:
                        DamageNotificationIcon(char, DamageNotificationTags.MISS)
                    if damageTags & DamageNotificationTags.RESIST:
                        DamageNotificationIcon(char, DamageNotificationTags.RESIST)
                if damageTags & DamageNotificationTags.EFFECTIVE:
                    DamageNotificationIcon(char, DamageNotificationTags.EFFECTIVE)


class Damage(SkillUseInstance):

    def __init__(self, skillInfo, damageType, char, atkChar=None, instanceId=None):
        self.skillInfo = skillInfo
        self.damageType = damageType
        self.char = char
        self.atkChar = atkChar
        self.instanceId = instanceId
        self.process()

    @staticmethod
    def callAgain(classObject, skillInfo, damageType, char, atkChar=None, instanceId=None):
        classObject(skillInfo, damageType, char, atkChar, instanceId)

    def process(self):
        raise Exception("Must be implemented.")


class GenericDamage(Damage):
    __doc__ = " The way the damage look like depends on the skill ID and the damageType. "

    def process(self):
        if self.char.visible:
            Effect(EffectData("normal_hit_[3]", position=(self.char.getPosition2D()), animation=Animation(delay=0.1, end=(AnimationEnd.STOP)), refPointType=(RefPointType.BOTTOMCENTER)))
            self.char.getHurt()


class Tackle(Damage):

    def process(self):
        Effect(EffectData("normal_hit_[3]", position=(self.char.getPosition2D()), animation=Animation(delay=0.1, end=(AnimationEnd.STOP)), refPointType=(RefPointType.BOTTOMCENTER)))
        self.char.getHurt()
        self.char.setStunDuration(0.3)
        if self.atkChar:
            touchingEmber = self.atkChar.skillStates.getSkill(self.skillInfo, self.instanceId)
            if touchingEmber:
                touchingEmber.endFromCollision(self.atkChar.getPosition2D())


class Grass(GenericDamage):

    def process(self):
        print("SELF.CHAR!", self.char)
        SkillEffect(EffectData("153", position=(self.char.getPosition2D()), animation=Animation(delay=0.1, end=(AnimationEnd.STOP)), refPointType=(RefPointType.BOTTOMCENTER)))
        self.char.getHurt()
        if self.atkChar:
            touchingEmber = self.atkChar.skillStates.getSkill(self.skillInfo, self.instanceId)
            if touchingEmber:
                touchingEmber.endFromCollision()


damageController = DamageController()
