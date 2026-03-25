# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\render\custom.py
"""
Created on Sep 9, 2019

@author: Admin

File for overriding pyglets default behavior instead of editing pyglet directly.
"""
import pyglet
from pyglet.gl import *
import math
from pyglet import app
from client.render.shader.default_sprite import default_sprite_shader
from _ctypes import byref, sizeof
from pyglet.image import ImageException, _is_pow2
from pyglet.window import MouseCursor, DefaultMouseCursor
from pyglet.window.win32 import Win32MouseCursor, _win32_cursor_visible
from pyglet.libs.win32 import _user32, _gdi32
from pyglet.libs.win32.constants import IDC_ARROW, GCL_HCURSOR, DIB_RGB_COLORS
from pyglet.libs.win32.types import MAKEINTRESOURCE, BITMAPINFOHEADER, ICONINFO
from ctypes import c_void_p, memmove

class EventLoop(pyglet.app.EventLoop):

    def idle(self):
        dt = self.clock.update_time()
        redraw_all = self.clock.call_scheduled_functions(dt)
        for window in app.windows:
            if redraw_all or window._legacy_invalid and window.invalid:
                window.dispatch_event("on_draw")
                window.flip()
                window._legacy_invalid = False

        return self.clock.get_sleep_time(True)


pyglet.app.EventLoop.idle = EventLoop.idle

class Projection2D(pyglet.window.Projection):
    __doc__ = "A 2D orthographic projection"

    def set(self, window_width, window_height, viewport_width, viewport_height):
        glViewport(0, 0, viewport_width, viewport_height)
        glMatrixMode(gl.GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, window_width, 0, window_height, -3000, 3000)
        glMatrixMode(gl.GL_MODELVIEW)


pyglet.window._projection = Projection2D

class Texture(pyglet.image.Texture):

    @classmethod
    def create(cls, width, height, internalformat=GL_RGBA, rectangle=False, force_rectangle=False, min_filter=None, mag_filter=None):
        min_filter = min_filter or cls.default_min_filter
        mag_filter = mag_filter or cls.default_mag_filter
        target = GL_TEXTURE_2D
        if rectangle or force_rectangle:
            if not force_rectangle:
                if _is_pow2(width):
                    if _is_pow2(height):
                        rectangle = False
                if gl_info.have_extension("GL_ARB_texture_rectangle"):
                    target = GL_TEXTURE_RECTANGLE_ARB
                    rectangle = True
            elif gl_info.have_extension("GL_NV_texture_rectangle"):
                target = GL_TEXTURE_RECTANGLE_NV
                rectangle = True
            else:
                rectangle = False
        if force_rectangle:
            if not rectangle:
                raise ImageException("Texture rectangle extensions not available")
        texture_width = width
        texture_height = height
        id = GLuint()
        glGenTextures(1, byref(id))
        glBindTexture(target, id.value)
        glTexParameteri(target, GL_TEXTURE_MIN_FILTER, min_filter)
        glTexParameteri(target, GL_TEXTURE_MAG_FILTER, mag_filter)
        blank = GLubyte * (texture_width * texture_height * 4)()
        glTexImage2D(target, 0, internalformat, texture_width, texture_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, blank)
        texture = cls(texture_width, texture_height, target, id.value)
        texture.min_filter = min_filter
        texture.mag_filter = mag_filter
        if rectangle:
            texture._is_rectangle = True
            texture.tex_coords = (0.0, 0.0, 0.0,
             width, 0.0, 0.0,
             width, height, 0.0,
             0.0, height, 0.0)
        glFlush()
        return texture

    @classmethod
    def create_for_size(cls, target, min_width, min_height, internalformat=None, min_filter=None, mag_filter=None):
        width = min_width
        height = min_height
        if target not in (GL_TEXTURE_RECTANGLE_NV, GL_TEXTURE_RECTANGLE_ARB):
            tex_coords = cls.tex_coords
        else:
            tex_coords = (
             0.0, 0.0, 0.0,
             width, 0.0, 0.0,
             width, height, 0.0,
             0.0, height, 0.0)
        min_filter = min_filter or cls.default_min_filter
        mag_filter = mag_filter or cls.default_mag_filter
        id = GLuint()
        glGenTextures(1, byref(id))
        glBindTexture(target, id.value)
        glTexParameteri(target, GL_TEXTURE_MIN_FILTER, min_filter)
        glTexParameteri(target, GL_TEXTURE_MAG_FILTER, mag_filter)
        if internalformat is not None:
            blank = GLubyte * (width * height * 4)()
            glTexImage2D(target, 0, internalformat, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, blank)
            glFlush()
        texture = cls(width, height, target, id.value)
        texture.min_filter = min_filter
        texture.mag_filter = mag_filter
        texture.tex_coords = tex_coords
        return texture


