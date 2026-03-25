# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\scene\patching.py
"""
Created on Dec 15, 2018

@author: Admin
"""
from client.scene.manager import Scene
from client.render.layer import backgroundLayer
from client.game import desktop

class PatchingScene(Scene):

    def __init__(self):
        self.handlers = (
         desktop,)
        from client.interface.patcher import patchControl
        self.patcher = patchControl

    def on_enter(self):
        Scene.on_enter(self)
        self.patcher.on_enter()

    def on_exit(self):
        Scene.on_exit(self)
        self.patcher.on_exit()

    def update(self, dt):
        desktop.update(dt)

    def draw(self):
        backgroundLayer.batch.draw()
        desktop.render()
