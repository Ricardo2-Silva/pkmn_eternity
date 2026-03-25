# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\interface\pokemon\party.py
"""
Created on Aug 21, 2011

@author: Ragnarok
"""
import random
from twisted.internet import reactor
import pyglet.clock
from client.control.gui.label import SpellingLabel
from client.control.system.sound import mixerController
from client.data.sprite import Sheet, CustomSheet
from client.data.world.eggs import EggIncubator, PokemonEgg
from client.interface.npc.dialog import DialogSpellingLabel
from client.render.cache import textureCache
from client.control.events.event import eventManager
from client.control.gui import Window, IconButton, Datatable
from client.game import desktop
from client.data.gui import styleDB
from shared.container.constants import Pokeball, PokemonFlag, RefPointType
from shared.container.net import cmsg
from client.control.service.session import sessionService
from client.data.utils.anchor import AnchorType, Alignment
from client.control.net.sending import packetManager
from client.control.camera import worldCamera
from client.control.gui.bar import Bar
from client.interface.pokemon.menu import pokemonMenu
from client.scene.manager import sceneManager
from client.control.gui.picture import Picture, AnimatedPicture

class IncubatorPartySlot:

    def __init__(self, window, incubator, underlayer, overlayer, egg=None):
        self.window = window
        self.incubator = incubator
        self.underlayer = underlayer
        self.overlayer = overlayer
        self.egg = egg

    def updateAlignments(self):
        x, y = self.window.getIncubatorPlacement(self.incubator)
        self.underlayer.setPosition(x + 1, y + 28)
        if self.egg:
            self.egg.setPosition(x + 3, y + 51)
        self.overlayer.setPosition(x, y)

    def addEgg(self, eggData: PokemonEgg, x, y):
        self.window.delChild(self.underlayer)
        self.window.delChild(self.overlayer)
        self.window.addChild(self.underlayer)
        self.egg = AnimatedPicture((self.window), position=(x + 3, y + 20), picture=(self.window.eggSheets[0]))
        self.window.addChild(self.overlayer)

    def destroy(self):
        self.underlayer.destroy()
        self.overlayer.destroy()
        if self.egg:
            self.egg.destroy()

    def pulseState(self):
        if self.egg:
            self.egg.playAnimation()

    def setEggAnimation(self):
        if self.egg:
            self.egg.loopAnimation()


eggFrames = []
for i in range(1, 4):
    eggFrames.append(textureCache.getGuiImage(f"daycare/Egg0{i}"))

rvr = reversed(eggFrames)
for frame in rvr:
    eggFrames.append(frame)

eggSheet = CustomSheet(eggFrames, frames=(len(eggFrames), 1), referencePoint=(AnchorType.BOTTOMCENTER), animationDelay=0.1)

