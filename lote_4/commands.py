# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\interface\chat\commands.py
"""
Created on Jul 28, 2011

@author: Ragnarok
"""
from twisted.internet import threads
from client.control.events.event import eventManager
from shared.container.net import cmsg
from client.control.service.session import sessionService
from shared.container.constants import ChatMessageType, NameLength, GuildEvent, GuildPermissions, Emotes
from client.control.net.sending import packetManager
from shared.controller.net.packetStruct import RawPacker
import time
from client.scene.manager import sceneManager
from utils.bug_reporter import submit_bug_report

class Command(object):

    def __init__(self, commandString, arguments, description, func):
        self.func = func
        self.commandString = commandString
        self.argumentNumber = arguments
        self.description = description


class Commands:

    def __init__(self):
        self._bug_reported = time.time()
        self._reported = False
        self.commandList = {'join':self.joinChat, 
         'w':self.pm, 
         'p':self.party, 
         'leave':self.leaveChat, 
         'invite':self.invite, 
         'where':self.where, 
         'ping':self.ping, 
         'fps':self.fps, 
         'emotes':self.emotes, 
         'bug':self.bug, 
         'commands':self.commands, 
         'trade':self.trade, 
         'effects':self.effects, 
         'ignore':self.ignore, 
         'unignore':self.unignore}

    def commands(self, values):
        eventManager.notify("onSystemMessage", "Command List (all use / prefix)")
        commands = " ".join(list(self.commandList.keys()))
        eventManager.notify("onSystemMessage", commands)

    def trade(self, values):
        from client.interface.trade import trade
        trade.window.toggle()

    def effects(self, values):
        eventManager.notify("onCharPlayEffect", sessionService.getSelectedChar(), values[0])

    def emotes(self, values):
        eventManager.notify("onSystemMessage", "Emote List (all use / prefix)")
        emoteList = " ".join([emote.value for emote in list(Emotes)])
        eventManager.notify("onSystemMessage", emoteList)

    def ignore(self, values):
        name = values[0]
        if len(values) != 1:
            eventManager.notify("onSystemMessage", "Not a username")
            return
        if len(name) > NameLength.TRAINER or len(name) < 3:
            eventManager.notify("onSystemMessage", "Username is too short.")
            return
        from client.interface.social import friendsList
        if friendsList.data.isFriendByName(name):
            eventManager.notify("onSystemMessage", "Cannot ignore friends.")
            return
        if friendsList.data.isIgnoredByName(name):
            eventManager.notify("onSystemMessage", "Player is already on the ignore list.")
            return
        packetManager.queueSend(cmsg.FriendIgnoreAdd, str(name).encode())

    def unignore(self, values):
        name = values[0]
        if len(values) != 1:
            eventManager.notify("onSystemMessage", "Not a username")
            return
        if len(name) > NameLength.TRAINER or len(name) < 3:
            eventManager.notify("onSystemMessage", "Username is too short.")
            return
        from client.interface.social import friendsList
        friendData = friendsList.getIgnoredByName(name)
        if not friendData:
            eventManager.notify("onSystemMessage", "Player is not on your ignore list.")
            return
        packetManager.queueSend(cmsg.FriendIgnoreDel, friendData.trainerId)

    def bug(self, values):
        if not values:
            eventManager.notify("onSystemMessage", "Please enter a detailed description of the bug to submit a report.")
            return
        else:
            if len(values) < 4:
                eventManager.notify("onSystemMessage", "Your description was too short, please enter a little bit more detail.")
                return
            if time.time() - self._bug_reported < 5 or self._reported:
                eventManager.notify("onSystemMessage", "You cannot submit another bug report this quickly after another.")
                return
        message = " ".join(values)
        self.submitReport(message)

    def submitReport(self, description):
        self._reported = True
        eventManager.notify("onSystemMessage", "Submitting bug report...")
        d = threads.deferToThread(submit_bug_report, description, sessionService.getClientTrainer().name, True)
        d.addCallback(self._bugReportCallback)
        return d

    def _bugReportCallback(self, result):
        succeeded, response = result
        if succeeded is True:
            eventManager.notify("onSystemMessage", f"Your report was successfully submitted. Bug ID #{response}")
        elif succeeded is False:
            eventManager.notify("onSystemMessage", "Bug report failed to submit, server may be temporarily down. Please try again later.")
        else:
            eventManager.notify("onSystemMessage", "Bug report failed to submit due to error, please try again later.")
        self._reported = False

    def fps(self, values):
        sceneManager.toggleFps()

    def ping(self, values):
        sessionService.pingTime = time.perf_counter()
        packetManager.ping()

    def party(self, values):
        message = " ".join(values)
        if len(message) > 1:
            if sessionService.group.inGroup():
                packetManager.queueSend(cmsg.ChatMessage, (ChatMessageType.PARTY, b'', message.encode()))

    def guild(self, values):
        message = " ".join(values)
        if len(message) > 1:
            if sessionService.guild.inGuild():
                if sessionService.guild.hasPermission(GuildPermissions.TALK):
                    packetManager.queueSend(cmsg.ChatMessage, (ChatMessageType.GUILD, b'', message.encode()))

    def where(self, values):
        mapData = sessionService.getClientData().map
        fileName = mapData.information.fileName
        x, y = sessionService.getClientData().getPosition()
        eventManager.notify("onSystemMessage", f"Coordinates: ({int(x)}, {int(y)}). Map: {mapData.name} | {fileName}")

    def joinChat(self, values):
        if values:
            channelName = values[0]
            if len(channelName) > NameLength.CHANNELS:
                eventManager.notify("onSystemMessage", "Channel name must be 8 characters or less.")
                return
            if self.channels.getChannelByName(channelName):
                eventManager.notify("onSystemMessage", "You are already in that channel.")
                return False
            packetManager.queueSend(cmsg.JoinChat, str(channelName).encode())

    def leaveChat(self, values):
        if values:
            channel = values[0]
            try:
                channel = int(channel)
                if channel <= 0:
                    return False
                channel = self.channels.numToName(channel)
                if not channel:
                    return False
            except ValueError:
                pass

            if not self.channels.getChannelByName(channel):
                return False
            packetManager.queueSend(cmsg.LeaveChat, str(channel).encode())
            return True
        else:
            return False

    def pm(self, values):
        if len(values) < 2:
            eventManager.notify("onSystemMessage", "Please add a message or username.")
            return
        else:
            name = values[0]
            message = " ".join(values[1:])
            if len(name) > NameLength.TRAINER or len(name) < 2:
                eventManager.notify("onSystemMessage", "Username is too short.")
                self.chatTxt.text = ""
                return
            if len(message) < 1:
                eventManager.notify("onSystemMessage", "Message is not long enough")
                return
        packetManager.queueSend(cmsg.ChatMessage, (ChatMessageType.WHISPER, name.encode(), message.encode()))

    def online(self, values):
        packetManager.queueSend(cmsg.OnlineCount, None)

    def invite(self, values):
        if values:
            name = values[0]
            if len(name) > NameLength.TRAINER or len(name) < 4:
                eventManager.notify("onSystemMessage", "Username is too short")
                self.chatTxt.text = ""
                return
            packetManager.queueSend(cmsg.GroupInvite, str(name).encode())
        else:
            eventManager.notify("onSystemMessage", "Requires a username.")
            return

    def guildInvite(self, values):
        if values:
            if sessionService.guild.inGuild():
                name = values[0]
                if len(name) > NameLength.TRAINER or len(name) < 4:
                    eventManager.notify("onSystemMessage", "Username is too short")
                    self.chatTxt.text = ""
                    return
                if sessionService.guild.hasPermission(GuildPermissions.INVITE):
                    packetManager.queueSend(cmsg.GuildInvite, str(name).encode())
                else:
                    eventManager.notify("onSystemMessage", "You are not in a guild.")
        else:
            eventManager.notify("onSystemMessage", "Requires a username.")
            return

    def guildCreate(self, values):
        if values:
            if not sessionService.guild.inGuild():
                packetManager.queueSend(cmsg.GuildCreate, str(values[0]).encode())

    def guildLeave(self, values):
        if sessionService.guild.inGuild():
            packetManager.queueSend(cmsg.GuildUpdate, 0, GuildEvent.LEFT)

    def guildMotd(self, values):
        if sessionService.guild.inGuild():
            packer = RawPacker()
            packer.pack("!B", cmsg.GuildMotd)
            packer.packString(str(" ".join(values))[:200])
            packetManager.sendRaw(packer.packet)

    def stuck(self, values):
        sessionService.trainer.checkIfStuck()
