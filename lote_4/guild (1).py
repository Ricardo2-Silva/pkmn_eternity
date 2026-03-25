# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\interface\guild.py
"""
Created on Aug 11, 2011

@author: Ragnarok
"""
from client.control.net.sending import packetManager
from client.control.system.cache import cacheController
from client.data.cache import nameCache
from client.render.cache import textureCache
from client.data.gui.guild import GuildRank, GuildMember
from client.data.utils.color import Color
from client.control.gui import Window, Button, Label, ScrollableContainer, Checkbox, Textbox, DropDown, Menu, Tabs, LineTable, IconButton, Header, LineRoundedContainer
from client.game import desktop
from shared.container.net import cmsg
from client.control.events.event import eventManager
from client.data.gui import styleDB
from shared.controller.net.packetStruct import RawUnpacker
from client.control.service.session import sessionService
from client.data.utils.anchor import AnchorType, Alignment
from client.data.DB import messageDB, mapDB
from shared.container.constants import GuildPermissions, GuildResponses, GuildEvent, NameLength, IdRange, PlayerStatus

class GuildMenu(Menu):

    def __init__(self):
        Menu.__init__(self, desktop)
        self.memberData = None
        self.leaderBtn = Button(self, style=(styleDB.menuItemStyle), size=(75, 20), text="Give Leader", autosize=(False,
                                                                                                                  False))
        self.kickBtn = Button(self, style=(styleDB.menuItemStyle), size=(75, 20), text="Kick", autosize=(False,
                                                                                                         False))
        self.kickBtn.addCallback("onMouseLeftClick", self.kickMember)
        self.promoteBtn = Button(self, style=(styleDB.menuItemStyle), size=(75, 20), text="Promote", autosize=(False,
                                                                                                               False))
        self.promoteBtn.addCallback("onMouseLeftClick", self.promoteMember)
        self.demoteBtn = Button(self, style=(styleDB.menuItemStyle), size=(75, 20), text="Demote", autosize=(False,
                                                                                                             False))
        self.demoteBtn.addCallback("onMouseLeftClick", self.demoteMember)
        self.cancelBtn = Button(self, style=(styleDB.menuItemStyle), size=(75, 20), text="Cancel", autosize=(False,
                                                                                                             False))
        self.buttons = (self.kickBtn, self.promoteBtn, self.demoteBtn, self.cancelBtn)

    def kickMember(self, widget, x, y, modifiers):
        packetManager.queueSend(cmsg.GuildUpdate, self.memberData.trainerId, GuildEvent.REMOVED)

    def promoteMember(self, widget, x, y, modifiers):
        packetManager.queueSend(cmsg.GuildUpdate, self.memberData.trainerId, GuildEvent.PROMOTED)

    def demoteMember(self, widget, x, y, modifiers):
        packetManager.queueSend(cmsg.GuildUpdate, self.memberData.trainerId, GuildEvent.DEMOTED)

    def closeWindow(self):
        if self.visible:
            for button in self.buttons:
                if button.visible:
                    button.hide()

            self.hide()

    def showMember(self, memberData, x, y):
        self.memberData = memberData
        self.populateMenu()
        self.show()
        self.setActive()
        self.setPosition(x, y)

    def populateMenu(self):
        self.hideAllOptions()
        if sessionService.guild.canAdjustPlayer(sessionService.guild.getMember(sessionService.getClientId()), self.memberData):
            if sessionService.guild.hasPermission(GuildPermissions.KICK):
                self.add(self.kickBtn)
            else:
                if sessionService.guild.hasPermission(GuildPermissions.PROMOTE):
                    if self.memberData.rank.id - 1 > 0:
                        self.add(self.promoteBtn)
                if sessionService.guild.hasPermission(GuildPermissions.DEMOTE):
                    if sessionService.guild.rankExists(self.memberData.rank.id + 1):
                        self.add(self.demoteBtn)
        self.add(self.cancelBtn)
        self.fitToContent()


