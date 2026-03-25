# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\render\gui\label.py
"""
Created on May 31, 2016

@author: Admin
"""
from client.control.utils.anchor import getAnchorOffsetsWidgetToSprite
from client.data.gui.style import ShadowType
from client.render.gui.core import BasicRender
from client.render.sprite import TextSprite, SpellingTextSprite
from client.render.utils.text import TextRenderer
counter = 0

class GDIPlusLabelRender(BasicRender):
    textClass = TextSprite

    def __init__(self, widget):
        self.textOffsetX = 0
        self.textOffsetY = 0
        self.textSprite = None
        self.shadowSprites = []
        BasicRender.__init__(self, widget)

    def initiate(self):
        BasicRender.initiate(self)
        if self.widget.text:
            self.createAndAddText()

    def createAndAddText(self):
        self.sprites.extend(self._createTextSprite(self.widget.getStyle().text))
        self._checkVisibility()

    def calculateSize(self, text):
        return TextRenderer.calculateSize(self.widget.getStyle().text.font, text)

    def _createTextSprite(self, textData):
        if self.widget.isAutoResizeWidth():
            width = None
        else:
            padding = self.widget.getPadding()
            width = self.widget.width - padding.left - padding.right
        if self.widget.isAutoResizeHeight():
            height = None
        else:
            height = self.widget.height
        self.textSprite = self.textClass(text=(self.widget.text), font_name=(textData.font.name),
          font_size=(textData.font.size),
          bold=(textData.bold),
          color=(textData.color + (255, )),
          z=(self.initialOrder + 1),
          width=width,
          height=height,
          align=(self.widget.alignment),
          multiline=(self.widget.multiline),
          anchor_x=(self.widget.anchor_x),
          anchor_y=(self.widget.anchor_y),
          group=(self.widget.group),
          batch=(self.widget.batch))
        if textData.shadow:
            if textData.shadow.type == ShadowType.MIN:
                sprites = 1
            else:
                if textData.shadow.type == ShadowType.FULL:
                    sprites = 4
            for i in range(sprites):
                self.shadowSprites.append(self.textClass(text=(self.widget.text), font_name=(textData.font.name),
                  font_size=(textData.font.size),
                  bold=(textData.bold),
                  color=(textData.shadow.color + (255, )),
                  z=(self.initialOrder),
                  width=width,
                  height=height,
                  align=(self.widget.alignment),
                  multiline=(self.widget.multiline),
                  anchor_x=(self.widget.anchor_x),
                  anchor_y=(self.widget.anchor_y),
                  group=(self.widget.group),
                  batch=(self.widget.batch)))

            return [
             *self.shadowSprites, self.textSprite]
        else:
            return [
             self.textSprite]

    def setTextColor(self, color):
        self.textSprite.color = color + (int(self.textSprite.opacity),)

    def _refreshTextSprite(self, textData):
        self.textSprite.text = self.widget.text
        if textData.shadow:
            for sprite in self.shadowSprites:
                sprite.text = self.widget.text

    def refreshStyle(self):
        textData = self.widget.getStyle().text
        self.textSprite.color = textData.color + (255, )
        if textData.shadow:
            for sprite in self.shadowSprites:
                sprite.color = textData.shadow.color + (255, )

    def updateSize(self):
        BasicRender.updateSize(self)
        self.setTextAnchorPosition()

    def setTextAnchors(self, anchor_x, anchor_y):
        """Set the Label anchors directly through Pyglet."""
        for sprite in self.sprites:
            sprite.anchor_x = anchor_x
            sprite.anchor_y = anchor_y

    def _updateTextPosition(self):
        if self.widget.text:
            self.textSprite.setPosition(self.widget.x + self.textOffsetX, self.widget.y + self.textOffsetY)
            shadow = self.widget.getStyle().text.shadow
            if shadow:
                if shadow.type == ShadowType.MIN:
                    self.shadowSprites[0].setPosition(self.widget.x + self.textOffsetX + 1, self.widget.y + self.textOffsetY + 1)
                elif shadow.type == ShadowType.FULL:
                    self.shadowSprites[0].setPosition(self.widget.x + self.textOffsetX + 1, self.widget.y + self.textOffsetY)
                    self.shadowSprites[1].setPosition(self.widget.x + self.textOffsetX - 1, self.widget.y + self.textOffsetY)
                    self.shadowSprites[2].setPosition(self.widget.x + self.textOffsetX, self.widget.y + self.textOffsetY + 1)
                    self.shadowSprites[3].setPosition(self.widget.x + self.textOffsetX, self.widget.y + self.textOffsetY - 1)
            elif shadow.type == ShadowType.FILL:
                self.shadowSprites[0].setPosition(self.widget.x + self.textOffsetX, self.widget.y + self.textOffsetY)

    def _updateTextPositionRender(self, interp):
        if self.widget.text:
            self.textSprite.setPositionInterpolate(self.widget.x + self.textOffsetX, self.widget.y + self.textOffsetY, interp)
            shadow = self.widget.getStyle().text.shadow
            if shadow:
                if shadow.type == ShadowType.MIN:
                    self.shadowSprites[0].setPositionInterpolate(self.widget.x + self.textOffsetX + 1, self.widget.y + self.textOffsetY + 1, interp)
                elif shadow.type == ShadowType.FULL:
                    self.shadowSprites[0].setPositionInterpolate(self.widget.x + self.textOffsetX + 1, self.widget.y + self.textOffsetY, interp)
                    self.shadowSprites[1].setPositionInterpolate(self.widget.x + self.textOffsetX - 1, self.widget.y + self.textOffsetY, interp)
                    self.shadowSprites[2].setPositionInterpolate(self.widget.x + self.textOffsetX, self.widget.y + self.textOffsetY + 1, interp)
                    self.shadowSprites[3].setPositionInterpolate(self.widget.x + self.textOffsetX, self.widget.y + self.textOffsetY - 1, interp)
            elif shadow.type == ShadowType.FILL:
                self.shadowSprites[0].setPositionInterpolate(self.widget.x + self.textOffsetX, self.widget.y + self.textOffsetY, interp)

    def setTextAnchorPosition(self):
        if self.widget.text:
            offx, offy = getAnchorOffsetsWidgetToSprite(self.widget, self.textSprite, self.widget.getStyle().text.anchor, self.widget.getPadding())
            offx += self.widget.getPadding().left
            offy += self.widget.getPadding().top
            if self.textOffsetX != offx or self.textOffsetY != offy:
                self.textOffsetX, self.textOffsetY = offx, offy
                self._updateTextPosition()

    def updatePosition(self):
        self._updateTextPosition()
        BasicRender.updatePosition(self)

    def setRenderPosition(self, interp):
        self._updateTextPositionRender(interp)
        BasicRender.setRenderPosition(self, interp)

    def refresh(self):
        if self.textSprite:
            self._refreshTextSprite(self.widget.getStyle().text)
            BasicRender.refresh(self)

    def getSize(self):
        """ return the size of the render """
        width, height = BasicRender.getSize(self)
        if self.widget.text:
            height = max(height, self.textSprite.content_height)
            width = max(width, self.textSprite.content_width)
        return (width, height)

    def destroy(self):
        BasicRender.destroy(self)


