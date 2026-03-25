# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\render\sprite.py
import traceback, rabbyt, client.data.exceptions as exceptions, pyglet
from twisted.internet import reactor
from client.render.custom import ZSprite, ZSpriteGroup
from client.render.shader.service import shaderService
from client.render.texture import unloadTexture
from pyglet.gl import *
from rabbyt.anims import lerp
from shared.container.constants import RefPointType
from client.scene.manager import sceneManager
import math
from client.render.shader.default_sprite import default_sprite_shader
from shared.controller.maths.maths import interpolate, interpolatePosition, interpolatePosition2D

class PygletSprite(pyglet.sprite.Sprite):

    def __init__(self, *args, **kwargs):
        self.alpha = 255
        self.z_offset = 0
        self._offset = [0, 0]
        self._previous_offset = [0, 0]
        self.schedule = None
        (pyglet.sprite.Sprite.__init__)(self, *args, **kwargs)
        self.previous_state = (self.x, self.y, self.z)
        self.current_state = (self.x, self.y, self.z)
        self.current_state_no_offset = (self.x, self.y, self.z)
        self.previous_state_no_offset = (self.x, self.y, self.z)

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value):
        self._previous_offset = self._offset
        self._offset = value

    def setInView(self):
        return

    def setOutOfView(self):
        return

    def setDefaultAlpha(self):
        self.alpha = 255

    def updatePosition(self, x, y, z):
        self.update(x=(x + self.offset[0]),
          y=(y + self.offset[1]),
          z=(1 - int(z) + self.z_offset))

    def setPosition(self, x, y, renderingOrder=None):
        """Sets the position and saves the previous state."""
        self.previous_state = (
         self.x, self.y, self.z)
        if not renderingOrder:
            renderingOrder = y
        self.update(x=(x + self.offset[0]),
          y=(y + self.offset[1]),
          z=(1 - int(renderingOrder) + self.z_offset))
        self.current_state = (
         self.x, self.y, self.z)

    def resetPreviousState(self):
        self.previous_state = (
         self.previous_state[0] - self._previous_offset[0] + self._offset[0],
         self.previous_state[1] - self._previous_offset[1] + self._offset[1],
         self.z)
        self.update(self.x - self._previous_offset[0] + self._offset[0], self.y - self._previous_offset[1] + self._offset[1], self.z)

    def resetRenderState(self):
        self.previous_state = self.current_state

    def setPositionInterpolate(self, x, y, z, interp):
        """Interpolates the previous state to the new state."""
        x0, y0, z0 = interpolatePosition(self.previous_state, (
         x + self.offset[0],
         y + self.offset[1],
         1 - int(z) + self.z_offset), interp)
        self.update(x0, y0, z0)

    def setMultipleAttributes(self, x, y, rotation, scale, renderingOrder=None):
        if not renderingOrder:
            renderingOrder = y
        self.update(x=(round(x + self.offset[0])), y=(round(y + self.offset[1])),
          z=(1 - int(renderingOrder) + self.z_offset),
          rotation=rotation,
          scale=scale)

    def getPosition(self):
        return self.position

    def getSize(self):
        return (
         self.width, self.height)

    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height + self.image.anchor_y

    def setSize(self, width, height):
        self.update(scale_x=(width / self.image.width), scale_y=(height / self.image.height))

    def setScale(self, x, y):
        self.update(scale_x=x, scale_y=y)

    def setColor(self, r, g, b):
        self.color = (
         r, g, b)

    def setRGBA(self, r, g, b, a):
        self._opacity = a
        self.color = (r, g, b)

    def setAlpha(self, alpha):
        self.opacity = alpha

    @property
    def bottom(self):
        return self.y

    @property
    def left(self):
        return self.x

    @property
    def right(self):
        return self.x + self.image.width

    @property
    def top(self):
        return self.y + self.image.height