class GuildInfo:

    def __init__(self, window):
        self.window = window
        self.motdBox = Label(window, position=(0, 0), size=(170, 0), visible=False, autosize=(False,
                                                                                              True), multiline=True)
        self.motdBox.setTextAnchor(AnchorType.LEFT)
        self.controlBtn = Button(window, position=(0, 100), text="Guild Control")
        self.controlBtn.addCallback("onMouseLeftClick", self._controlShow)
        self.controlBtn.disableEvents()
        self.infoBtn = window.tabControl.addTab("Information")
        self.infoBtn.addCallback("onMouseLeftClick", self._infoShow)
        self.window.fitToContent()

    def clearGuild(self):
        if self.controlBtn.isEventsEnabled():
            self.controlBtn.disableEvents()

    def _controlShow(self, widget, x, y, modifiers):
        self.window.leaderControl.showControl()

    def _infoShow(self, widget, x, y, modifiers):
        self.window.hideTab()
        self.show()
        self.window.fitToContent()
        self.window.header.updatePosition()

    def setInfo(self):
        self.window.setHeaderTitle(f"{sessionService.guild.name}  |   Online: {sessionService.guild.onlineCount()}")
        self.motdBox.text = sessionService.guild.motd
        if sessionService.guild.isLeader(sessionService.getClientId()):
            self.controlBtn.enableEvents()
        self.window.fitToContent()

    def show(self):
        self.window.currentTab = self
        self.motdBox.show()
        self.controlBtn.show()

    def hide(self):
        self.motdBox.hide()
        self.controlBtn.hide()


PLAYER = 0
GUILD = 1