class SpellingLabelRender(GDIPlusLabelRender):
    textClass = SpellingTextSprite


class LabelRender(GDIPlusLabelRender):
    return


class TitleRender(GDIPlusLabelRender):

    def _createTextSprite(self, textData):
        self.textSprite = TextSprite(text=(self.widget.text), font_name=(textData.font.name),
          font_size=(textData.font.size),
          color=(textData.color + (255, )),
          z=(self.initialOrder + 1),
          group=(self.widget.group),
          batch=(self.widget.batch))
        if textData.shadow:
            self.shadowSprites.append(TextSprite(text=(self.widget.text), font_name=(textData.font.name),
              font_size=(textData.font.size),
              color=(textData.shadow.color + (255, )),
              z=(self.initialOrder),
              group=(self.widget.group),
              batch=(self.widget.batch)))
            return [
             *self.shadowSprites, self.textSprite]
        else:
            return [
             self.textSprite]


class ChatRender(GDIPlusLabelRender):

    def _createTextSprite(self, textData):
        self.textSprite = TextSprite(text=(self.widget.text), font_name=(textData.font.name),
          font_size=(textData.font.size),
          color=(textData.color + (255, )),
          z=(self.initialOrder),
          group=(self.widget.group),
          batch=(self.widget.batch))
        return [
         self.textSprite]

    def _updateTextPosition(self):
        if self.widget.text:
            self.textSprite.setPosition(self.widget.x + self.textOffsetX, self.widget.y - self.textOffsetY)

    def refresh(self):
        style = self.widget.getStyle()
        self._refreshTextSprite(style.text)
        self._refreshBackgroundSprites(style.background)
        self._updateBackgroundSize(style.background)
        self._updateBorderSize(style.border)

    def updatePosition(self):
        GDIPlusLabelRender.updatePosition(self)

    def _refreshTextSprite(self, textData):
        self.textSprite.text = self.widget.text

    def _updateBackgroundPosition(self, backgroundData):
        GDIPlusLabelRender._updateBackgroundPosition(self, backgroundData)
        return


# global counter ## Warning: Unused global
