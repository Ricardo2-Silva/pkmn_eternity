# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\render\gui\caret.py
"""
Created on Apr 19, 2019

@author: Admin
"""
import pyglet
from client.scene.manager import sceneManager
from client.render.sprite import GUIPygletSprite
from client.render.cache import textureCache
from client.data.gui.button import TextboxType
from shared.service.utils import clamp

class Caret(object):
    PERIOD = 0.5
    _blink_visible = True
    _active = False
    _visible = False
    invisible = (0, 0, 0, 0, 0, 0)

    def __init__(self, height, *args, **kwargs):
        self._x = 0
        self._y = 0
        self._z = 2999
        self.width = 1
        self.height = height
        self._batch = kwargs["batch"]
        self._group = kwargs["group"]
        self.vertex_list = self._batch.add(2, pyglet.gl.GL_LINES, self._group, (
         "v3i", (0, 0, self._z, self.width, self.height, self._z)), ('c4B', (255, 255, 255, 255, 255, 255, 255, 255)))
        self.visible = False

    @property
    def group(self):
        return self._group

    @group.setter
    def group(self, group):
        if self._group.parent == group:
            return
        self._group = group
        if self._batch is not None:
            self._batch.migrate(self.vertex_list, pyglet.gl.GL_LINES, self._group, self._batch)

    def get_vertices(self):
        if self._visible:
            return (self._x, self._y, self._z, self._x + self.width, self._y + self.height, self._z)
        else:
            return self.invisible

    def setPosition(self, x, y):
        if self._visible:
            self._x, self._y = sceneManager.convert(x, y)
            self.vertex_list.vertices[:] = self.get_vertices()

    def _blink(self, dt):
        if self.PERIOD:
            self._blink_visible = not self._blink_visible
        elif self._visible and self._blink_visible:
            alpha = 255
        else:
            alpha = 0
        self.vertex_list.colors[3] = alpha
        self.vertex_list.colors[7] = alpha

    def _set_visible(self, visible):
        self._visible = visible
        pyglet.clock.unschedule(self._blink)
        if visible:
            if self.PERIOD:
                pyglet.clock.schedule_interval(self._blink, self.PERIOD)
                self._blink_visible = False
        self.vertex_list.vertices[:] = self.get_vertices()
        self._blink(0)

    def _get_visible(self):
        return self._visible

    visible = property(_get_visible, _set_visible, doc="Caret visibility.\n\n    The caret may be hidden despite this property due to the periodic blinking\n    or by `on_deactivate` if the event handler is attached to a window.\n\n    :type: bool\n    ")

    def _set_color(self, color):
        self.vertex_list.colors[:3] = color
        self.vertex_list.colors[4:7] = color

    def _get_color(self):
        return self.vertex_list.colors[:3]

    color = property(_get_color, _set_color, doc="Caret color.\n\n    The default caret color is ``[0, 0, 0]`` (black).  Each RGB color\n    component is in the range 0 to 255.\n\n    :type: (int, int, int)\n    ")

    def setHeight(self, height):
        if self.height is not height:
            self.height = height
            self.vertex_list.vertices[:] = self.get_vertices()


class TextSelection(object):

    def __init__(self, group, batch, order=2998):
        self.startIndex = 0
        self.endIndex = 0
        self.highlightSprite = GUIPygletSprite((textureCache.getBackgroundColor((255,
                                                                                 255,
                                                                                 255)).get_region(0, 0, 1, 1)), z=order,
          group=group,
          batch=batch)
        self.highlightSprite.opacity = 100
        self.highlightSprite.visible = False

    @property
    def group(self):
        return self.highlightSprite.group

    @group.setter
    def group(self, group):
        self.highlightSprite.group = group

    def setFocus(self, textbox, index):
        """
         This sets where the highlight will appear and use the focused widget for it's settings.
        """
        self.textbox = textbox
        self.group = textbox.renderer.group
        self.endIndex = 0
        self.setStartIndex(index)
        if self.textbox.renderer.textSprite:
            self.highlightSprite.scale_y = self.textbox.renderer.textSprite.getHeight()
            self.highlightSprite.z = self.textbox.renderer.textSprite.z + 1

    def setStartIndex(self, i):
        self.startIndex = i
        self._updatePosition()
        self.highlightSprite.scale_x = 1
        return i

    def _updatePosition(self):
        x, y = self.textbox.x + self.textbox.renderer.textOffsetX, self.textbox.y + self.textbox.renderer.textOffsetY
        self.highlightSprite.setPosition(int(x + self.textbox.renderer.getTextWidth(self.text[:self.startIndex])), int(y))

    @property
    def text(self):
        if self.textbox.getIdRange() & TextboxType.NORMAL:
            return self.textbox.text
        else:
            if self.textbox.getIdRange() & TextboxType.PASSWORD:
                return self.textbox.getPassword()
            return self.textbox.text

    def hide(self):
        if self.highlightSprite:
            if self.highlightSprite.getWidth() != 0:
                self.highlightSprite.visible = False
                self.setStartIndex(0)
                self.endIndex = 0

    def getHighlightedText(self):
        if self.startIndex != self.endIndex:
            if self.endIndex >= self.startIndex:
                text = self.text[self.startIndex:self.endIndex]
            else:
                if self.endIndex <= self.startIndex:
                    text = self.text[self.endIndex:self.startIndex]
            return text
        else:
            return ""

    def getUnhighlightedText(self):
        if self.startIndex != self.endIndex:
            if self.endIndex >= self.startIndex:
                text = self.text[:self.startIndex] + self.text[self.endIndex:]
            else:
                if self.endIndex <= self.startIndex:
                    text = self.text[:self.endIndex] + self.text[self.startIndex:]
            return text
        else:
            return ""

    def updateHighlightWidth(self, index):
        self.endIndex = index
        width = self.textbox.renderer.getTextWidth(self.getHighlightedText())
        if width > 0:
            if self.highlightSprite.visible is False:
                self.highlightSprite.visible = True
            self.highlightSprite.scale_x = width
        elif self.endIndex <= self.startIndex:
            self.highlightSprite.image.anchor_x = width / self.highlightSprite.scale_x
        else:
            self.highlightSprite.image.anchor_x = 0
        if width == 0:
            self.highlightSprite.scale_x = 0.1
        self._updatePosition()
