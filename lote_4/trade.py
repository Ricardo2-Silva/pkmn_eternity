# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\interface\trade.py
"""
Created on Jul 27, 2011

@author: Ragnarok
"""
from client.data.gui.styleDB import blackLabelStyleRight, Style, TextData, Color, ShadowData
from client.data.utils.anchor import AnchorType
from client.control.gui import Window, Button, Label, Datatable, Picture, Textbox, IconButton, PageDatatable
from client.game import desktop
from client.control.events.event import eventManager
from client.render.cache import textureCache
from client.data.gui import styleDB
from client.data.DB import messageDB, itemDB
from shared.container.net import cmsg
from shared.container.constants import TradeResponses, IdRange, TradeFinishing
from client.data.container.char import charContainer
from client.control.service.session import sessionService
from client.control.net.sending import packetManager
from client.interface.inputMenu import inputMenu
T_ITEMS = 0
T_PKMN = 1
CLIENT = 0
PARTNER = 1
BOX_LEFT = (0, 40)
BOX_RIGHT = (210, 40)

class TradeRequestWindow(Window):
    REQUEST_REJECTED = 1
    REQUEST_ACCEPTED = 2

    def __init__(self):
        Window.__init__(self, desktop, position=(AnchorType.CENTER), size=(250, 130), draggable=True, visible=False)
        self.infoLbl = Label(self, position=(AnchorType.CENTER), size=(200, 100), text="", autosize=(False,
                                                                                                     True), multiline=True)
        self.yesBtn = Button(self, position=(5, 80), size=(100, 26), style=(styleDB.greenButtonStyle), text=(messageDB["ACCEPT"]),
          autosize=(False, False))
        self.yesBtn.addCallback("onMouseLeftClick", self.acceptRequest)
        self.noBtn = Button(self, position=(130, 80), size=(100, 26), style=(styleDB.redButtonStyle), text=(messageDB["DENY"]),
          autosize=(False, False))
        self.noBtn.addCallback("onMouseLeftClick", self.denyRequest)

    def reset(self):
        self.forceHide()

    def showRequest(self, name, tradeType):
        self.infoLbl.text = messageDB["TRADE_REQUEST"].format(name)
        self.show()

    def acceptRequest(self, widget, x, y, modifiers):
        packetManager.queueSend(cmsg.TradeResponse, self.REQUEST_ACCEPTED)
        self.hideWindow()

    def denyRequest(self, widget, x, y, modifiers):
        packetManager.queueSend(cmsg.TradeResponse, self.REQUEST_REJECTED)
        self.hideWindow()

    def hideWindow(self):
        self.hide()


