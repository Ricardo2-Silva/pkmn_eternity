# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\interface\chat\chat.py
"""
Created on Jul 27, 2011

@author: Ragnarok
"""
import time
from typing import List, Any
from profilehooks import profile
from shared.container.constants import IdRange, Emotes
from client.control.gui import Textbox, Window, Label, Button, Datatable, ScrollableContainer, Checkbox, Menu, Tabs, Container, Thumb, Header, DropDown
import client.data.gui.styleDB as styleDB
from client.control.events.event import eventManager
from shared.container.net import cmsg
from client.control.service.session import sessionService, charContainer
from client.data.utils.anchor import AnchorType
from shared.container.constants import ChatMessageType
from . import commands
from . import channels
from . import pm
from client.data.system.chat import chatConfig
import client.data.font as font
from client.data.utils.color import Color
from client.control.net.sending import packetManager
from client.data.cache import nameCache
from client.game import desktop
from client.data.gui.button import ButtonState
from twisted.internet import reactor
from pyglet.window import key
from client.control.gui.chat import chatMessageController
from client.data.settings import gameSettings
CHATFONT = font.fontDB.getFont("chat")
COMMANDCHAR = "/"
CHANNELCHAR = "#"
PARTYFLAG = "!"
GUILDFLAG = "$"
EMOTECHAR = "/"

class FormattedMessage:
    trnId = 0
    name = ""
    channelId = 0
    channelNum = 0
    style = "DEFAULT"
    message = ""
    type = ChatMessageType.AREA

    def __init__(self, channels):
        self.channels = channels

    def formatName(self):
        if self.style == "PM_FROM":
            self.name = f"> From {self.name}"
        elif self.style == "PM_TO":
            self.name = f"> To {self.name}"
        elif self.style == "GLOBAL":
            c = self.channels.getChannel(self.channelId)
            if not c:
                self.name = f"[Unknown Channel.] {self.name}"
            else:
                self.name = f"[{c.num}. {c.name}] {self.name}"
                self.channelNum = c.num
        elif self.style == "PARTY":
            self.name = f"[Party] {self.name}"
        elif self.style == "GUILD":
            self.name = f"[Guild] {self.name}"


