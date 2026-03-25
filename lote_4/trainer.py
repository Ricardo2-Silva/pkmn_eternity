# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\interface\trainer.py
"""
Created on Aug 3, 2011

@author: Ragnarok
"""
from twisted.internet import reactor
from client.control.service.session import sessionService
from client.control.system.anims import ScaleTo, AnimCallable, FadeColor
from client.data.settings import gameSettings
from shared.container.net import cmsg
from client.control.events.event import eventManager
from client.control.gui import Button, Window, Label, Menu, Datatable, IconButton
from client.data.gui import styleDB
from shared.container.constants import IdRange, INTERACT_RANGE, Gender, PlayerAction, Appearance, Badges, BodyTypes
from client.data.utils.anchor import AnchorType
from client.render.cache import textureCache
from client.data.DB import messageDB, appearanceDB
from client.control.net.sending import packetManager
from client.control.utils.localization import localeInt
from shared.service.geometry import getDistanceBetweenTwoPoints
from client.interface.social import friendsList
from client.interface.battle import playerChallenge
import pyglet.window.mouse
from client.game import desktop
from client.scene.manager import sceneManager
from client.control.gui.char import NewStyleTrainerWidget
from client.control.gui.dropdown import DropDown
from client.control.gui.slider import Slider
from client.data.world.char import appearanceColors
from client.control.gui.picture import Picture
from shared.controller.net.packetStruct import RawUnpacker
from shared.container.player import AppearanceItem
from datetime import datetime
import time
UI_SCALE = gameSettings.getUIScale()

class MenuWindow(Menu):

    def __init__(self):
        Menu.__init__(self, desktop)
        self.trainerData = None
        self.cardBtn = Button(self, style=(styleDB.menuItemStyle), size=(90, 20), text="View Card", autosize=(False,
                                                                                                              False))
        self.cardBtn.addCallback("onMouseLeftClick", self.viewTrainerCard)
        self.tradeBtn = Button(self, style=(styleDB.menuItemStyle), size=(90, 20), text="Trade", autosize=(False,
                                                                                                           False))
        self.tradeBtn.addCallback("onMouseLeftClick", self.tradeItems)
        self.duelBtn = Button(self, style=(styleDB.menuItemStyle), size=(90, 20), text="Battle Challenge", autosize=(False,
                                                                                                                     False))
        self.duelBtn.addCallback("onMouseLeftClick", self.duelChallenge)
        self.friendBtn = Button(self, style=(styleDB.menuItemStyle), size=(90, 20), text="Add Friend", autosize=(False,
                                                                                                                 False))
        self.friendBtn.addCallback("onMouseLeftClick", self.addFriend)
        self.groupBtn = Button(self, style=(styleDB.menuItemStyle), size=(90, 20), text="Invite to Group", autosize=(False,
                                                                                                                     False))
        self.groupBtn.addCallback("onMouseLeftClick", self.inviteGroup)
        self.guildBtn = Button(self, style=(styleDB.menuItemStyle), size=(90, 20), text="Invite to Guild", autosize=(False,
                                                                                                                     False))
        self.guildBtn.addCallback("onMouseLeftClick", self.inviteGuild)
        self.cancelBtn = Button(self, style=(styleDB.menuItemStyle), size=(90, 20), text="Cancel", autosize=(False,
                                                                                                             False))
        self.buttons = (
         self.cardBtn, self.tradeBtn, self.guildBtn, self.duelBtn, self.friendBtn, self.groupBtn, self.cancelBtn)

    def reset(self):
        self.trainerData = None
        self.forceHide()

    def viewTrainerCard(self, widget, x, y, modifiers):
        packetManager.queueSend(cmsg.TrainerCard, self.trainerData.id)

    def tradeItems(self, widget, x, y, modifiers):
        if getDistanceBetweenTwoPoints(sessionService.trainer.getPosition2D(), self.trainerData.getPosition()) <= INTERACT_RANGE:
            packetManager.queueSend(cmsg.TradeRequest, self.trainerData.id, 0)
            eventManager.notify("onSystemMessage", "Your trade request was sent.")
        else:
            eventManager.notify("onSystemMessage", "You are too far away to trade.")

    def tradePokemon(self, widget, x, y, modifiers):
        if getDistanceBetweenTwoPoints(sessionService.trainer.getPosition2D(), self.trainerData.getPosition()) <= INTERACT_RANGE:
            packetManager.queueSend(cmsg.TradeRequest, self.trainerData.id, 1)
            eventManager.notify("onSystemMessage", "Your trade request was sent.")
        else:
            eventManager.notify("onSystemMessage", "You are too far away to trade.")

    def duelChallenge(self, widget, x, y, modifiers):
        playerChallenge.showChallenge(self.trainerData)

    def inviteGuild(self, widget, x, y, modifiers):
        packetManager.queueSend(cmsg.GuildInvite, self.trainerData.name.encode())

    def addFriend(self, widget, x, y, modifiers):
        packetManager.queueSend(cmsg.FriendRequest, str(self.trainerData.name).encode())

    def inviteGroup(self, widget, x, y, modifiers):
        packetManager.queueSend(cmsg.GroupInvite, self.trainerData.name.encode())

    def closeWindow(self):
        if self.visible:
            for button in self.buttons:
                if button.visible:
                    button.hide()

            self.hide()

    def showMenu(self, trainerData, x, y):
        self.trainerData = trainerData
        self.populateMenu()
        if not self.visible:
            self.show()
        self.setActive()
        self.setPosition(x, y)

    def populateMenu(self):
        self.hideAllOptions()
        client = sessionService.getClientData()
        self.add(self.cardBtn)
        if self.trainerData.id != client.id:
            self.add(self.tradeBtn)
            if not sessionService.battle.isActive():
                self.add(self.duelBtn)
            if friendsList.data.canFriend(self.trainerData.id):
                self.add(self.friendBtn)
            if sessionService.group.canInviteMember(self.trainerData.id):
                self.add(self.groupBtn)
            if sessionService.guild.canInviteMember(self.trainerData.id):
                self.add(self.guildBtn)
        self.add(self.cancelBtn)
        self.fitToContent()


