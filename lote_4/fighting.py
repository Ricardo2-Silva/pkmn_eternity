# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\world\action\moves\fighting.py
"""
Created on Jan 10, 2017

@author: Admin
"""
from client.data.world.skill import ClientSkillUseInstance
from shared.container.skill import StaticTickEventSource
from twisted.internet import reactor
from shared.container.constants import CreatureAction
from client.data.world.animation import AnimType, Animation, AnimationEnd
from client.control.world.map import Effect
from client.data.world.map import EffectData

class Doublekick(ClientSkillUseInstance):

    def process(self):
        self.direction = self.data
        self.char.setFacingNear(self.direction)
        StaticTickEventSource(self, 0, 0, 0, duration=0.5, count=2)
        self.start()

    def onSourceActivate(self, source, x, y, z, count):
        self.char.playAction(CreatureAction.KICK, 0)
        Effect(EffectData("normal_hit_[3]", (self.char.getPositionInFrontMiddle(self.direction, 10)[:2]), animation=Animation(delay=0.1, end=(AnimationEnd.STOP))))
