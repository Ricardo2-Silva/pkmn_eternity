# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\render\gui\sheet.py
"""
Created on May 31, 2016

@author: Admin
"""
from client.render.gui.core import AbstractRender
from client.control.world.animation import animationManager
from shared.container.constants import RefPointType, CreatureAction, PlayerAction
import pyglet
from shared.service.direction import directionService
from shared.service.utils import inRange
from client.data.world.char import SkinTone
from client.render.sprite import GUIPygletSheet
base_dt = 0.016666666666666666

def getShadowPosition(original, shadow, referencePoint):
    """ Takes the position and makes it center. """
    offx, offy = (0, 0)
    if referencePoint & RefPointType.CENTERX:
        offx = 0
    if referencePoint & RefPointType.CENTERY:
        offy = original.width / 2 - shadow.width / 2
    if referencePoint & RefPointType.LEFT:
        offx = original.width / 2 - shadow.width / 2
    if referencePoint & RefPointType.TOP:
        offy = shadow.height / 2
    if referencePoint & RefPointType.RIGHT:
        offx = shadow.right
    if referencePoint & RefPointType.BOTTOM:
        offy = -(shadow.height / 2)
    return (offx, offy)


class SheetWidgetRender(AbstractRender):

    def _create(self):
        self.sprite = GUIPygletSheet((self.widget.getSheet()), group=(self.widget.group),
          batch=(self.widget.batch))
        return self.sprite

    def setAlpha(self, alpha):
        self.sprite.setAlpha(alpha)

    def setColor(self, r, g, b):
        self.sprite.setColor(r, g, b)

    def getSize(self):
        return self.sprite.getSize()

    def setScale(self, scale):
        self.sprite.scale = scale
        if self.shadowSprite:
            self.shadowSprite.scale = scale

    def refresh(self):
        self.sprite.setSheet(self.widget.getSheet())
        self.updatePosition()

    def updatePosition(self):
        (self.sprite.setPosition)(*self.widget.position)

    def updateSize(self):
        return

    def initiate(self):
        (self._addSprites)(*self._create())


