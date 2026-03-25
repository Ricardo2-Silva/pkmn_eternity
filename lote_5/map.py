# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\render\world\map.py
"""
Created on 15 juil. 2011

@author: Kami
"""
from twisted.internet import defer
import client.render.cache as cache, pyglet
from client.control.system.anims import ScaleBy, FadeOut, AnimCallable, MoveTo, ScaleTo, Lerp, FadeColor, ScaleXTo, ScaleYTo, FadeToOpacity, Spiral
from client.control.world.animation import animationManager
from client.data.layer import LayerType
from client.data.sprite import Sheet
from client.data.world.animation import AnimDirection, AnimationEnd
from client.render.layer import weatherLayer, worldLayer
from client.render.sprite import PygletSheet, PygletSprite, MultiTextureSprite, LineSprite, TimerTextureSprite, TimerTextureSheet
from client.render.world.object import WorldObjectRender
from shared.container.constants import RefPointType
from shared.container.skill import getDistanceBetweenTwoPoints

class EffectRender(WorldObjectRender):
    __doc__ = " Render part of effect "

    def _create(self):
        group, batch = worldLayer.getLayerRender(LayerType.LAYERED, False)
        self._directionAnim = AnimDirection.FORWARD
        if type(self.object.data.fileId) is str:
            if self.object.data.metafile is True:
                self.sheet = cache.textureCache.getEffectXml(self.object.data.fileId, self.object.data.refPointType)
            else:
                self.sheet = cache.textureCache.getEffect(self.object.data.fileId, self.object.data.refPointType)
        else:
            self.sheet = self.object.data.fileId
        self.sprite = PygletSheet((self.sheet), batch=batch)
        self.sprite.renderingOrder = self.renderingOrder
        if self.object.data.animation:
            self.object.data.animation.create(self.sheet)
            self.sprite.setFrame(self.currentFrame.index)
        self.sprites = [self.sprite]

    def setRenderGroup(self, group):
        for sprite in self.sprites:
            sprite.group = group

    def resetFrame(self):
        if self.object.data.animation:
            self._currentFrame = 0
            self.sprite.setFrame(self.currentFrame.index)
        else:
            self.sprite.setFrame(0)

    def setAlpha(self, alpha):
        WorldObjectRender.setAlpha(self, alpha)
        if alpha > 0 and alpha < 255:
            self._startTransparency()
        else:
            self._endTransparency()

    @property
    def renderingOrder(self):
        if self.object.data.attach:
            return int(self.object.data.attach.getY()) + self.object.data.renderingOrder
        else:
            if self.object.data.renderingOrder:
                return self.object.data.renderingOrder
            return 0

    def updateTexture(self, effect):
        self.sprite.setSheet(cache.textureCache.getEffect(effect, self.object.data.refPointType))

    def spiral(self, direction, startAngle, radius, duration):
        anim = Spiral(self.sprite, direction, startAngle, radius, duration)
        self.startAnim(anim)

    def grow(self, duration, startScale=0.5, endScale=1.0, reset=True):
        anim = ScaleTo(self.sprite, startScale, endScale, duration)
        if reset:
            anim += AnimCallable(self._resetScale, 1)
        self.startAnim(anim)
        return anim

    def growSeparate(self, duration, startX, startY, endX, endY, reset=True):
        anim = ScaleXTo(self.sprite, startX, endX, duration)
        anim |= ScaleYTo(self.sprite, startY, endY, duration)
        if reset:
            anim += AnimCallable(self._resetScale, 1)
        self.startAnim(anim)

    def _resetScale(self, scale):
        for sprite in self.sprites:
            sprite.scale = scale

    def pulse(self, pulseCount, duration, scale=1.2):
        """ If no duration, pulse forever """
        original_scale = self.sprite.scale
        anim = ScaleTo(self.sprite, original_scale, scale, duration / 2)
        anim += reversed(anim)
        anim *= pulseCount
        if pulseCount > 0:
            anim += AnimCallable(self._resetScale, original_scale)
        self.startAnim(anim)
        return anim

    def pulseSeparate(self, pulseCount, duration, scale_x, scale_y):
        """ If no duration, pulse forever.
            Only animate if scale is not 1.0
        """
        original_scale = self.sprite.scale
        anim_x = False
        if scale_x != 1.0:
            anim_x = ScaleXTo(self.sprite, original_scale, scale_x, duration / 2)
            anim_x += reversed(anim_x)
            anim_x *= pulseCount
        else:
            anim_y = False
            if scale_y != 1.0:
                anim_y = ScaleYTo(self.sprite, original_scale, scale_y, duration / 2)
                anim_y += reversed(anim_y)
                anim_y *= pulseCount
            if anim_y:
                if anim_x:
                    anim = anim_x | anim_y
            if anim_x:
                anim = anim_x
            elif anim_y:
                anim = anim_y
            else:
                raise Exception("Trying animate 1.0 scales for both scale_x and scale_y", self)
        if pulseCount > 0:
            anim += AnimCallable(self._resetScale, original_scale)
        self.startAnim(anim)
        return anim

    def pulseAlpha(self, pulseCount, duration, alpha):
        """ If no duration, pulse forever """
        anim = FadeToOpacity(self.sprite, alpha, duration / 2)
        anim += reversed(anim)
        anim *= pulseCount
        self.startAnim(anim)
        return anim

    def moveTo(self, duration, x, y, extension='constant'):
        anim = MoveTo(self.sprite, (x, y), duration)
        if extension == "repeat":
            anim *= 0
        self.startAnim(anim)
        return anim

    def stop(self):
        """ Stops any lerps or other easements """
        self.sprite.x = self.sprite.x
        self.sprite.y = self.sprite.y

    def flash(self, duration, scale=4.0):
        """ Become bigger and disappear at the same time. """
        anim = (ScaleBy(self.sprite, scale, duration) | FadeOut(self.sprite, duration)) + AnimCallable(self.object.delete)
        self.startAnim(anim)
        return anim

    def fadeColor(self, duration, rgb, startColor=None):
        anim = FadeColor(self.sprite, rgb, duration, startColor)
        return anim

    def rotate(self, duration=1):
        anim = Lerp(self.sprite, "rotation", 0, 360, duration)
        self.startAnim(anim)
        return anim

    def spin(self, duration, spins):
        """Speed is spins per second."""
        per_sec = duration / spins
        anim = Lerp(self.sprite, "rotation", 0, 360, per_sec)
        anim *= spins
        self.startAnim(anim)
        return anim

    def setRotation(self, value):
        self.sprite.rotation = value

    def _finalize(self):
        if not self.object.data.hidden:
            self._checkAnimation()
        else:
            WorldObjectRender.hide(self)

    def hide(self, dt=None):
        WorldObjectRender.hide(self)
        if self.object.data.animation:
            self.stopAnimation()
        return True

    def stopAnimation(self):
        self._animating = False
        pyglet.clock.unschedule(self.animate)

    def delete(self):
        self.object.removeLink()
        self.stopAnimation()
        WorldObjectRender.delete(self)

    def show(self):
        WorldObjectRender.show(self)
        self._checkAnimation()

    def _permanentRemoval(self, dt):
        self.object.delete()

    @property
    def currentFrame(self):
        return self.object.data.animation.frames[self._currentFrame]

    def _checkAnimation(self):
        if self.object.data.animation:
            self._animating = True
            self._currentFrame = 0
            self._animationStep = 0
            pyglet.clock.schedule_once(self.animate, self.currentFrame.duration)

    def animationEnd(self):
        if self.object.data.animation.removal is "delete":
            self.object.delete()
        elif self.object.data.animation.removal is "hide":
            self.hide()

    def setMultipleAttributes(self, x, y, rotation, scale):
        for sprite in self.sprites:
            sprite.setMultipleAttributes(x, y, rotation, scale, renderingOrder=(self.renderingOrder))

    def animate(self, dt):
        """ Animates the frames until duration has passed. """
        self._animationStep += dt
        self._currentFrame += 1
        if self._currentFrame >= len(self.object.data.animation.frames):
            if self.object.data.animation.end == AnimationEnd.RESTART:
                self._currentFrame = 0
            elif self.object.data.animation.end == AnimationEnd.REVERSE:
                self.object.data.animation.frames = reversed(self.object.data.animation.frames)
                self._currentFrame = 0
            elif self.object.data.animation.end == AnimationEnd.STOP:
                if self._animationStep >= self.object.data.animation.duration:
                    self.animationEnd()
                    return
                pyglet.clock.schedule_once(self.animate, self.object.data.animation.frames[0].duration)
                return
        if self.object.data.animation.duration:
            if self._animationStep >= self.object.data.animation.duration:
                self.animationEnd()
                return
        self.sprite.setFrame(self.currentFrame.index)
        pyglet.clock.schedule_once(self.animate, self.currentFrame.duration)

    def framePulse(self):
        """ Used for animation. Shape changes are required for changing reference point sadly."""
        if self._directionAnim == AnimDirection.FORWARD:
            self.sprite._frame_index += 1
            if self.sprite._frame_index >= self.sprite._frameClamp[1] - 1:
                self._directionAnim = AnimDirection.REVERSE
                self.sprite._frame_index = self.sprite._frameClamp[1] - 1
        elif self._directionAnim == AnimDirection.REVERSE:
            pass
        self.sprite._frame_index -= 1
        if self.sprite._frame_index < self.sprite._frameClamp[0]:
            self._directionAnim = AnimDirection.FORWARD
            self.sprite._frame_index = self.sprite._frameClamp[0] + 1
        self.sprite.image = self.sprite._textureGrid[self.sprite._frame_index]

    def _updatePosition(self):
        """ Update the position of all sprites for this object. """
        (self.sprite.setPosition)(*self.object.getProjection2D(), **{"renderingOrder": (self.renderingOrder)})

    def setRenderPosition(self, x, y, z, interp):
        if self.object.data.attach:
            renderingOrder = self.object.data.attach.interp_state[1] + self.object.data.renderingOrder
        else:
            renderingOrder = self.object.data.renderingOrder
        self.sprite.updatePosition(x, y, renderingOrder)