class PokemonPartyWindow(Window):

    def __init__(self):
        Window.__init__(self, desktop, size=(28, 172), position=(AnchorType.LEFTCENTER), draggable=True, style=(styleDB.windowsNoStyle),
          autosize=(True, True),
          visible=False)
        self.heldImg = textureCache.getGuiImage("party/held")
        self.followImg = textureCache.getGuiImage("party/follow-all")
        self.recallImg = textureCache.getGuiImage("party/recall-all")
        self.followOverImg = textureCache.getGuiImage("party/follow-all-over")
        self.recallOverImg = textureCache.getGuiImage("party/recall-all-over")
        self.pokeballEmpty = textureCache.getGuiImage("party/PokemonSlot empty")
        self.pokeballTaken = textureCache.getGuiImage("party/PokemonSlot")
        self._ball_graphics = {}
        for i in range(1, 28):
            self._ball_graphics[i] = textureCache.getGuiImage(f"party/PokemonSlot{i}")

        self.bg_table = Datatable(self)
        self.bg_table.setInternalMargins(0, 1)
        self.bg_table.setManualFit()
        self.dataTable = Datatable(self, position=(0, 0))
        self.dataTable.setInternalMargins(0, 1)
        self.dataTable.setManualFit()
        self.heldTable = Datatable(self, position=(0, 0))
        self.heldTable.setInternalMargins(0, 30)
        self.heldTable.setManualFit()
        for x in range(1, 7):
            picture = Picture((self.bg_table), picture=(self.pokeballEmpty))
            picture.lineupId = x
            picture.setAlpha(160)
            button = IconButton((self.dataTable), style=(styleDB.simpleButtonStyle),
              draggable=True,
              size=(42, 37),
              autosize=(False, False),
              iconAnchor=(AnchorType.CENTER))
            button.focusEnabled = False
            button.id = "PokemonParty"
            button.addCallback("onMouseLeftClick", self.showData)
            button.addCallback("onMouseRightClick", pokemonMenu.openMenuFromParty)
            button.addCallback("onWidgetDroppedOn", self.droppedPkmn)
            button.addCallback("onMouseDragBegin", self.hideHpBarDrag)
            button.addCallback("onMouseOver", self.showHpBar)
            button.addCallback("onMouseLeave", self.hideHpBar)
            button.pkmnData = None
            button.lineupId = x
            heldIcon = IconButton((self.heldTable), style=(styleDB.simpleButtonStyle),
              size=(8, 10),
              autosize=(False, False),
              iconAnchor=(AnchorType.BOTTOMRIGHT),
              icon=(self.heldImg),
              visible=False)
            heldIcon.lineupId = x
            self.bg_table.add(picture, row=(x - 1), col=0)
            self.heldTable.add(heldIcon, row=(x - 1), col=0)
            self.dataTable.add(button, row=(x - 1), col=0)

        self.dataTable.fitToContent()
        self.heldTable.fitToContent()
        self.bg_table.fitToContent()
        self.setAutoFit()
        self.incubators = {}
        self.eggSheets = {0: eggSheet}
        self.hpBar = Bar(self, style=(styleDB.defaultBarWithHpColors), position=(0,
                                                                                 0), size=(32,
                                                                                           8), visible=False)
        self.hpBar.pkmnData = None
        pyglet.clock.schedule_interval_soft(self.incubatorPulse, 1)

    def reset(self):
        for widget in self.bg_table.getWidgets():
            widget.setPicture(self.pokeballEmpty)
            widget.setColor(255, 255, 255)

        for widget in self.dataTable.getWidgets():
            widget.pkmnData = None
            widget.removeIcon()

        for widget in self.heldTable.getWidgets():
            widget.removeIcon()

        self.forceHide()

    def getIncubatorPlacement(self, incubator):
        return (
         3 + list(sessionService.incubators.incubators).index(incubator.incubatorId) * 40, self.dataTable.getTableHeight() + 6)

    def incubatorPulse(self, dt):
        for incubator in self.incubators.values():
            if random.randint(1, 5) == 3:
                incubator.pulseState()

    def addIncubator(self, incubator: EggIncubator):
        x, y = self.getIncubatorPlacement(incubator)
        underlayer = Picture(self, position=(x + 1, y + 28), picture=(textureCache.getGuiImage("daycare/IncubatorU")))
        overlayer = Picture(self, position=(x, y), picture=(textureCache.getGuiImage("daycare/IncubatorO")), enableEvents=True)
        overlayer.incubator = incubator
        overlayer.addCallback("onMouseOver", self.showTooltip)
        overlayer.addCallback("onMouseLeave", self.closeTooltip)
        self.incubators[incubator.incubatorId] = IncubatorPartySlot(self, incubator, underlayer, overlayer)

    def showTooltip(self, widget, x, y):
        if widget.incubator:
            eventManager.notify("onShowTooltip", widget.incubator, x, y)

    def closeTooltip(self, widget):
        eventManager.notify("onCloseTooltip")

    def deleteIncubator(self, incubatorId):
        self.incubators[incubatorId].destroy()
        del self.incubators[incubatorId]

    def addEgg(self, eggData: PokemonEgg, incubator: EggIncubator):
        x, y = self.getIncubatorPlacement(incubator)
        self.incubators[incubator.incubatorId].addEgg(eggData, x, y)

    def showHpBar(self, widget, x, y):
        if not widget.pkmnData:
            if self.hpBar.visible:
                self.hpBar.hide()
            return
        elif not self.hpBar.visible:
            self.hpBar.show()
        else:
            position = widget.getRelativePosition()
            self.hpBar.setPosition(4, position[1] + 36)
            if widget.pkmnData:
                (self.hpBar.setPercent)(*widget.pkmnData.stats.hp.values)
                self.hpBar.pkmnData = widget.pkmnData
                if widget.pkmnData.isFainted():
                    self.hpBar.setStyle(styleDB.faintedBarStyle)
                else:
                    self.hpBar.setStyle(styleDB.defaultBarWithHpColors)

    def hideHpBarDrag(self, widget, x, y, modifiers):
        self.hideHpBar(widget)

    def hideHpBar(self, widget):
        if self.hpBar.visible:
            self.hpBar.hide()
        self.hpBar.pkmnData = None

    def droppedPkmn(self, button, widgetDroppedOn, x, y, modifiers):
        if not button.pkmnData:
            return
        droppedName = widgetDroppedOn.__class__.__name__
        if droppedName == "IconButton":
            if widgetDroppedOn.id == "PokemonParty":
                if button.pkmnData:
                    if widgetDroppedOn.lineupId == button.pkmnData.lineupId:
                        return
                    packetManager.queueSend(cmsg.PokemonLineup, button.pkmnData.lineupId, widgetDroppedOn.pkmnData.lineupId if widgetDroppedOn.pkmnData else widgetDroppedOn.lineupId)
            if widgetDroppedOn.id == "Storage":
                if sessionService.npcId:
                    if sessionService.canAccessStorage():
                        if button.pkmnData.flags & PokemonFlag.NOSTORE:
                            eventManager.notify("onSystemMessage", "This Pokemon cannot be stored.")
                            return
                        packetManager.queueSend(cmsg.StoragePkmnStore, sessionService.npcId, button.pkmnData.id, widgetDroppedOn.storageData.boxId)
                else:
                    eventManager.notify("onSystemMessage", "You cannot access this while in a trade or battle.")
        if droppedName == "StorageWindow":
            if sessionService.canAccessStorage():
                if button.pkmnData.flags & PokemonFlag.NOSTORE:
                    eventManager.notify("onSystemMessage", "This Pokemon cannot be stored.")
                    return
                packetManager.queueSend(cmsg.StoragePkmnStore, sessionService.npcId, button.pkmnData.id, widgetDroppedOn.currentBox.boxId)
            else:
                eventManager.notify("onSystemMessage", "You cannot access this while in a trade or battle.")
        elif droppedName == "TradeWindow":
            pass
        if widgetDroppedOn.id and not widgetDroppedOn.client.getPokemonButton(button.pkmnData.id):
            if button.pkmnData.isReleased():
                eventManager.notify("onSystemMessage", "Please recall the Pokemon before trading.")
            else:
                if widgetDroppedOn.client:
                    if widgetDroppedOn.client.full:
                        eventManager.notify("onSystemMessage", "The trade window is currently full.")
                        return
                    if button.pkmnData.flags & PokemonFlag.NOTRADE:
                        eventManager.notify("onSystemMessage", "This Pokemon cannot be traded.")
                        return
                packetManager.queueSend(cmsg.TradePokemon, 0, button.pkmnData.id)
        elif droppedName == "Desktop":
            if button.pkmnData:
                if sessionService.trade:
                    eventManager.notify("onSystemMessage", "You cannot do this action while trading.")
                    return
                x, y = sceneManager.convert(x, y)
                eventManager.notify("onReleaseAttempt", button.pkmnData, worldCamera.toMapPosition(x, y), modifiers)
                desktop.lostFocus()
        elif droppedName == "HotbarButton":
            if button.pkmnData:
                widgetDroppedOn.assignNewPokemon(button.pkmnData)
        elif droppedName == "DaycareContainer":
            pass
        if button.pkmnData:
            widgetDroppedOn.addRequestPokemon(button.pkmnData)

    def showData(self, widget, x, y, modifiers):
        if widget.pkmnData:
            eventManager.notify("onPokemonShow", widget.pkmnData)

    def getButtonByLineupId(self, lineupId):
        for widget in self.dataTable.widgets:
            if widget.lineupId == lineupId:
                return widget

        return

    def getButtonById(self, pkmnId):
        for widget in self.dataTable.widgets:
            if widget.pkmnData:
                if widget.pkmnData.id == pkmnId:
                    return widget

        return

    def getHeldButtonById(self, pkmnId):
        for widget in self.heldTable.widgets:
            if widget.pkmnData:
                if widget.pkmnData.id == pkmnId:
                    return widget

        return

    def getBgByLineupId(self, lineupId):
        for widget in self.bg_table.widgets:
            if widget.lineupId == lineupId:
                return widget

        return

    def getHeldButtonByLineupId(self, lineupId):
        for widget in self.heldTable.widgets:
            if widget.lineupId:
                if widget.lineupId == lineupId:
                    return widget

        return

    def itemEquipped(self, pkmnData):
        widget = self.getHeldButtonByLineupId(pkmnData.lineupId)
        if not widget.visible:
            widget.show()

    def itemUnequipped(self, pkmnData):
        widget = self.getHeldButtonByLineupId(pkmnData.lineupId)
        if widget.visible:
            widget.hide()

    def getBallBg(self, pkmnData):
        return self._ball_graphics[pkmnData.ballId]

    def DataChanged(self, pkmnData):
        widget = self.getButtonByLineupId(pkmnData.lineupId)
        widget.pkmnData = pkmnData
        icon = textureCache.getPokemonIcon(pkmnData.dexId)
        widget.setIconDefault(icon)
        if pkmnData.heldNameId:
            self.itemEquipped(pkmnData)
        self._updateBGButtons(pkmnData.lineupId)

    def _updateBGButtons(self, lineupId):
        button = self.getButtonByLineupId(lineupId)
        pkmnData = button.pkmnData
        bg = self.getBgByLineupId(lineupId)
        if pkmnData:
            bg.setPicture(self.getBallBg(pkmnData))
            if pkmnData.isReleased():
                bg.setColor(64, 64, 64)
            else:
                bg.setColor(255, 255, 255)
        else:
            bg.setPicture(self.pokeballEmpty)
            bg.setColor(255, 255, 255)

    def removePokemon(self, pokemonId):
        button = self.getButtonById(pokemonId)
        if button:
            button.pkmnData = None
            button.removeIcon()
            bg = self.getBgByLineupId(button.lineupId)
            bg.setPicture(self.pokeballEmpty)

    def lineupSwitch(self, lineupId1, lineupId2):
        original = self.getButtonByLineupId(lineupId1)
        new = self.getButtonByLineupId(lineupId2)
        oldHeld = self.getHeldButtonByLineupId(lineupId1)
        newHeld = self.getHeldButtonByLineupId(lineupId2)
        original.pkmnData, new.pkmnData = new.pkmnData, original.pkmnData
        if original.pkmnData:
            original.setIconDefault(textureCache.getPokemonIcon(original.pkmnData.dexId))
            if original.pkmnData.heldNameId > 0:
                if not oldHeld.visible:
                    oldHeld.show()
        elif oldHeld.visible:
            oldHeld.hide()
        else:
            original.removeIcon()
        if oldHeld.visible:
            oldHeld.hide()
        if new.pkmnData:
            new.setIconDefault(textureCache.getPokemonIcon(new.pkmnData.dexId))
            if new.pkmnData.heldNameId > 0:
                if not newHeld.visible:
                    newHeld.show()
        elif newHeld.visible:
            newHeld.hide()
        else:
            new.removeIcon()
            if newHeld.visible:
                newHeld.hide()
            self._updateBGButtons(lineupId1)
            self._updateBGButtons(lineupId2)