class PygletSheet(PygletSprite):

    def __init__(self, sheet, *args, **kwargs):
        self.sheet = sheet
        self._textureGrid = self.sheet.grid
        self._frameClamp = (
         0, len(self._textureGrid))
        self._frame_index = 0
        (PygletSprite.__init__)(self, self._textureGrid[self._frame_index], *args, **kwargs)
        self.setFrame(0)

    def setInView(self):
        return

    def setOutOfView(self):
        return

    @property
    def currentFrame(self):
        return self._frame_index

    @property
    def lastFrame(self):
        return len(self._textureGrid) - 1

    def setTransformation(self, sheet, offset, height, flip_x=0, flip_y=0):
        self.sheet = sheet
        self._textureGrid = self.sheet.getTransformation(offset, height, flip_x, flip_y)
        self._clipOffsetBottom = offset
        self._clipOffsetTop = height
        self._frameClamp = (0, len(self._textureGrid))

    def setFrameAndSize(self, col):
        self._frame_index = col
        self.image = self._textureGrid[self._frame_index]

    def setFrame(self, col, row=0):
        self._frame_index = col
        self.image = self._textureGrid[self._frame_index]

    def setFrameClamp(self, minFrame, maxFrame):
        """ Sets a customized frame to clamp to for animations. Some effects may only have certain frames for certain cases."""
        self._frameClamp = (
         minFrame, maxFrame)
        self.setFrame(minFrame)

    def setSheet(self, sheet):
        self.sheet = sheet
        self._textureGrid = self.sheet.grid
        self._frameClamp = (
         0, len(self._textureGrid))
        self.setFrame(0)

    def nextFrame(self):
        """ Used for animation. Shape changes are required for changing reference point sadly."""
        self._frame_index += 1
        if self._frame_index >= self._frameClamp[1]:
            self._frame_index = self._frameClamp[0]
        self.image = self._textureGrid[self._frame_index]

    def nextFrameNoReset(self):
        """ Used for animation. Shape changes are required for changing reference point sadly."""
        self._frame_index += 1
        if self._frame_index >= self._frameClamp[1]:
            return
        self.image = self._textureGrid[self._frame_index]

    def previousFrame(self):
        self._frame_index -= 1
        if self._frame_index < self._frameClamp[0]:
            self._frame_index = self._frameClamp[1] - 1
        self.image = self._textureGrid[self._frame_index]

    def animate(self):
        self._frame_index += 1
        if self._frame_index >= len(self._textureGrid):
            self._frame_index = 0
        self.image = self._textureGrid[self._frame_index]


class GUIPygletSprite(PygletSprite):

    def setPosition(self, x, y, z=0):
        self.previous_state = (
         self.x, self.y)
        (self.update)(*sceneManager.convert(int(x + self.offset[0]), int(y + self.offset[1] + self.height)))
        self.current_state = (
         self.x, self.y)

    def setPositionInterpolate(self, x, y, z=0, interp=0):
        x, y = sceneManager.convert(int(x + self.offset[0]), int(y + self.offset[1] + self.height))
        x0, y0 = interpolatePosition2D(self.previous_state, (
         x, y), interp)
        self.update(x0, y0)

    def setWidth(self, value):
        return

    def setHeight(self, value):
        return

    @property
    def z(self):
        return self._z

    @z.setter
    def z(self, value):
        self._z = value + self.z_offset
        self._update_position()


class GUIPygletSheet(PygletSheet):

    def setPosition(self, x, y, z=0):
        self.previous_state = (
         self.x, self.y)
        (self.update)(*sceneManager.convert(int(x + self.offset[0]), int(y + self.offset[1] + self.height)))

    def setPositionInterpolate(self, x, y, z=0, interp=0):
        x, y = sceneManager.convert(int(x + self.offset[0]), int(y + self.offset[1] + self.height))
        x0, y0 = interpolatePosition2D(self.previous_state, (
         x, y), interp)
        self.update(x0, y0)

    def setWidth(self, value):
        return

    def setHeight(self, value):
        return

    @property
    def z(self):
        return self._z

    @z.setter
    def z(self, value):
        self._z = value + self.z_offset
        self._update_position()


