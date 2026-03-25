# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\world\action\moves\flying.py
"""
Created on Feb 15, 2016

@author: Admin
"""
import random, pyglet
from client.control.world.map import Effect
from client.data.world.animation import Animation
from client.data.world.map import EffectData
from client.data.world.skill import ClientSkillUseInstance
from shared.container.constants import CreatureAction, RefPointType
from shared.container.skill import LinearEventSource
top = (0, 1, 2, 3, 2, 1)
middle = (4, 5, 6, 7, 6, 5)
bottom = (8, 9, 10, 11)
start = tuple(range(8))
tippytop = tuple(range(12)) + tuple(reversed(range(12)))

class Gust(ClientSkillUseInstance):
    delay = 0.02

    def process(self):
        direction = self.data
        self.char.setFacingNear(direction)
        self.char.playActionWithDelay(CreatureAction.SPATK, 0.5, 0.07)
        self.initialPosition = self.char.getPosition2D()
        self.gusts = []
        self.source = LinearEventSource(self, *(self.initialPosition), **{'direction':direction,  'speed':50,  'distance':100})
        self.start()

    def onSourceActivate(self, source, x, y, z, count):
        self.spawnGust()

    def spawnGust(self):
        pyglet.clock.schedule_once(self._createGust, 0, 0, start, 0)
        pyglet.clock.schedule_once(self._createGust, self.delay * 12, 6, middle, 0)
        pyglet.clock.schedule_once(self._createGust, self.delay * 17, 2 * random.randint(4, 6), top, 0)
        pyglet.clock.schedule_once(self._createGust, self.delay * 21, 18, middle, 0)
        pyglet.clock.schedule_once(self._createGust, self.delay * 29, 28, bottom, 0)

    def _createGust(self, dt, i, frames, duration):
        x, y = self.initialPosition[0], self.initialPosition[1]
        gust = Effect(EffectData("gust_[12]", (
         x, y),
          animation=Animation(frames=frames, delay=0.05, duration=duration),
          refPointType=(RefPointType.CENTER),
          renderingOrder=(self.initialPosition[1] - i),
          hidden=True))
        gust.adjust = i
        self.gusts.append(gust)

    def onSourceMove(self, source, x, y):
        for gust in self.gusts:
            gust.setPosition(x, y + gust.adjust)
            if not gust.visible:
                gust.show()

    def onSourceStop(self, source, result, x, y, z):
        for gust in self.gusts:
            if gust.visible:
                gust.delete()
