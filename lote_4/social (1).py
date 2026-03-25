# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\interface\social.py
"""
Created on Jul 29, 2011

@author: Ragnarok
"""
from shared.controller.net import packetStruct as ps
from shared.container.constants import IdRange
from client.render.cache import textureCache
from client.control.gui import Textbox, Window, Label, Button, IconButton, ScrollableContainer, Menu, Tabs, LineTable, LineRoundedContainer, Header
from client.game import desktop
import client.data.gui.styleDB as styleDB
from client.control.events.event import eventManager
from shared.container.net import cmsg
from client.data.DB import messageDB, mapDB
from client.control.service.session import sessionService
from client.data.utils.anchor import AnchorType
from shared.container.constants import PlayerStatus, FriendFlag
from client.control.net.sending import packetManager
from client.data.cache import nameCache
from client.data.utils.color import Color
from client.data.gui.social import FriendData, SocialData
from client.data.gui.button import TextboxType
from client.control.system.cache import cacheController
REQUEST_SENT = 0
REQUEST_ACCEPTED = 1
REQUEST_DENIED = 2

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

    def showRequest(self, name):
        self.infoLbl.text = f"{name} would like to be friends."
        self.show()

    def acceptRequest(self, widget, x, y, modifiers):
        packetManager.queueSend(cmsg.FriendResponse, REQUEST_ACCEPTED)
        self.hideWindow()

    def denyRequest(self, widget, x, y, modifiers):
        packetManager.queueSend(cmsg.FriendResponse, REQUEST_DENIED)
        self.hideWindow()

    def hideWindow(self):
        self.hide()


class FriendMenu(Menu):

    def __init__(self):
        Menu.__init__(self, desktop)
        self.friendData = None
        self.removeFriendBtn = Button(self, style=(styleDB.menuItemStyle), size=(75,
                                                                                 20), text="Remove", autosize=(False,
                                                                                                               False))
        self.removeFriendBtn.addCallback("onMouseLeftClick", self.removeFriend)
        self.cancelBtn = Button(self, style=(styleDB.menuItemStyle), size=(75, 20), text="Cancel", autosize=(False,
                                                                                                             False))
        self.buttons = (self.removeFriendBtn, self.cancelBtn)

    def reset(self):
        self.friendData = None
        self.closeWindow()

    def removeFriend(self, widget, x, y, modifiers):
        if self.friendData.flags & FriendFlag.IGNORED:
            packetManager.queueSend(cmsg.FriendIgnoreDel, self.friendData.trainerId)
        else:
            if self.friendData.flags & FriendFlag.FRIEND:
                packetManager.queueSend(cmsg.FriendDelete, self.friendData.trainerId)
        self.closeWindow()

    def closeWindow(self):
        if self.visible:
            for button in self.buttons:
                if button.visible:
                    button.hide()

            self.hide()

    def showFriend(self, friendData, x, y, modifiers):
        self.friendData = friendData
        self.populateMenu()
        self.show()
        self.setActive()
        self.setPosition(x, y)

    def populateMenu(self):
        self.hideAllOptions()
        self.add(self.removeFriendBtn)
        self.add(self.cancelBtn)
        self.fitToContent()


