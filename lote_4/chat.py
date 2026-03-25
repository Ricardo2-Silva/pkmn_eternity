# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\data\system\chat.py
import os
from shared.container.constants import ChatMessageType, NameLength
import ujson
defaultChatSettings = {'channels':{'1':"General", 
  '2':"Trade"}, 
 'tabs':{"Default": {'allowed_messages':ChatMessageType.CLIENT, 
              'allowed_channels':[
               1, 2]}}}

class TabData:

    def __init__(self):
        self.name = "Default"
        self.settings = {(ChatMessageType.AREA): False, 
         (ChatMessageType.CHANNEL): False, 
         (ChatMessageType.WHISPER): False, 
         (ChatMessageType.PARTY): False, 
         (ChatMessageType.GUILD): False, 
         (ChatMessageType.SYSTEM): False, 
         (ChatMessageType.BATTLE): False}
        self.channels = []

    def toString(self):
        """ Convert to writable """
        return {'allowed_messages':[message for message, setting in self.settings.items() if setting is True],  'allowed_channels':self.channels}


class ChatManager:

    def __init__(self):
        self.tabs = {}
        self.channels = {}
        self.config = None

    def setFilePath(self, path):
        self.file = os.path.join(path, "chat.cfg")
        self.loadConfig()

    def loadConfig(self):
        try:
            with open(self.file, "r") as fp:
                self.config = ujson.load(fp)
        except ValueError:
            print("WARNING: Failed to load chat config, creating new one.")
            self._createDefault()
        except FileNotFoundError:
            print("WARNING: Chat config not found, creating new one.")
            self._createDefault()

        try:
            self.loadChannels()
            self.loadTabs()
        except KeyError:
            print("WARNING: Failed to load chat config, incorrect data.")
            self._createDefault()
            self.loadConfig()

    def _createDefault(self):
        self.config = defaultChatSettings.copy()
        with open(self.file, "w") as fp:
            ujson.dump(defaultChatSettings, fp)

    def getTabs(self):
        return self.tabs.values()

    def getChannels(self):
        return self.channels.values()

    def loadChannels(self):
        for channelId, name in self.config["channels"].items():
            try:
                channelId = int(channelId)
            except:
                continue

            if len(name) <= NameLength.CHANNELS and channelId < 255 and channelId > 0:
                self.channels[channelId] = name

    def loadTabs(self):
        for tabName in self.config["tabs"]:
            self.config["tabs"][tabName]["allowed_channels"]
            tabData = TabData()
            tabData.name = tabName
            for messageType in self.config["tabs"][tabName]["allowed_messages"]:
                tabData.settings[messageType] = True

            for channelId in self.config["tabs"][tabName]["allowed_channels"]:
                if channelId in self.channels:
                    tabData.channels.append(channelId)

            self.tabs[tabName] = tabData

        if not self.tabs:
            data = TabData()
            for message in data.settings:
                data.settings[message] = True

            for channelId in self.channels:
                data.channels.append(channelId)

            self.tabs[data.name] = data
            self.save()

    def addChannel(self, channelId, channelName):
        if channelId not in self.channels:
            self.channels[channelId] = channelName
            for tab in self.tabs.values():
                if channelId not in tab.channels:
                    tab.channels.append(channelId)

        self.save()

    def removeChannel(self, channelId):
        if channelId in self.channels:
            for tab in self.tabs.values():
                if channelId in list(tab.channels):
                    tab.channels.remove(channelId)
                    if channelId in self.config["tabs"][tab.name]["allowed_channels"]:
                        self.config["tabs"][tab.name]["allowed_channels"].remove(channelId)
                    break

            del self.config["channels"][str(channelId)]
            del self.channels[channelId]
        self.save()

    def renameTab(self, tab, name):
        del self.config["tabs"][tab.name]
        del self.tabs[tab.name]
        tab.name = name
        self.tabs[tab.name] = tab
        self.save()

    def save(self):
        for tab in self.tabs.values():
            self.config["tabs"][tab.name] = tab.toString()

        for channelId, name in self.channels.items():
            self.config["channels"][str(channelId)] = name

        with open(self.file, "w") as fp:
            ujson.dump(self.config, fp)

    def deleteTab(self, tab):
        del self.tabs[tab.name]
        del self.config["tabs"][tab.name]
        self.save()

    def createNewTab(self, name):
        data = TabData()
        data.name = name
        self.tabs[data.name] = data
        for message in data.settings:
            data.settings[message] = True

        for channelId in self.channels:
            data.channels.append(channelId)

        self.save()
        return data


chatConfig = ChatManager()
# global chatConfig ## Warning: Unused global
