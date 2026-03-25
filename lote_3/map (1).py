# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\world\map.py
"""
Created on 18 juil. 2011

@author: Kami

Contains all map entities.

"""
import client.render.world.map as iRender
from client.control.world.object import WorldObject
from client.data.world.map import EmoteData, EffectData, WarpData
from shared.container.geometry import InterfacePositionable2D, InterfacePositionable3D
from client.control.service.session import sessionService
from client.data.utils.color import Color
from shared.container.constants import QuestStatus, StatusEffect, DamageNotificationTags, RefPointType
from client.data.world.animation import AnimType, Animation
import pyglet
from client.data.container.effects import effectContainer
import random
from twisted.logger import Logger
logging = Logger()

class Effect(WorldObject):
    renderClass = iRender.EffectRender

    def __init__(self, data):
        WorldObject.__init__(self, data)
        self.parent = None
        self.startVisible = False
        if isinstance(self, Effect):
            if data.attach:
                self.parent = data.attach
        if not data.permanent:
            effectContainer.effects.append(self)
        if self.parent:
            self.parent.addLinkedObject(self)
            self.offset = (data.x, data.y)
            self.updateFromObject()
            self.resetRenderState()

    def removeLink(self):
        if self.parent:
            self.parent.delLinkedObject(self)

    def updateMultiple(self, x, y, rotation=None, scale=None):
        self.data.setPosition(x, y, 0)
        InterfacePositionable3D.setPosition(self, x, y, 0)
        self.renderer.setMultipleAttributes(x, y, rotation, scale)

    def delete(self):
        try:
            super().delete()
        except AttributeError as err:
            logging.info(f"Error: Failed to delete effect {self.data.fileId}, it was already removed.")

        if not self.data.permanent:
            try:
                effectContainer.effects.remove(self)
            except ValueError:
                print(f"Warn: Effect '{self.data.fileId}' was already purged from effects container.")

    def canHide(self):
        return self.visible

    def canShow(self):
        return not self.visible

    def fadeOut(self, duration=2):
        return self.renderer.fadeOut(duration)

    def fadeIn(self, duration=2):
        return self.renderer.fadeTo(duration, 255)

    def fadeTo(self, duration=2, toAlpha=0.0, startAlpha=None):
        return self.renderer.fadeTo(duration, toAlpha, startAlpha)

    def fadeColor(self, duration, rgb, startColor=None):
        return self.renderer.fadeColor(duration, rgb, startColor)

    def hide(self, dt=None):
        WorldObject.hide(self)

    def setScale(self, scale):
        self.renderer.setScale(scale)

    def setScales(self, scaleX, scaley):
        self.renderer.setScales(scaleX, scaley)

    def grow(self, duration, startScale=0.5, endScale=1.0, reset=True):
        return self.renderer.grow(duration, startScale, endScale, reset)

    def growSeparate(self, duration, startX=0.5, startY=0.5, endX=1.0, endY=1.0, reset=True):
        return self.renderer.growSeparate(duration, startX, startY, endX, endY, reset)

    def flash(self, duration, scale=4.0):
        return self.renderer.flash(duration, scale)

    def setAlpha(self, alpha):
        self.renderer.setAlpha(alpha)

    def rotate(self, duration=1, speed=1):
        """Speed not used, by needs to be specified because of Throw function. (Rock Throw)"""
        self.renderer.rotate(duration)

    def spin(self, duration, spins):
        self.renderer.spin(duration, spins)

    def pulse(self, pulseCount, duration, scale=1.2):
        return self.renderer.pulse(pulseCount, duration, scale)

    def pulseSeparate(self, pulseCount, duration, scale_x=1.2, scale_y=1.2):
        return self.renderer.pulseSeparate(pulseCount, duration, scale_x, scale_y)

    def pulseAlpha(self, duration, pulseCount, alpha):
        self.renderer.pulseAlpha(pulseCount, duration, alpha)

    def moveTo(self, duration, x, y, extension='constant'):
        return self.renderer.moveTo(duration, x, y, extension)

    def setRotation(self, value):
        self.renderer.setRotation(value)

    def setColor(self, r, g, b):
        self.renderer.setColor(r, g, b)

    def updateFromObject(self):
        (self.setPosition)(*[x + y for x, y in zip(self.parent.getPosition2D(), self.offset)])

    def updateFromObjectNoRender(self):
        (self.setPositionNoRender)(*[x + y for x, y in zip(self.parent.getPosition2D(), self.offset)])

    def updateFromObjectRender(self, interp):
        self.setRenderPosition(interp)

    def stopAnimation(self):
        self.renderer.stopAnimation()

    def startAnimation(self):
        self.renderer._checkAnimation()

    def isAnimating(self):
        return self.renderer._animating

    def setShader(self, shader):
        self.renderer.setShader(shader)