class GuildRoster:

    def __init__(self, window):
        self.window = window
        self.currentTab = PLAYER
        self.guildMenu = GuildMenu()
        self.LINE_HEIGHT = 20
        self.memberArea = LineRoundedContainer(window, position=(AnchorType.TOPCENTERFIXED), size=(250,
                                                                                                   150), color=(Color.WHITE))
        self.scrollBox = ScrollableContainer((self.memberArea), position=(0, 0), size=(240,
                                                                                       140))
        self.lineTable = LineTable((self.scrollBox.content), position=(0, 0), maxCols=6, visible=False)
        self.lineTable.setColumns(['usericon', 'user', 'rank', 'mapicon', 'map', 'lastonline'])
        self.lineTable.setInternalMargins(5, 5)
        self.lineTable.setManualFit()
        self.rosterBtn = window.tabControl.addTab("Roster")
        self.rosterBtn.addCallback("onMouseLeftClick", self._showRoster)
        self.hide()
        self.fitToContent()

    def fitToContent(self):
        self.lineTable.fitToContent()
        self.memberArea.fitToContent()
        self.scrollBox.fitToContent()
        self.window.fitToContent()

    def addMember(self, memberData):
        head, earth = self._getIcons(memberData.status)
        widget = self.lineTable.addData(usericon=IconButton((self.lineTable), icon=(textureCache.getGuiImage(head)), size=(0, self.LINE_HEIGHT), style=(styleDB.transparentButtonStyle)), user=Label((self.lineTable), text=(memberData.name), size=(0, self.LINE_HEIGHT)),
          rank=Label((self.lineTable), text=(memberData.rank.name), size=(0, self.LINE_HEIGHT)),
          mapicon=IconButton((self.lineTable), icon=(textureCache.getGuiImage(earth)), size=(0, self.LINE_HEIGHT), style=(styleDB.transparentButtonStyle)),
          map=Label((self.lineTable), text=(mapDB.getMapNameById(memberData.mapId)), size=(0, self.LINE_HEIGHT)),
          lastonline=Label((self.lineTable), text=(self.onlineNumToText(memberData.lastOnline) if not memberData.status else ""), size=(0, self.LINE_HEIGHT)))
        widget.memberData = memberData
        widget.addCallback("onMouseRightClick", self.showGuildMenu)

    def onlineNumToText(self, timestamp):
        return "Today"

    def clearGuild(self):
        self.lineTable.emptyAndDestroy()
        self.fitToContent()

    def _getIcons(self, online):
        if online:
            head = "common/headmale_03"
            earth = "icons/earth"
        else:
            head = "common/headmaledisabled_02"
            earth = "icons/earthdisabled"
        return (head, earth)

    def showGuildMenu(self, widget, x, y, modiifers):
        if widget.memberData:
            self.guildMenu.showMember(widget.memberData, x, y)

    def removePlayer(self, memberData):
        line = self.getLineById(memberData.trainerId)
        self.lineTable.delLine(line)

    def updatePlayer(self, memberData):
        line = self.getLineById(memberData.trainerId)
        mapIcon = self.lineTable.getData(line.row, "mapicon")
        head, earth = self._getIcons(memberData.status)
        earthIcon = textureCache.getGuiImage(earth)
        if not mapIcon.iconMatches(earthIcon):
            userIcon = self.lineTable.getData(line.row, "usericon")
            userIcon.setIconDefault(textureCache.getGuiImage(head))
            mapIcon.setIconDefault(earthIcon)
        nameWidget = self.lineTable.getData(line.row, "user")
        userName = memberData.name
        if nameWidget.text != userName:
            nameWidget.text = memberData.name
        mapWidget = self.lineTable.getData(line.row, "map")
        mapName = mapDB.getMapNameById(memberData.mapId)
        if mapWidget.text != mapName:
            mapWidget.text = mapName
        rankWidget = self.lineTable.getData(line.row, "rank")
        rankName = memberData.rank.name
        if rankWidget.text != rankName:
            rankWidget.text = memberData.rank.name
        onlineName = self.onlineNumToText(memberData.lastOnline) if not memberData.status else ""
        lastOnlineWidget = self.lineTable.getData(line.row, "lastonline")
        if lastOnlineWidget.text != onlineName:
            lastOnlineWidget.text = onlineName

    def updateRank(self, rank):
        for line in self.lineTable.getLines():
            memberData = line.memberData
            if memberData.rank == rank:
                lbl = self.lineTable.getData(line.row, "rank")
                lbl.text = memberData.rank.name

    def deleteRank(self, rankId):
        """ This will also update everyones memberData """
        rank = sessionService.guild.lowestRank()
        for line in self.lineTable.getLines():
            if line.memeberData.rank.id == rankId:
                line.memberData.rank = rank
                rankWidget = self.lineTable.getData(line.row, "rank")
                rankWidget.text = rank.name

    def _showRoster(self, widget, x, y, modifiers):
        self.window.hideTab()
        self.show()
        self.window.header.updatePosition()
        self.fitToContent()

    def show(self):
        self.window.currentTab = self
        self.memberArea.show()
        self.scrollBox.show()
        self.lineTable.show()

    def hide(self):
        self.memberArea.hide()
        self.scrollBox.hide()
        self.lineTable.hide()

    def setMembers(self):
        for member in sessionService.guild.getMembers():
            self.addMember(member)

        self.fitToContent()

    def getLineById(self, memberId, table=PLAYER):
        for line in self.lineTable.getLines():
            if line.memberData.trainerId == memberId:
                return line

        return


class GuildControl(Window):

    def __init__(self):
        Window.__init__(self, desktop, position=(AnchorType.CENTER), size=(220, 280), draggable=True, autosize=(True,
                                                                                                                True), visible=False)
        self.setManualFit()
        self.tabControl = Tabs(self, desktop)
        self.ranks = RankControl(self)
        self.fitToContent()

    def clearGuild(self):
        self.ranks.clearGuild()
        if self.visible:
            self.hide()

    def showControl(self):
        if not self.visible:
            self.show()