class EggHatchWindow(Window):

    def __init__(self):
        Window.__init__(self, desktop, size=(150, 150), position=(AnchorType.CENTER), draggable=True, style=(styleDB.windowsDefaultStyle),
          autosize=(True, True),
          visible=False)
        self.eggImage = textureCache.getGuiImage("daycare/Egg01")
        self.shineImage = textureCache.getEffect("evolutionShine_[6]", referencePoint=(RefPointType.CENTER))
        self.spellingLabel = DialogSpellingLabel(self, text="What's this?... It's hatching!", position=(AnchorType.TOPCENTER), size=(150,
                                                                                                                                     0), multiline=True, alignment=(Alignment.CENTER))
        self.eggPicture = AnimatedPicture(self, position=(AnchorType.TOPCENTER), picture=eggSheet, refPointType=(RefPointType.BOTTOMCENTER))
        hatchFrames = []
        for i in range(1, 6):
            frame = textureCache.getGuiImage(f"daycare/EggHatch0{i}")
            hatchFrames.append(frame)

        self.hatchSheet = CustomSheet(hatchFrames, frames=(len(hatchFrames), 1), referencePoint=(RefPointType.BOTTOMCENTER), animationDelay=1)
        self.hatchPicture = AnimatedPicture(self, position=(78, 65), picture=(self.hatchSheet), refPointType=(RefPointType.BOTTOMCENTER))
        self.fitToContent()

    def hatch(self, incubator: EggIncubator):
        sessionService.incubators.hatching = True
        if self.hatchPicture.visible:
            self.hatchPicture.hide()
        if not self.eggPicture.visible:
            self.eggPicture.show()
        if self.eggPicture.picture != eggSheet:
            self.eggPicture.setPicture(eggSheet)
        self.spellingLabel.text = "What's this?...\nThe egg, it's hatching!"
        self.spellingLabel.start()
        self.eggPicture.loopAnimation()
        self.hatchPicture.setPicture(self.hatchSheet)
        self.fitToContent()

        def startHatching():
            self.eggPicture.stopAnimation()
            if not self.hatchPicture.visible:
                self.hatchPicture.show()
            self.hatchPicture.runAnimation(5)

            def stop():
                if self.hatchPicture.visible:
                    self.hatchPicture.hide()
                pokemonId, dexId, gender = sessionService.incubators.waiting.pop(0)
                self.eggPicture.setPicture(textureCache.getPokemonFront(dexId, 0))
                self.fitToContent()
                mixerController.playCry(dexId)
                eventManager.notify("onGetNewPokemon", pokemonId, dexId, gender)
                if not sessionService.incubators.waiting:
                    sessionService.incubators.hatching = False
                    reactor.callLater(2, self.close)

            reactor.callLater(5, stop)

        reactor.callLater(2, startHatching)