class FriendList:

    def __init__(self):
        self.window = FriendsWindow(self)
        self.requestWindow = GroupRequestWindow()
        eventManager.registerListener(self)
        self.data = SocialData()

    def reset(self):
        self.window.reset()
        self.data.reset()

    def onHotkeyPress(self, hotkeyName):
        if hotkeyName == "friends":
            self.window.toggle()

    def onFriendRequest(self, trainerName):
        self.requestWindow.showRequest(trainerName)

    def onFriendAdd(self, trainerId, trainerName, status, mapId):
        f = self.data.getFriend(trainerId)
        if not f:
            f = FriendData()
        f.trainerId = trainerId
        f.name = trainerName
        f.status = status
        f.mapId = mapId
        f.flags = f.flags | FriendFlag.FRIEND
        nameCache.setTrainer(f.trainerId, f.name)
        self.data.addFriend(f)
        self.window.addButtonFriend(f)
        self.window.fitToContentByTab()
        eventManager.notify("onSystemMessage", f"{f.name} has become your friend.")

    def onFriendRemove(self, trainerId):
        self.data.delFriend(trainerId)
        self.window.removeButton(trainerId, flag=(FriendFlag.FRIEND))
        self.window.fitToContentByTab()

    def onIgnoreAdd(self, trainerId, trainerName):
        f = self.data.getIgnored(trainerId)
        if not f:
            f = FriendData()
        f.trainerId = trainerId
        f.name = trainerName
        f.flags = f.flags | FriendFlag.IGNORED
        nameCache.setTrainer(f.trainerId, f.name)
        self.data.addIgnored(f)
        self.window.addButtonIgnored(f)
        self.window.fitToContentByTab()
        eventManager.notify("onSystemMessage", f"{f.name} added to ignore.")

    def onIgnoreRemove(self, trainerId):
        self.data.delIgnored(trainerId)
        self.window.removeButton(trainerId, flag=(FriendFlag.IGNORED))
        self.window.fitToContentByTab()

    def onFriendList(self, data):
        up = ps.RawUnpacker(data)
        _, size = up.get("!BB")
        for _ in range(size):
            f = FriendData()
            f.trainerId, f.mapId, f.status, f.flags = up.get("!IHBB")
            cacheName = nameCache.getTrainer(f.trainerId)
            if cacheName:
                f.name = cacheName
            else:
                nameCache.addIdToGet(f.trainerId, IdRange.PC_TRAINER)
            if f.flags & FriendFlag.FRIEND:
                self.data.addFriend(f)
            if f.flags & FriendFlag.IGNORED:
                self.data.addIgnored(f)

        cacheController.requestPCTrainerIds("friends")
        self.window.populateTables()

    def onNameQuery(self, charId, charType, name):
        if charType == IdRange.PC_TRAINER:
            friendData = self.data.getFriend(charId)
            if friendData:
                friendData.name = name
                self.window.updatePlayer(friendData)
            ignoreData = self.data.getIgnored(charId)
            if ignoreData:
                ignoreData.name = name
                self.window.updatePlayer(ignoreData)
            self.window.fitToContentByTab()

    def addFriend(self, trainerName):
        self.window.addFriend(trainerName)

    def onPlayerStatusChange(self, trainerId, status, value):
        friendData = self.data.getFriend(trainerId)
        if friendData:
            friendData.setStatus(status, value)
            self.window.updatePlayer(friendData)
            self.window.fitToContentByTab()