class Texture3D(pyglet.image.Texture3D):
    __doc__ = "A texture with more than one image slice.\n\n    Use `create_for_images` or `create_for_image_grid` classmethod to\n    construct.\n    "

    @classmethod
    def create_for_images(cls, images, internalformat=GL_RGBA):
        item_width = images[0].width
        item_height = images[0].height
        for image in images:
            if image.width != item_width or image.height != item_height:
                raise ImageException("Images do not have same dimensions.")

        depth = len(images)
        texture = cls.create_for_size(GL_TEXTURE_3D, item_width, item_height)
        if images[0].anchor_x or images[0].anchor_y:
            texture.anchor_x = images[0].anchor_x
            texture.anchor_y = images[0].anchor_y
        texture.images = depth
        blank = GLubyte * (texture.width * texture.height * texture.images)()
        glBindTexture(texture.target, texture.id)
        glTexImage3D(texture.target, texture.level, internalformat, texture.width, texture.height, texture.images, 0, GL_ALPHA, GL_UNSIGNED_BYTE, blank)
        items = []
        for i, image in enumerate(images):
            item = cls.region_class(0, 0, i, item_width, item_height, texture)
            items.append(item)
            image.blit_to_texture(texture.target, texture.level, image.anchor_x, image.anchor_y, i)

        glFlush()
        texture.items = items
        texture.item_width = item_width
        texture.item_height = item_height
        return texture


pyglet.image.Texture3D = Texture3D

class ZSpriteGroup(pyglet.graphics.Group):
    __doc__ = " Supports shaders "

    def __init__(self, texture, blend_src, blend_dest, parent=None, program=None):
        super().__init__(parent)
        self.texture = texture
        self.blend_src = blend_src
        self.blend_dest = blend_dest
        self.program = program or default_sprite_shader

    def set_state(self):
        self.program.use_program()
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
        return "%s(%r-%d-%r)" % (self.__class__.__name__, self.texture, self.texture.id, self.program)

    def __eq__(self, other):
        return other.__class__ is self.__class__ and self.program is other.program and self.texture.target == other.texture.target and self.texture.id == other.texture.id and self.blend_src == other.blend_src and self.blend_dest == other.blend_dest

    def __hash__(self):
        return hash((id(self.parent), id(self.program),
         self.texture.id, self.texture.target,
         self.blend_src, self.blend_dest))


pyglet.sprite.SpriteGroup = ZSpriteGroup

