# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\world\action\battle.py
"""
Created on 17 dec. 2011

@author: Kami
"""
from twisted.internet import defer
from client.control.service.session import sessionService
from client.control.events.event import eventManager
from client.control.system.selection import selectionController
from client.control.world.action.idle import idleCharManager
from client.data.settings import gameSettings
from client.data.world.battle import BattleAutoselectFlag
from shared.service.geometry import inElipse
import time
from client.control.world.map import Effect
from client.data.world.map import EffectData
from shared.container.constants import BattleUpdateType
from twisted.python import log

class BattleController:
    defaultArea = 400

    def __init__(self):
        self.startX = 0
        self.startY = 0
        self.radius = 0
        eventManager.registerListener(self)
        self.lastTime = time.time()
        self.battleCircle = None

    def reset(self):
        self.lastTime = time.time()
        if self.battleCircle:
            self.battleCircle.renderer.stopAnims()
            self.battleCircle.delete()
        self.battleCircle = None
        self.setInfo(0, 0, 0)

    def create(self, battleType):
        sessionService.battle.create(battleType)

    def setInfo(self, startX, startY, radius):
        if self.battleCircle:
            log.msg("Receiving battle information when we already have some, minor sync issue. Updating...")
            self.battleCircle.setPosition(startX, startY)
        self.startX = startX
        self.startY = startY
        self.radius = radius

    def spawnCircle(self):
        if self.startX == 0:
            if self.startY == 0:
                log.msg("Warning: Starting battle but did not receive information. Setting estimation.")
                (self.setInfo)(*sessionService.getSelectedChar().getPosition2D(), *(self.defaultArea,))
                return
        self.battleCircle = Effect(EffectData("area2", position=(
         self.startX, self.startY),
          renderingOrder=1))
        self.battleCircle.setColor(255, 0, 255)
        self.battleCircle.setAlpha(15)
        self.battleCircle.pulseAlpha(3, 0, 25)
        self.battleCircle.growSeparate(1, 0.1,
          0.1, (self.radius / self.defaultArea),
          (self.radius / self.defaultArea * 0.75), reset=False)

    def end(self, message):
        if not sessionService.battle.isActive():
            print("Warning: Unexpected battle end received. No battle on client found.")
        else:
            eventManager.notify("onBattleEnd")
            if self.battleCircle:
                self.battleCircle.renderer.stopAnims()
                self.battleCircle.delete()
            self.battleCircle = None
            self.setInfo(0, 0, 0)
            if message == BattleUpdateType.BATTLE_END_AREA:
                eventManager.notify("onBattleMessage", "You strayed too far from the battle area and fled.", log=True)
            if gameSettings.getAutoSelectionControl() & BattleAutoselectFlag.ON_BATTLE_END:
                from client.control.system.selection import selectionController
                selectionController.autoSelectFromBattle(False)

    def start(self, timestamp):
        """ Battle will start on timestamp """
        sessionService.battle.start()
        self.spawnCircle()
        eventManager.notify("onBattleStart", sessionService.battle.battleType)
        if gameSettings.getAutoSelectionControl() & BattleAutoselectFlag.ON_BATTLE_START:
            from client.control.system.selection import selectionController
            selectionController.autoSelectFromBattle(True)

    def addChar(self, char):
        sessionService.battle.addChar(char)
        if char.data.isPokemon():
            idleCharManager.charEnteredBattle(char)

    def delChar(self, char):
        sessionService.battle.delChar(char)
        if char.data.isPokemon():
            if char.isReleased():
                if not char.isFainted():
                    idleCharManager.charExitBattle(char)

    def onPokemonRelease(self, trainer, pokemon, x, y):
        return

    def onCharWarp(self, char, mapId, entering):
        if sessionService.battle.isInBattle(char):
            self.delChar(char)

    def onClientCharWarped(self, char):
        if sessionService.battle.isInBattle(char):
            sessionService.battle.end()

    def onBattleEnd(self):
        sessionService.battle.end()

    def update(self, dt):
        if sessionService.battle.active:
            if not inElipse(self.startX, self.startY, *sessionService.getSelectedChar().getPosition2D(), *(self.radius / 2, self.radius / 2 * 0.75)):
                if time.time() - self.lastTime >= 5:
                    eventManager.notify("onBattleMessage", "Warning: You are leaving the battle area!", log=False)
                    self.lastTime = time.time()


battleController = BattleController()