class RankControl:

    def __init__(self, window):
        self.window = window
        self.currentRank = None
        self.swapToRank = None
        self.permissionBoxes = {}
        self.permissionBoxes[GuildPermissions.LISTEN] = Checkbox(window, position=(0,
                                                                                   85), text="See guild chat.")
        self.permissionBoxes[GuildPermissions.TALK] = Checkbox(window, position=(0,
                                                                                 105), text="Talk in guild chat.")
        self.permissionBoxes[GuildPermissions.INVITE] = Checkbox(window, position=(0,
                                                                                   125), text="Invite members.")
        self.permissionBoxes[GuildPermissions.PROMOTE] = Checkbox(window, position=(0,
                                                                                    145), text="Promote members.")
        self.permissionBoxes[GuildPermissions.DEMOTE] = Checkbox(window, position=(0,
                                                                                   165), text="Demote members.")
        self.permissionBoxes[GuildPermissions.KICK] = Checkbox(window, position=(0,
                                                                                 185), text="Kick members.")
        self.permissionBoxes[GuildPermissions.SETMOTD] = Checkbox(window, position=(0,
                                                                                    205), text="Set message of the day.")
        self.rankNameTxt = Textbox(window, position=(0, 55), size=(110, 20), text="", maxLetters=(NameLength.GUILD_RANK))
        self.swapLbl = Label(window, position=(120, 0), text="Swap with Rank:")
        self.rankLbl = Label(window, position=(0, 0), text="Select Rank:")
        self.ranksBtn = window.tabControl.addTab("Ranks")
        self.saveBtn = Button(window, position=(AnchorType.CENTERBOTTOM), size=(60,
                                                                                0), autosize=(True,
                                                                                              False), text="Save", style=(styleDB.greenButtonStyle))
        self.saveBtn.addCallback("onMouseLeftClick", self.saveSettings)
        self.deleteBtn = Button(window, position=(AnchorType.CENTERBOTTOM), text="Delete Rank", style=(styleDB.redButtonStyle))
        self.deleteBtn.addCallback("onMouseLeftClick", self.deleteRank)
        self.cancelBtn = Button(window, position=(AnchorType.CENTERBOTTOM), size=(60,
                                                                                  0), autosize=(True,
                                                                                                False), text="Cancel")
        self.cancelBtn.addCallback("onMouseLeftClick", self.closeWindowClick)
        self.dropDown = DropDown((self.window), position=(0, 17), style=(styleDB.dropdownButtonStyle))
        self.swapDropDown = DropDown((self.window), position=(120, 17), style=(styleDB.dropdownButtonStyle))

    def clearGuild(self):
        self.dropDown.emptyAndDestroy()
        self.swapDropDown.emptyAndDestroy()

    def deleteRank(self, widget, x, y, modifiers):
        if self.currentRank:
            packetManager.queueSend(cmsg.GuildDeleteRank, self.currentRank.id)

    def saveSettings(self, widget, x, y, modifiers):
        rankName = self.rankNameTxt.text
        if not rankName or len(rankName) > NameLength.GUILD_RANK:
            return
        elif self.currentRank:
            if self.currentRank.name != rankName:
                packetManager.queueSend(cmsg.GuildRankRename, self.currentRank.id, rankName.encode("utf-8"))
            if self.currentRank.id != 0:
                newPermissions = self.getNewPermissions()
                if self.currentRank.permissions != newPermissions:
                    packetManager.queueSend(cmsg.GuildRankPermissions, self.currentRank.id, newPermissions)
                if self.swapToRank:
                    if self.swapToRank != self.currentRank:
                        packetManager.queueSend(cmsg.GuildSwapRank, self.currentRank.id, self.swapToRank.id)
        else:
            packetManager.queueSend(cmsg.GuildCreateRank, rankName.encode("utf-8"), self.getNewPermissions())

    def getNewPermissions(self):
        permission = 0
        for bitFlag in self.permissionBoxes:
            checkbox = self.permissionBoxes[bitFlag]
            if checkbox.isSelected():
                permission |= bitFlag

        return permission

    def closeWindowClick(self, widget, x, y, modifiers):
        self.window.hide()

    def displayPermissions(self, show=True):
        for chkbox in self.permissionBoxes.values():
            if show:
                chkbox.show()
            else:
                chkbox.hide()

    def set(self):
        self.dropDown.emptyAndDestroy()
        self.swapDropDown.emptyAndDestroy()
        button = Button((self.dropDown), text="New Rank", size=(90, 0), autosize=(False,
                                                                                  True))
        button.addCallback("onMouseLeftClick", self._showNewRank)
        self.dropDown.addOption(button)
        ranks = sessionService.guild.getRanks()
        ranks.sort(key=(lambda r: r.id))
        for rank in ranks:
            button = Button((self.dropDown), text=(rank.name))
            button.rank = rank
            self.dropDown.addOption(button)
            button.addCallback("onMouseLeftClick", self._showSettings)
            if rank.id == 0:
                pass
            else:
                button2 = Button((self.swapDropDown), text=(rank.name))
                button2.rank = rank
                self.swapDropDown.addOption(button2)
                button2.addCallback("onMouseLeftClick", self._addSwap)

        self.dropDown.fitToContent()
        self.swapDropDown.fitToContent()

    def _addSwap(self, widget, x, y, modifiers):
        self.swapToRank = widget.rank

    def _showNewRank(self, widget, x, y, modifiers):
        if self.currentRank:
            if self.currentRank.id == 0:
                self.displayPermissions(True)
        self.currentRank = None
        self.rankNameTxt.text = "Rank Name"
        for permission in self.permissionBoxes:
            checkbox = self.permissionBoxes[permission]
            checkbox.setSelected(False)

    def _showSettings(self, widget, x, y, modifiers):
        if self.currentRank != widget.rank:
            oldRank = self.currentRank
            self.currentRank = widget.rank
            self.rankNameTxt.text = widget.rank.name
            if widget.rank.id == 0:
                self.displayPermissions(False)
            if oldRank:
                if oldRank.id == 0:
                    self.displayPermissions(True)
            self.setCheckboxes(widget.rank)

    def permissionChange(self, rank):
        if self.currentRank == rank:
            self.setCheckboxes(rank)

    def setCheckboxes(self, rank):
        for permission in self.permissionBoxes:
            checkbox = self.permissionBoxes[permission]
            checkbox.setSelected(True if rank.permissions & permission else False)

        self.swapToRank = None
        self.swapDropDown.hide()
        self.swapDropDown.show()
        self.dropDown.hide()
        self.dropDown.show()


