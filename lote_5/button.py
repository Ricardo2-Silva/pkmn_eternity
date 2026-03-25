# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\render\gui\button.py
"""
Created on May 31, 2016

@author: Admin
"""
from client.control.utils.anchor import getAnchorOffsets, getAnchorOffsetsWidgetToSprite
from client.render.sprite import GUIPygletSprite
from client.render.gui.label import LabelRender
from client.render.gui.core import BasicRender
from client.data.gui import styleDB

class ButtonRender(LabelRender):

    def basicRefresh(self):
        """ This function is to refresh the button without refreshing the text sprite.
            Refreshing text sprite should only happen if the text changes. """
        Style = self.widget.getStyle()
        self._refreshBackgroundSprites(Style.background)
        self.updatePosition()


class CheckboxRender(ButtonRender):
    return


class IconButtonRender(ButtonRender):

    def __init__(self, widget):
        self.iconRx = 0
        self.iconRy = 0
        ButtonRender.__init__(self, widget)

    def initiate(self):
        BasicRender.initiate(self)
        if self.widget.iconData:
            self.sprites.append(self._createIconSprite())
        if self.widget.text:
            self.createAndAddText()

    def createAndAdd(self):
        """ Only do this when the icon doesn't exist after creation and then you update and add one.
         We add the sprite before text so text can appear over (If it exists).
        """
        self._addSpriteToList(self._createIconSprite())

    def _addSpriteToList(self, iconSprite):
        if self.widget.iconAlwaysBottom:
            self.sprites.insert(0, iconSprite)
        elif self.widget.text:
            if self.shadowSprites:
                idx = self.sprites.index(self.shadowSprites[0])
            else:
                idx = self.sprites.index(self.textSprite)
            self.sprites.insert(idx, iconSprite)
        else:
            self._addSprites(iconSprite)
        self._checkVisibility()

    def setColor(self, r, g, b):
        if self.widget.iconData:
            self.iconSprite.setColor(r, g, b)

    def setIconSize(self, width, height):
        self.iconSprite.setSize(width, height)

    def setIconRelativePosition(self):
        if self.widget.iconData:
            offx, offy = getAnchorOffsetsWidgetToSprite(self.widget, self.iconSprite, self.widget.iconAnchor, self.widget.getPadding())
            offx += self.widget.getPadding().left
            offy += self.widget.getPadding().top
            self.iconRx, self.iconRy = offx, offy

    def _createIconSprite(self):
        self.iconSprite = GUIPygletSprite((self.widget.iconData.get(self.widget.getState())), z=(self.initialOrder),
          group=(self.widget.group),
          batch=(self.widget.batch))
        return self.iconSprite

    def removeIcon(self):
        self.iconSprite.visible = False
        self.sprites.remove(self.iconSprite)

    def updateIconSprite(self):
        if self.widget.iconData:
            icon = self.widget.iconData.get(self.widget.getState())
            if icon == self.iconSprite.image:
                return
            if self.iconSprite:
                if self.iconSprite not in self.sprites:
                    self._addSpriteToList(self.iconSprite)
            old_image = self.iconSprite.image
            self.iconSprite.image = icon
            width, height = ButtonRender.getSize(self)
            if icon.width != width or icon.height != height:
                self.setIconRelativePosition()
                self.updateIconPosition()

    def updateIconPosition(self):
        if self.widget.iconData:
            self.iconSprite.setPosition(self.widget.x + self.iconRx, self.widget.y + self.iconRy)

    def updatePosition(self):
        self.updateIconPosition()
        ButtonRender.updatePosition(self)

    def updateSize(self):
        self.setIconRelativePosition()
        ButtonRender.updateSize(self)

    def refresh(self):
        self.updateIconSprite()
        self.updateIconPosition()
        ButtonRender.refresh(self)

    def getSize(self):
        width, height = ButtonRender.getSize(self)
        if self.widget.iconData:
            return (max(self.iconSprite.getWidth(), width), max(self.iconSprite.getHeight(), height))
        else:
            return (
             width, height)