class TrainerMenu:

    def __init__(self):
        self.window = MenuWindow()
        eventManager.registerListener(self)

    def reset(self):
        self.window.reset()

    def onCharMouseClick(self, x, y, button, char):
        if button == pyglet.window.mouse.RIGHT:
            if char.getIdRange() == IdRange.PC_TRAINER:
                x, y = sceneManager.convert(x, y)
                self.window.showMenu(char.data, int(x / UI_SCALE), int(y / UI_SCALE))
            elif self.window.visible:
                self.window.hide()


class CustomizationPage:

    def __init__(self, window):
        self.window = window
        self.accessoryId = 0
        self.clothesId = 0
        start_y = 175
        start_x = 20
        tabImage = textureCache.getGuiImage("trainercard/extended")
        self.picture = Picture((self.window), picture=tabImage, position=(16, 157))
        self.rotateDirections = (180, 135, 90, 45, 0, 315, 270, 225)
        self.direction = 270
        self.player = NewStyleTrainerWidget((self.window), action=(PlayerAction.STOP), position=(258, start_y + 54))
        self.player.renderer.setScale(2)
        Label((self.window), text="Accessory Options:", position=(start_x, start_y + 3), style=(styleDB.trainerCardLabelStyle))
        self.accessory = DropDown((self.window), position=(start_x + 100, start_y + 3 - 5), style=(styleDB.dropdownButtonStyle))
        Label((self.window), text="Accessory Color:", position=(start_x, start_y + 30), style=(styleDB.trainerCardLabelStyle))
        self.accessoryColorSlider = Slider((self.window), position=(start_x + 90, start_y + 30))
        (self.accessoryColorSlider.setValues)(*appearanceColors)
        self.accessoryColorSlider.addCallback("onValueChange", self.selectAccessoryColor)
        Label((self.window), text="Clothes Options:", position=(start_x, start_y + 55), style=(styleDB.trainerCardLabelStyle))
        self.clothes = DropDown((self.window), position=(start_x + 90, start_y + 50), style=(styleDB.dropdownButtonStyle))
        Label((self.window), text="Clothes Color:", position=(start_x, start_y + 80), style=(styleDB.trainerCardLabelStyle))
        self.clothesColorSlider = Slider((self.window), position=(start_x + 90, start_y + 80))
        (self.clothesColorSlider.setValues)(*appearanceColors)
        self.clothesColorSlider.addCallback("onValueChange", self.selectClothesColor)
        Label((self.window), text="Hair Color:", position=(start_x, start_y + 100), style=(styleDB.trainerCardLabelStyle))
        self.hairColorSlider = Slider((self.window), position=(start_x + 90, start_y + 100))
        (self.hairColorSlider.setValues)(*appearanceColors)
        self.hairColorSlider.addCallback("onValueChange", self.selectHairColor)
        self.requirementsLbl = Label((self.window), text="", position=(start_x, start_y + 150))
        self.leftButton = Button((self.window), position=(220, start_y + 60), style=(styleDB.leftArrowButtonStyle), text="", size=(22,
                                                                                                                                   22), autosize=(False,
                                                                                                                                                  False))
        self.leftButton.addCallback("onMouseLeftClick", self.rotateRight)
        self.rightButton = Button((self.window), position=(270, start_y + 60), style=(styleDB.rightArrowButtonStyle), text="", size=(22,
                                                                                                                                     22), autosize=(False,
                                                                                                                                                    False))
        self.rightButton.addCallback("onMouseLeftClick", self.rotateLeft)
        self.saveButton = Button((self.window), text="Save Changes", position=(start_x + 10, start_y + 120), style=(styleDB.greenButtonStyle))
        self.saveButton.addCallback("onMouseLeftClick", self.saveAppearance)
        self.cancelButton = Button((self.window), text="Cancel Changes", position=(start_x + 120, start_y + 120), style=(styleDB.cancelButtonStyle))
        self.cancelButton.addCallback("onMouseLeftClick", self.resetAppearance)

    def onClientTrainerLoaded(self):
        self.setDefaultAppearance()

    def setDefaultOptions(self):
        appearance = sessionService.getClientTrainer().data.appearance
        self.player.setAccessory(appearance.accessory.id)

    def setDefaultAppearance(self):
        appearance = sessionService.getClientTrainer().data.appearance
        bodyname = BodyTypes(appearance.body).name.lower()
        self.player.setBodyType(bodyname, Gender.toString[appearance.gender], appearance.skintone)
        self.player.setAccessory(appearance.accessory.id)
        self.player.setAccessoryColor(appearanceColors[appearance.accessory.color])
        self.accessoryId = appearance.accessory.id
        self.player.setHairstyle(Gender.toString[appearance.gender], appearance.hair.id)
        self.player.setHairColor(appearanceColors[appearance.hair.color])
        self.player.setClothes(bodyname, Gender.toString[appearance.gender], appearance.clothe.id)
        self.player.setClothesColor(appearanceColors[appearance.clothe.color])
        self.clothesId = appearance.clothe.id
        self.hairColorSlider.value = appearanceColors[appearance.hair.color]
        self.clothesColorSlider.value = appearanceColors[appearance.clothe.color]
        self.accessoryColorSlider.value = appearanceColors[appearance.accessory.color]
        option = self.clothes.getOption(appearanceDB.getClothesName(appearance.clothe.id))
        if option:
            self.clothes.setOption(option)
        option = self.accessory.getOption(appearanceDB.getAccessoryName(appearance.accessory.id))
        if option:
            self.accessory.setOption(option)

    def saveAppearance(self, widget, x, y, modifiers):
        currentAppearance = sessionService.getClientData().appearance
        if currentAppearance.hair.color != appearanceColors.index(self.hairColorSlider.value) or currentAppearance.accessory.color != appearanceColors.index(self.accessoryColorSlider.value) or currentAppearance.clothe.color != appearanceColors.index(self.clothesColorSlider.value) or currentAppearance.accessory.id != self.accessoryId or currentAppearance.clothe.id != self.clothesId:
            packetManager.queueSend(cmsg.AppearanceChange, self.accessoryId, appearanceColors.index(self.accessoryColorSlider.value), self.clothesId, appearanceColors.index(self.clothesColorSlider.value), 0, appearanceColors.index(self.hairColorSlider.value))

    def resetAppearance(self, widget, x, y, modifiers):
        self.setDefaultAppearance()

    def calculateCost(self):
        currentAppearance = sessionService.getClientData().appearance
        dye = 0
        if currentAppearance.hair.color != appearanceColors.index(self.hairColorSlider.value):
            dye += 1
        else:
            if currentAppearance.accessory.color != appearanceColors.index(self.accessoryColorSlider.value):
                dye += 1
            if currentAppearance.clothe.color != appearanceColors.index(self.clothesColorSlider.value):
                dye += 1
            if dye > 0:
                required = f'Requires {dye} reagent{"s" if dye > 1 else ""}.'
            else:
                required = ""
        if self.requirementsLbl.text != required:
            self.requirementsLbl.text = required

    def addInventoryItem(self, appearanceItem):
        if appearanceItem.type == Appearance.ACCESSORY:
            button = Button((self.accessory), text=(appearanceDB.getAccessoryName(appearanceItem.id)), style=(styleDB.dropdownButtonStyle))
            button.addCallback("onMouseLeftClick", self.selectAccessory)
            self.accessory.addOption(button)
        else:
            if appearanceItem.type == Appearance.CLOTHES:
                button = Button((self.clothes), text=(appearanceDB.getClothesName(appearanceItem.id)), style=(styleDB.dropdownButtonStyle))
                button.addCallback("onMouseLeftClick", self.selectClothes)
                self.clothes.addOption(button)
        button.data = appearanceItem.id

    def loadInventory(self, inventoryList):
        acc = Button((self.accessory), text="None", style=(styleDB.dropdownButtonStyle))
        acc.data = 0
        acc.addCallback("onMouseLeftClick", self.selectAccessory)
        self.accessory.addOption(acc)
        cl = Button((self.clothes), text="Default", style=(styleDB.dropdownButtonStyle))
        cl.data = 0
        cl.addCallback("onMouseLeftClick", self.selectClothes)
        self.clothes.addOption(cl)
        for appearanceItem in inventoryList:
            self.addInventoryItem(appearanceItem)

    def selectHairColor(self, value):
        self.player.setHairColor(value)
        self.calculateCost()

    def selectClothesColor(self, value):
        self.player.setClothesColor(value)
        self.calculateCost()

    def selectAccessoryColor(self, value):
        self.player.setAccessoryColor(value)
        self.calculateCost()

    def selectAccessory(self, widget, x, y, modifiers):
        self.player.setAccessory(widget.data)
        self.accessoryId = widget.data

    def selectClothes(self, widget, x, y, modifiers):
        self.player.setClothes(self.player.body, self.player.gender, widget.data)
        self.clothesId = widget.data

    def getNextLeft(self, direction):
        try:
            return self.rotateDirections[self.rotateDirections.index(direction) - 1]
        except Exception:
            return 225

    def getNextRight(self, direction):
        try:
            return self.rotateDirections[self.rotateDirections.index(direction) + 1]
        except Exception:
            return 180

    def rotateLeft(self, widget, x, y, modifiers):
        self.direction = self.getNextLeft(self.direction)
        self.player.setDirection(self.direction)
        self.player.renderer.updateFrame()

    def rotateRight(self, widget, x, y, modifiers):
        self.direction = self.getNextRight(self.direction)
        self.player.setDirection(self.direction)
        self.player.renderer.updateFrame()


