# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\interface\npc\dialog.py
"""
Created on Jul 31, 2011

@author: Ragnarok
"""
from client.control.gui import ScrollableContainer, Window, Label, Button, Datatable, ShadowContainer
from client.game import desktop
from shared.container.net import cmsg
from client.control.events.event import eventManager
from client.control.service.session import sessionService
from shared.container.constants import QuestStatus, QuestReward, QuestQuery, IdRange, DialogEnding, Gender
from client.data.utils.anchor import AnchorType, Alignment
from client.data.DB import pokemonDB, itemDB, textDB
from client.control.net.sending import packetManager
from client.control.utils.localization import localeInt
from client.data.gui import styleDB
from client.data.container.char import charContainer
import pyglet
from client.control.gui.label import SpellingLabel
from pyglet.window import key

class Dialog:

    def __init__(self):
        self.window = DialogWindow(self)
        eventManager.registerListener(self)

    def reset(self):
        self.window.reset()

    def receivedDialog(self, message, close, options):
        self.window.setDialog(message, close, options)

    def dialogClose(self):
        self.window.forceClose()


DIALOG = 0
QUEST = 1

class DialogSettings:

    def __init__(self):
        return


class QuestSettings:

    def __init__(self):
        self.questData = None
        self.questButtonTable = Datatable(self, position=(AnchorType.BOTTOMCENTER), maxRows=1, maxCols=2)
        self.questButtonTable.setAutoFit()

    def showAcceptance(self):
        accept = Button((self.questButtonTable), text="Accept", size=(100, 0), autosize=(False,
                                                                                         True), style=(styleDB.questButtonStyle))
        accept.addCallback("onMouseLeftClick", self.acceptQuest)
        denyQuestBtn = Button((self.questButtonTable), text="No thanks", size=(100,
                                                                               0), autosize=(False,
                                                                                             True), style=(styleDB.questButtonStyle))
        denyQuestBtn.addCallback("onMouseLeftClick", self.denyQuest)
        self.questButtonTable.add(accept)
        self.questButtonTable.add(denyQuestBtn)
        self.questButtonTable.setPosition(0, self.messageLbl.height)
        self.fitToContent()

    def showCompletion(self):
        completeButton = Button((self.questButtonTable), text="Complete", size=(100,
                                                                                0), autosize=(False,
                                                                                              True), style=(styleDB.questButtonStyle))
        completeButton.addCallback("onMouseLeftClick", self.completeQuest)
        denyQuestBtn = Button((self.questButtonTable), text="No thanks", size=(100,
                                                                               0), autosize=(False,
                                                                                             True), style=(styleDB.questButtonStyle))
        denyQuestBtn.addCallback("onMouseLeftClick", self.denyQuest)
        self.questButtonTable.add(completeButton)
        self.questButtonTable.add(denyQuestBtn)
        self.questButtonTable.setPosition(0, self.messageLbl.height)
        self.fitToContent()

    def acceptQuest(self, widget, x, y, modifiers):
        packetManager.queueSend(cmsg.QuestAccept, self.npcId, self.npcIdRange, self.questData.id)
        self.closeWindow()

    def denyQuest(self, widget, x, y, modifiers):
        self.closeWindow()

    def setQuestHello(self, questData):
        self.resetWindow()
        self.questData = questData
        self.mode = QUEST
        self.setMessage(questData.details)

    def setQuestIncomplete(self, questData):
        self.resetWindow()
        self.questData = questData
        self.mode = QUEST
        self.setMessage(questData.progress)

    def setQuestComplete(self, questData):
        self.resetWindow()
        self.questData = questData
        self.mode = QUEST
        self.setMessage(questData.reward)

    def completeQuest(self, widget, x, y, modifiers):
        packetManager.queueSend(cmsg.QuestComplete, self.npcId, self.npcIdRange, self.questData.id)
        self.closeWindow()


