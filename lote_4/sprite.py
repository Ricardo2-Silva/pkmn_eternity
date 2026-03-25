# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\data\sprite.py
"""
Created on 14 juil. 2011

@author: Kami
"""
import pyglet
from client.data.world.animation import AnimationSpeed
from pyglet.image import TextureRegion, TextureGrid, ImageGrid
from shared.container.constants import CreatureAction, RefPointType
from operator import attrgetter
import sys

class TopLeftTextureGrid(pyglet.image.TextureGrid):

    def __init__(self, grid):
        image = grid.get_texture()
        if isinstance(image, TextureRegion):
            owner = image.owner
        else:
            owner = image
        super(TextureGrid, self).__init__(image.x, image.y, image.z, image.width, image.height, owner)
        items = []
        y = image.height - grid.item_height
        for row in range(grid.rows):
            x = 0
            for col in range(grid.columns):
                items.append(self.get_region(x, y, grid.item_width, grid.item_height))
                x += grid.item_width + grid.column_padding

            y -= grid.item_height + grid.row_padding

        self.items = items
        self.rows = grid.rows
        self.columns = grid.columns
        self.item_width = grid.item_width
        self.item_height = grid.item_height


class TopLeftGrid(pyglet.image.ImageGrid):

    def _update_items(self):
        if not self._items:
            self._items = []
            y = self.image.height - self.item_height
            for row in range(self.rows):
                x = 0
                for col in range(self.columns):
                    self._items.append(self.image.get_region(x, y, self.item_width, self.item_height))
                    x += self.item_width + self.column_padding

                y -= self.item_height + self.row_padding

    def get_texture_sequence(self):
        if not self._texture_grid:
            self._texture_grid = TopLeftTextureGrid(self)
        return self._texture_grid


def getAnchorPosition(image, referencePoint, trimmed=False):
    """ Sets the anchor point for the texture. """
    if trimmed:
        width = image.oW
        height = image.oH
    else:
        width = image.width
        height = image.height
    offx, offy = (0, 0)
    if referencePoint & RefPointType.CENTERX:
        offx = width // 2
    if referencePoint & RefPointType.CENTERY:
        offy = height // 2
    if referencePoint & RefPointType.LEFT:
        offx = 0
    if referencePoint & RefPointType.TOP:
        offy = height
    if referencePoint & RefPointType.RIGHT:
        offx = width
    if referencePoint & RefPointType.BOTTOM:
        offy = 0
    return (offx, offy)


def setAnchorPoint(image, anchorPoint):
    offx, offy = (0, 0)
    if anchorPoint & RefPointType.CENTERX:
        offx = image.width // 2
    if anchorPoint & RefPointType.CENTERY:
        offy = image.height // 2
    if anchorPoint & RefPointType.LEFT:
        offx = 0
    if anchorPoint & RefPointType.TOP:
        offy = image.height
    if anchorPoint & RefPointType.RIGHT:
        offx = image.width
    if anchorPoint & RefPointType.BOTTOM:
        offy = 0
    image.anchor_x = offx
    image.anchor_y = offy


def getAnchorPositionCustom(width, height, referencePoint):
    """ Sets the anchor point for the texture. """
    offx, offy = (0, 0)
    if referencePoint & RefPointType.CENTERX:
        offx = width // 2
    if referencePoint & RefPointType.CENTERY:
        offy = height // 2
    if referencePoint & RefPointType.LEFT:
        offx = 0
    if referencePoint & RefPointType.TOP:
        offy = height
    if referencePoint & RefPointType.RIGHT:
        offx = width
    if referencePoint & RefPointType.BOTTOM:
        offy = 0
    return (offx, offy)


FLIP_X = 1
FLIP_Y = 2
ROTATE = 4

