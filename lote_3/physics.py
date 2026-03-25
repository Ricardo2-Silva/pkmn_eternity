# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\world\action\physics.py
"""
Created on 21 juil. 2011

@author: Kami
"""
import math, time
from client.data.layer import LayerType
from client.data.maths.physics import G
from client.control.events.event import eventManager
from client.control.service.session import sessionService
from client.data.settings import gameSettings
from client.render.layer import worldLayer
from shared.service.geometry import getDistanceBetweenTwoPoints, getAngleBetweenTwoPoints
from shared.controller.maths.maths import interpolate
from client.game import desktop
from client.control.system.sound import mixerController
from pyglet.window import key
from twisted.internet import reactor
from shared.container.constants import CreatureAction, GroundType
import pyglet
from twisted.internet import defer
from client.control.system.anims import Animable, FadeOut, ParallelAnims, MultiParallelAnim, AnimableRender, AnimCallable

class PhysicsController(object):
    __doc__ = " Here we handle which objects are getting updated "

    def __init__(self):
        self.physicsObjects = []
        self.jumpers = []
        eventManager.registerListener(self)

    def reset(self):
        self.physicsObjects.clear()
        self.jumpers.clear()

    def add(self, physicsObject):
        self.physicsObjects.append(physicsObject)

    def remove(self, physicsObject):
        self.physicsObjects.remove(physicsObject)

    def onCharFly(self, char, z, duration=1.0):
        f = Fly(char, duration=duration, height=z)
        f.start()
        if z > 0:
            char.flying = True
            char.setAction(CreatureAction.ATK)
        else:
            char.flying = False

    def canJump(self, charData):
        if charData in self.jumpers:
            return False
        else:
            if charData.groundType in GroundType.WATER:
                return False
            if charData.flying:
                return False
            return True

    def onKeyDown(self, symbol, modifiers):
        if desktop.hasFocus():
            return
        if symbol == gameSettings.getKey("jump"):
            if sessionService.ticks.canJump():
                char = sessionService.getSelectedChar()
                if char:
                    if self.canJump(char):
                        mixerController.playSound("Jump")
                        j = Jump(char)
                        j.start()
                        sessionService.ticks.setJump()

    def onCharJump(self, char):
        if self.canJump(char):
            self.jumpers.append(char)

            def removal(_):
                self.jumpers.remove(char)

            j = Jump(char)
            j.start()
            j.defer.addCallback(removal)

    def update(self, dt):
        for physicsObject in self.physicsObjects:
            physicsObject.update(dt)

    def draw(self, interp):
        for physicsObject in self.physicsObjects:
            physicsObject.draw(interp)


physicsController = PhysicsController()

class Throw(object):
    __doc__ = " All object that implements this... can be throw !"

    def __init__(self, object, toPosition, angle=33, initial_speed=45, speed=5, rotate=True):
        self.object = object
        self._position = self.object.getPosition2D()
        self.toPosition = toPosition
        self._angle = math.radians(angle)
        self._speed = speed
        self._speedS = initial_speed * math.sin(self._angle)
        self._anglePoints = math.radians(getAngleBetweenTwoPoints(object.getPosition2D(), toPosition))
        self._distance = getDistanceBetweenTwoPoints(object.getPosition2D(), toPosition)
        self._elapsedTime = 0
        self._finalTime = self._calcThrowTime()
        if rotate is True:
            self.object.rotate(self.getTotalTime(), 1)
        self.defer = defer.Deferred()
        self.defer.addErrback(self._canceled)
        self.active = False

    def _canceled(self, _):
        return

    def start(self):
        self.active = True
        physicsController.add(self)

    def stop(self):
        self.active = False
        physicsController.remove(self)

    def cancel(self):
        if self.active:
            self.stop()

    def _calcThrowTime(self):
        return -(2 * self._speedS) / -G

    def _calcHeightAtTime(self, deltaTime):
        return self._speedS * deltaTime + -G * pow(deltaTime, 2) / 2.0

    def getTotalTime(self):
        """ Some functions may need the final time to run onEnd functions or something else """
        return self._finalTime / self._speed

    def update(self, dt):
        distance = self._distance * self._elapsedTime / self._finalTime
        z = self._calcHeightAtTime(self._elapsedTime)
        x = self._position[0] + distance * math.cos(self._anglePoints)
        y = self._position[1] + distance * math.sin(self._anglePoints)
        self.object.setPosition(x, y, z)
        if self._elapsedTime >= self._finalTime:
            self.stop()
            self.defer.callback("stopped")
            return
        self._elapsedTime += dt * self._speed

    def draw(self, interp):
        self.object.setRenderPosition(interp)