class TabSettingsWindow(Window):

    def __init__(self, tabMenu):
        Window.__init__(self, desktop, position=(AnchorType.CENTER), draggable=True, size=(150,
                                                                                           205), visible=False, autosize=(True,
                                                                                                                          True))
        self.tabData = None
        self.setManualFit()
        self.checkBtns = {}
        self.typeLabel = Label(self, position=(AnchorType.TOPLEFT), text="Type:")
        self.checkBtns[ChatMessageType.AREA] = Checkbox(self, position=(AnchorType.TOPLEFT), text="Area")
        self.checkBtns[ChatMessageType.CHANNEL] = Checkbox(self, position=(AnchorType.TOPLEFT), text="Channels")
        self.checkBtns[ChatMessageType.WHISPER] = Checkbox(self, position=(AnchorType.TOPLEFT), text="Whispers")
        self.checkBtns[ChatMessageType.PARTY] = Checkbox(self, position=(AnchorType.TOPLEFT), text="Party")
        self.checkBtns[ChatMessageType.GUILD] = Checkbox(self, position=(AnchorType.TOPLEFT), text="Guild")
        self.checkBtns[ChatMessageType.BATTLE] = Checkbox(self, position=(AnchorType.TOPLEFT), text="Battle")
        self.checkBtns[ChatMessageType.SYSTEM] = Checkbox(self, position=(AnchorType.TOPLEFT), text="System")
        self.okBtn = Button(self, position=(AnchorType.CENTERBOTTOM), text="Save", style=(styleDB.blueButtonStyle))
        self.okBtn.addCallback("onMouseLeftClick", self.saveSettings)
        self.cancelBtn = Button(self, position=(AnchorType.CENTERBOTTOM), text="Cancel", style=(styleDB.redButtonStyle))
        self.cancelBtn.addCallback("onMouseLeftClick", self.closeWindow)
        self.typeLabel = Label(self, position=(AnchorType.TOPRIGHT), text="Channels:")
        self.channelsList = Datatable(self, position=(AnchorType.TOPRIGHT))
        self.channelsList.setInternalMargins(0, 6)
        self.fitToContent()

    def reset(self):
        self.forceHide()

    def showSettings(self, tab):
        if not self.visible:
            self.show()
        self.unCheckAll()
        self.channelsList.emptyAndDestroy()
        self.tabData = tab
        for msgType in tab.data.settings:
            setting = tab.data.settings[msgType]
            self.checkBtns[msgType].setSelected(True if setting else False)

        for channelId in chatConfig.channels:
            name = chatConfig.channels[channelId]
            cbox = Checkbox((self.channelsList), text=name)
            cbox.setSelected(True if channelId in tab.data.channels else False)
            cbox.channelId = channelId
            self.channelsList.add(cbox, col=0)

        self.channelsList.fitToContent()
        self.fitToContent()

    def unCheckAll(self):
        for chk in self.checkBtns.values():
            chk.setSelected(False)

    def saveSettings(self, widget, x, y, modifiers):
        for msgType in self.checkBtns:
            box = self.checkBtns[msgType]
            self.tabData.data.settings[msgType] = box.isSelected()

        for chkbox in self.channelsList.getWidgets():
            if chkbox.isSelected():
                if chkbox.channelId in chatConfig.channels:
                    self.tabData.addChannel(chkbox.channelId)
                else:
                    if chkbox.channelId in chatConfig.channels:
                        self.tabData.removeChannel(chkbox.channelId)

        self.tabData.saveData()
        self._closeWindow()

    def closeWindow(self, widget, x, y, modifiers):
        self._closeWindow()

    def _closeWindow(self):
        self.hide()
        self.tabData = None


class NameTabWindow(Window):

    def __init__(self, tabMenu):
        Window.__init__(self, desktop, position=(AnchorType.CENTER), size=(115, 85), autosize=(True,
                                                                                               True), draggable=True, visible=False)
        self.tab = None
        self.tabMenu = tabMenu
        self.renaming = False
        self.bannedChars = (',', ':')
        self.nameLbl = Label(self, text="Choose a name for this tab.")
        self.textBox = Textbox(self, position=(0, 20), size=(145, 20), maxLetters=20)
        self.textBox.addCallback("onKeyReturn", self._renameTab)
        self.okBtn = Button(self, position=(AnchorType.CENTERBOTTOM), text="Ok", size=(75,
                                                                                       0), autosize=(False,
                                                                                                     True), style=(styleDB.blueButtonStyle))
        self.okBtn.addCallback("onMouseLeftClick", self.renameClick)
        self.cancelBtn = Button(self, position=(AnchorType.CENTERBOTTOM), size=(75,
                                                                                0), autosize=(False,
                                                                                              True), text="Cancel", style=(styleDB.redButtonStyle))
        self.cancelBtn.addCallback("onMouseLeftClick", self.closeWindow)
        self.fitToContent()

    def reset(self):
        self.tab = None
        self.renaming = False
        self.forceHide()

    def createTab(self):
        self.renaming = False
        if not self.visible:
            self.show()
        self.nameLbl.text = "Choose a name for this tab."
        self.textBox.text = "Default"

    def renameTab(self, tab):
        self.renaming = True
        self.tab = tab
        if not self.visible:
            self.show()
        self.nameLbl.text = "Choose a new name for this tab."
        self.textBox.text = tab.data.name

    def renameClick(self, widget, x, y, modifiers):
        self._renameTab()

    def _renameTab(self):
        if len(self.textBox.text) < 1:
            return
        else:
            for char in self.bannedChars:
                if char in self.textBox.text:
                    return

            if self.textBox.text in chatConfig.tabs:
                self.nameLbl.text = "Choose a different name."
                return
            if self.renaming:
                success = self.tab.renameTab(self.textBox.text)
                if not success:
                    self.nameLbl.text = "Name exceeds length of window."
                    return
            else:
                if len(chatConfig.tabs.keys()) >= 5:
                    self.nameLbl.text = "Maximum of 5 tabs."
                    return
                tab = ChatTab((self.tabMenu.window), name=(self.textBox.text))
                if not tab.data:
                    self.nameLbl.text = "Name exceeds length of window."
                    return
                self.tabMenu.window.tabs.append(tab)
        self._closeWindow()

    def _closeWindow(self):
        self.tab = None
        self.hide()

    def closeWindow(self, widget, x, y, modifiers):
        self._closeWindow()


