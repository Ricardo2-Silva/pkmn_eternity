# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\data\gui\group.py
"""
Created on 25 nov. 2011

@author: Kami
"""
from shared.container.constants import PlayerStatus

class GroupData:

    def __init__(self):
        self.groupId = 0
        self.lootMode = 0
        self.expMode = 0
        self.leaderId = 0
        self.clientId = 0
        self.members = {}

    @property
    def count(self):
        return len(self.members)

    def leave(self):
        self.members.clear()

    def inGroup(self):
        return self.count > 0

    def addMember(self, member):
        self.members[member.trainerId] = member

    def delMember(self, member):
        del self.members[member.trainerId]

    def isLeader(self, trainerId):
        return self.leaderId == trainerId

    def isGroupLeader(self):
        return self.isLeader(self.clientId)

    def memberExists(self, trainerId):
        return trainerId in self.members

    def getMemberByName(self, trainerName):
        for member in self.members.values():
            if member.name == trainerName:
                return member

        return False

    def getMember(self, trainerId):
        return self.members.get(trainerId)

    def canInviteMember(self, trainerId):
        if self.inGroup():
            if self.memberExists(trainerId):
                return False
            return self.isGroupLeader() or False
        else:
            return True


class GroupMember:
    trainerId = 0
    name = "Unknown"
    mapId = 0
    status = 0

    def setStatus(self, status, mapId):
        if status < 4:
            self.status = status
        elif status == PlayerStatus.MAPCHANGE:
            self.mapId = mapId

    def __repr__(self):
        return f"GroupMember(id={self.trainerId}, name={self.name})"
