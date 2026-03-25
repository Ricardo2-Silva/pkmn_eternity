# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\net\world\parse\chat.py
import struct
from shared.service.utils import nullstrip
from client.data.container.char import charContainer
from shared.container.constants import Emotes, NameLength
from client.interface.social import friendsList
from client.interface.chat.chat import chat

def JoinChat(data):
    _, channelId, chanName = data
    chanName = nullstrip(chanName)
    chat.onJoinChannel(channelId, chanName)


def LeaveChat(data):
    _, channelId = data
    chat.onLeaveChannel(channelId)


def ChatMessage(data):
    _, messageType, trainerName, channelId = struct.unpack(f"!BB{NameLength.TRAINER}sB", data[:3 + NameLength.TRAINER])
    trainerName = nullstrip(trainerName)
    message = data[3 + NameLength.TRAINER:].decode("utf8")
    if len(message) < 1:
        return
    if friendsList.data.ignoreExists(trainerName):
        return
    chat.onReceivedMessage(trainerName, channelId, messageType, message)


def ChatMessageArea(data):
    _, charId, idRange = struct.unpack("!BIB", data[:6])
    message = data[6:].decode("utf8")
    if len(message) < 1:
        return
    if friendsList.data.ignoreExists(charId):
        return
    chat.onAreaReceivedMessage(charId, idRange, message)


def ShowEmote(data):
    _, charId, idRange, emoteId = data
    char = charContainer.getCharById(charId, idRange)
    try:
        char.emote(Emotes.ALL[emoteId])
    except ValueError:
        print(f"Emote Id: {emoteId} was not found.")
