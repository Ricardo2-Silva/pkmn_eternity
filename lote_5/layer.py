# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\render\layer.py
"""
Created on 6 juil. 2011

@author: Kami
"""
import rabbyt
from client.data.layer import LayerType, LayerMode
from client.control.service.view import viewService
from client.control.events.event import eventManager
from client.control.gui.implem import worldGUIContainer
import pyglet, sys, traceback
from client.render.sprite import PygletBackgroundSprite
from pyglet.gl import *
from _ctypes import byref

class SimpleLayer:
    __doc__ = " Contains sprites that will be rendered. "

    def __init__(self):
        self.sprites = []

    def add(self, *sprites):
        self.sprites.extend(sprites)

    def delete(self, *sprites):
        for sprite in sprites:
            self.sprites.remove(sprite)

    def getSprites(self):
        return self.sprites

    def setOnTop(self, *sprites):
        (self.delete)(*sprites)
        (self.add)(*sprites)

    def render(self):
        rabbyt.render_unsorted(self.sprites)

    def replace(self, sprites):
        self.sprites = sprites


class BackgroundLayer:

    def __init__(self):
        self.batch = pyglet.graphics.Batch()
        self.frontBatch = pyglet.graphics.Batch()


class WorldLayer(object):

    def __init__(self):
        self.gameMaps = []
        self.batches = {(LayerType.LIGHT): (lightLayer.batch)}
        self.groups = {(LayerType.LIGHT): None}
        self._createDynamicBatches()
        self.layers = {(LayerType.LAYERED_FIXED): self, 
         (LayerType.LAYERED): self, 
         (LayerType.LIGHT): lightLayer}
        eventManager.registerListener(self)

    def _createFixedBatches(self):
        """ These batches are essentially the entire map and does not change; will be cached """
        self.groundBatch = pyglet.graphics.Batch()
        self.aboveBatch = pyglet.graphics.Batch()
        self.batches = {(LayerType.LAYERED_FIXED): (self.groundBatch), 
         (LayerType.LIGHT): (lightLayer.batch)}
        self.groups = {(LayerType.LAYERED_FIXED): (pyglet.graphics.OrderedGroup(LayerType.LAYERED_FIXED)), 
         (LayerType.LIGHT): None}

    def _createDynamicBatches(self):
        """ These items are dynamic and may be removed constantly """
        self.dynamicBatch = pyglet.graphics.Batch()
        self.shadowBatch = pyglet.graphics.Batch()
        self.transparentBatch = pyglet.graphics.Batch()
        self.batches[LayerType.LAYERED] = self.dynamicBatch
        self.groups[LayerType.LAYERED] = None

    def combine_layers(self):
        """ This is used to combine the fixed and moving layer into one, this way we can sort sprites accordingly.
            Note that this method is the fastest sorting possible for our implementation."""
        return

    def add(self, layerType, *sprites):
        (self.layers[layerType].add)(*sprites)

    def delete(self, layerType, *sprites):
        (self.layers[layerType].delete)(*sprites)

    def render(self):
        for gameMap in self.gameMaps:
            gameMap.render.batch.draw()

        self.dynamicBatch.draw()
        self.shadowBatch.draw()
        glDepthMask(GL_FALSE)
        self.transparentBatch.draw()
        glDepthMask(GL_TRUE)
        for gameMap in self.gameMaps:
            gameMap.render.aboveBatch.draw()

        worldGUIContainer.draw()

    def getLayer(self, layerType):
        return self.layers[layerType]

    def getShadowLayer(self, layerType):
        return (
         self.groups[layerType], self.shadowBatch)

    def getLayerRender(self, layerType, transparent=False):
        if transparent is True:
            batch = self.transparentBatch
        else:
            batch = self.batches[layerType]
        return (self.groups[layerType], batch)

    def getAllLayerRenders(self, layerType):
        return (
         self.groups[layerType], self.batches[layerType], self.transparentBatch)

    def onViewChange(self, bounds):
        return

    def onLogout(self):
        self._createDynamicBatches()

    def onBlockRendering(self):
        print("Info: Creating new batches.")
        self._createDynamicBatches()


class LightLayer(object):

    def __init__(self):
        self.batch = pyglet.graphics.Batch()
        self.bufferId = GLuint(0)
        glGenFramebuffersEXT(1, byref(self.bufferId))

    def initLight(self, width, height):
        """ We blit the lights into one texture to prevent oversaturation before drawing """
        self.lights = pyglet.image.Texture.create(width, height, internalformat=(pyglet.gl.GL_RGBA))
        self.sprite = PygletBackgroundSprite(self.lights)

    def draw(self):
        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, self.bufferId)
        glFramebufferTexture2DEXT(GL_FRAMEBUFFER_EXT, GL_COLOR_ATTACHMENT0_EXT, self.lights.target, self.lights.id, self.lights.level)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.batch.draw()
        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, 0)
        glViewport(0, 0, self.lights.width, self.lights.height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.lights.width, 0, self.lights.height, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glBlendFunc(GL_DST_COLOR, GL_DST_ALPHA)
        self.lights.blit(0, 0)


class WeatherLayer(SimpleLayer):

    def __init__(self):
        super().__init__()
        self.renderer = None

    def render(self):
        self.renderer.render()


lightLayer = LightLayer()
worldLayer = WorldLayer()
weatherLayer = WeatherLayer()
backgroundLayer = BackgroundLayer()