class Trade:

    def __init__(self):
        self.window = TradeWindow()
        self.requestWindow = TradeRequestWindow()
        eventManager.registerListener(self)

    def reset(self):
        self.window.reset()
        self.requestWindow.reset()

    def onTradePokemonAdd(self, trainerId, pokemonData):
        if trainerId == sessionService.getClientId():
            self.window.client.addPkmn(pokemonData)
        else:
            self.window.partner.addPkmn(pokemonData)

    def onTradePokemonDelete(self, trainerId, pokemonId):
        if trainerId == sessionService.getClientId():
            self.window.client.delPkmn(pokemonId)
        else:
            self.window.partner.delPkmn(pokemonId)

    def onTradeItemAdd(self, trainerId, itemData):
        if trainerId == sessionService.getClientId():
            self.window.client.addItem(itemData)
        else:
            self.window.partner.addItem(itemData)

    def onTradeItemDelete(self, trainerId, itemData):
        if trainerId == sessionService.getClientId():
            self.window.client.delItem(itemData)
        else:
            self.window.partner.delItem(itemData)

    def onTradeMoney(self, money):
        self.window.partner.txtBox.text = str(money)

    def onTradeRequest(self, trainerName, tradeType):
        self.requestWindow.showRequest(trainerName, tradeType)

    def onTradeResponse(self, trainerId, tradeType, response):
        if response == TradeResponses.REJECTED:
            eventManager.notify("onSystemMessage", messageDB["TRADE_DENIED"])
        elif response == TradeResponses.ACCEPTED:
            partnerData = charContainer.getDataByIdIfAny(trainerId, IdRange.PC_TRAINER)
            if partnerData:
                eventManager.notify("onSystemMessage", messageDB["TRADE_ACCEPTED"])
                self.window.tradeType = tradeType
                self.window.client.setTrade(sessionService.getClientData(), tradeType)
                self.window.partner.setTrade(partnerData, tradeType)
                self.window.startTrade()
            else:
                print("ERROR! We received trade from trainer that no longer exists!")
        elif response == TradeResponses.INTRADE:
            eventManager.notify("onSystemMessage", messageDB["TRADE_EXISTS"])

    def onTradeFinish(self, response):
        if response == TradeFinishing.LOCK:
            self.window.partner.lock()
        elif response == TradeFinishing.CONFIRM:
            self.window.confirmBtn.enableEvents()
        elif response == TradeFinishing.CANCEL:
            eventManager.notify("onSystemMessage", messageDB["TRADE_CANCEL"])
            self.window.closeWindow()
        elif response == TradeFinishing.CANCEL_POKEMON_SPACE:
            eventManager.notify("onSystemMessage", "The trade was cancelled for insufficient party space.")
        elif response == TradeFinishing.COMPLETED:
            eventManager.notify("onSystemMessage", messageDB["TRADE_SUCCESS"])
            self.window.closeWindow()


class TradeData:

    def __init__(self):
        self.pokemon = {}
        self.items = {}
        self.money = 0
        self.oldMoney = 0
        self.locked = False

    @property
    def full(self):
        return len(self.items) + len(self.pokemon) >= 8

    def addPokemonData(self, pokemonData):
        self.pokemon[pokemonData.id] = pokemonData

    def addItemData(self, itemData):
        self.items[itemData.nameId] = itemData

    def delItemData(self, nameId):
        del self.items[nameId]

    def delPokemonData(self, pokemonId):
        del self.pokemon[pokemonId]

    def getPokemon(self, pokemonId):
        try:
            return self.pokemon[pokemonId]
        except Exception:
            return

    def getItem(self, nameId):
        try:
            return self.items[nameId]
        except Exception:
            return

    def wipeTradeData(self):
        self.pokemon = {}
        self.items = {}
        self.money = 0
        self.oldMoney = 0
        self.locked = False


tradeSourceLabel = Style(background=None, text=TextData(color=(Color.WHITE), shadow=(ShadowData(Color.GREY)), anchor=(AnchorType.LEFT)))
tradePartnerLabel = Style(background=None, text=TextData(color=(Color.WHITE), shadow=(ShadowData(Color.BLACK)), anchor=(AnchorType.RIGHT)))

