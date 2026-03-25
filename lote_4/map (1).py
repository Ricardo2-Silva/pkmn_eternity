# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\data\world\map.py
"""
Created on 21 juil. 2011

@author: Kami
"""
import pyglet
from client.data.world.object import WorldObjectData
from client.data.layer import LayerType
from client.data.world.animation import AnimType, AnimDirection, Animation
import sys
from shared.container.constants import RefPointType
from client.data.sprite import getAnchorPositionCustom
from client.control.maths.matrix import Matrix
from pyglet.gl.gl import GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA

class Chunk:
    __slots__ = [
     "loaded", "items"]

    def __init__(self):
        self.loaded = False
        self.items = []


class MapChunkData:

    def __init__(self):
        self.objects = Matrix(default=[])
        self.tilesets = Matrix(default=[])
        self.autotiles = Matrix(default=[])
        self.effects = Matrix(default=[])
        self.grounds = Matrix(default=[])
        self.walls = Matrix(default=[])
        self.lights = Matrix(default=[])
        self.sounds = Matrix(default=[])
        self.loaded = {}


CHUNK_SIZE = 128

class MapRenderData:

    def __init__(self):
        self.layers = {(LayerType.LAYERED_FIXED): (pyglet.graphics.OrderedGroup(LayerType.LAYERED_FIXED)), 
         (LayerType.LIGHT): None}
        self.batch = pyglet.graphics.Batch()
        self.aboveBatch = pyglet.graphics.Batch()

    def createLayers(self, layerCount):
        for layerNum in layerCount:
            self.layers[layerNum] = pyglet.graphics.OrderedGroup(layerNum)


class GameMap:
    __doc__ = " Data containing a single map from rendering to world position."

    def __init__(self, map_information):
        self.data = {}
        self.chunks = MapChunkData()
        self.information = map_information
        self.coordinates = (0, 0)
        self.size = [0, 0]
        self.world_position = [0, 0]
        self.offset = (0, 0)
        self.areas = []
        self.wallCache = Matrix(default=None)
        self.basicWalls = Matrix(default=[])
        self.specialWalls = Matrix(default=[])
        self.grounds = Matrix(default=[])
        self.effects = []
        self.tiles = []
        self.objects = []
        self.lights = []
        self.sound = []
        self.animated = []
        self.render = MapRenderData()

    def load(self, json_data):
        """ Loads map with the data given."""
        self.data = json_data
        self.size = self.data["map_size"]
        self.render.createLayers(self.data["layers"])

    def set_rect(self):
        self.left = self.world_position[0]
        self.bottom = self.world_position[1]
        self.top = self.bottom + self.height
        self.right = self.left + self.width
        self._start_chunk_x = self.left // CHUNK_SIZE
        self._start_chunk_y = self.bottom // CHUNK_SIZE

    @property
    def width(self):
        return self.size[0]

    @property
    def height(self):
        return self.size[1]

    @property
    def name(self):
        """ Map filename """
        return self.information.name

    @property
    def displayName(self):
        """ Default map area name """
        return self.areas[0].name

    def get_world_chunk(self, world_chunk_x, world_chunk_y):
        """ Take the world chunk and convert it to the chunk for this map. """
        local_x = world_chunk_x - self._start_chunk_x
        local_y = world_chunk_y - self._start_chunk_y

    def get_world_coordinate(self, pos):
        """ Converts a map coordinate into a world coordinate """
        return (
         self.world_position[0] + self.offset[0] + pos[0], self.world_position[1] + self.offset[1] + pos[1])


class AutotileMode:
    NORMAL = 0
    BIG = 1


class LightData(WorldObjectData):

    def __init__(self, fileId, position, rgb, size, mode):
        (WorldObjectData.__init__)(self, fileId, *position)
        self.rgb = rgb
        self.size = size
        self.mode = mode


class EffectData(WorldObjectData):

    def __init__(self, fileId, position=(0, 0), animation=None, layerType=LayerType.LAYERED, refPointType=RefPointType.CENTER, hidden=False, attach=None, shadow=False, flip_x=False, flip_y=False, program=None, blend_src=GL_SRC_ALPHA, blend_dest=GL_ONE_MINUS_SRC_ALPHA, renderingOrder=1, metafile=False):
        (WorldObjectData.__init__)(self, fileId, *position)
        self.renderingOrder = renderingOrder
        self.layerType = layerType
        self.animation = animation
        self.hidden = hidden
        self.attach = attach
        self.shadow = shadow
        self.flip_x = flip_x
        self.flip_y = flip_y
        self.program = program
        self.blend_src = blend_src
        self.blend_dest = blend_dest
        self.refPointType = refPointType
        self.metafile = metafile
        self.permanent = False

    def copy(self):
        return EffectData(self.fileId, self.getPosition(), self.animation, self.layerType, self.refPointType, self.hidden, self.attach, self.shadow, self.flip_x, self.flip_y, self.program, self.blend_src, self.blend_dest, self.renderingOrder, self.metafile)


class WarpData(EffectData):
    graphics = {
     0: '"warp_[6]"', 
     1: '"warp_up_[2]"', 
     2: '"warp_down_[2]"', 
     3: '"warp_left_[2]"', 
     4: '"warp_right_[2]"'}

    def __init__(self, graphicId, position=(0, 0), size=(0, 0)):
        anchor_x, anchor_y = getAnchorPositionCustom(size[0], size[1], RefPointType.CENTER)
        x, y = position
        EffectData.__init__(self, (self.graphics[graphicId]),
          (
         x + anchor_x, y + anchor_y),
          animation=Animation(delay=0.5, duration=0),
          layerType=(LayerType.LAYERED),
          renderingOrder=(y + size[1] if graphicId == 0 else y))
        self.size = size


class EmoteData(WorldObjectData):

    def __init__(self, fileId, position, animation=None, attach=None, renderingOrder=-1):
        (WorldObjectData.__init__)(self, fileId, *position)
        self.renderingOrder = renderingOrder
        self.layerType = LayerType.LAYERED
        self.animType = AnimType.ONCE
        self.animation = animation
        self.hidden = False
        self.animDirection = AnimDirection.FORWARD
        self.animationDelay = 0
        self.clamp = None
        self.attach = attach
        self.permanent = False


class MapObjectData(WorldObjectData):

    def __init__(self, gameMap, fileId, position, haveShadow, renderingOrder, flipX=False, flipY=False):
        (WorldObjectData.__init__)(self, fileId, *position)
        self.layerType = LayerType.LAYERED_FIXED
        self.renderingOrder = renderingOrder
        self.haveShadow = haveShadow
        self.gameMap = gameMap
        self.flipX = flipX
        self.flipY = flipY
