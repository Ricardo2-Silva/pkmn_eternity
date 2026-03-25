# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\render\world\trainer.py
from twisted.internet import defer
import pyglet
from client.control.system.anims import MultiParallelAnim, FadeToOpacity, AnimCallable
from client.data.layer import LayerType
from client.data.world.char import SkinTone, appearanceColors, FacingData
from client.render import cache, sprite as iSprite
from client.render.layer import worldLayer
from client.render.world.char import CharRender
from client.scene.manager import sceneManager
from shared.container.constants import Gender, PlayerAction, RefPointType, CreatureAction, BodyTypes, GroundType
from shared.service.direction import directionService, DirectionService
normalEnvironmentValues = (255, 50, 0)
waterEnvironmentValues = (0, 0, 255)
grassEnvironmentValues = (255, 0, 0)
bodySizes = {(BodyTypes.KID): (13, 20), 
 (BodyTypes.DEFAULT): (13, 27), 
 (BodyTypes.OLD): (13, 23)}

class PlayerTrainerRender(CharRender):

    def _create(self):
        self.gender = Gender.toString[self.object.data.appearance.gender]
        self.rendererAction = self.object.stopAction
        body_name = BodyTypes(self.object.data.appearance.body).name.lower()
        if self.object.data.appearance.accessory.id > 0:
            self.accessorySheet, self.accessoryMaskSheet = cache.textureCache.getTrainerAccessory(self.object.data.appearance.accessory.id)
        self.hairSheet = cache.textureCache.getTrainerHair(self.gender, self.object.data.appearance.hair.id)
        self.eyesSheet = cache.textureCache.getTrainerEyes(body_name, 0)
        self.sheet, self.frameInfo = self.bodySheet, self.frameData = cache.textureCache.getTrainerBody(body_name, self.gender)
        self.clothSheet, self.clothMaskSheet = cache.textureCache.getTrainerClothes(body_name, self.gender, self.object.data.appearance.clothe.id)
        self.swimSheet = cache.textureCache.getTrainerSwimSheet()
        self._currentFrameIndex = 0
        self._currentFrame = self._getMinFrame()
        self.hair_offset = (0, 0)
        self.eye_offset = (0, 0)
        self.accessoryOffset = 0 if self.gender == "m" else 1
        self._bodySpriteList = []
        self._setSprites()

    @property
    def offset(self):
        return self.frameData["actions"][self.rendererAction][directionService.facingToIndex(self.object.data.facing)][self.currentFrame]["offset"]

    @property
    def frameIndex(self):
        return self.frameData["actions"][self.rendererAction][directionService.facingToIndex(self.object.data.facing)][self.currentFrame]["frameIndex"]

    @property
    def hairOffset(self):
        return self.frameData["hairstyle_offsets"][self.frameIndex]

    @property
    def actionFrameCount(self):
        return len(self.frameData["actions"][self.rendererAction][directionService.facingToIndex(self.object.data.facing)])

    def _getMinFrame(self):
        """ Return the minimal frame for the current action and facing. """
        return self.frameData["actions"][self.rendererAction][directionService.facingToIndex(self.object.data.facing)][0]

    def _getMaxFrame(self):
        """ Return the maximal frame for the current action and facing. """
        return self.frameData["actions"][self.rendererAction][directionService.facingToIndex(self.object.data.facing)][-1]

    def playAction(self, oldAction, action, duration=0):
        """ Only sets animation delay """
        return

    def delete(self):
        pyglet.clock.unschedule(self._runAnimation)
        super().delete()

    def setAction(self, action):
        """ Set the action only. Do not play it. """
        self._setRenderAction(action)
        self.updateSpriteAction()
        pyglet.clock.unschedule(self._runAnimation)
        if action == PlayerAction.WALK or action == PlayerAction.SWIMMING or action == PlayerAction.THROW:
            self._runAnimation(0)
            pyglet.clock.schedule_interval(self._runAnimation, 0.15)

    def _setRenderAction(self, action):
        self.rendererAction = action

    def getSize(self):
        return bodySizes.get(self.object.data.appearance.body, bodySizes[BodyTypes.DEFAULT])

    def fadeIn(self, duration=2, reset=True):
        """ Uses default alpha settings """
        self.fading = True
        if not self.visible:
            self.show()
        if reset:
            self.setAlpha(0)
        d = defer.Deferred()
        if self.ready:
            self._startTransparency()
            anim = MultiParallelAnim(self._bodySpriteList, FadeToOpacity, 255, duration)
            anim |= MultiParallelAnim((self.clotheMaskSprite, self.clotheSprite), FadeToOpacity, self.alphas[0], duration)
            anim |= FadeToOpacity(self.shadowSprite, self.alphas[1], duration)
            if self.swimSprite:
                anim |= FadeToOpacity(self.swimSprite, self.alphas[2], duration)
            anim += AnimCallable(self._endTransparency)
            anim += AnimCallable(self._stoppedFade)
            anim += AnimCallable(d.callback, None)
            self.startAnim(anim)
        return d

    def _setSprites(self):
        group, batch = worldLayer.getLayerRender(LayerType.LAYERED)
        self.shadowSprite = self._createShadow((self.bodySheet), group, batch, referencePoint=(RefPointType.BOTTOMCENTER))
        self.bodySprite = iSprite.PygletSheet((self.bodySheet), group=group, batch=batch, subpixel=True)
        (self.bodySprite.setColor)(*SkinTone.rgb[self.object.data.appearance.skintone])
        self.footSprite = self.bodySprite
        self.eyesSprite = iSprite.PygletSheet((self.eyesSheet), group=group, batch=batch, subpixel=True)
        self.eyesSprite.z_offset = 0.11
        self.clotheSprite = iSprite.PygletSheet((self.clothSheet), group=group, batch=batch, subpixel=True)
        self.clotheSprite.z_offset = 0.12
        self.clotheMaskSprite = iSprite.PygletSheet((self.clothMaskSheet), group=group, batch=batch, subpixel=True)
        (self.clotheMaskSprite.setColor)(*appearanceColors[self.object.data.appearance.clothe.color])
        self.clotheMaskSprite.z_offset = 0.13
        self.hairSprite = iSprite.PygletSheet((self.hairSheet), group=group, batch=batch, subpixel=True)
        (self.hairSprite.setColor)(*appearanceColors[self.object.data.appearance.hair.color])
        self.hairSprite.z_offset = 0.14
        self.swimSprite = None
        if self.object.data.appearance.accessory.id > 0:
            self.accessorySprite = iSprite.PygletSheet((self.accessorySheet), group=group, batch=batch, subpixel=True)
            self.accessorySprite.z_offset = 0.15
            self.accessoryMaskSprite = iSprite.PygletSheet((self.accessoryMaskSheet), group=group, batch=batch, subpixel=True)
            (self.accessoryMaskSprite.setColor)(*appearanceColors[self.object.data.appearance.accessory.color])
            self.accessoryMaskSprite.z_offset = 0.16
            self.sprites = [self.shadowSprite, self.bodySprite, self.eyesSprite, self.clotheSprite,
             self.clotheMaskSprite, self.hairSprite, self.accessorySprite, self.accessoryMaskSprite]
            self._bodySpriteList = [self.bodySprite, self.eyesSprite, self.hairSprite, self.accessorySprite, self.accessoryMaskSprite]
        else:
            self.accessorySprite = None
            self.accessoryMaskSprite = None
            self.sprites = [
             self.shadowSprite, self.bodySprite, self.eyesSprite, self.clotheSprite,
             self.clotheMaskSprite, self.hairSprite]
            self._bodySpriteList = [self.bodySprite, self.eyesSprite, self.hairSprite]
        self.setFrame(self._getMinFrame())

    def _setSwimState(self, value):
        if value is True:
            if not self.swimSprite:
                group, batch = worldLayer.getLayerRender(LayerType.LAYERED)
                self.swimSprite = iSprite.PygletSheet((self.swimSheet), group=group, batch=batch, subpixel=True)
                self.swimSprite.z_offset = -1
            self.sprites.insert(1, self.swimSprite)
            self.addSprites()
            x, y, z = self.object.getDiffEffectPosition()
            self.swimSprite.setPosition(x, y, y)
            self.swimSprite.resetRenderState()
        elif value is False:
            pass
        if self.swimSprite:
            self.sprites.remove(self.swimSprite)

    def setAccessory(self):
        if self.object.data.appearance.accessory.id > 0:
            self.accessorySheet, self.accessoryMaskSheet = cache.textureCache.getTrainerAccessory(self.object.data.appearance.accessory.id)
            if self.accessorySprite == None:
                group, batch = worldLayer.getLayerRender(LayerType.LAYERED)
                self.accessorySprite = iSprite.PygletSheet((self.accessorySheet), group=group, batch=batch, subpixel=True)
                self.accessorySprite.z_offset = 0.15
                self.accessoryMaskSprite = iSprite.PygletSheet((self.accessoryMaskSheet), group=group, batch=batch, subpixel=True)
                self.accessoryMaskSprite.z_offset = 0.16
            else:
                self.accessorySprite.setSheet(self.accessorySheet)
                self.accessoryMaskSprite.setSheet(self.accessoryMaskSheet)
            self.accessorySprite.setFrame(self.frameInfo["frame_map"]["all"]["frames"][self._currentFrame["frameIndex"]])
            (self.accessoryMaskSprite.setColor)(*appearanceColors[self.object.data.appearance.accessory.color])
            self.accessoryMaskSprite.setFrame(self.frameInfo["frame_map"]["all"]["frames"][self._currentFrame["frameIndex"]])
            self.delSprites()
            self.sprites = [self.shadowSprite, self.bodySprite, self.eyesSprite, self.clotheSprite,
             self.clotheMaskSprite, self.hairSprite, self.accessorySprite, self.accessoryMaskSprite]
            self._bodySpriteList = [self.bodySprite, self.eyesSprite, self.hairSprite, self.accessorySprite,
             self.accessoryMaskSprite]
            self.addSprites()
            self.updatePosition()
        elif self.accessorySprite in self.sprites:
            self.delSprites()
            self.sprites = [self.shadowSprite, self.bodySprite, self.eyesSprite, self.clotheSprite,
             self.clotheMaskSprite, self.hairSprite]
            self._bodySpriteList = [self.bodySprite, self.eyesSprite, self.hairSprite]
            self.addSprites()
            self.updatePosition()

    def _updateBody(self):
        """If a body is updated, so must it's gender, and eyes."""
        body_name = BodyTypes(self.object.data.appearance.body).name.lower()
        self.sheet, self.frameInfo = self.bodySheet, self.frameData = cache.textureCache.getTrainerBody(body_name, self.gender)
        self.bodySprite.setSheet(self.bodySheet)
        self.eyesSheet = cache.textureCache.getTrainerEyes(body_name, 0)
        self.eyesSprite.setSheet(self.eyesSheet)
        self.clothSheet, self.clothMaskSheet = cache.textureCache.getTrainerClothes(body_name, self.gender, self.object.data.appearance.clothe.id)
        self.clotheSprite.setSheet(self.clothSheet)
        self.clotheMaskSprite.setSheet(self.clothMaskSheet)

    def _updateHairStyle(self):
        gender = Gender.toString[self.object.data.appearance.gender]
        self.hairSheet = cache.textureCache.getTrainerHair(gender, self.object.data.appearance.hair.id)
        self.hairSprite.setSheet(self.hairSheet)

    def _updateClothes(self):
        gender = Gender.toString[self.object.data.appearance.gender]
        self.clothSheet, self.clothMaskSheet = cache.textureCache.getTrainerClothes("default", gender, self.object.data.appearance.clothe.id)
        self.clotheSprite.setSheet(self.clothSheet)
        self.clotheMaskSprite.setSheet(self.clothMaskSheet)

    def updateAppearanceState(self, genderChanged, skintoneChanged, bodyChanged, eyesChanged, hairChanged, accessoryChanged, clothesChanged):
        hairColor = appearanceColors[self.object.data.appearance.hair.color]
        clothesColor = appearanceColors[self.object.data.appearance.clothe.color]
        accessoryColor = appearanceColors[self.object.data.appearance.accessory.color]
        if bodyChanged or eyesChanged or genderChanged:
            self._updateBody()
        if skintoneChanged:
            (self.bodySprite.setColor)(*SkinTone.rgb[self.object.data.appearance.skintone])
        if accessoryChanged:
            self.setAccessory()
        if self.accessoryMaskSprite:
            if accessoryColor != self.accessoryMaskSprite.color:
                (self.accessoryMaskSprite.setColor)(*accessoryColor)
        if hairChanged:
            self._updateHairStyle()
        if hairColor != self.hairSprite.color:
            (self.hairSprite.setColor)(*hairColor)
        if clothesChanged:
            self._updateClothes()
        if clothesColor != self.clotheMaskSprite.color:
            (self.clotheMaskSprite.setColor)(*clothesColor)
        self._refreshCurrentFrame()
        self._updatePosition()

    def resetPreviousState(self):
        for sprite in self.sprites:
            sprite.resetPreviousState()

    def setRenderPosition(self, x, y, z, interp):
        for sprite in self.sprites:
            if sprite == self.shadowSprite or sprite == self.swimSprite:
                sprite.updatePosition(x, y, y if not self.object.onBridge else y - 60)
            else:
                sprite.updatePosition(x, y + int(z), y if not self.object.onBridge else y - 60)

    def _updatePosition(self):
        """ Update the position of all sprites for this object. """
        x, y, z = self.object.getDiffEffectPosition()
        for sprite in self.sprites:
            if sprite == self.shadowSprite or sprite == self.swimSprite:
                sprite.setPosition(x, y, y if not self.object.onBridge else y - 60)
            else:
                sprite.setPosition(x, y + z, y if not self.object.onBridge else y - 60)

    def _updatePositionNoRender(self):
        """ Update the position of all sprites for this object. """
        self.resetPreviousState()

    def _arrangeSprites(self):
        self.shadowSprite.setTransformation((self.sheet), 0, 0, flip_y=True)

    def _refreshCurrentFrame(self):
        """ Refresh the current frame, will be called by:
            Update Sprite Action
            Set Facing Direction - Frame needs to be changed to match the facing position.
            Sometimes the flip direction will have changed, when you change your facing. (ex: right to left)
        """
        self._currentFrame = self._getMinFrame()
        self.setFrame(self._currentFrame)

    def setFrame(self, frame):
        """ From outside. """
        self._offset = frame["offset"]
        self.bodySprite.setFrame(frame["frameIndex"])
        self.bodySprite.offset = self._offset
        self.eye_offset = self.frameInfo["frame_map"]["eyes"]["offset"][self.gender][frame["frameIndex"]]
        self.eyesSprite.offset = self.eye_offset
        self.eyesSprite.setFrame(self.frameInfo["frame_map"]["eyes"]["frames"][frame["frameIndex"]])
        hair_frame = self.frameInfo["frame_map"]["hair"]["frames"][frame["frameIndex"]]
        self.hair_offset = self.frameInfo["frame_map"]["hair"]["offset"][self.gender][frame["frameIndex"]]
        self.hairSprite.setFrame(hair_frame)
        self.hairSprite.offset = self.hair_offset
        self.clotheSprite.setFrame(self.frameInfo["frame_map"]["body_only"]["frames"][frame["frameIndex"]])
        self.clotheSprite.offset = self._offset
        self.clotheMaskSprite.setFrame(self.frameInfo["frame_map"]["body_only"]["frames"][frame["frameIndex"]])
        self.clotheMaskSprite.offset = self._offset
        self.shadowSprite.offset = list(map(sum, zip(self.shadowSprite.shadowOffset, self._offset)))
        if self.accessorySprite:
            self.accessorySprite.setFrame(hair_frame)
            self.accessorySprite.offset = self.hair_offset
            self.accessoryMaskSprite.setFrame(hair_frame)
            self.accessoryMaskSprite.offset = self.hair_offset
        else:
            self.shadowSprite.setFrame(frame["frameIndex"])
            self.bodySprite.setSize(self.bodySprite.image.width, self.bodySprite.image.height)
            if self.swimSprite:
                self.swimSprite.setFrame(frame["frameIndex"] % 24)
                self.swimSprite.offset = self._offset
            if not self.object.isWalking():
                self._updatePosition()
            else:
                self._updatePositionNoRender()

    def _setFrameInformation(self):
        """ Set the the current frame index, the offsets, and the frames based on the frame data file.
            This is done every frame refresh.
        """
        self._actionFrames = self.frameInfo["actions"][self.rendererAction][directionService.facingToIndex(self.object.data.facing)]["fr"]
        self._currentFrameIndex = self._getMinFrame()

    def setEnvironment(self):
        """ Sets colors and alpha depending on ground type, need to call your show or fade in after"""
        if self.fading or self.object.groundType != self._lastGround:
            if self.object.groundType > 1:
                if self.object.data.z < 1:
                    if self.object.groundType in GroundType.WATER:
                        self.alphas = waterEnvironmentValues
                    elif self.object.groundType in GroundType.GRASS:
                        self.alphas = grassEnvironmentValues
                    else:
                        self.alphas = normalEnvironmentValues
                else:
                    self.alphas = normalEnvironmentValues
            else:
                self.alphas = normalEnvironmentValues
        else:
            self._lastGround = self.object.groundType

    def setAlphaValues(self):
        if not self.fading:
            for sprite in self._bodySpriteList:
                sprite.setAlpha(255)

            self.clotheSprite.setAlpha(self.alphas[0])
            self.clotheMaskSprite.setAlpha(self.alphas[0])
            self.shadowSprite.setAlpha(self.alphas[1])
            if self.swimSprite:
                self.swimSprite.setAlpha(self.alphas[2])
        return

    def setColorValues(self):
        if not self.fading:
            pass
        return

    def applyEnvironment(self):
        """Done last after setting alpha values."""
        if self.object.groundType in GroundType.WATER:
            self._setSwimState(True)
        else:
            if self.swimSprite:
                if self.swimSprite in self.sprites:
                    self._setSwimState(False)
            if not self.object.isWalking():
                self.updatePosition()

    def animate(self):
        self._currentFrameIndex += 1
        if self._currentFrameIndex >= self.actionFrameCount:
            self._currentFrameIndex = 0
        self.setFrame(self.frameData["actions"][self.rendererAction][directionService.facingToIndex(self.object.data.facing)][self._currentFrameIndex])


