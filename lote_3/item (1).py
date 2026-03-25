# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\world\item.py
"""
Created on 19 juil. 2011

@author: Kami
"""
import client.render.world.item as iRender
from client.control.world.action.physics import Throw
from twisted.internet import reactor
from client.data.DB import itemDB
from client.control.world.char import BasicCharObject
from client.data.container.map import mapContainer
import pyglet
from client.control.system.sound import CharSoundPlayer
from client.data.container.effects import effectContainer
from shared.container.constants import RefPointType
from client.control.system.anims import AnimCallable, Delay
from twisted.internet import defer

class Item(BasicCharObject):
    renderClass = iRender.ItemRender
    referencePoint = RefPointType.BOTTOMCENTER

    def __init__(self, data, *args):
        (BasicCharObject.__init__)(self, data, *args)
        self.followTarget = None
        self.throw = None

    @property
    def name(self):
        return self.data.name

    def rotate(self, duration, speed):
        self.renderer.rotate(duration, speed)

    def hide(self, dt=None):
        if self.throw:
            self.throw.cancel()
        pyglet.clock.unschedule(self.hide)
        BasicCharObject.hide(self)

    def getIdRange(self):
        return self.data.getIdRange()

    def getId(self):
        return self.data.getId()

    def stopThrow(self):
        if self.throw:
            self.throw.stop()

    def throws(self, toPosition, angle=33, weight=45, speed=5, rotate=True):
        self.renderer.setRenderingOrder(int(min(self.getPosition()[1], toPosition[1])))
        self.throw = Throw(self, toPosition, angle, weight, speed, rotate)
        self.throw.defer.addCallback(self.throwEnd)
        self.throw.start()
        return self.throw.defer

    def throwEnd(self, _):
        x, y = self.getPosition2D()
        self.renderer.setRenderingOrder(y)
        self.renderer.setOnGround(mapContainer.getAccumulatedGroundTypeAtPosition(self.data.map, x, y))

    def hasTarget(self):
        return False


class ItemDrop(Item):
    renderClass = iRender.ItemDropRender

    def __init__(self, data, *args):
        (BasicCharObject.__init__)(self, data, *args)
        self.followTarget = None
        self.throw = None


class WorldItem(Item):

    def __init__(self, data, *args):
        (Item.__init__)(self, data, *args)


class Ball(Item):
    renderClass = iRender.BallRender
    referencePoint = RefPointType.CENTER

    def __init__(self, data, *args):
        (Item.__init__)(self, data, *args)
        self.sound = CharSoundPlayer()

    def hide(self, dt=None):
        Item.hide(self, dt)

    def releasePokemon(self):
        self.opens()
        self.waitAndRemove(2)

    def opens(self):
        d = defer.Deferred()
        self.renderer.setFrame(1)
        pyglet.clock.schedule_once(self.setFrame, 0.05, 2)
        self.sound.playSound("Ball Open")
        reactor.callLater(0.7, d.callback, None)
        return d

    def capture(self):
        d = self.opens()
        d.addCallback(self.close)
        return d

    def close(self, _):
        self.renderer.setFrame(1)
        pyglet.clock.schedule_once(self.setFrame, 0.05, 0)

    def setFrame(self, dt, frameIdx):
        self.renderer.setFrame(frameIdx)

    def captureSuccess(self, times):
        anim = self.renderer.tremble(times)
        anim += AnimCallable(self.renderer.flashColor, 255, 0, 0)
        anim += AnimCallable(self.sound.playSound, "LevelUp")
        anim += AnimCallable(self.waitAndRemove, 3)

    def captureFail(self, times):
        anim = self.renderer.tremble(times)
        anim += AnimCallable(self.opens)
        return anim

    def captureRefused(self, toPosition):
        self.throws(toPosition)
        self.waitAndRemove(5)

    def waitAndRemove(self, seconds):
        anim = Delay(seconds)
        anim += AnimCallable(self.fadeAndDelete)
        self.startAnim(anim)

    def fadeAndDelete(self):
        d = self.renderer.fadeOut(2)

        def deletion(_):
            self.delete()

        d.addCallback(deletion)

    def tremble(self, shakes):
        self.renderer.tremble(shakes)