class MapEffectRender(EffectRender):

    def _create(self):
        group, batch = worldLayer.getLayerRender(LayerType.LAYERED, False)
        self._directionAnim = AnimDirection.FORWARD
        self.sheet = cache.textureCache.getMapEffect((self.object.data.fileId), (self.object.data.refPointType), delay=True)
        self.sprite = PygletSheet((self.sheet), batch=batch)
        self.sprite.renderingOrder = self.renderingOrder
        if self.object.data.animation:
            self.object.data.animation.delay = self.sheet.animationDelay
            self.object.data.animation.create(self.sheet)
            self.sprite.setFrame(self.currentFrame.index)
        self.sprites = [self.sprite]


class GrassEffectRender(EffectRender):

    def fadeOut(self, duration=2):
        """ Fading changes sprite color until set alpha """
        d = defer.Deferred()
        self.fading = True
        anim = FadeOut(self.sprite, duration)
        anim += AnimCallable(d.callback, None)
        self.startAnim(anim)
        d.addCallback(self._stoppedFade)
        return d


class WarpRender(EffectRender):

    def _create(self):
        group, batch = worldLayer.getLayerRender(LayerType.LAYERED, True)
        self.sheet = cache.textureCache.getEffect(self.object.data.fileId, self.object.data.refPointType)
        self.sprite = PygletSheet((self.sheet), batch=batch)
        self.sprite.renderingOrder = self.renderingOrder
        if self.object.data.animation:
            self.object.data.animation.create(self.sheet)
        self.sprites = [
         self.sprite]


