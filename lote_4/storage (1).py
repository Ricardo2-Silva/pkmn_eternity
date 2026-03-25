# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\interface\npc\storage.py
"""
Created on Jul 29, 2011

@author: Ragnarok
"""
from typing import Dict
from client.interface.notification import confirmWindow
from shared.container.net import cmsg
from shared.container.constants import IdRange, Gender, MAX_BOX_STORAGE
from client.render.cache import textureCache
from client.control.gui import Textbox, Window, Label, Button, Picture, IconButton, PageDatatable, Menu
from client.game import desktop
from client.data.gui import styleDB
from client.render.utils.patch import PatchType
from client.data.utils.anchor import AnchorType, Alignment
from client.control.events.event import eventManager
from client.control.service.session import sessionService
from client.data.DB import pokemonDB, natureDB, abilityDB, itemDB
from client.data.container.char import charContainer
from shared.controller.net.packetStruct import RawUnpacker
from client.control.net.sending import packetManager
from client.data.system.storage import storageConfig
from client.interface.inputMenu import inputMenu
from client.data.gui.style import ButtonStyle
from client.data.gui.styleDB import noPaddingStyle
from pyglet.window.key import MOD_CTRL
MAX_CLIENT_BOXES = 10

class MenuWindow(Menu):

    def __init__(self):
        Menu.__init__(self, desktop)
        self.pokemonData = None
        self.summaryBtn = Button(self, style=(styleDB.menuItemStyle), size=(90, 20), text="Summary", autosize=(False,
                                                                                                               False))
        self.summaryBtn.addCallback("onMouseLeftClick", self._showSummaryClick)
        self.add(self.summaryBtn)
        self.releaseBtn = Button(self, style=(styleDB.menuItemStyle), size=(90, 20), text="Release", autosize=(False,
                                                                                                               False))
        self.releaseBtn.addCallback("onMouseLeftClick", self._releasePokemonClick)
        self.add(self.releaseBtn)
        self.cancelBtn = Button(self, style=(styleDB.menuItemStyle), size=(90, 20), text="Cancel", autosize=(False,
                                                                                                             False))
        self.add(self.cancelBtn)
        self.buttons = (
         self.summaryBtn, self.releaseBtn, self.cancelBtn)
        self.fitToContent()

    def _showSummaryClick(self, widget, x, y, modifiers):
        pkmnData = charContainer.getDataByIdIfAny(self.pokemonData.id, IdRange.PC_POKEMON)
        if pkmnData:
            eventManager.notify("onPokemonShow", pkmnData)
        else:
            packetManager.queueSend(cmsg.StoragePreview, sessionService.npcId, self.pokemonData.id)

    def _releasePokemonClick(self, widget, x, y, modifiers):

        def deletePacketSend():
            packetManager.queueSend(cmsg.PokemonDelete, sessionService.npcId, self.pokemonData.id)

        confirmWindow.verify(f"This will permanently delete {self.pokemonData.name}.\n\nThis cannot be undone, are you sure you want to continue?", deletePacketSend)

    def reset(self):
        self.pokemonData = None
        self.forceHide()

    def closeWindow(self):
        if self.visible:
            self.hide()

    def showMenu(self, pokemonData, x, y):
        self.pokemonData = pokemonData
        if not self.visible:
            self.show()
        self.setActive()
        self.setPosition(x, y)


class BoxStyleDB:

    def __init__(self):
        self.bars = {}
        self.boxes = {}

    def getBarStyle(self, imageId, image):
        if imageId not in self.bars:
            boxButtonStyle = ButtonStyle(noPaddingStyle)
            boxButtonStyle.setBackgroundImage(image)
            self.bars[imageId] = boxButtonStyle
        return self.bars[imageId]

    def getMainStyle(self, imageId, image):
        if imageId not in self.boxes:
            boxButtonStyle = ButtonStyle(noPaddingStyle)
            boxButtonStyle.setBackgroundImage(image)
            self.boxes[imageId] = boxButtonStyle
        return self.boxes[imageId]


boxStyles = BoxStyleDB()