class TabMenu(Menu):

    def __init__(self, window):
        Menu.__init__(self, desktop)
        self.window = window
        self.tab = None
        self.nameWindow = NameTabWindow(self)
        self.settingsWindow = TabSettingsWindow(self)
        self.createBtn = Button(self, style=(styleDB.menuItemStyle), size=(75, 20), text="New", autosize=(False,
                                                                                                          False))
        self.createBtn.addCallback("onMouseLeftClick", self.createTab)
        self.renameBtn = Button(self, style=(styleDB.menuItemStyle), size=(75, 20), text="Rename", autosize=(False,
                                                                                                             False))
        self.renameBtn.addCallback("onMouseLeftClick", self.renameTab)
        self.closeTabBtn = Button(self, style=(styleDB.menuItemStyle), size=(75, 20), text="Close", autosize=(False,
                                                                                                              False))
        self.closeTabBtn.addCallback("onMouseLeftClick", self.closeTab)
        self.settingsBtn = Button(self, style=(styleDB.menuItemStyle), size=(75, 20), text="Settings", autosize=(False,
                                                                                                                 False))
        self.settingsBtn.addCallback("onMouseLeftClick", self.tabSettings)
        self.cancelBtn = Button(self, style=(styleDB.menuItemStyle), size=(75, 20), text="Cancel", autosize=(False,
                                                                                                             False))
        self.buttons = [
         self.createBtn, self.renameBtn, self.closeTabBtn, self.settingsBtn, self.cancelBtn]

    def reset(self):
        self.nameWindow.reset()
        self.settingsWindow.reset()
        self.forceHide()
        self.tab = None

    def createTab(self, widget, x, y, modifiers):
        self.nameWindow.createTab()

    def renameTab(self, widget, x, y, modifiers):
        self.nameWindow.renameTab(self.tab)

    def closeTab(self, widget, x, y, modifiers):
        self.tab.removeTab()

    def tabSettings(self, widget, x, y, modifiers):
        self.settingsWindow.showSettings(self.tab)

    def closeWindow(self):
        if self.visible:
            for button in self.buttons:
                if button.visible:
                    button.hide()

            self.hide()

    def showMenu(self, widget, x, y, modiifers):
        self.tab = widget
        self.populateMenu()
        self.show()
        self.setActive()
        self.setPosition(x, y)

    def populateMenu(self):
        self.hideAllOptions()
        self.add(self.createBtn)
        self.add(self.renameBtn)
        self.add(self.settingsBtn)
        if len(chatConfig.tabs) > 1:
            self.add(self.closeTabBtn)
        self.add(self.cancelBtn)
        self.fitToContent()