class SkillRender(EffectRender):

    def _create(self):
        group, batch = worldLayer.getLayerRender(LayerType.LAYERED, False)
        self._directionAnim = AnimDirection.FORWARD
        if self.object.data.program:
            atlas = False
        else:
            atlas = True
        if type(self.object.data.fileId) is str:
            if self.object.data.metafile:
                sheet = cache.textureCache.getSkillXml(self.object.data.fileId, self.object.data.refPointType)
            else:
                sheet = cache.textureCache.getSkillEffect(self.object.data.fileId, self.object.data.refPointType, atlas)
        else:
            sheet = self.object.data.fileId
        self.sheet = sheet
        self.sprite = PygletSheet((self.sheet), x=(self.object.data.x), y=(self.object.data.y), group=group, batch=batch)
        if self.object.data.flip_x is True or self.object.data.flip_y == True:
            self.sprite.setTransformation(self.sheet, 0, 0, self.object.data.flip_x, self.object.data.flip_y)
        self.sprite.renderingOrder = self.renderingOrder
        self.sprites.append(self.sprite)
        if self.object.data.shadow:
            self.shadowSprite = self._createShadow((self.sheet), group, batch, referencePoint=(self.object.data.refPointType))
            self.sprites.append(self.shadowSprite)
        if self.object.data.animation:
            self.object.data.animation.create(self.sheet)
            for sprite in self.sprites:
                sprite.setFrame(self.currentFrame.index)

    def _updatePosition(self):
        x, y, z = self.object.getPosition()
        self.sprite.setPosition(x, y + z, self.renderingOrder)
        if self.object.data.shadow:
            self.shadowSprite.setPosition(x, y, y)

    def setRenderPosition(self, x, y, z, interp):
        self.sprite.updatePosition(x, y + z, self.renderingOrder)
        if self.object.data.shadow:
            self.shadowSprite.updatePosition(x, y, y)


