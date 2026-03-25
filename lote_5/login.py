# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\scene\login.py
"""
Created on Oct 21, 2016

@author: Admin
"""
from client.scene.manager import Scene
import client.interface.login
from client.render.layer import backgroundLayer

class LoginScene(Scene):

    def __init__(self):
        from client.game import desktop
        self.handlers = (
         desktop,)
        self.login = client.interface.login.Login()

    def update(self, dt):
        self.login.window.update(dt)
        client.game.desktop.update(dt)

    def on_enter(self):
        Scene.on_enter(self)
        self.login.on_enter()

    def on_exit(self):
        Scene.on_exit(self)
        self.login.on_exit()

    def draw(self):
        client.game.desktop.render()
        backgroundLayer.batch.draw()
