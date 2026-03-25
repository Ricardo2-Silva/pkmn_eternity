# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\world\action\moves\fire.py
"""
Created on Feb 15, 2016

@author: Admin
"""
import time
from client.data.world.skill import ClientSkillUseInstance
from shared.container.skill import LinearEventSource
from shared.container.constants import CreatureAction, PointDataType, RefPointType, IdRange, StatusEffect
from client.data.world.animation import AnimType, Animation, AnimationEnd
from client.data.world.map import EffectData
from client.data.layer import LayerType
from client.control.world.map import SkillEffect, Effect
from twisted.internet import reactor
from client.data.container.char import charContainer
import random, pyglet
from shared.container.geometry import Polygon

class Ember(ClientSkillUseInstance):

    def process(self):
        direction = self.data
        self.char.setFacingNear(direction)
        self.char.playAction(CreatureAction.SHOOT, 0)
        self.initialPosition = self.char.getPositionInFrontMiddle(direction, 10)
        self.fire = LinearEventSource(self, *self.initialPosition, *(0, self.data, 125, 100))
        self.flame = SkillEffect(EffectData("134_[4]", (self.initialPosition), animation=Animation(delay=0.07, end=(AnimationEnd.RESTART), duration=0),
          renderingOrder=0))
        self.start()

    def onSourceMove(self, source, x, y):
        self.flame.setPosition(x, y)

    def onSourceStop(self, source, result, x, y, z):
        if result:
            if self.flame.visible:
                self.flame.hide()

    def onDestroyed(self):
        self.destroyFlame(self.flame.getPosition2D())

    def onSkillDamage(self, char, attacker, timeStamp, extraData):
        self.destroyFlame(char.getPosition2D())

    def destroyFlame(self, position):
        """ If destroyed early, destroy flame at current location."""
        if self.flame.visible:
            self.flame.hide()
        Effect(EffectData("fire_[3]", position=position, animation=Animation(delay=0.1, end=(AnimationEnd.STOP)), refPointType=(RefPointType.BOTTOMCENTER)))


class Firepunch(ClientSkillUseInstance):

    def process(self):
        direction = self.data
        self.char.setFacingNear(direction)
        self.char.playAction(CreatureAction.PUNCH, 0)
        punchInitialPos = self.char.getPositionInFront(direction, 20)[:2]
        e = SkillEffect(EffectData("punch", position=punchInitialPos, refPointType=(RefPointType.CENTER), animation=Animation(delay=0.05), metafile=True))
        hitChar = charContainer.getAllCharsInDirection(IdRange.PC_POKEMON, punchInitialPos[0], punchInitialPos[1], 0, self.data, 30, 30)
        if hitChar:
            self.onHit(hitChar[0])

    def onHit(self, hitChar):
        x, y = hitChar.getPosition2D()
        e = SkillEffect(EffectData("fire_punch", position=(x, y), refPointType=(RefPointType.CENTER), animation=Animation(delay=0.05), metafile=True))
        e.moveTo(0.4, x, y - 30)
        if random.randint(0, 100) < 30:
            hitChar.showStatusEffect(StatusEffect.BURN, 3)


class Flamethrower(ClientSkillUseInstance):

    def process(self):
        direction = self.data
        self.char.setFacingNear(direction)
        action = self.char.playAction(CreatureAction.SHOOT, 0)
        x, y = self.char.getPositionInFrontMiddle(direction, 10)[:2]
        self.effect = SkillEffect(EffectData("107_[4]", (x, y), animation=Animation(delay=0.1, duration=(self.skillInfo.duration)),
          refPointType=(RefPointType.LEFTCENTER),
          renderingOrder=1))
        self.effect.setRotation(-direction)
        self.start()
        self.char.getCastObject().startChannel(self.skillInfo.duration)

    def onDestroyed(self):
        print("ON DESTROYED")
        if self.effect.visible:
            self.effect.delete()

    def onExpired(self):
        print("ON EXPIRED")

    def _freeze(self, result):
        self.char.renderer.stopAnimation()
