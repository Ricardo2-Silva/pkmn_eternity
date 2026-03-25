# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\data\gui\style.py
"""
Created on 30 juin 2011

@author: Kami
"""
from client.render.utils.patch import PatchType
from client.data.utils.color import Color
from .button import ButtonState
from client.data.utils.anchor import AnchorType
from .padding import defaultPadding
from client.data.gui.padding import PaddingData
from client.data.font import fontDB
import copy
defaultMargins = PaddingData(3, 3, 4, 4)

class ShadowType:
    NONE = 0
    FULL = 1
    MIN = 2
    FILL = 3


class BorderType:
    LINE = 1
    IMAGE = 2


class TextData(object):
    __slots__ = [
     'color', 'font', 'shadow', 'anchor', 'bold']

    def __init__(self, font=fontDB.getFont("default"), color=Color.BLACK, shadow=None, anchor=AnchorType.CENTER, bold=False):
        self.color = color
        self.font = font
        self.shadow = shadow
        self.anchor = anchor
        self.bold = bold

    def copy(self):
        data = TextData(self.font, self.color, self.shadow, self.anchor, self.bold)
        if self.shadow:
            data.shadow = self.shadow.copy()
        return data


class ShadowData(object):
    __slots__ = [
     "color", "type"]

    def __init__(self, color=Color.WHITE, type=ShadowType.MIN):
        self.color = color
        self.type = type

    def copy(self):
        return ShadowData(self.color, self.type)


class BorderData:

    def __init__(self, images=None, type=BorderType.LINE, color=Color.BLACK, padding=defaultPadding, top=True, left=True, bottom=True, right=True, alpha=255):
        self.images = images
        self.type = type
        self.color = color
        self.padding = padding
        self.top = top
        self.left = left
        self.bottom = bottom
        self.right = right
        self.alpha = alpha
        if self.images:
            self.type = BorderType.IMAGE

    def setImages(self, ninePatch):
        self.images = ninePatch
        self.type = BorderType.IMAGE

    def updateImages(self, ninePatch):
        self.images.update(ninePatch)

    def copy(self):
        return BorderData(self.images, self.type, self.color, self.padding, self.top, self.left, self.bottom, self.right, self.alpha)


class ButtonStyle:
    __doc__ = " A button has different styleData for its mode "

    def __init__(self, styleData=None, patchType=PatchType.NOPATCH):
        if not styleData:
            styleData = Style()
        self.setStyle(styleData)
        self.patchType = patchType

    def setTextColor(self, color):
        for buttonState in ButtonState.ALLSTATE:
            self.__dict__[buttonState].setTextColor(color)

    def setTextAnchor(self, anchor):
        for buttonState in ButtonState.ALLSTATE:
            self.__dict__[buttonState].setTextAnchor(anchor)

    def getStyle(self, mode):
        return self.__dict__[mode]

    def setStyle(self, styleData):
        self.over = styleData.copy()
        self.normal = styleData.copy()
        self.down = styleData.copy()
        self.disabled = styleData.copy()

    def setBackgroundColors(self, buttonBackgrounds):
        for buttonState in ButtonState.ALLSTATE:
            self.__dict__[buttonState].background.color = buttonBackgrounds.get(buttonState)

    def setTextColors(self, buttonColors):
        for buttonState in ButtonState.ALLSTATE:
            self.__dict__[buttonState].text = buttonColors.get(buttonState)

    def updateBackgroundImage(self, backgrounds):
        if self.patchType == PatchType.NOPATCH:
            raise Exception("updating texture for NOPATCH Must be implemented")
        for buttonState in ButtonState.ALLSTATE:
            backgroundData = self.__dict__[buttonState].background
            backgroundData.updateImages(backgrounds.get(buttonState))

    def setBackgroundImage(self, backgrounds):
        """ set the backgrounds images for a buttons. """
        self.background = backgrounds
        for buttonState in ButtonState.ALLSTATE:
            backgroundData = self.__dict__[buttonState].background
            if backgroundData is not None:
                self.__dict__[buttonState].background = backgroundData.copy()
            else:
                self.__dict__[buttonState].background = BackgroundData()
            backgroundData = self.__dict__[buttonState].background
            if self.patchType == PatchType.NOPATCH:
                backgroundData.image = backgrounds
                backgroundData.patchType = PatchType.NOPATCH
            else:
                backgroundData.image = backgrounds.get(buttonState)
                backgroundData.patchType = self.patchType

    def copy(self):
        style = ButtonStyle(self.normal, self.patchType)
        return style


