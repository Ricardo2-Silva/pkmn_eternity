# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\scene\creation.py
"""
Created on Oct 21, 2016

@author: Admin
"""
import client.interface.creation_new
from client.game import desktop
from client.render.render import backgroundRender
from client.scene.manager import Scene

class CreationScene(Scene):

    def __init__(self):
        Scene.__init__(self)
        self.handlers = (
         desktop,)
        self.creation = client.interface.creation_new.CharacterCreation()

    def on_enter(self):
        Scene.on_enter(self)
        if self.creation.window.visible is False:
            self.creation.window.show()
        self.creation.on_enter()

    def on_exit(self):
        Scene.on_exit(self)
        if self.creation.window.visible is True:
            self.creation.window.hide()
        self.creation.on_exit()

    def update(self, dt):
        client.game.desktop.update(dt)
        self.creation.update(dt)

    def draw(self):
        desktop.render()
        self.creation.draw()