class SkillLayeredEffect(SkillRender):

    @property
    def renderingOrder(self):
        if getDistanceBetweenTwoPoints(self.object.data.originalPosition, self.object.data.getPosition()) < 15:
            return self.object.getY() - self.object.getHeight() - 5
        else:
            return self.object.data.renderingOrder


class CustomEffectRender(EffectRender):

    def _create(self):
        group, batch = worldLayer.getLayerRender(LayerType.LAYERED, False)
        self._directionAnim = AnimDirection.FORWARD
        self.sheet = self.object.data.fileId
        self.sprite = PygletSheet((self.sheet), group=group, batch=batch)
        if self.object.data.flip_x == True or self.object.data.flip_y == True:
            self.sprite.setTransformation(self.sheet, 0, 0, self.object.data.flip_x, self.object.data.flip_y)
        self.sprite.renderingOrder = self.renderingOrder
        self.sprites.append(self.sprite)
        if self.object.data.shadow:
            self.shadowSprite = self._createShadow((self.sheet), group, batch, referencePoint=(self.object.data.refPointType))
            self.sprites.append(self.shadowSprite)
        if self.object.data.animation:
            self.object.data.animation.create(self.sheet)
            for sprite in self.sprites:
                sprite.setFrame(self.currentFrame.index)

    def _updatePosition(self):
        x, y, z = self.object.getPosition()
        self.sprite.setPosition(x, y + z, self.renderingOrder)
        if self.object.data.shadow:
            self.shadowSprite.setPosition(x, y, y)

    def setRenderPosition(self, x, y, z, interp):
        self.sprite.updatePosition(x, y + z, self.renderingOrder)
        if self.object.data.shadow:
            self.shadowSprite.updatePosition(x, y, y)


class CustomEffectImageRender(EffectRender):

    def _create(self):
        group, batch = worldLayer.getLayerRender(LayerType.LAYERED, False)
        self.sprite = PygletSprite((self.object.data.fileId), group=group,
          batch=batch,
          blend_src=(self.object.data.blend_src),
          blend_dest=(self.object.data.blend_dest))
        self.sprite.renderingOrder = self.renderingOrder
        self.sprites.append(self.sprite)
        if self.object.data.shadow:
            self.shadowSprite = self._createShadow((self.object.data.fileId), group, batch, referencePoint=(self.object.data.refPointType))
            self.sprites.append(self.shadowSprite)

    def _finalize(self):
        if self.object.data.hidden:
            WorldObjectRender.hide(self)

    def _updatePosition(self):
        x, y, z = self.object.getPosition()
        self.sprite.setPosition(x, y + z, self.renderingOrder)
        if self.object.data.shadow:
            self.shadowSprite.setPosition(x, y, y)

    def setRenderPosition(self, x, y, z, interp):
        self.sprite.updatePosition(x, y + z, self.renderingOrder)
        if self.object.data.shadow:
            self.shadowSprite.updatePosition(x, y, y)

    def resetFrame(self):
        return

    def hide(self, dt=None):
        WorldObjectRender.hide(self)


