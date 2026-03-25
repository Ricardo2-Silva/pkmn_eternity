# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\render\system\background.py
"""
Created on 22 juil. 2011

@author: Kami
"""
from twisted.internet import defer, reactor
from client.control.system.anims import AnimableRender, FadeColor, MultiParallelAnim, AnimCallable, Animable
from client.data.layer import LayerType
from client.data.settings import gameSettings
from client.data.system.background import BackgroundOption
from client.data.utils.color import Color
from client.render.cache import textureCache
from client.render.layer import backgroundLayer
from client.render.sprite import PygletBackgroundSprite
from client.render.world.object import SimpleRender

class FadeToOpacity(Animable):

    def init(self, target, alpha, duration, startAlpha=None):
        self.target = target
        self.duration = duration
        self.target_alpha = alpha
        if startAlpha:
            self.initial_alpha = startAlpha
        else:
            self.initial_alpha = target.opacity

    def update(self, t):
        self.target.opacity = self.initial_alpha + (self.target_alpha - self.initial_alpha) * t

    def __reversed__(self):
        return FadeToOpacity(self.target, self.initial_alpha, self.duration, self.target_alpha)


class BackgroundRender(SimpleRender):
    _total_bgs = []

    def __init__(self, background):
        super().__init__()
        self.object = background
        self.sprite = None
        self.batch = backgroundLayer.batch
        if self.object.data.option & BackgroundOption.BEHIND_ALL:
            self.order = LayerType.BACKGROUND_BEHIND
        if self.object.data.option & BackgroundOption.IN_FRONT:
            self.order = LayerType.BACKGROUND_MIDDLE + 10
            self.batch = backgroundLayer.frontBatch
        if self.object.data.option & BackgroundOption.BETWEEN:
            self.order = LayerType.BACKGROUND_MIDDLE
        self._create()
        self.visible = True

    def _startTransparency(self):
        """ When a sprite's alpha becomes 0 - 1 it needs to be rendered last- """
        AnimableRender._startTransparency(self)

    def _endTransparency(self):
        """ Restore a sprite to it's original opaque layer """
        AnimableRender._endTransparency(self)

    def setAlpha(self, alpha):
        self.sprite.opacity = alpha

    def hide(self):
        self.sprite.visible = False
        self.visible = False

    def show(self):
        self.sprite.visible = True
        self.visible = True

    def fadeColor(self, rgb, duration=1, startColor=None):
        anim = FadeColor(self.sprite, rgb, duration, startColor)
        self.startAnim(anim)
        return anim

    def _create(self):
        BackgroundRender._total_bgs.append(self.object.data)
        data = self.object.data
        if data.color != Color.TRANSPARENT:
            self.texture = textureCache.getBackgroundColor((255, 255, 255))
            self.sprite = PygletBackgroundSprite((self.texture), batch=(self.batch),
              z=(self.order + len(BackgroundRender._total_bgs)),
              blend_src=(self.object.data.blending[0]),
              blend_dest=(self.object.data.blending[1]))
            self.sprite.color = data.color
        elif data.name is str:
            self.texture = textureCache.getBackground(data.name)
        else:
            self.texture = data.name
        self.sprite = PygletBackgroundSprite((self.texture), batch=(self.batch),
          z=(self.order + len(BackgroundRender._total_bgs)),
          blend_src=(self.object.data.blending[0]),
          blend_dest=(self.object.data.blending[1]))
        width, height = gameSettings.getWindowResolution()
        if data.option & BackgroundOption.STRETCH:
            self.sprite.setScale(width / self.texture.width, height / self.texture.height)
        if data.option & BackgroundOption.STRECH_IF_SMALLER:
            if self.texture.width < width:
                self.sprite.scale_x = width / self.texture.width
            if self.texture.height < height:
                self.sprite.scale_y = height / self.texture.height
        if data.alpha != 255:
            self.sprite.opacity = data.alpha
        self.sprites = [self.sprite]

    def destroy(self):
        self.sprite.delete()

    def fadeInAndOut(self, inDuration, outDuration, inAlpha, outAlpha):
        """ Fading changes sprite color until set alpha """
        d = defer.Deferred()
        self.fading = True
        if self.sprites:
            self.stopAnims()
            self._startTransparency()
            anim = FadeToOpacity(self.sprite, inAlpha, inDuration, outAlpha)
            anim += FadeToOpacity(self.sprite, outAlpha, outDuration, inAlpha)
            anim += AnimCallable(d.callback, None)
            self.startAnim(anim)
        d.addCallback(self._stoppedFade)
        return d
