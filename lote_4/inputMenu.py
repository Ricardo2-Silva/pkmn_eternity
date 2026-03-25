# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\interface\inputMenu.py
"""
Created on Jul 26, 2011

@author: Ragnarok
"""
from client.control.gui import Textbox, Window, Button, Header
from client.data.gui.shop import ShopItem, ShopPokemon
from shared.container.constants import ItemFlag
from shared.controller.net.packetStruct import RawPacker
from shared.container.net import cmsg
from client.control.service.session import sessionService
from client.control.events.event import eventManager
from client.control.net.sending import packetManager
from client.data.utils.anchor import AnchorType
from client.game import desktop

class InputWindow(Window):

    def __init__(self, headerName):
        Window.__init__(self, desktop, position=(100, 100), visible=False, size=(87,
                                                                                 85), draggable=True)
        Header(self, headerName)
        self.inputText = Textbox(self, position=(AnchorType.CENTERTOP), size=(75, 20), text="0", maxLetters=10)
        self.inputText.addCallback("onMouseLeftClick", self.resetInput)
        self.inputText.addCallback("onKeyReturn", self.process)
        self.confirmBtn = Button(self, position=(AnchorType.CENTERBOTTOM), size=(64,
                                                                                 24), text="Ok")
        self.confirmBtn.addCallback("onMouseLeftClick", self.clickProcess)
        self.fitToContent()

    def clickProcess(self, widget, x, y, modifiers):
        self.process()

    def resetInput(self, widget, x, y, modifiers):
        widget.text = ""

    def process(self):
        raise NotImplemented

    def clear(self):
        raise NotImplemented

    def showInput(self, x, y, text='0'):
        self.inputText.text = text
        self.setPosition(x, y)
        if not self.visible:
            self.show()
        desktop.setFocusWidget(self.inputText)
        self.inputText.set_cursor(len(self.inputText.text))

    def closeWindow(self):
        self.clear()
        if self.visible:
            self.hide()


class ItemDestroyMenu(InputWindow):

    def __init__(self):
        super().__init__("Destroy")

    def display(self, trainerId, itemData, x, y):
        self.trainerId = trainerId
        self.itemData = itemData
        self.showInput(x, y)

    def clear(self):
        self.trainerId = 0
        self.itemData = None

    def process(self):
        inputText = self.inputText.text
        try:
            quantity = int(inputText)
        except ValueError:
            self.closeWindow()
            return
        else:
            if self.itemData.flags & ItemFlag.NODESTROY:
                eventManager.notify("onSystemMessage", "This item cannot be destroyed.")
                self.closeWindow()
                return
            if quantity > 0:
                if quantity <= self.itemData.quantity:
                    packetManager.queueSend(cmsg.ItemDelete, self.trainerId, self.itemData.nameId, quantity)
            self.closeWindow()


class ItemSellMenu(InputWindow):

    def __init__(self):
        super().__init__("Sell")

    def display(self, itemData, x, y):
        self.itemData = itemData
        self.showInput(x, y)

    def clear(self):
        self.itemData = None

    def process(self):
        inputText = self.inputText.text
        try:
            quantity = int(inputText)
        except ValueError:
            self.closeWindow()
            return
        else:
            if self.itemData.flags & ItemFlag.NOSELL:
                eventManager.notify("onSystemMessage", "This item cannot be sold.")
                self.closeWindow()
                return
            if quantity > 0:
                if quantity <= self.itemData.quantity:
                    packetManager.queueSend(cmsg.NpcSell, sessionService.npc.id, self.itemData.nameId, quantity)
            self.closeWindow()


ITEM = 0
POKEMON = 1

class ItemBuyMenu(InputWindow):

    def __init__(self):
        super().__init__("Purchase")

    def display(self, itemData: ShopItem, x, y):
        self.itemData = itemData
        self.showInput(x, y)

    def clear(self):
        self.itemData = None

    def process(self):
        inputText = self.inputText.text
        try:
            quantity = int(inputText)
        except ValueError:
            self.closeWindow()
            return
        else:
            if quantity > 0:
                if self.itemData.currency == 0:
                    if sessionService.bag.money >= self.itemData.price * quantity:
                        packetManager.queueSend(cmsg.NpcBuy, ITEM, sessionService.npc.id, self.itemData.nameId, quantity)
                    else:
                        eventManager.notify("onSystemErrorMessage", f"""You don't have enough money to purchase {"these items" if quantity > 1 else "this item"}.""")
                elif sessionService.bag.hasItem(self.itemData.currency, quantity):
                    packetManager.queueSend(cmsg.NpcBuy, ITEM, sessionService.npc.id, self.itemData.nameId, quantity)
                else:
                    eventManager.notify("onSystemErrorMessage", f"""You don't have enough currency to purchase {"these items" if quantity > 1 else "this item"}.""")
            self.closeWindow()


