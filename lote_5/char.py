# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\render\world\char.py
from client.control.world.animation import InterfaceAnimable
from client.data.layer import LayerType
from client.render.layer import worldLayer
from client.render.world.object import WorldObjectRender, getShadowPosition
from shared.container.constants import CreatureAction, GroundType, RefPointType, PlayerAction
from twisted.internet import reactor
import client.data.exceptions as exceptions, client.render.cache as cache, client.render.sprite as iSprite, pyglet
from shared.service.utils import inRange
from pyglet.gl import *
from twisted.internet import defer
from client.control.system.anims import FadeToOpacity, ScaleTo, AnimCallable, MoveToTarget, FadeOut, MultiParallelAnim, MoveBy, ParallelAnims, Animable
base_dt = 0.016666666666666666

class NPCWorldObjectRender(WorldObjectRender):

    def fadeTo(self, duration=2, toAlpha=255):
        if not self.visible:
            self.show()
            self.setAlpha(0)
        WorldObjectRender.fadeTo(self, duration, toAlpha)

    def getSize(self):
        if self.sprites:
            return self.sprite.getSize()
        else:
            return (10, 10)

    def _create(self):
        group, batch = worldLayer.getLayerRender(LayerType.LAYERED)
        self.sheet = cache.textureCache.getInteractObject(self.object.data.fileId, RefPointType.BOTTOMLEFT)
        self.sprite = iSprite.PygletSheet((self.sheet), batch=batch, group=group)
        self.sprites = [
         self.sprite]
        if self.object.data.shadow:
            self.shadow = self._createShadow((self.sheet), group, batch, referencePoint=(RefPointType.BOTTOMLEFT))
            self.sprites.insert(0, self.shadow)

    def _updatePosition(self):
        """ Update the position of all sprites for this object. """
        x, y = self.object.getProjection2D()
        for sprite in self.sprites:
            sprite.setPosition(x, y, y + self.object.data.renderingOrder)

    def setRenderPosition(self, x, y, z, interp):
        """ Update the position of all sprites for this object. """
        x, y = self.object.getProjection2D()
        for sprite in self.sprites:
            sprite.setPositionInterpolate(x, y, y + self.object.data.renderingOrder, interp)

    def setColorValues(self):
        return

    def setAlphaValues(self):
        return

    def setAction(self, charAction):
        """Required for rendered moving objects."""
        return

    def setFacing(self, facing):
        """Required for rendered moving objects."""
        return

    def restoreState(self):
        return


class NPCBerryObjectRender(NPCWorldObjectRender):

    def _create(self):
        group, batch = worldLayer.getLayerRender(LayerType.LAYERED)
        self.attachSheet = cache.textureCache.getInteractObject("attach_berry", RefPointType.BOTTOMCENTER)
        self.sheet = cache.textureCache.getInteractObject(self.object.data.fileId, RefPointType.BOTTOMCENTER)
        self.sprite = iSprite.PygletSheet((self.sheet), batch=batch, group=group)
        self.sprites = [
         self.sprite]
        self.attachSprite = None
        self.shadow = None
        if self.object.data.dropped == False:
            self.attachSprite = iSprite.PygletSheet((self.attachSheet), batch=batch, group=group)
            self.sprites.append(self.attachSprite)
        else:
            self.shadow = self._createShadow((self.sheet), group, batch, referencePoint=(RefPointType.BOTTOMCENTER))
            self.sprites.insert(0, self.shadow)

    def restoreState(self):
        self.sprite.opacity = 255
        group, batch = worldLayer.getLayerRender(LayerType.LAYERED)
        if self.object.data.dropped == False:
            if self.attachSprite == None:
                self.attachSprite = iSprite.PygletSheet((self.attachSheet), batch=batch, group=group)
                self.sprites.append(self.attachSprite)
            else:
                self.attachSprite.opacity = 255
        elif not self.shadow:
            self.shadow = self._createShadow((self.sheet), group, batch, referencePoint=(RefPointType.BOTTOMCENTER))
            self.sprites.insert(0, self.shadow)
        else:
            self.shadow.opacity = 50

    def _updatePosition(self):
        """ Update the position of all sprites for this object. """
        x, y, z = self.object.getPosition()
        self.sprite.setPosition(x, y, y + self.object.data.renderingOrder)
        if self.attachSprite:
            self.attachSprite.setPosition(x, y + self.sprite.height - 2, y + self.object.data.renderingOrder - 1)
        if self.shadow:
            if self.object.isGoingToPosition():
                shadowY = self.object._positionToGo[0][1]
            else:
                shadowY = y + self.object.data.renderingOrder
            self.shadow.setPosition(x, shadowY, y)

    def setRenderPosition(self, x, y, z, interp):
        """ Update the position of all sprites for this object. """
        x, y, z = self.object.getPosition()
        self.sprite.setPositionInterpolate(x, y, y + self.object.data.renderingOrder, interp)
        if self.shadow:
            if self.object.isGoingToPosition():
                shadowY = self.object._positionToGo[0][1]
            else:
                shadowY = y + self.object.data.renderingOrder
            self.shadow.setPositionInterpolate(x, shadowY, y, interp)

    def setAction(self, charAction):
        """Required for rendered moving objects. If an action is set, it's moving. So remove stem!"""
        if self.attachSprite:
            self.attachSprite.delete()
            self.sprites.remove(self.attachSprite)
            self.attachSprite = None


