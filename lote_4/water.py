# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\world\action\moves\water.py
"""
Created on Feb 15, 2016

@author: Admin
"""
from client.render.world.map import SkillLayeredEffect
from shared.container.skill import LinearEventSource
from shared.service.geometry import getAngleBetweenTwoPoints, getPositionInFront, getDistanceBetweenTwoPoints
from shared.container.constants import CreatureAction, PointDataType, RefPointType
from client.data.world.animation import AnimType, Animation, AnimationEnd
from client.data.world.map import EffectData
from client.data.layer import LayerType
from client.control.world.map import SkillEffect, Effect
from shared.container.db.point import PointHandler
from client.data.world.skill import ClientSkillUseInstance
import math, random, rabbyt
from shared.service.direction import directionService
import time
from twisted.internet import reactor
from client.render.particle import ParticleSystem
from client.control.system.anims import ScaleXTo, ScaleYTo

class Bubble(ClientSkillUseInstance):

    def process(self):
        direction = self.data
        self.char.setFacingNear(direction)
        self.char.playActionWithDelay(CreatureAction.SPATK, 0.5, 0.07)
        self.startPosition = self.char.getPositionInFrontMiddle(self.data, 10)
        LinearEventSource(self, *(self.startPosition), **{'speed':70,  'distance':100,  'loopStep':0.03333333333333333})
        self.bubble = SkillEffect(EffectData("225_[7]", (self.startPosition), animation=Animation(delay=0.3, duration=0)))
        self.bubble.setScale(0.1)
        self.bubble.grow(1, 0.1, 1.0)
        self.start()

    def onSkillDamage(self, char, target, timeStamp, extraData):
        return

    def onSourceStop(self, source, result, x, y, z):
        pop = SkillEffect(EffectData("226_[4]", (self.bubble.getPosition2D()), animation=Animation(delay=0.1)))
        if self.bubble.visible:
            self.bubble.delete()

    def onSourceMove(self, source, x, y):
        self.bubble.setPosition(x, y)


class BubblebeamParticles(ParticleSystem):
    totalParticles = 20
    life = 0.5
    lifeVariation = 0.6
    angle = 90
    angleVariation = 8
    speed = 100
    speedVariation = 20
    scaleLife = False
    scale = 0.1
    scaleVar = 0.4
    gravity = (0, 0)
    duration = 0.7


class Bubblebeam(ClientSkillUseInstance):

    def process(self):
        direction = self.data
        self.char.setFacingNear(direction)
        self.char.playActionWithDelay(CreatureAction.SPATK, 0.5, 0.07)
        print("")
        beam = BubblebeamParticles(EffectData("bubble", self.char.getPositionInFrontMiddle(direction, 5)))
        beam.angle = direction
        beam.start()


class Aquatail(ClientSkillUseInstance):

    def process(self):
        self.direction = self.data - 50
        self.char.setFacingNear(self.data)
        self.char.playAction(CreatureAction.SWING, 0)
        self.char.clearAllOrders()
        self.move()

    def move(self):
        pos = self.char.getPosition2D()
        for i in range(0, 5):
            reactor.callLater(0.05 * i, self.createSplash, self.test(pos[0], pos[1], 36, math.radians(self.direction + i * 32)))

    def test(self, x, y, radius, angle):
        return (x + radius * math.cos(angle), y + radius * math.sin(angle))

    def createSplash(self, i):
        SkillEffect(EffectData("splash_normal", i, animation=Animation(delay=0.1), refPointType=(RefPointType.BOTTOMCENTER), metafile=True))