class OptionsWindow(Window):

    def __init__(self):
        Window.__init__(self, desktop, position=(AnchorType.CENTER), size=(300, 200), draggable=True, visible=False)


class DialogSpellingLabel(SpellingLabel):
    FAST = 35
    INCREASE = 70

    def __init__(self, parent, text="", style=styleDB.blackLabelStyle, position=(0, 0), size=(0, 0), draggable=False, visible=True, autosize=(True, True), alignment=Alignment.LEFT, multiline=False, enableEvents=False):
        SpellingLabel.__init__(self, parent, text=text, style=style, position=position, size=size, draggable=draggable, visible=visible,
          autosize=autosize,
          alignment=alignment,
          multiline=multiline,
          enableEvents=enableEvents)
        self.line = 0
        self.stopped = True

    def increaseRate(self):
        if self.renderer.textSprite.active:
            self.renderer.textSprite.rate = self.INCREASE
            self.renderer.textSprite.stop()
            self.renderer.textSprite.start()

    def update(self, dt):
        if self.renderer.textSprite._lines > 5:
            if self.renderer.textSprite._lines != self.line:
                self.line = self.renderer.textSprite._lines
                self.parent.parent.pushToDiff(-17)
        if self.renderer.textSprite.active is False:
            self.stop()

    def start(self):
        pyglet.clock.unschedule(self.update)
        pyglet.clock.schedule_interval(self.update, 0.05)
        self.renderer.textSprite.start()
        self.stopped = False

    def stop(self):
        pyglet.clock.unschedule(self.update)
        self.renderer.textSprite.stop()
        self.stopped = True
        self.resetSpeed()

    def resetSpeed(self):
        self.renderer.textSprite.rate = self.FAST


class DialogLabel(Label):

    def __init__(self, parent, text="", style=styleDB.blackLabelStyle, position=(0, 0), size=(0, 0), draggable=False, visible=True, autosize=(True, True), alignment=Alignment.LEFT, multiline=False, enableEvents=False):
        Label.__init__(self, parent, text=text, style=style, position=position, size=size, draggable=draggable, visible=visible,
          autosize=autosize,
          alignment=alignment,
          multiline=multiline,
          enableEvents=enableEvents)

    def start(self):
        return

    def stop(self):
        return