class SkillEffect(Effect):
    renderClass = iRender.SkillRender


class CustomEffect(Effect):
    renderClass = iRender.CustomEffectRender


class ImageEffect(Effect):
    renderClass = iRender.CustomEffectImageRender


class MultiImageEffect(Effect):
    renderClass = iRender.MultiImageEffectRender


class ShaderEffect(Effect):
    renderClass = iRender.ShaderEffectRender


class LineEffect(Effect):
    renderClass = iRender.LineEffectRender


class MapEffect(Effect):
    renderClass = iRender.MapEffectRender


class EnvironmentGrass(Effect):
    renderClass = iRender.GrassEffectRender

    def __init__(self, char):
        x, y = char.getPosition2D()
        self.char = char
        Effect.__init__(self, EffectData("grass_[5]", (
         x, y),
          animation=Animation(duration=0, delay=0.15, removal=False),
          hidden=True,
          refPointType=(RefPointType.BOTTOMCENTER),
          attach=char,
          renderingOrder=(-1)))

    def updateFromObject(self):
        (self.setPosition)(*self.char.getPosition2D())

    def updateFromObjectNoRender(self):
        x, y = self.char.getPosition2D()
        self.setPositionNoRender(x, y, y)


class AuraSelect(Effect):

    def __init__(self):
        self.char = None
        self.offset = (0, 0)
        data = EffectData("aura_[2]",
          (0, 0),
          animation=Animation(delay=0.3, duration=0, removal=False),
          hidden=True,
          renderingOrder=15)
        data.permanent = True
        Effect.__init__(self, data)
        self.setAlpha(150)

    def setChar(self, char):
        if char == self.char:
            return False
        else:
            if self.parent:
                self.parent.delLinkedObject(self)
            self.char = char
            self.parent = char
            self.data.attach = char
            self.setColorFromChar(char)
            self.parent.addLinkedObject(self)
            self.updateFromObject()
            self.resetRenderState()
            return True

    def removeChar(self):
        self.char = None
        self.data.attach = None
        if self.parent:
            self.parent.delLinkedObject(self)
        self.parent = None

    def setColorFromChar(self, char):
        """ Depending on the char type, it sets a specific color. """
        if sessionService.isClientChar(char):
            (self.setColor)(*Color.LIGHT_BLUE)
        else:
            (self.setColor)(*Color.LIGHT_YELLOW)

    def hide(self, dt=None):
        Effect.hide(self)
        if not sessionService.isSelected(self.char):
            self.startVisible = False

    def updatePosition(self):
        return

    def show(self):
        self.updateFromObject()
        self.resetRenderState()
        Effect.show(self)
        if sessionService.isSelected(self.char):
            self.startVisible = True

    def updateFromObject(self):
        (self.setPosition)(*self.parent.getBottomCenter())

    def updateFromObjectNoRender(self):
        (self.setPositionNoRender)(*self.parent.getBottomCenter(), *(self.parent.getY(),))

    def updateFromObjectRender(self, interp):
        self.setRenderPosition(interp)