grassEnvironmentValues = (255, 255, 0)
waterEnvironmentValues = (255, 40, 0)

class UpdatePositionAnim(Animable):
    __doc__ = "For shrink only."

    def init(self, target, duration):
        self.target = target
        self.duration = duration

    def update(self, t):
        self.target._updatePosition()


class CharRender(WorldObjectRender, InterfaceAnimable):

    def __init__(self, object, ready=True):
        self.rendererAction = CreatureAction.WALK
        self._oldAction = None
        self.sheet = None
        self._currentFlip = 0
        self.facings = {}
        self.shadowSprite = None
        self.footSprite = None
        self.bodySprite = None
        self._lastGround = None
        self.colors = [
         (255, 255, 255),
         (255, 255, 255),
         (0, 0, 0)]
        self.alphas = [
         255, 255, 50]
        self._cropValues = (10, 8)
        self._offset = (0, 0)
        self._shadowOffset = (0, 0)
        self._currentFrame = 0
        self._currentFrameIndex = 0
        WorldObjectRender.__init__(self, object, ready)

    def _createShadow(self, sheet, group, batch, referencePoint=RefPointType.CENTER, flip_x=False, frame=0):
        """ Here we create char shadows, always in the transparent layer to make sure shadows are drawn correctly """
        group, batch = worldLayer.getShadowLayer(LayerType.LAYERED)
        shadowSprite = iSprite.PygletSheet(sheet, group=group, batch=batch)
        shadowSprite.z_offset = -1
        shadowSprite.setTransformation(sheet, 0, 0, flip_x=flip_x, flip_y=True)
        shadowSprite.setFrame(frame)
        shadowSprite.customSize = True
        shadowSprite.setRGBA(0, 0, 0, 50)
        shadowSprite.setScale(0.95, 0.4)
        shadowSprite.shadowOffset = getShadowPosition(self.sheet.grid[frame], shadowSprite, referencePoint)
        return shadowSprite

    def hide(self, dt=None):
        self._lastGround = None
        WorldObjectRender.hide(self)
        pyglet.clock.unschedule(self._runAnimation)

    def show(self):
        WorldObjectRender.show(self)

    def fadeWhite2Normal(self, duration):
        return

    def restoreCompletely(self):
        self.fading = False
        self.setEnvironment()
        if self.ready:
            self.setScale(1)
            self.resetColor()
            self.setAlphaValues()

    def setNormalAlpha(self):
        self.footSprite.setDefaultAlpha()
        self.bodySprite.setDefaultAlpha()
        self.shadowSprite.setDefaultAlpha()

    def setEvolveState(self):
        self.footSprite.opacity = 255

    def shrink(self, scale=1, duration=1, reset=True):
        anim = ScaleTo(self.bodySprite, self.bodySprite.scale, scale, duration)
        anim |= ScaleTo(self.footSprite, self.footSprite.scale, scale, duration)
        anim |= ScaleTo(self.shadowSprite, self.shadowSprite.scale, scale, duration)
        anim |= UpdatePositionAnim(self, duration)

        def _restoreScale():
            self.setScale(1)
            self.updatePosition()

        if reset:
            anim += AnimCallable(_restoreScale)
        self.startAnim(anim)
        return anim

    def tremble(self, shakes=1, offset=10, duration=0.05):
        """ Shakes sprite back and forth """
        anim = ParallelAnims(*[MoveBy(sprite, (offset, 0), duration) for sprite in self.sprites])
        self.startAnim(anim)
        return anim

    def rotate(self, duration=1, dt=0.3):
        reactor.callLater(duration, self._rotateEnd)

    def _rotateEnd(self):
        self.footSprite.rot = 0
        if self.object.groundType:
            self.setEnvironment()
        else:
            self.bodySprite.setDefaultAlpha()
            self.footSprite.setDefaultAlpha()
        self._arrangeSprites()
        self.updatePosition()

    def pulse(self, pulseCount, duration, scale=1.2):
        """ Make the char pulse in scale. (Not the shadow) """
        original_scale = self.bodySprite.scale
        body = ScaleTo(self.bodySprite, original_scale, scale, duration / 2)
        body += reversed(body)
        foot = ScaleTo(self.footSprite, original_scale, scale, duration / 2)
        foot += reversed(foot)
        combined = body | foot
        combined *= pulseCount
        if pulseCount > 0:

            def resetScale(scale):
                self.bodySprite.scale = scale
                self.footSprite.scale = scale
                self._arrangeSprites()

            combined += AnimCallable(resetScale, original_scale)
        self.startAnim(combined)
        return combined

    def setGlAddOn(self):
        self.bodySprite.setGlAddOn()
        self.footSprite.setGlAddOn()

    def setGlAddOff(self):
        self.bodySprite.setGlAddOff()
        self.footSprite.setGlAddOff()

    def setEnvironment(self):
        """ Sets colors and alpha depending on ground type, need to call your show or fade in after"""
        if self.object.groundType != self._lastGround:
            if self.object.groundType > 1:
                if self.object.data.z < 1 or not self.object.flying:
                    if self.object.groundType in GroundType.WATER:
                        self.alphas = list(waterEnvironmentValues)
                    if self.object.groundType in GroundType.GRASS:
                        self.alphas = list(grassEnvironmentValues)
                    else:
                        self.alphas = [255, 255, 50]
                    self.colors[1] = (255, 255, 255)
            else:
                self.alphas = [
                 255, 255, 50]
        self._lastGround = self.object.groundType

    def resetColor(self):
        if self.ready:
            self.footSprite.setColor(255, 255, 255)
            self.bodySprite.setColor(255, 255, 255)

    def setColor(self, r, g, b):
        self.footSprite.setColor(r, g, b)
        self.bodySprite.setColor(r, g, b)

    def setRGBA(self, r, g, b, a):
        self.footSprite.setRGBA(r, g, b, a)
        self.bodySprite.setRGBA(r, g, b, a)

    def fadeTo(self, duration=2, toAlpha=255, reset=True):
        self.fading = True
        if not self.visible:
            self.show()
        if reset:
            self.setAlpha(0)
        anim = MultiParallelAnim(self.sprites, FadeToOpacity, toAlpha, duration)
        anim += AnimCallable(self._stoppedFade)
        self.startAnim(anim)
        for lObject in self.object.child_objects:
            if lObject.visible:
                lObject.renderer.fadeTo(duration, toAlpha)

    def setAlphaValues(self):
        if not self.fading:
            self.bodySprite.setAlpha(self.alphas[0])
            self.footSprite.setAlpha(self.alphas[1])
            self.shadowSprite.setAlpha(self.alphas[2])

    def setColorValues(self):
        if not self.fading:
            (self.bodySprite.setColor)(*self.colors[0])
            (self.footSprite.setColor)(*self.colors[1])
            (self.shadowSprite.setColor)(*self.colors[2])

    def fadeIn(self, duration=2, reset=True):
        """ Uses default alpha settings """
        self.fading = True
        if not self.visible:
            self.show()
        if reset:
            self.setAlpha(0)
        if self.ready:
            self._startTransparency()
            anim = FadeToOpacity(self.bodySprite, self.alphas[0], duration) | FadeToOpacity(self.footSprite, self.alphas[1], duration) | FadeToOpacity(self.shadowSprite, self.alphas[2], duration)
            anim += AnimCallable(self._endTransparency)
            anim += AnimCallable(self._stoppedFade)
            self.startAnim(anim)
        for lObject in self.object.child_objects:
            if lObject.visible:
                lObject.renderer.fadeTo(duration, self.alphas[0])

    def fadeOut(self, duration=2):
        """ Fading changes sprite color until set alpha """
        d = defer.Deferred()
        self.fading = True
        if self.ready:
            self._startTransparency()
            anim = MultiParallelAnim(self.sprites, FadeOut, duration)
            anim += AnimCallable(self._endTransparency)
            anim += AnimCallable(self._stoppedFade)
            anim += AnimCallable(d.callback, None)
            self.startAnim(anim)
        return d

    def setAlpha(self, value):
        """ Sets alpha of all sprites equally """
        WorldObjectRender.setAlpha(self, value)
        for lObject in self.object.child_objects:
            if lObject.visible:
                lObject.renderer.setAlpha(value)

    def _create(self):
        raise NotImplementedError

    def _updateSize(self):
        """ Update the size of all sprites for this object. """
        return

    def _updatePosition(self):
        """ Update the position of all sprites for this object. """
        x, y, z = self.object.getDiffEffectPosition()
        self.bodySprite.setPosition(x, y + self._cropValues[1], y if not self.object.onBridge else y - 60)
        self.footSprite.setPosition(x, y, y if not self.object.onBridge else y - 60)
        self.shadowSprite.setPosition(x, y, y + z)

    def setRenderPosition(self, x, y, z, interp):
        self.bodySprite.setPositionInterpolate(x, y + self._cropValues[1], y if not self.object.onBridge else y - 60, interp)
        self.footSprite.setPositionInterpolate(x, y, y if not self.object.onBridge else y - 60, interp)
        self.shadowSprite.setPositionInterpolate(x, y, y + z, interp)

    def setFrame(self, col, row=0):
        """ From outside. """
        for sprite in self.sprites:
            sprite.setFrame(col, row)

        self.bodySprite.setSize(self.bodySprite.image.width, self.bodySprite.image.height)
        self.footSprite.setSize(self.footSprite.image.width, self.footSprite.image.height)

    def getSize(self):
        if self.sheet:
            return (self.sheet.get(self.rendererAction).getWidth(), self.sheet.get(self.rendererAction).getHeight())
        else:
            return (20, 26)

    def animate(self):
        if not inRange(self._currentFrame + 1, self._getMinFrame(), self._getMaxFrame()):
            self._currentFrame = self._getMinFrame()
        else:
            self._currentFrame += 1
        self.setFrame(self._currentFrame)

    def _getMinFrame(self):
        """ Return the minimal frame for the current action and facing. """
        return self.facings[self.rendererAction][self.object.data.facing].frames[0]

    def _getMaxFrame(self):
        """ Return the maximal frame for the current action and facing. """
        return self.facings[self.rendererAction][self.object.data.facing].frames[1]

    def getFrameNumber(self):
        """ Return the number of frames for this animation. """
        return self._getMaxFrame() - self._getMinFrame()

    def _getFlip(self):
        """ Return the flip """
        return self.facings[self.rendererAction][self.object.data.facing].flip

    def setFacing(self, facing):
        assert facing is not None, "Setting wrong value to char facing."
        self._refreshCurrentFrame()

    def _setRenderAction(self):
        raise exceptions.MustBeImplemented()

    def delete(self):
        pyglet.clock.unschedule(self._runAnimation)
        super().delete()

    def setAction(self, action):
        """ Set the action only. Do not play it. """
        self._setRenderAction(action)
        if self.ready:
            self.updateSpriteAction()
            pyglet.clock.unschedule(self._runAnimation)
            if action == CreatureAction.WALK or action == CreatureAction.FLY:
                self._runAnimation(0.016666666666666666)
                pyglet.clock.schedule_interval(self._runAnimation, 0.15)

    def cancelAction(self, currentAction):
        pyglet.clock.unschedule(self._runAnimation)

    def _runAnimation(self, dt):
        self.animate()

    def _arrangeSprites(self):
        """ Arranges the sprites so that they get cropped and flipped """
        self._currentFlip = self._getFlip()
        self.footSprite.setTransformation((self.sheet), 0, (self._cropValues[0]), flip_x=(self._currentFlip))
        self.bodySprite.setTransformation((self.sheet), (self._cropValues[1]), 0, flip_x=(self._currentFlip))
        self.shadowSprite.setTransformation((self.sheet), 0, 0, flip_x=(self._currentFlip), flip_y=True)

    def updateSpriteAction(self):
        """ Action has changed, go ahead and set the sheet to the current action """
        self.sheet = self.sheet.get(self.rendererAction)
        self._arrangeSprites()
        self._refreshCurrentFrame()

    def _refreshCurrentFrame(self):
        """ Refresh the current frame, will be called by:
            Update Sprite Action
            Set Facing Direction - Frame needs to be changed to match the facing position.
            Sometimes the flip direction will have changed, when you change your facing. (ex: right to left)
        """
        if self._currentFlip != self._getFlip():
            self._arrangeSprites()
        self._currentFrame = self._getMinFrame()
        self.setFrame(self._currentFrame)

    def _setSprites(self):
        self.sheet = self.sheet.get(CreatureAction.WALK)
        self._currentFlip = self._getFlip()
        self._currentFrame = self._getMinFrame()
        group, batch = worldLayer.getLayerRender(LayerType.LAYERED)
        self.bodySprite = iSprite.PygletSheet((self.sheet), group=group, batch=batch)
        self.bodySprite.setTransformation((self.sheet), (self._cropValues[1]), 0, flip_x=(self._currentFlip))
        self.bodySprite.setFrame(self._currentFrame)
        self.footSprite = iSprite.PygletSheet((self.sheet), group=group, batch=batch)
        self.footSprite.setTransformation((self.sheet), 0, (self._cropValues[0]), flip_x=(self._currentFlip))
        self.footSprite.setFrame(self._currentFrame)
        self.shadowSprite = self._createShadow((self.sheet), group,
          batch,
          referencePoint=(RefPointType.BOTTOMCENTER),
          flip_x=(self._currentFlip),
          frame=(self._currentFrame))
        self.shadowSprite.offset = self.shadowSprite.shadowOffset
        self.sprites = [
         self.shadowSprite, self.footSprite, self.bodySprite]
