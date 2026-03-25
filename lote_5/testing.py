# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\scene\testing.py
"""
Created on Oct 21, 2016

@author: Admin
"""
import math, time
from client.control import camera
from client.control.camera import worldCamera, guiCamera
from client.control.events.event import eventManager, eventDispatcher
from client.control.gui.textbox import Textbox
from client.control.service.session import sessionService
from client.control.system.background import backgroundController
from client.control.world.action.battle import battleController
from client.control.world.action.physics import physicsController
from client.control.world.action.skill_receive import skillController
from client.control.world.action.walking import walkerPositionManager, areaChange, walkingCharsController
from client.control.world.char import PCTrainer, NPCTrainer
from client.control.world.item import Item, Ball
from client.control.world.map import Effect, ShaderEffect
from client.data.DB import skillDB, mapDB, itemDB
from client.data.container.char import charContainer, charLoader
from client.data.container.map import mapContainer
from client.data.container.world import World
from client.data.sprite import Sheet
from client.data.world.char import PcTrainerData, NpcTrainerData
from client.data.world.item import WorldItemData, BallData
from client.data.world.map import EffectData
from client.game import desktop
from client.interface.map.loading import loadingScreen
from client.render.cache import textureCache
from client.render.render import worldRender, setViewport, setViewportTranslate, backgroundRender
from client.render.shader.default_sprite import white_sprite_shader, ripple_shader, pulse_shader, bubble_shader, shield_shader, lightray_shader
from client.render.sprite import TimerTextureSprite, ElapsedTimerSpriteGroup
from client.render.world.weather import weatherRender
from client.scene.manager import Scene, sceneManager
from pyglet.gl import *
from shared.container.constants import TargetType, CharCategory, StatusEffect, StatType, RefPointType, CreatureAction, Emotes
from shared.service.direction import directionService
from shared.service.geometry import getAngleBetweenTwoPoints
from twisted.internet import reactor, defer, threads
from client.control.gui.windows import Window
from client.data.utils.anchor import AnchorType
from client.control.system.sound import mixerController
import traceback

def canSwim():
    return True


sessionService.canSwim = canSwim
skill_test = "absorb"

