# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\interface\bag.py
from client.render.cache import textureCache
from client.control.gui import *
from client.game import desktop
import client.data.gui.styleDB as styleDB
from client.control.events.event import eventManager
from client.control.service.session import sessionService
from client.data.DB import itemDB
from client.data.utils.anchor import AnchorType
from shared.container.constants import ItemType, ItemUsage, TargetType
import copy
from shared.container.net import cmsg
from client.control.net.sending import packetManager
from client.control.utils.localization import localeInt
from client.data.settings import gameSettings
import pyglet
from client.scene.manager import sceneManager
from client.interface.inputMenu import inputMenu
from client.data.gui.icon import IconData, IconDataAll
from client.control.gui.desktop import Desktop

class ItemMenu(Menu):

    def __init__(self):
        Menu.__init__(self, desktop)
        self.itemData = None
        self.useBtn = Button(self, style=(styleDB.menuItemStyle), size=(75, 20), text="Use", autosize=(False,
                                                                                                       False))
        self.useBtn.addCallback("onMouseLeftClick", self.useItem)
        self.sellBtn = Button(self, style=(styleDB.menuItemStyle), size=(75, 20), text="Sell", autosize=(False,
                                                                                                         False))
        self.sellBtn.addCallback("onMouseLeftClick", self.sellItem)
        self.cancelBtn = Button(self, style=(styleDB.menuItemStyle), size=(75, 20), text="Cancel", autosize=(False,
                                                                                                             False))
        self.buttons = (
         self.useBtn, self.sellBtn, self.cancelBtn)

    def useItem(self, widget, x, y, modifiers):
        if self.itemData:
            eventManager.notify("onUseItem", self.itemData)

    def sellItem(self, widget, x, y, modifiers):
        if self.itemData:
            inputMenu.itemSell.display(self.itemData, x, y)

    def closeWindow(self):
        if self.visible:
            for button in self.buttons:
                if button.visible:
                    button.hide()

            self.hide()

    def showItem(self, x, y, itemData):
        self.itemData = itemData
        self.populateMenu()
        self.show()
        self.setActive()
        self.setPosition(x, y)

    def populateMenu(self):
        self.hideAllOptions()
        self.add(self.useBtn)
        if sessionService.shop:
            self.add(self.sellBtn)
        self.add(self.cancelBtn)
        self.fitToContent()