class ChatTab(ScrollableContainer):

    def __init__(self, parent, name='Default', data=None):
        ScrollableContainer.__init__(self, parent, position=(10, 0), size=(426, 120))
        self.data = None
        self.parent = parent
        self.tabButton = parent.tab.addTab(name)
        if self.tabButton:
            if not data:
                self.data = chatConfig.createNewTab(name)
            else:
                self.data = data
            self.tabButton.addCallback("onMouseLeftClick", self.showTab)
            self.tabButton.addCallback("onMouseRightClick", self.showTabMenu)
            self.hide()

    def reset(self):
        self.parent.tabs.remove(self)
        self.parent.tab.delTab(self.data.name)
        self.content.emptyAndDestroy()
        if self.parent.tabs:
            self.parent.currentTab = self.parent.tabs[-1]

    def removeChannel(self, channelId):
        if channelId in self.data.channels:
            self.data.channels.remove(channelId)

    def addChannel(self, channelId):
        if channelId not in self.data.channels:
            self.data.channels.append(channelId)

    def showTab(self, widget, x, y, modifiers):
        if self == self.parent.currentTab:
            return
        self.parent.currentTab.hide()
        self.show()
        self.parent.currentTab = self
        self.fitToContent()
        self.pushToBottom()

    def showTabMenu(self, widget, x, y, modifiers):
        self.parent.tabMenu.showMenu(self, x, y, modifiers)

    def renameTab(self, name):
        renamed = self.parent.tab.renameTab(self.data.name, name)
        if renamed:
            chatConfig.renameTab(self.data, name)
            return True
        else:
            return False

    def saveData(self):
        chatConfig.save()

    def removeTab(self):
        self.parent.tabs.remove(self)
        chatConfig.deleteTab(self.data)
        self.parent.tab.delTab(self.data.name)
        self.content.emptyAndDestroy()
        self.parent.currentTab = self.parent.tabs[-1]


MAX_TABS = 5