class TradeContainer(TradeData):

    def __init__(self, window):
        TradeData.__init__(self)
        self.window = window
        self.trainerData = None
        self.playerType = ""
        self.nameLbl = Label(window, text="Player", size=(92, 0), style=tradeSourceLabel)
        self.boxPic = Picture(window)
        self.txtBox = Textbox(window, size=(120, 0), text="0")
        self.txtBox.addCallback("onLostFocus", self.changeMoney)
        self.table = PageDatatable(window, maxRows=2, maxCols=4)

    def changeMoney(self, widget):
        if len(self.txtBox.text) < 1:
            self.txtBox.text = "0"
            return
        try:
            money = int(self.txtBox.text)
        except ValueError:
            self.txtBox.text = "0"
            return
        else:
            if money > 2147483647 or money < 0:
                self.txtBox.text = "0"
                return
            else:
                if money > sessionService.bag.money:
                    self.txtBox.text = str(sessionService.bag.money)
                    money = sessionService.bag.money
                if self.oldMoney != money:
                    self.oldMoney = money
                    packetManager.queueSend(cmsg.TradeMoney, money)

    def addPkmn(self, pkmnData):
        self.addPokemonData(pkmnData)
        button = IconButton((self.table), style=(styleDB.simpleButtonStyle), icon=(textureCache.getPokemonIcon(pkmnData.dexId)),
          draggable=(True if isinstance(self, PlayerContainer) else False))
        button.addCallback("onWidgetDroppedOn", self.dragStop)
        button.addCallback("onMouseRightClick", self.showPokemon)
        button.addCallback("onMouseLeftClick", self.showPokemon)
        button.data = pkmnData
        button.id = "TradePokemon"
        button.tradeData = None
        if isinstance(self, PlayerContainer):
            button.tradeData = self
        self.table.add(button)
        self.table.fitToContent()

    def showPokemon(self, widget, x, y, modifiers):
        if widget.data:
            eventManager.notify("onPokemonShow", widget.data)

    def getPokemonButton(self, pkmnId):
        for widget in self.table.getWidgets():
            if widget.id == "TradePokemon":
                if widget.data.id == pkmnId:
                    return widget

        return

    def getItemButton(self, nameId):
        for widget in self.table.getWidgets():
            if widget.id == "TradeItem":
                if widget.data.nameId == nameId:
                    return widget

        return

    def delPkmn(self, pokemonId):
        button = self.getPokemonButton(pokemonId)
        if button:
            self.table.deleteAndDestroy(button)
            self.table.reorganize()
            self.delPokemonData(pokemonId)

    def addItem(self, itemData):
        nameId = itemData.nameId
        quantity = itemData.quantity
        tradeItemData = self.getItem(nameId)
        if tradeItemData:
            tradeItemData.quantity += quantity
            button = self.getItemButton(nameId)
            button.text = f"x{tradeItemData.quantity}"
        else:
            self.addItemData(itemData)
            button = IconButton((self.table), style=(styleDB.itemButtonStyle),
              icon=(textureCache.getItemIcon(itemDB.getItemGraphic(itemData.nameId))),
              text=f"x{itemData.quantity}",
              size=(42, 42),
              autosize=(False, True),
              draggable=(True if isinstance(self, PlayerContainer) else False))
            button.addCallback("onWidgetDroppedOn", self.dragStop)
            button.addCallback("onMouseOver", self.showTooltip, itemData)
            button.addCallback("onMouseLeave", self.hideTooltip)
            button.data = itemData
            button.id = "TradeItem"
            button.tradeData = None
            self.table.add(button)
            self.table.fitToContent()
        if isinstance(self, PlayerContainer):
            button.tradeData = self

    def showTooltip(self, widget, x, y, itemData):
        eventManager.notify("onShowTooltip", itemData, x, y)

    def hideTooltip(self, widget):
        eventManager.notify("onCloseTooltip")

    def dragStop(self, button, widgetDroppedOn, x, y, modifiers):
        if not self.locked:
            if isinstance(self, PlayerContainer):
                dropName = widgetDroppedOn.__class__.__name__
                if dropName == "Desktop":
                    if button.id == "TradeItem":
                        inputMenu.tradeDelete.display(button.data, x, y)
            elif button.id == "TradePokemon":
                packetManager.queueSend(cmsg.TradePokemon, 1, button.data.id)

    def delItem(self, itemData):
        nameId = itemData.nameId
        quantity = itemData.quantity
        tradeItemData = self.getItem(nameId)
        button = self.getItemButton(nameId)
        if tradeItemData:
            tradeItemData.quantity -= quantity
            if tradeItemData.quantity < 1:
                self.table.deleteAndDestroy(button)
                self.table.reorganize()
                self.delItemData(nameId)
            else:
                button.text = f"x{tradeItemData.quantity}"