class ZSprite(pyglet.sprite.Sprite):
    __doc__ = " Supports Z layer "

    def __init__(self, img, x=0, y=0, z=0, blend_src=GL_SRC_ALPHA, blend_dest=GL_ONE_MINUS_SRC_ALPHA, batch=None, group=None, usage="dynamic", subpixel=False):
        if batch is not None:
            self._batch = batch
        self._x = x
        self._y = y
        self._z = z
        self._texture = img.get_texture()
        self._group = ZSpriteGroup(self._texture, blend_src, blend_dest, group)
        self._usage = usage
        self._subpixel = subpixel
        self._create_vertex_list()

    @property
    def group(self):
        return self._group.parent

    @group.setter
    def group(self, group):
        if self._group.parent == group:
            return
        self._group = self._group.__class__(self._texture, self._group.blend_src, self._group.blend_dest, group)
        if self._batch is not None:
            self._batch.migrate(self._vertex_list, GL_QUADS, self._group, self._batch)

    @property
    def shader_program(self):
        return self._group.program

    @shader_program.setter
    def shader_program(self, program):
        if self._group.program == program:
            return
        self._group = self._group.__class__((self._texture), (self._group.blend_src), (self._group.blend_dest), program=program)
        self._batch.migrate(self._vertex_list, GL_QUADS, self._group, self._batch)

    def _create_vertex_list(self):
        if self._subpixel:
            vertex_format = "v3f/%s" % self._usage
        else:
            vertex_format = "v3i/%s" % self._usage
        if self._batch is None:
            self._vertex_list = pyglet.graphics.vertex_list(4, vertex_format, "c4B", ("t3f", self._texture.tex_coords))
        else:
            self._vertex_list = self._batch.add(4, GL_QUADS, self._group, vertex_format, "c4B", ("t3f", self._texture.tex_coords))
        self._update_position()
        self._update_color()

    def _update_position(self):
        img = self._texture
        scale_x = self._scale * self.scale_x
        scale_y = self._scale * self.scale_y
        if not self._visible:
            vertices = [
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
             0]
        elif self._rotation:
            x1 = -img.anchor_x * scale_x
            y1 = -img.anchor_y * scale_y
            x2 = x1 + img.width * scale_x
            y2 = y1 + img.height * scale_y
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
            vertices = [ax, ay, z, bx, by, z, cx, cy, z, dx, dy, z]
        elif scale_x != 1.0 or scale_y != 1.0:
            x1 = self._x - img.anchor_x * scale_x
            y1 = self._y - img.anchor_y * scale_y
            x2 = x1 + img.width * scale_x
            y2 = y1 + img.height * scale_y
            z = self._z
            vertices = [x1, y1, z, x2, y1, z, x2, y2, z, x1, y2, z]
        else:
            x1 = self._x - img.anchor_x
            y1 = self._y - img.anchor_y
            x2 = x1 + img.width
            y2 = y1 + img.height
            z = self._z
            vertices = [x1, y1, z, x2, y1, z, x2, y2, z, x1, y2, z]
        if not self._subpixel:
            vertices = [int(v) for v in vertices]
        self._vertex_list.vertices[:] = vertices

    @property
    def z(self):
        """Z coordinate of the sprite.

        :type: int
        """
        return self._z

    @z.setter
    def z(self, z):
        self._z = z
        self._update_position()

    def update(self, x=None, y=None, z=None, rotation=None, scale=None, scale_x=None, scale_y=None):
        if x is not None:
            self._x = x
        else:
            if y is not None:
                self._y = y
            else:
                if z is not None:
                    self._z = z
                else:
                    if rotation is not None:
                        self._rotation = rotation
                    if scale is not None:
                        self._scale = scale
                if scale_x is not None:
                    self._scale_x = scale_x
            if scale_y is not None:
                self._scale_y = scale_y
        self._update_position()


pyglet.sprite.Sprite = ZSprite

class _AbstractBox(object):
    owner = None

    def __init__(self, ascent, descent, advance, length):
        self.ascent = ascent
        self.descent = descent
        self.advance = advance
        self.length = length

    def place(self, layout, i, x, y, z):
        raise NotImplementedError("abstract")

    def delete(self, layout):
        raise NotImplementedError("abstract")

    def get_position_in_box(self, x):
        raise NotImplementedError("abstract")

    def get_point_in_box(self, position):
        raise NotImplementedError("abstract")


pyglet.text.layout._AbstractBox = _AbstractBox

