# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\render\system\cursor.py
from client.render.cache import textureCache
from pyglet.gl import *
from client.control.service.session import sessionService
from client.control.camera import worldCamera
import math
from shared.container.constants import CursorMode
from client.data.gui.styleDB import cursorText
from client.render.sprite import TextSprite

class SoftwareCursor:
    gl_drawable = True
    hw_drawable = False
    drawable = True
    hardware = False

    def __init__(self, renderer, image, hot_x, hot_y):
        self.renderer = renderer
        self.cursor = None
        self.image = image.get_texture()
        self.texture = self.image
        self.hot_x = hot_x
        self.hot_y = hot_y

    def draw(self, x, y):
        gl.glPushAttrib(gl.GL_ENABLE_BIT | gl.GL_CURRENT_BIT)
        gl.glColor4f(1, 1, 1, 1)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        if self.renderer.mode in CursorMode.NO_TEXTURE:
            self.drawCircle(x - self.hot_x, y - self.hot_y)
        else:
            self.image.blit(x - self.hot_x, y - self.hot_y, 0)
        if self.renderer.label.visible:
            self.renderer.label.update(x + 26, y)
            self.renderer.labelShadow.update(x + 27, y - 1)
            self.renderer.batch.draw()
        gl.glPopAttrib()


class HardwareCursor:
    gl_drawable = True
    hw_drawable = True
    drawable = True
    hardware = True

    def __init__(self, renderer, image, hot_x, hot_y):
        self.renderer = renderer
        self.cursor = None
        self.image = image.get_texture()
        self.texture = self.image
        self.hot_x = hot_x
        self.hot_y = hot_y

    def draw(self, x, y):
        gl.glPushAttrib(gl.GL_ENABLE_BIT | gl.GL_CURRENT_BIT)
        gl.glColor4f(1, 1, 1, 1)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        if self.renderer.mode in CursorMode.NO_TEXTURE:
            self.renderer.drawCircle(x - self.hot_x, y - self.hot_y)
        else:
            if self.renderer.label.visible:
                self.renderer.label.update(x + 26, y)
                self.renderer.labelShadow.update(x + 27, y - 1)
                self.renderer.batch.draw()
        gl.glPopAttrib()


class CustomImageCursor(object):
    gl_drawable = False
    drawable = False

    def __init__(self, hardwareEnabled):
        self.hardwareEnabled = hardwareEnabled
        self.cursors = {}
        self._cursor_textures = {(CursorMode.DEFAULT): (pyglet.resource.image("lib/system/cursor/default.png")), 
         (CursorMode.POINTER): (pyglet.resource.image("lib/system/cursor/pointer.png")), 
         (CursorMode.DRAGBEGIN): (pyglet.resource.image("lib/system/cursor/grab.png")), 
         (CursorMode.DRAGGING): (pyglet.resource.image("lib/system/cursor/dragging.png")), 
         (CursorMode.TARGET): (pyglet.resource.image("lib/system/cursor/target.png")), 
         (CursorMode.TEXT): (pyglet.resource.image("lib/system/cursor/caret.png"))}
        _cursor_hotspots = {(CursorMode.DEFAULT): (0, 22), 
         (CursorMode.POINTER): (0, 18), 
         (CursorMode.DRAGBEGIN): (0, 18), 
         (CursorMode.DRAGGING): (9, 8), 
         (CursorMode.TARGET): (8, 8), 
         (CursorMode.TEXT): (3, 8)}
        if self.hardwareEnabled:
            cursor_class = HardwareCursor
        else:
            cursor_class = SoftwareCursor
        for cursor, data in _cursor_hotspots.items():
            self.cursors[cursor] = cursor_class(self, self._cursor_textures[cursor], *data)

        self.radius = 200
        self._mode = None
        self.mode = CursorMode.DEFAULT
        self.batch = pyglet.graphics.Batch()
        self.label = TextSprite(text="", x=20,
          y=20,
          z=3000,
          font_name=(cursorText.font.name),
          font_size=(cursorText.font.size),
          color=(cursorText.color + (255, )),
          batch=(self.batch))
        self.labelShadow = TextSprite(text="", x=20,
          y=20,
          z=2999,
          font_name=(cursorText.font.name),
          font_size=(cursorText.font.size),
          color=(0, 0, 0, 255),
          batch=(self.batch))

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, mode):
        if self.mode != mode:
            self._mode = mode

    def drawCircle(self, x, y):
        if self.mode == CursorMode.PLAYER_CIRCLE:
            x, y = (worldCamera.toScreenPosition)(*sessionService.getSelectedChar().getPosition2D())
        verts = []
        for i in range(32):
            cosine = self.radius * math.cos(i * 2 * math.pi / 32) / worldCamera.zoom + x
            sine = self.radius / 2 * math.sin(i * 2 * math.pi / 32) / worldCamera.zoom + y
            verts += [cosine, sine]

        pyglet.graphics.draw(32, pyglet.gl.GL_LINE_LOOP, (
         "v2f", verts))
