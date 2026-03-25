# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\interface\pokemon\details.py
"""
Created on Aug 21, 2011

@author: Ragnarok
"""
from client.control.gui import Label, IconButton, Datatable, Picture, Window, Button, Bar, ScrollableContainer
from client.data.gui import styleDB
from client.render.cache import textureCache
from client.data.utils.anchor import AnchorType
from shared.container.constants import StatType, Gender, MAX_SKILL_SIZE, Pokeball
from client.data.DB import abilityDB, pokemonDB, itemDB, natureDB, mapDB, skillDB
from client.control.events.event import eventManager
from client.control.service.session import sessionService
from datetime import date
from client.control.utils.localization import localeInt
from shared.container.net import cmsg
from client.control.net.sending import packetManager
from client.game import desktop
from client.interface.notification import confirmWindow
from client.data.gui.button import ButtonState

class Panel:

    def __init__(self, parent, panelNum):
        self.parent = parent
        self.bg = textureCache.getGuiImage(f"summary/panel_{panelNum}")
        self.bg.anchor_x = 0
        self.bg.anchor_y = 0
        self.on = textureCache.getGuiImage(f"summary/panel_{panelNum}_button_active")
        self.off = textureCache.getGuiImage(f"summary/panel_{panelNum}_button_inactive")
        self.off.anchor_y = self.off.oY
        self.button = IconButton(parent, position=(80 + panelNum * 30, 173), icon=(self.off), style=(styleDB.simpleButtonStyle))
        self.button.addCallback("onMouseLeftClick", self.showClick)
        self.button.setIconOver(self.on)
        self.button.setIconDown(self.on)

    def showClick(self, widget, x, y, modifiers):
        self.show()

    def show(self):
        self.parent.currentPanel.hide()
        self.parent.panelPic.setPicture(self.bg)
        self.button.setIconNormal(self.on)
        self.parent.currentPanel = self

    def hide(self):
        self.button.setIconNormal(self.off)


class PanelInfo(Panel):

    def __init__(self, parent):
        Panel.__init__(self, parent, 1)
        self.dexLbl = Label(parent, text="000", position=(197, 49), size=(113, 15), autosize=(False,
                                                                                              False), style=(styleDB.summaryLabelStyle))
        self.nameLbl = Label(parent, text="Unknown", position=(197, 65), size=(113,
                                                                               15), autosize=(False,
                                                                                              False), style=(styleDB.summaryLabelStyle))
        self.element1 = Picture(parent, position=(237, 81))
        self.element2 = Picture(parent, position=(218, 81))
        self.element3 = Picture(parent, position=(254, 81))
        self.originTrn = Label(parent, text="GM", position=(197, 97), size=(113, 15), autosize=(False,
                                                                                                False), style=(styleDB.blueDetailsStyle))
        self.id = Label(parent, text="1234", position=(197, 113), size=(113, 15), autosize=(False,
                                                                                            False), style=(styleDB.summaryLabelStyle))
        self.expCurrent = Label(parent, text="1", position=(197, 130), size=(113, 15), autosize=(False,
                                                                                                 False), style=(styleDB.summaryLabelStyle))
        self.expTotal = Label(parent, text="1", position=(197, 145), size=(113, 15), autosize=(False,
                                                                                               False), style=(styleDB.summaryLabelStyle))
        self.expBar = Bar(parent, position=(194, 163), size=(111, 5), style=(styleDB.xpBarStyle))

    def show(self):
        Panel.show(self)
        self.dexLbl.show()
        self.nameLbl.show()
        self.element1.show()
        self.element2.show()
        self.element3.show()
        self.originTrn.show()
        self.id.show()
        self.expCurrent.show()
        self.expTotal.show()
        self.expBar.show()

    def hide(self):
        Panel.hide(self)
        self.dexLbl.hide()
        self.nameLbl.hide()
        self.element1.hide()
        self.element2.hide()
        self.element3.hide()
        self.originTrn.hide()
        self.id.hide()
        self.expCurrent.hide()
        self.expTotal.hide()
        self.expBar.hide()

    def updateExp(self, pkmnData):
        self.expCurrent.text = str(localeInt(pkmnData.stats.exp.permanent - pkmnData.stats.exp.current if pkmnData.level < 100 else 0))
        self.expTotal.text = str(localeInt(pkmnData.stats.exp.permanent))
        minExp, maxExp = pkmnData.stats.exp.values
        if minExp < maxExp:
            self.expBar.setPercent(minExp - pkmnData.expThisLevel, maxExp - pkmnData.expThisLevel)

    def updateInfo(self, pkmnData):
        self.dexLbl.text = str(pkmnData.dexId).zfill(3)
        self.nameLbl.text = pokemonDB.getById(pkmnData.dexId).name.upper()
        element = pokemonDB.type(pkmnData.dexId)
        if element[1] is None:
            self.element1.setPicture(textureCache.getElementIcon(element[0]))
            self.element2.removePicture()
            self.element3.removePicture()
        else:
            self.element1.removePicture()
            self.element2.setPicture(textureCache.getElementIcon(element[0]))
            self.element3.setPicture(textureCache.getElementIcon(element[1]))
        self.originTrn.text = pkmnData.ot
        self.id.text = str(pkmnData.id)
        self.updateExp(pkmnData)


