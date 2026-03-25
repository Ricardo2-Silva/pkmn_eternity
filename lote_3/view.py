# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\service\view.py
"""
Created on 23 juil. 2011

@author: Kami
"""
from client.control.camera import worldCamera
from client.data.settings import gameSettings
from shared.container.constants import MapSettings
import rabbyt

class ViewService:

    def __init__(self):
        self.maxHorScreenTile = int(gameSettings.getWindowResolution()[0] / MapSettings.SQUARE)
        self.maxVertScreenTile = int(gameSettings.getWindowResolution()[1] / MapSettings.SQUARE)

    def getChunksInView(self):
        return worldCamera.getChunks()

    def isMapPositionInView(self, x, y):
        """ return yes if this position is in the view """
        return bool(rabbyt.collisions.aabb_collide_single(rabbyt.Quad((x, y, x, y)), worldCamera))

    def toMapPositition(self, x, y):
        """ return the map position from a mouse position """
        return worldCamera.toMapPosition(x, y)

    def collideView(self, objects):
        """ Return the objects in square view from the objects list. """
        return rabbyt.collisions.aabb_collide_single(rabbyt.Quad(worldCamera.getSquareBounds()), objects)

    def collideViewNoZoom(self, objects):
        """ Return the objects in square view from the objects list. """
        return rabbyt.collisions.aabb_collide_single(rabbyt.Quad(worldCamera.getSquareBounds()), objects)

    def isInView(self, sprite):
        return bool(rabbyt.collisions.aabb_collide_single(rabbyt.Quad(worldCamera.getSquareBounds()), [sprite]))

    def isInNonZoomedView(self, sprite):
        return bool(rabbyt.collisions.aabb_collide_single(worldCamera.cullSquare, [sprite]))

    def isInNonZoomedViewList(self, spriteList):
        return bool(rabbyt.collisions.aabb_collide_single(worldCamera.cullSquare, spriteList))


viewService = ViewService()