class StorageBox:

    def __init__(self, window, boxId, imageId, name):
        self.pokemon = {}
        self.window = window
        self.haveBox = False
        self.boxId = boxId
        self.name = name
        self.imageId = imageId
        self.bgImg = window.boxImages.bgs[imageId]
        self.barImg = window.boxImages.bars[imageId]
        self.mainBtn = Button((window.boxSelect.boxPicTable), text=(self.name), size=(116,
                                                                                      23), autosize=(False,
                                                                                                     False), style=(boxStyles.getBarStyle(imageId, self.barImg)))
        self.mainBtn.addCallback("onMouseLeftClick", self.showBox)
        window.boxSelect.boxPicTable.add(self.mainBtn)
        self.boxTable = PageDatatable(window, position=(218, 35), maxCols=5, maxRows=4, visible=False)

    def reset(self):
        self.haveBox = False
        self.boxTable.emptyAndDestroy()

    def setData(self, window, imageId, name):
        self.bgImg = window.boxImages.bgs[imageId]
        self.barImg = window.boxImages.bars[imageId]
        self.imageId = imageId
        self.name = name
        self.mainBtn.text = name
        self.mainBtn.setStyle(boxStyles.getBarStyle(imageId, self.barImg))

    def fitToContent(self):
        self.boxTable.fitToContent()

    def showBox(self, widget, x, y, modifiers):
        if sessionService.npcId or True:
            if sessionService.canAccessStorage():
                if not self.haveBox:
                    packetManager.queueSend(cmsg.StorageGetBox, sessionService.npcId, self.boxId)
                else:
                    self.displayBox()
            else:
                eventManager.notify("onSystemMessage", "You cannot access this while in a trade or battle.")

    def getButtonById(self, pkmnId):
        for widget in self.boxTable.widgets:
            if widget.storedPokemon:
                if widget.storedPokemon.id == pkmnId:
                    return widget

        return

    def displayBox(self):
        self.window.insideBox.bgPic.setPicture(self.bgImg)
        self.window.showBox()
        self.window.insideBox.barBtn.setBackgroundImage(self.barImg)
        self.window.insideBox.barBtn.text = self.name
        self.boxTable.show()
        self.window.currentBox = self

    def hideBox(self):
        self.boxTable.hide()
        self.window.showMenu()
        self.window.currentBox = None

    def openMenu(self, widget, x, y, modifiers):
        self.window.menu.showMenu(widget.storedPokemon, x, y)

    def previousSkin(self):
        previousBox = self.imageId - 1
        if previousBox < 0:
            return
        if previousBox in self.window.boxImages.bgs:
            self.bgImg = self.window.boxImages.bgs[previousBox]
            self.barImg = self.window.boxImages.bars[previousBox]
            self.imageId = previousBox
            self.changeSkin()

    def changeSkin(self):
        self.mainBtn.setBackgroundImage(self.barImg)
        self.window.insideBox.barBtn.setBackgroundImage(self.barImg)
        self.window.insideBox.bgPic.setPicture(self.bgImg)
        self.saveBox()

    def saveBox(self):
        storageConfig.updateBox(self)
        storageConfig.save()

    def nextSkin(self):
        nextBox = self.imageId + 1
        if nextBox > 31:
            return
        if nextBox in self.window.boxImages.bgs:
            self.bgImg = self.window.boxImages.bgs[nextBox]
            self.barImg = self.window.boxImages.bars[nextBox]
            self.imageId = nextBox
            self.changeSkin()

    def changeBoxName(self, name):
        self.name = name
        self.mainBtn.text = name
        self.saveBox()

    def addPokemon(self, storedPokemon):
        self.pokemon[storedPokemon.id] = storedPokemon
        button = IconButton((self.boxTable), icon=(textureCache.getPokemonIcon(storedPokemon.dexId)), draggable=True, style=(styleDB.simpleButtonStyle))
        button.storedPokemon = storedPokemon
        button.addCallback("onMouseRightClick", self.openMenu)
        button.addCallback("onWidgetDroppedOn", self.dropPokemon)
        button.addCallback("onMouseLeftClick", self.setSelected)
        button.addCallback("onMouseLeftClick", self.addToMove)
        self.boxTable.add(button)

    def removePokemon(self, pokemonId):
        widget = self.getButtonById(pokemonId)
        if widget:
            del self.pokemon[pokemonId]
            self.boxTable.deleteAndDestroy(widget)
            self.boxTable.reorganize()
            return True
        else:
            return False

    def dropPokemon(self, draggedWidget, droppedOnWidget, x, y, modifiers):
        dropName = droppedOnWidget.__class__.__name__
        if dropName == "IconButton":
            if droppedOnWidget.id == "PokemonParty":
                if sessionService.canAccessStorage():
                    packetManager.queueSend(cmsg.StoragePkmnWithdraw, sessionService.npcId, draggedWidget.storedPokemon.id, droppedOnWidget.pkmnData.id if droppedOnWidget.pkmnData else 0)
            else:
                eventManager.notify("onSystemMessage", "You cannot access this while in a trade or battle.")

    def addToMove(self, widget, x, y, modifiers):
        if modifiers & MOD_CTRL:
            self.window.insideBox.addToMove(widget)

    def setSelected(self, widget, x, y, modifiers):
        if widget.storedPokemon:
            self.window.insideBox.showMinorDetails(widget.storedPokemon)

    def getSize(self):
        return len(self.pokemon)