class TestScene(Scene):

    def __init__(self):
        self._elapsed = 0
        eventManager.registerListener(self)
        sceneManager.window.push_handlers(self)
        from client.control.events.world import worldInputManager
        from client.game import desktop
        from client.control.system.target import targetting
        self.handlers = (
         worldInputManager.keys, worldInputManager, desktop, worldCamera, targetting)
        import client.control.world.action.recall, client.control.world.action.release, client.control.system.selection, client.control.world.action.physics, client.control.world.load, client.control.world.char, client.control.world.warp, client.control.world.action.capture, client.control.world.action.skill_client, client.control.world.action.battle, client.control.world.action.damage, client.control.world.effects
        from client.interface.cycle import timeWindow
        timeWindow.show()
        from client.interface.timing import timerDisplay
        import client.interface.cycle as cycle
        from client.render.shader.service import shaderService
        self.shaderService = shaderService
        from client.interface.npc import storage, shop, quest, dialog
        from client.interface.pokemon import details, menu, new, party, pokedex, info, choose
        import client.interface.system as system
        self.textInput = Textbox(desktop, text=skill_test, size=(100, 20), scrollable=True)
        self.verify(self.textInput)
        self.textInput.addCallback("onLostFocus", self.verify)
        self._range = 1
        self.batch = pyglet.graphics.Batch()
        self.setupGame2()

    def on_enter(self):
        for handler in self.handlers:
            sceneManager.window.push_handlers(handler)

        pyglet.clock.schedule_interval(self.update, 0.016666666666666666)

    def verify(self, widget):
        try:
            self.skillIdTest = skillDB.getByName(widget.text.upper())
        except Exception:
            widget.text = "invalid"

    def setupGame(self):
        from client.data.world.char import PokemonData
        from client.control.world.char import Pokemon

    def setupGame2(self):
        eventManager.notify("onBeforeMapLoad")
        mapInfo = mapDB.getById(99)
        from client.data.world.char import PokemonData
        from client.control.world.char import Pokemon
        from client.control.world.char import NewPCTrainer, PCTrainer
        d = PokemonData()
        d.id = 100
        d.dexId = 88
        d.walkMode = 2
        d.walkingSpeed = 100
        d.stats.hp.set(100, 100)
        d.name = "Test Pokemon"
        d.setPosition(750, 900)
        d.map = mapInfo
        eventManager.notify("onMapLoad", mapInfo, d.getPosition())
        img = pyglet.image.SolidColorImagePattern((255, 255, 0, 255)).create_image(100, 100)
        img.anchor_x = img.width // 2
        img.anchor_y = img.height // 2
        b = BallData(267, 267, (760, 880))
        b.id = 4
        b.map = mapInfo
        b.name = "Pokeball"
        b.setPosition(760, 880)
        ball = Ball(b)
        charContainer.addChar(ball)
        self.clientChar = Pokemon(d)
        d = PokemonData()
        d.dexId = 3
        d.map = mapInfo
        d.setPosition(700, 900)
        d.stats.hp.set(100, 100)
        self.targetChar = Pokemon(d)
        self.targetChar.showStatusEffect(StatusEffect.CONFUSED, 20)
        self.targetChar.emote(Emotes.ANGRY_MARK)
        charContainer.addChar(self.targetChar)
        m = NpcTrainerData()
        m.fileId = "am01"
        m.map = mapInfo
        m.setPosition(900, 900)
        self.mmm = NPCTrainer(m)
        charContainer.addChar(self.clientChar)
        charContainer.addClientChar(self.clientChar)
        sessionService.setClientTrainer(self.clientChar)
        walkerPositionManager.onClientTrainerLoaded()
        eventDispatcher.dispatch_event("onCharSelection", self.clientChar)
        self.duration = 0.1
        eventManager.notify("onAfterMapLoad")
        loadingScreen.hide()

    def on_mouse_release(self, x, y, button, modifiers):
        x, y = worldCamera.toMapPosition(x, y)
        data = None
        if self.skillIdTest.target & TargetType.COORDINATES:
            data = (
             x, y)
        elif self.skillIdTest.target & TargetType.DIRECTION:
            data = int(getAngleBetweenTwoPoints(self.clientChar.getProjection2D(), (x, y)))
        elif self.skillIdTest.target & TargetType.CHAR:
            data = (
             self.targetChar.getId(), self.targetChar.getIdRange())
        elif self.skillIdTest.target & TargetType.AREA:
            data = (
             x, y)
        else:
            if self.skillIdTest.target & TargetType.SELF:
                data = (
                 self.clientChar.getId(), self.clientChar.getIdRange())
        if button == pyglet.window.mouse.LEFT:
            if self.clientChar.data.category == CharCategory.POKEMON:
                skillController.useSkill(self.skillIdTest, 0, self.clientChar, self.duration, time.time(), data)
                self.clientChar.data.stats.energy.set(100, 100)
        return pyglet.event.EVENT_HANDLED

    def update(self, dt):
        self.shaderService.update(dt)
        walkerPositionManager.update(dt)
        physicsController.update(dt)
        battleController.update(dt)
        desktop.update(dt)
        weatherRender.update(dt)
        self._elapsed += dt

    def draw(self):
        worldRender.render()
        setViewportTranslate(camera.worldCamera)
        self.batch.draw()
        setViewport(guiCamera)
        desktop.render()


class CircleSprite(object):

    def __init__(self, x, y, z, radius, batch, verts=128):
        self._x = x
        self._y = y
        self.z = z
        self.batch = batch
        self._radius = radius
        self.verts = verts
        self._create_vertex_list()

    def update(self, x, y):
        self._x = x
        self._y = y
        self._update_vertex_list()

    def _update_vertex_list(self):
        verts = []
        for i in range(self.verts):
            cosine = self._radius * math.cos(i * 2 * math.pi / self.verts) + self._x
            sine = self._radius / 2 * math.sin(i * 2 * math.pi / self.verts) + self._y
            verts += [cosine, sine, self.z]

        self._vertex_list.vertices[:] = verts

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        self._radius = value
        self._update_vertex_list()

    def _create_vertex_list(self):
        verts = []
        for i in range(self.verts):
            cosine = self._radius * math.cos(i * 2 * math.pi / self.verts) + self._x
            sine = self._radius / 2 * math.sin(i * 2 * math.pi / self.verts) + self._y
            verts += [cosine, sine, self.z]

        self._vertex_list = self.batch.add(self.verts, pyglet.gl.GL_LINE_LOOP, None, (
         "v3f", verts), (
         "c4f", (1, 1, 1, 1) * self.verts))