class MultiImageEffectRender(EffectRender):

    def _create(self):
        group, batch = None, worldLayer.transparentBatch
        self.sprite = MultiTextureSprite((self.object.data.fileId), group=group, batch=batch, program=(self.object.data.program))
        self.sprite.renderingOrder = self.renderingOrder
        self.sprites.append(self.sprite)
        if self.object.data.shadow:
            self.shadowSprite = self._createShadow((self.object.data.fileId), group, batch, referencePoint=(self.object.data.refPointType))
            self.sprites.append(self.shadowSprite)

    def _finalize(self):
        if self.object.data.hidden:
            WorldObjectRender.hide(self)

    def _updatePosition(self):
        x, y = self.object.getProjection2D()
        self.sprite.setPosition(x, y, renderingOrder=(self.renderingOrder))
        if self.object.data.shadow:
            sX, sY = self.object.getPosition2D()
            self.shadowSprite.setPosition(sX, sY + 10, sY - 1)

    def setRenderPosition(self, x, y, z, interp):
        self.sprite.setPositionInterpolate(x, y + z, self.renderingOrder)
        if self.object.data.shadow:
            self.shadowSprite.setPositionInterpolate(x, y + 10, y - 1)

    def hide(self, dt=None):
        WorldObjectRender.hide(self)


class LineEffectRender(EffectRender):

    def _create(self):
        group, batch = worldLayer.getLayerRender(LayerType.LAYERED, False)
        self.sprite = LineSprite((self.object.data.x), (self.object.data.y), color=(self.object.data.fileId), z=1, group=group, batch=batch)
        self.sprites.append(self.sprite)

    def _finalize(self):
        if self.object.data.hidden:
            WorldObjectRender.hide(self)

    def _updatePosition(self):
        x, y = self.object.getProjection2D()
        self.sprite.setPosition(x, y, renderingOrder=(self.renderingOrder))
        if self.object.data.shadow:
            sX, sY = self.object.getPosition2D()
            self.shadowSprite.setPosition(sX, sY + 10, sY - 1)

    def setRenderPosition(self, x, y, z, interp):
        self.sprite.update(x, y + z, self.renderingOrder)
        if self.object.data.shadow:
            self.shadowSprite.setPositionInterpolate(x, y + 10, y - 1, interp)

    def hide(self, dt=None):
        WorldObjectRender.hide(self)


class ShaderEffectRender(EffectRender):

    def _create(self):
        group, batch = worldLayer.getLayerRender(LayerType.LAYERED, False)
        self._directionAnim = AnimDirection.FORWARD
        if type(self.object.data.fileId) is str:
            image = cache.textureCache.getImageFile((self.object.data.fileId), atlas=False)
            self.sheet = Sheet(image, frames=(1, 1), referencePoint=(self.object.data.refPointType))
        else:
            self.sheet = self.object.data.fileId
        self.sprite = TimerTextureSheet((self.sheet), batch=batch)
        self.sprite.renderingOrder = self.renderingOrder
        self.sprites = [
         self.sprite]


