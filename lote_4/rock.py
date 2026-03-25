# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\world\action\moves\rock.py
"""
Created on Feb 15, 2016

@author: Admin
"""
import time
from twisted.internet import reactor
from client.data.world.skill import ClientSkillUseInstance
from shared.container.constants import CreatureAction, RefPointType
import pyglet
from client.control.world.action.physics import Throw
from client.control.world.map import SkillEffect
from client.data.world.map import EffectData
from client.data.world.animation import AnimType, Animation, AnimationEnd
from client.control.world.action.moves.normal import Tackle
from shared.service.geometry import getAngleBetweenTwoPoints

class Rockpolish(ClientSkillUseInstance):

    def process(self):
        self.char.playAction(CreatureAction.WITHDRAW, 0.5)


class Magnitude(ClientSkillUseInstance):

    def process(self):
        self.char.playAction(CreatureAction.JUMP, 0.5)

    def onDamageSourceReceived(self, targetId, targetIdRange, x, y, z, direction, radius, duration, timeStamp):
        e = SkillEffect(EffectData("test_2", position=(
         x, y),
          refPointType=(RefPointType.CENTER),
          animation=Animation(delay=0.1, duration=duration),
          metafile=True))
        reactor.callLater(duration, e.delete)


class Rockthrow(ClientSkillUseInstance):

    def process(self):
        x, y = self.data
        direction = getAngleBetweenTwoPoints(self.char.getPosition2D(), self.data)
        self.char.setFacingNear(direction)
        self.char.playAction(CreatureAction.SPATK, 0.5)
        self.e = SkillEffect(EffectData("rock_throw", position=(self.char.getPosition2D()),
          refPointType=(RefPointType.CENTER),
          animation=Animation(delay=0.1, duration=0, end=(AnimationEnd.STOP)),
          shadow=True,
          metafile=True))
        self.throw = Throw(self.e, (x, y))
        self.throw.defer.addCallback(self.throwEnd)
        self.throw.start()

    def throwEnd(self, _):
        self.e.delete()
        e = SkillEffect(EffectData("rock_throw_hit", position=(self.e.getPosition2D()),
          refPointType=(RefPointType.CENTER),
          animation=Animation(delay=0.05, duration=0.5),
          shadow=False,
          metafile=True))


class Rollout(Tackle):
    return


class Rockslide(ClientSkillUseInstance):

    def process(self):
        x, y = self.data
        self.e = SkillEffect(EffectData("rock_throw", position=(self.char.getPosition2D()),
          refPointType=(RefPointType.CENTER),
          animation=Animation(delay=0.1, duration=0, end=(AnimationEnd.STOP)),
          shadow=True,
          metafile=True))
        self.t = Throw(self.e, (x, y))
        self.throw.defer.addCallback(self.throwEnd)
        self.throw.start()

    def throwEnd(self, _):
        self.e.hide()
        e = SkillEffect(EffectData("rock_throw_hit", position=(self.e.getPosition2D()),
          refPointType=(RefPointType.CENTER),
          animation=Animation(delay=0.05, duration=0.5, end=(AnimationEnd.STOP)),
          shadow=True,
          metafile=True))