class Pocket:

    def __init__(self, bagWindow, pocket):
        self.id = pocket
        self.bagWindow = bagWindow
        self.bg = textureCache.getGuiImage(f"bag/{pocket + 1}_background")
        self.over = textureCache.getGuiImage(f"bag/{pocket + 1}_button_hov")
        self.normal = textureCache.getGuiImage(f"bag/{pocket + 1}_button_reg")
        self.down = textureCache.getGuiImage(f"bag/{pocket + 1}_button_act")
        icon = IconDataAll(self.normal, self.over, self.down, self.down)
        self.button = IconButton((self.bagWindow), icon=icon, iconAnchor=(AnchorType.CENTER), position=(37 + pocket * 32, 3), style=(styleDB.simpleButtonStyle))
        self.button.addCallback("onMouseLeftClick", self.showPocketClick)
        self.pageTable = PageContainer((self.bagWindow), maxCols=6, maxRows=2, position=(8,
                                                                                         46), visible=False)
        self.pageTable.setInternalMargins(6, 7)
        self.pageTable.setNextButtonPosition(35, 100)
        self.pageTable.setBackButtonPosition(6, 100)
        self.pageTable.setPageNumberPosition(72, 103)
        self.pageTable.setLabelSpacing(3)
        self.pageTable.setAutoFit()

    def reset(self):
        self.pageTable.emptyAndDestroy()

    def showPocketClick(self, widget, x, y, modifiers):
        self.showPocket()

    def showPocket(self):
        """Changes currently viewed pocket"""
        if self.id == self.currentPocket:
            return
        oldPocket = self.bagWindow.pockets[self.currentPocket]
        oldPocket.button.setIconNormal(oldPocket.normal)
        oldPocket.button.setIconOver(oldPocket.over)
        if oldPocket.pageTable.visible:
            oldPocket.pageTable.hide()
        self.bagWindow.currentPocket = self.id
        self.bagWindow.info.setPicture(self.bg)
        self.button.setIconNormal(self.down)
        self.button.setIconOver(self.down)
        self.pageTable.show()

    def getButtonById(self, nameId):
        for widget in self.pageTable.datatable.getWidgets():
            if widget.itemData.nameId == nameId:
                return widget

        return

    def addItem(self, nameId):
        button = self.getButtonById(nameId)
        itemData = sessionService.bag.getItemIfAny(nameId)
        if button:
            button.text = f"x{itemData.quantity}"
        else:
            self.addButton(itemData)

    def delItem(self, itemData):
        button = self.getButtonById(itemData.nameId)
        if button:
            if itemData.quantity > 0:
                button.text = text = f"x{itemData.quantity}"
            else:
                self.pageTable.deleteAndDestroy(button)
                self.pageTable.reorganize()

    def dragStart(self, widget, x, y, modifiers):
        eventManager.notify("onCloseTooltip")

    def dragStop(self, widget, droppedOnWidget, x, y, modifiers):
        if isinstance(droppedOnWidget, Button):
            if droppedOnWidget.id == "TradeItem":
                if droppedOnWidget.tradeData:
                    if droppedOnWidget.tradeData.full:
                        eventManager.notify("onSystemMessage", "Trade window is currently full.")
                        return
            for nameId in self.bagWindow.tradeList:
                if nameId == widget.itemData.nameId:
                    if self.bagWindow.tradeList[nameId] >= widget.itemData.quantity:
                        return

            inputMenu.tradeAdd.display(widget.itemData, self.bagWindow.tradeList, x, y)
        elif droppedOnWidget.id == "Hotbar":
            droppedOnWidget.assignNewItem(widget.itemData)
        elif droppedOnWidget.id == "PokemonParty" and droppedOnWidget.pkmnData:
            pass
        if droppedOnWidget.pkmnData.heldNameId == 0:
            if sessionService.trade:
                eventManager.notify("onSystemMessage", "You cannot perform this action while in a trade.")
                return
            packetManager.queueSend(cmsg.ItemEquip, droppedOnWidget.pkmnData.id, widget.itemData.nameId)
        elif isinstance(droppedOnWidget, Window):
            if droppedOnWidget.id == "Trade":
                if droppedOnWidget.client.full:
                    eventManager.notify("onSystemMessage", "The trade window is currently full.")
                    return
                inputMenu.tradeAdd.display(widget.itemData, [], x, y)
        elif isinstance(droppedOnWidget, Desktop):
            if sessionService.trade:
                return
            inputMenu.itemDestroy.display(sessionService.getClientId(), widget.itemData, x, y)

    def createButtons(self, show=False):
        for itemData in sessionService.bag.getItems():
            if itemData.type == self.id:
                self.addButton(itemData)

    def addButton(self, itemData):
        button = IconButton((self.pageTable), icon=(textureCache.getItemIcon(itemDB.getItemGraphic(itemData.nameId))),
          style=(styleDB.itemButtonStyle),
          size=(46, 38),
          autosize=(False, False),
          text=f"x{itemData.quantity}",
          draggable=True)
        button.id = "Bag"
        button.itemData = itemData
        button.addCallback("onMouseDragBegin", self.dragStart)
        button.addCallback("onWidgetDroppedOn", self.dragStop)
        button.addCallback("onMouseOver", self.showTooltip, itemData)
        button.addCallback("onMouseLeave", self.hideTooltip)
        button.addCallback("onMouseRightClick", self.showItemMenu, itemData)
        self.pageTable.add(button)

    def showItemMenu(self, widget, x, y, modifiers, itemData):
        eventManager.notify("onCloseTooltip")
        self.bagWindow.itemMenu.showItem(x, y, itemData)

    def showTooltip(self, widget, x, y, itemData):
        eventManager.notify("onShowTooltip", itemData, x, y)

    def hideTooltip(self, widget):
        eventManager.notify("onCloseTooltip")

    @property
    def currentPocket(self):
        return self.bagWindow.currentPocket


