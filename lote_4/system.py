# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\interface\system.py
"""
Created on Aug 3, 2011

@author: Ragnarok
"""
from client.data.utils.anchor import AnchorType
from client.data.gui import styleDB
from client.control.gui import Window, IconButton
from client.game import desktop
from client.render.cache import textureCache
from client.control.events.event import eventManager
from client.interface.social import friendsList
from client.interface.bag import bag
from client.interface.pokemon.pokedex import pokedex
from client.interface.pokemon.party import pokemonParty
from client.interface.guild import guild
from client.interface.npc.quest import quest
from client.interface.map.worldmap import worldMap
from client.interface.trainer import trainerCard
from client.control.system.anims import FadeColor, ParallelAnims

class MainWindow(Window):

    def __init__(self):
        Window.__init__(self, desktop, position=(AnchorType.TOPLEFT), draggable=True, style=(styleDB.windowsNoStylePadded), autosize=(True,
                                                                                                                                      True), visible=False)
        self.partyNormalImg = textureCache.getGuiImage("icons/pokeballn")
        self.partyOverImg = textureCache.getGuiImage("icons/pokeballc")
        self.pokedexNormalImg = textureCache.getGuiImage("icons/pokedexn")
        self.pokedexOverImg = textureCache.getGuiImage("icons/pokedexc")
        self.bagNormalImg = textureCache.getGuiImage("icons/bagn")
        self.bagOverImg = textureCache.getGuiImage("icons/bagc")
        self.questNormalImg = textureCache.getGuiImage("icons/optionn")
        self.questOverImg = textureCache.getGuiImage("icons/optionc")
        self.cardNormalImg = textureCache.getGuiImage("icons/card")
        self.cardOverImg = textureCache.getGuiImage("icons/icons_45")
        self.mapNormalImg = textureCache.getGuiImage("icons/icons_74")
        self.mapOverImg = textureCache.getGuiImage("icons/icons_75")
        self.socialNormalImg = textureCache.getGuiImage("icons/friend_disabled")
        self.socialOverImg = textureCache.getGuiImage("icons/friend")
        self.guildNormalImg = textureCache.getGuiImage("icons/friend2_disabled")
        self.guildOverImg = textureCache.getGuiImage("icons/friend2")
        self.pokemonBtn = IconButton(self, position=(AnchorType.LEFTTOP), icon=(self.partyNormalImg), style=(styleDB.transparentButtonStyle), clickSound="MenuSelect")
        self.pokemonBtn.setIconOver(self.partyOverImg)
        self.pokemonBtn.addCallback("onMouseLeftClick", pokemonParty.window.toggleEvent)
        self.pokedexBtn = IconButton(self, position=(AnchorType.LEFTTOP), icon=(self.pokedexNormalImg), style=(styleDB.transparentButtonStyle), clickSound="MenuSelect")
        self.pokedexBtn.setIconOver(self.pokedexOverImg)
        self.pokedexBtn.addCallback("onMouseLeftClick", pokedex.window.toggleEvent)
        self.bagBtn = IconButton(self, position=(AnchorType.LEFTTOP), icon=(self.bagNormalImg), style=(styleDB.transparentButtonStyle), clickSound="MenuSelect")
        self.bagBtn.setIconOver(self.bagOverImg)
        self.bagBtn.addCallback("onMouseLeftClick", bag.window.toggleEvent)
        self.cardBtn = IconButton(self, position=(AnchorType.LEFTTOP), icon=(self.cardNormalImg), style=(styleDB.transparentButtonStyle), clickSound="MenuSelect")
        self.cardBtn.setIconOver(self.cardOverImg)
        self.cardBtn.addCallback("onMouseLeftClick", trainerCard.window.toggleEvent)
        self.mapBtn = IconButton(self, position=(AnchorType.LEFTTOP), icon=(self.mapNormalImg), style=(styleDB.transparentButtonStyle), clickSound="MenuSelect")
        self.mapBtn.setIconOver(self.mapOverImg)
        self.mapBtn.addCallback("onMouseLeftClick", worldMap.window.toggleEvent)
        self.questBtn = IconButton(self, position=(AnchorType.LEFTTOP), icon=(self.questNormalImg), style=(styleDB.transparentButtonStyle), clickSound="MenuSelect")
        self.questBtn.setIconOver(self.questOverImg)
        self.questBtn.addCallback("onMouseLeftClick", self.openQuests)
        self.socialBtn = IconButton(self, position=(AnchorType.LEFTTOP), icon=(self.socialNormalImg), style=(styleDB.transparentButtonStyle), clickSound="MenuSelect")
        self.socialBtn.setIconOver(self.socialOverImg)
        self.socialBtn.addCallback("onMouseLeftClick", friendsList.window.toggleEvent)
        self.guildBtn = IconButton(self, position=(AnchorType.LEFTTOP), icon=(self.guildNormalImg), style=(styleDB.transparentButtonStyle), clickSound="MenuSelect")
        self.guildBtn.setIconOver(self.guildOverImg)
        self.guildBtn.addCallback("onMouseLeftClick", guild.window.toggleEvent)
        self.guildBtn.disableEvents()
        self.setAutoFit()

    def setNotification(self, button):
        """ This will set an icon to pulse a color, typically on a notification """
        anim = ParallelAnims(*[FadeColor(sprite, (200, 0, 0), 1) + FadeColor(sprite, (255,
                                                                                      255,
                                                                                      255), 1, startColor=(200,
                                                                                                           0,
                                                                                                           0)) for sprite in button.renderer.sprites])
        anim *= 0
        button.renderer.startAnim(anim)

    def clearNotification(self, button):
        button.renderer.stopAnims()
        button.setColor(255, 255, 255)

    def openQuests(self, widget, x, y, modifiers):
        self.clearNotification(self.questBtn)
        quest.window.toggleEvent(widget, x, y, modifiers)

    def enableGuild(self):
        self.guildBtn.enableEvents()

    def disableGuild(self):
        self.guildBtn.disableEvents()

    def quitt(self, button):
        eventManager.notify("onWidgetShow", "Quit")


class MainMenu:

    def __init__(self):
        eventManager.registerListener(self)
        self.window = MainWindow()

    def reset(self):
        if self.window.guildBtn.isEventsEnabled():
            self.window.disableGuild()
        if self.window.visible:
            self.window.hide()

    def onHotkeyPress(self, hotkeyName):
        if hotkeyName == "questjournal":
            self.window.clearNotification(self.window.questBtn)

    def onQuestAccept(self, questId):
        self.window.setNotification(self.window.questBtn)

    def onQuestJournalComplete(self):
        self.window.setNotification(self.window.questBtn)

    def onClientLeftGuild(self):
        self.window.disableGuild()

    def onGuildList(self, data):
        self.window.enableGuild()


mainMenu = MainMenu()
