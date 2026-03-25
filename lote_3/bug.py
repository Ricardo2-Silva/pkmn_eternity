# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\world\action\moves\bug.py
from shared.container.skill import StaticEventSource, LinearEventSource
from shared.controller.net.packetStruct import RawUnpacker
from shared.service.geometry import getAngleBetweenTwoPoints, getDistanceBetweenTwoPoints
from shared.container.constants import CreatureAction, PointDataType, RefPointType, StatType
from client.data.world.animation import AnimationEnd, Animation
from client.data.world.map import EffectData
from client.control.world.map import SkillEffect, Effect, LineEffect
from shared.container.db.point import PointHandler
from client.data.world.skill import ClientSkillUseInstance
import time, random
from twisted.internet import reactor
from client.data.container.char import charContainer
from client.control.system.anims import AnimCallable, BezierPathObjects, BezierTargetObject, BezierPath
import pyglet

class Stringshot(ClientSkillUseInstance):

    def process(self):
        self.direction = self.data
        self.char.setFacingNear(self.direction)
        self.char.playActionWithDelay(CreatureAction.SHOOT, 0.5, 0.07)
        self.initialPosition = self.char.getPositionInFrontMiddle(self.direction, 10)
        LinearEventSource(self, *(self.initialPosition), **{'direction':self.direction,  'speed':150,  'distance':100})
        self.strings = []
        self.start()

    def onDamageSourceReceived(self, targetId, targetIdRange, x, y, z, direction, radius, duration, timeStamp):
        targetChar = charContainer.getCharByIdIfAny(targetId, targetIdRange)
        if targetChar:
            stringhit = SkillEffect(EffectData("stringshot_hit_[7]", position=(0, targetChar.getHeight() // 2), attach=targetChar, animation=Animation(delay=0.1),
              renderingOrder=1))

    def onSourceMove(self, source, x, y):
        x0, y0 = self.initialPosition
        distance = getDistanceBetweenTwoPoints((x0, y0), (x, y))
        for string in self.strings:
            string.setWidth(distance)

    def onSourceStop(self, source, result, x, y, z):
        for string in self.strings:
            string.delete()

    def onSourceActivate(self, source, x, y, z, count):
        for i in range(4):
            pyglet.clock.schedule_once(self.makeStrings, i * 0.15, i)

    def makeStrings(self, dt, i):
        string = LineEffect(EffectData((255, 255, 255, 150), (self.initialPosition[0], self.initialPosition[1])))
        string.setRotation(-random.randrange(int(self.direction - 10), int(self.direction + 10)))
        self.strings.append(string)


class Leechlife(ClientSkillUseInstance):

    def process(self):
        charId, charType = self.data
        self.target = charContainer.getCharByIdIfAny(charId, charType)
        if self.target:
            if self.char.getPosition2D() != self.target.getPosition2D():
                angle = getAngleBetweenTwoPoints(self.char.getPosition2D(), self.target.getPosition2D())
                self.char.setFacingNear(angle)
            self.char.playAction(CreatureAction.SHOOT, 0.5)
            self.showLeech()

    def showLeech(self):
        if self.target.isFainted() or self.char.isFainted():
            return
        for i in range(5):
            reactor.callLater(0.05 * i, self._leechEffect)

    def _leechEffect(self):
        if not self.target.isFainted() or not self.char.isFainted() or not self.expired:
            x, y = randomPositionWithinEntity(self.target)
            leech = Effect(EffectData("ball_bright_small_[4]", (x, y), animation=Animation(delay=0.1, end=(AnimationEnd.RESTART), duration=0)))
            path = BezierPath((
             x, y), self.char.getCenter(), (
             x + 20, y + 80), self.char.getPosition2D())
            anim = BezierTargetObject(leech, self.char, path, 0.5)
            anim += AnimCallable(leech.stopAnimation)
            anim += AnimCallable(leech.delete)
            leech.startAnim(anim)


def randomPositionWithinEntity(char):
    x, y = char.getPosition2D()
    width, height = char.getSize()
    return (random.randrange(int(x) - width // 2, int(x) + width // 2), random.randrange(int(y), int(y) + height))


def randomPositionWithinSquare(x, y, width, height):
    return (
     random.randrange(x - width // 2, x + width // 2), random.randrange(y, y + height))