class GroupRequestWindow(Window):

    def __init__(self):
        Window.__init__(self, desktop, position=(700, 100), size=(250, 130), draggable=True, visible=False, autosize=(True,
                                                                                                                      True))
        self.infoLbl = Label(self, position=(20, 20), size=(200, 100), text="", autosize=(False,
                                                                                          False), multiline=True)
        self.yesBtn = Button(self, position=(5, 80), size=(100, 26), style=(styleDB.greenButtonStyle), text=(messageDB["ACCEPT"]), autosize=(False,
                                                                                                                                             False))
        self.yesBtn.addCallback("onMouseLeftClick", self.acceptRequest)
        self.noBtn = Button(self, position=(130, 80), size=(100, 26), style=(styleDB.redButtonStyle), text=(messageDB["DENY"]), autosize=(False,
                                                                                                                                          False))
        self.noBtn.addCallback("onMouseLeftClick", self.denyRequest)

    def showRequest(self, trainerName, guildName):
        self.infoLbl.text = f"{trainerName} invited you to join {guildName}."
        self.show()

    def acceptRequest(self, widget, x, y, modifiers):
        packetManager.queueSend(cmsg.GuildResponse, GuildResponses.REQUEST_ACCEPTED)
        self.hideWindow()

    def denyRequest(self, widget, x, y, modifiers):
        packetManager.queueSend(cmsg.GuildResponse, GuildResponses.REQUEST_DENIED)
        self.hideWindow()

    def hideWindow(self):
        self.hide()


class GuildWindow(Window):

    def __init__(self, control):
        Window.__init__(self, desktop, position=(AnchorType.CENTER), size=(200, 200), draggable=True, autosize=(True,
                                                                                                                True), visible=False)
        self.control = control
        self.currentTab = None
        Header(self, "Guild Name", close=True)
        self.tabControl = Tabs(self, desktop)
        self.fitToContent()
        self.leaderControl = GuildControl()
        self.info = GuildInfo(self)
        self.roster = GuildRoster(self)
        self.currentTab = self.info
        self.currentTab.show()

    def reset(self):
        self.clearGuild()
        if self.visible:
            self.hide()

    def hideTab(self):
        self.currentTab.hide()

    def clearGuild(self):
        self.roster.clearGuild()
        self.info.clearGuild()
        self.leaderControl.clearGuild()

    def setGuild(self):
        self.roster.setMembers()
        self.info.setInfo()
        self.leaderControl.ranks.set()
        self.fitToContent()

    def setLeader(self, btn):
        return

    def openMenu(self, widget, x, y, modifiers):
        self.menu.showMenu(self.getGroup(), widget.memberData)


