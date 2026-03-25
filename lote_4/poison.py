# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\world\action\moves\poison.py
"""
Created on Feb 15, 2016

@author: Admin
"""
import math, random, time
from twisted.internet.task import LoopingCall
from client.control.camera import worldCamera
from client.control.events.world import worldInputManager
from client.control.system.anims import MoveBy, AnimCallable, MoveTo, MoveToMovingPosition, OrbitPosition
from client.control.world.map import SkillEffect
from client.data.layer import LayerType
from client.data.world.animation import Animation, AnimationEnd
from client.data.world.map import EffectData
from client.data.world.skill import ClientSkillUseInstance
from shared.container.constants import CreatureAction, PointDataType, RefPointType
from shared.container.db.point import PointHandler
from shared.container.skill import LinearEventSource, LinearPositionEventSource, LinearConstantEventSource
from twisted.internet import reactor
from shared.controller.maths.maths import interpolate
from shared.service.geometry import getAngleBetweenTwoPoints, getDistanceBetweenTwoPoints

class Poisonsting(ClientSkillUseInstance):

    def process(self):
        direction = self.data
        self.char.setFacingNear(direction)
        self.char.playActionWithDelay(CreatureAction.SPATK, 0.5, 0.07)
        self.startPosition = self.char.getPositionInFrontMiddle(direction, 10)
        poison = LinearEventSource(self, *self.startPosition, *(0, direction, 90, 100))
        self.stinger = SkillEffect(EffectData("sting_[1]", self.startPosition))
        self.stinger.setRotation(-direction)
        self.start()

    def onSourceMove(self, source, x, y):
        self.stinger.setPosition(x, y)

    def onSourceStop(self, source, result, x, y, z):
        if self.stinger.visible:
            self.stinger.hide()


class Poisonpowder(ClientSkillUseInstance):

    def process(self):
        self.char.playAction(CreatureAction.SPATK, self.skillInfo.duration)
        self.char.getCastObject().startChannel(self.skillInfo.duration)
        x, y = self.char.getCenter()
        self.start()
        for i in range(30):
            reactor.callLater(0.05 * i, self.generateCloud, x, y)

    def generateCloud(self, x, y, radius=100):
        q = random.random() * (math.pi * 2)
        r = math.sqrt(random.random())
        x1 = radius * r * math.cos(q)
        y1 = radius / 2 * r * math.sin(q)
        cloude = SkillEffect(EffectData("poisonpowder", (
         x + x1, y + y1),
          animation=Animation(end=(AnimationEnd.STOP), delay=0.1, duration=0.75, removal=False),
          layerType=(LayerType.LAYERED),
          refPointType=(RefPointType.BOTTOMCENTER),
          metafile=True))
        axis = random.randrange(-6, 6)
        m1 = MoveBy(cloude.renderer.sprite, (
         axis, random.randrange(-8, -5)), 0.5 + 0.25 * random.random())
        m1 += MoveBy(cloude.renderer.sprite, (
         -axis, random.randrange(-5, -3)), 0.5 + 0.15 * random.random())
        m1 += AnimCallable(cloude.delete)
        cloude.startAnim(m1)


class Sludge(ClientSkillUseInstance):

    def process(self):
        x, y = self.data
        direction = getAngleBetweenTwoPoints(self.char.getPosition2D(), self.data)
        self.ground = None
        self._elapsed = 0
        self.test_duration = 4
        self.char.setFacingNear(direction)
        self.char.playAction(CreatureAction.SPATK)
        splash = SkillEffect(EffectData("68_[12]", (
         x, y),
          animation=Animation(frames=(range(12)), delay=0.1),
          renderingOrder=1))
        reactor.callLater(0.30000000000000004, self.setOnGround, splash)
        reactor.callLater(1.2000000000000002, self.setGround, x, y)

    def onSourceMove(self, source, x, y):
        self.ground.setPosition(x, y)

    def onSourceStop(self, source, result, x, y, z):
        self.ground.delete()

    def tester(self):
        self._elapsed += 0.016666666666666666
        t = min(1, self._elapsed / self.test_duration)
        new_x, new_y = self.originalPos
        x0 = self.proper_lerp(new_x, self.to_x, t)
        y0 = self.proper_lerp(new_y, self.to_y, t)
        self.ground.setPosition(x0, y0)
        if t == 1.0:
            self.loopTest.stop()

    def setOnGround(self, splash):
        splash.data.renderingOrder = 2800
        splash.renderer.updatePosition()

    def _update(self):
        return

    def setGround(self, x, y):
        self.ground = SkillEffect(EffectData("68_[12]", (
         x, y),
          renderingOrder=2800,
          animation=Animation(frames=(range(7, 12)), delay=0.1, duration=10, end=(AnimationEnd.RESTART), removal="delete")))
