# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\scene\world.py
"""
Created on Oct 21, 2016

@author: Admin
"""
from client.control.system.sound import mixerController
from client.control.world.warp import warpController
from client.interface.pokemon.info import infoBar
from client.render.render import worldRender, setViewport, backgroundRender
from client.control.events.event import eventManager
from client.render.system.loop import FixedTimeStepLoop
from client.scene.manager import Scene
from client.control.camera import worldCamera, guiCamera
from client.game import desktop
from client.control.world.action.walking import walkerPositionManager, areaChange
from client.control.world.action.physics import physicsController
from client.render.world.weather import weatherRender
from client.control.world.action.buffs import buffTimeHandler
import rabbyt
from client.interface.hotbar import hotbar
from client.control.world.action.idle import idleCharManager
from client.control.world.action.status import statusTimeHandler
from client.render.shader.default_sprite import ripple_shader
from client.control.world.action.battle import battleController

class WorldScene(Scene):

    def __init__(self):
        eventManager.registerListener(self)
        mixerController.stopMusic()
        from client.control.events.world import worldInputManager
        from client.control.system.target import targetting
        from client.control.service.hotkey import HotkeyManager
        hotkeyManager = HotkeyManager(desktop)
        self.handlers = (
         worldInputManager, desktop, worldInputManager.keys, hotkeyManager, worldCamera, targetting)
        import client.control.world.action.recall, client.control.world.action.release, client.control.system.selection, client.control.world.action.physics, client.control.world.load, client.control.world.char, client.control.world.warp, client.control.world.action.capture, client.control.world.action.skill_client, client.control.world.action.battle, client.control.world.action.damage, client.control.world.effects
        from client.interface.cycle import timeWindow
        import client.interface.tooltip as tooltip, client.interface.inputMenu as inputMenu, client.interface.hotbar as hotbar, client.interface.bag as bag, client.interface.social as social, client.interface.chat.chat as chat, client.interface.battle as battle, client.interface.group as group, client.interface.trainer as trainer, client.interface.trade as trade, client.interface.guild as guild, client.interface.cycle as cycle
        from client.interface.daycare import daycare
        from client.interface.npc import storage, shop, quest, dialog
        from client.interface.pokemon import party, details, menu, new, pokedex, info, choose
        from client.interface import help
        import client.interface.system as system
        from client.render.shader.service import shaderService
        self.shaderService = shaderService
        self.chat = chat.chat
        self.pokemon = party.pokemonParty
        self.hotbar = hotbar.hotbar
        self.main = system.mainMenu
        self.timeWindow = timeWindow
        self.fixed_time_step = FixedTimeStepLoop(self.fixed_update, self.fixed_draw, 0.02, 0.04)

    def on_enter(self):
        Scene.on_enter(self)
        self.fixed_time_step.start()

    def on_exit(self):
        Scene.on_exit(self)
        self.fixed_time_step.stop()

    def onShowDefaultGUI(self):
        self.chat.window.show()
        self.pokemon.window.show()
        self.hotbar.window.show()
        self.main.window.show()
        self.timeWindow.show()
        desktop.fitToContent()

    def fixed_update(self, dt):
        walkerPositionManager.update(dt)
        physicsController.update(dt)
        worldCamera.update(dt)

    def fixed_draw(self, interp):
        walkerPositionManager.draw(interp)
        physicsController.draw(interp)
        worldCamera.draw(interp)

    def update(self, dt):
        self.shaderService.update(dt)
        idleCharManager.update(dt)
        areaChange.update(dt)
        warpController.update(dt)
        hotbar.update(dt)
        statusTimeHandler.update(dt)
        desktop.update(dt)
        weatherRender.update(dt)
        buffTimeHandler.update(dt)
        infoBar.window.buffTimeKeeper.update(dt)
        battleController.update(dt)

    def draw(self):
        worldRender.render()
        setViewport(guiCamera)
        desktop.render()