class CustomSprite:

    def __init__(self, x, y, z, color=None, group=None, batch=None):
        self._x = x
        self._y = y
        self._z = z
        self.previous_state = (x, y)
        self.current_state = (x, y)
        self.z_offset = 0
        self._color = [255, 255, 255, 255] if not color else color
        self._visible = True
        self._group = group
        self._batch = batch

    @property
    def position(self):
        return (self._x, self._y)

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, visibility):
        self._visible = visibility
        self._vertex_list.vertices[:] = self._get_vertices()

    def setColor(self, r, g, b):
        self._color[:3] = (
         r, g, b)
        self._vertex_list.colors[:] = list(map(int, self._color)) * 16

    def setAlpha(self, value):
        self._color[3] = value
        self._vertex_list.colors[:] = list(map(int, self._color)) * 16

    @property
    def opacity(self):
        return self._color[3]

    @opacity.setter
    def opacity(self, value):
        self._color[3] = value
        self._vertex_list.colors[:] = list(map(int, self._color)) * 16

    def update(self, x=None, y=None, z=None):
        self._x = x
        self._y = y
        self._vertex_list.vertices[:] = self._get_vertices()

    def setSize(self, width, height):
        self._width = width
        self._height = height
        self._vertex_list.vertices[:] = self._get_vertices()

    def setPosition(self, x, y, z=0):
        self.previous_state = (
         self._x, self._y)
        self._x = x
        self._y = y
        self._vertex_list.vertices[:] = self._get_vertices()
        self.current_state = (self._x, self._y)

    def resetRenderState(self):
        self.previous_state = self.current_state

    def setPositionInterpolate(self, x, y, interp):
        self._x, self._y = interpolatePosition2D(self.previous_state, (x, y), interp)
        self._vertex_list.vertices[:] = self._get_vertices()

    def delete(self):
        self._vertex_list.delete()
        self._vertex_list = None
        self._group = None

    @property
    def batch(self):
        return self._batch

    @property
    def z(self):
        return self._z + self.z_offset

    @z.setter
    def z(self, value):
        self._z = value
        self._vertex_list.vertices[:] = self._get_vertices()


class LineSprite(CustomSprite):
    __doc__ = " Use a rect to create a line with thickness. "

    def __init__(self, x, y, z, width=1, color=(255, 0, 0, 255), group=None, batch=None):
        super().__init__(x, y, z, group=group, batch=batch)
        self._width = width
        self._rotation = 0
        self._color = color
        self._create_vertex_list()

    def _get_vertices(self):
        if not self._visible:
            vertices = [
             0, 0, 0, 0, 0, 0]
        elif self._rotation:
            x1 = 0
            y1 = 0
            x2 = x1 + self._width
            y2 = y1
            x = self._x
            y = self._y
            z = self._z
            r = -math.radians(self._rotation)
            cr = math.cos(r)
            sr = math.sin(r)
            ax = x1 * cr - y1 * sr + x
            ay = x1 * sr + y1 * cr + y
            bx = x2 * cr - y1 * sr + x
            by = x2 * sr + y1 * cr + y
            cx = x2 * cr - y2 * sr + x
            cy = x2 * sr + y2 * cr + y
            dx = x1 * cr - y2 * sr + x
            dy = x1 * sr + y2 * cr + y
            vertices = [
             ax, ay, z, bx, by, z]
        else:
            x1 = self._x
            y1 = self._y
            x2 = x1 + self._width
            y2 = y1
            z = self._z
            vertices = [x1, y1, z, x2, y1, z]
        return vertices

    def setWidth(self, value):
        self._width = value
        self._vertex_list.vertices[:] = self._get_vertices()

    def setColor(self, r, g, b):
        self._color[:3] = (
         r, g, b)
        self._vertex_list.colors[:] = self._color * 2

    def setAlpha(self, value):
        self._color[3] = value
        self._vertex_list.colors[:] = self._color * 2

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        self._rotation = value
        self._vertex_list.vertices[:] = self._get_vertices()

    def _create_vertex_list(self):
        self._vertex_list = self._batch.add(2, pyglet.gl.GL_LINES, self._group, (
         "v3f", self._get_vertices()), (
         "c4B", self._color * 2))

    def setPosition(self, x, y, renderingOrder=0):
        CustomSprite.setPosition(self, x, y, z=renderingOrder)

    def getSize(self):
        return (
         self._width, 1)