class ChatWindow(Window, commands.Commands):
    tabs: List[ChatTab]

    def __init__(self, control):
        commands.Commands.__init__(self)
        Window.__init__(self, desktop, position=(AnchorType.BOTTOMRIGHT), size=(453,
                                                                                165), draggable=True, visible=False)
        self._currentTab = None
        self._last_messages = []
        self.tabs = []
        self.tabMenu = TabMenu(self)
        self.tab = Tabs(self, desktop)
        self.reduce = Button(self, "", position=(AnchorType.BOTTOMRIGHTFIXED), size=(16,
                                                                                     16), style=(styleDB.reduceButtonStyle), autosize=(False,
                                                                                                                                       False))
        self.thumb = Thumb(self, "Chat", position=(AnchorType.BOTTOMRIGHT), reduceButton=(self.reduce))
        self.control = control
        self.channels = control.channels
        self.tabTable = Datatable(self)
        self.dataTable = Datatable(self, position=(AnchorType.BOTTOMLEFT), maxCols=2)
        self.dropdownPrefix = ""
        self.dropdownType = ChatMessageType.AREA
        self.chatTxt = Textbox(self, position=(90, 130), size=(325, 0), text="", keepFocus=True, scrollable=True)
        self.chatTxt.addCallback("onKeyReturn", self.sendMessage)
        self.chatDropdown = DropDown(self, position=(0, 127), direction="up", style=(styleDB.dropdownButtonStyle))
        self.emote_texts = [emote.value for emote in Emotes.ALL]
        self.fitToContent()

    @property
    def currentTab(self):
        return self._currentTab

    @currentTab.setter
    def currentTab(self, tab):
        self._currentTab = tab
        self._currentTab.show()

    def reset(self):
        for tab in self.tabs:
            tab.reset()
            tab.emptyAndDestroy()

        self.chatDropdown.emptyAndDestroy()
        self.tabs.clear()
        self.tabTable.emptyAndDestroy()
        self._currentTab = None
        self.tabMenu.reset()
        self.chatTxt.text = ""
        if self.visible:
            self.hide()

    def createDropdowns(self, default=True):
        self.chatDropdown.emptyAndDestroy()
        button = Button((self.chatDropdown), "Area", style=(styleDB.dropdownButtonStyle))
        button.prefixSelect = ""
        button.prefixType = ChatMessageType.AREA
        button.addCallback("onMouseLeftClick", self.changePrefix)
        self.chatDropdown.addOption(button)
        if sessionService.group.inGroup():
            button = Button((self.chatDropdown), "Party", style=(styleDB.dropdownButtonStyle))
            button.prefixSelect = f""
            button.prefixType = ChatMessageType.PARTY
            button.addCallback("onMouseLeftClick", self.changePrefix)
            self.chatDropdown.addOption(button)
        if sessionService.guild.inGuild():
            button = Button((self.chatDropdown), "Guild", style=(styleDB.dropdownButtonStyle))
            button.prefixSelect = f""
            button.prefixType = ChatMessageType.GUILD
            button.addCallback("onMouseLeftClick", self.changePrefix)
            self.chatDropdown.addOption(button)
        for channel in self.control.channels.getAllChannels():
            button = Button((self.chatDropdown), f"{channel.num}. {channel.name}", style=(styleDB.dropdownButtonStyle))
            button.prefixSelect = f"{CHANNELCHAR}{channel.num} "
            button.prefixType = ChatMessageType.CHANNEL
            button.addCallback("onMouseLeftClick", self.changePrefix)
            self.chatDropdown.addOption(button)

        self.chatDropdown.fitToContent()
        if default:
            self.chatDropdown.setOption(self.chatDropdown.getOption("Area"))

    def changePrefix(self, widget, x, y, modifiers):
        try:
            self.dropdownPrefix = widget.prefixSelect
            self.dropdownType = widget.prefixType
        except AttributeError:
            print("Warning: Tried to pass a chat prefix that doesn't exist.")

    def loadChat(self):
        for tabData in chatConfig.getTabs():
            tab = ChatTab(self, name=(tabData.name), data=tabData)
            if tab.data:
                self.tabs.append(tab)
            else:
                tab.emptyAndDestroy()

        self.currentTab = self.tabs[0]
        self.setBackground(color=(Color.CHAT_BACKGROUND), alpha=150)

    def setMessageFocus(self, messageType, *args):
        """Sets the current chat focus to the last used message, whether it's a channel, area, party, etc"""
        if messageType == ChatMessageType.AREA:
            self.focusButton.text = "Area"
        elif messageType == ChatMessageType.CHANNEL:
            self.focusButton.text = ""

    def hide(self):
        Window.hide(self)
        self.tab.hide()

    def show(self):
        Window.show(self)
        self.tab.show()
        if self.currentTab:
            if not self.currentTab.visible:
                self.currentTab.show()

    def checkForCommand(self, text):
        if text[0] == COMMANDCHAR:
            broken = text.split(" ")
            command = broken[0].strip(COMMANDCHAR)
            values = broken[1:]
            if isinstance(values, int):
                values = [
                 values]
        if command in self.commandList:
            self.commandList[command](values)
            return True
        else:
            return False

    def checkForChannel(self, text):
        if text[0] == CHANNELCHAR:
            broken = text.split(" ")
            channel = broken[0].strip(CHANNELCHAR)
            message = " ".join(broken[1:])
            try:
                channel = int(channel)
                if channel <= 0:
                    return False
                channelData = self.channels.getChannelByNum(channel)
                if not channelData:
                    return False
            except ValueError:
                channelData = self.channels.getChannelByName(channel)
                if not channelData:
                    return False

            packetManager.queueSend(cmsg.ChatMessage, (ChatMessageType.CHANNEL, channelData.name.encode("utf-8"), message.encode("utf-8")))
            return True
        else:
            return False

    def checkForEmote(self, text):
        if text[0] == EMOTECHAR:
            emote = str(text[1:])
            if emote in self.emote_texts:
                if sessionService.selected:
                    emoteNum = self.emote_texts.index(emote)
                    packetManager.queueSend(cmsg.Emote, sessionService.selected.data.id, sessionService.selected.data.idRange, emoteNum)
                    return True
        return False

    def sendMessage(self):
        message = self.chatTxt.text
        if message:
            self.chatTxt.text = ""
            if self.checkForCommand(message):
                return
            if self.checkForEmote(message):
                return
            if self.checkForChannel(message):
                return
            if not sessionService.ticks.canChat():
                return
            message = self.dropdownPrefix + message
            if self.checkForChannel(message):
                return
            sessionService.ticks.setChat()
            packetManager.queueSend(cmsg.ChatMessage, (self.dropdownType,
             str(sessionService.getClientId()).encode(),
             message.encode()))
        else:
            desktop.lostFocus()

    def addMessage(self, messageData):
        if messageData.type == ChatMessageType.WHISPER:
            if self.control.privateMessages.say(messageData):
                return
        messageData.formatName()
        for tab in self.tabs:
            if messageData.type == ChatMessageType.ANNOUNCE or tab.data.settings[messageData.type]:
                if messageData.type == ChatMessageType.CHANNEL:
                    if messageData.channelNum not in tab.data.channels:
                        continue
                    if messageData.name:
                        message = f"{messageData.name}: {messageData.message}"
                else:
                    message = messageData.message
                Label((tab.content), position=(AnchorType.TOPLEFT),
                  size=(360, 0),
                  style=(styleDB.chatStyles[messageData.style]),
                  autosize=(False, True),
                  multiline=True,
                  text=message)
                tab.contentAdded()


