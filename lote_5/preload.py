# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\scene\preload.py
"""
Created on Jun 29, 2017

@author: Admin
"""
from client.scene.manager import Scene
import pyglet

class PreLoadScene(Scene):

    def __init__(self, manager):
        Scene.__init__(self)
        self.loading = pyglet.text.Label(text="Loading Assets", font_size=25, font_name="Segoe UI", bold=True, x=(manager.width // 2), y=(manager.height // 2), anchor_x="center", anchor_y="center")

    def draw(self):
        self.loading.draw()

    def on_exit(self):
        self.loading.delete()
