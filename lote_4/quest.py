# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\interface\npc\quest.py
"""
Created on Jul 27, 2011

@author: Ragnarok
"""
import sys
from client.control.gui import Window, ScrollableContainer, Button, Label, PageContainer
from client.game import desktop
from client.render.cache import textureCache
from client.data.gui import styleDB
from shared.container.net import cmsg
from shared.container.constants import IdRange, QuestObjectives, QuestStatus, QuestQuery, Element, Gender
from client.control.events.event import eventManager
from client.data.DB import itemDB, pokemonDB
from shared.controller.net.packetStruct import RawUnpacker
from client.control.service.session import sessionService
from client.data.utils.anchor import AnchorType, Alignment
from client.control.net.sending import packetManager
from client.control.utils.localization import localeInt
from client.data.cache import nameCache
from client.control.system.sound import mixerController
from client.interface.npc.dialog import dialog

class ObjectiveInfo(object):

    def __init__(self, id, questId, type):
        self.id = id
        self.questId = questId
        self.type = type
        self.values = []
        self.valueCount = 0

    def __repr__(self):
        return f"ObjectiveInfo(id={self.id}, type={self.type}, values={self.values})"


class Reward:

    def __init__(self, questId, type, value, amount):
        self.questId = questId
        self.type = type
        self.value = value
        self.amount = amount
        self.playerCount = 0


class QuestData:
    id = 0
    timeLimit = 0
    flags = 0
    title = "Unknown"
    details = "Unknown"
    objective = "Unknown"
    progress = "Unknown"
    reward = "Unknown"
    complete = "Unknown"
    end = "Unknown"
    acceptItem = {}
    acceptPokemon = 0
    acceptEventId = 0
    endEventId = 0
    status = QuestStatus.NONE
    requiredState = 0
    abandonAllowed = True

    def __init__(self):
        self.objectives = []
        self.rewards = []
        self.state = 0

    def addObjective(self, objective):
        self.objectives.append(objective)

    def needsRequirement(self):
        if self.status == QuestStatus.INCOMPLETE:
            if self.title == "Unknown":
                return True
        return False

    def needsReward(self):
        if self.status == QuestStatus.COMPLETE:
            if self.reward == "Unknown":
                return True
        return False


