# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\scene\gui.py
"""
Created on Oct 21, 2016

@author: Admin
"""
from client.control.system.background import backgroundController
from client.render.render import worldRender, setViewport
from client.render.world.weather import weatherRender
from client.control.events.event import eventManager, eventDispatcher
from client.scene.manager import Scene, sceneManager
import random
from twisted.internet import reactor, defer, threads
import ujson, json
from client.control.gui.textbox import Textbox
import rabbyt
from pyglet.gl import *
from client.control import camera
from client.control.gui.label import Label
from client.game import desktop
import pyglet
from client.data.container.char import charContainer
from client.control.service.session import sessionService
from shared.service.geometry import getAngleBetweenTwoPoints
from shared.container.constants import TargetType, CharCategory, PMSettings
from client.render.render import worldRender
from client.control.events.event import eventManager, eventDispatcher
from client.scene.manager import Scene, sceneManager
import random
from twisted.internet import reactor, defer, threads
import threading
from twisted.internet.task import coiterate
import ujson, json, pyglet
from client.control.world.action.skill_receive import skillController
from shared.container.constants import TargetType, RefPointType, CreatureAction, CharCategory
from shared.service.geometry import getAngleBetweenTwoPoints
from client.control.world.load import mapLoader
from client.control.gui.textbox import Textbox
import rabbyt
from client.render.layer import worldLayer
from client.data.layer import LayerType, LayerMode
from client.control.service.session import sessionService
from pyglet.gl import *
from client.data.container.map import mapContainer
from client.control import camera
from client.control.gui.label import Label
from client.game import desktop
import pyglet
from client.render.cache import textureCache, atlasLoader
from client.data.settings import gameSettings
from client.data.sprite import Sheet
from shared.service.direction import directionService
import math, time
from client.control.gui.container import Container, LineRoundedContainer
from client.data.gui import styleDB
from client.data.gui.button import TextboxType
from client.data.utils.anchor import AnchorType, Alignment
from client.control.gui.windows import Window, Tabs
from client.control.gui.button import Button, IconButton
import client.control.camera as camera
from client.data.DB import itemDB
from client.control.gui.picture import Picture, AnimatedPicture
from client.control.gui.scrollbox import ScrollableContainer
from client.data.utils.color import Color
from client.control.gui.bar import Bar
from client.control.gui.lines import Line, LineTable
from client.control.gui.tables import Datatable
from client.control.gui.dropdown import DropDown
from client.data.gui.styleDB import blackLabelStyle

class GuiScene(Scene):

    def __init__(self):
        eventManager.registerListener(self)
        sceneManager.window.push_handlers(self)
        from client.game import desktop
        self.handlers = (
         desktop,)
        self.window2 = Window(desktop, size=(453, 165), position=(825, 555), visible=True)
        self.scontainer2 = ScrollableContainer((self.window2), position=(0, 0), size=(400,
                                                                                      160))
        Label((self.scontainer2.content), position=(AnchorType.TOPLEFT),
          size=(360, 0),
          style=(styleDB.chatStyles["PARTY"]),
          autosize=(False, True),
          multiline=True,
          text="WHASSUP BOI")
        Label((self.scontainer2.content), position=(AnchorType.TOPLEFT),
          size=(360, 0),
          style=(styleDB.chatStyles["PARTY"]),
          autosize=(False, True),
          multiline=True,
          text="WHASSUP BOI")
        Label((self.scontainer2.content), position=(AnchorType.TOPLEFT),
          size=(360, 0),
          style=(styleDB.chatStyles["PARTY"]),
          autosize=(False, True),
          multiline=True,
          text="WHASSUP BOI")
        Label((self.scontainer2.content), position=(AnchorType.TOPLEFT),
          size=(360, 0),
          style=(styleDB.chatStyles["PARTY"]),
          autosize=(False, True),
          multiline=True,
          text="WHASSUP BOI")
        Label((self.scontainer2.content), position=(AnchorType.TOPLEFT),
          size=(360, 0),
          style=(styleDB.chatStyles["PARTY"]),
          autosize=(False, True),
          multiline=True,
          text="WHASSUP BOI")
        Label((self.scontainer2.content), position=(AnchorType.TOPLEFT),
          size=(360, 0),
          style=(styleDB.chatStyles["PARTY"]),
          autosize=(False, True),
          multiline=True,
          text="WHASSUP BOI")
        Label((self.scontainer2.content), position=(AnchorType.TOPLEFT),
          size=(360, 0),
          style=(styleDB.chatStyles["PARTY"]),
          autosize=(False, True),
          multiline=True,
          text="WHASSUP BOI")
        Label((self.scontainer2.content), position=(AnchorType.TOPLEFT),
          size=(360, 0),
          style=(styleDB.chatStyles["PARTY"]),
          autosize=(False, True),
          multiline=True,
          text="WHASSUP BOI")
        self.scontainer2.fitToContent()

    def dummyClick(self, widget, x, y, modifiers):
        print("YOU DUMMY")

    def createGrids(self):
        size = 128
        self.color = (255, 255, 255, 255)
        width, height = (960, 960)
        self.grid = pyglet.graphics.Batch()
        group = pyglet.graphics.Group()
        w = width // size
        h = height // size
        for i in range(0, w + 1):
            self.grid.add(2, pyglet.gl.GL_LINES, group, (
             "v2f", (i * size, 0, i * size, height)), (
             "c4B", self.color * 2))

        for j in range(0, h + 1):
            self.grid.add(2, pyglet.gl.GL_LINES, group, (
             "v2f", (0, j * size, width, j * size)), (
             "c4B", self.color * 2))

    def verify(self, widget):
        try:
            self.skillIdTest = skillDB.getByName(widget.text.upper())
        except Exception:
            widget.text = "invalid"

    def update(self, dt):
        desktop.update(dt)

    def draw(self):
        glClearColor(0, 1, 1, 0)
        desktop.render()
