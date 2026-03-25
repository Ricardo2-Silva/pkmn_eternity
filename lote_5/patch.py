# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\render\utils\patch.py
"""
Created on 1 juil. 2011

@author: Kami
"""
from client.control.maths.matrix import Matrix
from client.data.gui.button import ButtonData
import pyglet
from pyglet.image import SolidColorImagePattern

class PatchType:
    NINE = 9
    THREE = 3
    THREE_VERT = 4
    FOUR_IMAGE = 1
    NOPATCH = 0


class LinePattern(pyglet.image.ImagePattern):
    __doc__ = "Creates an image filled with a solid color."
    center = bytes((0, 0, 0, 0))

    def __init__(self, color=(0, 0, 0, 0)):
        """Create a solid image pattern with the given color.

        :Parameters:
            `color` : (int, int, int, int)
                4-tuple of ints in range [0,255] giving RGBA components of
                color to fill with.

        """
        self.color = pyglet.image.color_as_bytes(color)

    def create_image(self, left, top, right, bottom):
        """ Creates a 9 patch based on the color. (3x3)
            With center being alpha """
        l, t, r, b = (
         self.center, self.center, self.center, self.center)
        if left:
            l = self.color
        if top:
            t = self.color
        if right:
            r = self.color
        if bottom:
            b = self.color
        data = (b'').join([l, b, r, l, self.center, r, l, t, r])
        return pyglet.image.ImageData(3, 3, "RGBA", data)


class BorderLine(object):

    def __init__(self, color, left, top, right, bottom):
        self.texture = pyglet.image.SolidColorImagePattern(color + (255, )).get_texture()
        self.bottom = pyglet.sprite.Sprite()


class NinePatchLine(object):
    __doc__ = "A scalable 9-patch image.\n    "

    def __init__(self, color, left, top, right, bottom):
        """Create NinePatch cuts of an image

        Arguments:
            image - an ImageData (Texture, TextureRegion, etc)
            texture - force cut ImageDatas to be Textures (or Regions)
        """
        color = LinePattern(color + (255, ))
        width = 3
        height = 3
        self.texture = color.create_image(left, top, right, bottom).get_texture()
        self.stretch_left = 1
        self.stretch_right = 1
        self.stretch_bottom = 1
        self.stretch_top = 1
        u1 = 0
        v1 = 0
        u2 = self.stretch_left
        v2 = self.stretch_bottom
        u3 = width - self.stretch_right
        v3 = height - self.stretch_top
        u4 = width
        v4 = height
        u1, u2, u3, u4 = [s / float(width) for s in (u1, u2, u3, u4)]
        v1, v2, v3, v4 = [s / float(height) for s in (v1, v2, v3, v4)]
        tu1, tv1, _, _, _, _, tu2, tv2, _, _, _, _ = self.texture.tex_coords
        u_scale = tu2 - tu1
        u_bias = tu1
        v_scale = tv2 - tv1
        v_bias = tv1
        u1, u2, u3, u4 = [u_bias + u_scale * s for s in (u1, u2, u3, u4)]
        v1, v2, v3, v4 = [v_bias + v_scale * s for s in (v1, v2, v3, v4)]
        self.tex_coords = (
         u1, v1,
         u2, v1,
         u3, v1,
         u4, v1,
         u1, v2,
         u2, v2,
         u3, v2,
         u4, v2,
         u1, v3,
         u2, v3,
         u3, v3,
         u4, v3,
         u1, v4,
         u2, v4,
         u3, v4,
         u4, v4)
        self.indices = []
        for y in range(3):
            for x in range(3):
                self.indices.extend([
                 x + y * 4,
                 x + 1 + y * 4,
                 x + 1 + (y + 1) * 4,
                 x + (y + 1) * 4])

    def get_vertices(self, x, y, width, height):
        """Get 16 2D vertices for the given image region"""
        x1 = x
        y1 = y
        x2 = x + self.stretch_left
        y2 = y + self.stretch_bottom
        x3 = x + width - self.stretch_right
        y3 = y + height - self.stretch_top
        x4 = x + width
        y4 = y + height
        return (
         x1, y1,
         x2, y1,
         x3, y1,
         x4, y1,
         x1, y2,
         x2, y2,
         x3, y2,
         x4, y2,
         x1, y3,
         x2, y3,
         x3, y3,
         x4, y3,
         x1, y4,
         x2, y4,
         x3, y4,
         x4, y4)

    def get_vertices_z(self, x, y, z, width, height):
        """Get 16 2D vertices for the given image region"""
        x1 = x
        y1 = y
        x2 = x + self.stretch_left
        y2 = y + self.stretch_bottom
        x3 = x + width - self.stretch_right
        y3 = y + height - self.stretch_top
        x4 = x + width
        y4 = y + height
        return (
         x1, y1, z,
         x2, y1, z,
         x3, y1, z,
         x4, y1, z,
         x1, y2, z,
         x2, y2, z,
         x3, y2, z,
         x4, y2, z,
         x1, y3, z,
         x2, y3, z,
         x3, y3, z,
         x4, y3, z,
         x1, y4, z,
         x2, y4, z,
         x3, y4, z,
         x4, y4, z)

    def get_vertices_flipped(self, x, y, width, height):
        """Get 16 2D vertices for the given image region"""
        x1 = x
        y4 = y
        x2 = x + self.stretch_left
        y3 = y + self.stretch_bottom
        x3 = x + width - self.stretch_right
        y2 = y + height - self.stretch_top
        x4 = x + width
        y1 = y + height
        return (
         x1, y1,
         x2, y1,
         x3, y1,
         x4, y1,
         x1, y2,
         x2, y2,
         x3, y2,
         x4, y2,
         x1, y3,
         x2, y3,
         x3, y3,
         x4, y3,
         x1, y4,
         x2, y4,
         x3, y4,
         x4, y4)