class PendingArea(ScrollableContainer):

    def __init__(self, parent, pokemonId):
        ScrollableContainer.__init__(self, parent, position=(235, 70), size=(72, 94), autosize=(False,
                                                                                                False), visible=False)
        self.id = pokemonId
        self.table = Datatable((self.content), maxCols=1, position=(AnchorType.TOPCENTER))
        self.table.setInternalMargins(3, 3)

    def hasSkillId(self, skillId):
        for button in self.table.getWidgets():
            if button.skillData.skillInfo.id == skillId:
                return True

        return False

    def delete(self, skillId):
        for button in self.table.getWidgets():
            if button.skillData.skillInfo.id == skillId:
                self.table.deleteAndDestroy(button)
                self.table.reorganize()
                break

    def fitToContent(self):
        self.table.fitToContent()
        ScrollableContainer.fitToContent(self)


class PanelMoves(Panel):

    def __init__(self, parent):
        Panel.__init__(self, parent, 4)
        self.parent = parent
        self.pendingArea = None
        self.skillTable = Datatable(parent, maxRows=3, maxCols=2, position=(129, 68))
        self.skillTable.setInternalMargins(12, 3)
        for x in range(6):
            button = IconButton((self.skillTable), size=(31, 29), draggable=False, autosize=(False,
                                                                                             False), style=(styleDB.graySkillButtonStyle))
            button.skillData = None
            button.skillSlot = x
            button.addCallback("onMouseLeave", self.closeTooltip)
            button.addCallback("onMouseOver", self.showTooltip)
            button.addCallback("onMouseDragBegin", self.closeTooltipDrag)
            button.addCallback("onWidgetDroppedOn", self.dragEndSkill)
            button.id = "SkillButton"
            self.skillTable.add(button)

        self.pendingData = {}
        self.skillTable.hide()
        self.skillTable.fitToContent()

    def dragEndSkill(self, widget, droppedOnWidget, x, y, modifiers):
        if widget.skillData:
            droppedName = droppedOnWidget.__class__.__name__
            if droppedName == "HotbarButton":
                droppedOnWidget.assignNewSkill(self.parent.control.currentId, widget.skillData)

    def getPendingData(self, pokemonInfo):
        pokemonId = pokemonInfo.id
        if pokemonId not in self.pendingData:
            self.pendingData[pokemonId] = PendingArea(self.parent, pokemonId)
            for skill in pokemonInfo.skills.getPendingSkills():
                self.addPending(pokemonInfo, skill)

            self.pendingData[pokemonId].fitToContent()
        return self.pendingData[pokemonId]

    def addPending(self, pokemonInfo, skillData, fitToContent=False):
        pendingArea = self.getPendingData(pokemonInfo)
        if pendingArea.hasSkillId(skillData.skillInfo.id):
            return
        button = IconButton((pendingArea.table), size=(31, 29), draggable=True, icon=(textureCache.getPokemonSkillIcon(skillData.skillInfo.graphicId)), autosize=(False,
                                                                                                                                                                  False), style=(styleDB.graySkillButtonStyle))
        button.skillData = skillData
        button.addCallback("onMouseLeave", self.closeTooltip)
        button.addCallback("onMouseOver", self.showTooltip)
        button.addCallback("onMouseRightClick", self.swapSkill, button.skillData.skillInfo.id, 0)
        button.addCallback("onMouseDragBegin", self.dragStartPending)
        button.addCallback("onWidgetDroppedOn", self.dragEndPending)
        pendingArea.table.add(button)
        if fitToContent:
            pendingArea.fitToContent()

    def deletePending(self, pokemonInfo, skillId):
        pendingArea = self.getPendingData(pokemonInfo)
        pendingArea.delete(skillId)
        pendingArea.fitToContentChange()

    def showTooltip(self, widget, x, y):
        if widget.skillData:
            eventManager.notify("onShowTooltip", widget.skillData, x, y)

    def closeTooltipDrag(self, widget, x, y, modifiers):
        self.closeTooltip(widget)

    def closeTooltip(self, widget):
        if widget.skillData:
            eventManager.notify("onCloseTooltip")

    def dragStartPending(self, widget, x, y, modifiers):
        widget.setParent(desktop)
        widget.setPosition(x, y)
        self.closeTooltip(widget)

    def dragEndPending(self, button, droppedOnWidget, x, y, modifiers):
        button.setParent(self.pendingArea.table)
        self.pendingArea.fitToContent()
        if sessionService.isInBattle():
            eventManager.notify("onSystemMessage", "You can't do this while in battle.")
            return
        else:
            if button.skillData:
                if droppedOnWidget and droppedOnWidget.id == "SkillButton":
                    if droppedOnWidget.skillData:
                        activeId = droppedOnWidget.skillData.skillInfo.id
                        confirmWindow.verify("You are about to unlearn {0} and learn {1} instead. Unlearning will remove the skill from the Pokemon entirely.\nThis action cannot be undone.\n\nDo you want to continue?".format(droppedOnWidget.skillData.skillInfo.name, button.skillData.skillInfo.name), self.swapSkill, button.skillData.skillInfo.id, activeId)
                else:
                    activeId = 0
                    self.swapSkill(button.skillData.skillInfo.id, activeId)

    def swapSkill(self, inactiveId, activeId):
        pokemon = sessionService.getClientPokemonByID(self.pendingArea.id)
        if activeId == 0:
            if len(pokemon.skills.getActiveSkills()) >= MAX_SKILL_SIZE:
                return
        if pokemon.skills.hasActiveSkill(inactiveId):
            return
        packetManager.queueSend(cmsg.SwapSkill, self.pendingArea.id, inactiveId, activeId)

    def addSkill(self, pokemonInfo):
        self.updateSkills(pokemonInfo)

    def deleteSkill(self, skillId):
        for button in self.skillTable.getWidgets():
            if button.skillData.skillInfo.id == skillId:
                button.removeIcon()
                button.skillData = None
                button.draggable = False
                break

    def show(self):
        Panel.show(self)
        if self.pendingArea:
            self.pendingArea.show()
        self.skillTable.show()

    def hide(self):
        Panel.hide(self)
        if self.pendingArea:
            self.pendingArea.hide()
        self.skillTable.hide()

    def updateInfo(self, pokemonInfo):
        self.updateSkillPending(pokemonInfo)
        self.updateSkills(pokemonInfo)

    def updateSkillPending(self, pokemonInfo):
        pendingArea = self.getPendingData(pokemonInfo)
        if self.pendingArea:
            if self.pendingArea == pendingArea:
                return
            if self.pendingArea.visible:
                self.pendingArea.hide()
        self.pendingArea = pendingArea
        if self.skillTable.visible:
            if self.parent.visible:
                self.pendingArea.show()

    def updateSkills(self, pokemonInfo):
        skills = list(pokemonInfo.skills.getActiveSkills())
        length = len(skills)
        if pokemonInfo.trainerId == sessionService.getClientId():
            draggable = True
        else:
            draggable = False
        for button in self.skillTable.getWidgets():
            if button.skillSlot < length:
                skill = skills[button.skillSlot]
                button.setIconDefault(textureCache.getPokemonSkillIcon(skill.skillInfo.graphicId))
                button.skillData = skill
            else:
                button.removeIcon()
                button.skillData = None
            button.draggable = draggable