class PokemonParty:

    def __init__(self):
        self.window = PokemonPartyWindow()
        self.hatchWindow = EggHatchWindow()
        eventManager.registerListener(self)

    def reset(self):
        self.window.reset()

    def onItemEquip(self, pokemon, nameId):
        self.window.itemEquipped(pokemon)

    def onItemUnequip(self, pokemon):
        self.window.itemUnequipped(pokemon)

    def onPokemonReceived(self, pokemonData):
        self.window.DataChanged(pokemonData)

    def onPokemonDelete(self, pokemonId):
        self.window.removePokemon(pokemonId)

    def onLineupSwitch(self, lineupId1, lineupId2):
        self.window.lineupSwitch(lineupId1, lineupId2)

    def onHotkeyPress(self, hotkeyName):
        if hotkeyName == "pokeparty":
            if self.window.visible:
                self.window.hide()
            else:
                self.window.show()

    def onPokemonEvolve(self, pokemonData, dexId):
        if pokemonData in sessionService.getClientPokemonsData():
            button = self.window.getButtonById(pokemonData.id)
            button.setIconDefault(textureCache.getPokemonIcon(pokemonData.dexId))

    def onPokemonRelease(self, trainer, pokemon, x, y):
        if trainer == sessionService.getClientTrainer():
            bg = self.window.getBgByLineupId(pokemon.data.lineupId)
            bg.setColor(64, 64, 64)

    def onPokemonRecall(self, pokemon):
        if sessionService.isClientPokemon(pokemon):
            bg = self.window.getBgByLineupId(pokemon.data.lineupId)
            bg.setColor(255, 255, 255)

    def onPokemonHpUpdate(self, pokemonData):
        if sessionService.isClientPokemonData(pokemonData) and self.window.hpBar.visible and self.window.hpBar.pkmnData:
            if self.window.hpBar.pkmnData == pokemonData:
                (self.window.hpBar.setPercent)(*pokemonData.stats.hp.values)

    def onPokemonStatUpdate(self, pokemonData):
        if sessionService.isClientPokemonData(pokemonData) and self.window.hpBar.visible and self.window.hpBar.pkmnData:
            if self.window.hpBar.pkmnData == pokemonData:
                (self.window.hpBar.setPercent)(*pokemonData.stats.hp.values)

    def onIncubatorReceived(self, incubator: EggIncubator):
        self.window.addIncubator(incubator)

    def onIncubatorDeleted(self, incubatorId):
        self.window.deleteIncubator(incubatorId)
        for incubator in self.window.incubators.values():
            incubator.updateAlignments()

    def onIncubatedEggReceive(self, incubator, eggData):
        self.window.addEgg(eggData, incubator)

    def onEggHatch(self, incubator: EggIncubator):
        if not self.hatchWindow.visible:
            self.hatchWindow.show()
        self.hatchWindow.hatch(incubator)


pokemonParty = PokemonParty()
