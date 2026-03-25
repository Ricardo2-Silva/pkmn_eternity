# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\interface\daycare.py
from datetime import datetime
import time
from client.control.events import eventManager
from client.control.gui import Window, Datatable, Button, IconButton, Picture, Label, Header
from client.control.net.sending import packetManager
from client.control.service.session import sessionService
from client.control.utils.localization import localeInt
from client.data.DB import pokemonDB
from client.data.container.char import charContainer
from client.data.gui import styleDB
from client.data.gui.icon import IconData
from client.data.settings import gameSettings
from client.data.utils.anchor import AnchorType, Alignment
from client.game import desktop
from client.interface.notification import ConfirmationWindow
from client.render.cache import textureCache
from shared.container.constants import IdRange, RefPointType
from shared.container.net import cmsg
from shared.controller.net.packetStruct import RawUnpacker
EGG = 3
CHANGE = 2
CREATE = 1
DELETE = 0

class DaycareConfirm(ConfirmationWindow):

    def __init__(self):
        self.runFunc = None
        self.runArgs = []
        Window.__init__(self, desktop, size=(self.confirmSize), position=(gameSettings.getWindowCenter(250, 170)), draggable=True, visible=False, autosize=(False,
                                                                                                                                                            True))
        self.messageLabel = Label(self, size=(240, 0), position=(AnchorType.TOPCENTER), autosize=(False,
                                                                                                  True), alignment=(Alignment.CENTER), multiline=True)
        self.buttonTable = Datatable(self, position=(AnchorType.TOPCENTER), maxRows=1, maxCols=2)
        self.buttonTable.setInternalMargins(25, 0)
        self.confirmButton = Button((self.buttonTable), text="Ok", size=(75, 0), autosize=(False,
                                                                                           True))
        self.confirmButton.addCallbackEnd("onMouseLeftClick", self.runFunction)
        self.buttonTable.add(self.confirmButton)
        self.cancelButton = Button((self.buttonTable), text="Cancel", size=(75, 0), autosize=(False,
                                                                                              True))
        self.cancelButton.addCallbackEnd("onMouseLeftClick", self.hideWindow)
        self.buttonTable.add(self.cancelButton)
        self.buttonTable.fitToContent()
        self.fitToContent()


confirmWindow = DaycareConfirm()

class DaycareContainer(IconButton):

    def __init__(self, parent, icon=None, iconAnchor=AnchorType.CENTER, text="", style=styleDB.blueButtonStyle, position=(0, 0), size=(42, 37), draggable=False, visible=True, autosize=(False, False), enableEvents=True, clickSound=None, overSound=None):
        self.pokemonData = None
        self.requestData = None
        super().__init__(parent, icon, iconAnchor, text, style, position, size, draggable, visible, autosize, enableEvents, clickSound, overSound)

    def clearRequest(self):
        if self.requestData:
            self.setIconDefault(None)
            self.requestData = None

    def addRequestPokemon(self, pokemonData):
        if pokemonData.isReleased():
            eventManager.notify("onBattleMessage", "Please recall your Pokemon before adding it to the daycare.", log=False)
            return
        for widget in self.parent.getWidgets():
            if widget.requestData == pokemonData or widget.pokemonData == pokemonData:
                return

        if not self.pokemonData:
            self.requestData = pokemonData
            self.setIconDefault(textureCache.getPokemonIcon(pokemonData.dexId))

    def addPokemon(self, pokemonId):
        data = charContainer.getDataById(pokemonId, IdRange.PC_POKEMON)
        self.setIconDefault(textureCache.getPokemonIcon(data.dexId))
        self.requestData = None
        self.pokemonData = data


