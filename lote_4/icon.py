# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\data\gui\icon.py
"""
Created on 25 juil. 2011

@author: Kami
"""
from client.render.cache import textureCache
from client.data.utils.color import Color
from client.data.utils.utils import DynamicObject
from client.data.utils.anchor import AnchorType
from client.data.gui.button import ButtonState

class IconData(DynamicObject):

    def __init__(self, texture):
        texture = self.checkTexture(texture)
        self.normal = texture
        self.over = texture
        self.down = texture
        self.disabled = texture

    def checkTexture(self, texture):
        if texture == None:
            return textureCache.getBackgroundColor(Color.TRANSPARENT)
        else:
            return texture

    def hasIcon(self):
        if self.normal == textureCache.getBackgroundColor(Color.TRANSPARENT):
            return False
        else:
            return True

    def textureMatches(self, texture):
        if self.normal == texture:
            return True
        else:
            return False

    def set(self, key, value):
        if key in ButtonState.ALLSTATE:
            value = self.checkTexture(value)
        if key == "anchor":
            if value == None:
                raise Exception("Anchor specified can't be none.")
        DynamicObject.set(self, key, value)


class IconDataAll(DynamicObject):

    def __init__(self, normal, over, down, disabled):
        self.normal = normal.get_texture()
        self.over = over.get_texture()
        self.down = down.get_texture()
        self.disabled = disabled.get_texture()

    def checkTexture(self, texture):
        if texture == None:
            return textureCache.getBackgroundColor(Color.TRANSPARENT)
        else:
            return texture

    def hasIcon(self):
        if self.normal == textureCache.getBackgroundColor(Color.TRANSPARENT):
            return False
        else:
            return True

    def textureMatches(self, texture):
        if self.normal == texture:
            return True
        else:
            return False

    def set(self, key, value):
        if key in ButtonState.ALLSTATE:
            value = self.checkTexture(value)
        if key == "anchor":
            if value == None:
                raise Exception("Anchor specified can't be none.")
        DynamicObject.set(self, key, value)
