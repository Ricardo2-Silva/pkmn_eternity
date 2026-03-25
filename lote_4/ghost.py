# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\world\action\moves\ghost.py
"""
Created on Sep 22, 2017

@author: Admin
"""
from client.data.world.skill import ClientSkillUseInstance
from shared.container.constants import CreatureAction, RefPointType
import pyglet
from client.control.world.action.physics import Throw
from client.control.world.map import SkillEffect, ShaderEffect
from client.data.world.map import EffectData
from client.data.world.animation import AnimType, Animation
from client.control.world.action.moves.normal import Tackle
from client.data.container.char import charContainer
from client.data.layer import LayerType
from shared.container.skill import StaticEventSource
from shared.service.geometry import getAngleBetweenTwoPoints
from shared.service.direction import directionService
from client.control.system.anims import ScaleBy, ScaleTo, AnimCallable
from client.control.system.background import backgroundController, Background
from client.data.system.background import BackgroundData
from client.data.utils.color import Color
from client.render.shader.default_sprite import ripple_shader
from twisted.internet import reactor

class Astonish(ClientSkillUseInstance):

    def process(self):
        self.char.playAction(CreatureAction.SPATK, 0.5)

    def onDamageSourceReceived(self, targetId, targetIdRange, x, y, z, direction, radius, duration, timeStamp):
        char = charContainer.getCharById(targetId, targetIdRange)
        if char:
            s = SkillEffect(EffectData("astonish_[2]", position=(char.getPosition2D()), animation=Animation(delay=0.1)))


class Curse(ClientSkillUseInstance):

    def process(self):
        self.char.playAction(CreatureAction.SHOOT, 0.5)
        char = charContainer.getCharById(self.data[0], self.data[1])
        if char:
            x, y = char.getPosition2D()
            direction = getAngleBetweenTwoPoints(self.char.getPosition2D(), (x, y))
            self.char.setFacingNear(direction)
            s = SkillEffect(EffectData("curse_ghost_end", attach=char, refPointType=(RefPointType.BOTTOMCENTER), animation=Animation(delay=0.05), metafile=True))
            s.moveTo(1, x, y - char.getHeight())
        s = SkillEffect(EffectData("curse_ghost_start", attach=(self.char), position=(0,
                                                                                      -20), refPointType=(RefPointType.CENTER), animation=Animation(delay=0.08), renderingOrder=(-1), metafile=True))


class Lick(ClientSkillUseInstance):

    def process(self):
        direction = self.data
        self.char.setFacingNear(direction)
        self.char.playAction(CreatureAction.LICK, 0.5)
        if direction < 90 or direction > 270:
            flip_x = False
        else:
            if direction > 90 or direction < 270:
                flip_x = True
        SkillEffect(EffectData("lick_[4]", (self.char.getPositionInFrontMiddle(direction, 15)[:2]),
          animation=Animation(delay=0.05),
          refPointType=(RefPointType.BOTTOMCENTER),
          flip_x=flip_x))


nightshadeBackground = BackgroundData("nightshade", color=(Color.RED), alpha=50)

class Nightshade(ClientSkillUseInstance):

    def process(self):
        self.char.playAction(CreatureAction.SPATK, 2)
        self.effect = None
        StaticEventSource(self, *self.char.getPosition(), *(self.skillInfo.duration,))
        self.start()

    def onSourceActivate(self, source, x, y, z, count):
        self.createShade()

    def onExpired(self):
        if self.effect.visible:
            self.effect.delete()

    def createShade(self):
        x, y = self.char.getPosition2D()
        self.effect = ShaderEffect(EffectData("lib/skills/effects/nightshade_[1].png", position=(self.char.getPosition2D()), refPointType=(RefPointType.CENTER), renderingOrder=(y + 300)))
        self.effect.setScale(2.2)
        self.effect.renderer.setShader(ripple_shader)