class PanelStats(Panel):

    def __init__(self, parent):
        Panel.__init__(self, parent, 3)
        self.hp = Label(parent, position=(212, 43), size=(65, 15), text="HP", autosize=(False,
                                                                                        False), visible=False, style=(styleDB.summaryLabelStyle))
        self.hpBar = Bar(parent, position=(213, 60), size=(50, 5), visible=False)
        self.atk = Label(parent, position=(212, 67), size=(65, 15), text="atk", autosize=(False,
                                                                                          False), visible=False, style=(styleDB.summaryLabelStyle))
        self.defense = Label(parent, position=(212, 83), size=(65, 15), text="def", autosize=(False,
                                                                                              False), visible=False, style=(styleDB.summaryLabelStyle))
        self.spatk = Label(parent, position=(212, 99), size=(65, 15), text="spatk", autosize=(False,
                                                                                              False), visible=False, style=(styleDB.summaryLabelStyle))
        self.spdef = Label(parent, position=(212, 115), size=(65, 15), text="spdef", autosize=(False,
                                                                                               False), visible=False, style=(styleDB.summaryLabelStyle))
        self.speed = Label(parent, position=(212, 131), size=(65, 15), text="stspeed", autosize=(False,
                                                                                                 False), visible=False, style=(styleDB.summaryLabelStyle))
        self.abilityLbl = Label(parent, position=(182, 150), text="Ability", size=(108,
                                                                                   17), autosize=(False,
                                                                                                  False), visible=False, style=(styleDB.summaryLabelStyle), enableEvents=True)
        self.abilityLbl.abilityId = 0
        self.abilityLbl.addCallback("onMouseOver", self.showTooltip)
        self.abilityLbl.addCallback("onMouseLeave", self.hideTooltip)

    def showTooltip(self, widget, x, y):
        if widget.abilityId:
            eventManager.notify("onShowTooltip", abilityDB.description(widget.abilityId), x, y)

    def hideTooltip(self, widget):
        if self.abilityLbl.abilityId:
            eventManager.notify("onCloseTooltip")

    def show(self):
        Panel.show(self)
        self.hp.show()
        self.atk.show()
        self.defense.show()
        self.spatk.show()
        self.spdef.show()
        self.speed.show()
        self.abilityLbl.show()
        self.hpBar.show()

    def hide(self):
        Panel.hide(self)
        self.hp.hide()
        self.atk.hide()
        self.defense.hide()
        self.spatk.hide()
        self.spdef.hide()
        self.speed.hide()
        self.abilityLbl.hide()
        self.hpBar.hide()

    def updateHP(self, pkmnData):
        self.hp.text = ("{0}/{1}".format)(*pkmnData.stats.hp.values)
        (self.hpBar.setPercent)(*pkmnData.stats.hp.values)

    def updateInfo(self, pkmnData):
        self.updateHP(pkmnData)
        self.atk.text = str(pkmnData.stats.atk.permanent)
        self.defense.text = str(pkmnData.stats.defense.permanent)
        self.spatk.text = str(pkmnData.stats.spatk.permanent)
        self.spdef.text = str(pkmnData.stats.spdef.permanent)
        self.speed.text = str(pkmnData.stats.speed.permanent)
        self.abilityLbl.text = abilityDB.name(pkmnData.abilityId)
        self.abilityLbl.abilityId = pkmnData.abilityId


