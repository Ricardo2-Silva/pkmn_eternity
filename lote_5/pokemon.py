# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\render\world\pokemon.py
from twisted.internet import defer
import pyglet
from client.control.system.anims import ParallelAnims, MoveTo
from client.data.DB import sheetExperiment
from client.data.layer import LayerType
from client.render.cache import textureCache
from client.render.layer import worldLayer
from client.render.sprite import PygletSheet
from client.render.world.char import CharRender, base_dt
from shared.container.constants import RefPointType, CreatureAction, Gender
from shared.service.direction import directionService
from shared.service.utils import inRange

class PokemonRender(CharRender):
    __doc__ = " Render part of pokemon "

    def __init__(self, object, ready=True):
        super().__init__(object, ready)

    def _create(self):
        self._custom_duration = 0
        self.sheet = textureCache.getPokemon(self.object.data.dexId, self.object.data.gender, self.object.data.subspecies)
        self.frameInfo = sheetExperiment.getPokemon(self.sheet.dexId, Gender.toString[self.object.data.gender], self.object.data.subspecies)
        self._setSprites()

    def changeSprites(self):
        self.stopAnimation()
        self.sheet = textureCache.getPokemon(self.object.data.dexId, self.object.data.gender, self.object.data.subspecies)
        self.frameInfo = sheetExperiment.getPokemon(self.sheet.dexId, Gender.toString[self.object.data.gender], self.object.data.subspecies)
        self._arrangeSprites()
        self.updateSpriteAction()
        self.updatePosition()
        self.resetRenderState()

    def moveTo(self, duration, x, y, extension='constant'):
        anim = ParallelAnims(*[MoveTo(sprite, (x, y), duration) for sprite in self.sprites])
        if extension == "repeat":
            anim *= 0
        self.startAnim(anim)
        return anim

    def _createShadow(self, sheet, group, batch, referencePoint=RefPointType.CENTER, flip_x=False, frame=0):
        """ Here we create char shadows, always in the transparent layer to make sure shadows are drawn correctly """
        group, batch = worldLayer.getShadowLayer(LayerType.LAYERED)
        shadowSprite = PygletSheet(sheet, group=group, batch=batch)
        shadowSprite.z_offset = -2
        shadowSprite.setTransformation(sheet, 0, 0, flip_x=flip_x, flip_y=True)
        shadowSprite.setFrame(frame)
        shadowSprite.customSize = True
        shadowSprite.setRGBA(0, 0, 0, 50)
        shadowSprite.setScale(0.95, 0.4)
        shadowSprite.offset = (0, shadowSprite.height // 2)
        return shadowSprite

    def _setSprites(self):
        """ Create sprites for our Pokemon """
        self._currentFlip = self._getFlip()
        self._currentFrame = self._getMinFrame()
        height = self.sheet.getMinHeight()
        self._cropValues = (
         int(round(0.6 * height)), int(round(0.4 * height)))
        group, batch = worldLayer.getLayerRender(LayerType.LAYERED)
        self.footSprite = PygletSheet((self.sheet), group=group, batch=batch)
        self.footSprite.setTransformation((self.sheet), 0, (self._cropValues[0]), flip_x=(self._currentFlip))
        self.footSprite.setAlpha(255)
        self.footSprite.setFrame(self._currentFrame)
        self.bodySprite = PygletSheet((self.sheet), group=group, batch=batch)
        self.bodySprite.setTransformation((self.sheet), (self._cropValues[1]), 0, flip_x=(self._currentFlip))
        self.bodySprite.setAlpha(255)
        self.bodySprite.setFrame(self._currentFrame)
        self.shadowSprite = self._createShadow((self.sheet), group,
          batch,
          referencePoint=(RefPointType.CENTER),
          flip_x=(self._currentFlip),
          frame=(self._currentFrame))
        self.sprites = [
         self.shadowSprite, self.footSprite, self.bodySprite]

    def hide(self, dt=None):
        CharRender.hide(self, dt=dt)
        pyglet.clock.unschedule(self._runAnimation)

    def playAction(self, duration=0):
        """ Only sets animation delay """
        if duration == 0:
            self._animationDelay = self.frameInfo[self.rendererAction]["dir"][directionService.facingToIndex(self.object.data.facing)]["t"] * 1 / 60.0
        else:
            self._animationDelay = duration / float(len(self.frameInfo[self.rendererAction]["dir"][directionService.facingToIndex(self.object.data.facing)]["fr"]))

    def stopAnimation(self):
        pyglet.clock.unschedule(self._runAnimation)

    def setAction(self, action):
        """ Set the action only. Do not play it. """
        self._setRenderAction(action)
        self.updateSpriteAction()
        pyglet.clock.unschedule(self._runAnimation)
        if action > CreatureAction.STOP:
            self._elapsed = 0
            self._defer = defer.Deferred()
            self._setCurrentFrame(1)
            self._next_dt = self.frames[1]["d"] * base_dt
            pyglet.clock.schedule_once(self._runAnimation, self._next_dt)
            return self._defer

    @property
    def frameDuration(self):
        if self._custom_duration:
            return self._custom_duration
        else:
            return self.frameInfo[self.rendererAction]["dir"][directionService.facingToIndex(self.object.data.facing)]["fr"][self._currentFrameIndex]["d"] * base_dt

    @property
    def frames(self):
        return self.frameInfo[self.rendererAction]["dir"][directionService.facingToIndex(self.object.data.facing)]["fr"]

    def _runAnimation(self, dt):
        newFrame = (self._currentFrameIndex + 1) % len(self.frames)
        self._setCurrentFrame(newFrame)
        frameDuration = self.frameDuration
        duration = frameDuration - (self._next_dt - dt)
        duration = min(max(0, duration), frameDuration)
        pyglet.clock.schedule_once(self._runAnimation, duration)
        self._next_dt = duration
        self._elapsed += self.frameInfo[self.rendererAction]["dir"][directionService.facingToIndex(self.object.data.facing)]["fr"][self._currentFrameIndex]["d"]
        if self.rendererAction >= CreatureAction.IDLE:
            if self._defer:
                if self._elapsed == self.frameInfo[self.rendererAction]["dir"][directionService.facingToIndex(self.object.data.facing)]["hp"]:
                    self._defer.callback("hp")
                    self._defer = None

    def _setCurrentFrame(self, frameNumber):
        frame = self.frames[frameNumber]
        self._currentFrameIndex = frameNumber
        self.setFrame(frame)

    def _setRenderAction(self, action):
        if action > 50:
            action = CreatureAction.toRenderAction[action]
        self.rendererAction = action

    def updateSpriteAction(self):
        self._refreshCurrentFrame()

    def getSize(self):
        if self.ready:
            return (
             self.sheet.getWidth(), self.sheet.getMaxHeight())
        else:
            return (24, 24)

    def setFrame(self, frame):
        """ Set the Pokemon frame to the specified frame.
            Each frame may need some sort of transformation in terms of flipping, so unfortunately we need to test it.
            flip values and arrange. """
        if self._currentFlip != frame["f"]:
            self._currentFlip = frame["f"]
            self._arrangeSprites()
        self._offset = frame["o"]
        self._shadowOffset = frame["s"]
        self.bodySprite.setFrame(frame["i"])
        self.footSprite.setFrame(frame["i"])
        self.shadowSprite.setFrame(frame["i"])
        if not self.object.isWalking():
            self._updatePosition()

    def _setFrameInformation(self):
        """ Set the the current frame index, the offsets, and the frames based on the frame data file.
            This is done every frame refresh.
        """
        self._actionFrames = self.frameInfo[self.rendererAction]["dir"][directionService.facingToIndex(self.object.data.facing)]["fr"]
        self._currentFrameIndex = self._getMinFrame()

    def _arrangeSprites(self):
        """ Set the transformation which may be a flipped image. Only set when necessary."""
        self._currentFlip = self._getFlip()
        self.footSprite.setTransformation((self.sheet), 0, (self._cropValues[0]), flip_x=(self._currentFlip))
        self.bodySprite.setTransformation((self.sheet), (self._cropValues[1]), 0, flip_x=(self._currentFlip))
        self.shadowSprite.setTransformation((self.sheet), 0, 0, flip_y=True, flip_x=(self._currentFlip))

    def _refreshCurrentFrame(self):
        self._setFrameInformation()
        self.setFrame(self._actionFrames[self._currentFrameIndex])

    def getActionDuration(self, action):
        return self.frameInfo[action]["dir"][directionService.facingToIndex(self.object.data.facing)]["t"]

    def _getMinFrame(self):
        """ Return the minimal frame for the current action and facing. """
        return 0

    def getFrameNumber(self):
        """ Return the number of frames for this animation. """
        return self._getMaxFrame() - self._getMinFrame()

    def _getFlip(self):
        """ Return the flip """
        return self.frameInfo[self.rendererAction]["dir"][directionService.facingToIndex(self.object.data.facing)]["fr"][self._currentFrameIndex]["f"]

    def _getMaxFrame(self):
        return len(self.frameInfo[self.rendererAction]["dir"][directionService.facingToIndex(self.object.data.facing)]["fr"]) - 1

    def animate(self):
        if not inRange(self._currentFrameIndex, self._getMinFrame(), self._getMaxFrame()):
            self._currentFrameIndex = 0
        else:
            self._currentFrameIndex += 1
        self.setFrame(self.frameInfo[self.rendererAction]["dir"][directionService.facingToIndex(self.object.data.facing)]["fr"][self._currentFrameIndex])

    def resetPreviousState(self):
        for sprite in self.sprites:
            sprite.resetPreviousState()

    def _updatePosition(self):
        """ Update the position of all sprites for this object. """
        x, y, z = self.object.getDiffEffectPosition()
        self.bodySprite.setPosition(x + self._offset[0], y + 8 + self._cropValues[1] * self.bodySprite.scale - self._offset[1] + z, y if not self.object.onBridge else y - 60)
        self.footSprite.setPosition(x + self._offset[0], y + 8 - self._offset[1] + z, y if not self.object.onBridge else y - 60)
        self.shadowSprite.setPosition(x + self._shadowOffset[0], y - self._shadowOffset[1], y + z)

    def _updatePositionNoRender(self):
        """ Update the position of all sprites for this object. """
        self.resetPreviousState()

    def setRenderPosition(self, x, y, z, interp):
        self.bodySprite.updatePosition(x + self._offset[0], y + 8 + self._cropValues[1] * self.bodySprite.scale - self._offset[1] + z, y if not self.object.onBridge else y - 60)
        self.footSprite.updatePosition(x + self._offset[0], y + 8 - self._offset[1] + z, y if not self.object.onBridge else y - 60)
        self.shadowSprite.updatePosition(x + self._shadowOffset[0], y - self._shadowOffset[1], y + z)
