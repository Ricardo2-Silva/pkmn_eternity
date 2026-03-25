# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\interface\npc\shop.py
"""
Created on Jul 30, 2011

@author: Ragnarok
"""
from client.control.gui import Window, Button, IconButton, PageContainer, Label
from client.data.gui.shop import ShopItem, ShopPokemon
from client.game import desktop
from client.render.cache import textureCache
from client.control.events.event import eventManager
from client.data.gui import styleDB
from client.data.DB import itemDB, pokemonDB
from client.data.utils.anchor import AnchorType
from client.control.service.session import sessionService
from client.control.utils.localization import localeInt
from client.interface.inputMenu import inputMenu
from client.control.gui.tables import PageDatatable
import random

class ShopPageContainer(PageContainer):

    def __init__(self, parent, maxCols=3, maxRows=3, position=(0, 0), size=(0, 0), draggable=False, visible=True, slash=True, spacePadding=1):
        PageContainer.__init__(self, parent, maxCols, maxRows, position, size, draggable, visible, slash, spacePadding)
        self.entryTable = PageDatatable(self, maxRows, maxCols, position=(position[0] + 20, position[1] - 9))
        self.entryTable.setInternalMargins(38, 24)
        self.entryTable.setAutoFit()

    def emptyAndDestroy(self):
        PageContainer.emptyAndDestroy(self)
        self.entryTable.emptyAndDestroy()

    def add(self, widget, row=None, col=None):
        """ Currency type of 0 is money. Anything higher becomes an item. """
        PageContainer.add(self, widget, row=None, col=None)
        if widget.itemData:
            data = widget.itemData
        else:
            if widget.pokemonData:
                data = widget.pokemonData
        price = localeInt(data.price)
        marker = "$" if data.currency == 0 else ""
        label_price = f"{marker}{price}"
        button = IconButton((self.entryTable), iconAnchor=(AnchorType.CENTERX),
          icon=(textureCache.getItemIcon(data.currency) if data.currency > 0 else None),
          text=label_price,
          size=(90, 16),
          autosize=(False, False),
          enableEvents=False,
          style=(styleDB.transparentButtonStyleRight))
        if data.currency > 0:
            button.setIconSize(16, 16)
        self.entryTable.add(button)
        widget.priceButton = button

    def updateShopItem(self, widget):
        if widget.itemData.restockTime > 0:
            item_name = f"{itemDB.name(widget.itemData.nameId).title()} ({widget.itemData.quantity})"
        else:
            item_name = itemDB.name(itemDB.getItemGraphic(widget.itemData.dexId)).title()
        widget.text = item_name
        priceButton = widget.priceButton
        price = localeInt(widget.itemData.price)
        marker = "$" if widget.itemData.currency == 0 else ""
        priceButton.text = f"{marker}{price}"

    def updateShopPokemon(self, widget):
        if widget.itemData.restockTime > 0:
            item_name = f"{pokemonDB.name(widget.pokemonData.dexId).title()} ({widget.pokemonData.quantity})"
        else:
            item_name = itemDB.name(widget.pokemonData.dexId).title()
        widget.text = item_name
        priceButton = widget.priceButton
        price = localeInt(widget.pokemonData.price)
        marker = "$" if widget.pokemonData.currency == 0 else ""
        priceButton.text = f"{marker}{price}"

    def nextPage(self, widget, x, y, modifiers):
        self.entryTable.nextPage()
        PageContainer.nextPage(self, widget, x, y, modifiers)

    def backPage(self, widget, x, y, modifiers):
        self.entryTable.backPage()
        PageContainer.backPage(self, widget, x, y, modifiers)


