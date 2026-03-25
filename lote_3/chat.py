# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\gui\chat.py
"""
Created on 22 oct. 2011

@author: Kami
"""
from client.control.events.event import eventManager
from shared.container.constants import ChatMessageType, IdRange
from client.data.utils.color import Color
from client.data.container.char import charContainer
import random

class ChatMessageController:

    def __init__(self):
        eventManager.registerListener(self)

    def displayMessage(self, char, messageType, message):
        if messageType == ChatMessageType.PARTY:
            char.getChatMessage().setTextColor(Color.LIGHT_BLUE)
        else:
            char.getChatMessage().setTextColor(Color.WHITE)
        char.getChatMessage().text = f"{char.name}: {message}"


chatMessageController = ChatMessageController()

class InteractiveCharMessages:

    def __init__(self):
        eventManager.registerListener(self)

    def _makeCharSpeak(self, char, message):
        eventManager.notify("onMakeCharSpeak", char, message)
        char.getChatMessage().text = message

    def onPokemonRecall(self, char):
        if char.data.idRange == IdRange.NPC_BATTLE_PKMN:
            trainer = charContainer.getCharByIdIfAny(char.data.trainerId, IdRange.NPC_CHARACTER)
            if trainer:
                self._makeCharSpeak(trainer, random.choice(recallMessages).format(char.data.name))

    def onPokemonRelease(self, trainer, pokemon, x, y):
        if trainer.data.idRange == IdRange.NPC_CHARACTER:
            self._makeCharSpeak(trainer, random.choice(releaseMessages).format(pokemon.data.name))
        return


releaseMessages = ('Go, {0}!', "Let's go, {0}!", 'I choose you, {0}!')
recallMessages = ('Well done {0}. Return.', 'Return {0}.', 'Oh no!')
interactiveCharMessages = InteractiveCharMessages()