class PatchSprite(CustomSprite):
    __doc__ = " This is a container to contain and draw a patch "
    invisible = [0] * 16 * 3

    def __init__(self, patch, padding, x=0, y=0, z=1, width=10, height=10, group=None, batch=None):
        super().__init__(x, y, z, group=group, batch=batch)
        self.patch = patch
        self._width = width
        self._height = height
        self._padding = padding
        self._index = 0
        self._group = pyglet.sprite.SpriteGroup(patch.texture, pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA, group)
        self._create_vertex_list()

    @property
    def group(self):
        """Parent graphics group.

        The sprite can change its rendering group, however this can be an
        expensive operation.

        :type: :py:class:`pyglet.graphics.Group`
        """
        return self._group.parent

    @group.setter
    def group(self, group):
        if self._group.parent == group:
            return
        self._group = self._group.__class__(self.patch.texture, pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA, group)
        if self._batch is not None:
            self._batch.migrate(self._vertex_list, GL_QUADS, self._group, self._batch)

    @property
    def batch(self):
        return self._batch

    @batch.setter
    def batch(self, batch):
        if self._batch == batch:
            return
        elif batch is not None and self._batch is not None:
            self._batch.migrate(self._vertex_list, GL_QUADS, self._group, batch)
            self._batch = batch
        else:
            self._vertex_list.delete()
            self._batch = batch
            self._create_vertex_list()

    @property
    def image(self):
        return self.patch

    @image.setter
    def image(self, idx):
        self._vertex_list.tex_coords[:] = self.patch.tex_coords[idx]

    @property
    def texture(self):
        return self.patch.textures[self._index]

    @texture.setter
    def texture(self, idx):
        self._index = idx
        self._vertex_list.tex_coords[:] = self.patch.tex_coords[idx]

    def _create_vertex_list(self):
        self._vertex_list = self._batch.add_indexed(16, pyglet.gl.GL_QUADS, self._group, self.patch.indices, (
         "v3f", self._get_vertices()), (
         "t2f", self.patch.tex_coords[0]), (
         "c4B", self._color * 16))

    def _get_vertices(self):
        if self._visible:
            return (self.patch.get_vertices_z)(*sceneManager.convert(self._x - self._padding.left, self._y + self._padding.bottom + self._height), *(
             self._z + self.z_offset,
             self._width + self._padding.left + self._padding.right,
             self._height + self._padding.bottom + self._padding.top))
        else:
            return self.invisible


class PatchSpriteRound(PatchSprite):

    def _get_vertices(self):
        if self._visible:
            vertices = (self.patch.get_vertices_z)(*sceneManager.convert(self._x - self._padding.left, self._y + self._padding.bottom + self._height), *(
             self._z + self.z_offset,
             self._width + self._padding.left + self._padding.right,
             self._height + self._padding.bottom + self._padding.top))
            return [int(v) for v in vertices]
        else:
            return self.invisible


