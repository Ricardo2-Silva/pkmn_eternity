# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\interface\group.py
"""
Created on Jul 31, 2011

@author: Chuck, Kami
"""
from client.control.gui import Window, Button, Label, Menu, Thumb, LineRoundedContainer, ScrollableContainer, IconButton, LineTable, Header, Textbox, Thumb
from client.control.system.cache import cacheController
from client.game import desktop
from shared.container.net import cmsg
from client.control.events.event import eventManager
from client.data.gui import styleDB
from shared.controller.net.packetStruct import RawUnpacker
from client.control.service.session import sessionService
from client.data.utils.anchor import AnchorType, Alignment
from client.data.DB import messageDB, mapDB
from shared.container.constants import GroupUpdates, GroupResponses, IdRange, NameLength
from client.control.net.sending import packetManager
from client.render.cache import textureCache
from client.data.utils.color import Color
from client.data.cache import nameCache
from client.data.gui.group import GroupMember
from client.interface.social import friendsList

class GroupInviteWindow(Window):

    def __init__(self):
        Window.__init__(self, desktop, position=(AnchorType.CENTER), size=(160, 105), draggable=True, visible=False)
        self.infoLbl = Label(self, position=(AnchorType.TOPCENTER), text="Enter the name of the player you wish to invite.", size=(150,
                                                                                                                                   0), autosize=(False,
                                                                                                                                                 True), alignment=(Alignment.CENTER), multiline=True)
        self.nameTextbox = Textbox(self, position=(AnchorType.TOPCENTER), size=(120,
                                                                                0))
        self.okBtn = Button(self, position=(AnchorType.CENTERBOTTOM), size=(65, 0), autosize=(False,
                                                                                              True), text="Ok")
        self.cancelBtn = Button(self, position=(AnchorType.CENTERBOTTOM), size=(65,
                                                                                0), autosize=(False,
                                                                                              True), text="Cancel")
        self.okBtn.addCallback("onMouseLeftClick", self.onOkClick)
        self.cancelBtn.addCallback("onMouseLeftClick", self.onCancelClick)
        self.fitToContent()

    def reset(self):
        self.forceHide()

    def onOkClick(self, widget, x, y, modifiers):
        name = self.nameTextbox.text
        if name:
            if len(name) > NameLength.TRAINER or len(name) < 4:
                eventManager.notify("onSystemMessage", "Username is too short")
                self.nameTextbox.text = ""
                return
            packetManager.queueSend(cmsg.GroupInvite, str(name).encode())
            self.close()
        else:
            eventManager.notify("onSystemMessage", "Requires a username.")
            return

    def onCancelClick(self, widget, x, y, modifiers):
        self.close()


class GroupRequestWindow(Window):

    def __init__(self):
        Window.__init__(self, desktop, position=(AnchorType.CENTER), size=(250, 130), draggable=True, visible=False)
        self.infoLbl = Label(self, position=(20, 20), size=(200, 100), text="", autosize=(False,
                                                                                          False), multiline=True)
        self.yesBtn = Button(self, position=(5, 80), size=(100, 26), style=(styleDB.greenButtonStyle), text=(messageDB["ACCEPT"]), autosize=(False,
                                                                                                                                             False))
        self.yesBtn.addCallback("onMouseLeftClick", self.acceptRequest)
        self.noBtn = Button(self, position=(130, 80), size=(100, 26), style=(styleDB.redButtonStyle), text=(messageDB["DENY"]), autosize=(False,
                                                                                                                                          False))
        self.noBtn.addCallback("onMouseLeftClick", self.denyRequest)

    def reset(self):
        self.forceHide()

    def showRequest(self, name):
        self.infoLbl.text = f"{name} wants you to join their group."
        self.show()

    def acceptRequest(self, widget, x, y, modifiers):
        packetManager.queueSend(cmsg.GroupResponse, GroupResponses.REQUEST_ACCEPTED)
        self.hideWindow()

    def denyRequest(self, widget, x, y, modifiers):
        packetManager.queueSend(cmsg.GroupResponse, GroupResponses.REQUEST_DENIED)
        self.hideWindow()

    def hideWindow(self):
        self.hide()