class PokemonWidgetRender(SheetWidgetRender):

    def _create(self):
        self.rendererAction = CreatureAction.WALK
        self.facing = 90
        self._currentFlip = 0
        self._currentFrame = 0
        self._currentFrameIndex = 0
        self._offset = [0, 0]
        self._shadowOffset = [0, 0]
        self._currentFlip = self._getFlip()
        self.sprite = GUIPygletSheet((self.widget.charSheet), group=(self.widget.group),
          batch=(self.widget.batch))
        self.sprite.setTransformation((self.widget.charSheet), 0, 0, flip_x=(self._currentFlip))
        self.sprite.setFrame(self._currentFrame)
        if self.widget.shadow:
            self.shadowSprite = self._createShadow(self.widget.charSheet, self.widget.group, self.widget.batch)
            sprites = [self.shadowSprite, self.sprite]
        else:
            sprites = [
             self.sprite]
            self.shadowSprite = False
        return sprites

    def animate(self):
        if not inRange(self._currentFrameIndex, self._getMinFrame(), self._getMaxFrame()):
            self._currentFrameIndex = 0
        else:
            self._currentFrameIndex += 1
        self.setFrame(self.widget.frameInfo[self.rendererAction]["dir"][directionService.facingToIndex(self.facing)]["fr"][self._currentFrameIndex])

    def _createShadow(self, sheet, group, batch, referencePoint=RefPointType.CENTER, flip_x=False, frame=0):
        """ Add a shadow to the sprite. """
        shadowSprite = GUIPygletSheet(sheet, group=(self.widget.group),
          batch=(self.widget.desktop.transparent))
        shadowSprite.setTransformation(sheet, 0, 0, flip_x=flip_x, flip_y=True)
        shadowSprite.setFrame(frame)
        shadowSprite.setRGBA(0, 0, 0, 50)
        shadowSprite.setScale(0.95, 0.4)
        shadowSprite.offset = getShadowPosition(sheet.grid[frame], shadowSprite, referencePoint)
        return shadowSprite

    def setFacing(self, facing):
        if not facing is not None:
            raise AssertionError("Setting wrong value to char facing.")
        elif not self.facing != facing:
            raise AssertionError("Trying to set the same facing two times.")
        self.facing = facing
        self._refreshCurrentFrame()

    def getActionDuration(self, action):
        return self.widget.frameInfo[action]["dir"][directionService.facingToIndex(self.facing)]["t"]

    def _getMinFrame(self):
        """ Return the minimal frame for the current action and facing. """
        return 0

    def getFrameNumber(self):
        """ Return the number of frames for this animation. """
        return self._getMaxFrame() - self._getMinFrame()

    def _getFlip(self):
        """ Return the flip """
        return self.widget.frameInfo[self.rendererAction]["dir"][directionService.facingToIndex(self.facing)]["fr"][self._currentFrameIndex]["f"]

    def _getMaxFrame(self):
        return len(self.widget.frameInfo[self.rendererAction]["dir"][directionService.facingToIndex(self.facing)]["fr"]) - 1

    def stopAnimation(self):
        pyglet.clock.unschedule(self._playAnimation)

    def loopAnimation(self, duration):
        self.setAction(None, self.rendererAction)

    def _setRenderAction(self, action):
        if action > 50:
            action = CreatureAction.toRenderAction[action]
        self.rendererAction = action

    def setAction(self, oldAction, action):
        """ Set the action only. Do not play it. """
        self._setRenderAction(action)
        self.updateSpriteAction()
        pyglet.clock.unschedule(self._playAnimation)
        if action > CreatureAction.STOP:
            self._setCurrentFrame(1)
            self._next_dt = self.frames[1]["d"] * base_dt
            pyglet.clock.schedule_once(self._playAnimation, self._next_dt)

    @property
    def frameDuration(self):
        return self.widget.frameInfo[self.rendererAction]["dir"][directionService.facingToIndex(self.facing)]["fr"][self._currentFrameIndex]["d"] * base_dt

    @property
    def frames(self):
        return self.widget.frameInfo[self.rendererAction]["dir"][directionService.facingToIndex(self.facing)]["fr"]

    def _stopAnimation(self, dt):
        pyglet.clock.unschedule(self._playAnimation)

    def _playAnimation(self, dt):
        newFrame = (self._currentFrameIndex + 1) % len(self.frames)
        self._setCurrentFrame(newFrame)
        frameDuration = self.frameDuration
        duration = frameDuration - (self._next_dt - dt)
        duration = min(max(0, duration), frameDuration)
        pyglet.clock.schedule_once(self._playAnimation, duration)
        self._next_dt = duration

    def _setCurrentFrame(self, frameNumber):
        frame = self.frames[frameNumber]
        self._currentFrameIndex = frameNumber
        self.setFrame(frame)

    def _arrangeSprites(self):
        """ Arranges the sprites so that they get cropped and flipped """
        self._currentFlip = self._getFlip()
        self.sprite.setTransformation((self.widget.charSheet), 0, 0, flip_x=(self._currentFlip))
        if self.shadowSprite:
            self.shadowSprite.setTransformation((self.widget.charSheet), 0, 0, flip_x=(self._currentFlip), flip_y=True)

    def updateSpriteAction(self):
        self._refreshCurrentFrame()

    def setFrame(self, frame):
        if self._currentFlip != frame["f"]:
            self._currentFlip = frame["f"]
            self._arrangeSprites()
        self._offset = frame["o"]
        self._shadowOffset = frame["s"]
        self.sprite.setFrame(frame["i"])
        if self.shadowSprite:
            self.shadowSprite.setFrame(frame["i"])
        self.updatePosition()

    def _refreshCurrentFrame(self):
        self.setFrame(self.frames[self._currentFrameIndex])

    def updatePosition(self):
        x, y = self.widget.position
        self.sprite.setPosition(x + self._offset[0], y - self.sprite.height - 8 + self._offset[1])
        if self.shadowSprite:
            self.shadowSprite.setPosition(x + self._shadowOffset[0], y - self.shadowSprite.height - self._shadowOffset[1])


