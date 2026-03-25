# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\interface\chat\pm.py
"""
Created on Jul 28, 2011

@author: Ragnarok
"""
from shared.container.constants import PMSettings
from client.control.gui import Textbox, Window, Label, ScrollableContainer, Header, Container
import client.data.gui.styleDB as styleDB
from client.data.settings import gameSettings
from shared.container.net import cmsg
from client.data.utils.anchor import AnchorType, Alignment
from shared.container.constants import ChatMessageType
import client.data.font as font
from client.control.net.sending import packetManager
from client.control.service.session import sessionService
from client.interface.social import friendsList
from client.game import desktop
CHATFONT = font.fontDB.getFont("chat")

class PMHeader(Header):

    def __init__(self, parent, name, close=True, minimize=True):
        self.minimized = False
        Header.__init__(self, parent, name, close, minimize)

    def minimizeClick(self, widget, x, y, modifiers):
        if not self.minimized:
            self.minimized = True
            self.parent.scrollBox.hide()
            self.parent.textbox.hide()
            self.parent.setSize(self.width, 0)
            self.parent.fitToContent()
        else:
            self.minimized = False
            self.parent.setSize(self.width, 200)
            self.parent.scrollBox.show()
            self.parent.textbox.show()
            self.parent.fitToContent()


class PMWindow(Window):

    def __init__(self, controller, playerName):
        Window.__init__(self, desktop, position=(100, 100), size=(200, 200), autosize=(True,
                                                                                       True), draggable=True)
        PMHeader(self, playerName, minimize=True, close=True)
        self.userId = 0
        self.playerName = playerName
        self.controller = controller
        self.scrollBox = ScrollableContainer(self, position=(AnchorType.TOPLEFT), size=(178,
                                                                                        140), visible=False)
        self.scrollBox.show()
        self.textbox = Textbox(self, position=(AnchorType.BOTTOMLEFT), size=(178, 20), scrollable=True)
        self.textbox.addCallback("onKeyReturn", self.sendMessage)
        self.scrollBox.fitToContent()
        self.fitToContent()

    def hide(self):
        super().hide()
        self.scrollBox.hide()

    def show(self):
        super().show()
        self.scrollBox.show()

    def close(self):
        self.controller.remove(self.playerName)
        self.hide()

    def printLog(self):
        return

    def sendMessage(self):
        text = self.textbox.text
        if len(text) > 0:
            packetManager.queueSend(cmsg.ChatMessage, (ChatMessageType.WHISPER, self.playerName.encode(), text.encode()))
            self.textbox.text = ""

    def say(self, messageData):
        if messageData.style == "PM_FROM":
            self.header.title.setStyle(styleDB.titleLabelFocusStyle)
            charName = messageData.name
        else:
            charName = sessionService.trainer.data.name
        if charName:
            message = f"{charName}: {messageData.message}"
        else:
            message = messageData.message
        print("messageData.style", messageData.style)
        Label((self.scrollBox.content), position=(AnchorType.TOPLEFT),
          size=(150, 0),
          style=(styleDB.chatStyles[messageData.style]),
          autosize=(False, True),
          multiline=True,
          text=message)
        self.scrollBox.contentAdded()


class PrivateMessageController:

    def __init__(self):
        self.conversations = {}

    def reset(self):
        for window in list(self.conversations.values()):
            window.destroy()

        self.conversations.clear()

    def say(self, messageData):
        config = gameSettings.getPM()
        name = messageData.name
        if config == PMSettings.NONE:
            return False
        else:
            if config == PMSettings.FRIENDS:
                if not friendsList.data.isFriendByName(name):
                    return False
            if name not in self.conversations:
                self.conversations[name] = PMWindow(self, name)
                self.conversations[name].addCallback("onGainFocus", self.nowFocused)
            self.conversations[name].say(messageData)
            return True

    def nowFocused(self, widget):
        widget.header.title.setStyle(styleDB.titleLabelStyle)

    def remove(self, name):
        del self.conversations[name]