class ShopData:

    def __init__(self, window, shopList):
        self.shopTable = ShopPageContainer(window, position=(7, 27), maxCols=2, maxRows=5)
        self.shopTable.setInternalMargins(6, 5)
        self.shopTable.setNextButtonPosition(35, 203)
        self.shopTable.setBackButtonPosition(6, 203)
        self.shopTable.setPageNumberPosition(76, 206)
        self.shopTable.setAutoFit()
        self.shopList = shopList
        self._generateItemButtons(shopList)
        self._generatePokemonButtons(shopList)

    def _generateItemButtons(self, shopList):
        for nameId, price, quantity, currency, restockTime in shopList["items"]:
            if restockTime > 0:
                item_name = f"{itemDB.name(nameId).title()} ({quantity})"
            else:
                item_name = itemDB.name(nameId).title()
            button = IconButton((self.shopTable),
              size=(122, 35),
              style=(styleDB.shopButtonStyle),
              text=item_name,
              autosize=(False, False),
              icon=(textureCache.getItemIcon(itemDB.getItemGraphic(nameId))),
              iconAnchor=(AnchorType.LEFTCENTER))
            button.addCallback("onMouseLeftClick", self.purchaseItem)
            button.addCallback("onMouseRightClick", self.purchaseItem)
            button.itemData = ShopItem(nameId, price, quantity, currency, restockTime)
            button.pokemonData = None
            self.shopTable.add(button)

    def _generatePokemonButtons(self, shopList):
        for dexId, price, quantity, currency, restockTime in shopList["pokemon"]:
            if restockTime > 0:
                item_name = f"{pokemonDB.name(dexId).title()} ({quantity})"
            else:
                item_name = pokemonDB.name(dexId).title()
            button = IconButton((self.shopTable),
              size=(122, 35),
              style=(styleDB.shopButtonStyle),
              text=item_name,
              autosize=(False, False),
              icon=(textureCache.getPokemonIcon(dexId, 0)),
              iconAnchor=(AnchorType.LEFTCENTER))
            button.addCallback("onMouseLeftClick", self.purchasePokemon)
            button.addCallback("onMouseRightClick", self.purchasePokemon)
            button.itemData = None
            button.pokemonData = ShopPokemon(dexId, price, quantity, currency, restockTime)
            self.shopTable.add(button)

    def reset(self):
        self.shopTable.emptyAndDestroy()

    def updateQuantity(self, nameId, quantity):
        for button in self.shopTable.getTableWidgets():
            if button.itemData.nameId == nameId:
                if button.itemData.restockTime > 0:
                    button.itemData.quantity -= quantity
                    self.shopTable.updateShopItem(button)
                break

    def updateShopData(self, newShopData):
        destroy = False
        update = False
        if len(self.shopList["items"]) != len(newShopData["items"]):
            destroy = True
        else:
            update = True
        if len(self.shopList["pokemon"]) != len(newShopData["pokemon"]):
            destroy = True
        else:
            update = True
        if update and not destroy:
            for button in self.shopTable.getTableWidgets():
                for nameId, price, quantity, currency, restockTime in newShopData["items"]:
                    if button.itemData:
                        if button.itemData.nameId == nameId:
                            if button.itemData.price != price or button.itemData.quantity != quantity:
                                button.itemData.price = price
                                button.itemData.quantity = quantity
                                self.shopTable.updateShopItem(button)
                            break

                for dexId, price, quantity, currency, restockTime in newShopData["pokemon"]:
                    if button.pokemonData:
                        if button.pokemonData.dexId == dexId:
                            if button.pokemonData.price != price or button.pokemonData.quantity != quantity:
                                button.pokemonData.price = price
                                button.pokemonData.quantity = quantity
                                self.shopTable.updateShopPokemon(button)
                            break

        if destroy:
            self.shopTable.emptyAndDestroy()
            self._generateItemButtons(newShopData)
            self._generatePokemonButtons(newShopData)
        self.shopList = newShopData

    def purchaseItem(self, widget, x, y, modifiers):
        inputMenu.itemBuy.display(widget.itemData, x, y)

    def purchasePokemon(self, widget, x, y, modifiers):
        inputMenu.pokemonBuy.display(widget.pokemonData, x, y)

    def showShop(self):
        self.shopTable.show()

    def hideShop(self):
        self.shopTable.hide()
        sessionService.npc = None
        sessionService.shop = None


class Shop:

    def __init__(self):
        self.shopData = {}
        self.window = ShopWindow(self)
        eventManager.registerListener(self)

    def reset(self):
        for shopData in self.shopData.values():
            shopData.reset()

        self.shopData.clear()
        self.window.reset()

    def openShop(self, npcData):
        if sessionService.shop:
            return
        else:
            sessionService.npc = npcData
            sessionService.shop = npcData.vendor
            self.window.show()
            self.window.updateMoney()
            if sessionService.npc.id in self.shopData:
                self.shopData[sessionService.npc.id].updateShopData(npcData.vendor)
                self.shopData[sessionService.npc.id].showShop()
            else:
                self.shopData[sessionService.npc.id] = ShopData(self.window, npcData.vendor)

    def currentShop(self):
        return self.shopData[sessionService.npc.id]

    def onItemAdd(self, nameId, quantity):
        if sessionService.shop:
            self.shopData[sessionService.npc.id].updateQuantity(nameId, quantity)

    def onReceivedMoney(self, money):
        if self.window.visible:
            self.window.updateMoney()

    def onClientCharWarp(self, char, mapId, mapX, mapY):
        if self.window.visible:
            self.currentShop().hideShop()
            self.window.hide()


class ShopWindow(Window):

    def __init__(self, control):
        Window.__init__(self, desktop, position=(100, 70), size=(264, 265), draggable=True, visible=False, style=(styleDB.windowsNoStyle))
        self.bgImg = textureCache.getGuiImage("shop/buy")
        self.setBackground(self.bgImg)
        self.control = control
        self.moneyLabel = Label(self, position=(150, 5), size=(100, 0), text="Funds: $ 0", style=(styleDB.shopMoneyLabelStyle))
        self.cancelBtn = Button(self, position=(190, 227), size=(64, 26), autosize=(False,
                                                                                    False), style=(styleDB.cancelButtonStyle), text="Close")
        self.cancelBtn.addCallback("onMouseLeftClick", self.hideWindow)

    def reset(self):
        if self.visible:
            self.hide()

    def updateMoney(self):
        self.moneyLabel.text = f"Funds: $ {localeInt(sessionService.bag.money)}"

    def hideWindow(self, widget, x, y, modifiers):
        self.control.currentShop().hideShop()
        self.hide()


shop = Shop()
