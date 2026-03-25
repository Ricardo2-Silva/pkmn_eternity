# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\world\rain.py
"""
Created on Nov 12, 2015

@author: Admin
"""
import pyglet
from pyglet.gl import *
import math
from random import randint
from client.data.world.map import EffectData
from client.control.world.map import Effect
from client.control.camera import worldCamera
from client.data.world.animation import AnimType, Animation
from client.data.layer import LayerType
from twisted.internet import reactor
from shared.container.euclid import Line2, Point2
DROP_LENGTH = 40

class Point(object):
    __slots__ = ('x', 'y')

    def __init__(self, x, y):
        self.x = x
        self.y = y


class Line(object):
    __slots__ = ('p1', 'p2')

    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2


class RainDrop:

    def __init__(self, x, controller, batch):
        self.id = x
        self.controller = controller
        self.batch = batch
        self.createLine()
        data = EffectData("drop_[4]", position=(300, 300),
          animation=Animation(delay=0.1, removal="hide"),
          layerType=(LayerType.LAYERED),
          hidden=True,
          renderingOrder=0)
        data.permanent = True
        self.dropEffect = Effect(data)

    @property
    def vertices(self):
        return (self.line.p1.x, self.line.p1.y, self.line.p2.x, self.line.p2.y)

    def updateLine(self):
        self.vertex_list.vertices = (
         self.line.p1.x, self.line.p1.y, self.line.p2.x, self.line.p2.y)

    def createLine(self):
        self.createVertices()
        self.vertex_list = self.batch.add(2, pyglet.gl.GL_LINES, None, (
         "v2f", self.vertices), ('c4f', (1, 1, 1, 0.5, 1, 1, 1, 0.5)))

    def createVertices(self):
        angle = math.radians(self.controller.angle)
        point1 = Point(randint(-self.controller.width, self.controller.width + 50), randint(self.controller.height, self.controller.height + 10))
        point2 = Point(point1.x + math.cos(angle) * DROP_LENGTH, point1.y + math.sin(angle) * DROP_LENGTH)
        self.line = Line(point1, point2)
        if self.controller.angle < 270:
            if point2.x > 0:
                self.deathPoint = Point(randint(-DROP_LENGTH - 1, int(point2.x)), randint(-DROP_LENGTH - 1, int(point2.y)))
        if self.controller.angle > 270 and point2.x < self.controller.width:
            self.deathPoint = Point(randint(int(point2.x), self.controller.width + DROP_LENGTH + 1), randint(DROP_LENGTH - 1, int(point2.y)))
        elif self.controller.angle == 270:
            self.deathPoint = Point(int(point2.x), randint(DROP_LENGTH - 1, int(point2.y)))
        else:
            self.deathPoint = Point(int(point2.x), int(point2.y))


class Rain(object):

    def __init__(self, controller):
        self.controller = controller
        self.rainDrops = {}
        self.batch = pyglet.graphics.Batch()

    def start(self):
        if not self.rainDrops:
            for x in range(0, self.controller.intensity):
                self.rainDrops[x] = RainDrop(x, self.controller, self.batch)

    def stop(self):
        for drop in self.rainDrops.values():
            if drop.dropEffect.visible:
                drop.dropEffect.hide()

    def render(self):
        glDisable(GL_TEXTURE_2D)
        glLineWidth(1.0)
        glEnable(GL_LINE_SMOOTH)
        self.batch.draw()
        glEnable(GL_TEXTURE_2D)

    def update(self, dt):
        an = math.radians(self.controller.angle)
        for drop in self.rainDrops.values():
            point1 = drop.line.p1
            point2 = drop.line.p2
            pointMax = drop.deathPoint
            if point1.x >= pointMax.x and point1.y <= pointMax.y or point1.y < 0:
                point1.x = randint(0, self.controller.width + 50)
                point1.y = randint(self.controller.height + 10, self.controller.height + 20)
                point2.x = point1.x + math.cos(an) * DROP_LENGTH
                point2.y = point1.y + math.sin(an) * DROP_LENGTH
                if self.controller.angle < 270 and point2.x > 0:
                    pointMax.x = randint(-DROP_LENGTH - 1, int(point2.x))
                    pointMax.y = randint(DROP_LENGTH + 1, int(point2.y))
            if self.controller.angle > 270:
                if point2.x < self.controller.width:
                    pointMax.x = randint(int(point2.x), self.controller.width + DROP_LENGTH + 1)
                    pointMax.y = randint(DROP_LENGTH - 1, int(point2.y))
                if self.controller.angle == 270:
                    pointMax.x = point2.x
                    pointMax.y = (DROP_LENGTH - 1, int(point2.y))
                else:
                    if point2.x >= pointMax.x:
                        if point2.y <= pointMax.y:
                            if not drop.dropEffect.visible:
                                (drop.dropEffect.setPosition)(*worldCamera.toMapPosition(point2.x - 3, point2.y - 2))
                                drop.dropEffect.show()
                            point1.x += self.controller.speed * math.cos(an)
                            point1.y += self.controller.speed * math.sin(an)
                        else:
                            point1.x += self.controller.speed * math.cos(an)
                            point1.y += self.controller.speed * math.sin(an)
                            point2.x += self.controller.speed * math.cos(an)
                            point2.y += self.controller.speed * math.sin(an)
                    drop.updateLine()