class NotificationWindow(Window):
    currentMessages: List[Label]

    def __init__(self):
        Window.__init__(self, desktop, position=(AnchorType.TOPCENTERFIXED), autosize=(False,
                                                                                       True), style=(styleDB.notificationWindow))
        self.currentMessages = []
        self.maxMessages = 3
        self.fadeTime = 3

    def reset(self):
        for message in self.currentMessages:
            message.fadeCall.cancel()
            message.destroy()

        self.currentMessages.clear()

    def addMessage(self, messageText, messageType):
        if len(self.currentMessages) < self.maxMessages:
            for tm in self.currentMessages:
                if tm.text == messageText:
                    tm.fadeCall.cancel()
                    tm.renderer.setAlpha(255)
                    tm.renderer.fadeOut(3)
                    tm.fadeCall = reactor.callLater(3, self.freeMessage, tm)
                    return

            message = Label(self, position=(AnchorType.TOPCENTER),
              size=(800, 0),
              autosize=(False, True),
              text=messageText,
              style=(styleDB.errorNotificationLabelStyle if messageType != ChatMessageType.ANNOUNCE else styleDB.announceNotificationLabel),
              multiline=True)
            if messageType == ChatMessageType.ANNOUNCE:
                message.setTextAnchors("left", "center")
            self.currentMessages.append(message)
            if messageType != ChatMessageType.ANNOUNCE:
                message.renderer.fadeOut(3)
            message.fadeCall = reactor.callLater(3 if messageType != ChatMessageType.ANNOUNCE else 8, self.freeMessage, message)
            self.fitToContent()

    def freeMessage(self, widget):
        self.currentMessages.remove(widget)
        widget.destroy()


