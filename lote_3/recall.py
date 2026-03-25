# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\world\action\recall.py
"""
Created on 30 juil. 2011

@author: Kami
"""
from client.control.events import eventManager
from shared.container.constants import WalkMode
from shared.container.net import cmsg as clientMessage
from client.control.net.sending import packetManager
from client.control.service.session import sessionService
from client.control.events.event import eventDispatcher

class RecallController:
    __doc__ = " Controls pokemon recall"

    def __init__(self):
        eventManager.registerListener(self)

    def isRecallPossible(self, pkmnData):
        if pkmnData.skillStates.inUse():
            eventManager.notify("onBattleMessage", "You cannot recall a Pokemon during a move!", log=False)
            return False
        else:
            return True

    def onRecallAttempt(self, pokemonData):
        """ Check if recall is possible. And if possible, does the action required. (Take out pokemon from charContainer, etc..."""
        if not self.isRecallPossible(pokemonData):
            return
        packetManager.queueSend(clientMessage.PokemonReturn, pokemonData.id)

    def recall(self, char):
        if not char.isReleased():
            raise AssertionError(f"This char is already recalled or not released {char.data.name}")
        else:
            char.stopMoving()
            if char.followTarget:
                char.stopFollow()
            char.setReleased(False)
            if char.visible:
                char.recall()
            selectChar = char in sessionService.getClientChars()
            if sessionService.getSelectedChar() == char:
                eventDispatcher.dispatch_event("onCharSelection", sessionService.trainer)

    def onPokemonRecall(self, char):
        self.recall(char)


recallController = RecallController()