class FriendsWindow(Window):
    FRIENDS = 0
    IGNORED = 1

    def __init__(self, control):
        Window.__init__(self, desktop, position=(AnchorType.CENTER), size=(200, 100), draggable=True, visible=False, autosize=(True,
                                                                                                                               True))
        Header(self, "Friends", close=True)
        self.headOnline = textureCache.getGuiImage("common/headmale")
        self.worldOnline = textureCache.getGuiImage("icons/earth")
        self.headOffline = textureCache.getGuiImage("common/headmaledisabled")
        self.worldOffline = textureCache.getGuiImage("icons/earthdisabled")
        self.control = control
        self.tabControl = Tabs(self, desktop)
        self.currentTab = self.FRIENDS
        self.friendMenu = FriendMenu()
        self.memberArea = LineRoundedContainer(self, position=(AnchorType.TOPCENTER), size=(220,
                                                                                            140), color=(Color.WHITE))
        self.friendsBtn = self.tabControl.addTab("Friends")
        self.friendsBtn.addCallback("onMouseLeftClick", self.showFriends)
        self.ignoreBtn = self.tabControl.addTab("Ignored")
        self.ignoreBtn.addCallback("onMouseLeftClick", self.showIgnored)
        self.addUserTxt = Textbox(self, position=(AnchorType.BOTTOMLEFT), size=(100,
                                                                                0), text="Add Friend", type=(TextboxType.RESET_ON_CLICK))
        self.addUserTxt.addCallback("onKeyReturn", self.addUser)
        self.addUserBtn = Button(self, position=(AnchorType.BOTTOMRIGHT), size=(50,
                                                                                0), text="Add", autosize=(False,
                                                                                                          True))
        self.addUserBtn.addCallback("onMouseLeftClick", self.addUser)
        self.friendScrollBox = ScrollableContainer((self.memberArea), position=(0,
                                                                                0), size=(210,
                                                                                          130), visible=False)
        self.ignoreScrollBox = ScrollableContainer((self.memberArea), position=(0,
                                                                                0), size=(210,
                                                                                          130), visible=False)
        self.friendTable = LineTable((self.friendScrollBox.content), maxCols=3)
        self.friendTable.setColumns(['usericon', 'user', 'mapicon', 'map', 'status'])
        self.friendTable.setInternalMargins(5, 5)
        self.ignoreTable = LineTable((self.ignoreScrollBox.content), maxCols=1)
        self.ignoreTable.setColumns(["user"])
        self.ignoreTable.setInternalMargins(5, 5)
        self.tabControl.fitToContent()
        self.fitToContent()

    def reset(self):
        self.currentTab = self.FRIENDS
        self.friendMenu.reset()
        self.friendTable.emptyAndDestroy()
        self.ignoreTable.emptyAndDestroy()
        if self.visible:
            self.hide()

    def show(self):
        super().show()
        self.tabControl.show()
        if self.currentTab is self.FRIENDS:
            self.friendScrollBox.show()
            if self.ignoreScrollBox.visible:
                self.ignoreScrollBox.hide()
        else:
            if self.friendScrollBox.visible:
                self.friendScrollBox.hide()
            self.ignoreScrollBox.show()

    def hide(self):
        super().hide()
        print("HIDING?")
        self.tabControl.hide()
        if self.friendScrollBox.visible:
            self.friendScrollBox.hide()
        if self.ignoreScrollBox.visible:
            self.ignoreScrollBox.hide()

    def fitToContentIgnored(self):
        self.ignoreTable.fitToContent()
        self.ignoreScrollBox.fitToContent()
        self.memberArea.fitToContent()
        Window.fitToContent(self)

    def fitToContentFriends(self):
        self.friendTable.fitToContent()
        self.friendScrollBox.fitToContent()
        self.memberArea.fitToContent()
        Window.fitToContent(self)

    def toggle(self):
        super().toggle()
        self.fitToContentByTab()

    def fitToContentByTab(self):
        if self.currentTab == self.FRIENDS:
            self.fitToContentFriends()
        else:
            self.fitToContentIgnored()

    def showIgnored(self, widget, x, y, modifiers):
        if self.currentTab != self.IGNORED:
            self.currentTab = self.IGNORED
            self.friendScrollBox.hide()
            self.ignoreScrollBox.show()
            if self.addUserTxt.text == "Add Friend":
                self.addUserTxt.text = "Ignore user"
        self.fitToContentIgnored()

    def showFriends(self, widget, x, y, modifiers):
        if self.currentTab != self.FRIENDS:
            self.currentTab = self.FRIENDS
            self.ignoreScrollBox.hide()
            self.friendScrollBox.show()
            if self.addUserTxt.text == "Ignore user":
                self.addUserTxt.text = "Add Friend"
        self.fitToContentFriends()

    def populateTables(self):
        for friend in self.control.data.getFriends():
            self.addButtonFriend(friend)

        for friend in self.control.data.getIgnoreds():
            self.addButtonIgnored(friend)

        self.fitToContentByTab()

    def getFriendLine(self, trainerId):
        for line in self.friendTable.getLines():
            if line.friendData.trainerId == trainerId:
                return line

        return

    def getIgnoreLine(self, trainerId):
        for line in self.ignoreTable.getLines():
            if line.friendData.trainerId == trainerId:
                return line

        return

    def statusToText(self, status):
        return PlayerStatus.statusText[status]

    def addButtonFriend(self, friendData):
        if friendData.flags & FriendFlag.FRIEND:
            h = 20
            line = self.friendTable.addData(usericon=IconButton((self.friendTable), icon=(self.headOnline if friendData.status else self.headOffline), size=(0, h), style=(styleDB.transparentButtonStyle)),
              user=Label((self.friendTable), text=(friendData.name), size=(0, h), anchor_y="center"),
              mapicon=IconButton((self.friendTable), icon=(self.worldOnline if friendData.status else self.worldOffline), size=(0, h), style=(styleDB.transparentButtonStyle)),
              map=Label((self.friendTable), text=(mapDB.getMapNameById(friendData.mapId)), size=(0, h), anchor_y="center"),
              status=Label((self.friendTable), text=(self.statusToText(friendData.status)), size=(0, h), anchor_y="center"))
            line.friendData = friendData
            line.addCallback("onMouseRightClick", self.showFriendMenu)

    def addButtonIgnored(self, friendData):
        if friendData.flags & FriendFlag.IGNORED:
            line = self.ignoreTable.addData(user=Label((self.ignoreTable), text=(friendData.name)))
            line.friendData = friendData
            line.addCallback("onMouseRightClick", self.showFriendMenu)

    def showFriendMenu(self, widget, x, y, modifiers):
        if widget.friendData:
            self.friendMenu.showFriend(widget.friendData, x, y, modifiers)

    def removeButton(self, trainerId, flag=FriendFlag.FRIEND):
        if flag == FriendFlag.FRIEND:
            line = self.getFriendLine(trainerId)
            self.friendTable.delLine(line)
        elif flag == FriendFlag.IGNORED:
            line = self.getIgnoreLine(trainerId)
            self.ignoreTable.delLine(line)

    def updatePlayer(self, friendData):
        if friendData.flags & FriendFlag.FRIEND:
            line = self.getFriendLine(friendData.trainerId)
            widget = self.friendTable.getData(line.row, "usericon")
            if friendData.status == PlayerStatus.OFFLINE:
                widget.setIconNormal(self.headOffline)
            else:
                widget.setIconNormal(self.headOnline)
            widget = self.friendTable.getData(line.row, "status")
            if widget.text != self.statusToText(friendData.status):
                widget.text = self.statusToText(friendData.status)
            widget = self.friendTable.getData(line.row, "user")
            if friendData.name != widget.text:
                widget.text = friendData.name
            mapWidget = self.friendTable.getData(line.row, "map")
            mapName = mapDB.getMapNameById(friendData.mapId)
            if mapWidget.text != mapName:
                mapWidget.text = mapName
            widget = self.friendTable.getData(line.row, "mapicon")
            if friendData.status == PlayerStatus.OFFLINE:
                widget.setIconNormal(self.worldOffline)
            else:
                widget.setIconNormal(self.worldOnline)
        elif friendData.flags & FriendFlag.IGNORED:
            pass
        line = self.getIgnoreLine(friendData.trainerId)
        widget = self.ignoreTable.getData(line.row, "user")
        if friendData.name != widget.text:
            widget.text = friendData.name

    def addUser(self, widget, x, y, modifiers):
        text = self.addUserTxt.text
        self.addFriend(text, True if self.currentTab == self.FRIENDS else False)

    def addFriend(self, trainerName, isFriend=True):
        if len(trainerName) > 2:
            if trainerName.lower() == sessionService.getClientData().name.lower():
                eventManager.notify("onSystemMessage", "You can't be your own friend.")
                return
            else:
                if self.control.data.isFriendByName(trainerName):
                    if self.currentTab == self.FRIENDS:
                        return
                if self.control.data.isIgnoredByName(trainerName):
                    if self.currentTab == self.IGNORED:
                        return
            packetManager.queueSend(cmsg.FriendRequest if isFriend else cmsg.FriendIgnoreAdd, str(trainerName).encode())


friendsList = FriendList()