class Guild:

    def __init__(self):
        self.window = GuildWindow(self)
        self.requestWindow = GroupRequestWindow()
        eventManager.registerListener(self)

    def reset(self):
        self.window.reset()

    def onGuildInvite(self, trainerName, guildName):
        self.requestWindow.showRequest(trainerName, guildName)

    def onGuildAddPlayer(self, data):
        member = GuildMember()
        packer = RawUnpacker(data)
        _, member.trainerId, rankId, member.status = packer.get("!BHBB")
        member.name = packer.getString()
        member.mapId = packer.getString()
        member.rank = sessionService.guild.getRank(rankId)
        nameCache.setTrainer(member.trainerId, member.name)
        self.addMember(member)
        self.window.fitToContent()
        eventManager.notify("onSystemMessage", f"{member.name} has joined the guild!")

    def onGuildResponse(self, response):
        if response == GuildResponses.REQUEST_SENT:
            eventManager.notify("onSystemMessage", "Your guild invitation was sent.")
        elif response == GuildResponses.REQUEST_ACCEPTED:
            eventManager.notify("onSystemMessage", "Your guild invitation was accepted.")
        elif response == GuildResponses.REQUEST_DENIED:
            eventManager.notify("onSystemMessage", "Your guild invitation was declined.")
        elif response == GuildResponses.ALREADY_IN_GUILD:
            eventManager.notify("onSystemMessage", "That player is already in a guild.")
        elif response == GuildResponses.NOT_ONLINE:
            eventManager.notify("onSystemMessage", "Player couldn't be found.")
        elif response == GuildResponses.NO_REQUESTS:
            eventManager.notify("onSystemMessage", "Player is currently busy.")
        elif response == GuildResponses.GUILD_FULL:
            eventManager.notify("onSystemMessage", "Guild is currently full.")
        elif response == GuildResponses.GUILD_CANNOTLEAVE:
            eventManager.notify("onSystemMessage", "You can't leave as guild leader, select another user as leader first.")

    def onGuildUpdate(self, trainerId, targetId, action):
        memberData = sessionService.guild.getMember(trainerId)
        targetData = sessionService.guild.getMember(targetId)
        if action == GuildEvent.DISBAND:
            eventManager.notify("onSystemMessage", "The guild has been disbanded!")
        elif action == GuildEvent.REMOVED:
            if targetId == sessionService.getClientId():
                self.leaveGuild()
                eventManager.notify("onSystemMessage", f"You have been kicked from the guild by {memberData.name}!")
            else:
                self.removePlayer(targetData)
                eventManager.notify("onSystemMessage", f"{memberData.name} kicked {targetData.name} from the guild!")
        elif action == GuildEvent.LEFT:
            if trainerId == sessionService.getClientId():
                self.leaveGuild()
                eventManager.notify("onSystemMessage", "You have left the guild!")
            else:
                self.removePlayer(memberData)
                eventManager.notify("onSystemMessage", f"{memberData.name} has left the guild!")
        elif action == GuildEvent.PROMOTED:
            sessionService.guild.promote(targetData)
            self.updatePlayer(targetData)
            eventManager.notify("onSystemMessage", f"{targetData.name} was promoted to {targetData.rank.name}!")
        elif action == GuildEvent.DEMOTED:
            sessionService.guild.demote(targetData)
            self.updatePlayer(targetData)
            eventManager.notify("onSystemMessage", f"{targetData.name} was demoted to {targetData.rank.name}!")
        else:
            if action == GuildEvent.LEADERCHANGE:
                memberData.rank, targetData.rank = targetData.rank, memberData.rank
                self.updatePlayer(memberData)
                self.updatePlayer(targetData)
                eventManager.notify("onSystemMessage", f"{memberData.name} has set {targetData.name} as the new guild leader!")
        self.window.fitToContent()

    def onGuildList(self, data):
        guild = sessionService.guild
        packer = RawUnpacker(data)
        _, guild.leaderId, memberCount, rankCount = packer.get("!BHBB")
        guild.name = packer.getString()
        guild.motd = packer.getString()
        for _ in range(rankCount):
            rank = GuildRank()
            rank.id, rank.permissions = packer.get("!BB")
            rank.name = packer.getString()
            guild.addRank(rank)

        for _ in range(memberCount):
            member = GuildMember()
            member.trainerId, rankId, member.status, member.mapId, member.lastOnline = packer.get("!HBBHI")
            cacheName = nameCache.getTrainer(member.trainerId)
            if cacheName:
                member.name = cacheName
            else:
                nameCache.addIdToGet(member.trainerId, IdRange.PC_TRAINER)
            member.note = packer.getString()
            member.rank = guild.getRank(rankId)
            guild.addMember(member)

        cacheController.requestPCTrainerIds("guild")
        self.window.setGuild()

    def onNameQuery(self, charId, charType, name):
        if charType == IdRange.PC_TRAINER:
            memberData = sessionService.guild.getMember(charId)
            if memberData:
                memberData.name = name
                self.updatePlayer(memberData)
                self.window.fitToContent()

    def addMember(self, memberData):
        sessionService.guild.addMember(memberData)
        self.window.roster.addMember(memberData)

    def removePlayer(self, memberData):
        sessionService.guild.delMember(memberData)
        self.window.roster.removePlayer(memberData)

    def updatePlayer(self, memberData):
        self.window.roster.updatePlayer(memberData)

    def leaveGuild(self):
        sessionService.guild.leave()
        self.window.clearGuild()

    def onGuildMotd(self, data):
        unpacker = RawUnpacker(data)
        _ = unpacker.get("!B")
        message = unpacker.getString()
        eventManager.notify("onSystemMessage", message)
        sessionService.guild.motd = message
        self.window.info.motdBox.text = message

    def onGuildRankAdd(self, rankId, rankName, permissions):
        rank = GuildRank()
        rank.id = rankId
        rank.name = rankName
        rank.permissions = permissions
        sessionService.guild.addRank(rank)
        self.window.leaderControl.ranks.set()

    def onGuildRankRename(self, rankId, rankName):
        rank = sessionService.guild.getRank(rankId)
        rank.name = rankName
        self.window.roster.updateRank(rank)
        self.window.fitToContent()
        self.window.leaderControl.ranks.set()

    def onGuildRankPermissions(self, rankId, permissions):
        rank = sessionService.guild.getRank(rankId)
        rank.permissions = permissions
        self.window.leaderControl.newPermissions(rank)

    def onGuildRankDelete(self, rankId):
        sessionService.guild.delRank(rankId)
        self.window.roster.deleteRank(rankId)
        self.window.fitToContent()
        self.window.leaderControl.ranks.set()

    def onGuildSwapRank(self, sourceRankId, targetRankId):
        sourceRank = sessionService.guild.getRank(sourceRankId)
        targetRank = sessionService.guild.getRank(targetRankId)
        sourceRank.id = targetRankId
        targetRank.id = sourceRankId
        sessionService.guild.ranks.swap(sourceRankId, targetRankId)
        self.window.leaderControl.ranks.set()

    def onPlayerStatusChange(self, trainerId, status, value):
        memberData = sessionService.guild.getMember(trainerId)
        if memberData:
            memberData.setStatus(status, value)
            self.window.roster.updatePlayer(memberData)
            if status == PlayerStatus.OFFLINE or status == PlayerStatus.ONLINE:
                self.window.setHeaderTitle(f"{sessionService.guild.name} | Online: {sessionService.guild.onlineCount()}")
            self.window.fitToContent()


guild = Guild()
