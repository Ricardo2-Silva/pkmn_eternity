# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\data\system\background.py
"""
Created on 22 juil. 2011

@author: Kami
"""
from client.data.gui.style import AnchorType
from client.data.utils.color import Color
from pyglet.gl.gl import GL_SRC_ALPHA, GL_FUNC_ADD, GL_ONE_MINUS_SRC_ALPHA

class BackgroundOption:
    __doc__ = " Defines the position and how it's stretched. "
    NORMAL = 1
    STRETCH = 2
    STRECH_IF_SMALLER = 16
    BEHIND_ALL = 4
    IN_FRONT = 8
    BETWEEN = 32


class BackgroundData:

    def __init__(self, id, name=None, color=Color.TRANSPARENT, option=BackgroundOption.IN_FRONT + BackgroundOption.STRETCH, anchor=AnchorType.CENTER, blending=(
 GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA), blendMode=GL_FUNC_ADD, alpha=255):
        self.option = option
        self.anchor = anchor
        self.blending = blending
        self.blendMode = blendMode
        self.color = color
        self.name = name
        self.id = id
        self.alpha = alpha
        if color == Color.TRANSPARENT:
            if name is None:
                raise Exception("This background have neither a picture nor a color.")

    def __repr__(self):
        return f"BackgroundData(id={self.id}, name={self.name}, color={self.color})"


blackFrontBackground = BackgroundData("black", Color.BLACK)