class BagWindow(Window):

    def __init__(self, tradeList):
        Window.__init__(self, desktop, position=(AnchorType.CENTER), size=(322, 183), autosize=(False,
                                                                                                False), draggable=True, style=(styleDB.windowNoBgStyle), visible=False)
        self.setManualFit()
        self.tradeList = tradeList
        self.pockets = {}
        self.itemMenu = ItemMenu()
        self.bgimg = textureCache.getGuiImage("bag/template")
        self.info = Picture(self, position=(0, 33))
        self.bgbtn = Picture(self, picture=(self.bgimg), position=(0, 0))
        self.signLbl = Label(self, position=(130, 148), text="$")
        self.moneyLbl = Label(self, position=(134, 148), size=(100, 20), text=(localeInt(sessionService.bag.money)), autosize=(False,
                                                                                                                               False))
        self.moneyLbl.setTextAnchor(AnchorType.RIGHT)
        for x in range(0, 8):
            self.pockets[x] = Pocket(self, x)

        self.closeBtn = Button(self, position=(253, 143), size=(64, 26), autosize=(False,
                                                                                   False), text="Close", style=(styleDB.cancelButtonStyle))
        self.closeBtn.addCallback("onMouseLeftClick", self.closeWindow)
        self.currentPocket = ItemType.MEDICINE
        self.fitToContent()

    def reset(self):
        self.currentPocket = ItemType.MEDICINE
        for pocket in self.pockets.values():
            pocket.reset()

        eventManager.notify("onCloseTooltip")
        if self.visible:
            self.hide()

    def updateMoney(self):
        self.moneyLbl.text = localeInt(sessionService.bag.money)

    def closeWindow(self, widget, x, y, modifiers):
        self.hide()


class Bag:

    def __init__(self):
        eventManager.registerListener(self)
        self.tradeList = {}
        self.window = BagWindow(self.tradeList)
        self.showPocket(ItemType.ITEMS)
        self.blank = textureCache.getItemIcon(0)

    def reset(self):
        self.tradeList.clear()
        self.window.reset()

    def onHotkeyPress(self, hotkeyName):
        if hotkeyName == "bag":
            if self.window.visible:
                self.window.hide()
            else:
                self.window.show()

    def onUseItem(self, item):
        if sessionService.ticks.canUseItem():
            itemData = itemDB.getItem(item.nameId)
            if not itemData:
                raise Exception("Somehow... itemData doesn't exist.")
            if sessionService.battle:
                flag = itemData.useInBattle
            else:
                flag = itemData.useOutBattle
            if flag & ItemUsage.NONE:
                print("Unuseable item.")
                return
        if itemData.target & TargetType.NOTARGETS or itemData.target == 0:
            print("Requires no Target to use.")
            targetData = sessionService.getClientData()
            if itemDB.canUse(targetData, itemData.id):
                packetManager.queueSend(cmsg.ItemUse, targetData.id, targetData.idRange, itemData.nameId)
        elif itemData.target & TargetType.COORDINATES or itemData.target & TargetType.POKEMON:
            print("Requires a target.")
            eventManager.notify("onTargetMode", item, closeAfter=True)
        else:
            print("No valid target for item.")

    def onBagReceived(self):
        for pocket in self.window.pockets.values():
            pocket.pageTable.setManualFit()
            pocket.createButtons()
            pocket.pageTable.fitToContent()
            pocket.pageTable.setAutoFit()

        self.window.updateMoney()

    def showPocket(self, pocket):
        self.window.pockets[pocket].showPocket()

    def onReceivedMoney(self, money):
        self.window.updateMoney()

    def onItemAdd(self, nameId, quantity):
        itemData = sessionService.bag.getItemIfAny(nameId)
        self.window.pockets[itemData.type].addItem(nameId)

    def onItemDelete(self, itemData, nameId):
        self.window.pockets[itemData.type].delItem(itemData)

    def onTradeItemAdd(self, trainerId, itemData):
        nameId = itemData.nameId
        quantity = itemData.quantity
        if nameId in self.tradeList:
            self.tradeList[nameId] += quantity
        else:
            self.tradeList[nameId] = quantity

    def onTradeItemDelete(self, trainerId, itemData):
        nameId = itemData.nameId
        quantity = itemData.quantity
        if nameId in self.tradeList:
            self.tradeList[nameId] -= quantity
        if self.tradeList[nameId] < 1:
            del self.tradeList[nameId]

    def onTradeFinish(self, response):
        if response == 3 or response == 2:
            self.tradeList.clear()


bag = Bag()
