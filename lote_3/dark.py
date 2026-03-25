# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\world\action\moves\dark.py
"""
Created on Jul 11, 2016

@author: Admin
"""
from client.data.world.skill import ClientSkillUseInstance
from shared.controller.net.packetStruct import RawUnpacker
from shared.container.constants import CreatureAction
from client.control.world.map import Effect, SkillEffect
from client.data.world.map import EffectData
import pyglet
from twisted.internet import reactor

class Bite(ClientSkillUseInstance):

    def process(self):
        direction = self.data
        self.char.setFacingNear(direction)
        self.char.playAction(CreatureAction.BITE, 0.5)
        s = SkillEffect(EffectData("118_[16]", self.char.getPositionInFrontMiddle(direction, 10)))
        sprite = s.renderer.sprite
        sprite.scale = 0.5
        if direction < 90 or direction > 270:
            startFrame = 8
            endFrame = 11
        else:
            if direction > 90 or direction < 270:
                startFrame = 0
                endFrame = 3
        self.customAnimate(0.1, sprite, startFrame, endFrame)
        reactor.callLater(0.5, s.hide)

    def customAnimate(self, dt, sprite, startFrame, endFrame):
        sprite.setFrame(startFrame)
        pyglet.clock.schedule_interval(self._animate, dt, sprite, startFrame, endFrame)

    def _animate(self, dt, sprite, startFrame, endFrame):
        sprite.setFrame(sprite.currentFrame + 1)
        if sprite.currentFrame == endFrame:
            pyglet.clock.unschedule(self._animate)


class Crunch(Bite):
    return
