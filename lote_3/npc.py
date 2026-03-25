# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\net\world\parse\npc.py
import time
from datetime import datetime
from twisted.internet import defer
from client.control.events import eventManager
from client.data.container.char import charContainer
from client.control.service.session import sessionService
from shared.service.utils import nullstrip
from shared.container.constants import Direction, IdRange, CharCategory, CreatureAction, ObjectFlags
from client.data.world.char import NpcPokemonData, NpcTrainerData, NpcWorldItemData, NpcWorldObjectData
from client.control.world.char import Pokemon, NPCWorldObject, NPCTrainer, NPCPokemon, WildBerryObject
from shared.controller.net.packetStruct import RawUnpacker
from client.data.DB import textDB, mapDB
from client.data.cache import nameCache
from client.control.world.item import WorldItem
from client.interface.npc.dialog import dialog
from client.interface.npc.shop import shop

def ShopList(data):
    shopList = {'items':[],  'pokemon':[]}
    packer = RawUnpacker(data)
    _, npcId, item_size, pokemon_size = packer.get("!BHBB")
    for _ in range(item_size):
        nameId, price, quantity, currency, restockTime = packer.get("!HIBHH")
        shopList["items"].append((nameId, price, quantity, currency, restockTime))

    for _ in range(pokemon_size):
        nameId, price, quantity, currency, restockTime = packer.get("!HIBHH")
        shopList["pokemon"].append((nameId, price, quantity, currency, restockTime))

    npcData = charContainer.getDataByIdIfAny(npcId, IdRange.NPC_CHARACTER)
    npcData.vendor = shopList
    shop.openShop(npcData)


class OptionData:

    def __init__(self, number, icon, text):
        self.number = number
        self.icon = icon
        self.text = text


def NpcDialogMessage(data):
    up = RawUnpacker(data)
    _, npcId, npcIdRange, textId, closeType, optionCount = up.get("!BHBHBB")
    options = []
    if optionCount:
        for _ in range(optionCount):
            number, icon = up.get("!BB")
            text = up.getString()
            options.append(OptionData(number, icon, text))

    message = textDB.get(textId)
    if not message:
        message = up.getString(fmt="H")
        textDB.store(textId, message)
    sessionService.npc = charContainer.getDataByIdIfAny(npcId, npcIdRange)
    dialog.receivedDialog(message, closeType, options)


def DialogTextQuery(data):
    upack = RawUnpacker(data)
    _, textId = upack.get("!BH")
    message = upack.getString(fmt="H")
    textDB.store(textId, message)


def Npc(data):
    _, charId, idRange, category, name, fileId, walkingSpeed, mapId, x, y, z, flags, action, facing, questStatus = data
    name = nullstrip(name)
    fileId = nullstrip(fileId)
    data = charContainer.getDataByIdIfAny(charId, idRange)
    if not data:
        if category == CharCategory.TRN:
            data = NpcTrainerData()
            data.fileId = fileId
            data.name = name
        elif category == CharCategory.POKEMON:
            data = NpcPokemonData()
            data.dexId = int(fileId)
            data.fileId = fileId
            data.name = name
    elif category == CharCategory.ITEM:
        data = NpcWorldItemData()
        data.fileId = int(fileId)
        data.name = name
    data.id = charId
    data.idRange = idRange
    data.category = category
    data.walkingSpeed = walkingSpeed
    data.map = mapDB.getById(mapId)
    data.x = x
    data.y = y
    data.z = z
    data.action = action
    data.facing = Direction.toDeg[facing]
    data.originalFacing = Direction.toDeg[facing]
    data.flags = flags
    data.dialogStatus = questStatus
    if category == CharCategory.TRN:
        char = NPCTrainer(data)
    elif category == CharCategory.POKEMON:
        char = NPCPokemon(data)
    else:
        if category == CharCategory.ITEM:
            char = WorldItem(data)
    charContainer.addChar(char)
    if name:
        nameCache.setPlayer(charId, idRange, name)


def NpcClose(data):
    dialog.dialogClose()


def NpcWorldObject(data):
    _, objId, idRange, name, fileId, mapId, x, y, z, flags, questStatus, order = data
    name = nullstrip(name)
    fileId = nullstrip(fileId)
    data = charContainer.getDataByIdIfAny(objId, idRange)
    if not data:
        data = NpcWorldObjectData()
    data.id = objId
    data.idRange = idRange
    data.fileId = fileId
    data.name = name
    data.map = mapDB.getById(mapId)
    data.x = x
    data.y = y
    data.z = z
    data.flags = flags
    data.renderingOrder = order
    data.dialogStatus = questStatus
    if flags & ObjectFlags.NO_SHADOW:
        data.shadow = False
    if idRange == IdRange.NPC_BERRY:
        if flags == 1:
            data.dropped = True
        else:
            data.dropped = False
        obj = charContainer.getCharByIdIfAny(objId, idRange)
        if not obj:
            if idRange == IdRange.NPC_BERRY:
                obj = WildBerryObject(data)
            else:
                obj = NPCWorldObject(data)
            charContainer.addChar(obj)
    else:
        obj.renderer.restoreState()
    if not obj.visible:
        obj.show()
    obj.setPosition(x, y, z)

    def setOnFloor(_):
        data.renderingOrder = 0
        obj.renderer.updatePosition()

    d = defer.Deferred()
    d.addCallback(setOnFloor)
    obj.event = d


def RebattleTimer(data):
    _, npcId, npcIdRange, timestamp, state = data
    end = datetime.fromtimestamp(timestamp)
    start = datetime.fromtimestamp(time.time())
    td = end - start
    timestring = f"{td.days} day(s) {td.seconds // 3600} minute(s) {td.seconds // 60 % 60} second(s)."
    eventManager.notify("onSystemMessage", f"You have already battled this trainer, you can rebattle in {timestring}.")
