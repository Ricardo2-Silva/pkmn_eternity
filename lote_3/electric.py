# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\world\action\moves\electric.py
"""
Created on Feb 15, 2016

@author: Admin
"""
import time
from shared.container.skill import StaticEventSource
from shared.controller.net.packetStruct import RawUnpacker
from shared.service.geometry import getAngleBetweenTwoPoints
from shared.container.constants import CreatureAction, PointDataType, RefPointType
from client.data.world.animation import AnimType, Animation, AnimationEnd
from client.data.world.map import EffectData
from client.data.layer import LayerType
from client.control.world.map import SkillEffect, WeatherEffect, ImageEffect
from shared.container.db.point import PointHandler
from client.data.world.skill import ClientSkillUseInstance
import math, random
from twisted.internet import reactor
from client.control.system.background import backgroundController
from client.data.system.background import BackgroundData, BackgroundOption
from client.data.container.map import mapContainer
from client.render.cache import textureCache

class Thundershock(ClientSkillUseInstance):

    def process(self):
        direction = getAngleBetweenTwoPoints(self.char.getPosition2D(), self.data)
        self.char.setFacingNear(direction)
        self.char.playAction(CreatureAction.SHOCK, 0)
        bolt = SkillEffect(EffectData("232_[6]", (self.data), animation=Animation(delay=0.07), layerType=(LayerType.LAYERED), refPointType=(RefPointType.BOTTOMCENTER)))
        reactor.callLater(0.21000000000000002, self.areaEffect)

    def areaEffect(self):
        bolt = SkillEffect(EffectData("45_[3]", (self.data), animation=Animation(delay=0.07), layerType=(LayerType.LAYERED), refPointType=(RefPointType.CENTER)))


class Thunderwave(ClientSkillUseInstance):

    def process(self):
        direction = self.data
        self.char.setFacingNear(direction)
        self.char.playActionWithDelay(CreatureAction.SHOCK, 0.5, 0.07)
        self.initialPosition = self.char.getPositionInFront(direction, 5, offsetY=5)

        def wave():
            wave = SkillEffect(EffectData("98_[7]", (self.initialPosition), animation=Animation(delay=0.05, end=(AnimationEnd.STOP)), refPointType=(RefPointType.LEFTCENTER)))
            wave.setRotation(-direction)

        reactor.callLater(0.1, wave)


class Discharge(ClientSkillUseInstance):

    def process(self):
        x, y = self.data
        direction = getAngleBetweenTwoPoints(self.char.getPosition2D(), self.data)
        self.running = True
        self.char.setFacingNear(direction)
        self.char.playActionWithDelay(CreatureAction.SHOCK, self.skillInfo.duration, 0.07)
        self.startTime = time.time()
        StaticEventSource(self, x, y, 0, self.skillInfo.duration)
        self.start()

    def onSourceActivate(self, source, x, y, z, count):
        return

    def onSourceStop(self, source, result, x, y, z):
        self.char.getCastObject().cancelCast()

    def onDamageSourceReceived(self, targetId, targetIdRange, x, y, z, direction, radius, duration, timeStamp):
        bolt = SkillEffect(EffectData("44_[5]", (x, y), animation=Animation(delay=0.07, end=(AnimationEnd.STOP)), layerType=(LayerType.LAYERED),
          refPointType=(RefPointType.BOTTOMCENTER)))


class Thunder(ClientSkillUseInstance):

    def process(self):
        direction = getAngleBetweenTwoPoints(self.char.getPosition2D(), self.data)
        self.char.setFacingNear(direction)
        self.char.playAction(CreatureAction.SHOCK, 0)
        self.generateCloud()
        self.flashLightning()
        self.start()

    def flashLightning(self):
        bg = ImageEffect(EffectData((textureCache.getBackgroundColor((0, 0, 0))), position=(0,
                                                                                            0), layerType=(LayerType.LAYERED), refPointType=(RefPointType.BOTTOMLEFT)))
        (bg.setScales)(*mapContainer.getMapSize())
        bg.setAlpha(0)

        def removeBG(_):
            bg.delete()

        def fadeOut(_):
            b = bg.fadeOut(0.8)
            b.addCallback(removeBG)

        d = bg.fadeTo(0.3, 150)
        d.addCallback(fadeOut)
        for i in range(2):
            reactor.callLater(i * 0.5, self.fireBolt)

    def fireBolt(self):
        self.char.playAction(CreatureAction.SHOCK, 0)
        bolt = SkillEffect(EffectData("254_[10]_X", (self.data), animation=Animation(delay=0.05), layerType=(LayerType.LAYERED), refPointType=(RefPointType.BOTTOMCENTER)))

    def removeLightning(self):
        backgroundController.fadeOut("thunderskill", 0.8)

    def generateCloud(self):
        x, y = self.char.getPosition2D()
        effect = WeatherEffect(EffectData("cloud1_[1]", (
         x - 1100, y + 1000),
          refPointType=(RefPointType.TOPLEFT)))
        effect.setColor(0, 0, 0)
        effect.setAlpha(0)
        d = effect.fadeTo(0.3, 110)

        def fadeOut(result):
            effect.fadeOut(1.3)

        d.addCallback(fadeOut)
        effect.moveTo(2, x - 900, y + 1000)


class Thunderbolt(ClientSkillUseInstance):

    def process(self):
        direction = getAngleBetweenTwoPoints(self.char.getPosition2D(), self.data)
        self.char.setFacingNear(direction)
        self.char.playAction(CreatureAction.SHOCK, 0)
        x, y = self.data
        bolt = SkillEffect(EffectData("thunderbolt_[11]", (x, y - 10), animation=Animation(delay=0.07), layerType=(LayerType.LAYERED), refPointType=(RefPointType.BOTTOMCENTER), renderingOrder=0))
