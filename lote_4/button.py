# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\data\gui\button.py
"""
Created on 25 juil. 2011

@author: Kami
"""
from client.data.utils.utils import DynamicObject

class ButtonState:
    NORMAL = "normal"
    DISABLED = "disabled"
    OVER = "over"
    DOWN = "down"
    ALLSTATE = (NORMAL, OVER, DOWN, DISABLED)


class TextboxType:
    NORMAL = 1
    PASSWORD = 2
    RESET_ON_CLICK = 4
    NORMAL_RESET = 5
    PASSWORD_RESET = 6
    ONLY_INT = 7


class ButtonData(DynamicObject):

    def __init__(self, normal, over, down, disabled):
        self.normal = normal
        self.over = over
        self.down = down
        self.disabled = disabled


class PatchData(object):
    __slots__ = [
     "patch", "texture"]

    def __init__(self, patch, textureIdx):
        self.patch = patch
        self.texture = textureIdx


class ButtonPatchData(DynamicObject):

    def __init__(self, patch):
        self.normal = PatchData(patch, 0)
        self.over = PatchData(patch, 1)
        self.down = PatchData(patch, 2)
        self.disabled = PatchData(patch, 3)