class PokemonBuyMenu(InputWindow):

    def __init__(self):
        super().__init__("Purchase")

    def display(self, pokemonData: ShopPokemon, x, y):
        self.pokemonData = pokemonData
        self.showInput(x, y)

    def clear(self):
        self.pokemonData = None

    def process(self):
        inputText = self.inputText.text
        try:
            quantity = int(inputText)
        except ValueError:
            self.closeWindow()
            return
        else:
            if quantity > 0:
                if self.pokemonData.currency == 0:
                    if sessionService.bag.money >= self.pokemonData.price * quantity:
                        packetManager.queueSend(cmsg.NpcBuy, POKEMON, sessionService.npc.id, self.pokemonData.dexId, quantity)
                    else:
                        eventManager.notify("onSystemErrorMessage", "You don't have enough money to purchase this Pokemon.")
                elif sessionService.bag.hasItem(self.pokemonData.currency, quantity):
                    packetManager.queueSend(cmsg.NpcBuy, POKEMON, sessionService.npc.id, self.pokemonData.dexId, quantity)
                else:
                    eventManager.notify("onSystemErrorMessage", "You don't have enough currency to purchase this Pokemon.")
            self.closeWindow()


class TradeAddItemMenu(InputWindow):

    def __init__(self):
        super().__init__("Add")

    def display(self, itemData, tradeList, x, y):
        self.itemData = itemData
        self.tradeList = tradeList
        self.showInput(x, y)

    def clear(self):
        self.itemData = None
        self.tradeList = None

    def process(self):
        inputText = self.inputText.text
        try:
            quantity = int(inputText)
        except ValueError:
            self.closeWindow()
            return
        else:
            if self.itemData.flags & ItemFlag.NOTRADE:
                eventManager.notify("onSystemMessage", "This item cannot be traded.")
                self.closeWindow()
                return
            else:
                if quantity > 0:
                    if quantity <= self.itemData.quantity:
                        if self.itemData.nameId in self.tradeList:
                            if self.tradeList[self.itemData.nameId] + quantity > self.itemData.quantity:
                                self.closeWindow()
                                return
                        packetManager.queueSend(cmsg.TradeItem, 0, self.itemData.nameId, quantity)
            self.closeWindow()


class TradeDeleteItemMenu(InputWindow):

    def __init__(self):
        super().__init__("Remove")

    def display(self, itemData, x, y):
        self.itemData = itemData
        self.showInput(x, y)

    def clear(self):
        self.itemData = None

    def process(self):
        inputText = self.inputText.text
        try:
            quantity = int(inputText)
        except ValueError:
            self.closeWindow()
            return
        else:
            if quantity > 0:
                if quantity <= self.itemData.quantity:
                    packetManager.queueSend(cmsg.TradeItem, 1, self.itemData.nameId, quantity)
            self.closeWindow()


class StorageMoveMenu(InputWindow):

    def __init__(self):
        super().__init__("Storage Box")

    def display(self, storageWindow, fromBox, moveList, x, y):
        self.storageBoxes = storageWindow.boxes
        self.storageWindow = storageWindow
        self.fromBox = fromBox
        self.moveList = moveList
        self.showInput(x, y, text="# or Name")

    def clear(self):
        self.storageBoxes = None
        self.fromBox = None
        self.moveList = None

    def process(self):
        inputText = self.inputText.text
        try:
            toBoxId = int(inputText)
        except ValueError:
            toBoxId = self.storageWindow.boxNameToStorage(self.inputText.text)
            if not toBoxId:
                eventManager.notify("onSystemMessage", "That box name was not found.")
                self.closeWindow()
                return

        if self.fromBox.boxId == toBoxId:
            eventManager.notify("onSystemMessage", "You cannot move Pokemon to the same box.")
            self.closeWindow()
            return
        if toBoxId < 1 or toBoxId > 10:
            eventManager.notify("onSystemMessage", "That box ID is not valid. (1-10)")
            self.closeWindow()
            return
        try:
            size = self.storageBoxes[toBoxId].getSize()
            if size > 20 or size + len(self.moveList) > 20:
                eventManager.notify("onSystemMessage", "Not enough space to move that many Pokemon.")
                self.closeWindow()
                return
        except KeyError:
            pass

        packer = RawPacker()
        packer.pack("!BHBBB", cmsg.StorageMove, sessionService.npcId, self.fromBox.boxId, toBoxId, len(self.moveList))
        for pkmnId in self.moveList:
            packer.pack("!H", pkmnId)

        eventManager.notify("onSendRawPacket", packer.packet)
        self.closeWindow()


class InputMenu:

    def __init__(self):
        self.storageMove = StorageMoveMenu()
        self.itemDestroy = ItemDestroyMenu()
        self.itemSell = ItemSellMenu()
        self.itemBuy = ItemBuyMenu()
        self.pokemonBuy = PokemonBuyMenu()
        self.tradeAdd = TradeAddItemMenu()
        self.tradeDelete = TradeDeleteItemMenu()

    def reset(self):
        self.storageMove.clear()
        self.storageMove.forceHide()
        self.itemDestroy.clear()
        self.itemDestroy.forceHide()
        self.itemSell.clear()
        self.itemSell.forceHide()
        self.itemBuy.clear()
        self.itemBuy.forceHide()
        self.pokemonBuy.clear()
        self.pokemonBuy.forceHide()
        self.tradeAdd.clear()
        self.tradeAdd.forceHide()
        self.tradeDelete.clear()
        self.tradeDelete.forceHide()


inputMenu = InputMenu()