TRAINER_FRAMES = 3
trainerFacings = {}
framesByDir = 12 // TRAINER_FRAMES
for action in PlayerAction.NPC_TRAINER_ACTIONS:
    trainerFacings[action] = {(DirectionService.UP): (FacingData([0, framesByDir * 1], 0)), 
     (DirectionService.UP_LEFT): (FacingData([framesByDir * 1, framesByDir * 2], 1)), 
     (DirectionService.LEFT): (FacingData([framesByDir * 1, framesByDir * 2], 1)), 
     (DirectionService.DOWN_LEFT): (FacingData([framesByDir * 1, framesByDir * 2], 1)), 
     (DirectionService.DOWN): (FacingData([framesByDir * 2, framesByDir * 3], 0)), 
     (DirectionService.DOWN_RIGHT): (FacingData([framesByDir * 1, framesByDir * 2], 0)), 
     (DirectionService.RIGHT): (FacingData([framesByDir * 1, framesByDir * 2], 0)), 
     (DirectionService.UP_RIGHT): (FacingData([framesByDir * 1, framesByDir * 2], 0))}

class NPCTrainerRender(CharRender):

    def _create(self):
        self.sheet = cache.textureCache.getTrainer(self.object.data.fileId)
        self.facings = trainerFacings
        self._setSprites()

    def _setRenderAction(self, action):
        self.rendererAction = CreatureAction.WALK