class EmoteRender(EffectRender):

    def _create(self):
        group, batch = worldLayer.getLayerRender(LayerType.LAYERED, False)
        self.fileId = self.object.data.fileId
        self.sheet = cache.textureCache.getEmote(self.object.data.fileId)
        self.sheet.animationDelay = 0.8 / float(self.sheet.getFrameNbr() + 1)
        self.sprite = PygletSheet((self.sheet), group=group,
          batch=batch)
        if self.object.data.animation:
            self.object.data.animation.create(self.sheet)
        self.sprites = [
         self.sprite]

    def animateAndFunc(self, afterFunc):
        """ animate the sprite until the end of the frames. """
        delay = 0.8 / float(self.sheet.getFrameNbr() + 1)
        duration = 0.8
        self.runAnimation(delay, duration)

    def updateEmote(self, fileId):
        if self.fileId != fileId:
            self.sheet = cache.textureCache.getEmote(fileId)
            self.fileId = fileId
            self.sprite.setSheet(self.sheet)

    def replayAnimation(self):
        pyglet.clock.unschedule(self.animate)
        self._checkAnimation()

    def hide(self, dt=None):
        EffectRender.hide(self, dt=dt)


class WeatherEffectRender(EffectRender):
    __doc__ = " Effect for weather. it's in another layer, and it animates to the infinite. "

    def _create(self):
        group, batch = worldLayer.getLayerRender(LayerType.LAYERED, True)
        if type(self.object.data.fileId) is str:
            self.sheet = cache.textureCache.getEffect(self.object.data.fileId, self.object.data.refPointType)
        else:
            self.sheet = self.object.data.fileId
        self.sprite = PygletSheet((self.sheet), group=group, batch=batch)
        self.sprites = [
         self.sprite]
        if self.object.data.animation:
            self.object.data.animation.create(self.sheet)
            self.sprite.setFrame(self.currentFrame.index)
            self._checkAnimation()
        elif self.sheet.isAnimated():
            animationManager.register(self, self.object.getAnimationSpeed())

    def getSize(self):
        return (self.sheet.getWidth(), self.sheet.getHeight())

    def updateTexture(self):
        self.sheet = cache.textureCache.getEffect(self.object.data.fileId, self.object.data.refPointType)
        self.sprite.setSheet(self.sheet)

    def _addSprites(self, *sprites):
        (weatherLayer.add)(*sprites)

    def _delSprites(self, *sprites):
        (weatherLayer.delete)(*sprites)


class MapObjectRender(WorldObjectRender):

    def _create(self):
        gameMap = self.object.data.gameMap.render
        group, batch = gameMap.layers[LayerType.LAYERED_FIXED], gameMap.batch
        self.sheet = cache.textureCache.getMapObject(self.object.data.fileId, RefPointType.BOTTOMLEFT)
        self.sprite = PygletSheet((self.sheet), group=group, batch=batch)
        self.sprite.customSize = True
        if self.object.data.flipX or self.object.data.flipY:
            self.sprite.setTransformation(self.sheet, 0, 0, self.object.data.flipX, self.object.data.flipY)
            self.sprite.setFrame(0)
        self.sprites = [
         self.sprite]

    def _updatePosition(self):
        """ Note that fixed objects never change rendering order after inserted, don't need to update layer for it. """
        (self.sprite.setPosition)(*self.object.getProjection2D(), **{"renderingOrder": (self.object.data.renderingOrder)})

    def hide(self):
        WorldObjectRender.hide(self)
        if self.sheet.isAnimated():
            animationManager.unRegister(self, self.sheet.getAnimationDelay())

    def show(self):
        WorldObjectRender.show(self)
        self._checkAnimation()

    def _checkAnimation(self):
        if self.sheet.isAnimated():
            animationManager.register(self, self.sheet.getAnimationDelay())

    def stopAnimation(self):
        """ WARNING: Only to be used by map loading for performance.
        We add it here because loader cannot import animation Manager. """
        if self.sheet.isAnimated():
            animationManager.removeIfRegistered(self, self.sheet.getAnimationDelay())


shadow_adjustments = {'stone_01_02':(0, -2), 
 'stone_big_01':(0, -1), 
 'stone_big_02':(0, -2)}

