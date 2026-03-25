# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\net\world\parse\guild.py
"""
Created on Aug 11, 2011

@author: Ragnarok
"""
from client.control.events import eventManager
from shared.service.utils import nullstrip
from client.interface.guild import guild

def GuildList(data):
    eventManager.notify("onGuildList", data)


def Invite(data):
    _, trainerName, guildName = data
    trainerName = nullstrip(trainerName)
    guildName = nullstrip(guildName)
    guild.onGuildInvite(trainerName, guildName)


def Response(data):
    _, response = data
    guild.onGuildResponse(response)


def AddPlayer(data):
    guild.onGuildAddPlayer(data)


def Update(data):
    _, trainerId, targetId, event = data
    guild.onGuildUpdate(trainerId, targetId, event)


def Motd(data):
    guild.onGuildMotd(data)


def CreateRank(data):
    _, rankId, rankName, permissions = data
    rankName = nullstrip(rankName)
    guild.onGuildRankAdd(rankId, rankName, permissions)


def RankRename(data):
    _, rankId, rankName = data
    rankName = nullstrip(rankName)
    guild.onGuildRankRename(rankId, rankName)


def RankPermissions(data):
    _, rankId, permissions = data
    guild.onGuildRankPermissions(rankId, permissions)


def SwapRank(data):
    _, sourceRankId, targetRankId = data
    guild.onGuildSwapRank(sourceRankId, targetRankId)


def DeleteRank(data):
    _, rankId = data
    guild.onGuildRankDelete(rankId)