class BoxImages(object):
    __slots__ = [
     "bars", "bgs"]

    def __init__(self):
        self.bars = {}
        self.bgs = {}
        for x in range(0, 31):
            topName = "".join(["%.2d", "_top"]) % x
            bottomName = "".join(["%.2d", "_bottom"]) % x
            self.bars[x] = textureCache.getGuiImage(f"storage/boxes/{topName}")
            self.bgs[x] = textureCache.getGuiImage(f"storage/boxes/{bottomName}")


class StoredPokemonData:
    boxId = 0
    id = 0
    dexId = 0
    level = 0
    gender = 0
    shiny = 0
    name = "Unknown."
    nature = 0
    abilityId = 0
    heldNameId = 0
    frontVer = 0


class StorageWindow(Window):
    boxes: Dict[(int, StorageBox)]

    def __init__(self, control):
        Window.__init__(self, desktop, position=(200, 200), size=(393, 216), draggable=True, visible=False, style=(styleDB.windowsDefaultStyleNoPadding))
        self.control = control
        self.currentBox = None
        self.menu = MenuWindow()
        self.boxes = {}
        self.boxImages = BoxImages()
        self.boxSelect = BoxSelection(self)
        self.insideBox = InsideBox(self)
        self.selected = self.boxSelect
        self.setManualFit()
        for i in range(1, MAX_CLIENT_BOXES + 1):
            self.boxes[i] = StorageBox(self, i, i, "Box 1")

        self.boxSelect.boxPicTable.fitToContent()
        self.setAutoFit()

    def boxNameToStorage(self, boxName):
        for box in self.boxes.values():
            if box.name.lower() == boxName.lower():
                return box.boxId

        return

    def reset(self):
        self.currentBox = None
        self.menu.reset()
        for i in range(1, MAX_CLIENT_BOXES + 1):
            self.boxes[i].reset()

        self.openDefault()
        if self.visible:
            self.hide()

    def loadStorage(self):
        """
         Load storage happens after the client trainer is set since Storage data is now trainer specific.
         We only load 10 boxes as that's the max view.
        """
        self.setManualFit()
        for i in range(1, MAX_CLIENT_BOXES + 1):
            boxConfig = storageConfig.getStorageBox(i)
            self.boxes[i].setData(self, boxConfig["graphic"], boxConfig["name"])

        self.boxSelect.boxPicTable.fitToContent()
        self.setAutoFit()

    def showBox(self):
        self.boxSelect.hide()
        self.insideBox.show()
        self.selected = self.insideBox

    def showMenu(self):
        self.insideBox.hide()
        self.boxSelect.show()
        self.selected = self.boxSelect

    def openDefault(self):
        if self.selected != self.boxSelect:
            self.showMenu()