class SkillsPage:

    def __init__(self, window):
        self.window = window


class ScaleBadge(ScaleTo):

    def init(self, target, startScale, endScale, duration):
        self.widget = target
        super().init(target.renderer.iconSprite, startScale, endScale, duration)

    def update(self, t):
        if not self.widget.visible:
            self.widget.show()
        super().update(t)


class BadgePage:

    def __init__(self, window):
        self.cardWindow = window
        self.animating = False
        self.toggleButton = Button((self.cardWindow), position=(170, 13), text="Badges", style=(styleDB.greenButtonStyle), visible=False)
        self.toggleButton.addCallback("onMouseLeftClick", self._show)
        self.bgImg = textureCache.getGuiImage("badges/badge_case")
        self.badgeWindow = Window(desktop, position=(AnchorType.CENTER), size=(self.bgImg.width, self.bgImg.height), style=(styleDB.windowsNoStyle), draggable=True, visible=False)
        self.badgeWindow.setBackground(self.bgImg)
        self.closeBtn = Button((self.badgeWindow), position=(275, 286), size=(46, 24), text="", style=(styleDB.reduceButtonStyle), visible=True)
        self.closeBtn.addCallback("onMouseLeftClick", self.closeBadgeWindowEVent)
        self.badgeTable = Datatable((self.badgeWindow), position=(47, 187), maxRows=3, maxCols=6)
        self.badgeTable.setInternalMargins(22, 18)
        self.badgeTable.setManualFit()
        self.all_badge_names = [badge for badge in list(Badges)][1:]
        self.badgeDescriptions = {(Badges.ROCK): "Name: Albite Badge\nElement: Rock"}
        self.icons = {}
        for badge in self.all_badge_names:
            badgeIcon = IconButton((self.badgeTable), icon=(textureCache.getGuiImage(f"badges/badge_{badge.name.lower()}")), style=(styleDB.iconButtonStyle), visible=False)
            badgeIcon.addCallback("onMouseOver", self.showTooltip, badge)
            badgeIcon.addCallback("onMouseLeave", self.hideTooltip)
            self.icons[badge] = badgeIcon
            self.badgeTable.add(badgeIcon)

        self.badgeTable.fitToContent()

    def closeBadgeWindowEVent(self, widget, x, y, modifiers):
        if self.animating:
            return
        self.badgeWindow.close()

    def enableBadges(self):
        self.toggleButton.forceUnHide()

    def showTooltip(self, widget, x, y, badge):
        try:
            info = self.badgeDescriptions[badge]
            eventManager.notify("onShowTooltip", info, x, y)
        except KeyError:
            pass

    def hideTooltip(self, widget):
        eventManager.notify("onCloseTooltip")

    def _show(self, widget, x, y, modifiers):
        self.badgeWindow.toggle()

    def _testBadge(self, widget, x, y, modifiers):
        enums = list(Badges)[1:]
        for i in range(6):
            reactor.callLater(i * 0.3, self.receiveNewBadge, enums[i])

    def receiveNewBadge(self, badge):
        self.animating = True
        self.badgeWindow.draggable = False
        self.badgeWindow.forceUnHide()

        def animateBadgeReceive():
            badgeIcon = self.icons[badge]
            anim = ScaleBadge(badgeIcon, 50, 1, duration=0.5)
            color = (197, 179, 88)
            anim += FadeColor((badgeIcon.renderer.iconSprite), color, duration=0.5, startColor=(255,
                                                                                                255,
                                                                                                255))
            anim += FadeColor((badgeIcon.renderer.iconSprite), (255, 255, 255), duration=0.5, startColor=color)

            def finishAnimation():
                self.badgeTable.fitToContent()
                self.badgeWindow.draggable = True
                self.animating = False

            anim += AnimCallable(finishAnimation)
            badgeIcon.renderer.startAnim(anim)

        reactor.callLater(0.5, animateBadgeReceive)

    def setInitialBadges(self):
        playerBadges = sessionService.getClientData().badges
        for badge, icon in self.icons.items():
            if playerBadges & badge:
                self.icons[badge].show()

        self.badgeTable.fitToContent()


