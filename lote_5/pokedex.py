# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\interface\pokemon\pokedex.py
"""
Created on Aug 21, 2011

@author: Ragnarok
"""
import math
from client.control.events.event import eventManager
from shared.container.constants import Element, RefPointType
from shared.controller.net.packetStruct import RawUnpacker
from client.control.gui import Label, Picture, ScrollableContainer, Window, IconButton, Datatable, BackgroundContainer, Button, AnimatedPicture
from client.game import desktop
from client.render.cache import textureCache
from client.data.utils.anchor import AnchorType, Alignment
from client.data.gui import styleDB
from client.data.DB import pokemonDB
from client.control.service.session import sessionService
import time
from client.data.cache import pokedexCache
from twisted.internet import reactor
from client.data.sprite import Sheet
from client.data.settings import gameSettings
from client.data.gui.icon import IconData
import zlib

class PokedexWindow(Window):

    def __init__(self, control):
        x, y = gameSettings.getWindowCenter(447, 445)
        Window.__init__(self, desktop, position=(x, 152), size=(447, 445), style=(styleDB.windowsNoStyle), visible=False, autosize=(False,
                                                                                                                                    False))
        self.control = control
        self.currentId = 0
        self.animating = False
        self.pokedexOpen = textureCache.getGuiImage("pokedex/pokedex_open")
        self.pokedexClose = textureCache.getGuiImage("pokedex/pokedex_closed")
        self.pokedexClose.anchor_y = self.pokedexClose.oY
        self.noPicture = textureCache.getGuiImage("pokedex/noPicture")
        self.hiddenImg = textureCache.getGuiImage("pokedex/noIcon")
        self.hiddenIcon = IconData(self.hiddenImg)
        self.infoImg = textureCache.getGuiImage("pokedex/info")
        self.flashSheet = Sheet((textureCache.getGuiImage("pokedex/pokedex_flash")), frames=(4,
                                                                                             1), animationDelay=0.1, referencePoint=(RefPointType.BOTTOMLEFT))
        self.flashSheet.setGUIReferencePoint()
        self.addCallback("onMouseClickOut", self.close)
        self.setBackground(self.pokedexOpen)
        self.screen = BackgroundContainer(self, (self.infoImg), position=(70, 22), size=(306,
                                                                                         169), visible=False)
        self.heightLbl = Label((self.screen), position=(240, 3), size=(37, 15), autosize=(False,
                                                                                          False), style=(styleDB.pokedexLabelStyle))
        self.weightLbl = Label((self.screen), position=(240, 21), size=(32, 15), autosize=(False,
                                                                                           False), style=(styleDB.pokedexLabelStyle))
        self.dexInfo = Label((self.screen), position=(16, 2), style=(styleDB.pokemonWhiteGuiStyle))
        self.dexImg = Picture((self.screen), position=(50, 23))
        self.flashImg = AnimatedPicture(self, picture=(self.flashSheet), position=(0,
                                                                                   233))
        self.flashImg.hide()
        self.element1 = Picture((self.screen), position=(190, 70))
        self.element2 = Picture((self.screen), position=(228, 70))
        self.descriptionLbl = Label((self.screen), position=(15, 105), size=(276, 63), autosize=(False,
                                                                                                 False), style=(styleDB.pokedexDescriptionLabelStyle), multiline=True)
        self.descriptionLbl.autosize = (False, True)
        self.speciesLbl = Label((self.screen), position=(177, 46), style=(styleDB.pokemonWhiteGuiStyle))
        self.footprintPic = Picture((self.screen), position=(184, 15))
        self.scrollBox = ScrollableContainer(self, position=(69, 228), size=(307, 169), visible=False)
        self.closeBtn = Button(self, position=(404, 404), size=(46, 24), text="", style=(styleDB.reduceButtonStyle), visible=True)
        self.closeBtn.addCallback("onMouseLeftClick", (lambda widget, x, y, modifiers: self.close()))
        self.tables = {}
        self.table = Datatable((self.scrollBox.content), maxCols=8)
        height = 7
        for i in range(68):
            self.tables[i] = Datatable((self.scrollBox.content), position=(0, height), maxRows=1, maxCols=7)
            self.tables[i].setManualFit()
            self.tables[i].setInternalMargins(1, 1)
            self.tables[i].setMinHeight(40)
            for x in range(7 * i + 1, 7 * i + 8):
                if x > 493:
                    break
                self.createButton(i, x)

            height += 40
            self.tables[i].setAutoFit()

        self.scrollBox.fitToContent()

    def reset(self):
        self.animating = False
        for tableId in self.tables:
            for widget in self.tables[tableId].getWidgets():
                if widget.icon != self.hiddenIcon:
                    widget.setIconDefault(self.hiddenIcon)

        self.forceHide()

    def open(self):
        if not self.visible:
            if not self.animating:
                self.showLid()
                self.show()
                self.animating = True

                def foo():
                    if self.animating:
                        self.showInside()
                        self.animating = False

                reactor.callLater(0.2, foo)
                from client.interface.help import helpWindow
                helpWindow.showText("pokedex")

    def close(self):
        if self.visible:
            if not self.animating:
                self.showLid()
                self.animating = True

                def foo():
                    if self.animating:
                        self.hide()
                        self.animating = False

                reactor.callLater(0.2, foo)

    def showLid(self):
        if self.screen.visible:
            self.screen.hide()
            self.scrollBox.hide()
        self.setBackground(self.pokedexClose)

    def showInside(self):
        if not self.screen.visible:
            self.screen.show()
            self.scrollBox.show()
        self.setBackground(self.pokedexOpen)

    def scanAnimation(self):
        if not self.flashImg.visible:
            self.flashImg.show()
            self.flashImg.loopAnimation()
            reactor.callLater(2, self.flashImg.hide)

    def scan(self, dexId):
        self.animating = True
        self.showLid()
        if not self.visible:
            self.show()
        self.scanAnimation()

        def foo():
            self.showInside()
            self._selectPokemon(dexId)
            height = 39 * (dexId // 7 - 1)
            self.scrollBox.pushToTop()
            self.scrollBox.pushToDiff(-height)
            self.animating = False

        reactor.callLater(2.2, foo)

    def getButtonById(self, dexId):
        x = (dexId - 1) // 7
        for widget in self.tables[x].getWidgets():
            if widget.dexId == dexId:
                return widget

        return

    def enablePokemon(self, dexId, value=1):
        widget = self.getButtonById(dexId)
        widget.setIconDefault(textureCache.getPokemonIcon(dexId))
        sessionService.pokedex.setPokemon(dexId, value)

    def setPokedex(self):
        height = 0
        self.t = time.time()
        for dexId in sessionService.pokedex.getRevealed():
            button = self.getButtonById(dexId)
            button.setIconDefault(textureCache.getPokemonIcon(dexId))

    def createButton(self, tableId, dexId):
        button = IconButton((self.tables[tableId]), text=(str(dexId).zfill(3)),
          size=(39, 39),
          iconAnchor=(AnchorType.BOTTOM),
          autosize=(False, False),
          style=(styleDB.pokedexButtonStyle),
          icon=(self.hiddenIcon))
        button.dexId = dexId
        button.addCallback("onMouseLeftClick", self.selectPokemonClick)
        self.tables[tableId].add(button)

    def selectPokemonClick(self, widget, x, y, modifiers):
        self._selectPokemon(widget.dexId)

    def _selectPokemon(self, dexId):
        if self.currentId != dexId:
            self.currentId = dexId
            if sessionService.pokedex.getPokemon(dexId):
                self.heightLbl.text = "{:.1f}".format(pokemonDB.height(dexId))
                self.weightLbl.text = "{:.1f}".format(pokemonDB.weight(dexId))
                self.dexInfo.text = f"No. {str(dexId).zfill(3)} {pokemonDB.name(dexId)}"
                self.dexImg.setPicture(textureCache.getPokemonFront(dexId, 1))
                self.descriptionLbl.text = pokemonDB.pokedex(dexId)
                self.speciesLbl.text = f"{pokemonDB.species(dexId)} POKéMON"
                self.footprintPic.setPicture(textureCache.getPokemonFootprint(dexId))
                element = pokemonDB.type(dexId)
                if element[1] is None:
                    self.element1.setPicture(textureCache.getElementIcon(element[0]))
                    self.element2.removePicture()
                else:
                    self.element1.setPicture(textureCache.getElementIcon(element[0]))
                    self.element2.setPicture(textureCache.getElementIcon(element[1]))
            else:
                self.showBlank(dexId)

    def showBlank(self, dexId):
        self.heightLbl.text = "???.?"
        self.weightLbl.text = "???.?"
        self.speciesLbl.text = "????? POKéMON"
        self.dexInfo.text = f"No. {str(dexId).zfill(3)}"
        self.dexImg.setPicture(self.noPicture)
        self.footprintPic.removePicture()
        self.descriptionLbl.text = ""
        self.element1.removePicture()
        self.element2.removePicture()


class Pokedex:

    def __init__(self):
        self.afterBattle = None
        self.window = PokedexWindow(self)
        eventManager.registerListener(self)

    def reset(self):
        self.window.reset()

    def onHotkeyPress(self, hotkeyName):
        if hotkeyName == "pokedex":
            self.window.toggle()

    def onPokedexReceived(self, data):
        packer = RawUnpacker(data)
        _, length = packer.get("!BH")
        data = packer.get(f"{length}s")
        decompressed = list(zlib.decompress(data))
        for value in decompressed:
            sessionService.pokedex.appendPokemon(value)

        pokedexCache.setPokedex(sessionService.pokedex.getPokedex())
        self.window.setPokedex()

    def checksumValidated(self):
        sessionService.pokedex.setPokedex(pokedexCache.getPokedex())
        self.window.setPokedex()

    def onPokedexUpdate(self, dexId, value):
        self.window.enablePokemon(dexId, value)
        if sessionService.battle.isActive():
            self.afterBattle = dexId
        else:
            self.window.scan(dexId)
        pokedexCache.setPokemon(dexId, value)

    def onBattleEnd(self):
        if self.afterBattle:
            self.window.scan(self.afterBattle)
            self.afterBattle = None


pokedex = Pokedex()