class Sheet:
    __doc__ = " Saves texture + frame number inside it.\n        Will save grid texture sequence information as to not constantly create them."

    def __init__(self, texture, frames=(1, 1), animationDelay=AnimationSpeed.NORMALFAST, referencePoint=RefPointType.TOPLEFT):
        self.texture = texture
        self.frames = frames
        self.transformations = {}
        self.referencePoint = referencePoint
        if not self.frames[1] >= 0:
            assert self.frames[0] >= 0, "Frame number can't be less than 0 or 0."
            self.animationDelay = animationDelay
            if self.isAnimated():
                self.grid = TopLeftGrid(texture, self.frames[1], self.frames[0])
        else:
            self.grid = (
             self.texture,)
        for grid_image in self.grid:
            anchor_x, anchor_y = getAnchorPosition(grid_image, self.referencePoint)
            grid_image.anchor_x, grid_image.anchor_y = anchor_x, anchor_y

        self.transformations[(0, 0, 0, 0)] = self.grid

    def setReferencePoint(self, referencePoint):
        self.referencePoint = referencePoint
        self.transformations = {}
        for grid_image in self.grid:
            anchor_x, anchor_y = getAnchorPosition(grid_image, self.referencePoint)
            grid_image.anchor_x, grid_image.anchor_y = anchor_x, anchor_y

    def setGUIReferencePoint(self):
        for grid_image in self.grid:
            anchor_x, anchor_y = getAnchorPosition(grid_image, self.referencePoint)
            grid_image.anchor_x, grid_image.anchor_y = anchor_x, -anchor_y

    def get(self, action):
        return self

    def getMaxHeight(self):
        return max((self.grid), key=(attrgetter("height"))).height

    def getMinHeight(self):
        return min((self.grid), key=(attrgetter("height"))).height

    def getMaxWidth(self):
        return max((self.grid), key=(attrgetter("width"))).width

    def getMinWidth(self):
        return min((self.grid), key=(attrgetter("width"))).width

    def getHeight(self):
        """ Here we are basing the sprite off of the first frame in size and width"""
        return self.grid[0].height

    def getWidth(self):
        """ Here we are basing the sprite off of the first frame in size and width"""
        return self.grid[0].width

    def getTransformation(self, offset=0, height=0, flip_x=0, flip_y=0):
        """ Retrieves, stores, and manages transformations, so we do not need to constantly create them. """
        transform = (
         offset, height, flip_x, flip_y)
        if transform not in self.transformations:
            if (offset, height, 0, 0) in self.transformations and (flip_x != 0 or flip_y != 0):
                self.transformations[transform] = [texture.get_transform(flip_x, flip_y) for texture in self.transformations[(offset, height, 0, 0)]]
            else:
                self.transformations[transform] = [texture.get_region(0, offset, texture.width, texture.height - offset - height).get_transform(flip_x, flip_y) if flip_x or flip_y else texture.get_region(0, offset, texture.width, texture.height - offset - height) for texture in self.grid]
            for idx, cropped_image in enumerate(self.transformations[transform]):
                anchor_x, anchor_y = getAnchorPosition(cropped_image, self.referencePoint)
                cropped_image.anchor_x, cropped_image.anchor_y = anchor_x, anchor_y

        return self.transformations[transform]

    def getAnimationDelay(self):
        return self.animationDelay

    def getFrameNbr(self):
        return self.frames[0]

    def getHorizontalFrames(self):
        return self.frames[0]

    def getVerticalFrames(self):
        return self.frames[1]

    def isAnimated(self):
        return self.frames[0] > 1 or self.frames[1] > 1


class CustomSheet(Sheet):

    def __init__(self, textures, frames=(1, 1), animationDelay=AnimationSpeed.NORMALFAST, referencePoint=RefPointType.TOPLEFT):
        self.texture = textures[0]
        self.frames = frames
        self.transformations = {}
        self.referencePoint = referencePoint
        if not self.frames[1] >= 0:
            if not self.frames[0] >= 0:
                raise AssertionError("Frame number can't be less than 0 or 0.")
        self.animationDelay = animationDelay
        self.trimmed = hasattr(self.texture, "oW")
        self.grid = textures
        for grid_image in self.grid:
            anchor_x, anchor_y = getAnchorPosition(grid_image, (self.referencePoint), trimmed=False)
            grid_image.anchor_x, grid_image.anchor_y = anchor_x, anchor_y - grid_image.anchor_y

        self.transformations[(0, 0, 0, 0)] = self.grid

    def getHeight(self):
        """ Here we are basing the sprite off of the first frame in size and width"""
        if not self.trimmed:
            return self.grid[0].height
        else:
            return self.grid[0].oH

    def getWidth(self):
        """ Here we are basing the sprite off of the first frame in size and width"""
        if not self.trimmed:
            return self.grid[0].width
        else:
            return self.grid[0].oW


