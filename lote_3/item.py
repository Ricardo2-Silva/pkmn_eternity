# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\net\world\parse\item.py
from client.control.events.event import eventManager
from client.control.service.session import sessionService
from client.data.world.item import ItemData, WorldItemData, BallData
from client.data.DB import itemDB
from shared.controller.net.packetStruct import RawUnpacker
from shared.container.constants import IdRange, ItemType, MoneyMessage
from client.data.container.char import charContainer
from client.control.world.item import Item, Ball, ItemDrop
from client.control.utils.localization import localeInt
from twisted.internet import reactor
import pyglet

def ItemEquip(data):
    _, pokemonId, nameId = data
    pokemon = charContainer.getDataByIdIfAny(pokemonId, IdRange.PC_POKEMON)
    pokemon.heldNameId = nameId
    eventManager.notify("onItemEquip", pokemon, nameId)


def ItemUnequip(data):
    _, pokemonId = data
    pokemon = charContainer.getDataByIdIfAny(pokemonId, IdRange.PC_POKEMON)
    pokemon.heldNameId = 0
    eventManager.notify("onItemUnequip", pokemon)


def ItemThrow(data):
    _, charId, charIdRange, itemId, nameId, x, y = data
    itemInfo = itemDB.getById(nameId)
    char = charContainer.getCharById(charId, charIdRange)
    if itemInfo.type == ItemType.POKEBALL:
        data = BallData(itemId, nameId, char.getPosition2D())
        data.map = char.data.map
        item = Ball(data)
    else:
        data = WorldItemData(itemId, itemDB.getItemGraphic(nameId), char.getPosition2D())
        data.map = char.data.map
        item = Item(data)
    charContainer.addChar(item)
    char.throw(item, x, y)
    pyglet.clock.schedule_once(item.hide, 15)


def ItemUse(data):
    _, charId, charType, nameId, wasHeld = data
    char = charContainer.getCharByIdIfAny(charId, charType)
    if wasHeld:
        eventManager.notify("onBattleMessage", f"{char.name}'s held item {itemDB.name(nameId)} was triggered and consumed!", log=True)
    elif nameId == 1:
        eventManager.notify("onSystemMessage", "Pokemon will avoid you for 30 seconds.")
        pyglet.clock.schedule_once(_endUse, 30, nameId)
    elif nameId == 2:
        eventManager.notify("onSystemMessage", "Pokemon will avoid you for 60 seconds.")
        pyglet.clock.schedule_once(_endUse, 60, nameId)
    elif nameId == 3:
        eventManager.notify("onSystemMessage", "Pokemon will avoid you for 90 seconds.")
        pyglet.clock.schedule_once(_endUse, 90, nameId)


def _endUse(dt, nameId):
    if nameId == 1:
        eventManager.notify("onSystemMessage", "The repel effect has worn off.")
    elif nameId == 2:
        eventManager.notify("onSystemMessage", "The repel effect has worn off.")
    elif nameId == 3:
        eventManager.notify("onSystemMessage", "The repel effect has worn off.")


def BagInventory(data):
    packer = RawUnpacker(data)
    _, sessionService.bag.money, length = packer.get("!BIB")
    for _ in range(length):
        nameId, quantity, type, sell, flags = packer.get("!HHBHB")
        data = ItemData(nameId)
        data.quantity = quantity
        data.type = type
        data.sell = sell
        data.flags = flags
        sessionService.bag.addItem(data)

    sessionService.bag.isLoaded = True
    eventManager.notify("onBagReceived")


def ItemDelete(data):
    _, nameId, quantity = data
    itemData = sessionService.bag.getItemIfAny(nameId)
    if itemData:
        sessionService.bag.decrQuantity(nameId, quantity)
        if itemData.quantity < 1:
            sessionService.bag.delItem(nameId)
        eventManager.notify("onItemDelete", itemData, nameId)


def ItemAdd(data):
    _, nameId, quantity, type, sell, flags = data
    itemData = sessionService.bag.getItemIfAny(nameId)
    if itemData:
        sessionService.bag.incrQuantity(nameId, quantity)
    else:
        x = ItemData(nameId)
        x.quantity = quantity
        x.type = type
        x.sell = sell
        x.flags = flags
        sessionService.bag.addItem(x)
    eventManager.notify("onItemAdd", nameId, quantity)
    eventManager.notify("onSystemMessage", f"You received {quantity} {itemDB.name(nameId)}.")


def Money(data):
    _, money, message = data
    sessionService.bag.money += money
    eventManager.notify("onReceivedMoney", money)
    if message:
        money_formatted = localeInt(abs(money))
        if message == MoneyMessage.STANDARD:
            if money > 0:
                message = "You received ${}"
            else:
                message = "You lost ${}"
        elif message == MoneyMessage.FLEE_PENALTY:
            message = "You dropped ${} fleeing from battle."
        elif message == MoneyMessage.PLAYER_BET:
            if money > 0:
                message = "You won ${}!"
            else:
                message = "You placed a bet of ${}"
        elif message == MoneyMessage.ALL_FAINT:
            message = "You blacked out and paid ${} in expenses from being rescued."
        elif message == MoneyMessage.SHOP:
            if money > 0:
                message = "You sold items for ${}."
            else:
                message = "You spent ${} shopping."
        elif message == MoneyMessage.TRADE:
            if money > 0:
                message = "You received ${} from trade."
        else:
            message = "You traded away ${}."
        eventManager.notify("onSystemMessage", message.format(money_formatted))


def ItemObject(data):
    _, objId, fileId, mapId, x, y, z, flags = data
    item = charContainer.getCharByIdIfAny(objId, IdRange.NPC_ITEM)
    if item:
        return False
    elif fileId == 0:
        itemData = WorldItemData(objId, "zitems/", (x, y))
        itemData.name = "Container"
        itemData.flags = flags
        obj = ItemDrop(itemData)
    else:
        itemData = WorldItemData(objId, itemDB.getItemGraphic(fileId), (x, y))
        itemData.flags = flags
        obj = Item(itemData)
    charContainer.addChar(obj)