class ArcPath(AnimableRender):

    def __init__(self, source, target, source_offset=(0, 0), target_offset=(0, 0), angle=33, curveFactor=100, speed=1):
        super().__init__()
        self.object = object
        self._angle = math.radians(angle)
        self._factor = curveFactor * math.sin(self._angle)
        self._distance = getDistanceBetweenTwoPoints(source.getPosition2D(), target.getPosition2D())
        self._accumulatedTime = 0
        self._finalTime = self._calcTotalTime()
        self._speed = speed
        self._source_offset = source_offset
        self._target_offset = target_offset
        self.group, self.batch = worldLayer.getLayerRender(LayerType.LAYERED, False)
        x, y = source.getPosition2D()
        self._x, self._y = x + self._source_offset[0], y + self._source_offset[1]
        self.startPoint = source
        self.endPoint = target
        self.active = False
        self._lines = []

    def start(self):
        self.active = True
        physicsController.add(self)

    def stop(self):
        if self.active:
            anim = MultiParallelAnim([line for line, dt in self._lines], FadeOut, 0.8)
            anim += AnimCallable(physicsController.remove, self)
            self.startAnim(anim)
        self.active = False

    def clear(self):
        for line in self._lines:
            line[0].delete()

        self._lines.clear()
        self._x, self._y = self.startPoint.getPosition2D()
        self._accumulatedTime = 0

    def _calcTotalTime(self):
        return -(2 * self._factor) / -G

    def _calcHeightAtTime(self, t):
        return self._factor * t + -G * pow(t, 2) / 2.0

    def update_existing(self):
        start_pos = tuple(sum(x) for x in zip(self.startPoint.getPosition2D(), self._source_offset))
        self._x, self._y = start_pos
        start = start_pos
        end = tuple(sum(x) for x in zip(self.endPoint.getPosition2D(), self._target_offset))
        nx, ny = start_pos
        angle = math.radians(getAngleBetweenTwoPoints(start, end))
        dis = getDistanceBetweenTwoPoints(start, end)
        for line, dt in self._lines:
            distance = dis * dt / self._finalTime
            x = start[0] + distance * math.cos(angle)
            y = start[1] + distance * math.sin(angle)
            z = self._calcHeightAtTime(dt)
            line.position = (
             nx, ny, x, y + z)
            nx = x
            ny = y + z

    def update(self, dt):
        if self.active:
            start = tuple(sum(x) for x in zip(self.startPoint.getPosition2D(), self._source_offset))
            end = tuple(sum(x) for x in zip(self.endPoint.getPosition2D(), self._target_offset))
            distance = getDistanceBetweenTwoPoints(start, end) * self._accumulatedTime / self._finalTime
            a = getAngleBetweenTwoPoints(start, end)
            angle = math.radians(a)
            x = start[0] + distance * math.cos(angle)
            y = start[1] + distance * math.sin(angle)
            z = self._calcHeightAtTime(self._accumulatedTime)
            self._lines.append((
             pyglet.shapes.Line((self._x), (self._y), x, (y + z), width=2, color=(255, 0, 0), opacity=180, batch=(self.batch)),
             self._accumulatedTime))
            if self._accumulatedTime >= self._finalTime:
                self.stop()
                return
            self._x = x
            self._y = y + z
            self._accumulatedTime += dt * self._speed

    def draw(self, interp):
        self.update_existing()