class _GlyphBox(_AbstractBox):

    def __init__(self, owner, font, glyphs, advance):
        """Create a run of glyphs sharing the same texture.

        :Parameters:
            `owner` : `pyglet.image.Texture`
                Texture of all glyphs in this run.
            `font` : `pyglet.font.base.Font`
                Font of all glyphs in this run.
            `glyphs` : list of (int, `pyglet.font.base.Glyph`)
                Pairs of ``(kern, glyph)``, where ``kern`` gives horizontal
                displacement of the glyph in pixels (typically 0).
            `advance` : int
                Width of glyph run; must correspond to the sum of advances
                and kerns in the glyph list.

        """
        super(_GlyphBox, self).__init__(font.ascent, font.descent, advance, len(glyphs))
        assert owner
        self.owner = owner
        self.font = font
        self.glyphs = glyphs
        self.advance = advance

    def place(self, layout, i, x, y, z, context):
        if not self.glyphs:
            raise AssertionError
        else:
            try:
                group = layout.groups[self.owner]
            except KeyError:
                group = layout.groups[self.owner] = TextLayoutTextureGroup(self.owner, layout.foreground_group)

            n_glyphs = self.length
            vertices = []
            tex_coords = []
            x1 = x
            for start, end, baseline in context.baseline_iter.ranges(i, i + n_glyphs):
                baseline = layout._parse_distance(baseline)
                assert len(self.glyphs[start - i:end - i]) == end - start
                for kern, glyph in self.glyphs[start - i:end - i]:
                    x1 += kern
                    v0, v1, v2, v3 = glyph.vertices
                    v0 += x1
                    v2 += x1
                    v1 += y + baseline
                    v3 += y + baseline
                    vertices.extend(map(int, [v0, v1, z, v2, v1, z, v2, v3, z, v0, v3, z]))
                    t = glyph.tex_coords
                    tex_coords.extend(t)
                    x1 += glyph.advance

            colors = []
            for start, end, color in context.colors_iter.ranges(i, i + n_glyphs):
                if color is None:
                    color = (0, 0, 0, 255)
                colors.extend(color * ((end - start) * 4))

            vertex_list = layout.batch.add(n_glyphs * 4, GL_QUADS, group, (
             "v3f/dynamic", vertices), (
             "t3f/dynamic", tex_coords), (
             "c4B/dynamic", colors))
            context.add_list(vertex_list)
            background_vertices = []
            background_colors = []
            underline_vertices = []
            underline_colors = []
            y1 = y + self.descent + baseline
            y2 = y + self.ascent + baseline
            x1 = x
            for start, end, decoration in context.decoration_iter.ranges(i, i + n_glyphs):
                bg, underline = decoration
                x2 = x1
                for kern, glyph in self.glyphs[start - i:end - i]:
                    x2 += glyph.advance + kern

                if bg is not None:
                    background_vertices.extend([
                     x1, y1, x2, y1, 
                     x2, y2, x1, y2])
                    background_colors.extend(bg * 4)
                if underline is not None:
                    underline_vertices.extend([
                     x1, y + baseline - 2, x2, y + baseline - 2])
                    underline_colors.extend(underline * 2)
                x1 = x2

            if background_vertices:
                background_list = layout.batch.add(len(background_vertices) // 2, GL_QUADS, layout.background_group, (
                 "v2f/dynamic", background_vertices), (
                 "c4B/dynamic", background_colors))
                context.add_list(background_list)
            if underline_vertices:
                underline_list = layout.batch.add(len(underline_vertices) // 2, GL_LINES, layout.foreground_decoration_group, (
                 "v2f/dynamic", underline_vertices), (
                 "c4B/dynamic", underline_colors))
                context.add_list(underline_list)


pyglet.text.layout._GlyphBox = _GlyphBox

