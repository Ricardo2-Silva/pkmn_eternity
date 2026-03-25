# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\net\world\parse\social.py
from client.control.events.event import eventManager
from client.control.service.session import sessionService
from shared.controller.net.packetStruct import RawUnpacker
from client.data.container.char import charContainer
from client.data.world.char import PcTrainerData
from shared.container.constants import IdRange, FriendResponses
from shared.service.utils import nullstrip
from client.interface.social import friendsList

def FriendStatus(data):
    _, trainerId, status = data


def FriendRequest(data):
    _, charName = data
    charName = nullstrip(charName)
    friendsList.onFriendRequest(charName)


def FriendAdd(data):
    _, trainerId, mapId, status, trainerName = data
    trainerName = nullstrip(trainerName)
    if not charContainer.getDataByIdIfAny(trainerId, IdRange.PC_TRAINER):
        char = PcTrainerData()
        char.id = trainerId
        char.name = trainerName
        charContainer.addData(char)
    friendsList.onFriendAdd(trainerId, trainerName, status, mapId)


def FriendDel(data):
    _, trainerId = data
    friendsList.onFriendRemove(trainerId)


def IgnoreAdd(data):
    _, trainerId, trainerName = data
    trainerName = nullstrip(trainerName)
    if not charContainer.getDataByIdIfAny(trainerId, IdRange.PC_TRAINER):
        char = PcTrainerData()
        char.id = trainerId
        char.name = trainerName
        charContainer.addData(char)
    friendsList.onIgnoreAdd(trainerId, trainerName)


def IgnoreDelete(data):
    _, trainerId = data
    friendsList.onIgnoreRemove(trainerId)


def FriendAck(data):
    _, response = data
    if response == FriendResponses.REQUEST_SENT:
        text = "Friend request sent."
    elif response == FriendResponses.REQUEST_ACCEPTED:
        text = "Friend request accepted."
    elif response == FriendResponses.REQUEST_DENIED:
        text = "Your friend request was rejected."
    elif response == FriendResponses.FRIEND_ALREADY:
        text = "This person is already your friend."
    elif response == FriendResponses.NOT_ONLINE:
        text = "Player could not be found."
    elif response == FriendResponses.FRIEND_BUSY:
        text = "Player is not accepting requests."
    elif response == FriendResponses.OUR_FRIEND_FULL:
        text = "Our friends list is currently full."
    elif response == FriendResponses.CANNOT_ADD:
        text = "Cannot add that person."
    elif response == FriendResponses.NOT_IN_LIST:
        text = "Player is not located in your ignore or friend list."
    elif response == FriendResponses.IGNORE_SUCCESS:
        text = "Player ignored successfully."
    elif response == FriendResponses.IGNORE_REMOVED:
        text = "Player was removed from ignore list."
    elif response == FriendResponses.IGNORE_REMOVED:
        text = "Player was removed from friends list."
    else:
        text = "Unknown Message."
    eventManager.notify("onSystemMessage", text)


def FriendList(data):
    friendsList.onFriendList(data)


def PlayerStatusChange(data):
    _, trainerId, status, value = data
    eventManager.notify("onPlayerStatusChange", trainerId, status, value)