class GroupMenu(Menu):

    def __init__(self):
        Menu.__init__(self, desktop)
        self.member = None
        self.leaderBtn = Button(self, style=(styleDB.menuItemStyle), size=(75, 20), text="Give Leader", autosize=(False,
                                                                                                                  False))
        self.leaderBtn.addCallback("onMouseLeftClick", self.giveLeaderClick)
        self.kickBtn = Button(self, style=(styleDB.menuItemStyle), size=(75, 20), text="Kick", autosize=(False,
                                                                                                         False))
        self.kickBtn.addCallback("onMouseLeftClick", self.kickPlayerClick)
        self.friendBtn = Button(self, style=(styleDB.menuItemStyle), size=(75, 20), text="Add Friend", autosize=(False,
                                                                                                                 False))
        self.friendBtn.addCallback("onMouseLeftClick", self.addFriendClick)
        self.cancelBtn = Button(self, style=(styleDB.menuItemStyle), size=(75, 20), text="Cancel", autosize=(False,
                                                                                                             False))
        self.buttons = (self.leaderBtn, self.kickBtn, self.friendBtn, self.cancelBtn)

    def reset(self):
        self.member = None
        self.forceHide()

    def kickPlayerClick(self, widget, x, y, modifiers):
        packetManager.queueSend(cmsg.GroupUpdate, self.member.trainerId, GroupUpdates.KICKED)

    def giveLeaderClick(self, widget, x, y, modifiers):
        packetManager.queueSend(cmsg.GroupUpdate, self.member.trainerId, GroupUpdates.LEADER)

    def inviteGuild(self):
        packetManager.queueSend(cmsg.GuildInvite, str(self.member.name).encode())

    def addFriendClick(self, widget, x, y, modifiers):
        packetManager.queueSend(cmsg.FriendRequest, str(self.member.name).encode())

    def showMenu(self, member, x, y):
        self.member = member
        print("SHOWING", self.member)
        self.populateMenu()
        self.show()
        self.setActive()
        self.setPosition(x, y)

    def populateMenu(self):
        self.hideAllOptions()
        if sessionService.isGroupLeader():
            if self.member.trainerId != sessionService.group.leaderId:
                self.add(self.leaderBtn)
                self.add(self.kickBtn)
        if friendsList.data.canFriend(self.member.trainerId):
            self.add(self.friendBtn)
        self.add(self.cancelBtn)
        self.fitToContent()


