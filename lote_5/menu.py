# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\interface\pokemon\menu.py
"""
Created on Aug 21, 2011

@author: Ragnarok
"""
from client.control.gui import Button, Menu
from client.data.gui import styleDB
from client.control.events.event import eventManager
from client.data.settings import gameSettings
from shared.container.constants import IdRange, WalkMode, CharCategory
from client.control.service.session import sessionService
from shared.container.net import cmsg
from client.control.net.sending import packetManager
import pyglet.window.mouse
from client.game import desktop
from client.scene.manager import sceneManager
UI_SCALE = gameSettings.getUIScale()

class PokemonMenu:

    def __init__(self):
        self.menu = Menu(desktop)
        self.summaryBtn = Button((self.menu), style=(styleDB.menuItemStyle), size=(70,
                                                                                   20), text="Summary", autosize=(False,
                                                                                                                  False))
        self.summaryBtn.addCallback("onMouseLeftClick", self.showSummary)
        self.followBtn = Button((self.menu), style=(styleDB.menuItemStyle), size=(70,
                                                                                  20), text="Make Follow", autosize=(False,
                                                                                                                     False))
        self.followBtn.addCallback("onMouseLeftClick", self.makeFollow)
        self.freeBtn = Button((self.menu), style=(styleDB.menuItemStyle), size=(70,
                                                                                20), text="Stop Follow", autosize=(False,
                                                                                                                   False))
        self.freeBtn.addCallback("onMouseLeftClick", self.stopFollow)
        self.recallBtn = Button((self.menu), style=(styleDB.menuItemStyle), size=(70,
                                                                                  20), text="Recall", autosize=(False,
                                                                                                                False))
        self.recallBtn.addCallback("onMouseLeftClick", self.recallPokemon)
        self.scanBtn = Button((self.menu), style=(styleDB.menuItemStyle), size=(70,
                                                                                20), text="Scan", autosize=(False,
                                                                                                            False))
        self.scanBtn.addCallback("onMouseLeftClick", self.scanPokemon)
        self.unequipBtn = Button((self.menu), style=(styleDB.menuItemStyle), size=(70,
                                                                                   20), text="Unequip Item", autosize=(False,
                                                                                                                       False))
        self.unequipBtn.addCallback("onMouseLeftClick", self.unequipItem)
        self.cancelBtn = Button((self.menu), style=(styleDB.menuItemStyle), size=(70,
                                                                                  20), text="Cancel", autosize=(False,
                                                                                                                False))
        self.char = None
        self.charData = None
        eventManager.registerListener(self)

    def reset(self):
        self.char = None
        self.charData = None
        self.menu.forceHide()

    def makeFollow(self, widget, x, y, modifiers):
        if self.char.data.skillStates.inUse():
            eventManager.notify("onBattleMessage", "You cannot make a Pokemon follow during a move!", log=False)
            return
        self.char.data.unselectedMode = WalkMode.FOLLOW
        self.char.startFollowing(sessionService.trainer)
        packetManager.queueSend(cmsg.MakeFollow, self.charData.id, self.charData.idRange, sessionService.trainer.getId(), sessionService.trainer.getIdRange())

    def stopFollow(self, widget, x, y, modifiers):
        self.char.data.unselectedMode = WalkMode.FREE
        packetManager.queueSend(cmsg.StopFollow, self.charData.id, self.charData.idRange)

    def unequipItem(self, widget, x, y, modifiers):
        packetManager.queueSend(cmsg.ItemUnequip, self.charData.id)

    def recallPokemon(self, widget, x, y, modifiers):
        eventManager.notify("onRecallAttempt", self.charData)

    def scanPokemon(self, widget, x, y, modifiers):
        packetManager.queueSend(cmsg.PokedexScan, self.charData.id, self.charData.idRange)

    def showSummary(self, widget, x, y, modifiers):
        eventManager.notify("onPokemonShow", self.charData)

    def openMenuFromPokemon(self, char, x, y):
        self.char = char
        self.charData = char.data
        self.openMenu(char.data, x, y, None)

    def openMenu(self, charData, x, y, modifiers):
        if not charData.canOpenMenu():
            return
        if charData.getIdRange() == IdRange.PC_POKEMON:
            self.populatePC(charData, x, y)
        elif charData.getIdRange() == IdRange.NPC_CHARACTER:
            self.populateNpc(charData, x, y)
        elif charData.getIdRange() == IdRange.NPC_WILD_PKMN:
            self.populateWild(charData, x, y)

    def openMenuFromParty(self, widget, x, y, modifiers):
        if widget.pkmnData:
            self.charData = widget.pkmnData
            self.openMenu(widget.pkmnData, int(x / UI_SCALE), int(y / UI_SCALE), modifiers)

    def onCharMouseClick(self, x, y, button, char):
        if button == pyglet.window.mouse.RIGHT:
            if char.data.idRange in IdRange.POKEMON:
                x, y = sceneManager.convert(x, y)
                self.openMenuFromPokemon(char, int(x / UI_SCALE), int(y / UI_SCALE))
            elif self.menu.visible:
                self.menu.hide()

    def populatePC(self, charData, x, y):
        self.menu.hideAllOptions()
        self.menu.fitToContent()
        if sessionService.canPokedexScan(charData.dexId):
            self.menu.add(self.scanBtn)
        else:
            if sessionService.isClientPokemonData(charData):
                self.menu.add(self.summaryBtn)
                if charData.isReleased():
                    if sessionService.selected.data is not charData:
                        if not charData.isFainted():
                            if charData.walkMode == WalkMode.FREE:
                                self.menu.add(self.followBtn)
                        else:
                            self.menu.add(self.freeBtn)
                    self.menu.add(self.recallBtn)
        if not charData.isFainted():
            if charData.heldNameId > 0:
                self.menu.add(self.unequipBtn)
        self.menu.add(self.cancelBtn)
        if not self.menu.visible:
            self.menu.show()
        self.menu.setActive()
        self.menu.setPosition(x, y)
        self.menu.fitToContent()

    def populateNpc(self, charData, x, y):
        self.menu.hideAllOptions()
        if charData.category == CharCategory.POKEMON:
            if sessionService.canPokedexScan(charData.dexId):
                self.menu.add(self.scanBtn)
        self.menu.add(self.cancelBtn)
        if not self.menu.visible:
            self.menu.show()
        self.menu.setActive()
        self.menu.setPosition(x, y)
        self.menu.fitToContent()

    def populateWild(self, charData, x, y):
        self.menu.hideAllOptions()
        if sessionService.canPokedexScan(charData.dexId):
            self.menu.add(self.scanBtn)
        self.menu.add(self.cancelBtn)
        if not self.menu.visible:
            self.menu.show()
        self.menu.setActive()
        self.menu.setPosition(x, y)
        self.menu.fitToContent()


pokemonMenu = PokemonMenu()
