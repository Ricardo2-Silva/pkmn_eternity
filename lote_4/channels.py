# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\interface\chat\channels.py
"""
Created on Jul 28, 2011

@author: Ragnarok
"""
from typing import Dict, Any, Optional
from client.data.system.chat import chatConfig

class ChannelData:

    def __init__(self, id, num, name):
        self.id = id
        self.name = name
        self.num = num

    def __repr__(self):
        return f"Channel(id={self.id}, name={self.name}, clientId={self.num})"


class ChannelController:
    channels: Dict[(int, ChannelData)]

    def __init__(self):
        self.channels = {}
        self.clientNums = {}

    def reset(self):
        self.channels.clear()
        self.clientNums.clear()

    def join(self, channelId, channelName):
        exists = None
        for id in chatConfig.channels:
            name = chatConfig.channels[id]
            if name == channelName:
                exists = id
                break

        if exists:
            num = exists
        else:
            num = self.availableNum()
        c = ChannelData(channelId, num, channelName)
        self.channels[channelId] = c
        self.clientNums[num] = c
        chatConfig.addChannel(c.num, c.name)
        return True

    def leave(self, channelId):
        c = self.getChannel(channelId)
        print("LEAVING CHANNEL?", c)
        if c:
            del self.clientNums[c.num]
            del self.channels[c.id]
            chatConfig.removeChannel(c.num)
            return True
        else:
            return False

    def getChannel(self, channelId):
        if channelId in self.channels:
            return self.channels[channelId]
        else:
            return

    def getAllChannels(self):
        return self.channels.values()

    def getChannelByNum(self, clientId):
        if clientId in self.clientNums:
            return self.clientNums[clientId]
        else:
            return

    def getChannelByName(self, channelName):
        for channel in self.channels.values():
            if channelName == channel.name:
                return channel

        return

    def numToName(self, num):
        if num in self.clientNums:
            return self.clientNums[num].name
        else:
            return

    def numToId(self, num):
        if num in self.clientNums:
            return self.clientNums[num].id
        else:
            return

    def idToName(self, id):
        if id in self.channels:
            return self.channels[id].name
        else:
            return

    def idToNum(self, id):
        if id in self.channels:
            return self.channels[id].num
        else:
            return

    def availableNum(self):
        """Finds available channel number, used in client id to game_server id conversion."""
        num = None
        i = 1
        while not num:
            if i not in self.clientNums:
                num = i
                break
            i += 1

        return num