class _InlineElementBox(_AbstractBox):

    def __init__(self, element):
        """Create a glyph run holding a single element.
        """
        super(_InlineElementBox, self).__init__(element.ascent, element.descent, element.advance, 1)
        self.element = element
        self.placed = False

    def place(self, layout, i, x, y, z, context):
        self.element.place(layout, x, y, z)
        self.placed = True
        context.add_box(self)

    def delete(self, layout):
        if self.placed:
            self.element.remove(layout)
            self.placed = False

    def get_point_in_box(self, position):
        if position == 0:
            return 0
        else:
            return self.advance

    def get_position_in_box(self, x):
        if x < self.advance // 2:
            return 0
        else:
            return 1

    def __repr__(self):
        return "_InlineElementBox(%r)" % self.element


pyglet.text.layout._InlineElementBox = _InlineElementBox

class TextLayoutForegroundGroup(pyglet.graphics.OrderedGroup):
    __doc__ = "Rendering group for foreground elements (glyphs) in all text layouts.\n\n    The group enables ``GL_TEXTURE_2D``.\n    "

    def set_state(self):
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glEnable(GL_ALPHA_TEST)
        glAlphaFunc(GL_GREATER, 0.01)


pyglet.text.layout.TextLayoutForegroundGroup = TextLayoutForegroundGroup

class TextLayoutForegroundDecorationGroup(pyglet.graphics.OrderedGroup):
    __doc__ = "Rendering group for decorative elements (e.g., glyph underlines) in all\n    text layouts.\n\n    The group disables ``GL_TEXTURE_2D``.\n    "

    def set_state(self):
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_DEPTH_TEST)


pyglet.text.layout.TextLayoutForegroundDecorationGroup = TextLayoutForegroundDecorationGroup

class TextLayoutTextureGroup(pyglet.graphics.Group):
    __doc__ = "Rendering group for a glyph texture in all text layouts.\n\n    The group binds its texture to ``GL_TEXTURE_2D``.  The group is shared\n    between all other text layout uses of the same texture.\n    "

    def __init__(self, texture, parent):
        assert texture.target == GL_TEXTURE_2D
        super(TextLayoutTextureGroup, self).__init__(parent)
        self.texture = texture

    def set_state(self):
        glBindTexture(GL_TEXTURE_2D, self.texture.id)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glEnable(GL_ALPHA_TEST)
        glAlphaFunc(GL_GREATER, 0.01)

    def __hash__(self):
        return hash((self.texture.id, self.parent))

    def __eq__(self, other):
        return self.__class__ is other.__class__ and self.texture.id == other.texture.id and self.parent is other.parent

    def __repr__(self):
        return "%s(%d, %r)" % (self.__class__.__name__,
         self.texture.id,
         self.parent)


pyglet.text.layout.TextLayoutTextureGroup = TextLayoutTextureGroup

class TextLayout(pyglet.text.layout.TextLayout):

    def _update(self):
        if not self._update_enabled:
            return
        else:
            for _vertex_list in self._vertex_lists:
                _vertex_list.delete()

            for box in self._boxes:
                box.delete(self)

            self._vertex_lists = []
            self._boxes = []
            self.groups.clear()
            if not self._document or not self._document.text:
                return
            lines = self._get_lines()
            colors_iter = self._document.get_style_runs("color")
            background_iter = self._document.get_style_runs("background_color")
            if self._origin_layout:
                left = top = 0
            else:
                left = self._get_left()
            top = self._get_top(lines)
        context = pyglet.text.layout._StaticLayoutContext(self, self._document, colors_iter, background_iter)
        for line in lines:
            self._create_vertex_lists(left + line.x, top + line.y, self._z, line.start, line.boxes, context)

    def _create_vertex_lists(self, x, y, z, i, boxes, context):
        for box in boxes:
            box.place(self, i, x, y, z, context)
            x += box.advance
            i += box.length

    def _set_x(self, x):
        if self._boxes:
            self._x = x
            self._update()
        else:
            dx = x - self._x
            l_dx = lambda x: int(x + dx)
            for vertex_list in self._vertex_lists:
                vertices = vertex_list.vertices[:]
                vertices[::3] = list(map(l_dx, vertices[::3]))
                vertex_list.vertices[:] = vertices

            self._x = x

    def _set_y(self, y):
        if self._boxes:
            self._y = y
            self._update()
        else:
            dy = y - self._y
            l_dy = lambda y: int(y + dy)
            for vertex_list in self._vertex_lists:
                vertices = vertex_list.vertices[:]
                vertices[1::3] = list(map(l_dy, vertices[1::3]))
                vertex_list.vertices[:] = vertices

            self._y = y

    def update(self, x, y):
        if self._boxes:
            self._x = x
            self._y = y
            self._update()
        else:
            dx = x - self._x
            dy = y - self._y
            l_dx = lambda x: x + dx
            l_dy = lambda y: y + dy
            for vertex_list in self._vertex_lists:
                vertices = vertex_list.vertices[:]
                vertices[::3] = list(map(l_dx, vertices[::3]))
                vertices[1::3] = list(map(l_dy, vertices[1::3]))
                vertex_list.vertices[:] = vertices

            self._x = x
            self._y = y

    @property
    def z(self):
        return self._z

    @z.setter
    def z(self, value):
        self._z = value
        for vertex_list in self._vertex_lists:
            vertices = vertex_list.vertices[:]
            vertices[2::3] = [self._z + self.z_offset for i in range(len(vertices[2::3]))]
            vertex_list.vertices[:] = vertices