class VertexGroup(pyglet.graphics.Group):

    def set_state(self):
        pyglet.gl.glDisable(pyglet.gl.GL_TEXTURE_2D)
        glPushAttrib(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glEnable(GL_ALPHA_TEST)
        glAlphaFunc(GL_GREATER, 0.01)

    def unset_state(self):
        glPopAttrib()
        glDisable(GL_DEPTH_TEST)
        pyglet.gl.glEnable(pyglet.gl.GL_TEXTURE_2D)

    def __eq__(self, other):
        return other.__class__ is self.__class__

    def __hash__(self):
        return hash((id(self.parent),))


class LineBorderSprite(CustomSprite):
    invisible = [
     0] * 6

    def __init__(self, x=0, y=0, z=0, width=10, height=10, group=None, batch=None, color=(0, 0, 0, 255), left=True, top=True, right=True, bottom=True):
        super().__init__(x, y, z, color, group, batch)
        self._width = width
        self._height = height
        self._total_lines = 0
        self.left = left
        self.top = top
        self.bottom = bottom
        self.right = right
        if self.left:
            self._total_lines += 1
        elif self.right:
            self._total_lines += 1
        elif self.top:
            self._total_lines += 1
        else:
            if self.bottom:
                self._total_lines += 1
        self._group = VertexGroup(group)
        self._create_vertex_list()

    def _get_vertices(self):
        if self._visible is False:
            return self.invisible * self._total_lines
        else:
            x, y = sceneManager.convert(self._x, self._y + self._height)
            vertices = []
            if self.left:
                vertices.extend([x, y, self.z, x, y + self._height, self.z])
            if self.top:
                vertices.extend([x, y + self._height, self.z, x + self._width, y + self._height, self.z])
            if self.bottom:
                vertices.extend([x - 1, y, self.z, x + self._width, y, self.z])
            if self.right:
                vertices.extend([x + self._width, y, self.z, x + self._width, y + self._height, self.z])
            return vertices

    def _create_vertex_list(self):
        vertices = self._get_vertices()
        count = len(vertices) // 3
        self._vertex_list = self._batch.add(count, pyglet.gl.GL_LINES, self._group, (
         "v3f", vertices), (
         "c4B", self._color * count), (
         "t2f", (1, 1) * count))


class TextSprite(pyglet.text.Label):
    _cached_groups = {}

    def __init__(self, text='', font_name=None, font_size=None, bold=False, italic=False, color=(255, 255, 255, 255), x=0, y=0, z=0, width=None, height=None, anchor_x='left', anchor_y='baseline', align='left', multiline=False, dpi=None, batch=None, group=None):
        self.z_offset = 0
        self._visible = True
        self._opacity = 255
        self.previous_state = (x, y)
        self.current_state = (x, y)
        pyglet.text.Label.__init__(self, text=text,
          font_name=font_name,
          font_size=font_size,
          bold=bold,
          italic=italic,
          color=color,
          x=x,
          y=y,
          z=z,
          width=width,
          height=height,
          anchor_x=anchor_x,
          anchor_y=anchor_y,
          align=align,
          multiline=multiline,
          dpi=dpi,
          batch=batch,
          group=group)

    def _init_groups(self, group):
        if not group:
            return
        if group not in list(self.__class__._cached_groups.keys()):
            top = pyglet.text.layout.TextLayoutGroup(group)
            bg = pyglet.graphics.OrderedGroup(0, top)
            fg = pyglet.text.layout.TextLayoutForegroundGroup(1, top)
            fg2 = pyglet.text.layout.TextLayoutForegroundDecorationGroup(2, top)
            self.__class__._cached_groups[group] = [top, bg, fg, fg2, 0]
        groups = self.__class__._cached_groups[group]
        self.top_group = groups[0]
        self.background_group = groups[1]
        self.foreground_group = groups[2]
        self.foreground_decoration_group = groups[3]
        groups[4] += 1

    def delete(self):
        pyglet.text.Label.delete(self)

    def on_insert_text(self, start, text):
        if self._visible:
            self._init_document()
        elif self.document.text:
            self._get_lines()

    def on_delete_text(self, start, end):
        if self._visible:
            self._init_document()

    def setColor(self, r, g, b):
        return

    def setAlpha(self, a):
        self.opacity = a

    @property
    def position(self):
        return (self._x, self._y)

    @property
    def opacity(self):
        return self._opacity

    @opacity.setter
    def opacity(self, alpha):
        self._opacity = alpha
        self.color = list(map(int, (*self.color[:3], self._opacity)))

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, visibility):
        self._visible = visibility
        if visibility is True:
            self._update()
            self.update(self._x, self._y)
        else:
            self.delete()

    @property
    def z(self):
        return self._z + self.z_offset

    @z.setter
    def z(self, value):
        self._z = value
        for vertex_list in self._vertex_lists:
            vertices = vertex_list.vertices[:]
            vertices[2::3] = [self._z + self.z_offset for i in range(len(vertices[2::3]))]
            vertex_list.vertices[:] = vertices

    def setPosition(self, x, y):
        self.previous_state = (self._x, self._y)
        (self.update)(*sceneManager.convert(x, y + self.font_size + 3))
        self.current_state = (self._x, self._y)

    def resetRenderState(self):
        self.previous_state = self.current_state

    def setPositionInterpolate(self, x, y, interp):
        x, y = sceneManager.convert(x, y + self.font_size + 3)
        x0, y0 = interpolatePosition2D(self.previous_state, (
         x, y), interp)
        self.update(x0, y0)

    def getHeight(self):
        return self.content_height

    def getWidth(self):
        return self.content_width


SLOW = 8
MEDIUM = 15
FAST = 35
INSTANT = 0