class Quest:

    def __init__(self):
        self.questData = {}
        self.window = QuestJournal(self)
        eventManager.registerListener(self)

    def reset(self):
        self.questData.clear()
        self.window.reset()

    def getQuest(self, questId) -> QuestData:
        return self.questData.get(questId)

    def onHotkeyPress(self, hotkeyName):
        if hotkeyName == "questjournal":
            self.window.toggle()

    def onQuestHello(self, questId):
        questId = questId
        questData = self.getQuest(questId)
        if not questData:
            packetManager.queueSend(cmsg.QuestDetailsQuery, sessionService.npc.id, sessionService.npc.idRange, questId, QuestQuery.DETAILS)
        else:
            if questData.details == "":
                packetManager.queueSend(cmsg.QuestDetailsQuery, sessionService.npc.id, sessionService.npc.idRange, questId, QuestQuery.DETAILS)
                return
            if questData.needsRequirement():
                packetManager.queueSend(cmsg.QuestDetailsQuery, sessionService.npc.id, sessionService.npc.idRange, questId, QuestQuery.REQUIREMENTS)
            elif questData.needsReward():
                packetManager.queueSend(cmsg.QuestDetailsQuery, sessionService.npc.id, sessionService.npc.idRange, questId, QuestQuery.REWARD)
            elif questData.status == QuestStatus.NONE:
                dialog.window.setQuestHello(questData)
            elif questData.status == QuestStatus.INCOMPLETE:
                dialog.window.setQuestIncomplete(questData)
            elif questData.status == QuestStatus.COMPLETE:
                dialog.window.setQuestComplete(questData)

    def onNpcQuestList(self, data):
        packer = RawUnpacker(data)
        startList = []
        endList = []
        _, npcId, npcIdRange, startQuestSize, endQuestSize = packer.get("!BHBBB")
        dialog.window.setNpc(npcId, npcIdRange)
        for _ in range(startQuestSize):
            questId = packer.get("B")
            questTitle = packer.getString()
            questData = self.getQuest(questId)
            if not questData:
                questData = QuestData()
                self.questData[questId] = questData
            questData.id = questId
            questData.title = questTitle
            startList.append(questData)

        for _ in range(endQuestSize):
            questId = packer.get("B")
            questTitle = packer.getString()
            questData = self.getQuest(questId)
            if not questData:
                questData = QuestData()
                self.questData[questId] = questData
            questData.id = questId
            questData.title = questTitle
            endList.append(questData)

        if dialog.window.visible:
            dialog.window.addQuestList(startList, endList)

    def onQuestQuery(self, data):
        packer = RawUnpacker(data)
        _, npcId, npcIdRange, questId, detailsType = packer.get("!BHBHB")
        questData = self.getQuest(questId)
        dialog.window.setNpc(npcId, npcIdRange)
        if not questData:
            questData = QuestData()
            self.questData[questId] = questData
        else:
            questData.id = questId
            if detailsType == QuestQuery.DETAILS:
                questData.details = packer.getString(fmt="H")
                dialog.window.setQuestHello(questData)
            elif detailsType == QuestQuery.REQUIREMENTS:
                questData.abandonAllowed = bool(packer.get("!?"))
                questData.title = packer.getString()
                questData.details = packer.getString(fmt="H")
                questData.complete = packer.getString(fmt="H")
                questData.objective = packer.getString()
                questData.requiredState = packer.get("B")
                objectiveCount = packer.get("B")
                for _ in range(objectiveCount):
                    objectiveType, valueLength = packer.get("BB")
                    objectiveData = ObjectiveInfo(len(questData.objectives), questId, objectiveType)
                    for _ in range(valueLength):
                        objectiveData.values.append(packer.get("H"))

                    questData.objectives.append(objectiveData)

            elif detailsType == QuestQuery.REWARD:
                questData.reward = packer.getString(fmt="H")
                if not questData.rewards:
                    rewardCount = packer.get("B")
                    for _ in range(rewardCount):
                        rewardType, value, amount = packer.get("!BIB")
                        require = Reward(questId, rewardType, value, amount)
                        questData.rewards.append(require)

                dialog.window.setQuestComplete(questData)

    def onQuestAccept(self, questId):
        mixerController.playSound("QuestAccept")
        questData = self.getQuest(questId)
        if questData:
            questData.status = QuestStatus.INCOMPLETE
            self.window.addTitleButton(questData)
            eventManager.notify("onSystemMessage", f"Quest Accepted: {questData.title}")
            self.window.checkCompletion(questId)

    def onQuestAbandon(self, questId):
        questData = self.getQuest(questId)
        if questData:
            self.window.removeQuest(questData)
            del self.questData[questId]
            eventManager.notify("onSystemMessage", f"Quest Abandoned: {questData.title}")

    def onQuestFail(self, questId):
        questData = self.getQuest(questId)
        if questData:
            self.window.failedQuest(questData)
            del self.questData[questId]
            eventManager.notify("onSystemMessage", f"Quest Failed: {questData.title}")

    def onQuestComplete(self, questId):
        questData = self.getQuest(questId)
        if questData:
            self.window.completeQuest(questData)
            del self.questData[questId]
            eventManager.notify("onSystemMessage", f"Quest Complete: {questData.title}")

    def onQuestState(self, questId, state):
        self.window.updateState(questId, state)

    def onQuestRequireUpdate(self, questId, objectiveId, value):
        questData = self.getQuest(questId)
        if questData:
            objective = questData.objectives[objectiveId]
            objective.valueCount = value
            self.window.updateRequirement(objective)

    def onQuestList(self, data):
        packer = RawUnpacker(data)
        _, questId, status, state, abandonable = packer.get("!BHBB?")
        questData = self.getQuest(questId)
        if not questData:
            questData = QuestData()
            self.questData[questId] = questData
        questData.id = questId
        questData.status = status
        questData.state = state
        questData.abandonAllowed = bool(abandonable)
        questData.title = packer.getString()
        questData.details = packer.getString(fmt="H")
        questData.complete = packer.getString(fmt="H")
        questData.objective = packer.getString()
        questData.requiredState = packer.get("B")
        objectiveCount = packer.get("B")
        for _ in range(objectiveCount):
            objectiveType, objectiveValueCount, valueCount, complete = packer.get("BBIB")
            objective = ObjectiveInfo(len(questData.objectives), questId, objectiveType)
            objective.valueCount = valueCount
            objective.complete = complete
            for _ in range(objectiveValueCount):
                value = packer.get("I")
                objective.values.append(value)

            questData.addObjective(objective)

        self.window.addQuest(questData)
        if questData.requiredState == questData.state:
            self.window.checkCompletion(questId)

    def onItemAdd(self, nameId, quantity):
        for quest in self.questData.values():
            for require in quest.objectives:
                if require.type == QuestObjectives.ITEM or require.type == QuestObjectives.LOOT_DEFEAT:
                    if require.values[0] == nameId:
                        self.window.updateRequirement(require)
                        break

    def onItemDelete(self, itemData, nameId):
        for quest in self.questData.values():
            for require in quest.objectives:
                if require.type == QuestObjectives.ITEM or require.type == QuestObjectives.LOOT_DEFEAT:
                    if require.values[0] == nameId:
                        self.window.updateRequirement(require)
                        break

    def onReceivedMoney(self, money):
        for quest in self.questData.values():
            for require in quest.objectives:
                if require.type == QuestObjectives.MONEY:
                    self.window.updateRequirement(require)
                    break

    def onNameQuery(self, charId, charType, name):
        if charType == IdRange.NPC_CHARACTER:
            for quest in self.questData.values():
                for require in quest.objectives:
                    print(require, quest, quest.id)
                    if require.type in (QuestObjectives.NPCTALK, QuestObjectives.NPC_BATTLE_DEFEAT):
                        if require.values[0] == charId:
                            self.window.updateRequirement(require)
                            break

    def onPokemonReceived(self, pokemonData):
        for quest in self.questData.values():
            for require in quest.objectives:
                if require.type in (QuestObjectives.WILDCAPTURE,):
                    if require.values[0] == pokemonData.dexId:
                        self.window.updateRequirement(require)
                        break

    def onPokemonEvolve(self, pokemonData, dexId):
        for quest in self.questData.values():
            for require in quest.objectives:
                if require.type in (QuestObjectives.WILDCAPTURE,):
                    if require.values[0] == pokemonData.dexId:
                        self.window.updateRequirement(require)
                        break