flagToIcon = {(DamageNotificationTags.MISS): "x_[9]", 
 (DamageNotificationTags.CRITICAL): "sword_[13]", 
 (DamageNotificationTags.IMMUNE): "shield_[13]", 
 (DamageNotificationTags.RESIST): "arrow_down_[11]", 
 (DamageNotificationTags.EFFECTIVE): "effective_[8]"}

class DamageNotificationIcon(Effect):
    __doc__ = " Displays visually in text what damage notification there is, even though Damage Notification Tags have multiple packed in, this label will only display one at a time. "

    def __init__(self, char, damageFlag):
        x, y = char.getProjection2D()
        Effect.__init__(self, EffectData((flagToIcon[damageFlag]), (x, y + char.getHeight()), animation=Animation(delay=0.1, removal=False)))
        self.startVisible = True
        self.char = char
        directionRandomness = random.choice((-self.getWidth(), self.getWidth() / 2))
        self.renderer.moveTo(2, x + directionRandomness, y + self.char.getHeight() + self.getHeight() + 15)
        callback = self.fadeOut(2)
        callback.addCallback(self.permanentRemoval)

    def permanentRemoval(self, result):
        self.delete()

    def updateFromObject(self):
        return

    def updateFromObjectNoRender(self):
        return

    def updateFromObjectRender(self, interp):
        return


class QuestStatusEffect(Effect):

    def __init__(self, char):
        x, y = char.getProjection2D()
        self.char = char
        Effect.__init__(self, EffectData("available_[1]", (
         x, y)))
        self.char.addLinkedObject(self)
        self.offset = (0, self.char.getHeight() + self.getHeight())
        self.startVisible = True
        self.updateFromObject()
        self.resetRenderState()

    def updateStatus(self, status):
        if status != QuestStatus.NONE:
            if not self.visible:
                self.show()
        if status == QuestStatus.AVAILABLE:
            self.renderer.updateTexture("available_[1]")
        elif status == QuestStatus.INCOMPLETE:
            self.renderer.updateTexture("incomplete_[1]")
        elif status == QuestStatus.COMPLETE:
            self.renderer.updateTexture("complete_[1]")
        elif self.visible:
            self.hide()

    def updateFromObject(self):
        (self.setPosition)(*[x + y for x, y in zip(self.char.getBottomCenter(), self.offset)])

    def updateFromObjectNoRender(self):
        self.setPositionNoRender([x + y for x, y in zip(self.char.getBottomCenter(), self.offset)])


class StatusEffectObject(Effect):
    renderClass = iRender.EffectRender

    def __init__(self, status, char):
        x, y = char.getProjection2D()
        delay = 0.1
        renderingOrder = -1
        if status == StatusEffect.CONFUSED:
            fileId = "confusion_[4]"
            yPos = char.getHeight()
        elif status == StatusEffect.BURN:
            fileId = "burn_[7]"
            yPos = char.getHeight()
        elif status == StatusEffect.FREEZE:
            fileId = "frozen_[6]"
            yPos = char.getHeight() / 2
        elif status == StatusEffect.SLEEP:
            fileId = "sleep_[10]"
            yPos = char.getHeight()
        elif status == StatusEffect.POISON:
            fileId = "poison_[15]"
            yPos = char.getHeight()
        elif status == StatusEffect.PARALYSIS:
            fileId = "paralysis_[7]"
            yPos = char.getHeight() // 2
        elif status == StatusEffect.STUN:
            fileId = "stun_[4]"
            yPos = char.getHeight()
        else:
            if status == StatusEffect.ROOT:
                fileId = "immobilize_[5]"
                yPos = 0
                renderingOrder = 2
        self.char = char
        self.offset = (
         0, yPos)
        Effect.__init__(self, EffectData(fileId, (
         0, yPos),
          animation=Animation(delay=delay, duration=0),
          attach=char,
          renderingOrder=renderingOrder))
        self.startVisible = True
        self.updateFromObject()
        self.resetRenderState()

    def _removeSchedules(self):
        if self.visible:
            if not self.renderer.fading:
                self.hide()
        return False

    def show(self):
        Effect.show(self)

    def hide(self, dt=None):
        WorldObject.hide(self)

    def updateFromObject(self):
        (self.setPosition)(*[x + y for x, y in zip(self.char.getPosition2D(), self.offset)])

    def updateFromObjectNoRender(self):
        (self.setPositionNoRender)(*[x + y for x, y in zip(self.char.getPosition2D(), self.offset)])