class PanelMedals(Panel):

    def __init__(self, parent):
        Panel.__init__(self, parent, 5)


class PanelMemo(Panel):

    def __init__(self, parent):
        Panel.__init__(self, parent, 2)
        self.natureStart = Label(parent, position=(143, 49), text="start", style=(styleDB.redDetailsStyle), autosize=(True,
                                                                                                                      True), visible=False)
        self.natureEnd = Label(parent, position=(143, 49), text="nature.", style=(styleDB.summaryLabelStyle), visible=False)
        self.createDateLbl = Label(parent, text="create", position=(143, 67), style=(styleDB.summaryLabelStyle), visible=False)
        self.foundMapLbl = Label(parent, text="found", position=(143, 82), style=(styleDB.redDetailsStyle), visible=False)
        self.foundLevelLbl = Label(parent, text="level", position=(143, 99), style=(styleDB.summaryLabelStyle), visible=False)

    def show(self):
        Panel.show(self)
        self.natureStart.show()
        self.natureEnd.show()
        self.createDateLbl.show()
        self.foundMapLbl.show()
        self.foundLevelLbl.show()

    def hide(self):
        Panel.hide(self)
        self.natureStart.hide()
        self.natureEnd.hide()
        self.createDateLbl.hide()
        self.foundMapLbl.hide()
        self.foundLevelLbl.hide()

    def updateInfo(self, pkmnData):
        self.natureStart.text = natureDB.name(pkmnData.nature)
        x, y = self.natureStart.getRelativePosition()
        x += self.natureStart.width
        self.natureEnd.setPosition(x, y)
        self.createDateLbl.text = date.fromtimestamp(pkmnData.createdTime).strftime("%B %d, %Y")
        self.foundMapLbl.text = mapDB.getMapNameById(pkmnData.createdMapId)
        self.foundLevelLbl.text = f"Met at Level {pkmnData.createdLevel}."


