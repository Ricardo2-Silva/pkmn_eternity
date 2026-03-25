# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\render\render.py
import client.control.camera as camera, rabbyt, pyglet
from pyglet.gl import *
from client.data.settings import gameSettings
from client.scene.manager import sceneManager
from client.render.layer import worldLayer, backgroundLayer, lightLayer
from client.render.world.weather import weatherRender
import math

class FixedResolutionViewport(object):

    def __init__(self, window, camera, width, height, filtered=False):
        self.shaders = []
        self.window = window
        self.camera = camera
        self.width = width
        self.height = height
        self.filtered = filtered
        self._calculate_viewport(self.window.width, self.window.height)
        self.elapsed = 0
        self.texture = pyglet.image.Texture.create(width, height, rectangle=False)
        if not filtered:
            glTexParameteri(self.texture.target, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glTexParameteri(self.texture.target, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

    def _calculate_viewport(self, new_screen_width, new_screen_height):
        aspect_ratio = self.width / self.height
        aspect_width = new_screen_width
        aspect_height = aspect_width / aspect_ratio + 0.5
        if aspect_height > new_screen_height:
            aspect_height = new_screen_height
            aspect_width = aspect_height * aspect_ratio + 0.5
        if not self.filtered:
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        self._viewport = (int(new_screen_width / 2 - aspect_width / 2),
         int(new_screen_height / 2 - aspect_height / 2),
         0,
         int(aspect_width),
         int(aspect_height))

    def begin(self):
        glViewport(0, 0, self.width, self.height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.width, 0, self.height, -3000, 3000)
        glMatrixMode(GL_MODELVIEW)
        glScalef(self.camera.zoom, self.camera.zoom, 1)
        glTranslatef(-round(self.camera.offsetX), -round(self.camera.offsetY), 0)

    def end(self):
        buffer = pyglet.image.get_buffer_manager().get_color_buffer()
        self.texture.blit_into(buffer, 0, 0, 0)
        glViewport(0, 0, self.window.width, self.window.height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.window.width, 0, self.window.height, -3000, 3000)
        glMatrixMode(GL_MODELVIEW)
        glClearColor(0, 0, 0, 0)
        self.window.clear()
        glLoadIdentity()
        glColor3f(1, 1, 1)
        (self.texture.blit)(*self._viewport)


def setViewportTranslate(camera):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, camera.width, 0, camera.height, 0, 3000)
    glMatrixMode(GL_MODELVIEW)
    glScalef(camera.zoom, camera.zoom, 0)
    glTranslatef(-camera.offsetX, -camera.offsetY, 0)


def setViewport(camera):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, camera.width, 0, camera.height, -3000, 3000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


target_width, target_height = gameSettings.getWorldResolution()
worldViewPort = FixedResolutionViewport((sceneManager.window), (camera.worldCamera),
  target_width,
  target_height,
  filtered=False)
lightLayer.initLight(sceneManager.window.width, sceneManager.window.height)

class Projection(object):
    __doc__ = "Abstract OpenGL projection."

    def set(self, window_width, window_height, viewport_width, viewport_height):
        """Set the OpenGL projection

        Using the passed in Window and viewport sizes,
        set a desired orthographic or perspective projection.

        :Parameters:
            `window_width` : int
                The Window width
            `window_height` : int
                The Window height
            `viewport_width` : int
                The Window internal viewport width.
            `viewport_height` : int
                The Window internal viewport height.
        """
        raise NotImplementedError("abstract")


class Projection3D(Projection):
    __doc__ = "A 3D perspective projection"

    def __init__(self, fov=60, znear=0.1, zfar=255):
        """Create a 3D projection

        :Parameters:
            `fov` : float
                The field of vision. Defaults to 60.
            `znear` : float
                The near clipping plane. Defaults to 0.1.
            `zfar` : float
                The far clipping plane. Defaults to 255.
        """
        self.fov = fov
        self.znear = znear
        self.zfar = zfar

    def set(self, window_width, window_height, viewport_width, viewport_height):
        gl.glViewport(0, 0, max(1, viewport_width), max(1, viewport_height))
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        aspect_ratio = float(window_width) / float(window_height)
        f_width = math.tan(self.fov / 360.0 * math.pi) * self.znear
        f_height = f_width * aspect_ratio
        gl.glFrustum(-f_height, f_height, -f_width, f_width, self.znear, self.zfar)
        gl.glMatrixMode(gl.GL_MODELVIEW)


class WorldRender:

    def render(self):
        worldViewPort.begin()
        worldLayer.render()
        worldViewPort.end()
        weatherRender.render()
        setViewportTranslate(camera.worldCamera)
        backgroundRender.render()
        setViewportTranslate(camera.worldCamera)
        lightLayer.draw()
        setViewport(camera.simpleCamera)
        backgroundLayer.frontBatch.draw()


class BackgroundRender:

    def render(self):
        setViewport(camera.simpleCamera)
        backgroundLayer.batch.draw()


worldRender = WorldRender()
backgroundRender = BackgroundRender()
