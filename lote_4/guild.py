# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\data\gui\guild.py
"""
Created on Nov 27, 2011

@author: Ragnarok
"""
from shared.container.constants import PlayerStatus, GuildPermissions
MAX_RANKS = 8

class GuildData:

    def __init__(self):
        self.clientId = 0
        self.id = 0
        self.name = ""
        self.leaderId = 0
        self.members = {}
        self.ranks = {}
        self.motd = ""
        self.createdate = 0

    def leave(self):
        self.members.clear()
        self.ranks.clear()

    def addMember(self, member):
        self.members[member.trainerId] = member

    def delMember(self, member):
        del self.members[member.trainerId]

    def memberExists(self, trainerId):
        return trainerId in self.members

    def getMember(self, trainerId):
        return self.members.get(trainerId)

    def getMembers(self):
        return list(self.members.values())

    def addRank(self, rank):
        self.ranks[rank.id] = rank

    def delRank(self, rankId):
        del self.ranks[rankId]

    def rankExists(self, rankId):
        return rankId in self.ranks

    def getRank(self, rankId):
        return self.ranks.get(rankId)

    def getRanks(self):
        return list(self.ranks.values())

    def promote(self, member):
        member.rank = self.getRank(member.rank.id - 1)

    def demote(self, member):
        member.rank = self.getRank(member.rank.id + 1)

    def isLeader(self, trainerId):
        return self.leaderId == trainerId

    def isGuildLeader(self):
        return self.isLeader(self.clientId)

    def inGuild(self):
        return len(self.members) > 0

    def lowestRank(self):
        for x in range(MAX_RANKS):
            if x not in self.ranks:
                return self.ranks[x - 1]

        return

    def onlineCount(self):
        i = 0
        for member in self.members.values():
            if member.status != PlayerStatus.OFFLINE:
                i += 1

        return i

    def hasPermission(self, permission):
        member = self.getMember(self.clientId)
        if member.rank.permissions & permission:
            return True
        else:
            return False

    def canAdjustPlayer(self, member, target):
        if member.rank.id < target.rank.id:
            return True
        else:
            return False

    def canInviteMember(self, trainerId):
        if self.inGuild():
            if self.getMember(trainerId):
                return False
            if self.hasPermission(GuildPermissions.INVITE):
                return True
        return False


class GuildMember:
    trainerId = 0
    name = "Unknown"
    mapId = 0
    status = 0
    rank = None
    note = ""
    lastOnline = 0

    def setStatus(self, status, mapId):
        if status < 4:
            self.status = status
        elif status == PlayerStatus.MAPCHANGE:
            self.mapId = mapId


class GuildRank:

    def __init__(self):
        self.id = 0
        self.name = ""
        self.permissions = 0
