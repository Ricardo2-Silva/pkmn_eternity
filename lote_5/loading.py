# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\scene\loading.py
"""
Created on Oct 23, 2016

@author: Admin
"""
from client.render.render import backgroundRender
from client.scene.manager import Scene
from client.game import desktop
from client.interface.map.loading import loadingScreen

class LoadingScene(Scene):

    def __init__(self):
        Scene.__init__(self)
        self.loading = loadingScreen

    def draw(self):
        desktop.render()
        backgroundRender.render()
