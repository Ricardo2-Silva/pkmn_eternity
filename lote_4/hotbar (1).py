# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\interface\hotbar.py
"""
Created on Jul 24, 2011

@author: Ragnarok
"""
from client.render.cache import textureCache
from client.control.gui import Window, IconButton, Datatable, Label
import client.data.gui.styleDB as styleDB
from client.data.settings import gameSettings
from client.data.system.hotbar import hotbarConfig
from client.data.utils.anchor import AnchorType
from client.control.events.event import eventManager, eventDispatcher
from pyglet.window.key import symbol_string
from shared.container.constants import IdRange
from client.control.service.session import sessionService
from client.data.container.char import charContainer
from client.game import desktop
import pyglet.clock, time
from client.data.utils.color import Color
from client.data.DB import itemDB
from client.scene.manager import sceneManager
BUTTON_TYPE_NONE = 0
BUTTON_TYPE_ITEM = 1
BUTTON_TYPE_SKILL = 2
BUTTON_TYPE_POKEMON = 3
SELECTED_SLOT = 0
SHARED_SLOT = 6
SELECTED_RESERVED = 6
SHARED_RESERVED = 4

class HotbarButton(IconButton):

    def __init__(self, window, number, slotType, *args, **kwargs):
        (IconButton.__init__)(self, *args, **kwargs)
        self.iconAlwaysBottom = True
        self.window = window
        self.bType = BUTTON_TYPE_NONE
        self.number = number
        self.slotType = slotType
        self.data = None

    def isDraggable(self):
        return bool(self.data)

    def isPokemonButton(self):
        if self.window.control.currentTarget.data.isPokemon():
            return self in self.window.playerButtons
        else:
            return False

    def isSkill(self):
        return self.bType == BUTTON_TYPE_SKILL

    @property
    def key(self):
        return gameSettings.getHotbarKeyByNumber(self.number + self.slotType + 1)

    @property
    def currentTarget(self):
        return self.window.control.currentTarget

    def setTypeStyle(self, styleType):
        if styleType == BUTTON_TYPE_SKILL:
            self.setStyle(styleDB.hotbarSkillButtonStyle)
        else:
            self.setStyle(styleDB.hotbarNormalButtonStyle)

    def assign(self, data):
        self.setTypeStyle(data["type"])
        if data["type"] == BUTTON_TYPE_ITEM:
            itemData = sessionService.bag.getItemIfAny(data["id"])
            if itemData:
                self.assignItem(itemData)
                return True
            hotbarConfig.clearItem(data["id"])
        elif data["type"] == BUTTON_TYPE_SKILL:
            hasSkill = self.currentTarget.data.skills.hasActiveSkill(data["id"])
            if hasSkill:
                skillData = self.currentTarget.data.skills.getActiveSkill(data["id"])
                self.assignSkill(skillData)
                return True
            self.unassignData()
        elif data["type"] == BUTTON_TYPE_POKEMON:
            pkmnData = charContainer.getDataByIdIfAny(data["id"], IdRange.PC_POKEMON)
            if pkmnData:
                self.assignPokemon(pkmnData)
                return True
            self.unassignData()
        else:
            self.unassign()
        return False

    def assignPokemon(self, pkmnData):
        self.data = pkmnData
        self.setIconDefault(textureCache.getPokemonIcon(pkmnData.dexId))
        self.text = ""
        self.bType = BUTTON_TYPE_POKEMON

    def assignNewPokemon(self, pkmnData):
        if not self.isPokemonButton():
            self.assignPokemon(pkmnData)
            self.save()

    def assignSkill(self, skillData):
        self.data = skillData
        self.setIconDefault(textureCache.getPokemonSkillIcon(skillData.skillInfo.graphicId))
        self.text = ""
        self.bType = BUTTON_TYPE_SKILL
        self.setTypeStyle(self.bType)

    def assignNewSkill(self, pkmnId, skillData):
        target = self.currentTarget.data
        if target:
            if self.isPokemonButton():
                if target.idRange == IdRange.PC_POKEMON:
                    if target.id == pkmnId:
                        self.assignSkill(skillData)
                        self.save()

    def assignItem(self, itemData):
        self.data = itemData
        self.text = f"x{itemData.quantity}"
        self.setIconDefault(textureCache.getItemIcon(itemDB.getItemGraphic(itemData.nameId)))
        self.bType = BUTTON_TYPE_ITEM
        self.setTypeStyle(self.bType)
        self.allowDefault("onMouseDragBegin")

    def assignNewItem(self, itemData):
        if not self.isPokemonButton():
            self.assignItem(itemData)
            self.save()

    def swapButton(self, new_button):
        if self.isPokemonButton() == new_button.isPokemonButton():
            if self.bType or new_button.bType:
                self.data, new_button.data = new_button.data, self.data
                self.bType, new_button.bType = new_button.bType, self.bType
                self.text, new_button.text = new_button.text, self.text
                oldIcon = self.getIcon().normal
                newIcon = new_button.getIcon()
                if not newIcon:
                    self.removeIcon()
                else:
                    self.setIconDefault(newIcon.normal)
                new_button.setIconDefault(oldIcon)
                self.text = self.text if self.text else ""
                new_button.text = new_button.text if new_button.text else ""
                self.setTypeStyle(self.bType)
                new_button.setTypeStyle(new_button.bType)
                self.save()
                new_button.save()

    def unassign(self):
        """ Purge data and reset button """
        self.bType = BUTTON_TYPE_NONE
        self.removeIcon()
        if self.text:
            self.text = ""
        self.data = None

    def unassignData(self):
        self.unassign()
        self.save()

    def save(self):
        if self.bType == BUTTON_TYPE_ITEM:
            classId = self.data.nameId
        elif self.bType == BUTTON_TYPE_SKILL:
            try:
                classId = self.data.id
            except Exception:
                classId = self.data.skillInfo.id

        elif self.bType == BUTTON_TYPE_POKEMON:
            classId = self.data.id
        else:
            classId = 0
        if self in self.window.playerButtons:
            if self.window.control.currentTarget.data.isPokemon():
                data = self.window.control.pokemonHotbarData
            else:
                data = self.window.control.trainerHotbarData
        if self in self.window.sharedButtons:
            data = self.window.control.sharedHotbarData
        data[self.number]["id"] = classId
        data[self.number]["type"] = self.bType
        hotbarConfig.save()