class CardWindow(Window):

    def __init__(self):
        Window.__init__(self, desktop, position=(AnchorType.CENTER), size=(322, 330), style=(styleDB.windowsNoStyle), draggable=True, visible=False)
        self.bgImg = textureCache.getGuiImage("trainercard/trainer_card_0")
        self.setBackground(self.bgImg)
        self.lastFetch = time.time()
        self.customizePage = CustomizationPage(self)
        self.badges = BadgePage(self)
        self.cancelBtn = Button(self, position=(230, 13), size=(64, 26), autosize=(False,
                                                                                   False), style=(styleDB.cancelButtonStyle), text=(messageDB["CANCEL"]))
        self.cancelBtn.addCallback("onMouseLeftClick", self.closeWindowClick)
        self.nameLbl = Label(self, position=(151, 41), size=(100, 16), text="", style=(styleDB.blackLabelStyleRight))
        self.money = Label(self, position=(151, 63), size=(100, 16), text="", style=(styleDB.blackLabelStyleRight))
        self.job = Label(self, position=(195, 129), size=(100, 16), text="", style=(styleDB.blackLabelStyleRight))
        self.team = Label(self, position=(51, 129), size=(100, 16), text="", style=(styleDB.blackLabelStyleRight))
        self.joined = Label(self, position=(195, 106), size=(100, 16), text="", style=(styleDB.blackLabelStyleRight))
        self.seen = Label(self, position=(135, 84), size=(50, 16), text="", style=(styleDB.blackLabelStyleRight))
        self.caught = Label(self, position=(244, 84), size=(50, 16), text="", style=(styleDB.blackLabelStyleRight))

    def reset(self):
        self.forceHide()

    def toggleEvent(self, widget, x, y, modifiers):
        if not self.visible:
            self.open()
            if time.time() - self.lastFetch > 3:
                packetManager.queueSend(cmsg.TrainerCard, sessionService.getClientId())
                self.lastFetch = time.time()
        else:
            self.close()

    def showTrainerCard(self, trainerData):
        self.nameLbl.text = trainerData.name
        if trainerData is sessionService.getClientData():
            self.money.text = localeInt(int(sessionService.bag.money))
            self.customizePage.setDefaultAppearance()
        else:
            self.money.text = "Hidden"
        self.seen.text = str(trainerData.stats.pokedexSeen)
        self.caught.text = str(trainerData.stats.pokedexCaught)
        self.joined.text = datetime.utcfromtimestamp(trainerData.stats.createDate).strftime("%Y-%m-%d %H:%M:%S")

    def closeWindowClick(self, widget, x, y, modifiers):
        self.closeWindow()

    def closeWindow(self):
        self.hide()


