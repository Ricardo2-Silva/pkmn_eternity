# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\render\system\light.py
"""
Created on Oct 11, 2015

@author: Admin
"""
from client.render.layer import lightLayer, worldLayer
from rabbyt.anims import lerp
from twisted.internet import reactor, defer
from client.render.cache import textureCache
from client.render.sprite import PygletSprite
from client.scene.manager import sceneManager
from shared.container.constants import RefPointType
from client.data.layer import LayerType
from client.control.system.anims import ScaleBy, AnimCallable, ScaleTo, MultiParallelAnim
from client.render.world.object import SimpleRender

class LightRender(SimpleRender):

    def __init__(self, object):
        SimpleRender.__init__(self)
        self.object = object
        self.sprites = []
        self.visible = False
        self._initiate()

    def _initiate(self):
        self._create()
        self._updatePosition()
        self._finalize()

    def setSize(self, width, height):
        self.sprite.setSize(width, height)

    def pulse(self, pulseCount, duration, scale=1.2):
        """ If no duration, pulse forever """
        original_scale = self.sprite.scale
        anim = ScaleTo(self.sprite, original_scale, scale, duration / 2)
        anim += reversed(anim)
        anim *= pulseCount
        if pulseCount > 0:

            def resetScale(sprite, scale):
                sprite.scale = scale

            anim += AnimCallable(resetScale, self.sprite, original_scale)
        self.startAnim(anim)
        return anim

    def hide(self):
        self.visible = False
        self.sprite.visible = False

    def show(self):
        self.visible = True
        self.sprite.visible = True

    def setColor(self, r, g, b):
        self.sprite.setColor(r, g, b)

    def setAlpha(self, alpha):
        self.sprite.setAlpha(alpha)

    def lerpColor(self, r, g, b, a=255, dt=1):
        self.sprite.lerpColor(r, g, b, a, dt)
        d = defer.Deferred()
        self.fading = True
        self._startTransparency()
        anim = MultiParallelAnim(self.sprites, Color, toAlpha, duration)
        anim += AnimCallable(d.callback, None)
        self.startAnim(anim)
        d.addCallback(self._stoppedFade)
        return d

    def destroy(self):
        """ Destroy the sprite. Take it out from the layer, also unload it SOMETIMES. """
        self.hide()

    def getSize(self):
        return self.sprite.getSize()

    def _create(self):
        self.texture = textureCache.getLight(self.object.data.fileId)
        group, batch = worldLayer.getLayerRender(LayerType.LIGHT, False)
        self.sprite = PygletSprite((self.texture), group=group, batch=batch)
        self.sprite.visible = False
        self.sprites = [self.sprite]

    def _finalize(self):
        return

    def resetRenderState(self):
        self.sprite.resetRenderState()

    def _updatePosition(self):
        """ Update the position of all sprites for this object. """
        (self.sprite.setPosition)(*self.object.data.getPosition())

    def setRenderPosition(self, interp):
        x, y = self.object.data.getPosition()
        self.sprite.setPositionInterpolate(x, y, y, interp)