class InsideBox(object):
    __doc__ = " Shows Pokemon stats, box background and other options. "

    def __init__(self, window):
        self.window = window
        self.selectedPkmn = []
        self.currentId = 0
        self.boxImg = textureCache.getGuiImage("storage/storage")
        self.boxPic = Picture((self.window), (self.boxImg), visible=False)
        self.backSkinImg = textureCache.getGuiImage("storage/back")
        self.nextSkinImg = textureCache.getGuiImage("storage/next")
        self.barBtn = Button((self.window), position=(241, 17), size=(116, 23), visible=False, style=(styleDB.simpleButtonStyle), autosize=(False,
                                                                                                                                            False))
        self.barBtn.addCallback("onMouseLeftClick", self.showBoxRename)
        self.bgPic = Picture((self.window), position=(218, 43), visible=False)
        self.backBtn = Button((self.window), text="", position=(210, 172), size=(22,
                                                                                 24), autosize=(False,
                                                                                                False), visible=False, style=(styleDB.leftArrowButtonStyle))
        self.backBtn.addCallback("onMouseLeftClick", self.backToMenu)
        self.prevSkinBtn = IconButton((self.window), position=(219, 17), visible=False, icon=(self.backSkinImg), style=(styleDB.simpleButtonStyle))
        self.prevSkinBtn.addCallback("onMouseLeftClick", self.prevSkinShow)
        self.nextSkinBtn = IconButton((self.window), position=(362, 17), visible=False, icon=(self.nextSkinImg), style=(styleDB.simpleButtonStyle))
        self.nextSkinBtn.addCallback("onMouseLeftClick", self.nextSkinShow)
        self.boxNameTxt = Textbox((self.window), position=(241, 17), size=(116, 23), visible=False, maxLetters=16)
        self.boxNameTxt.addCallback("onMouseClickOut", self.setBoxName)
        self.boxNameTxt.addCallback("onKeyReturn", self.setBoxName)
        self.nicknameLbl = Label((self.window), position=(8, 29), size=(71, 16), text="Nickname", visible=False)
        self.shinyLbl = Label((self.window), position=(175, 36), text="", visible=False)
        self.frontPic = Picture((self.window), position=(105, 36), visible=False)
        self.levelLbl = Label((self.window), position=(8, 45), size=(70, 14), text="Level", visible=False)
        self.natureLbl = Label((self.window), position=(8, 77), visible=False)
        self.abilityLbl = Label((self.window), position=(8, 110), visible=False)
        self.itemLbl = Label((self.window), position=(8, 143), visible=False)
        self.dexIdLbl = Label((self.window), position=(113, 129), size=(89, 16), alignment=(Alignment.CENTER), multiline=True, text="100", visible=False)
        self.nameLbl = Label((self.window), position=(114, 145), size=(89, 16), alignment=(Alignment.CENTER), multiline=True, visible=False)
        self.genderLbl = Label((self.window), position=(114, 161), size=(89, 16), visible=False, style=(styleDB.blueDetailsStyle))
        self.element1 = Picture((self.window), position=(142, 177), visible=False)
        self.element2 = Picture((self.window), position=(123, 177), visible=False)
        self.element3 = Picture((self.window), position=(159, 177), visible=False)
        self.detailsButton = Button((self.window), position=(10, 170), size=(90, 26), visible=False, autosize=(False,
                                                                                                               False), style=(styleDB.cancelButtonStyle), text="Summary")
        self.detailsButton.addCallback("onMouseLeftClick", self.getDetails)
        self.moveButton = Button((self.window), position=(250, 170), size=(64, 26), visible=False, autosize=(False,
                                                                                                             False), style=(styleDB.cancelButtonStyle), text="Move")
        self.moveButton.addCallback("onMouseLeftClick", self.movePokemon)
        self.cancelButton = Button((self.window), position=(320, 170), size=(64, 26), autosize=(False,
                                                                                                False), style=(styleDB.cancelButtonStyle), visible=False, text="Close")
        self.cancelButton.addCallback("onMouseLeftClick", self.hideWindow)

    def prevSkinShow(self, widget, x, y, modifiers):
        self.window.currentBox.previousSkin()

    def nextSkinShow(self, widget, x, y, modifiers):
        self.window.currentBox.nextSkin()

    def setBoxName(self):
        currentBox = self.window.currentBox
        currentBox.changeBoxName(self.boxNameTxt.text)
        self.barBtn.text = currentBox.name
        self.boxNameTxt.hide()
        self.boxNameTxt.setInactive()

    def showBoxRename(self, widget, x, y, modifiers):
        if not self.boxNameTxt.visible:
            self.boxNameTxt.show()
            self.boxNameTxt.text = self.barBtn.text
            self.boxNameTxt.setActive()

    def showMinorDetails(self, storedPokemon):
        if self.currentId != storedPokemon.id:
            if not self.frontPic.visible:
                self.frontPic.show()
                self.levelLbl.show()
                self.dexIdLbl.show()
                self.nameLbl.show()
                self.nicknameLbl.show()
                self.natureLbl.show()
                self.abilityLbl.show()
                self.itemLbl.show()
                self.genderLbl.show()
                self.shinyLbl.show()
                self.element1.show()
                self.element2.show()
                self.element3.show()
            self.nameLbl.text = pokemonDB.name(storedPokemon.dexId)
            self.nicknameLbl.text = storedPokemon.name
            if storedPokemon.gender == Gender.MALE:
                self.genderLbl.text = "♂"
                self.genderLbl.setStyle(styleDB.blueDetailsStyle)
            else:
                if storedPokemon.gender == Gender.FEMALE:
                    self.genderLbl.text = "♀"
                    self.genderLbl.setStyle(styleDB.redDetailsStyle)
                else:
                    self.genderLbl.text = ""
                element = pokemonDB.type(storedPokemon.dexId)
                if element[1] is None:
                    self.element1.setPicture(textureCache.getElementIcon(element[0]))
                    self.element2.removePicture()
                    self.element3.removePicture()
                else:
                    self.element1.removePicture()
                    self.element2.setPicture(textureCache.getElementIcon(element[0]))
                    self.element3.setPicture(textureCache.getElementIcon(element[1]))
            self.frontPic.setPicture(textureCache.getPokemonFront((storedPokemon.dexId), version=(storedPokemon.frontVer), shiny=(storedPokemon.shiny), gender=(storedPokemon.gender)))
            self.levelLbl.text = f"Level {storedPokemon.level}"
            self.dexIdLbl.text = str(storedPokemon.dexId)
            self.nameLbl.text = pokemonDB.name(storedPokemon.dexId).title()
            self.shinyLbl.text = "★" if storedPokemon.shiny else ""
            self.natureLbl.text = natureDB.name(storedPokemon.nature)
            self.abilityLbl.text = abilityDB.name(storedPokemon.abilityId)
            self.itemLbl.text = itemDB.name(storedPokemon.heldNameId)
            self.currentId = storedPokemon.id

    def getDetails(self, widget, x, y, modifiers):
        pkmnData = charContainer.getDataByIdIfAny(self.currentId, IdRange.PC_POKEMON)
        if pkmnData:
            eventManager.notify("onPokemonShow", pkmnData)
        else:
            packetManager.queueSend(cmsg.StoragePreview, sessionService.npcId, self.currentId)

    def addToMove(self, button):
        if button.storedPokemon:
            pkmnId = button.storedPokemon.id
            if pkmnId in self.selectedPkmn:
                button.setColor(255, 255, 255)
                self.selectedPkmn.remove(pkmnId)
            else:
                button.setColor(255, 0, 0)
                self.selectedPkmn.append(pkmnId)

    def movePokemon(self, widget, x, y, modifiers):
        if self.selectedPkmn:
            inputMenu.storageMove.display(self.window, self.window.currentBox, self.selectedPkmn, x, y)
        else:
            eventManager.notify("onSystemMessage", "Use Ctrl + Click to select at least one Pokemon to move.")

    def hideWindow(self, widget, x, y, modifiers):
        if self.window.currentBox:
            self.window.currentBox.hideBox()
        self.window.hide()

    def backToMenu(self, widget, x, y, modifiers):
        if self.window.currentBox:
            self.window.currentBox.hideBox()

    def hide(self):
        storageBox = self.window.currentBox
        for pkmnId in self.selectedPkmn:
            button = storageBox.getButtonById(pkmnId)
            button.setColor(255, 255, 255)

        del self.selectedPkmn[:]
        self.selectedId = 0
        self.boxPic.hide()
        self.barBtn.hide()
        self.bgPic.hide()
        self.backBtn.hide()
        self.prevSkinBtn.hide()
        self.nextSkinBtn.hide()
        if self.frontPic.visible:
            self.frontPic.hide()
            self.levelLbl.hide()
            self.dexIdLbl.hide()
            self.nameLbl.hide()
            self.shinyLbl.hide()
            self.nicknameLbl.hide()
            self.natureLbl.hide()
            self.abilityLbl.hide()
            self.itemLbl.hide()
            self.genderLbl.hide()
            self.element1.hide()
            self.element2.hide()
            self.element3.hide()
        self.detailsButton.hide()
        self.moveButton.hide()
        self.cancelButton.hide()

    def show(self):
        self.boxPic.show()
        self.bgPic.show()
        self.barBtn.show()
        self.backBtn.show()
        self.prevSkinBtn.show()
        self.nextSkinBtn.show()
        self.detailsButton.show()
        self.moveButton.show()
        self.cancelButton.show()