class NinePatchImage(object):
    __doc__ = "9-patch image that supports Z and grids. "

    def __init__(self, image, stretch, cols=None):
        """ If cols is specified, we split the image into separate patches. Otherwise 1 patch. """
        self._current_index = 0
        self.tex_coords = {}
        self.stretch = stretch
        self.texture = image
        if cols is not None:
            grid = pyglet.image.ImageGrid(image, 1, cols)
            self.textures = grid.get_texture_sequence()
        else:
            self.textures = [
             self.texture]
        for idx, texture in enumerate(self.textures):
            self.tex_coords[idx] = self._create_patch(texture)

    def _create_patch(self, image):
        width = image.width
        height = image.height
        texture = image.get_texture()
        u1 = 0
        v1 = 0
        u2 = self.stretch.left
        v2 = self.stretch.bottom
        u3 = width - self.stretch.right
        v3 = height - self.stretch.top
        u4 = width
        v4 = height
        u1, u2, u3, u4 = [s / float(width) for s in (u1, u2, u3, u4)]
        v1, v2, v3, v4 = [s / float(height) for s in (v1, v2, v3, v4)]
        tu1, tv1, _, _, _, _, tu2, tv2, _, _, _, _ = texture.tex_coords
        u_scale = tu2 - tu1
        u_bias = tu1
        v_scale = tv2 - tv1
        v_bias = tv1
        u1, u2, u3, u4 = [u_bias + u_scale * s for s in (u1, u2, u3, u4)]
        v1, v2, v3, v4 = [v_bias + v_scale * s for s in (v1, v2, v3, v4)]
        self.indices = []
        for y in range(3):
            for x in range(3):
                self.indices.extend([
                 x + y * 4,
                 x + 1 + y * 4,
                 x + 1 + (y + 1) * 4,
                 x + (y + 1) * 4])

        return (
         u1, v1,
         u2, v1,
         u3, v1,
         u4, v1,
         u1, v2,
         u2, v2,
         u3, v2,
         u4, v2,
         u1, v3,
         u2, v3,
         u3, v3,
         u4, v3,
         u1, v4,
         u2, v4,
         u3, v4,
         u4, v4)

    def get_vertices(self, x, y, width, height):
        x1 = x
        y1 = y
        x2 = x + self.stretch.left
        y2 = y + self.stretch.bottom
        x3 = x + width - self.stretch.right
        y3 = y + height - self.stretch.top
        x4 = x + width
        y4 = y + height
        return (
         x1, y1,
         x2, y1,
         x3, y1,
         x4, y1,
         x1, y2,
         x2, y2,
         x3, y2,
         x4, y2,
         x1, y3,
         x2, y3,
         x3, y3,
         x4, y3,
         x1, y4,
         x2, y4,
         x3, y4,
         x4, y4)

    def get_vertices_z(self, x, y, z, width, height):
        x1 = x
        y1 = y
        x2 = x + self.stretch.left
        y2 = y + self.stretch.bottom
        x3 = x + width - self.stretch.right
        y3 = y + height - self.stretch.top
        x4 = x + width
        y4 = y + height
        return (
         x1, y1, z,
         x2, y1, z,
         x3, y1, z,
         x4, y1, z,
         x1, y2, z,
         x2, y2, z,
         x3, y2, z,
         x4, y2, z,
         x1, y3, z,
         x2, y3, z,
         x3, y3, z,
         x4, y3, z,
         x1, y4, z,
         x2, y4, z,
         x3, y4, z,
         x4, y4, z)