class DialogWindow(Window, QuestSettings):

    def __init__(self, control):
        Window.__init__(self, desktop, position=(AnchorType.TOPCENTER), size=(288,
                                                                              144), autosize=(False,
                                                                                              True), draggable=True,
          visible=False,
          style=(styleDB.questDetailsStyle))
        QuestSettings.__init__(self)
        self.setManualFit()
        self.options = []
        self.labels = []
        self.control = control
        self.currentPage = 0
        self.message = [""]
        self.mode = DIALOG
        self.npcId = 0
        self.npcIdRange = 0
        self.shadow = ShadowContainer(self, position=(0, 0), size=(280, 110), color=(233,
                                                                                     208,
                                                                                     191), alpha=255)
        self.scrollArea = ScrollableContainer((self.shadow), position=(0, 0), size=(260,
                                                                                    95), autosize=(False,
                                                                                                   False), visible=False)
        self.scrollArea.setManualFit()
        self.messageLbl = DialogSpellingLabel((self.scrollArea.content), position=(AnchorType.TOPLEFT), size=(235,
                                                                                                              0), text="T",
          autosize=(False, True),
          multiline=True,
          style=(styleDB.npcLabelStyle))
        self.messageLbl.renderer.batch = self.messageLbl.transparentBatch
        self.nextButton = Button(self, position=(self.width - 50, self.scrollArea.height + 15), text="Next", size=(50,
                                                                                                                   0), visible=False, style=(styleDB.questButtonStyle))
        self.nextButton.addCallback("onMouseLeftClick", self.nextPage)
        self.closeButton = Button(self, position=(self.width - 50, self.scrollArea.height + 15), text="Close", size=(50,
                                                                                                                     0), visible=False, style=(styleDB.questButtonStyle))
        self.closeButton.addCallback("onMouseLeftClick", self.closeWindowClick)
        self.optionsTable = Datatable(self, position=(0, self.scrollArea.height + 15), maxCols=1)
        self.optionsTable.setAutoFit()
        self.addCallback("onKeyDown", self.advanceDialog)
        self.fitToContent()

    def reset(self):
        self.npcId = 0
        self.npcIdRange = 0
        self.currentPage = 0
        self.questId = 0
        for label in self.labels:
            label.destroy()

        self.labels.clear()
        self.optionsTable.emptyAndDestroy()
        if self.visible:
            self.hide()

    def advanceDialog(self, symbol, modifiers):
        if symbol == key.ENTER or symbol == key.RETURN:
            if self.messageLbl.stopped:
                self.closeWindow()
        elif symbol == key.SPACE:
            pass
        if not self.messageLbl.stopped:
            self.messageLbl.increaseRate()
        elif self.nextButton.visible:
            self.nextPage(None, None, None, None)
        else:
            if len(self.optionsTable.getWidgets()) >= 1:
                return
            self.closeWindow()

    def resetWindow(self):
        if not self.visible:
            self.show()
        else:
            self.currentPage = 0
            self.questId = 0
            for label in self.labels:
                label.destroy()

            self.labels.clear()
            self.optionsTable.emptyAndDestroy()
            self.optionsTable.setPosition(0, self.scrollArea.height + 15)
            self.questButtonTable.emptyAndDestroy()
            self.questButtonTable.setPosition(0, 0)
            self.scrollArea.fitToContent()
            if self.closeButton.visible:
                self.closeButton.hide()
            if self.nextButton.text == "Battle!":
                self.nextButton.text = "Next"
            if self.nextButton.visible:
                self.nextButton.hide()

    def setNpc(self, npcId, npcIdRange):
        self.npcId = npcId
        self.npcIdRange = npcIdRange

    def setMessage(self, message):
        self.message = self.parseMessage(message)
        if len(self.message) > 1:
            self.nextButton.show()
        self.showPage()

    def setDialog(self, message, close, options):
        self.resetWindow()
        self.mode = DIALOG
        self.options = options
        self.closeMode = close
        self.setMessage(message)
        desktop.setFocusWidget(self)
        if close == DialogEnding.CLOSE:
            if len(self.message) == 1:
                self.closeButton.show()
        elif close == DialogEnding.NEXT:
            pass
        if len(self.options) == 0:
            self.nextButton.show()
        elif close == DialogEnding.BATTLE:
            self.nextButton.show()
            self.nextButton.text = "Battle!"
        else:
            if close == DialogEnding.TIMED_CLOSE or close == DialogEnding.TIMED_CONTINUE:
                if self.closeButton.visible:
                    self.closeButton.hide()
                pyglet.clock.schedule_once(self._hideDialog, 3)
                desktop.lostFocus()
        if self.options:
            self.fitToContent()
        else:
            self.setHeight(144)

    def _hideDialog(self, dt):
        if self.visible:
            self.closeWindow()

    def onLastPage(self):
        return self.currentPage >= len(self.message) - 1

    def continueScript(self):
        print("SENDING CONTINUE")
        packetManager.queueSend(cmsg.NpcContinue, None)
        self.closeWindow()

    def nextPage(self, widget, x, y, modifiers):
        if self.onLastPage():
            if self.closeMode == DialogEnding.NEXT:
                self.continueScript()
            else:
                self.closeWindow()
            return
        self.currentPage += 1
        if len(self.message) > 1:
            self.showPage()
            self.desktop.setFocusWidget(self)

    def showPage(self):
        if not self.scrollArea.visible:
            self.scrollArea.show()
        self.scrollArea.pushToTop()
        message = self.message[self.currentPage]
        self.messageLbl.text = message
        self.messageLbl.start()
        if self.onLastPage():
            if self.mode == DIALOG:
                for option in self.options:
                    button = Button((self.optionsTable), text=f"▶ {option.text}", style=(styleDB.questButtonStyle))
                    button.optionId = option.number
                    button.addCallback("onMouseLeftClick", self.selectOption)
                    self.optionsTable.add(button)

                if self.closeMode == DialogEnding.CLOSE:
                    if not self.closeButton.visible:
                        self.closeButton.show()
                    if self.nextButton.visible:
                        self.nextButton.close()
        else:
            if self.mode == QUEST:
                if self.questData.status == QuestStatus.COMPLETE:
                    for reward in self.questData.rewards:
                        if reward.type == QuestReward.MONEY:
                            requireText = f"${localeInt(reward.value)}"
                        elif reward.type == QuestReward.POKEMON:
                            requireText = f"A {pokemonDB.name(reward.value)}!"
                        elif reward.type == QuestReward.ITEM:
                            requireText = f"{itemDB.name(reward.value)} x{reward.amount}"
                        elif reward.type == QuestReward.XP:
                            requireText = f"{localeInt(reward.value)} Experience"
                        else:
                            requireText = "A Surprise!"
                        label = Label((self.scrollArea.content), position=(AnchorType.TOPLEFT), size=(180,
                                                                                                      0), autosize=(False,
                                                                                                                    True),
                          text=requireText)
                        self.labels.append(label)

                    if self.nextButton.visible:
                        self.nextButton.hide()
                self.showCompletion()
            else:
                if self.questData.status == QuestStatus.NONE:
                    self.showAcceptance()
                    if self.closeButton.visible:
                        self.closeButton.hide()
            if self.nextButton.visible:
                self.nextButton.hide()
            elif not self.closeButton.visible:
                self.closeButton.show()
            self.scrollArea.fitToContent()
            self.fitToContent()

    def addQuestList(self, startList, endList):
        for quest in startList + endList:
            button = Button((self.optionsTable), text=("QUEST: {0}".format(quest.title)), style=(styleDB.questButtonStyle))
            button.questId = quest.id
            button.addCallback("onMouseLeftClick", self.selectQuest)
            self.optionsTable.add(button, col=0)

        self.scrollArea.fitToContent()
        self.fitToContent()

    def selectQuest(self, widget, x, y, modifiers):
        packetManager.queueSend(cmsg.QuestDetailsQuery, sessionService.npc.id, sessionService.npc.idRange, widget.questId, QuestQuery.DETAILS)

    def parseMessage(self, message):
        message = message.replace("$N", sessionService.getClientData().name)
        genderData = sessionService.getClientData().gender
        if genderData == Gender.MALE:
            gender = "guy"
        elif genderData == Gender.FEMALE:
            gender = "girl"
        else:
            gender = "person"
        message = message.replace("$G", gender)
        message = message.split("$B")
        return message

    def optionOver(self, widget, x, y, modifiers):
        widget.text = " " + widget.text

    def optionLost(self, button):
        button.text = button.text[2:]

    def selectOption(self, widget, x, y, modifiers):
        packetManager.queueSend(cmsg.NpcSelectOption, widget.optionId)

    def forceClose(self):
        self.hide()

    def hide(self):
        self.scrollArea.hide()
        Window.hide(self)
        if sessionService.npc:
            if sessionService.npc.idRange != IdRange.NPC_OBJECT:
                npc = charContainer.getCharByIdIfAny(sessionService.npc.id, sessionService.npc.idRange)
                if npc:
                    npc.setFacingNear(npc.data.originalFacing)
        sessionService.npc = None

    def closeWindowClick(self, widget, x, y, modifiers):
        self.closeWindow()

    def closeWindow(self):
        if not self.onLastPage():
            self.nextButton.hide()
        elif self.mode == QUEST:
            pass
        if self.questData.status == QuestStatus.NONE:
            self.closeButton.show()
        packetManager.queueSend(cmsg.NpcClose, None)
        self.hide()


dialog = Dialog()