class BoxSelection:

    def __init__(self, window):
        self.window = window
        self.mainImg = textureCache.getGuiImage("storage/main")
        self.mainPic = Picture(window, self.mainImg)
        self.pokeOverImg = textureCache.getGuiImage("storage/pokeclose_normal")
        self.pokeNormalImg = textureCache.getGuiImage("storage/pokeclose_over")
        self.closeBtn = IconButton(window, position=(175, 170), icon=(self.pokeNormalImg), style=(styleDB.simpleButtonStyle))
        self.closeBtn.setIconOver(self.pokeOverImg)
        self.closeBtn.addCallback("onMouseLeftClick", self.closeWindow)
        self.boxPicTable = PageDatatable(window, position=(50, 28), maxCols=2, maxRows=5)
        self.boxPicTable.setInternalMargins(61, 11)

    def hide(self):
        self.mainPic.hide()
        self.boxPicTable.hide()
        self.closeBtn.hide()

    def show(self):
        self.mainPic.show()
        self.boxPicTable.show()
        self.closeBtn.show()

    def closeWindow(self, widget, x, y, modifiers):
        sessionService.npc = None
        self.window.hide()


class PokemonStorage:

    def __init__(self):
        self.window = StorageWindow(self)
        eventManager.registerListener(self)

    def reset(self):
        self.window.reset()

    def onClientTrainerLoaded(self):
        self.window.loadStorage()

    def openStorage(self):
        if not self.window.visible:
            self.window.show()
        self.window.openDefault()

    def onClientCharWarp(self, char, mapId, mapx, mapy):
        if self.window.visible:
            self.window.hide()

    def getBox(self, boxId):
        return self.window.boxes[boxId]

    def onStorePokemon(self, pokemonData, boxId):
        storageBox = self.getBox(boxId)
        storedPokemon = StoredPokemonData()
        storedPokemon.boxId = boxId
        storedPokemon.id = pokemonData.id
        storedPokemon.dexId = pokemonData.dexId
        storedPokemon.level = pokemonData.level
        storedPokemon.gender = pokemonData.gender
        storedPokemon.shiny = pokemonData.shiny
        storedPokemon.name = pokemonData.name
        storedPokemon.nature = pokemonData.nature
        storedPokemon.abilityId = pokemonData.abilityId
        storedPokemon.heldNameId = pokemonData.heldNameId
        storedPokemon.frontVer = pokemonData.frontVer
        storageBox.addPokemon(storedPokemon)
        storageBox.fitToContent()

    def onPokemonReceived(self, pokemonData):
        for storageBox in self.window.boxes.values():
            if storageBox.removePokemon(pokemonData.id):
                storageBox.fitToContent()
                break

    def onPokemonDelete(self, pokemonId):
        for storageBox in self.window.boxes.values():
            if storageBox.removePokemon(pokemonId):
                storageBox.fitToContent()
                break

    def onReceivedStorage(self, data):
        packer = RawUnpacker(data)
        _, boxId, length = packer.get("!BBB")
        storageBox = self.getBox(boxId)
        for _ in range(length):
            pkmnId, dexId, level, gender, shiny, nature, abilityId, itemId, frontVer = packer.get("!IHBBBBBHB")
            name = packer.getString()
            storedPokemon = StoredPokemonData()
            storedPokemon.boxId = boxId
            storedPokemon.id = pkmnId
            storedPokemon.dexId = dexId
            storedPokemon.level = level
            storedPokemon.gender = gender
            storedPokemon.shiny = shiny
            storedPokemon.name = name
            storedPokemon.nature = nature
            storedPokemon.abilityId = abilityId
            storedPokemon.heldNameId = itemId
            storedPokemon.frontVer = frontVer
            storageBox.addPokemon(storedPokemon)

        storageBox.fitToContent()
        if storageBox.haveBox:
            pass
        else:
            storageBox.displayBox()
        storageBox.haveBox = True

    def onStorageMove(self, fromBoxId, toBoxId, pokemonIds):
        sourceBox = self.window.boxes[fromBoxId]
        destinationBox = self.window.boxes[toBoxId]
        storedPokemon = [sourceBox.pokemon[pokemonId] for pokemonId in pokemonIds]
        for pokemonId in pokemonIds:
            sourceBox.removePokemon(pokemonId)

        sourceBox.fitToContent()
        if destinationBox.haveBox:
            for pokemon in storedPokemon:
                destinationBox.addPokemon(pokemon)

            destinationBox.fitToContent()
        self.window.insideBox.selectedPkmn = []


storage = PokemonStorage()