class NinePatch(Matrix):

    def __init__(self):
        Matrix.__init__(self, 3, 3)


class ThreePatch(Matrix):

    def __init__(self):
        Matrix.__init__(self, 1, 3)

    def set(self, value, i, j=0):
        return Matrix.set(self, value, i, j)

    def get(self, i, j=0):
        return Matrix.get(self, i, j)


def loadNinePatch(windowTexture):
    """ Create 9 imgs with each part of the picture, put them in a matrix """
    matrix = NinePatch()
    seq = pyglet.image.ImageGrid(windowTexture, 3, 3)
    textureGrid = pyglet.image.TextureGrid(seq)
    matrix.set(textureGrid[0], 0, 2)
    matrix.set(textureGrid[1], 1, 2)
    matrix.set(textureGrid[2], 2, 2)
    matrix.set(textureGrid[3], 0, 1)
    matrix.set(textureGrid[4], 1, 1)
    matrix.set(textureGrid[5], 2, 1)
    matrix.set(textureGrid[6], 0, 0)
    matrix.set(textureGrid[7], 1, 0)
    matrix.set(textureGrid[8], 2, 0)
    return matrix


def loadThreePatch(windowTexture):
    """ Create 3 imgs with each vertical part of the picture, put them in a matrix """
    matrix = ThreePatch()
    seq = pyglet.image.ImageGrid(windowTexture, 1, 3)
    textureGrid = pyglet.image.TextureGrid(seq)
    for i in range(0, 3):
        matrix.set(textureGrid[i], i, 0)

    return matrix


def loadThreePatchVertical(windowTexture):
    """ Create 3 imgs with each vertical part of the picture, put them in a matrix """
    seq = pyglet.image.ImageGrid(windowTexture, 3, 1)
    textureGrid = pyglet.image.TextureGrid(seq)
    matrix = ThreePatch()
    for i in range(0, 3):
        matrix.set(textureGrid[i], 2 - i, 0)

    return matrix


def loadButtonPatch(windowTexture, patchType):
    seq = pyglet.image.ImageGrid(windowTexture, 1, 4)
    textureGrid = pyglet.image.TextureGrid(seq)
    l = []
    for i in range(0, 4):
        l.append(patchMethod[patchType](textureGrid[i]))

    return ButtonData(*l)


def loadOneButtonBackground(stateSurface):
    return ButtonData(*stateSurface)


def loadButtonBackground(windowTexture):
    seq = pyglet.image.ImageGrid(windowTexture, 1, 4)
    textureGrid = pyglet.image.TextureGrid(seq)
    return ButtonData(*textureGrid)


patchMethod = {(PatchType.NINE): loadNinePatch, 
 (PatchType.THREE): loadThreePatch, 
 (PatchType.THREE_VERT): loadThreePatchVertical}