class SpellingTextSprite(TextSprite):

    def __init__(self, *args, rate=FAST, **kwargs):
        """ Rate is characters per second """
        (TextSprite.__init__)(self, *args, **kwargs)
        self.rate = rate
        self.active = False
        if self.multiline:
            self._wordwrap_fix()
        else:
            self._original_text = self.text
        self.document.text = ""
        self._char_pos = 1
        self._lines = 0

    def _wordwrap_fix(self):
        """ Fixes multiline wrapping so characters inserted into one line
            do not get pushed into the next line after the word is complete.
        """
        separated_lines = [[glyph[1] for box in line.boxes for glyph in iter((box.glyphs))] for line in self._get_lines()]
        self._text_lines = []
        start = 0
        formatted = self.text.replace("\n", "")
        for glyphs in separated_lines:
            length = len(glyphs)
            self._text_lines.append(formatted[start:start + length])
            start += length

        self._original_text = "\n".join(self._text_lines)

    def _spell_word(self, dt):
        self.document.text = self._original_text[:self._char_pos]
        self._char_pos += 1
        if self.multiline:
            self._lines = len(self.document.text.split("\n"))
        if self._char_pos > len(self._original_text):
            self.stop()

    @property
    def text(self):
        return self.document.text

    @text.setter
    def text(self, text):
        if text == self.document._text:
            return
        else:
            self.stop()
            self._char_pos = 1
            self.document.delete_text(0, len(self.document._text))
            if self.multiline:
                self.document.insert_text(0, text)
                self._wordwrap_fix()
                self.document.delete_text(0, len(self.document._text))
            else:
                self._original_text = text

    def start(self):
        pyglet.clock.schedule_interval(self._spell_word, 1.0 / self.rate)
        self.active = True

    def stop(self):
        pyglet.clock.unschedule(self._spell_word)
        self.active = False


class PygletBackgroundSprite(pyglet.sprite.Sprite):

    def __init__(self, img, x=0, y=0, z=0, blend_src=GL_SRC_ALPHA, blend_dest=GL_ONE_MINUS_SRC_ALPHA, batch=None, group=None, usage="dynamic", subpixel=False):
        self.alpha = 255
        self.z_offset = 0
        self.offset = [0, 0]
        self.schedule = None
        if batch is not None:
            self._batch = batch
        self._x = x
        self._y = y
        self._z = z
        self._texture = img.get_texture()
        self._group = pyglet.sprite.SpriteGroup(self._texture, blend_src, blend_dest, group)
        self._usage = usage
        self._subpixel = subpixel
        self._create_vertex_list()

    def getPosition(self):
        return self.position

    def getSize(self):
        return (
         self.width, self.height)

    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height

    def setSize(self, width, height):
        self.update(scale_x=(width / self.image.width), scale_y=(height / self.image.height))

    def setScale(self, x, y):
        self.update(scale_x=x, scale_y=y)

    def setColor(self, r, g, b):
        self.color = (
         r, g, b)

    def setRGBA(self, r, g, b, a):
        self._opacity = a
        self.color = (r, g, b)

    def setAlpha(self, alpha):
        self.opacity = alpha

    @property
    def group(self):
        return self._group.parent

    @group.setter
    def group(self, group):
        if self._group.parent == group:
            return
        self._group = pyglet.sprite.SpriteGroup(self._texture, self._group.blend_src, self._group.blend_dest, group)
        if self._batch is not None:
            self._batch.migrate(self._vertex_list, GL_QUADS, self._group, self._batch)


class ElapsedTimerSpriteGroup(pyglet.sprite.SpriteGroup):
    __doc__ = "A sprite group that uses multiple active textures.\n    "

    def __init__(self, texture, blend_src, blend_dest, parent=None, program=None):
        super(pyglet.sprite.SpriteGroup, self).__init__(parent)
        self.texture = texture
        self.blend_src = blend_src
        self.blend_dest = blend_dest
        self.program = program

    def set_state(self):
        self.program.use_program()
        self.program["time"] = shaderService.elapsed
        glEnable(self.texture.target)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(self.texture.target, self.texture.id)
        glPushAttrib(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_BLEND)
        glBlendFunc(self.blend_src, self.blend_dest)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glEnable(GL_ALPHA_TEST)
        glAlphaFunc(GL_GREATER, 0.01)

    def unset_state(self):
        glPopAttrib()
        glBindTexture(self.texture.target, 0)
        glDisable(self.texture.target)
        glDisable(GL_DEPTH_TEST)
        self.program.stop_program()

    def __repr__(self):
        return "%s(%r-%d)" % (self.__class__.__name__, self.texture, self.texture.id)

    def __eq__(self, other):
        return other.__class__ is self.__class__ and self.program is other.program and self.texture == other.texture and self.blend_src == other.blend_src and self.blend_dest == other.blend_dest

    def __hash__(self):
        return hash((id(self.parent),
         id(self.texture),
         id(self.program),
         self.blend_src, self.blend_dest))