class Daycare:

    def __init__(self):
        self.xpPerMinute = 20
        self.costPerMinute = 1
        self.slotCount = 2
        self.daycareId = 0
        self.eggId = 0
        eventManager.registerListener(self)
        self.window = Window(desktop, position=(AnchorType.CENTER), size=(250, 235), visible=False)
        Header((self.window), "Daycare", close=True)
        self.welcomeLabel = Label((self.window), text="Welcome to our humble Daycare, would you like us to take care of some Pokemon for you?", size=(245,
                                                                                                                                                      0), position=(AnchorType.TOPCENTER), multiline=True, alignment=(Alignment.CENTER))
        self.expLabel = Label((self.window), position=(AnchorType.TOPCENTER), text=f"Cost Per Minute: ${self.costPerMinute}")
        self.costLabel = Label((self.window), position=(AnchorType.TOPCENTER), text=f"Experience Per Minute: {self.xpPerMinute}")
        self.datatable = Datatable((self.window), position=(AnchorType.TOPCENTER), maxRows=1)
        self.datatable.setInternalMargins(25, 0)
        for i in range(self.slotCount):
            dropper = DaycareContainer((self.datatable), text="")
            dropper.addCallback("onMouseLeftClick", self.removePokemon)
            self.datatable.add(dropper)

        self.datatable.fitToContent()
        noEggImg = textureCache.getGuiImage("daycare/no_egg")
        noEggImg.anchor_x = 0
        noEggImg.anchor_y = 0
        eggImg = textureCache.getGuiImage("daycare/Egg01")
        defaultEggImg = eggImg.get_region(0, 0, eggImg.width, eggImg.height)
        defaultEggImg.anchor_x = 0
        defaultEggImg.anchor_y = 0
        self.defaultEggIcon = IconData(defaultEggImg)
        self.mysteryEggIcon = IconData(noEggImg)
        self.eggButton = IconButton((self.window), icon=(self.mysteryEggIcon), size=(34,
                                                                                     42), position=(AnchorType.TOPCENTER), style=(styleDB.simpleButtonStyle))
        self.eggButton.addCallback("onMouseLeftClick", self.checkEgg)
        self.eggButton.addCallback("onMouseOver", self.showTooltip)
        self.eggButton.addCallback("onMouseLeave", self.hideTooltip)
        self.testButton = Button((self.window), position=(AnchorType.TOPCENTER), text="Care For My Pokemon")
        self.testButton.addCallback("onMouseLeftClick", self._addPokemon)
        self.window.fitToContent()

    def showTooltip(self, widget, x, y):
        if self.eggButton.icon == self.mysteryEggIcon:
            eventManager.notify("onShowTooltip", "Your Pokemon have been together for quite a while, sometimes they may produce an egg if we check!", x, y)
        elif self.eggButton.icon == self.defaultEggIcon:
            eventManager.notify("onShowTooltip", "Oh my, that's a beautiful egg! To properly take care of this, you will need an incubator. Once you have one, take it with you!", x, y)

    def hideTooltip(self, widget):
        eventManager.notify("onCloseTooltip")

    def setMysteryEgg(self):
        if not self.eggButton.eventsEnabled:
            self.eggButton.enableEvents()
        if self.eggButton.icon is not self.mysteryEggIcon:
            self.eggButton.setIconDefault(self.mysteryEggIcon)

    def setNoEgg(self):
        if self.eggButton.eventsEnabled:
            self.eggButton.disableEvents()
        if self.eggButton.icon is not None:
            self.eggButton.setIconDefault(None)

    def checkEgg(self, widget: IconButton, x, y, modifiers):
        eventManager.notify("onCloseTooltip")
        if self.eggId == 0:
            packetManager.queueSend(cmsg.DaycareUpdate, EGG, 0, 0)
        elif sessionService.incubators.isIncubatorAvailable():
            packetManager.queueSend(cmsg.DaycareUpdate, EGG, 1, 0)
        else:
            eventManager.notify("onSystemMessage", "You need an unoccupied incubator to carry an egg.")

    def onIncubatedEggReceive(self, incubator, eggData):
        if eggData.id == self.eggId:
            self.setNoEgg()

    def createDaycareButtons(self):
        self.datatable.emptyAndDestroy()
        for i in range(self.slotCount):
            dropper = DaycareContainer((self.datatable), text="")
            dropper.addCallback("onMouseLeftClick", self.removePokemon)
            dropper.addCallback("onMouseRightClick", self.previewPokemon)
            self.datatable.add(dropper)

    def previewPokemon(self, widget, x, y, modifiers):
        if widget.pokemonData:
            eventManager.notify("onPokemonShow", widget.pokemonData)
        elif widget.requestData:
            eventManager.notify("onPokemonShow", widget.requestData)

    def setDaycare(self):
        self.expLabel.text = f"Cost Per Minute: ${self.costPerMinute}"
        self.costLabel.text = f"Experience Per Minute: {self.xpPerMinute}"

    def removePokemon(self, widget, x, y, modifiers):
        if widget.requestData:
            widget.clearRequest()
            return
        if widget.pokemonData:
            slotData = sessionService.daycare.getPokemon(widget.pokemonData.id)
            if slotData:
                start = datetime.fromtimestamp(slotData.addedTime)
                end = datetime.fromtimestamp(time.time())
                delta = end - start
                totalSeconds = time.time() - slotData.addedTime
                seconds = delta.seconds
                hours = seconds // 3600
                minutes = seconds // 60 % 60
                totalMinutes = totalSeconds // 60
                display = "Let's see... we've been taking care of your Pokemon for "
                if delta.days:
                    display += f'{delta.days} day{"s" if delta.days != 1 else ""} '
                if hours:
                    display += f'{hours} hour{"s" if hours != 1 else ""} '
                if minutes:
                    display += f'{minutes} minute{"s" if minutes != 1 else ""}'
                if not hours and not minutes:
                    if not delta.days:
                        display = f"You just left {pokemonDB.name(slotData.dexId).title()} here, would you like to take it back? No charge."
                    else:
                        display += f".\nMy how time flies! Your fee for taking care of {pokemonDB.name(slotData.dexId).title()} comes to... ${localeInt(self.costPerMinute * totalMinutes)}.\nAre you ready to pick them up?"
                    if sessionService.daycare.eggPossible():
                        display += "\n\nWARNING: Be sure to check if an egg is available before removing."

                    def removePokemon():
                        if widget.pokemonData:
                            packetManager.queueSend(cmsg.DaycareUpdate, DELETE, widget.pokemonData.id, 0)

                    confirmWindow.verify(display, removePokemon, yes=True)
                    confirmWindow.fitToContent()

    def requestAddition(self):
        for widget in self.datatable.getWidgets():
            if widget.requestData and not widget.pokemonData:
                packetManager.queueSend(cmsg.DaycareUpdate, CREATE, widget.requestData.id, 0)

    def _addPokemon(self, widget, x, y, modifiers):
        changes = False
        for widget in self.datatable.getWidgets():
            if widget.requestData:
                pokemonIds = [pokemon.pokemonId for pokemon in sessionService.daycare.slots]
                if widget.requestData.id not in pokemonIds:
                    changes = True
                if widget.requestData.isReleased():
                    eventManager.notify("onBattleMessage", "Please recall your Pokemon before adding it to the daycare.",
                      log=False)
                    return

        if changes:
            confirmWindow.verify("Pokemon can be a handful to take care of, so our time is not free. We will require payment for our services when you come to pick them up.\nAre you sure you really want us to take care of your Pokemon?", self.requestAddition)

    def onDaycareUpdate(self, daycareId, status, pokemonId, addedTime, endTime, accruingDebt):
        if status == EGG:
            if pokemonId == 0:
                self.setNoEgg()
            else:
                self.eggId = pokemonId
                self.eggButton.setIconDefault(self.defaultEggIcon)
        elif status == CHANGE:
            egg = sessionService.daycare.getPokemon(pokemonId)
            egg.eggTime = addedTime

    def onDaycareOpen(self, daycareId, slotCount, cost, xp):
        self.slotCount = slotCount
        self.costPerMinute = cost
        self.xpPerMinute = xp
        self.daycareId = daycareId
        if not self.window.visible:
            self.window.show()
            self.setDaycare()

    def onDaycareInformation(self, data):
        self.createDaycareButtons()
        up = RawUnpacker(data)
        _, count, eggId = up.get("!BBI")
        sessionService.daycare.clear()
        self.eggId = eggId
        for idx in range(count):
            pokemonId, dexId, addedTime, eggTime = up.get("IHdd")
            pokemonData = charContainer.getDataByIdIfAny(pokemonId, IdRange.PC_POKEMON)
            sessionService.daycare.addPokemon(pokemonId, dexId, addedTime, eggTime, pokemonData)
            widget = self.datatable.get(0, idx)
            print("WIDGET?", widget)
            widget.addPokemon(pokemonId)
            eventManager.notify("onPokemonDelete", pokemonId)
            print(pokemonId, dexId, addedTime)

        if eggId == 0:
            if sessionService.daycare.eggPossible():
                self.setMysteryEgg()
            else:
                self.setNoEgg()
        else:
            self.eggButton.setIconDefault(self.defaultEggIcon)
        self.datatable.fitToContent()


daycare = Daycare()
