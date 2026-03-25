# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\net\world\parse\quest.py
"""
Created on Aug 2, 2011

@author: Ragnarok
"""
from client.control.events.event import eventManager
from client.control.service.session import sessionService
from client.data.container.char import charContainer
from client.interface.npc.quest import quest

def QuestGiverHello(data):
    _, npcId, questId = data
    sessionService.npcId = npcId
    quest.onQuestHello(questId)


def QuestQueryDetails(data):
    quest.onQuestQuery(data)


def QuestAccept(data):
    _, questId = data
    eventManager.notify("onQuestAccept", questId)


def QuestAbandon(data):
    _, questId = data
    quest.onQuestAbandon(questId)


def QuestFail(data):
    _, questId = data
    quest.onQuestFail(questId)


def QuestComplete(data):
    _, questId = data
    eventManager.notify("onQuestComplete", questId)


def QuestRequireUpdate(data):
    _, questId, objectiveId, value = data
    quest.onQuestRequireUpdate(questId, objectiveId, value)


def QuestState(data):
    _, questId, state = data
    quest.onQuestState(questId, state)


def QuestNpcList(data):
    quest.onNpcQuestList(data)


def QuestList(data):
    quest.onQuestList(data)


def NpcQuestStatus(data):
    _, npcId, idRange, state = data
    npcChar = charContainer.getCharByIdIfAny(npcId, idRange)
    if npcChar:
        npcChar.data.dialogStatus = state
        npcChar.showDialogStatus()
    else:
        print("WARNING: Got Quest status for character not in range.")