class BarStyle:

    def __init__(self, patchType=PatchType.THREE, margins=defaultMargins, backgroundColor=None, borderImg=None, secondary=True):
        self.primaryColors = {}
        self.secondaryColors = {}
        self.useSecondary = secondary
        self.patchType = patchType
        if self.patchType == PatchType.THREE:
            if not borderImg:
                raise Exception("You must provide a border image if you use a three patch.")
        self.borderImg = borderImg
        self.margins = margins
        if backgroundColor is not None:
            if len(backgroundColor) != 3:
                raise Exception("Background color must be in r, g, b")
        self.backgroundColor = backgroundColor

    def setPrimaryColor(self, cRange, r, g, b):
        self.primaryColors[cRange] = (
         r, g, b)

    def setSecondaryColor(self, cRange, r, g, b):
        self.secondaryColors[cRange] = (
         r, g, b)

    def getPrimaryColor(self, per):
        for percent in sorted(self.primaryColors.keys()):
            if per <= percent / 100.0:
                return self.primaryColors[percent]

    def getSecondaryColor(self, per):
        for percent in sorted(self.secondaryColors.keys()):
            if per <= percent / 100.0:
                return self.secondaryColors[percent]

    def getColor(self, per):
        for percent in sorted(self.primaryColors.keys()):
            if per <= percent / 100.0:
                return self.primaryColors[percent]

    def copy(self):
        style = BarStyle(self.patchType, self.margins.copy(), self.backgroundColor, self.borderImg, self.useSecondary)
        for color in self.primaryColors:
            style.primaryColors[color] = copy.deepcopy(self.primaryColors[color])

        for color in self.secondaryColors:
            style.secondaryColors[color] = copy.deepcopy(self.secondaryColors[color])

        return style


class BackgroundData:
    __slots__ = [
     'color', 'image', 'anchor', 'patchType', 'alpha']

    def __init__(self, color=None, image=None, anchor=AnchorType.TOPLEFT, patchType=PatchType.FOUR_IMAGE, alpha=255):
        self.color = color
        self.image = image
        self.anchor = anchor
        self.patchType = patchType
        self.alpha = alpha

    def updateImages(self, images):
        self.image.update(images)

    def copy(self):
        return BackgroundData(self.color, self.image, self.anchor, self.patchType, self.alpha)


defaultBackground = BackgroundData(Color.TRANSPARENT)

class Style:
    __slots__ = [
     'border', 'background', 'text', 'padding', 'padding', 'margins']

    def __init__(self, background=defaultBackground, border=None, text=None, padding=defaultPadding, margins=defaultMargins):
        if border:
            border = border.copy()
        else:
            if text:
                text = text.copy()
            if padding:
                padding = padding.copy()
            if background:
                background = background.copy()
        self.border = border
        self.background = background
        self.text = text
        self.padding = padding
        self.margins = margins

    def setTextColor(self, color):
        self.text.color = color

    def setTextAnchor(self, anchor):
        self.text.anchor = anchor

    def copy(self):
        """ Copy the style, so it's not overridden. """
        if self.border:
            border = self.border.copy()
        else:
            border = None
        if self.background:
            background = self.background.copy()
        else:
            background = None
        if self.text:
            text = self.text.copy()
        else:
            text = None
        return Style(background, border, text, self.padding.copy(), self.margins.copy())


class PictureStyle:
    __slots__ = [
     "margins"]

    def __init__(self, margins=defaultMargins):
        self.margins = margins

    def copy(self):
        return PictureStyle(self.margins)