pyglet.text.layout.TextLayout = TextLayout

class DocumentLabel(pyglet.text.layout.TextLayout):
    __doc__ = "Base label class.\n\n    A label is a layout that exposes convenience methods for manipulating the\n    associated document.\n    "

    def __init__(self, document=None, x=0, y=0, z=0, width=None, height=None, anchor_x='left', anchor_y='baseline', multiline=False, dpi=None, batch=None, group=None):
        """Create a label for a given document.

        :Parameters:
            `document` : `AbstractDocument`
                Document to attach to the layout.
            `x` : int
                X coordinate of the label.
            `y` : int
                Y coordinate of the label.
            `width` : int
                Width of the label in pixels, or None
            `height` : int
                Height of the label in pixels, or None
            `anchor_x` : str
                Anchor point of the X coordinate: one of ``"left"``,
                ``"center"`` or ``"right"``.
            `anchor_y` : str
                Anchor point of the Y coordinate: one of ``"bottom"``,
                ``"baseline"``, ``"center"`` or ``"top"``.
            `multiline` : bool
                If True, the label will be word-wrapped and accept newline
                characters.  You must also set the width of the label.
            `dpi` : float
                Resolution of the fonts in this layout.  Defaults to 96.
            `batch` : `~pyglet.graphics.Batch`
                Optional graphics batch to add the label to.
            `group` : `~pyglet.graphics.Group`
                Optional graphics group to use.

        """
        self._x = x
        self._y = y
        self._z = z
        super(DocumentLabel, self).__init__(document, width=width,
          height=height,
          multiline=multiline,
          dpi=dpi,
          batch=batch,
          group=group)
        self._anchor_x = anchor_x
        self._anchor_y = anchor_y
        self._update()

    @property
    def text(self):
        """The text of the label.

        :type: str
        """
        return self.document.text

    @text.setter
    def text(self, text):
        self.document.text = text

    @property
    def color(self):
        """Text color.

        Color is a 4-tuple of RGBA components, each in range [0, 255].

        :type: (int, int, int, int)
        """
        return self.document.get_style("color")

    @color.setter
    def color(self, color):
        self.document.set_style(0, len(self.document.text), {"color": color})

    @property
    def font_name(self):
        """Font family name.

        The font name, as passed to :py:func:`pyglet.font.load`.  A list of names can
        optionally be given: the first matching font will be used.

        :type: str or list
        """
        return self.document.get_style("font_name")

    @font_name.setter
    def font_name(self, font_name):
        self.document.set_style(0, len(self.document.text), {"font_name": font_name})

    @property
    def font_size(self):
        """Font size, in points.

        :type: float
        """
        return self.document.get_style("font_size")

    @font_size.setter
    def font_size(self, font_size):
        self.document.set_style(0, len(self.document.text), {"font_size": font_size})

    @property
    def bold(self):
        """Bold font style.

        :type: bool
        """
        return self.document.get_style("bold")

    @bold.setter
    def bold(self, bold):
        self.document.set_style(0, len(self.document.text), {"bold": bold})

    @property
    def italic(self):
        """Italic font style.

        :type: bool
        """
        return self.document.get_style("italic")

    @italic.setter
    def italic(self, italic):
        self.document.set_style(0, len(self.document.text), {"italic": italic})

    def get_style(self, name):
        """Get a document style value by name.

        If the document has more than one value of the named style,
        `pyglet.text.document.STYLE_INDETERMINATE` is returned.

        :Parameters:
            `name` : str
                Style name to query.  See documentation for
                `pyglet.text.layout` for known style names.

        :rtype: object
        """
        return self.document.get_style_range(name, 0, len(self.document.text))

    def set_style(self, name, value):
        """Set a document style value by name over the whole document.

        :Parameters:
            `name` : str
                Name of the style to set.  See documentation for
                `pyglet.text.layout` for known style names.
            `value` : object
                Value of the style.

        """
        self.document.set_style(0, len(self.document.text), {name: value})