class TimerTextureSprite(PygletSprite):

    def __init__(self, img, x=0, y=0, z=0, blend_src=GL_SRC_ALPHA, blend_dest=GL_ONE_MINUS_SRC_ALPHA, batch=None, group=None, usage="dynamic", subpixel=False, program=None):
        self.alpha = 255
        self.z_offset = 0
        self._offset = [0, 0]
        self._previous_offset = [0, 0]
        self.schedule = None
        if batch is not None:
            self._batch = batch
        self._x = x
        self._y = y
        self._z = z
        self._texture = img.get_texture()
        self._group = ElapsedTimerSpriteGroup(self._texture, blend_src, blend_dest, group, program)
        self._usage = usage
        self._subpixel = subpixel
        self._create_vertex_list()


class TimerTextureSheet(PygletSheet):

    def __init__(self, sheet, x=0, y=0, z=0, blend_src=GL_SRC_ALPHA, blend_dest=GL_ONE_MINUS_SRC_ALPHA, batch=None, group=None, usage="dynamic", subpixel=False, program=None):
        self.sheet = sheet
        self._textureGrid = self.sheet.grid
        self._frameClamp = (
         0, len(self._textureGrid))
        self._frame_index = 0
        self.alpha = 255
        self.z_offset = 0
        self._offset = [0, 0]
        self._previous_offset = [0, 0]
        self.schedule = None
        if batch is not None:
            self._batch = batch
        self._x = x
        self._y = y
        self._z = z
        self._texture = self._textureGrid[self._frame_index].get_texture()
        self._group = ElapsedTimerSpriteGroup(self._texture, blend_src, blend_dest, group, program)
        self._usage = usage
        self._subpixel = subpixel
        self._create_vertex_list()


class MultiTextureSpriteGroup(pyglet.sprite.SpriteGroup):
    __doc__ = "A sprite group that uses multiple active textures.\n    "

    def __init__(self, textures, blend_src, blend_dest, parent=None, program=None):
        """Create a sprite group for multiple textures and samplers.
           All textures must share the same target type.

        :Parameters:
            `textures` : `dict`
                Textures in samplername : texture.
            `blend_src` : int
                OpenGL blend source mode; for example,
                ``GL_SRC_ALPHA``.
            `blend_dest` : int
                OpenGL blend destination mode; for example,
                ``GL_ONE_MINUS_SRC_ALPHA``.
            `parent` : `~pyglet.graphics.Group`
                Optional parent group.
        """
        super(pyglet.sprite.SpriteGroup, self).__init__(parent)
        self.textures = textures
        self.target = list(self.textures.values())[0].target
        self.blend_src = blend_src
        self.blend_dest = blend_dest
        self.program = program or default_sprite_shader

    def set_state(self):
        self.program.use_program()
        for idx, name in enumerate(self.textures):
            self.program[name] = idx

        glEnable(self.target)
        for i, texture in enumerate(self.textures.values()):
            glActiveTexture(GL_TEXTURE0 + i)
            glBindTexture(self.target, texture.id)

        glPushAttrib(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_BLEND)
        glBlendFunc(self.blend_src, self.blend_dest)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glEnable(GL_ALPHA_TEST)
        glAlphaFunc(GL_GREATER, 0.01)

    def unset_state(self):
        glPopAttrib()
        glDisable(self.target)
        glDisable(GL_DEPTH_TEST)
        self.program.stop_program()
        glActiveTexture(GL_TEXTURE0)

    def __repr__(self):
        return "%s(%r-%d)" % (self.__class__.__name__, self.texture, self.texture.id)

    def __eq__(self, other):
        return other.__class__ is self.__class__ and self.program is other.program and self.textures == other.textures and self.blend_src == other.blend_src and self.blend_dest == other.blend_dest

    def __hash__(self):
        return hash((id(self.parent),
         id(self.textures),
         self.blend_src, self.blend_dest))