class Aquajet(ClientSkillUseInstance):

    def process(self):
        self.direction = self.data
        self.char.setFacingNear(self.direction)
        self.startPosition = self.char.getPosition2D()
        LinearEventSource(self, *(self.startPosition), **{'speed':190,  'distance':100})
        self.totalDistance = 0
        self.createdImages = 0
        self.char.playAction(CreatureAction.WALK, 3)
        (self.createSplash)(*self.startPosition, *(0, ))
        self.start()

    def onExpired(self):
        self.char.cancelAction()

    def onDestroyed(self):
        self.char.cancelAction()
        self.char.setStunDuration(0.3)

    def createSplash(self, x, y, z):
        SkillEffect(EffectData("splash_normal", (x, y), animation=Animation(delay=0.1), refPointType=(RefPointType.BOTTOMCENTER), metafile=True))
        self.createdImages += 1

    def removeImage(self, result, sprite):
        if sprite.visible:
            sprite.delete()

    def onSourceStop(self, source, result, x, y, z):
        self.char.cancelAction()

    def onSourceMove(self, source, x, y):
        self.totalDistance = int(getDistanceBetweenTwoPoints(self.startPosition, (x, y)))
        if (self.char.canMoveOnPosition)(self.direction, *self.char.getPosition2D(), *(x, y, 0)):
            self.char.setPosition(x, y)
            if self.totalDistance / 16 > self.createdImages:
                self.createSplash(x, y, 0)
                self.char.applyEnvironmentEffects()
        else:
            self.stop(False)


class Watergun(ClientSkillUseInstance):

    def process(self):
        direction = self.data
        self.char.setFacingNear(direction)
        self.char.playAction(CreatureAction.SHOOT, 0)
        self.initialPosition = self.char.getPositionInFrontMiddle(direction, 10)[:2]
        self.particle = SkillEffect(EffectData("109_[4]", (self.initialPosition),
          animation=Animation(delay=0.1),
          refPointType=(RefPointType.LEFTCENTER)))
        self.particle.setScales(0.1, 0.1)
        self.particle.setRotation(-direction)
        anim = ScaleXTo(self.particle.renderer.sprite, 0.1, 0.5, 0.1) | ScaleYTo(self.particle.renderer.sprite, 0.3, 0.5, 0.3)
        self.particle.startAnim(anim)


class PulseEffect(SkillEffect):
    renderClass = SkillLayeredEffect


class Waterpulse(ClientSkillUseInstance):
    directionToGraphic = {(directionService.RIGHT): "water_pulse_r", 
     (directionService.UP_RIGHT): "water_pulse_tr", 
     (directionService.DOWN_RIGHT): "water_pulse_br", 
     (directionService.UP): "water_pulse_c", 
     (directionService.DOWN): "water_pulse_c", 
     (directionService.LEFT): "water_pulse_r", 
     (directionService.UP_LEFT): "water_pulse_tr", 
     (directionService.DOWN_LEFT): "water_pulse_br"}
    directionToFlip = {(directionService.RIGHT): False, 
     (directionService.UP_RIGHT): False, 
     (directionService.DOWN_RIGHT): False, 
     (directionService.UP): False, 
     (directionService.DOWN): False, 
     (directionService.LEFT): True, 
     (directionService.UP_LEFT): True, 
     (directionService.DOWN_LEFT): True}

    def process(self):
        direction = self.data
        self.char.setFacingNear(direction)
        self.char.playAction(CreatureAction.SHOOT, 0)
        self.initialPosition = self.char.getPositionInFrontMiddle(direction, 10)[:2]
        self.particles = {}
        self.sources = []
        for i in range(3):
            reactor.callLater(i * 0.1, self._genParticle)

        self.start()

    def onSourceMove(self, source, x, y):
        particle = self.particles[source]
        if particle.visible:
            particle.setPosition(x, y)

    def onSourceActivate(self, source, x, y, z, count):
        return

    def _genParticle(self):
        source = LinearEventSource(self, *self.initialPosition, *(0, self.data, 50, 200))
        closest = directionService.getNear(self.data)
        data = EffectData((self.directionToGraphic[closest]),
          (self.initialPosition),
          animation=Animation(delay=0.1),
          refPointType=(RefPointType.CENTER),
          metafile=True,
          flip_x=(self.directionToFlip[closest]),
          renderingOrder=1)
        data.originalPosition = self.initialPosition
        particle = PulseEffect(data)
        self.particles[source] = particle
        source.start()
        self.sources.append(source)


class Withdraw(ClientSkillUseInstance):

    def process(self):
        self.char.playAction(CreatureAction.WITHDRAW, 0)