class ThrowTarget(object):
    __doc__ = " All object that implements this... can be throw !"

    def __init__(self, object, target, speed=5, height=30, rotate=True):
        self.object = object
        self._position = self.object.getPosition2D()
        self._height = height
        self._speed = speed
        self._angle = math.radians(getAngleBetweenTwoPoints(object.getPosition2D(), target.getPosition2D()))
        self._distance = getDistanceBetweenTwoPoints(object.getPosition2D(), target.getPosition2D())
        self._elapsed = 0
        self._finalTime = self._calcThrowTime()
        if rotate is True:
            self.object.rotate(self.getTotalTime(), 1)
        self.defer = defer.Deferred()
        self.defer.addErrback(self._canceled)
        self.active = False

    def _canceled(self, _):
        return

    def start(self):
        self.active = True
        physicsController.add(self)

    def stop(self):
        self.active = False
        physicsController.remove(self)

    def cancel(self):
        if self.active:
            self.stop()

    def _calcThrowTime(self):
        return -(2 * self._height) / -G

    def _calcHeightAtTime(self, t):
        return self._height * t + -G * pow(t, 2) / 2.0

    def getTotalTime(self):
        """ If an external needs the total duration. """
        return self._finalTime / self._speed

    def update(self, dt):
        t = self._elapsed / self._finalTime
        distance = self._distance * t
        x = self._position[0] + distance * math.cos(self._angle)
        y = self._position[1] + distance * math.sin(self._angle)
        z = self._calcHeightAtTime(self._elapsed)
        self.object.setPosition(x, y, z)
        self._elapsed += dt * self._speed
        if self._elapsed >= self._finalTime:
            self.stop()
            self.defer.callback("stopped")


class ThrowTargetObject(object):
    __doc__ = " All object that implements this... can be throw !"

    def __init__(self, source, target, speed=5, height=30, rotate=True):
        self.source = source
        self.target = target
        self._position = self.source.getPosition2D()
        self._distance = getDistanceBetweenTwoPoints(self.source.getPosition2D(), self.target.getPosition2D())
        self._height = height
        self._speed = speed
        self._angle = math.radians(getAngleBetweenTwoPoints(self.source.getPosition2D(), self.target.getPosition2D()))
        self._elapsed = 0
        self._finalTime = self._calcThrowTime()
        if rotate is True:
            self.source.rotate(self.getTotalTime(), 1)
        self.defer = defer.Deferred()
        self.defer.addErrback(self._canceled)
        self.active = False

    def _canceled(self, _):
        return

    def start(self):
        self.active = True
        physicsController.add(self)

    def stop(self):
        self.active = False
        physicsController.remove(self)

    def cancel(self):
        if self.active:
            self.stop()

    def _calcThrowTime(self):
        return -(2 * self._height) / -G

    def _calcHeightAtTime(self, t):
        return self._height * t + -G * pow(t, 2) / 2.0

    def getTotalTime(self):
        """ If an external needs the total duration. """
        return self._finalTime / self._speed

    def update(self, dt):
        t = self._elapsed / self._finalTime
        sX, sY = self.source.getPosition2D()
        tX, tY = self.target.getPosition2D()
        distance = self._distance * t
        xDiff = (tX - sX) * t
        yDiff = (tY - sX) * t
        self._angle = math.radians(getAngleBetweenTwoPoints(self.source.getPosition2D(), self.target.getPosition2D()))
        x = sX + xDiff
        y = sY + yDiff
        z = self._calcHeightAtTime(self._elapsed)
        self.source.setPosition(x, y, z)
        self._elapsed += dt * self._speed
        if self._elapsed >= self._finalTime:
            self.stop()
            self.defer.callback("stopped")