class MultiTextureSprite(PygletSprite):

    def __init__(self, imgs, x=0, y=0, z=0, blend_src=GL_SRC_ALPHA, blend_dest=GL_ONE_MINUS_SRC_ALPHA, batch=None, group=None, usage="dynamic", subpixel=False, program=None):
        self.alpha = 255
        self.z_offset = 0
        self.offset = [0, 0]
        self.schedule = None
        if batch is not None:
            self._batch = batch
        self._x = x
        self._y = y
        self._z = z
        self._texture = list(imgs.values())[0]
        self._group = MultiTextureSpriteGroup(imgs, blend_src, blend_dest, group, program)
        self._usage = usage
        self._subpixel = subpixel
        self._create_vertex_list()


class Line(pyglet.shapes._ShapeBase):

    def __init__(self, x, y, x2, y2, z, width=1, color=(255, 255, 255), opacity=255, batch=None, group=None):
        """Create a line.

        The line's anchor point defaults to the center of the line's
        width on the X axis, and the Y axis.

        :Parameters:
            `x` : float
                The first X coordinate of the line.
            `y` : float
                The first Y coordinate of the line.
            `x2` : float
                The second X coordinate of the line.
            `y2` : float
                The second Y coordinate of the line.
            `width` : float
                The desired width of the line.
            `color` : (int, int, int)
                The RGB color of the line, specified as a tuple of
                three ints in the range of 0-255.
            `batch` : `~pyglet.graphics.Batch`
                Optional batch to add the line to.
            `group` : `~pyglet.graphics.Group`
                Optional parent group of the line.
        """
        self._x = x
        self._y = y
        self._x2 = x2
        self._y2 = y2
        self._z = z
        self._width = width
        self._rotation = math.degrees(math.atan2(y2 - y, x2 - x))
        self._rgb = color
        self._opacity = opacity
        self._batch = batch or pyglet.graphics.Batch()
        self._group = pyglet.shapes._ShapeGroup(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, group)
        self._vertex_list = self._batch.add(6, GL_TRIANGLES, self._group, "v3f", "c4B")
        self._update_position()
        self._update_color()

    def _update_position(self):
        if not self._visible:
            self._vertex_list.vertices[:] = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                             0, 0, 0, 0, 0)
        else:
            x1 = -self._anchor_y
            y1 = self._anchor_x - self._width / 2
            x = self._x
            y = self._y
            x2 = x1 + math.hypot(self._y2 - y, self._x2 - x)
            y2 = y1 + self._width
            r = math.atan2(self._y2 - y, self._x2 - x)
            cr = math.cos(r)
            sr = math.sin(r)
            ax = x1 * cr - y1 * sr + x
            ay = x1 * sr + y1 * cr + y
            bx = x2 * cr - y1 * sr + x
            by = x2 * sr + y1 * cr + y
            cx = x2 * cr - y2 * sr + x
            cy = x2 * sr + y2 * cr + y
            dx = x1 * cr - y2 * sr + x
            dy = x1 * sr + y2 * cr + y
            self._vertex_list.vertices[:] = (ax, ay, self._z, bx, by, self._z, cx, cy, self._z, ax, ay, self._z, cx, cy, self._z, dx, dy, self._z)

    def _update_color(self):
        self._vertex_list.colors[:] = [*self._rgb, int(self._opacity)] * 6

    @property
    def x2(self):
        """Second X coordinate of the shape.

        :type: int or float
        """
        return self._x2

    @x2.setter
    def x2(self, value):
        self._x2 = value
        self._update_position()

    @property
    def y2(self):
        """Second Y coordinate of the shape.

        :type: int or float
        """
        return self._y2

    @y2.setter
    def y2(self, value):
        self._y2 = value
        self._update_position()

    @property
    def position(self):
        """The (x, y, x2, y2) coordinates of the line, as a tuple.

        :Parameters:
            `x` : int or float
                X coordinate of the line.
            `y` : int or float
                Y coordinate of the line.
            `x2` : int or float
                X2 coordinate of the line.
            `y2` : int or float
                Y2 coordinate of the line.
        """
        return (
         self._x, self._y, self._x2, self._y2)

    @position.setter
    def position(self, values):
        self._x, self._y, self._x2, self._y2 = values
        self._update_position()