class CooldownManager(object):

    def __init__(self):
        self.char = None

    def update(self, dt):
        for widget in self.window.playerButtonTable.getWidgets():
            if widget.bType == BUTTON_TYPE_SKILL:
                if widget.data.skillInfo.cooldown:
                    if widget.data.cooldownTick:
                        cooldownTick = widget.data.cooldownTick
                        cooldownNum = widget.data.skillInfo.cooldown - int(round(time.time() - cooldownTick))
                        if cooldownNum > 0:
                            widget.text = "{0}".format(cooldownNum)
                            (widget.setColor)(*Color.DARK_GREY)
                elif widget.text != "":
                    widget.text = ""
                    if self.selectedButton == widget:
                        widget.setColor(255, 0, 0)
                    else:
                        widget.setColor(255, 255, 255)
                else:
                    if widget.text != "":
                        widget.text = ""
                        if self.selectedButton == widget:
                            widget.setColor(255, 0, 0)
                        else:
                            widget.setColor(255, 255, 255)

    def setChar(self):
        return

    def setCooldowns(self):
        return


class Hotbar(CooldownManager):

    def __init__(self):
        CooldownManager.__init__(self)
        self.canLoadBar = False
        self.currentTarget = None
        self.trainerHotbarData = None
        self.pokemonHotbarData = None
        self.targetModeData = None
        self.selectedButton = None
        self.window = HotbarWindow(self)
        eventManager.registerListener(self)
        eventDispatcher.push_handlers(self)
        sceneManager.window.push_handlers(self)

    def reset(self):
        self.window.reset()

    def onKeyDown(self, symbol, modifiers):
        if not desktop.hasFocus():
            if gameSettings.getHotbarNumber(symbol):
                button = self.window.getButtonByKey(symbol)
                if button:
                    if gameSettings.getQuickCast():
                        eventManager.notify("onQuickCast", button.data)
            else:
                eventManager.notify("onTargetMode", button.data)

    def on_mouse_scrollParse error at or near `COME_FROM' instruction at offset 252_1

    def resetColors(self):
        for widget in self.window.playerButtonTable.getWidgets():
            widget.setColor(255, 255, 255)

    def onPokemonDeleteSkill(self, pokemonData, skillId, isSaved):
        if isSaved == 0:
            if self.currentTarget.data == pokemonData:
                button = self.window.getButtonBySkillId(skillId)
                if button:
                    button.unassignData()
            else:
                pokemonHotbarData = hotbarConfig.getPokemon(pokemonData)
                found = False
                for idx in range(6):
                    if pokemonHotbarData[idx]["id"] == skillId:
                        if pokemonHotbarData[idx]["type"] == 2:
                            found = True
                            pokemonHotbarData[idx]["id"] = 0
                            pokemonHotbarData[idx]["type"] = 0
                            break

                if found:
                    hotbarConfig.save()

    def onPokemonNewSkill(self, pokemonData, skillData):
        if skillData.isSaved:
            return
        if self.currentTarget.data == pokemonData:
            button = self.window.getBlankSkillButton()
            if button:
                button.assignNewSkill(pokemonData.id, skillData)
        else:
            pokemonHotbarData = hotbarConfig.getPokemon(pokemonData)
            found = False
            for idx in range(6):
                if pokemonHotbarData[idx]["id"] == 0:
                    if pokemonHotbarData[idx]["type"] == 0:
                        found = True
                        pokemonHotbarData[idx]["id"] = skillData.skillInfo.id
                        pokemonHotbarData[idx]["type"] = 2
                        break

        if found:
            hotbarConfig.save()

    def onPokemonDelete(self, pokemonId):
        if self.currentTarget.data:
            if self.currentTarget.data.idRange == IdRange.PC_TRAINER:
                button = self.window.getButtonByPokemonId(pokemonId)
                if button:
                    button.unassign()
        hotbarConfig.clearPokemon(pokemonId)

    def onItemDelete(self, itemData, nameId):
        for button in self.window.getButtonByItemId(nameId):
            if itemData.quantity < 1:
                if button:
                    button.unassignData()
                hotbarConfig.clearItem(nameId)
            else:
                if button:
                    button.text = f"x{itemData.quantity}"

    def onItemAdd(self, nameId, quantity):
        for button in self.window.getButtonByItemId(nameId):
            currentQuantity = int(button.text.strip("x"))
            button.text = f"x{currentQuantity + quantity}"

    def onCharSelection(self, char):
        self.currentTarget = char
        self.switchBarToCurrentTarget()

    def switchBarToCurrentTarget(self):
        if self.canLoadBar:
            self.resetColors()
            if self.currentTarget.getIdRange() == IdRange.PC_POKEMON:
                self.pokemonHotbarData = hotbarConfig.getPokemon(self.currentTarget.data)
                self.window.assignPokemon()
            else:
                self.pokemonHotbarData = None
                self.window.assignTrainer()

    def onBagReceived(self):
        self.canLoadBar = True
        self.trainerHotbarData = hotbarConfig.getTrainer(self.currentTarget.data)
        self.sharedHotbarData = hotbarConfig.getShared()
        self.window.assignShared()
        self.window.assignTrainer()
        self.switchBarToCurrentTarget()

    def onTargetMode(self, data, closeAfter=False):
        if not data:
            if self.selectedButton:
                self.selectedButton.setColor(255, 255, 255)
                self.selectedButton = None


class HotbarWindow(Window):

    def __init__(self, control):
        Window.__init__(self, desktop, position=(AnchorType.TOPCENTER), size=(357,
                                                                              34), draggable=True, style=(styleDB.hotbarWindow), visible=False)
        self.control = control
        self.playerButtons = []
        self.sharedButtons = []
        self.playerButtonTable = Datatable(self, position=(0, 0))
        self.playerButtonTable.setInternalMargins(2, 2)
        self.sharedButtonTable = Datatable(self, position=(213, 0))
        self.sharedButtonTable.setInternalMargins(2, 2)
        self.hotkeyNameTable = []
        for i in range(SELECTED_RESERVED):
            b = HotbarButton(self, i, SELECTED_SLOT, (self.playerButtonTable), text="", size=(32,
                                                                                              32), autosize=(False,
                                                                                                             False), draggable=True, style=(styleDB.hotbarNormalButtonStyle))
            b.addCallback("onMouseLeave", self.closeTooltip)
            b.addCallback("onMouseOver", self.showTooltip)
            b.addCallback("onMouseDragBegin", (lambda widget, x, y, modifiers: self.closeTooltip(widget)))
            b.addCallback("onWidgetDroppedOn", self.dragStop)
            b.addCallback("onMouseLeftClick", self.useButton)
            b.id = "Hotbar"
            self.playerButtonTable.add(b, col=i, row=0)
            self.playerButtons.append(b)

        for i in range(SHARED_RESERVED):
            b = HotbarButton(self, i, SHARED_SLOT, (self.sharedButtonTable), text="", size=(32,
                                                                                            32), autosize=(False,
                                                                                                           False), draggable=True, style=(styleDB.hotbarNormalButtonStyle))
            b.addCallback("onMouseLeave", self.closeTooltip)
            b.addCallback("onMouseOver", self.showTooltip)
            b.addCallback("onMouseDragBegin", (lambda widget, x, y, modifiers: self.closeTooltip(widget)))
            b.addCallback("onWidgetDroppedOn", self.dragStop)
            b.addCallback("onMouseLeftClick", self.useButton)
            b.id = "Hotbar"
            self.sharedButtonTable.add(b, col=i, row=0)
            self.sharedButtons.append(b)

        self.playerButtonTable.setAutoFit()
        self.sharedButtonTable.setAutoFit()
        x, y = (0, 0)
        for idx, symbol in enumerate(gameSettings.getHotbarKeys()):
            l = Label(self, text=(self.symbolToText(symbol)), position=(x, y), size=(32,
                                                                                     32), style=(styleDB.hotbarLabelStyle))
            x += 34
            if idx == SELECTED_RESERVED - 1:
                x += 7
            self.hotkeyNameTable.append(l)

        self.setAutoFit()

    def updateKeys(self):
        widgets = self.hotkeyNameTable
        for idx, symbol in enumerate(gameSettings.getHotbarKeys()):
            widgets[idx].text = self.symbolToText(symbol)

    def symbolToText(self, symbol):
        text = symbol_string(symbol).lstrip("_")
        if len(text) > 3:
            text = f"{text[:3]}.."
        return text

    def reset(self):
        for button in self.playerButtonTable.getWidgets() + self.sharedButtonTable.getWidgets():
            button.unassign()
            button.setColor(255, 255, 255)

        if self.visible:
            self.hide()

    def getButtonByNumber(self, number):
        return self.playerButtons[number]

    def getValidButtonByNumber(self, number):
        for widget in self.playerButtons:
            if widget.number == number:
                if widget.bType != BUTTON_TYPE_NONE:
                    return widget

        return

    def getValidButton(self):
        for widget in self.playerButtons:
            if widget.bType != BUTTON_TYPE_NONE:
                return widget

        return

    def getBlankSkillButton(self):
        for i in range(6):
            button = self.getButtonByNumber(i)
            if button.data:
                continue
            return button

        return

    def getButtonByItemId(self, nameId):
        return [widget for widget in self.sharedButtonTable.getWidgets() + self.playerButtonTable.getWidgets() if widget.bType == BUTTON_TYPE_ITEM if widget.data if widget.data.nameId == nameId]

    def getButtonBySkillId(self, skillId):
        for widget in self.playerButtonTable.getWidgets():
            if widget.bType == BUTTON_TYPE_SKILL:
                if widget.data:
                    if widget.data.skillInfo.id == skillId:
                        return widget

        return

    def getButtonByPokemonId(self, pkmnId):
        for widget in self.sharedButtonTable.getWidgets() + self.playerButtonTable.getWidgets():
            if widget.bType == BUTTON_TYPE_POKEMON:
                if widget.data:
                    if widget.data.id == pkmnId:
                        return widget

        return

    def getButtonByKey(self, key):
        for widget in self.playerButtons + self.sharedButtons:
            if widget.key == key:
                if widget.bType != BUTTON_TYPE_NONE:
                    if widget.data:
                        return widget

        return

    def dragStop(self, draggedWidget, widgetDroppedOn, x, y, widget):
        if draggedWidget.data:
            dropName = widgetDroppedOn.__class__.__name__
            if dropName == "Desktop":
                draggedWidget.unassignData()
            elif dropName == "HotbarButton":
                draggedWidget.swapButton(widgetDroppedOn)

    def showTooltip(self, widget, x, y):
        if widget.data:
            if widget.bType != BUTTON_TYPE_POKEMON:
                eventManager.notify("onShowTooltip", widget.data, x, y)

    def closeTooltip(self, widget):
        eventManager.notify("onCloseTooltip")

    def assignPokemon(self):
        for i, button in enumerate(self.playerButtons):
            if self.control.pokemonHotbarData:
                button.assign(self.control.pokemonHotbarData[i])
            else:
                button.unassign()

        anySkills = False
        for button in self.playerButtons:
            if button.bType != BUTTON_TYPE_NONE:
                anySkills = True
                break

        if anySkills is False:
            hotbarConfig.clearPokemon(self.control.currentTarget.data.id)
            self.control.pokemonHotbarData = hotbarConfig.getPokemon(self.control.currentTarget.data)
            self.assignPokemon()

    def assignTrainer(self):
        for i, button in enumerate(self.playerButtons):
            if self.control.trainerHotbarData:
                button.assign(self.control.trainerHotbarData[i])
            else:
                button.unassign()

    def assignShared(self):
        for i, button in enumerate(self.sharedButtons):
            button.assign(self.control.sharedHotbarData[i])

    def useButton(self, widget, x, y, modifiers):
        if not widget.data:
            return
        else:
            if widget.bType == BUTTON_TYPE_NONE or widget.bType == BUTTON_TYPE_POKEMON:
                return
            if widget.bType == BUTTON_TYPE_ITEM or widget.bType == BUTTON_TYPE_SKILL:
                eventManager.notify("onTargetMode", widget.data)


hotbar = Hotbar()