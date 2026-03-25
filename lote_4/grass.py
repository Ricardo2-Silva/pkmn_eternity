# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\world\action\moves\grass.py
"""
Created on Feb 15, 2016

@author: Admin
"""
import time
from client.control.camera import worldCamera
from client.control.events import eventManager
from client.control.events.world import worldInputManager
from client.control.net.sending import packetManager
from shared.container.geometry import createPolygon, Polygon
from shared.container.net import cmsg
from shared.container.skill import LinearEventSource, StaticEventSource, LinearConstantEventSource, StaticTickEventSource
from shared.service.direction import directionService
from shared.service.geometry import getAngleBetweenTwoPoints, getDistanceBetweenTwoPoints
from shared.container.constants import CreatureAction, PointDataType, RefPointType
from client.data.world.animation import AnimType, Animation, AnimationEnd
from client.data.world.map import EffectData
from client.data.layer import LayerType
from client.control.world.map import SkillEffect, Effect
from shared.container.db.point import PointHandler
from client.data.world.skill import ClientSkillUseInstance
from client.data.container.char import charContainer
from twisted.internet import reactor
import random, math, pyglet, rabbyt
from client.control.system.anims import MoveToTarget, MoveToTargetObject, AnimCallable, BezierTargetObject, BezierPath, BezierPathObjects, ScaleXTo, ScaleYTo, MoveBy, Lerp

class Solarbeam(ClientSkillUseInstance):

    def process(self):
        direction = self.data
        self.char.setFacingNear(direction)
        self.direction = direction
        self.char.playAction(CreatureAction.SPATK, 3)
        self.charge = Effect(EffectData("charge_particles_[3]", (self.char.getCenter()), animation=Animation(delay=0.15, duration=0), refPointType=(RefPointType.BOTTOMCENTER)))
        self.char.getCastObject().startCast(4)
        source = StaticEventSource(self, 0, 0, 0, duration=6)
        self.start()

    def delete(self):
        if self.charge.visible:
            self.charge.delete()

    def onSourceStop(self, source, result, x, y, z):
        self.delete()

    def onDamageSourceReceived(self, targetId, targetIdRange, x, y, z, direction, radius, duration, timeStamp):
        self.fireBeam()

    def fireBeam(self):
        self.charge.delete()
        self.char.playAction(CreatureAction.EMIT, 2)
        e = SkillEffect(EffectData("112_[2]", (self.char.getCenter()), animation=Animation(delay=0.15, duration=0), refPointType=(RefPointType.LEFTCENTER)))
        e.setRotation(-self.direction)
        e.setScales(0.1, 0.1)
        anim = ScaleXTo(e.renderer.sprite, 0.1, 10, 0.1)
        anim |= ScaleYTo(e.renderer.sprite, 0.3, 2, 0.5) + ScaleYTo(e.renderer.sprite, 2, 0, 2)
        e.startAnim(anim)


class Vinewhip(ClientSkillUseInstance):

    def process(self):
        direction = self.data
        self.char.setFacingNear(direction)
        self.char.playAction(CreatureAction.ATK, 0.5)
        x, y = self.char.getPositionInFrontMiddle(direction, 8)
        s = Effect(EffectData("vine_whip_[6]", (x, y), animation=Animation(delay=0.1), refPointType=(RefPointType.TOPCENTER)))
        s.setRotation(-direction + 276)