class TrainerWidgetRender(SheetWidgetRender):

    def _create(self):
        SheetWidgetRender._create(self)
        self.sprite.setFrame(8)
        return [self.sprite]

    def animate(self):
        self.sprite.nextFrame()

    def stopAnimation(self):
        if self.duration:
            animationManager.unRegister(self, self.duration)

    def loopAnimation(self, duration):
        self.duration = duration
        animationManager.register(self, duration)


class NewTrainerWidgetRender(SheetWidgetRender):

    def initiate(self):
        self._renderAction = self.widget.action
        self.currentFrame = 0
        self.scale = 1
        self.direction = directionService.facingToIndex(directionService.DOWN)
        self.hairOffset = (0, 0)
        (self._addSprites)(*self._create())
        self.setFrame(self.widget.frameInfo["actions"][self._renderAction][self.direction][0])

    def setDirection(self, direction):
        self.direction = directionService.facingToIndex(direction)

    def setAction(self):
        self._renderAction = self.widget.action
        self.updatePosition()
        if self.widget.action in (PlayerAction.SWIMMING, PlayerAction.STOP_SWIM):
            self.clotheSprite.setAlpha(0)
            self.clotheMaskSprite.setAlpha(0)
            self.swimSprite.setAlpha(255)
        else:
            self.clotheSprite.setAlpha(255)
            self.clotheMaskSprite.setAlpha(255)
            self.swimSprite.setAlpha(0)

    def setBodyType(self):
        self.bodySprite.setSheet(self.widget.bodySheet)
        (self.bodySprite.setColor)(*SkinTone.rgb[self.widget.skintone])
        self.eyesSprite.setSheet(self.widget.eyesSheet)
        self.setFrame(self.widget.frameInfo["actions"][self._renderAction][self.direction][self.currentFrame])
        self.updatePosition()

    def setClothes(self):
        self.clotheSprite.setSheet(self.widget.clothSheet)
        self.clotheMaskSprite.setSheet(self.widget.clothMaskSheet)
        self.setFrame(self.widget.frameInfo["actions"][self._renderAction][self.direction][self.currentFrame])

    def setClothesColor(self, palleteId):
        (self.clotheMaskSprite.setColor)(*palleteId)

    def setAccessory(self, accessoryId):
        if accessoryId == 0:
            self.accessorySprite.setAlpha(0)
            self.accessoryMaskSprite.setAlpha(0)
        else:
            self.accessorySprite.setAlpha(255)
            self.accessoryMaskSprite.setAlpha(255)
            self.accessorySprite.setSheet(self.widget.accessorySheet)
            self.accessoryMaskSprite.setSheet(self.widget.accessoryMaskSheet)
        self.setFrame(self.widget.frameInfo["actions"][self._renderAction][self.direction][self.currentFrame])

    def setAccessoryColor(self, palleteId):
        (self.accessoryMaskSprite.setColor)(*palleteId)

    def setHairstyle(self, hairId):
        if hairId == 0:
            self.hairSprite.setAlpha(0)
        else:
            self.hairSprite.setAlpha(255)
            self.hairSprite.setSheet(self.widget.hairSheet)
            self.setFrame(self.widget.frameInfo["actions"][self._renderAction][self.direction][self.currentFrame])

    def setHairColor(self, palleteId):
        (self.hairSprite.setColor)(*palleteId)

    def _create(self):
        self.bodySprite = GUIPygletSheet((self.widget.bodySheet), group=(self.widget.group),
          batch=(self.widget.batch))
        (self.bodySprite.setColor)(*SkinTone.rgb[self.widget.skintone])
        self.eyesSprite = GUIPygletSheet((self.widget.eyesSheet), group=(self.widget.group),
          batch=(self.widget.batch))
        self.clotheSprite = GUIPygletSheet((self.widget.clothSheet), group=(self.widget.group),
          batch=(self.widget.batch))
        self.clotheMaskSprite = GUIPygletSheet((self.widget.clothMaskSheet), group=(self.widget.group),
          batch=(self.widget.batch))
        self.hairSprite = GUIPygletSheet((self.widget.hairSheet), group=(self.widget.group),
          batch=(self.widget.batch),
          subpixel=True)
        self.hairSprite.setColor(238, 192, 83)
        self.accessorySprite = GUIPygletSheet((self.widget.accessorySheet), group=(self.widget.group),
          batch=(self.widget.batch))
        self.accessorySprite.setAlpha(0)
        self.accessoryMaskSprite = GUIPygletSheet((self.widget.accessoryMaskSheet), group=(self.widget.group),
          batch=(self.widget.batch))
        self.accessoryMaskSprite.setAlpha(0)
        self.swimSprite = GUIPygletSheet((self.widget.swimSheet), group=(self.widget.group),
          batch=(self.widget.batch))
        self.swimSprite.z_offset = -1
        self.swimSprite.setAlpha(0)
        return (
         self.bodySprite, self.swimSprite, self.eyesSprite, self.clotheSprite, self.clotheMaskSprite, self.hairSprite, self.accessorySprite, self.accessoryMaskSprite)

    @property
    def frameIndex(self):
        return self.widget.frameInfo["actions"][self._renderAction][self.direction][self.currentFrame]["frameIndex"]

    @property
    def actionFrameCount(self):
        return len(self.widget.frameInfo["actions"][self._renderAction][self.direction])

    def updatePosition(self):
        x, y = self.widget.position
        for sprite in self.sprites:
            if sprite == self.hairSprite or sprite == self.accessoryMaskSprite or sprite == self.accessorySprite:
                sprite.setPosition(x + self.hair_offset[0] * self.scale, y - sprite.height - self.hair_offset[1] * self.scale)
            elif sprite == self.eyesSprite:
                sprite.setPosition(x + self.eye_offset[0] * self.scale, y - sprite.height - self.eye_offset[1] * self.scale)
            else:
                sprite.setPosition(x + self._offset[0] * self.scale, y - sprite.height - self._offset[1] * self.scale)

    def getSize(self):
        return self.bodySprite.getSize()

    def getHeight(self):
        return self.bodySprite.getHeight() * self.bodySprite.scale

    def setFrame(self, frame):
        self.bodySprite.setFrame(frame["frameIndex"])
        self._offset = frame["offset"]
        hair_frame = self.widget.frameInfo["frame_map"]["hair"]["frames"][frame["frameIndex"]]
        self.hairSprite.setFrame(hair_frame)
        self.hair_offset = self.widget.frameInfo["frame_map"]["hair"]["offset"][self.widget.gender][frame["frameIndex"]]
        self.eye_offset = self.widget.frameInfo["frame_map"]["eyes"]["offset"][self.widget.gender][frame["frameIndex"]]
        eye_frame = self.widget.frameInfo["frame_map"]["eyes"]["frames"][frame["frameIndex"]]
        self.eyesSprite.setFrame(eye_frame)
        self.clotheSprite.setFrame(self.widget.frameInfo["frame_map"]["body_only"]["frames"][frame["frameIndex"]])
        self.clotheMaskSprite.setFrame(self.widget.frameInfo["frame_map"]["body_only"]["frames"][frame["frameIndex"]])
        if self.accessorySprite:
            self.accessorySprite.setFrame(hair_frame)
            self.accessoryMaskSprite.setFrame(hair_frame)
        self.swimSprite.setFrame(frame["frameIndex"] % 24)
        self.bodySprite.setSize(self.bodySprite.image.width, self.bodySprite.image.height)
        self.updatePosition()

    def setScale(self, scale):
        for sprite in self.sprites:
            sprite.scale = scale

        self.scale = scale
        self.updatePosition()

    def updateFrame(self):
        self.setFrame(self.widget.frameInfo["actions"][self._renderAction][self.direction][self.currentFrame])

    def animate(self):
        self.currentFrame += 1
        if self.currentFrame >= self.actionFrameCount:
            self.currentFrame = 0
        self.setFrame(self.widget.frameInfo["actions"][self._renderAction][self.direction][self.currentFrame])

    def stopAnimation(self):
        if self.duration:
            animationManager.unRegister(self, self.duration)

    def loopAnimation(self, duration):
        self.duration = duration
        animationManager.register(self, duration)
