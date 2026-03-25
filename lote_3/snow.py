# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\world\snow.py
"""
Created on Dec 17, 2015

@author: Admin
"""
import pyglet
from pyglet.gl import *
from twisted.internet import reactor
from random import random, randint
import math, time

class SnowFlake:

    def __init__(self, x, y, radius, d, batch):
        self.x = x
        self.y = y
        self.r = radius
        self.d = d
        self.batch = batch
        self.timing = time.time()
        self.lifetime = 1 + 6 * random()
        self.createCircle(x, y, radius, batch)

    def updateCircle(self):
        circle, indices = self.create_indexed_vertices(self.x, self.y, self.r)
        self.vertex_list.vertices[:] = circle

    def createCircle(self, x, y, radius, batch, sides=24):
        circle, indices = self.create_indexed_vertices(x, y, radius)
        vertex_count = len(circle) // 2
        self.vertex_list = batch.add_indexed(vertex_count, pyglet.gl.GL_TRIANGLES, None, indices, (
         "v2f", circle), (
         "c4f", (1, 1, 1, 0.8) * vertex_count))

    def create_vertices(self, x, y, radius, sides=24):
        verts = []
        for i in range(sides):
            angle = math.radians(float(i) / sides * 360.0)
            x1 = radius * math.cos(angle) + x
            y1 = radius * math.sin(angle) + y
            verts += [x1, y1]

        return ("v2f", verts)

    def create_indexed_vertices(self, x, y, radius, sides=5):
        vertices = [
         x, y]
        for side in range(sides):
            angle = side * 2.0 * math.pi / sides
            vertices.append(x + math.cos(angle) * radius)
            vertices.append(y + math.sin(angle) * radius)

        vertices.append(x + math.cos(0) * radius)
        vertices.append(y + math.sin(0) * radius)
        indices = []
        for side in range(1, sides + 1):
            indices.append(0)
            indices.append(side)
            indices.append(side + 1)

        return (
         vertices, indices)


class Snow(object):

    def __init__(self, controller):
        self.controller = controller
        self.angle = 0
        self.density = 60
        self.batch = pyglet.graphics.Batch()
        self.flakes = []
        for _ in range(1, self.density):
            self.flakes.append(SnowFlake(random() * self.controller.width, random() * self.controller.height, random() * 4 + 1, random() * self.density, self.batch))

    def start(self):
        return

    def stop(self):
        return

    def render(self):
        glDisable(GL_TEXTURE_2D)
        self.batch.draw()
        glEnable(GL_TEXTURE_2D)

    def makeCircle(self, x, y, radius, sides=20):
        verts = []
        for i in range(sides):
            angle = math.radians(float(i) * 2 * math.pi / sides)
            cos = radius * math.cos(angle) + x
            sin = radius * math.sin(angle) + y
            verts += [cos, sin]

        return ("v2f", verts)

    def update(self, dt):
        """ Updates the position of the snow flakes """
        self.angle += 0.001
        for flake in self.flakes:
            flake.y -= math.cos(self.angle + flake.d) + 1 + flake.r / 2
            flake.x += math.sin(self.angle)
            if flake.x > self.controller.width + 5 or flake.x < -5 or flake.y < 0:
                if self.flakes.index(flake) % 3 > 0:
                    flake.x = random() * self.controller.width
                    flake.y = self.controller.height + 30
                elif math.sin(self.angle) > 0:
                    flake.x = -20
                    flake.y = random() * self.controller.height
                else:
                    flake.x = self.controller.width + 20
                    flake.y = random() * self.controller.height
                if time.time() - flake.timing > flake.lifetime:
                    if math.sin(self.angle) > 0:
                        flake.x = -20
                        flake.y = random() * self.controller.height
                    else:
                        flake.x = self.controller.width + 20
                        flake.y = random() * self.controller.height
                    flake.timing = time.time()
                    flake.lifetime = 1 + 6 * random()
                flake.updateCircle()