class Sleeppowder(ClientSkillUseInstance):

    def process(self):
        self.char.playAction(CreatureAction.SPATK, self.skillInfo.duration)
        self.char.getCastObject().startChannel(self.skillInfo.duration)
        x, y = self.char.getCenter()
        self.start()
        for i in range(60):
            reactor.callLater(0.05 * i, self.generateCloud, x, y)

    def generateCloud(self, x, y, radius=100):
        if self.active:
            q = random.random() * (math.pi * 2)
            r = math.sqrt(random.random())
            x1 = radius * r * math.cos(q)
            y1 = radius / 2 * r * math.sin(q)
            cloude = SkillEffect(EffectData("sleeppowder", (
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


class Razorleaf(ClientSkillUseInstance):

    def process(self):
        direction = self.data
        self.char.setFacingNear(direction)
        self.char.playActionWithDelay(CreatureAction.SPATK, 0.5, 0.07)
        x, y, z = self.char.getPositionInFront(direction, 10)
        self.leaves = {}
        self.sources = []
        self.start()

    def onDamageSourceReceived(self, targetId, targetIdRange, x, y, z, direction, radius, duration, timeStamp):
        source = LinearEventSource(self, x, y, z, direction, 100, 100)
        self.leaves[source] = SkillEffect(EffectData("leaf1_[8]", (x, y), animation=None, layerType=(LayerType.LAYERED), refPointType=(RefPointType.BOTTOMCENTER)))
        self.leaves[source].spin(1, 5)
        self.sources.append(source)
        source.start()

    def onSourceStop(self, source, result, x, y, z):
        self.sources.remove(source)
        if self.leaves[source].visible:
            self.leaves[source].delete()
        del self.leaves[source]
        if not self.sources:
            self.stop(True)

    def onSourceMove(self, source, x, y):
        leaf = self.leaves[source]
        if leaf.visible:
            leaf.setPosition(x, y, 0)


class Leechseed(ClientSkillUseInstance):

    def process(self):
        charId, charType = self.data
        self.target = charContainer.getCharByIdIfAny(charId, charType)
        self.duration = 30
        self.seed = Effect(EffectData("seed_[1]", (self.char.getPosition2D()),
          renderingOrder=1))
        self.sprout = None
        if self.char.getPosition2D() != self.target.getPosition2D():
            angle = getAngleBetweenTwoPoints(self.char.getPosition2D(), self.target.getPosition2D())
            self.char.setFacingNear(angle)
            self.target.damageStates.set(self)
        else:
            angle = 0
        anim = MoveToTargetObject(self.seed, self.target, 0.5)
        anim += AnimCallable(self.seed.delete)
        anim += AnimCallable(self._sproutSeed)
        self.seed.startAnim(anim)
        self.start()

    def _sproutSeed(self):
        """ Sprout will populate. """
        if self.active:
            if not self.sprout:
                self.sprout = Effect(EffectData("sprout_[2]", (
                 0, random.random() * 10),
                  animation=Animation(delay=0.3, duration=0),
                  attach=(self.target),
                  renderingOrder=(-1)))

    def onExpired(self):
        if self.seed.visible:
            self.seed.hide()
        if self.sprout:
            if self.sprout.visible:
                self.sprout.hide()
        self.target.damageStates.delete(self)

    def onSkillDamage(self, char, target, timeStamp, extraData):
        self._sproutSeed()
        self.showLeech()

    def showLeech(self):
        if not self.active:
            return
        if self.target.isFainted() or self.char.isFainted():
            self.stop()
            return
        for i in range(5):
            pyglet.clock.schedule_once(self._leechEffect, 0.1 * i)

        reactor.callLater(1, self.healEffect)

    def _leechEffect(self, dt):
        if self.active:
            if not self.target.isFainted() or not self.char.isFainted():
                x, y = self.sprout.getPosition2D()
                leech = Effect(EffectData("ball_bright_small_[4]", (x, y), animation=Animation(delay=0.1, duration=0)))
                path = BezierPathObjects(self.sprout, self.char, (
                 x + 20, y + 80), self.char.getPosition2D())
                anim = BezierTargetObject(leech, self.char, path, 1)
                anim += AnimCallable(leech.stopAnimation)
                anim += AnimCallable(leech.delete)
                leech.startAnim(anim)

    def healEffect(self):
        if self.active:
            eventManager.notify("onCharPlayEffect", self.char, "Heal")


class Magicalleaf(ClientSkillUseInstance):

    def process(self):
        x, y = self.data
        direction = getAngleBetweenTwoPoints(self.char.getPosition2D(), self.data)
        self.running = True
        self.char.setFacingNear(direction)
        self.char.playActionWithDelay(CreatureAction.SPATK, 0.5, 0.07)
        self.leaves = {}
        self.sources = []
        self.start()
        self._genPosition()

    def _genPosition(self):
        if self.active:
            self.to_x, self.to_y = worldCamera.toMapPosition(worldInputManager.x, worldInputManager.y)
            packetManager.queueSend(cmsg.SkillUpdatePosition, self.char.data.id, self.char.data.idRange, self.skillInfo.id, self.instanceId, int(self.to_x), int(self.to_y))
            reactor.callLater(0.25, self._genPosition)

    def onPositionUpdate(self, x, y):
        for source in self.sources:
            source.target_x = x
            source.target_y = y

    def onSkillDamage(self, char, target, timeStamp, extraData):
        try:
            source = self.sources[extraData]
            source.stop()
        except IndexError:
            print("Warning: Failed to find index in skill Magicalleaf", extraData)

    def onDamageSourceReceived(self, targetId, targetIdRange, x, y, z, direction, radius, duration, timeStamp):
        source = LinearConstantEventSource(self, x, y, z, x, y, 2, 3)
        self.leaves[source] = SkillEffect(EffectData("magical_leaf_[11]", (x, y), animation=Animation(delay=0.02, duration=5), layerType=(LayerType.LAYERED), refPointType=(RefPointType.BOTTOMCENTER)))
        self.sources.append(source)
        source.start()

    def onExpired(self):
        for leaf in self.leaves.values():
            try:
                leaf.delete()
            except:
                pass

        self.sources.clear()
        self.leaves.clear()

    def onSourceStop(self, source, result, x, y, z):
        self.leaves[source].delete()
        del self.leaves[source]
        if not self.sources:
            self.stop(True)

    def onSourceMove(self, source, x, y):
        leaf = self.leaves[source]
        if leaf.visible:
            leaf.setPosition(x, y, 0)


class Absorb(ClientSkillUseInstance):

    def process(self):
        direction = self.direction = self.data
        pos = self.startPos = self.char.getPositionInFrontMiddle(direction, 10)
        x, y = pos
        self.startEffect = SkillEffect(EffectData("absorb_s_[4]", pos,
          renderingOrder=1,
          animation=Animation(delay=0.07, duration=0)))
        self.startEffect.setRotation(-direction)
        nx = x + math.cos(math.radians(direction)) * 5
        ny = y + math.sin(math.radians(direction)) * 5
        self.beamEffect = SkillEffect(EffectData("absorb_m", (
         nx, ny),
          renderingOrder=1,
          refPointType=(RefPointType.LEFTCENTER)))
        self.beamEffect.setRotation(-direction)
        ex, ey = self.beamEffect.getPosition2D()
        enx = ex + math.cos(math.radians(direction)) * self.beamEffect.getWidth()
        eny = ey + math.sin(math.radians(direction)) * self.beamEffect.getWidth()
        self.endEffect = SkillEffect(EffectData("absorb_e",
          (
         enx, eny),
          renderingOrder=1))
        self.endEffect.setRotation(-direction)
        self.char.setFacingNear(direction)
        self.paused = False
        self.stopAt = 1000
        self.beamStop = False
        self.source = LinearEventSource(self, *pos, *(0, self.direction, 150, 150))
        self.damageSource = StaticTickEventSource(self, *pos, *(0, 0.5, 4))
        self.start()

    def onSourceStop(self, source, result, x, y, z):
        if source == self.damageSource:
            self.kill()

    def onDamageSourceReceived(self, targetId, targetIdRange, x, y, z, direction, radius, duration, timeStamp):
        print("RECEIVED")
        if self.source.active:
            if not self.paused:
                self.paused = (
                 x, y)

    def onSourceMove(self, source, x, y):
        if source == self.source:
            if self.paused:
                print("getDistanceBetweenTwoPoints(self.paused, (x, y))", getDistanceBetweenTwoPoints(self.paused, (x, y)))
                stopAt = getDistanceBetweenTwoPoints(self.paused, (x, y))
                if stopAt <= self.stopAt:
                    self.stopAt = stopAt
                else:
                    self.beamStop = True
                if not self.beamStop:
                    distance = getDistanceBetweenTwoPoints(self.startPos, (x, y))
                    self.beamEffect.setWidth(distance)
                    ex, ey = self.beamEffect.getPosition2D()
                    enx = ex + math.cos(math.radians(self.direction)) * self.beamEffect.getWidth()
                    eny = ey + math.sin(math.radians(self.direction)) * self.beamEffect.getWidth()
                    self.endEffect.setPosition(enx, eny)

    def kill(self):
        self.beamEffect.delete()
        self.endEffect.delete()
        self.startEffect.delete()