class Chat:

    def __init__(self):
        self.queue = []
        self.channels = channels.ChannelController()
        self.privateMessages = pm.PrivateMessageController()
        self.window = ChatWindow(self)
        self.ingame = True
        self.notification = NotificationWindow()
        eventManager.registerListener(self)

    def reset(self):
        self.queue.clear()
        self.channels.reset()
        self.privateMessages.reset()
        self.notification.reset()
        self.window.reset()

    def onKeyReturn(self):
        self.toggleChatFocus()

    def toggleChatFocus(self):
        if self.ingame:
            if not desktop.hasFocus():
                desktop.setActive(self.window.chatTxt)
                self.window.chatTxt.setState(ButtonState.DOWN)

    def onKeyDown(self, symbol, modifiers):
        """ This is here to open chat on key """
        if symbol == key.ENTER or symbol == key.RETURN:
            if not self.window.thumb.visible:
                self.toggleChatFocus()

    def onClientTrainerLoaded(self):
        self.window.loadChat()
        self.ingame = True
        self.window.createDropdowns()

    def onBattleMessage(self, messageText, log=True):
        if log == True:
            message = FormattedMessage(self.channels)
            message.style = "BATTLE"
            message.type = ChatMessageType.BATTLE
            message.message = messageText
            self.window.addMessage(message)
        self.notification.addMessage(messageText, "error")

    def onSystemMessage(self, messageText):
        message = FormattedMessage(self.channels)
        message.style = "SYSTEM"
        message.type = ChatMessageType.SYSTEM
        message.message = messageText
        self.window.addMessage(message)

    def onSystemErrorMessage(self, messageText):
        message = FormattedMessage(self.channels)
        message.style = "SYSTEM_ERROR"
        message.type = ChatMessageType.SYSTEM
        message.message = messageText
        self.window.addMessage(message)

    def onShowMessage(self, chatMessage, style, mType):
        if not style:
            style = "DEFAULT"
        if not mType:
            mType = ChatMessageType.SYSTEM
        message = FormattedMessage(self.channels)
        message.style = style
        message.message = chatMessage
        message.type = mType
        self.window.addMessage(message)

    def onJoinChannel(self, channelId, channelName):
        if not self.channels.join(channelId, channelName):
            return
        else:
            message = FormattedMessage(self.channels)
            message.style = "JOIN"
            message.type = ChatMessageType.SYSTEM
            c = self.channels.getChannel(channelId)
            if not c:
                message.message = "Joined Channel [0. Unknown]"
            else:
                message.message = f"Joined Channel [{c.num}. {c.name}]"
        self.window.addMessage(message)
        self.window.createDropdowns(False)

    def onLeaveChannel(self, channelId):
        c = self.channels.getChannel(channelId)
        if not self.channels.leave(channelId):
            return
        else:
            message = FormattedMessage(self.channels)
            message.style = "LEAVE"
            message.type = ChatMessageType.SYSTEM
            if not c:
                message.message = "Left Channel [0. Unknown]"
            else:
                message.message = f"Left Channel [{c.num}. {c.name}]"
        self.window.addMessage(message)
        self.window.createDropdowns()

    def onGroupJoined(self):
        self.window.createDropdowns(False)

    def onAreaReceivedMessage(self, trainerId, charIdType, messageText):
        message = FormattedMessage(self.channels)
        message.message = messageText
        message.trainerId = trainerId
        message.type = ChatMessageType.AREA
        char = charContainer.getCharByIdIfAny(trainerId, charIdType)
        if not char:
            raise Exception("Server sent an area chat message but we don't know about the char who said it. This case should never happen!")
        message.message = messageText
        self._displayMessage(message, char.data.name, char)

    def onReceivedMessage(self, trainerName, channelId, messageType, messageText):
        message = FormattedMessage(self.channels)
        message.message = messageText
        message.type = messageType
        char = None
        if messageType == ChatMessageType.AREA:
            return
        if messageType == ChatMessageType.CHANNEL:
            message.style = "GLOBAL"
            message.channelId = channelId
        elif messageType == ChatMessageType.WHISPER:
            isConfirmation = channelId
            if isConfirmation:
                message.style = "PM_TO"
            else:
                message.style = "PM_FROM"
        elif messageType == ChatMessageType.GUILD:
            message.style = "GUILD"
        elif messageType == ChatMessageType.PARTY:
            pass
        message.style = "PARTY"
        groupMember = sessionService.group.getMemberByName(trainerName)
        if groupMember:
            if groupMember.name != "Unknown":
                char = charContainer.getCharByIdIfAny(groupMember.trainerId, IdRange.PC_TRAINER)
        else:
            if messageType == ChatMessageType.ANNOUNCE:
                message.style = "ANNOUNCE"
                self.window.addMessage(message)
                self.notification.addMessage(message.message, ChatMessageType.ANNOUNCE)
                return
            if messageType == ChatMessageType.SYSTEM:
                message.style = "SYSTEM"
                self.window.addMessage(message)
                return
            self._displayMessage(message, trainerName, char)

    def _displayMessage(self, message, name, char):
        message.name = name
        self.window.addMessage(message)
        if message.type in ChatMessageType.DISPLAYED:
            if char:
                chatMessageController.displayMessage(char, message.type, message.message)
            else:
                print("Warning: Received chat message from character don't know about", message.type, message.message)


chat = Chat()