class Emote(Effect):
    renderClass = iRender.EmoteRender

    def __init__(self, emote, char):
        self.char = char
        Effect.__init__(self, EmoteData((emote.value), (
         5, self.char.getHeight() / 2 + 10),
          animation=Animation(duration=0.8, removal=False),
          attach=char,
          renderingOrder=(-3)))
        self.offset = (
         5, self.char.getHeight() / 2 + 10)
        pyglet.clock.schedule_once(self.hide, 2)
        self.updateFromObject()
        self.resetRenderState()

    def updateEmote(self, emote):
        """ Here we update the sprite with a new image, reschedule to hide """
        pyglet.clock.unschedule(self.hide)
        self.updateFromObject()
        self.resetRenderState()
        self.renderer.updateEmote(emote.value)
        if not self.visible and not self.renderer.fading:
            self.show()
        else:
            self.renderer.replayAnimation()
        pyglet.clock.schedule_once(self.hide, 2)

    def show(self):
        WorldObject.show(self)

    def hide(self, dt=None):
        pyglet.clock.unschedule(self.hide)
        WorldObject.hide(self)

    def updateFromObject(self):
        (self.setPosition)(*[x + y for x, y in zip(self.char.getPosition2D(), self.offset)])

    def updateFromObjectNoRender(self):
        (self.setPositionNoRender)(*[x + y for x, y in zip(self.char.getPosition2D(), self.offset)])


class WeatherEffect(Effect):
    renderClass = iRender.WeatherEffectRender

    def __init__(self, data):
        WorldObject.__init__(self, data)
        self.parent = None
        self.startVisible = False

    def updateTexture(self, filename):
        self.data.fileId = filename
        self.renderer.updateTexture()

    def getAnimationSpeed(self):
        return 0.1


class WarpPoint(Effect):

    def __init__(self, *args, **kwargs):
        (Effect.__init__)(self, *args, **kwargs)
        if self.data.fileId == "warp_[6]":
            self.setAlpha(254)


class MapObject(WorldObject):
    __doc__ = " Control view of an object. Object have shadows, though they can be disabled. "
    renderClass = iRender.MapObjectRender

    def __init__(self, data):
        WorldObject.__init__(self, data)

    def disableShadow(self):
        if not self.data.haveShadow:
            raise Exception("Shadow are already disabled for this object.")
        self.data.haveShadow = False
        self.renderer.disableShadow()

    def enableShadow(self):
        if self.data.haveShadow:
            raise Exception("Shadow are already enabled for this object.")
        self.data.haveShadow = True
        self.renderer.enableShadow()

    def isAnimated(self):
        return self.renderer.sheet.isAnimated()

    def stopAnimation(self):
        self.renderer.stopAnimation()

    def startAnimation(self):
        self.renderer._checkAnimation()


class MapObjectShadow(MapObject):
    renderClass = iRender.MapShadowObjectRender


class MapRect(InterfacePositionable2D):
    __slots__ = []

    def __init__(self, x, y, width, height):
        InterfacePositionable2D.__init__(self)
        self.setSize(width, height)
        self.setPosition(x, y)
        self.collision_radius = max(width, height)


class MapWall(MapRect):
    __doc__ = " Define a zone with a specific ground level. "
    __slots__ = ["wallHeight"]

    def __init__(self, x, y, width, height, wallHeight):
        self.wallHeight = wallHeight
        MapRect.__init__(self, x, y, width, height)


class MapGround(MapRect):
    __doc__ = " Define a zone with a specific ground type. "
    __slots__ = ["groundType"]

    def __init__(self, x, y, width, height, groundType):
        self.groundType = groundType
        MapRect.__init__(self, x, y, width, height)
