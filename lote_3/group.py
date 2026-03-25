# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\net\world\parse\group.py
from shared.service.utils import nullstrip
from client.interface.group import groupController

def GroupUpdate(data):
    _, trainerId, result = data
    groupController.onGroupUpdate(trainerId, result)


def GroupInvite(data):
    _, trainerName = data
    trainerName = nullstrip(trainerName)
    groupController.onGroupInvite(trainerName)


def GroupResponse(data):
    _, response = data
    groupController.onGroupResponse(response)


def GroupList(data):
    groupController.onGroupList(data)


def GroupOptions(data):
    _, groupId, lootMode, expMode = data
    groupController.onGroupOptions(groupId, lootMode, expMode)


def GroupAddPlayer(data):
    _, trainerId, name, mapId, onlineStatus = data
    trainerName = nullstrip(name)
    groupController.onGroupAddPlayer(trainerId, trainerName, mapId, onlineStatus)