class TrainerCard:

    def __init__(self):
        self.window = CardWindow()
        eventManager.registerListener(self)

    def reset(self):
        self.window.reset()

    def showTrainer(self, trainerData):
        if not self.window.visible:
            self.window.show()
        self.window.showTrainerCard(trainerData)
        if trainerData.badges != Badges.NONE:
            if not self.window.badges.toggleButton.visible:
                self.window.badges.enableBadges()

    def clientOpen(self, widget, x, y, modifiers):
        trainerData = sessionService.getClientData()
        self.window.showTrainerCard(trainerData)
        if trainerData.badges != Badges.NONE:
            if not self.window.badges.toggleButton.visible:
                self.window.badges.enableBadges()
        self.window.toggleEvent(widget, x, y, modifiers)

    def onClientTrainerLoaded(self):
        self.window.badges.setInitialBadges()

    def onAppearanceList(self, data):
        appearance = sessionService.getClientTrainer().data.appearance
        packer = RawUnpacker(data)
        _, length = packer.get("!BB")
        for _ in range(length):
            appearanceType, appearanceId, appearanceColor = packer.get("!BBB")
            item = AppearanceItem(appearanceType, appearanceId, appearanceColor)
            appearance.inventory.append(item)

        self.window.customizePage.loadInventory(appearance.inventory)

    def onAppearanceItemUpdate(self, appearanceType, appearanceId, appearanceColor):
        appearance = sessionService.getClientTrainer().data.appearance
        item = AppearanceItem(appearanceType, appearanceId, appearanceColor)
        appearance.inventory.append(item)
        self.window.customizePage.addInventoryItem(item)

    def newBadgeReceived(self, badge):
        self.window.badges.receiveNewBadge(badge)


trainerCard = TrainerCard()
trainerMenu = TrainerMenu()
