# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\world\action\moves\ground.py
"""
Created on Oct 25, 2017

@author: Admin
"""
from client.data.world.skill import ClientSkillUseInstance
from client.data.world.animation import AnimType
from client.data.world.map import EffectData
from client.control.world.map import SkillEffect
from shared.container.constants import CreatureAction, PointDataType
from shared.container.db.point import PointHandler
import time

class Earthquake(ClientSkillUseInstance):

    def process(self):
        self.direction = self.data
        self.char.setFacingNear(self.direction)
        self.char.playActionWithDelay(CreatureAction.SHOOT, 0.5, 0.07)
        self.pointHandler = PointHandler((PointDataType.LINEAR_LONG), speed=200, direction=(self.direction))
        self.timeBegin = time.time()
        self.initialPosition = self.char.getPositionInFront(self.direction, 30)
        self.initialPosition2 = self.char.getPositionInFront(self.direction, 30, 0, 10)
        self.save()
        self.runLoop(0.1, self.move)

    def getY(self):
        return 0

    def endFromCollision(self):
        self.endLoop()
        self.delete()

    def move(self):
        dt = time.time() - self.timeBegin
        if self.pointHandler.isOver(dt):
            dx, dy = self.pointHandler.last()
            self.endLoop()
            self.delete()
            return
        dx, dy = self.pointHandler.get(dt)
        x0, y0, z = self.initialPosition
        x1, y1, z = self.initialPosition2
        SkillEffect(EffectData("earthquake_[1]", (x1 + dx, y1 + dy), shadow=True, renderingOrder=(y1 + dy)))
        SkillEffect(EffectData("earthquake_[1]", (x0 + dx, y0 + dy), shadow=True, renderingOrder=(y0 + dy)))
