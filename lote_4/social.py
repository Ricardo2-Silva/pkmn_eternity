# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\data\gui\social.py
"""
Created on Nov 27, 2011

@author: Ragnarok
"""
from shared.container.constants import PlayerStatus
from client.control.service.session import sessionService

class SocialData:

    def __init__(self):
        self.groupId = 0
        self.lootMode = 0
        self.expMode = 0
        self.leaderId = 0
        self.clientId = 0
        self.friends = {}
        self.ignored = {}

    def reset(self):
        self.__init__()

    def addFriend(self, friend):
        self.friends[friend.trainerId] = friend

    def addIgnored(self, friend):
        self.ignored[friend.trainerId] = friend

    def delFriend(self, trainerId):
        del self.friends[trainerId]

    def delIgnored(self, trainerId):
        del self.ignored[trainerId]

    def friendExists(self, trainerId):
        return trainerId in self.friends

    def ignoreExists(self, trainerId):
        return trainerId in self.ignored

    def getFriend(self, trainerId):
        return self.friends.get(trainerId)

    def getIgnored(self, trainerId):
        return self.ignored.get(trainerId)

    def getFriends(self):
        return list(self.friends.values())

    def getIgnoreds(self):
        return list(self.ignored.values())

    def canIgnore(self, trainerId):
        if self.ignoreExists(trainerId):
            return False
        else:
            return True

    def canFriend(self, trainerId):
        if self.friendExists(trainerId):
            return False
        else:
            if trainerId == sessionService.trainer.data.id:
                return False
            return True

    def isFriendByName(self, trainer):
        for friend in self.friends.values():
            if friend.name.lower() == trainer.lower():
                return True

        return False

    def isIgnoredByName(self, trainer):
        for friend in self.ignored.values():
            if friend.name.lower() == trainer.lower():
                return True

        return False

    def getIgnoredByName(self, trainer):
        for friend in self.ignored.values():
            if friend.name.lower() == trainer.lower():
                return friend

        return


class FriendData:
    trainerId = 0
    name = "Unknown."
    mapId = 0
    status = 0
    flags = 0

    def setStatus(self, status, mapId):
        if status < 4:
            self.status = status
        elif status == PlayerStatus.MAPCHANGE:
            self.mapId = mapId