class PlayerContainer(TradeContainer):

    def __init__(self, window):
        TradeContainer.__init__(self, window)
        self.playerType = "Trade"
        self.boxLeftImg = textureCache.getGuiImage("trade/box_left")
        self.boxLeftLockedImg = textureCache.getGuiImage("trade/box_left_lock")
        self.boxPic.setPicture(self.boxLeftImg)
        self.boxPic.setPosition(0, 40)
        self.nameLbl.setPosition(31, 11)
        self.txtBox.setPosition(45, 130)
        self.table.setPosition(0, 40)

    def resetTrade(self):
        self.wipeTradeData()
        if self.table.eventsEnabled == False:
            self.table.enableEvents()
        self.table.emptyAndDestroy()
        self.boxPic.setPicture(self.boxLeftImg)

    def setTrade(self, trnData, tradeType):
        self.trainerData = trnData
        self.nameLbl.text = trnData.name

    def lock(self):
        if not self.locked:
            self.locked = True
            self.window.id = ""
            self.table.disableEvents()
            self.boxPic.setPicture(self.boxLeftLockedImg)
            packetManager.queueSend(cmsg.TradeConfirm, 0)


class PartnerContainer(TradeContainer):

    def __init__(self, window):
        TradeContainer.__init__(self, window)
        self.boxRightImg = textureCache.getGuiImage("trade/box_right")
        self.boxRightLockedImg = textureCache.getGuiImage("trade/box_right_lock")
        self.boxPic.setPicture(self.boxRightImg)
        self.boxPic.setPosition(210, 40)
        self.nameLbl.setPosition(263, 11)
        self.nameLbl.setStyle(tradePartnerLabel)
        self.txtBox.setPosition(220, 130)
        self.txtBox.disableEvents()
        self.table.setPosition(210, 40)

    def resetTrade(self):
        self.wipeTradeData()
        if self.table.eventsEnabled == False:
            self.table.enableEvents()
        self.table.emptyAndDestroy()
        self.boxPic.setPicture(self.boxRightImg)

    def setTrade(self, trnData, tradeType):
        self.trainerData = trnData
        self.nameLbl.text = trnData.name

    def lock(self):
        if not self.locked:
            self.locked = True
            self.boxPic.setPicture(self.boxRightLockedImg)


class TradeWindow(Window):
    T_ITEMS = 0
    T_PKMN = 1

    def __init__(self):
        Window.__init__(self, desktop, position=(AnchorType.CENTER), size=(384, 201), draggable=True, visible=False, autosize=(True,
                                                                                                                               True),
          style=(styleDB.windowsDefaultStyleNoPadding))
        self.client = PlayerContainer(self)
        self.partner = PartnerContainer(self)
        self.bgImg = textureCache.getGuiImage("trade/background")
        self.setBackground(self.bgImg)
        self.okBtn = Button(self, position=(50, 170), style=(styleDB.blueButtonStyle), text=(messageDB["OK"]))
        self.okBtn.addCallback("onMouseLeftClick", self.lockTrade)
        self.confirmBtn = Button(self, position=(155, 170), style=(styleDB.greenButtonStyle), text=(messageDB["CONFIRM_TRADE"]))
        self.confirmBtn.addCallback("onMouseLeftClick", self.confirmTrade)
        self.confirmBtn.disableEvents()
        self.cancelBtn = Button(self, position=(300, 170), style=(styleDB.redButtonStyle), text=(messageDB["CANCEL"]))
        self.cancelBtn.addCallback("onMouseLeftClick", self.cancelTrade)
        self.id = "Trade"

    def reset(self):
        self.resetTrade()
        self.forceHide()

    def startTrade(self):
        self.id = "Trade"
        sessionService.trade = True
        self.resetTrade()
        self.show()

    def resetTrade(self):
        self.partner.resetTrade()
        self.client.resetTrade()
        if self.confirmBtn.eventsEnabled is True:
            self.confirmBtn.disableEvents()
        if self.okBtn.eventsEnabled is False:
            self.okBtn.enableEvents()

    def lockTrade(self, widget, x, y, modifiers):
        self.client.lock()
        self.okBtn.disableEvents()

    def confirmTrade(self, widget, x, y, modifiers):
        self.confirmBtn.disableEvents()
        packetManager.queueSend(cmsg.TradeConfirm, 1)

    def cancelTrade(self, widget, x, y, modifiers):
        packetManager.queueSend(cmsg.TradeConfirm, 2)

    def closeWindow(self):
        sessionService.trade = False
        self.hide()


trade = Trade()