pyglet.text.DocumentLabel = DocumentLabel

class Label(pyglet.text.DocumentLabel):
    __doc__ = "Plain text label.\n    "

    def __init__(self, text='', font_name=None, font_size=None, bold=False, italic=False, color=(255, 255, 255, 255), x=0, y=0, z=0, width=None, height=None, anchor_x='left', anchor_y='baseline', align='left', multiline=False, dpi=None, batch=None, group=None):
        """Create a plain text label.

        :Parameters:
            `text` : str
                Text to display.
            `font_name` : str or list
                Font family name(s).  If more than one name is given, the
                first matching name is used.
            `font_size` : float
                Font size, in points.
            `bold` : bool
                Bold font style.
            `italic` : bool
                Italic font style.
            `color` : (int, int, int, int)
                Font colour, as RGBA components in range [0, 255].
            `x` : int
                X coordinate of the label.
            `y` : int
                Y coordinate of the label.
            `width` : int
                Width of the label in pixels, or None
            `height` : int
                Height of the label in pixels, or None
            `anchor_x` : str
                Anchor point of the X coordinate: one of ``"left"``,
                ``"center"`` or ``"right"``.
            `anchor_y` : str
                Anchor point of the Y coordinate: one of ``"bottom"``,
                ``"baseline"``, ``"center"`` or ``"top"``.
            `align` : str
                Horizontal alignment of text on a line, only applies if
                a width is supplied. One of ``"left"``, ``"center"``
                or ``"right"``.
            `multiline` : bool
                If True, the label will be word-wrapped and accept newline
                characters.  You must also set the width of the label.
            `dpi` : float
                Resolution of the fonts in this layout.  Defaults to 96.
            `batch` : `~pyglet.graphics.Batch`
                Optional graphics batch to add the label to.
            `group` : `~pyglet.graphics.Group`
                Optional graphics group to use.

        """
        document = pyglet.text.decode_text(text)
        super(Label, self).__init__(document, x, y, z, width, height, anchor_x, anchor_y, multiline, dpi, batch, group)
        self.document.set_style(0, len(self.document.text), {
         'font_name': font_name, 
         'font_size': font_size, 
         'bold': bold, 
         'italic': italic, 
         'color': color, 
         'align': align})


pyglet.text.Label = Label
pyglet.image.Texture.default_min_filter = GL_NEAREST
pyglet.image.Texture.default_mag_filter = GL_NEAREST
pyglet.font.base.Font.texture_min_filter = GL_NEAREST
pyglet.font.base.Font.texture_mag_filter = GL_NEAREST