class GroupWindow(Window):
    LINE_HEIGHT = 20

    def __init__(self):
        Window.__init__(self, desktop, position=(AnchorType.TOPRIGHT), size=(100, 210), draggable=True, autosize=(True,
                                                                                                                  True), visible=False)
        self.isLeader = False
        self.lineByMemberId = {}
        self.menu = GroupMenu()
        self.inviteWin = GroupInviteWindow()
        Header(self, "Party", close=False, minimize=True)
        self.thumb = Thumb(self, "Party", position=(AnchorType.RIGHTTOP))
        self.memberArea = LineRoundedContainer(self, position=(AnchorType.TOPCENTER), size=(180,
                                                                                            140), color=(Color.WHITE))
        self.scroll = ScrollableContainer((self.memberArea), size=(50, 130), autosize=(True,
                                                                                       False), visible=False)
        self.inviteBtn = Button(self, position=(AnchorType.LEFTBOTTOM), style=(styleDB.blueButtonStyle), text="Invite", visible=False)
        self.inviteBtn.addCallback("onMouseLeftClick", self.onInviteClick)
        self.disbandBtn = Button(self, position=(AnchorType.RIGHTBOTTOM), style=(styleDB.redButtonStyle), text="Disband", visible=False)
        self.disbandBtn.addCallback("onMouseLeftClick", self.onDisbandClick)
        self.leaveBtn = Button(self, position=(AnchorType.RIGHTBOTTOM), style=(styleDB.redButtonStyle), text="Leave", visible=True)
        self.leaveBtn.addCallback("onMouseLeftClick", self.onLeaveClick)
        self.lineTable = LineTable((self.scroll.content), maxCols=4)
        self.lineTable.setColumns(["usericon", "user", "mapicon", "map"])
        self.lineTable.setInternalMargins(5, 5)
        self.lineTable.setManualFit()
        self.fitToContent()

    def reset(self):
        self.menu.reset()
        self.inviteWin.reset()
        self.lineByMemberId.clear()
        self.lineTable.emptyAndDestroy()
        self.forceHide()

    def show(self):
        super().show()
        self.scroll.show()

    def hide(self):
        super().hide()
        self.scroll.hide()

    def fitToContent(self):
        self.lineTable.fitToContent()
        self.scroll.fitToContent()
        self.memberArea.fitToContent()
        Window.fitToContent(self)

    def onLeaveClick(self, widget, x, y, modifiers):
        packetManager.queueSend(cmsg.GroupUpdate, sessionService.getClientId(), GroupUpdates.LEAVE)

    def onDisbandClick(self, widget, x, y, modifiers):
        packetManager.queueSend(cmsg.GroupUpdate, sessionService.getClientId(), GroupUpdates.DISBAND)

    def onInviteClick(self, widget, x, y, modifiers):
        self.inviteWin.open()

    def onMemberClick(self, widget, x, y, modifiers):
        self.menu.showMenu(widget.member, x, y)

    def _getIcons(self, online):
        if online:
            head = "common/headmale_03"
            earth = "common/earth"
        else:
            head = "common/headmaledisabled_03"
            earth = "common/earthdisabled"
        return (head, earth)

    def addMember(self, member):
        """ Add a player's line. """
        head, earth = self._getIcons(member.status)
        button = self.lineTable.addData(usericon=IconButton((self.lineTable), icon=(textureCache.getGuiImage(head)), size=(0, self.LINE_HEIGHT), style=(styleDB.transparentButtonStyle)),
          user=Label((self.lineTable), text=(member.name), size=(0, self.LINE_HEIGHT), style=(styleDB.leaderLabelStyle if member.trainerId == sessionService.group.leaderId else styleDB.nonLeaderLabelStyle), anchor_y="center"),
          mapicon=IconButton((self.lineTable), icon=(textureCache.getGuiImage(earth)), size=(0, self.LINE_HEIGHT), style=(styleDB.transparentButtonStyle)),
          map=Label((self.lineTable), text=(mapDB.getMapNameById(member.mapId)), size=(0, self.LINE_HEIGHT), anchor_y="center"))
        button.member = member
        button.addCallback("onMouseRightClick", self.onMemberClick)
        self.lineByMemberId[member.trainerId] = button

    def removePlayer(self, member):
        """ Remove a player's line """
        self.lineTable.delLine(self.lineByMemberId[member.trainerId])
        del self.lineByMemberId[member.trainerId]

    def clear(self):
        """ Clear the whole windows. (Member, leader buttons) """
        if self.disbandBtn.visible:
            self.disbandBtn.hide()
        if self.inviteBtn.visible:
            self.inviteBtn.hide()
        self.isLeader = False
        self.lineTable.emptyAndDestroy()
        self.lineByMemberId.clear()
        self.fitToContent()

    def updatePlayer(self, member):
        """ Update the status of a player in the list. """
        line = self.lineByMemberId[member.trainerId]
        mapIcon = self.lineTable.getData(line.row, "mapicon")
        head, earth = self._getIcons(member.status)
        earthIcon = textureCache.getGuiImage(earth)
        if not mapIcon.iconMatches(earthIcon):
            userIcon = self.lineTable.getData(line.row, "usericon")
            userIcon.setIconDefault(textureCache.getGuiImage(head))
            mapIcon.setIconDefault(earthIcon)
        else:
            user = self.lineTable.getData(line.row, "user")
            if user.text != member.name:
                user.text = member.name
            if sessionService.group.leaderId == member.trainerId:
                user.setStyle(styleDB.leaderLabelStyle)
            else:
                user.setStyle(styleDB.nonLeaderLabelStyle)
        map = self.lineTable.getData(line.row, "map")
        mapName = mapDB.getMapNameById(member.mapId)
        if map.text != mapName:
            map.text = mapName

    def populateButtons(self):
        """ Populate the buttons in the windows, depending on the leader state """
        if sessionService.isGroupLeader():
            self.inviteBtn.show()
            self.disbandBtn.show()
        self.fitToContent()

    def depopulateButtons(self):
        if sessionService.isGroupLeader():
            self.inviteBtn.hide()
            self.disbandBtn.hide()
        self.fitToContent()


