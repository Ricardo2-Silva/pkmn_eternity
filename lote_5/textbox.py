# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\render\gui\textbox.py
"""
Created on May 31, 2016

@author: Admin
"""
from client.data.gui.button import TextboxType
from client.render.cache import textureCache
from client.render.sprite import GUIPygletSprite, TextSprite
from client.render.gui.core import BasicRender
from client.render.gui.button import ButtonRender
from client.render.utils.text import TextCursorRenderer, TextRender, TextRenderer
from shared.container.constants import RefPointType
import rabbyt, pyglet
from shared.service.utils import clamp
from client.render.gui.label import GDIPlusLabelRender
from client.control.utils.anchor import getAnchorOffsets, getAnchorOffsetsWidgetToSprite
from client.data.font import fontDB
from pyglet.gl.gl import GL_SCISSOR_TEST, glEnable, glScissor, glTranslatef, glDisable, glScalef
from client.data.settings import gameSettings
scaled_width, scaled_height = gameSettings.getScaledUIWindowResolution()
g_width, g_height = gameSettings.getWindowResolution()
scale = gameSettings.getUIScale()

class TextClipGroup(pyglet.graphics.Group):

    def __init__(self, widget, parent=None):
        pyglet.graphics.Group.__init__(self, parent=parent)
        self.widget = widget
        self.view_x = 0
        self.visible = self.widget.visible

    def set_state(self):
        glEnable(GL_SCISSOR_TEST)
        glScissor(int(self.widget.x * scale + self.widget.renderer.textOffsetX * scale), int(g_height - self.widget.top * scale), int(self.widget.getPaddedWidth() * scale), int(self.widget.height * scale))
        glTranslatef(-self.view_x, 0, 0)

    def unset_state(self):
        glTranslatef(self.view_x, 0, 0)
        glDisable(GL_SCISSOR_TEST)

    def __hash__(self):
        return hash(id(self))

    def __eq__(self, other):
        return False


class TextboxRender(GDIPlusLabelRender):

    def __init__(self, widget):
        self.textStyle = widget.getStyle().text
        self.textRender = TextCursorRenderer
        self.startIndex = 0
        self.endIndex = 0
        self.highlightSprite = None
        if widget.scrollable:
            self._group = TextClipGroup(widget, widget.parent.group)
        self._viewOffset = 0
        self.contentWidth = 0
        GDIPlusLabelRender.__init__(self, widget)
        self.textOffsetY = 2
        if self.widget.text:
            self.textSprite.setPosition(self.widget.x + self.textOffsetX, self.widget.y + self.textOffsetY)
            self.contentWidth = fontDB.get_width(self.textStyle.font, self.text)

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, visibility):
        self._visible = visibility
        for sprite in self.sprites:
            sprite.visible = visibility

        if self.widget.scrollable:
            if visibility is False:
                self._group.visible = False
            else:
                self._group.visible = True

    @property
    def viewOffset(self):
        return self._viewOffset

    @viewOffset.setter
    def viewOffset(self, value):
        self._viewOffset = max(0, min(self.contentWidth - self.widget.getPaddedWidth(), value))
        if self.widget.scrollable:
            self._group.view_x = self._viewOffset

    @property
    def group(self):
        if self.widget.scrollable:
            return self._group
        else:
            return self.widget.group

    @property
    def text(self):
        if self.widget.getIdRange() & TextboxType.NORMAL:
            return self.widget.text
        else:
            if self.widget.getIdRange() & TextboxType.PASSWORD:
                return self.widget.getPassword()
            return self.widget.text

    def basicRefresh(self):
        """ This function is to refresh the button without refreshing the text sprite.
            Refreshing text sprite should only happen if the text changes. """
        Style = self.widget.getStyle()
        self._refreshBackgroundSprites(Style.background)
        self.updatePosition()

    def _updateTextPosition(self):
        if self.textSprite:
            self.textSprite.setPosition(self.widget.x + self.textOffsetX, self.widget.y + self.textOffsetY)
            if self.widget.getStyle().text.shadow:
                self.shadowTextSprite.setPosition(self.widget.x + self.textOffsetX + 1, self.widget.y + self.textOffsetY + 1)

    def updatePosition(self):
        BasicRender.updatePosition(self)
        if self.textSprite:
            self._updateTextPosition()

    def refresh(self):
        BasicRender.refresh(self)
        if self.textSprite:
            self._refreshTextSprite(self.widget.getStyle().text)

    def calculateOffset(self):
        text_width = fontDB.get_width(self.widget.getStyle().text.font, self.widget.text[:self.widget.get_cursor()])
        self.offsetX = text_width
        if text_width <= self.viewOffset:
            self.viewOffset = text_width
        elif text_width >= self.viewOffset + self.widget.getPaddedWidth():
            self.viewOffset = text_width - self.widget.getPaddedWidth()
        elif text_width >= self.viewOffset + self.widget.getPaddedWidth():
            pass
        if self.contentWidth > self.widget.getPaddedWidth():
            self.viewOffset = text_width - self.widget.getPaddedWidth()

    def getTextWidth(self, text):
        return fontDB.get_width(self.textStyle.font, text)

    def getTextHeight(self):
        return self.textStyle.font.height

    def updateCaret(self):
        self.calculateOffset()
        x, y = self.widget.x + self.textOffsetX, self.widget.y + self.textOffsetY
        self.widget.caret.group = self.group
        if self.textSprite:
            self.widget.caret.setHeight(self.textSprite.getHeight())
            self.widget.caret.setPosition(int(x + self.offsetX), int(y + self.textSprite.getHeight()))
        else:
            self.widget.caret.setPosition(int(x + self.widget.getPadding().left), int(y + self.widget.caret.height + self.widget.getPadding().top))

    def getCursorPosition(self, x, y):
        """ Return the cursor position in the textbox """
        if self.widget.text:
            x = x - (self.widget.x + self.widget.getPadding().left)
        else:
            x = 0
        if x <= 0:
            return 0
        else:
            return self.textRender.findLetterPosition(self.textStyle, x + self.viewOffset, self.text)

    def _refreshTextSprite(self, textData):
        self.textSprite.text = self.text
        if textData.shadow:
            self.shadowTextSprite.text = self.text
        self.contentWidth = fontDB.get_width(textData.font, self.text)

    def _createTextSprite(self, textData):
        self.textSprite = TextSprite(text=(self.text), font_name=(textData.font.name),
          font_size=(textData.font.size),
          color=(textData.color + (255, )),
          z=(self.order + 3),
          group=(self.group),
          batch=(self.widget.batch))
        if textData.shadow:
            self.shadowTextSprite = TextSprite(text=(self.text), font_name=(textData.font.name),
              font_size=(textData.font.size),
              color=(textData.shadow.color + (255, )),
              z=(self.order + 2),
              group=(self.group),
              batch=(self.widget.batch))
            return [
             self.shadowTextSprite, self.textSprite]
        else:
            return [
             self.textSprite]