class ThrowAnim(Animable):

    def init(self, source, endPos, duration=3):
        self.source = source
        self.startPos = source.getPosition2D()
        self.endPos = endPos
        self.speed = 40
        self._angle = math.radians(getAngleBetweenTwoPoints(source.getPosition2D(), endPos))
        self.distance = getDistanceBetweenTwoPoints(self.startPos, self.endPos)
        self._speedS = self.speed * math.sin(math.radians(33))
        self.duration = self._calcThrowTime()

    def _calcThrowTime(self):
        return -(2 * self._speedS) / -G

    def _calcHeightAtTime(self, dt):
        return self._speedS + -G * dt / 2.0

    def update(self, t):
        self.dt = 0.016666666666666666
        distance = self.distance * t
        z = self._calcHeightAtTime(t)
        x = self.startPos[0] + distance * math.cos(self._angle)
        y = self.startPos[1] + distance * math.sin(self._angle)
        self.source.setPosition(x, y, z)


class Fly(Throw):

    def __init__(self, object, duration=1.0, height=100):
        self.object = object
        angle = getAngleBetweenTwoPoints((0, self.object.getZ()), (0, height))
        self._angle = math.radians(angle)
        self._speed = 100
        self._speedS = self._speed * math.sin(self._angle)
        self._height = height
        self._duration = duration
        self._elapsedTime = 0

    def getTotalTime(self):
        return self._finalTime / 5.0

    def update(self, dt):
        distance = self._speedS * dt
        self.object.setPosition(self.object.getX(), self.object.getY(), self.object.getZ() + distance)
        if self._elapsedTime > self._duration:
            self.object.setZ(self._height)
            if self._height == 0:
                if not self.object.isFainted():
                    self.object.setAction(CreatureAction.STOP)
            self.stop()
        self._elapsedTime += dt

    def _calcThrowTime(self):
        return -(2 * self._speedS) / -G

    def _calcHeightAtTime(self, deltaTime):
        return self._speedS * deltaTime + -G * pow(deltaTime, 2) / 2.0


class Jump(Throw):

    def __init__(self, object, callback=None, speed=10):
        self.object = object
        self._position = self.object.getPosition2D()
        self._angle = math.radians(90)
        self._speed = speed
        self._speedS = self._speed * math.sin(self._angle)
        self._elapsedTime = 0
        self._finalTime = self._calcThrowTime()
        self._maxHeight = self._calcHeightAtTime(self._finalTime / 2.0)
        self.defer = defer.Deferred()
        self.active = False

    def start(self):
        self.active = True
        physicsController.add(self)

    def stop(self):
        physicsController.remove(self)
        self.active = False

    def cancel(self):
        if self.active:
            self.stop()
            if not self.defer.called:
                self.defer.cancel()

    def getTotalTime(self):
        return self._finalTime / 5.0

    def update(self, dt):
        z = self._calcHeightAtTime(self._elapsedTime)
        x, y = self.object.getPosition2D()
        self.object.setPosition(x, y, z)
        self._elapsedTime += dt * 5
        if self._elapsedTime > self._finalTime:
            self.object.setPosition(x, y, 0)
            self.stop()
            self.defer.callback("stopped")


class Knockback(Animable):

    def init(self, source, endPos, duration):
        self._scheduled = False
        self.anims = []
        self.target = None
        self._elapsed = 0
        self._done = False
        self.duration = None
        self.callables = []
        self.meta = False
        self.source = source
        self.startPos = source.getPosition()
        self.endPos = endPos
        self.speed = 40
        self.duration = duration

    def start(self):
        self.active = True
        physicsController.add(self)

    def stop(self):
        physicsController.remove(self)
        self.active = False

    def step(self, dt):
        self._elapsed += dt
        self.anim_update(min(1, self._elapsed / self.duration))

    def update(self, dt):
        """ Steps all of the anims playing on one renderer """
        self.step(dt)
        if self.done():
            self.stop()
            self.doCallbacks()

    def anim_update(self, t):
        x = self.startPos[0] + (self.endPos[0] - self.startPos[0]) * t
        y = self.startPos[1] + (self.endPos[1] - self.startPos[1]) * t
        self.source.setPosition(x, y, self.startPos[2])
        self.source.applyEnvironmentEffects()

    def draw(self, interp):
        return
