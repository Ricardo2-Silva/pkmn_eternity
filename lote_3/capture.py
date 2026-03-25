# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\net\world\parse\capture.py
from client.data.container.char import charContainer
from shared.container.constants import IdRange
from client.control.events.event import eventManager
from client.control.world.action.capture import captureController

def PokemonCaptureResult(data):
    """ A pokemon has been captured """
    _, ballid, pkmnid, x, y, z, tremble, result = data
    wild = charContainer.getCharById(pkmnid, IdRange.NPC_WILD_PKMN)
    ball = charContainer.getCharById(ballid, IdRange.NPC_ITEM)
    captureController.onPokemonCaptureResult(wild, ball, x, y, z, tremble, result)
