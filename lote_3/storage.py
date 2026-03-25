# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\net\world\parse\storage.py
from client.control.events.event import eventManager
from shared.controller.net.packetStruct import RawUnpacker
from client.control.service.session import sessionService
from shared.container.constants import IdRange
from client.data.container.char import charContainer
from client.interface.npc.storage import storage

def StorageBoxOpen(data):
    storage.onReceivedStorage(data)


def StorageWithdraw(data):
    _, pokemonId, lineupId = data
    pkmnData = charContainer.getDataById(pokemonId, IdRange.PC_POKEMON)
    pkmnData.lineupId = lineupId
    eventManager.notify("onPokemonReceived", pkmnData)


def StoragePreview(data):
    _, pokemonId = data
    pkmnData = charContainer.getDataById(pokemonId, IdRange.PC_POKEMON)
    eventManager.notify("onPokemonShow", pkmnData)


def StorePokemon(data):
    _, pokemonId, boxId = data
    pokemonData = charContainer.getDataById(pokemonId, IdRange.PC_POKEMON)
    eventManager.notify("onPokemonDelete", pokemonId)
    storage.onStorePokemon(pokemonData, boxId)


def StorageOpen(data):
    _, npcId = data
    sessionService.npcId = npcId
    storage.openStorage()


def StorageMove(data):
    unpack = RawUnpacker(data)
    _, fromBox, toBox, pkmnCount = unpack.get("!BBBB")
    idsList = []
    for _ in range(pkmnCount):
        charId = unpack.get("!I")
        idsList.append(charId)

    storage.onStorageMove(fromBox, toBox, idsList)