class MapShadowObjectRender(MapObjectRender):
    __doc__ = " Object renderer for objects that have a shadow "

    def _create(self):
        gameMap = self.object.data.gameMap.render
        group, batch = gameMap.layers[LayerType.LAYERED_FIXED], gameMap.batch
        self.sheet = cache.textureCache.getMapObject(self.object.data.fileId, RefPointType.BOTTOMLEFT)
        self.shadowSprite = self._createShadow((self.sheet), group, batch, (RefPointType.BOTTOMLEFT), flip_x=(self.object.data.flipX))
        self.shadowSprite.customSize = True
        if self.object.data.fileId in shadow_adjustments:
            self.shadowSprite.offset = shadow_adjustments[self.object.data.fileId]
        self.sprite = PygletSheet((self.sheet), group=group, batch=batch)
        self.sprite.customSize = True
        if self.object.data.flipX or self.object.data.flipY:
            self.sprite.setTransformation(self.sheet, 0, 0, self.object.data.flipX, self.object.data.flipY)
            self.sprite.setFrame(0)
        self.sprites = [self.shadowSprite, self.sprite]

    def disableShadow(self):
        if not self.shadowSprite:
            raise Exception("This object has no shadow already.")
        self._delSprites(self.shadowSprite)

    def enableShadow(self):
        if not self.shadowSprite:
            raise Exception("This object has no shadow already.")
        self._addSprites(self.shadowSprite)

    def _updateSize(self):
        """ Update the size of all sprites for this object. """
        (self.sprite.setSize)(*self.object.getSize())

    def _updatePosition(self):
        """ Update the position of all sprites for this object. """
        x, y = self.object.getProjection2D()
        self.sprite.setPosition(x, y, self.object.data.renderingOrder)
        self.shadowSprite.setPosition(x, y, -LayerType.OBJECT_SHADOWS)


class MapTileset(PygletSprite):

    def __init__(self, gameMap, layer_type, *args, **kwargs):
        self.layer_type = layer_type
        if self.layer_type >= 20:
            zOrder = LayerType.ABOVE_PLAYER + self.layer_type
            batch = gameMap.render.aboveBatch
        else:
            zOrder = LayerType.GROUND_START + self.layer_type
            batch = gameMap.render.batch
        (super().__init__)(args, group=gameMap.render.layers[layer_type], subpixel=True, batch=batch, z=zOrder, **kwargs)

    def change_layer(self):
        group, batch = worldLayer.getLayerRender(self.layer_type)
        self.group = group
        self.batch = batch


class MapAutotile(PygletSheet):
    __doc__ = " Special Autotile. Animate does not need to update shape at all, saves some performance "

    def __init__(self, sheet, gameMap, layer_type, *args, **kwargs):
        self.layer_type = layer_type
        if self.layer_type >= 20:
            zOrder = LayerType.ABOVE_PLAYER + self.layer_type
        else:
            zOrder = LayerType.GROUND_START + self.layer_type
        (super().__init__)(sheet, *args, group=gameMap.render.layers[layer_type], subpixel=True, batch=gameMap.render.batch, z=zOrder, **kwargs)

    def isAnimated(self):
        return self.sheet.isAnimated()

    def change_layer(self):
        group, batch = worldLayer.getLayerRender(self.layer_type)
        self.group = group
        self.batch = batch

    def _checkAnimation(self):
        if self.sheet.isAnimated():
            delay = self.sheet.getAnimationDelay()
            self.setFrame(animationManager.getCurrentFrame(delay, self.sheet.frames[0]))
            animationManager.register(self, delay)

    def setInView(self):
        delay = self.sheet.getAnimationDelay()
        animationManager.register(self, delay)
        self.setFrame(animationManager.getCurrentFrame(delay, self.sheet.frames[0]))

    def setOutOfView(self):
        animationManager.unRegister(self, self.sheet.getAnimationDelay())

    def setFrame(self, col, row=0):
        self._frame_index = col
        self.image = self._textureGrid[self._frame_index]

    def stopAnimation(self):
        """ WARNING: Only to be used by map loading for performance.
        We add it here because loader cannot import animation Manager. """
        if self.sheet.isAnimated():
            animationManager.removeIfRegistered(self, self.sheet.getAnimationDelay())

    def startAnimation(self):
        self._checkAnimation()