class SummaryWindow(Window):

    def __init__(self, control):
        Window.__init__(self, desktop, position=(AnchorType.CENTER), size=(320, 205), draggable=True, style=(styleDB.windowNoBgStyle), visible=False)
        self.setManualFit()
        self.control = control
        self.bgImg = textureCache.getGuiImage("summary/main")
        self.setBackground(self.bgImg)
        self.panelPic = Picture(self, picture=(textureCache.getGuiImage("summary/panel_1")), position=(0,
                                                                                                       6), style=(styleDB.pictureNoPaddingStyle))
        self.dataTable = Datatable(self, position=(63, 0), size=(32, 32))
        self.dataTable.setInternalMargins(5, 0)
        for x in range(1, 7):
            button = IconButton((self.dataTable), size=(38, 32), autosize=(False, False), iconAnchor=(AnchorType.TOPCENTER), style=(styleDB.graySkillButtonStyle))
            button.addCallback("onMouseLeftClick", self.showClick)
            button.pkmnData = None
            button.lineupId = x
            self.dataTable.add(button, row=0)

        self.levelLbl = Label(self, position=(18, 51), text="0", style=(styleDB.summaryLabelStyle))
        self.genderLbl = Label(self, position=(89, 51), text="0", autosize=(True, True), style=(styleDB.summaryLabelStyle))
        self.nameLbl = Label(self, position=(19, 36), text="0", style=(styleDB.whiteLabelStyle))
        self.itemNameLbl = Label(self, position=(8, 190), text="0", style=(styleDB.summaryLabelStyle))
        self.pokeballPic = Picture(self, position=(1, 32))
        self.dexPic = Picture(self, position=(18, 86), style=(styleDB.pictureNoPaddingStyle))
        self.cancelBtn = Button(self, position=(261, 178), size=(55, 26), autosize=(False,
                                                                                    False), style=(styleDB.cancelButtonStyle), text="Close")
        self.cancelBtn.addCallback("onMouseLeftClick", self.closeWindow)
        self.infoPanel = PanelInfo(self)
        self.statsPanel = PanelStats(self)
        self.medalsPanel = PanelMedals(self)
        self.movesPanel = PanelMoves(self)
        self.memoPanel = PanelMemo(self)
        self.currentPanel = self.infoPanel
        self.currentPanel.show()
        self.dataTable.fitToContent()

    def reset(self):
        for widget in self.dataTable.getWidgets():
            widget.pkmnData = None
            widget.removeIcon()

        newWidget = self.getButtonById(self.currentId)
        if newWidget:
            newWidget.setState((ButtonState.NORMAL), custom=False)
        if self.visible:
            self.hide()

    def hide(self):
        Window.hide(self)
        newWidget = self.getButtonById(self.currentId)
        if newWidget:
            newWidget.setState((ButtonState.NORMAL), custom=False)
        self.control.currentId = 0

    def closeWindow(self, widget, x, y, modifiers):
        self.hide()

    def show(self):
        Window.show(self)

    def showClick(self, widget, x, y, modifiers):
        if widget.pkmnData:
            if self.currentId != widget.pkmnData.id:
                oldWidget = self.getButtonById(self.currentId)
                if oldWidget:
                    oldWidget.setState((ButtonState.NORMAL), custom=False)
                self.control.currentId = widget.pkmnData.id
                self.showPokemon(widget.pkmnData)
                widget.setState((ButtonState.OVER), custom=True)
            else:
                widget.setState((ButtonState.OVER), custom=True)

    def showPokemon(self, pkmnData, updateTabs=True):
        if pkmnData.gender == Gender.MALE:
            self.genderLbl.text = "♂"
            self.genderLbl.setStyle(styleDB.blueDetailsStyle)
        elif pkmnData.gender == Gender.FEMALE:
            self.genderLbl.text = "♀"
            self.genderLbl.setStyle(styleDB.redDetailsStyle)
        else:
            self.genderLbl.text = ""
        self.dexPic.setPicture(textureCache.getPokemonFront((pkmnData.dexId), version=(pkmnData.frontVer), shiny=(pkmnData.shiny), gender=(pkmnData.gender)))
        self.levelLbl.text = str(pkmnData.level)
        self.nameLbl.text = pkmnData.name
        self.pokeballPic.setPicture(textureCache.getItemIcon(Pokeball.toItemId.get(pkmnData.ballId, 1)))
        if updateTabs:
            self.infoPanel.updateInfo(pkmnData)
            self.memoPanel.updateInfo(pkmnData)
            self.statsPanel.updateInfo(pkmnData)
            self.movesPanel.updateInfo(pkmnData)
        self.itemNameLbl.text = itemDB.name(pkmnData.heldNameId)

    def getButtonByLineupId(self, lineupId):
        for widget in self.dataTable.widgets:
            if widget.lineupId == lineupId:
                return widget

        return

    def getButtonById(self, pkmnId):
        for widget in self.dataTable.widgets:
            if widget.pkmnData:
                if widget.pkmnData.id == pkmnId:
                    return widget

        return

    def gotPokemon(self, pkmnData):
        button = self.getButtonByLineupId(pkmnData.lineupId)
        if button:
            button.pkmnData = pkmnData
            button.setIconDefault(textureCache.getPokemonIcon(pkmnData.dexId))

    def lineupSwitch(self, lineupId1, lineupId2):
        original = self.getButtonByLineupId(lineupId1)
        new = self.getButtonByLineupId(lineupId2)
        if self.currentId:
            if original.pkmnData:
                if original.pkmnData.id == self.currentId:
                    original.setState((ButtonState.NORMAL), custom=False)
                    new.setState((ButtonState.OVER), custom=True)
                original.pkmnData, new.pkmnData = new.pkmnData, original.pkmnData
                if original.pkmnData:
                    original.setIconDefault(textureCache.getPokemonIcon(original.pkmnData.dexId))
            else:
                original.removeIcon()
            if new.pkmnData:
                new.setIconDefault(textureCache.getPokemonIcon(new.pkmnData.dexId))
        else:
            new.removeIcon()

    def _updateSelectState(self):
        newWidget = self.window.getButtonById(self.currentId)
        if newWidget:
            newWidget.setState((ButtonState.OVER), custom=True)

    def removePokemon(self, pokemonId):
        button = self.getButtonById(pokemonId)
        if button:
            button.pkmnData = None
            button.removeIcon()

    @property
    def currentId(self):
        return self.control.currentId