class QuestJournal(Window):
    BUTTON_POS = (20, 200)
    ROW_SPACING = 46
    ROWS = 4
    QUESTS_PER_PAGE = 4

    def __init__(self, control):
        Window.__init__(self, desktop, position=(AnchorType.CENTER), size=(500, 338), draggable=True, visible=False, style=(styleDB.windowsNoStyle))
        self.control = control
        self.questData = {}
        self.bgImg = textureCache.getGuiImage("questlog/window")
        self.setBackground(self.bgImg)
        self.scrollBox = ScrollableContainer(self, position=(265, 15), size=(215, 265), visible=False)
        self.scrollBox.setManualFit()
        self.closeBtn = Button(self, position=(170, 290), autosize=(False, True), size=(64,
                                                                                        0), style=(styleDB.questButtonStyle), text="Close")
        self.closeBtn.addCallback("onMouseLeftClick", self.closeJournal)
        self.abandonBtn = Button(self, position=(335, 286), autosize=(False, True), size=(64,
                                                                                          0), style=(styleDB.questButtonStyle), text="Abandon")
        self.abandonBtn.addCallback("onMouseLeftClick", self.abandonQuest)
        self.mainLabels = []
        self.objectives = []
        self.questTitleTable = PageContainer(self, position=(10, 10), maxRows=7, maxCols=1)
        self.questTitleTable.setInternalMargins(5, 5)
        self.questTitleTable.setNextButtonPosition(35, 282)
        self.questTitleTable.setBackButtonPosition(6, 282)
        self.questTitleTable.setPageNumberPosition(70, 286)
        self.questTitleTable.setAutoFit()
        self.scrollBox.fitToContent()
        self.setOpenQuest(0)

    def reset(self):
        self.clearDescription()
        self.questTitleTable.emptyAndDestroy()
        self.questData.clear()
        self.setOpenQuest(0)
        if self.visible:
            self.hide()

    def clearDescription(self):
        for label in self.objectives:
            label.destroy()

        for label in self.mainLabels:
            label.destroy()

        self.mainLabels.clear()
        self.objectives.clear()
        self.scrollBox.fitToContent()

    def closeJournal(self, widget, x, y, modifiers):
        self.hide()

    def hide(self):
        super().hide()
        self.scrollBox.hide()

    def show(self):
        super().show()
        self.scrollBox.show()

    def abandonQuest(self, widget, x, y, modifiers):
        if self.openQuest:
            questData = self.getQuest(self.openQuest)
            if questData:
                if questData.abandonAllowed:
                    packetManager.queueSend(cmsg.QuestAbandon, self.openQuest)

    def checkCompletion(self, questId):
        questData = self.getQuest(questId)
        if questData:
            if questData.requiredState != questData.state:
                return False
            if questData.status != QuestStatus.COMPLETE:
                for objective in questData.objectives:
                    if objective.type == QuestObjectives.ITEM or objective.type == QuestObjectives.LOOT_DEFEAT:
                        itemData = sessionService.bag.getItemIfAny(objective.values[0])
                        if itemData:
                            if itemData.quantity < objective.values[1]:
                                return False
                            else:
                                return False
                        elif objective.type == QuestObjectives.MONEY:
                            if sessionService.bag.money < objective.values[0]:
                                return False
                        if objective.type == QuestObjectives.TRAINERDEFEAT:
                            if objective.valueCount < objective.values[0]:
                                return False
                            elif objective.type == QuestObjectives.WILDCAPTURE:
                                pkmn = [x for x in sessionService.getClientPokemonsData() if x.dexId == objective.values[0]]
                                if not pkmn:
                                    return False
                            else:
                                if objective.type == QuestObjectives.WILDDEFEAT:
                                    if objective.valueCount < objective.values[1]:
                                        return False
                                elif objective.type == QuestObjectives.NPCTALK:
                                    pass
                                if not objective.valueCount:
                                    return False
                    elif objective.type == QuestObjectives.CAPTURE_POKEMON:
                        if objective.valueCount < objective.values[1]:
                            return False
                    else:
                        if objective.type == QuestObjectives.NPC_BATTLE_DEFEAT:
                            if not objective.valueCount:
                                return False

                questData.status = QuestStatus.COMPLETE
                eventManager.notify("onQuestJournalComplete")
                return True
        return False

    def setOpenQuest(self, questId):
        self.openQuest = questId
        if questId == 0:
            if self.abandonBtn.visible:
                self.abandonBtn.hide()
        else:
            questData = self.getQuest(self.openQuest)
            if questData:
                pass
        if questData.abandonAllowed:
            if not self.abandonBtn.visible:
                self.abandonBtn.show()
        elif self.abandonBtn.visible:
            self.abandonBtn.hide()
        elif self.abandonBtn.visible:
            self.abandonBtn.hide()

    def format_text(self, text):
        """Removes special characters from Quest Journal."""
        message = text.replace("$N", sessionService.getClientData().name)
        genderData = sessionService.getClientData().gender
        if genderData == Gender.MALE:
            gender = "guy"
        elif genderData == Gender.FEMALE:
            gender = "girl"
        else:
            gender = "person"
        message = message.replace("$G", gender)
        message = message.replace("$B", "\n")
        return message

    def showQuest(self, widget, x, y, modifiers):
        questId = widget.questId
        self.scrollBox.pushToTop()
        self.clearDescription()
        questData = self.getQuest(questId)
        if questData:
            self.setOpenQuest(questId)
            titleLbl = Label((self.scrollBox.content), position=(AnchorType.TOPCENTER), text=(questData.title), size=(180,
                                                                                                                      0), autosize=(False,
                                                                                                                                    True), multiline=True, style=(styleDB.journalTitleLabel), alignment=(Alignment.CENTER))
            descriptionLbl = Label((self.scrollBox.content), position=(AnchorType.TOPCENTER), text=(self.format_text(questData.details)), size=(180,
                                                                                                                                                0), autosize=(False,
                                                                                                                                                              True), multiline=True)
            objectiveLbl = Label((self.scrollBox.content), position=(AnchorType.TOPCENTER), text=(questData.objective), size=(180,
                                                                                                                              0), autosize=(False,
                                                                                                                                            True), multiline=True)
            for objective in questData.objectives:
                label = Label((self.scrollBox.content), position=(AnchorType.TOPCENTER), size=(180,
                                                                                               0), autosize=(False,
                                                                                                             True), text=(self.getQuestObjectiveText(objective)), multiline=True)
                label.requirement = objective
                self.objectives.append(label)

            self.mainLabels = [titleLbl, descriptionLbl, objectiveLbl]
        else:
            sys.stderr.write(f"Attempted to open quest #{questId} but no data was found.\n")
        self.scrollBox.fitToContent()

    def addQuest(self, questData):
        self.addTitleButton(questData)
        self.checkCompletion(questData.id)

    def addTitleButton(self, questData):
        title = Button((self.questTitleTable), size=(228, 0), autosize=(False, True), text=(questData.title), style=(styleDB.questButtonStyle))
        title.questId = questData.id
        title.addCallback("onMouseLeftClick", self.showQuest)
        self.questTitleTable.add(title)

    def getQuestTitleButton(self, questId):
        for widget in self.questTitleTable.getTableWidgets():
            if widget.questId == questId:
                return widget

        return

    def removeQuest(self, questData):
        if self.openQuest == questData.id:
            self.clearDescription()
        button = self.getQuestTitleButton(questData.id)
        self.questTitleTable.deleteAndDestroy(button)
        self.questTitleTable.reorganize()
        self.setOpenQuest(0)

    def failedQuest(self, questData):
        self.removeQuest(questData)

    def completeQuest(self, questData):
        self.removeQuest(questData)

    def objectiveComplete(self, questId):
        return

    def updateObjective(self, questId, objectiveNum):
        return

    def needsDetails(self, questId):
        questData = self.getQuest(questId)
        if questData:
            return False
        else:
            return True

    def needsRequirements(self, questId):
        questData = self.getQuest(questId)
        if questData:
            if questData.status == QuestStatus.NONE:
                return True
        return False

    def needsReward(self, questId):
        questData = self.getQuest(questId)
        if questData:
            if questData.status == QuestStatus.COMPLETE:
                return True
        return False

    def setQuestData(self, questData):
        self.questData[questData.id] = questData

    def getQuest(self, questId):
        return self.control.getQuest(questId)

    def convertMoney(self, value):
        return localeInt(value)

    def getQuestObjectiveText(self, objective: ObjectiveInfo):
        requireText = "Unknown Requirement {0}".format(objective.type)
        if objective.type == QuestObjectives.MONEY:
            requireText = f"- Collected Money : {self.convertMoney(sessionService.bag.money) if sessionService.bag.money < objective.values[0] else self.convertMoney(objective.values[0])}/{self.convertMoney(objective.values[0])}"
        elif objective.type == QuestObjectives.ITEM or objective.type == QuestObjectives.LOOT_DEFEAT:
            itemData = sessionService.bag.getItemIfAny(objective.values[0])
            if itemData:
                itemQuantity = itemData.quantity
            else:
                itemQuantity = 0
            requireText = f"- {itemDB.name(objective.values[0])}'s collected: {objective.values[1] if itemQuantity >= objective.values[1] else itemQuantity}/{objective.values[1]}."
        elif objective.type == QuestObjectives.WILDDEFEAT:
            requireText = f"- {pokemonDB.name(objective.values[0]).title()} defeated: {objective.valueCount}/{objective.values[1]} ."
        elif objective.type == QuestObjectives.WILDCAPTURE:
            pkmn = [x for x in sessionService.getClientPokemonsData() if x.dexId == objective.values[0]]
            if pkmn:
                requireText = f"- Obtain a {pokemonDB.name(objective.values[0]).title()}: Complete"
            else:
                requireText = f"- Obtain a {pokemonDB.name(objective.values[0]).title()}."
        elif objective.type == QuestObjectives.CAPTURE_POKEMON:
            pass
        if objective.values[1] == 1:
            if objective.values[0] == 0:
                requireText = "- Capture any Pokemon."
            else:
                requireText = f"- Capture a {pokemonDB.name(objective.values[0]).title()}"
            if objective.valueCount >= objective.values[1]:
                requireText += " : Complete!"
            elif objective.values[0] == 0:
                requireText = f"- Capture {objective.values[1]} of any Pokemon."
            else:
                requireText = f"- Capture a {pokemonDB.name(objective.values[0]).title()}"
            if objective.valueCount >= objective.values[1]:
                requireText += " - Complete!"
            else:
                requireText += f" - {objective.valueCount}/{objective.values[1]}"
        elif objective.type == QuestObjectives.TRAINERDEFEAT:
            requireText = f"- Trainer's Defeated: {objective.valueCount}/{objective.values[0]}."
        elif objective.type == QuestObjectives.NPCTALK:
            npcName = nameCache.getPlayer(objective.values[0], IdRange.NPC_CHARACTER)
            if npcName:
                requireText = f"- Speak with {npcName}."
                if objective.valueCount:
                    requireText = f"- Speak with {npcName}: Complete."
                else:
                    requireText = "- Speak with Unknown."
                    packetManager.queueSend(cmsg.QueryName, 1, objective.values[0], IdRange.NPC_CHARACTER)
        if objective.type == QuestObjectives.NPC_BATTLE_DEFEAT:
            npcName = nameCache.getPlayer(objective.values[0], IdRange.NPC_CHARACTER)
            if npcName:
                requireText = f"- Battle and defeat {npcName}."
                if objective.valueCount:
                    requireText = f"- Battle and defeat {npcName}: Complete."
            else:
                requireText = "- Battle and defeat: Unknown"
                packetManager.queueSend(cmsg.QueryName, 1, objective.values[0], IdRange.NPC_CHARACTER)
        else:
            if objective.type == QuestObjectives.POKEDEX_SEEN_GLOBAL:
                requireText = f"- Find and scan {objective.values[0]} unique Pokemon."
                if sessionService.pokedex.seen >= objective.values[0]:
                    requireText += " - Complete"
            elif objective.type == QuestObjectives.POKEDEX_CAUGHT_GLOBAL:
                requireText = f"- Capture {objective.values[0]} unique Pokemon."
                if sessionService.pokedex.caught >= objective.values[0]:
                    requireText += " - Complete"
            elif objective.type == QuestObjectives.POKEDEX_SEEN_POKEMON:
                requireText = f"- Scan {pokemonDB.name(objective.values[0])} into your Pokedex."
                if sessionService.pokedex.hasSeen(objective.values[0]):
                    requireText += " - Complete"
            elif objective.type == QuestObjectives.POKEDEX_CAUGHT_POKEMON:
                pass
            requireText = f"- Capture {objective.values[1]} {Element.toStr[objective.values[0]].title()} type Pokemon."
            if sessionService.pokedex.hasSeen(objective.values[0]):
                requireText += " - Complete"
            elif objective.type == QuestObjectives.POKEDEX_SEEN_TYPE:
                requireText = "- TODO"
            elif objective.type == QuestObjectives.POKEDEX_CAUGHT_TYPE:
                requireText = ""
            elif objective.type == QuestObjectives.BATTLE_TYPE:
                requireText = ""
            elif objective.type == QuestObjectives.CAPTURE_TYPE:
                requireText = ""
            elif objective.type == QuestObjectives.PVP_BATTLE:
                requireText = ""
            elif objective.type == QuestObjectives.EVOLVE:
                requireText = ""
            return requireText

    def updateRequirement(self, requirement):
        if self.openQuest == requirement.questId:
            for label in self.objectives:
                if label.requirement == requirement:
                    label.text = self.getQuestObjectiveText(requirement)
                    break

        self.scrollBox.fitToContent()
        self.checkCompletion(requirement.questId)

    def updateState(self, questId, state):
        quest = self.getQuest(questId)
        if quest:
            quest.state = state
            self.checkCompletion(questId)


quest = Quest()