class XmlSheet(object):

    def __init__(self, texture, referencePoint=RefPointType.TOPLEFT):
        self.texture = texture
        self.sheetFile = None
        self.referencePoint = referencePoint
        self.transformations = {}
        for image in self.texture:
            anchor_x, anchor_y = getAnchorPosition(image, self.referencePoint)
            image.anchor_x, image.anchor_y = anchor_x, anchor_y

        self.animationDelay = 0.3

    @property
    def grid(self):
        return self.texture

    def getHeight(self):
        """ Here we are basing the sprite off of the first frame in size and width"""
        return self.grid[0].height

    def getMaxHeight(self):
        return max((self.texture), key=(attrgetter("height"))).height

    def getMinHeight(self):
        return min((self.texture), key=(attrgetter("height"))).height

    def getMaxWidth(self):
        return max((self.texture), key=(attrgetter("width"))).width

    def getMinWidth(self):
        return min((self.texture), key=(attrgetter("width"))).width

    def getWidth(self):
        """ Here we are basing the sprite off of the first frame in size and width"""
        return self.grid[0].width

    def getOriginalHeight(self, frame):
        return self.texture[frame].height

    def getAnimationDelay(self):
        return self.animationDelay

    def getFrameNbr(self):
        return len(self.texture)

    def isAnimated(self):
        return len(self.texture) > 1

    def getTransformation(self, offset=0, height=0, flip_x=0, flip_y=0):
        """ Caches the cropped grid and texture sequence so we do not need to constantly create it. """
        transform = (
         offset, height, flip_x, flip_y)
        if transform not in self.transformations:
            if (offset, height, 0, 0) in self.transformations and (flip_x != 0 or flip_y != 0):
                cropped_images = [texture.get_transform(flip_x, flip_y) for texture in self.transformations[(offset, height, 0, 0)]]
            else:
                cropped_images = [texture.get_region(0, offset, texture.width, texture.height - offset - height) for texture in self.texture]
                for idx, cropped_image in enumerate(cropped_images):
                    anchor_x, anchor_y = getAnchorPosition(cropped_image, self.referencePoint)
                    cropped_image.anchor_x, cropped_image.anchor_y = anchor_x, anchor_y

            if flip_x or flip_y:
                cropped_images = [texture.get_transform(flip_x, flip_y) for texture in cropped_images]
            self.transformations[transform] = cropped_images
        return self.transformations[transform]


class PokemonSheet(XmlSheet):

    def __init__(self, dexId, texture, referencePoint=RefPointType.TOPLEFT):
        self.dexId = dexId
        super().__init__(texture, referencePoint)
        self.maxHeight = max((self.texture[0:15]), key=(attrgetter("height"))).height

    def getMaxHeight(self):
        return self.maxHeight

    def getTransformation(self, offset=0, height=0, flip_x=0, flip_y=0):
        """ Caches the cropped grid and texture sequence so we do not need to constantly create it. """
        transform = (
         offset, height, flip_x, flip_y)
        if transform not in self.transformations:
            if (offset, height, 0, 0) in self.transformations and (flip_x != 0 or flip_y != 0):
                cropped_images = [texture.get_transform(flip_x, flip_y) for texture in self.transformations[(offset, height, 0, 0)]]
            else:
                cropped_images = [texture.get_region(0, offset, texture.width, texture.height - offset - height) for texture in self.texture]
                anchor_x, anchor_y = getAnchorPositionCustom(self.texture[0].oW, self.texture[0].oH, self.referencePoint)
                for idx, cropped_image in enumerate(cropped_images):
                    cropped_image.anchor_x = -self.texture[idx].oX + anchor_x
                    bottom = self.texture[idx].oH - self.texture[idx].height - self.texture[idx].oY
                    cropped_image.anchor_y = -bottom + anchor_y

            if flip_x or flip_y:
                cropped_images = [texture.get_transform(flip_x, flip_y) for texture in cropped_images]
            self.transformations[transform] = cropped_images
        return self.transformations[transform]


class AutocaseSheet:

    def __init__(self, mode, texture, framesHor, framesVert=1, animationDelay=AnimationSpeed.NORMALFAST):
        self.texture = texture
        self.frames = (framesHor, framesVert)
        self.animationDelay = animationDelay
        if self.isAnimated():
            self.grid = pyglet.image.ImageGrid(texture, self.frames[1], self.frames[0]).get_texture_sequence()
        else:
            self.grid = (
             self.texture,)

    def getAnimationDelay(self):
        return self.animationDelay

    def getFrameNbr(self):
        return self.frames

    def getHorizontalFrames(self):
        return self.frames[0]

    def getVerticalFrames(self):
        return self.frames[1]

    def isAnimated(self):
        return self.frames[0] > 1