class GroupController:

    def __init__(self):
        self.window = GroupWindow()
        self.requestWindow = GroupRequestWindow()
        eventManager.registerListener(self)

    def reset(self):
        self.window.reset()
        self.requestWindow.reset()

    def addMember(self, member):
        sessionService.group.addMember(member)
        self.window.addMember(member)
        self.window.fitToContent()

    def updatePlayer(self, member):
        self.window.updatePlayer(member)
        self.window.fitToContent()

    def removePlayer(self, member):
        sessionService.group.delMember(member)
        self.window.removePlayer(member)
        self.window.fitToContent()

    def leaveGroup(self):
        sessionService.group.leave()
        self.window.clear()
        self.window.hide()

    def changeLeaderTo(self, member):
        oldLeader = sessionService.group.getMember(sessionService.group.leaderId)
        sessionService.group.leaderId = member.trainerId
        self.window.updatePlayer(member)
        self.window.updatePlayer(oldLeader)
        if member.trainerId == sessionService.getClientId():
            self.window.populateButtons()
        self.window.fitToContent()

    def onGroupInvite(self, trainerName):
        self.requestWindow.showRequest(trainerName)

    def onGroupOptions(self, groupId, lootMode, expMode):
        return

    def onGroupResponse(self, response):
        if response == GroupResponses.REQUEST_SENT:
            eventManager.notify("onSystemMessage", "Party request was sent.")
        elif response == GroupResponses.REQUEST_ACCEPTED:
            eventManager.notify("onSystemMessage", "Party request was accepted.")
        elif response == GroupResponses.REQUEST_DENIED:
            eventManager.notify("onSystemMessage", "Party request was declined.")
        elif response == GroupResponses.ALREADY_IN_PARTY:
            eventManager.notify("onSystemMessage", "That player is already in a party.")
        elif response == GroupResponses.NOT_ONLINE:
            eventManager.notify("onSystemMessage", "Could not found player, either incorrect or offline.")
        elif response == GroupResponses.NO_REQUESTS:
            eventManager.notify("onSystemMessage", "Player is not currently accepting party requests.")
        elif response == GroupResponses.FULL:
            eventManager.notify("onSystemMessage", "Party is currently full.")

    def onGroupAddPlayer(self, trainerId, name, mapId, onlineStatus):
        member = GroupMember()
        member.trainerId = trainerId
        member.name = name
        member.mapId = mapId
        member.status = onlineStatus
        nameCache.setTrainer(trainerId, name)
        self.addMember(member)
        self.window.fitToContent()

    def onGroupList(self, data):
        """ Creates a group setting all the players in it."""
        unpacker = RawUnpacker(data)
        self.window.clear()
        if sessionService.group.inGroup():
            raise Exception("The player is already in a group!")
        _, sessionService.group.groupId, sessionService.group.lootMode, sessionService.group.expMode, sessionService.group.leaderId, membersCount = unpacker.get("!BHBBHB")
        for _ in range(membersCount):
            member = GroupMember()
            member.trainerId, member.mapId, member.status = unpacker.get("!HHB")
            cacheName = nameCache.getTrainer(member.trainerId)
            if cacheName:
                member.name = cacheName
            else:
                nameCache.addIdToGet(member.trainerId, IdRange.PC_TRAINER)
            self.addMember(member)

        cacheController.requestPCTrainerIds("group")
        self.window.populateButtons()
        self.window.show()
        self.window.fitToContent()
        eventManager.notify("onGroupJoined")

    def onNameQuery(self, charId, charType, name):
        if charType == IdRange.PC_TRAINER:
            member = sessionService.group.getMember(charId)
            if member:
                member.name = name
                self.updatePlayer(member)
                self.window.fitToContent()

    def onGroupUpdate(self, trainerId, action):
        clientId = sessionService.getClientId()
        if trainerId > 0:
            member = sessionService.group.getMember(trainerId)
        if action == GroupUpdates.LEAVE:
            if clientId == trainerId:
                eventManager.notify("onSystemMessage", "You have left the party.")
                self.leaveGroup()
            else:
                eventManager.notify("onSystemMessage", f"{member.name} has left the party.")
        elif action == GroupUpdates.KICKED:
            if clientId == trainerId:
                eventManager.notify("onSystemMessage", "You have been removed from the party.")
                self.leaveGroup()
            else:
                eventManager.notify("onSystemMessage", f"{member.name} has been removed from the party.")
                self.removePlayer(member)
        elif action == GroupUpdates.DISBAND:
            if trainerId:
                eventManager.notify("onSystemMessage", f"{member.name} disbanded the party.")
            else:
                eventManager.notify("onSystemMessage", "The party has been disbanded.")
            self.leaveGroup()
        else:
            if action == GroupUpdates.LEADER:
                if clientId == sessionService.group.leaderId:
                    self.window.depopulateButtons()
                self.changeLeaderTo(member)
        self.window.fitToContent()

    def onPlayerStatusChange(self, trainerId, status, value):
        memberData = sessionService.group.getMember(trainerId)
        if memberData:
            memberData.setStatus(status, value)
            self.updatePlayer(memberData)
            self.window.fitToContent()


groupController = GroupController()
