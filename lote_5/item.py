# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\render\world\item.py
"""
Created on 19 juil. 2011

@author: Kami
"""
import client.render.cache as cache, client.render.sprite as iSprite
from client.render.layer import worldLayer
from client.data.layer import LayerType
from client.render.world.object import WorldObjectRender, getShadowPosition
from shared.container.constants import RefPointType, Pokeball
from client.control.system.anims import Lerp, FadeColor, AnimCallable, Delay
from client.data.sprite import setAnchorPoint

class ItemRender(WorldObjectRender):

    def __init__(self, object):
        self.onSpecialGround = 0
        WorldObjectRender.__init__(self, object)

    def setRenderingOrder(self, renderingOrder):
        for sprite in self.sprites:
            sprite.renderingOrder = renderingOrder

        self._updatePosition()

    def _create(self):
        group, batch = worldLayer.getLayerRender(LayerType.LAYERED, False)
        self.texture = cache.textureCache.getItemIcon(self.object.data.fileId)
        setAnchorPoint(self.texture, RefPointType.BOTTOMCENTER)
        self.sprite = iSprite.PygletSprite((self.texture), batch=batch)
        self.sprite.scale = 0.5
        self.shadowSprite = self._createShadow(self.texture, group, batch)
        self.shadowSprite.scale = 0.5
        self.sprites = [self.shadowSprite, self.sprite]

    def _createShadow(self, texture, group, batch, referencePoint=RefPointType.CENTER, flip_x=False, frame=0):
        """ Add a shadow to the sprite. """
        group, batch = worldLayer.getLayerRender(LayerType.LAYERED, True)
        shadowSprite = iSprite.PygletSprite(texture, group=group, batch=batch)
        shadowSprite.z_offset = -1
        shadowSprite.setRGBA(0, 0, 0, 50)
        shadowSprite.setScale(0.95, 0.4)
        return shadowSprite

    def _updatePosition(self):
        """ Update the position of all sprites for this object. """
        x, y, z = self.object.getPosition()
        self.sprite.setPosition(x, y + z, y)
        self.shadowSprite.setPosition(x, y, y)

    def setRenderPosition(self, x, y, z, interp):
        self.sprite.updatePosition(x, y + z, y)
        self.shadowSprite.updatePosition(x, y, y)

    def rotate(self, duration, speed):
        anim = Lerp(self.sprite, "rotation", 0, round(duration / speed) * 360, duration)
        self.startAnim(anim)
        return anim

    def getSize(self, *sprites):
        """ Add the sprite to the layer. """
        return self.sprite.getSize()

    def updateSize(self):
        width, height = self.object.getSize()
        self.sprite.setSize(width, height)
        self._updatePosition()

    def setEnvironment(self):
        if not self.fading:
            if self.onSpecialGround > 1:
                self.sprite.setAlpha(60)
                self.shadowSprite.setAlpha(0)
            else:
                self.sprite.setAlpha(255)
                self.shadowSprite.setAlpha(50)

    def setOnGround(self, groundType):
        self.onSpecialGround = groundType
        self.setEnvironment()

    def setOffGround(self):
        self.onSpecialGround = 0
        self.setEnvironment()


class ItemDropRender(ItemRender):

    def _create(self):
        group, batch = worldLayer.getLayerRender(LayerType.LAYERED, False)
        sheet = cache.textureCache.getMapObject("zitems/item_drop", RefPointType.BOTTOMCENTER)
        self.texture = sheet.texture
        setAnchorPoint(self.texture, RefPointType.BOTTOMCENTER)
        self.sprite = iSprite.PygletSprite((self.texture), batch=batch)
        self.shadowSprite = self._createShadow(self.texture, group, batch)
        self.sprites = [self.shadowSprite, self.sprite]


class BallRender(ItemRender):

    def _create(self):
        group, batch = worldLayer.getLayerRender(LayerType.LAYERED, False)
        self.sheet = cache.textureCache.getBall(Pokeball.toGraphicId.get(self.object.data.fileId, 1))
        self.sprite = iSprite.PygletSheet((self.sheet), batch=batch, group=group)
        self.shadowSprite = self._createShadow(self.sheet, group, batch)
        self.sprites = [self.shadowSprite, self.sprite]

    def flashColor(self, r, g, b):
        anim = FadeColor(self.sprite, self.sprite.color, 1, (r, g, b))
        self.startAnim(anim)
        return anim

    def _createShadow(self, texture, group, batch, referencePoint=RefPointType.CENTER, flip_x=False, frame=0):
        return WorldObjectRender._createShadow(self, texture, group, batch, referencePoint=referencePoint, flip_x=flip_x, frame=frame)

    def _updatePosition(self):
        """ Update the position of all sprites for this object. """
        x, y, z = self.object.getPosition()
        self.sprite.setPosition(x, y + z, y)
        self.shadowSprite.setPosition(x, y - self.sprite.height // 2, y)

    def setRenderPosition(self, x, y, z, interp):
        self.sprite.updatePosition(x, y + z, y)
        self.shadowSprite.updatePosition(x, y - self.sprite.height // 2, y)

    def setOnGround(self, groundType):
        self.onSpecialGround = groundType
        self.setEnvironment()
        self._startTransparency()
        x, y, z = self.object.getPosition()
        self.sprite.setPosition(x, y + z, y + 1)
        shadowY = y - self.sprite.height // 2
        self.shadowSprite.setPosition(x, shadowY, y + 2)

    def tremble(self, repeat=5):
        if repeat <= 0:
            return
        else:
            anim = Lerp((self.sprite), "rotation", 0, 20, duration=0.05)
            anim += AnimCallable(self.object.sound.playSound, "Ball Shake")
            anim += Lerp((self.sprite), "rotation", 20, (-20), duration=0.3)
            anim += Lerp((self.sprite), "rotation", (-20), 1, duration=0.05)
            anim += Delay(0.3)
            anim *= repeat
            self.startAnim(anim)
            return anim