class PokemonSummary:

    def __init__(self):
        self.currentId = 0
        self.window = SummaryWindow(self)
        eventManager.registerListener(self)

    def reset(self):
        self.window.reset()
        self.currentId = 0

    def onHotkeyPress(self, hotkeyName):
        if hotkeyName == "pokemon_summary":
            selected = sessionService.getSelectedChar()
            if selected.data.isPokemon():
                if self.currentId == selected.data.id:
                    if self.window.visible:
                        self.window.close()
            else:
                self.onPokemonShow(selected.data)

    def onPokemonReceived(self, pokemonData):
        self.window.gotPokemon(pokemonData)

    def onLineupSwitch(self, lineupId1, lineupId2):
        self.window.lineupSwitch(lineupId1, lineupId2)

    def onPokemonShow(self, pokemonData):
        if pokemonData:
            if not self.window.visible:
                self.window.show()
            if pokemonData.id != self.currentId:
                oldWidget = self.window.getButtonById(self.currentId)
                if oldWidget:
                    oldWidget.setState((ButtonState.NORMAL), custom=False)
                self.currentId = pokemonData.id
                self.window.showPokemon(pokemonData)
                newWidget = self.window.getButtonById(self.currentId)
                if newWidget:
                    newWidget.setState((ButtonState.OVER), custom=True)

    def onPokemonDelete(self, pokemonId):
        self.window.removePokemon(pokemonId)

    def onPokemonLevelUp(self, pkmnData):
        if self.currentId == pkmnData.id:
            self.window.showPokemon(pkmnData, updateTabs=False)

    def onPokemonExp(self, pokemonData, exp):
        if self.currentId == pokemonData.id:
            self.window.infoPanel.updateExp(pokemonData)

    def onItemEquip(self, pokemon, nameId):
        if self.currentId == pokemon.id:
            self.window.showPokemon(pokemon, False)

    def onItemUnequip(self, pokemon):
        if self.currentId == pokemon.id:
            self.window.showPokemon(pokemon, False)

    def onPokemonEvolve(self, pokemonData, dexId):
        if pokemonData in sessionService.getClientPokemonsData():
            button = self.window.getButtonById(pokemonData.id)
            if button:
                button.setIconDefault(textureCache.getPokemonIcon(dexId))
                if self.currentId == pokemonData.id:
                    self.window.showPokemon(pokemonData)

    def onPokemonDeleteSkill(self, pokemonData, skillId, isSaved):
        if isSaved:
            self.window.movesPanel.deletePending(pokemonData, skillId)
        else:
            if self.currentId == pokemonData.id:
                self.window.movesPanel.deleteSkill(skillId)
            skillInfo = skillDB.getByIdIfAny(skillId)
        if skillInfo:
            eventManager.notify("onSystemMessage", f"{pokemonData.name} forgot {skillInfo.name}!")

    def onPokemonNewSkill(self, pkmnData, skillData):
        if skillData.isSaved:
            self.window.movesPanel.addPending(pkmnData, skillData, fitToContent=True)
            eventManager.notify("onSystemMessage", f"{pkmnData.name} tried to learn {skillData.skillInfo.name}, but it didn't have room!")
        else:
            if self.currentId == pkmnData.id:
                self.window.movesPanel.addSkill(pkmnData)
            eventManager.notify("onSystemMessage", f"{pkmnData.name} learned {skillData.skillInfo.name}!")

    def onPokemonStatUpdate(self, pokemonData):
        if self.currentId == pokemonData.id:
            self.window.statsPanel.updateInfo(pokemonData)

    def onPokemonHpUpdate(self, pokemonData):
        if self.currentId == pokemonData.id:
            self.window.statsPanel.updateHP(pokemonData)


pokemonSummary = PokemonSummary()
