# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\interface\pokemon\choose.py
"""
Created on Oct 22, 2015

@author: Admin
"""
from client.control.gui import Datatable, Window, Button, IconButton, Label
from client.game import desktop
from client.data.utils.anchor import AnchorType
from client.data.gui import styleDB
from client.render.cache import textureCache
from client.data.DB import pokemonDB
from client.control.net.sending import packetManager
from shared.container.net import cmsg
from client.control.events.event import eventManager
from client.data.sprite import Sheet
from client.control.gui.picture import AnimatedPicture, Picture
from twisted.internet import reactor
from shared.container.constants import RefPointType
import pyglet
from client.control.gui.windows import Header
from client.control.system.sound import mixerController

class PokemonPicker:

    def __init__(self):
        self.window = PickerWindow()
        eventManager.registerListener(self)

    def reset(self):
        self.window.reset()

    def addPokemon(self, dexId):
        self.window.addPokemon(dexId)

    def onPokemonChoiceSelection(self, dexList):
        self.window.resetChoices()
        for dexId in dexList:
            if dexId > 0:
                self.addPokemon(dexId)

        self.window.fitToContent()
        self.window.hidePokemon()
        if not self.window.visible:
            self.window.show()


class PickerWindow(Window):

    def __init__(self):
        Window.__init__(self, desktop, position=(AnchorType.CENTER), size=(320, 160), draggable=True, autosize=(True,
                                                                                                                True), style=(styleDB.windowsDefaultStyle), visible=False)
        header = Header(self, "Choose A Pokemon!", close=True)
        header.close.addCallback("onMouseLeftClick", self.closeAndDestroy)
        self.animating = False
        self.lastBall = None
        self.dexId = 0
        self.pokeballSheet = Sheet((textureCache.getGuiImage("common/pokeball")), (5,
                                                                                   1), 0.1, referencePoint=(RefPointType.BOTTOMLEFT))
        self.pokeballSheet.setGUIReferencePoint()
        self.labelChoose = Label(self, position=(AnchorType.TOPCENTER), text="Which Pokemon do you like the most? You may only pick one.", style=(styleDB.blackLabelStyle))
        self.currentPokemonLbl = Label(self, position=(AnchorType.TOPCENTER), text="Pokemon", style=(styleDB.titleLabelStyle), visible=False)
        self.dataTable = Datatable(self, position=(AnchorType.TOPCENTER), maxRows=1)
        self.dataTable.setInternalMargins(80, 1)
        self.pokemonPictures = []
        self.chooseButton = Button(self, position=(AnchorType.BOTTOMCENTER), size=(140,
                                                                                   0), autosize=(False,
                                                                                                 True), text="Choose Selected Pokemon")
        self.chooseButton.addCallback("onMouseLeftClick", self.chosePokemon)
        self.fitToContent()

    def reset(self):
        self.resetChoices()

    def closeAndDestroy(self, widget, x, y, modifiers):
        self.resetChoices()

    def showPokemon(self, widget, x, y, modifiers, ballImage, pokemonImage):
        if self.animating == False:
            if ballImage.open == False:
                if self.lastBall:
                    if self.lastBall[0].open == True:
                        (self.closeBall)(*self.lastBall)
                self.animating = True
                ballImage.runAnimation(0.5, stopOnFrame=4)
                cb = ballImage.renderer.fadeTo(0.5, 150)
                cb.addCallback(self.setAnimating)
                pokemonImage.show()
                pokemonImage.renderer.setAlpha(0)
                d = pokemonImage.renderer.fadeTo(0.5, 255)

                def revertTransparency(calback):
                    pokemonImage.renderer._endTransparency()

                d.addCallback(revertTransparency)
                ballImage.open = True
                mixerController.playCry(ballImage.dexId)
                self.selectPokemon(ballImage.dexId)
                self.lastBall = (ballImage, pokemonImage)
            else:
                self.closeBall(ballImage, pokemonImage)

    def closeBall(self, ballImage, pokemonImage):
        ballImage.open = False
        ballImage.renderer.setFrame(0)
        ballImage.setAlpha(255)
        pokemonImage.hide()
        self.animating = False
        self.dexId = 0

    def setAnimating(self, _):
        self.animating = not self.animating

    def chosePokemon(self, widget, x, y, modifiers):
        if self.dexId != 0:
            packetManager.queueSend(cmsg.PokemonSelection, self.dexId)
            self.resetChoices()

    def hidePokemon(self):
        for widget in self.pokemonPictures:
            widget.hide()

    def resetChoices(self):
        self.lastBall = None
        self.dexId = 0
        for widget in self.dataTable.getWidgets():
            widget.hide()

        self.dataTable.emptyAndDestroy()
        for widget in self.pokemonPictures:
            widget.destroy()

        self.pokemonPictures.clear()
        self.forceHide()
        self.animating = False

    def addPokemon(self, dexId):
        pokeballImage = AnimatedPicture((self.dataTable), picture=(self.pokeballSheet), enableEvents=True, refPointType=(RefPointType.TOPLEFT))
        pokeballImage.dexId = dexId
        pokeballImage.open = False
        self.dataTable.add(pokeballImage)
        self.dataTable.fitToContent()
        self.fitToContent()
        x, y = pokeballImage.getRelativePosition()
        x1, y1 = self.dataTable.getRelativePosition()
        w, h = pokeballImage.width / 2 - pokeballImage.width / 2, pokeballImage.height / 2 - pokeballImage.height / 2
        pokemonImage = Picture(self, (textureCache.getPokemonFront(dexId, 0)), position=(x + w, y + y1 + h), visible=True, refPointType=(RefPointType.TOPLEFT))
        self.pokemonPictures.append(pokemonImage)
        pokeballImage.addCallback("onMouseLeftClick", self.showPokemon, pokeballImage, pokemonImage)

    def selectPokemon(self, dexId):
        self.dexId = dexId
        self.chooseButton.text = "Choose {0}!".format(pokemonDB.getPokemon(dexId).name.title())


choicePokemonPick = PokemonPicker()
