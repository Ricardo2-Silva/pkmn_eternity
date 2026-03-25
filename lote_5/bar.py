# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\render\gui\bar.py
"""
Created on May 31, 2016

@author: Admin
"""
from client.render.utils.patch import PatchType, ThreePatch
from client.render.sprite import PatchSprite, PatchSpriteRound
from client.render.cache import textureCache
from client.render.gui.core import BasicRender
from client.data.gui.padding import PaddingData

class BarRender(BasicRender):

    def _createBackgroundSprites(self, style):
        self.backgroundSprite = self.spriteClass((textureCache.getBackgroundColor(style.backgroundColor)), z=(self.order + 1),
          group=(self.widget.group),
          batch=(self.widget.batch))
        return self.backgroundSprite

    def _createBorderSprites(self, style):
        ninepatch = style.borderImg
        self.borderSprite = PatchSpriteRound(ninepatch, padding=(PaddingData(1, 1, 1, 1)),
          x=(self.widget.x),
          y=(self.widget.y),
          z=(self.order + 2),
          width=(self.widget.width),
          height=(self.widget.height),
          batch=(self.widget.transparentBatch),
          group=(self.widget.group))
        return self.borderSprite

    def _createBarSprites(self, style):
        sprites = []
        self.fillColorSprite = self.spriteClass((textureCache.getBackgroundColor((255,
                                                                                  255,
                                                                                  255))), z=(self.order + 2),
          group=(self.widget.group),
          batch=(self.widget.batch))
        sprites.append(self.fillColorSprite)
        if style.useSecondary:
            self.fillColorSprite2 = self.spriteClass((textureCache.getBackgroundColor((255,
                                                                                       255,
                                                                                       255))), z=(self.order + 2),
              group=(self.widget.group),
              batch=(self.widget.batch))
            sprites.append(self.fillColorSprite2)
        return sprites

    def initiate(self):
        style = self.widget.getStyle()
        if style.backgroundColor:
            self.sprites.append(self._createBackgroundSprites(style))
        if style.borderImg:
            self.sprites.append(self._createBorderSprites(style))
        self.sprites.extend(self._createBarSprites(style))
        self.updatePosition()
        self.updateSize()

    def setColor(self, r, g, b):
        return

    def setBarColor(self, per):
        style = self.widget.getStyle()
        (self.setPrimaryColor)(*style.getPrimaryColor(per))
        if style.useSecondary:
            (self.setSecondaryColor)(*style.getSecondaryColor(per))

    def setPrimaryColor(self, r, g, b):
        self.fillColorSprite.setColor(r, g, b)

    def setSecondaryColor(self, r, g, b):
        self.fillColorSprite2.setColor(r, g, b)

    def _updateBackgroundColor(self):
        style = self.widget.getStyle()
        if style.backgroundColor:
            (self.backgroundSprite.setColor)(*style.backgroundColor)

    def _updateBackgroundSize(self):
        style = self.widget.getStyle()
        if style.patchType == PatchType.THREE:
            if style.backgroundColor:
                self.backgroundSprite.setSize(self.widget.width, self.widget.height)
            self.borderSprite.setSize(self.widget.width, self.widget.height)
        else:
            if style.backgroundColor:
                self.backgroundSprite.setSize(self.widget.width, self.widget.height)
        self.setPercent(self.widget.getPercent())

    def _updateBackgroundPosition(self):
        style = self.widget.getStyle()
        if style.backgroundColor:
            (self.backgroundSprite.setPosition)(*self.widget.position)
        if style.patchType == PatchType.THREE:
            (self.borderSprite.setPosition)(*self.widget.position)
        (self.fillColorSprite.setPosition)(*self.widget.position)
        if style.useSecondary:
            self.fillColorSprite2.setPosition(self.widget.x, self.widget.y + self.fillColorSprite.height)

    def _updateBackgroundRenderPosition(self, interp):
        style = self.widget.getStyle()
        if style.backgroundColor:
            (self.backgroundSprite.setPositionInterpolate)(*(self.widget).position, **{"interp": interp})
        if style.patchType == PatchType.THREE:
            (self.borderSprite.setPositionInterpolate)(*(self.widget).position, **{"interp": interp})
        (self.fillColorSprite.setPositionInterpolate)(*(self.widget).position, **{"interp": interp})
        if style.useSecondary:
            self.fillColorSprite2.setPositionInterpolate((self.widget.x), (self.widget.y + self.fillColorSprite.height), interp=interp)

    def updatePosition(self):
        self._updateBackgroundPosition()

    def setRenderPosition(self, interp):
        self._updateBackgroundRenderPosition(interp)

    def updateSize(self):
        self._updateBackgroundSize()
        self.updatePosition()

    def setPercent(self, per):
        style = self.widget.getStyle()
        if style.useSecondary:
            primaryHeight = int(0.7 * self.widget.height)
            secondaryHeight = int(0.3 * self.widget.height)
        else:
            primaryHeight = self.widget.height
        self.fillColorSprite.setSize(self.widget.width * per, primaryHeight)
        if style.useSecondary:
            self.fillColorSprite2.setSize(self.widget.width * per, secondaryHeight)

    def refresh(self):
        self.updateSize()
        self._updateBackgroundColor()
