# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\interface\tooltip.py
"""
Created on Jul 26, 2011

@author: Ragnarok
"""
from datetime import datetime
from client.data.world.eggs import EggIncubator
from client.data.world.item import ItemData
from shared.container.skill import SkillInfo, PokemonSkill
from client.data.DB import itemDB, skillDB, pokemonDB
from client.control.service.session import sessionService
from client.control.events.event import eventManager
from client.control.gui import Window, Label
from client.game import desktop
from client.data.gui import styleDB
from client.data.utils.anchor import AnchorType, Alignment
from client.data.settings import gameSettings
from client.control.gui.container import StylizedContainer

class TooltipWindow(Window):

    def __init__(self):
        Window.__init__(self, desktop, size=(10, 10), position=(170, 100), visible=False, autosize=(True,
                                                                                                    True), draggable=False)
        self.setManualFit()
        self.description = Label(self, position=(AnchorType.TOPLEFT), size=(125, 0), text="", autosize=(False,
                                                                                                        True), multiline=True, alignment=(Alignment.CENTER))

    def show(self):
        StylizedContainer.show(self)
        self.desktop.pushToTop(self)


class Tooltip:

    def __init__(self):
        self.window = TooltipWindow()
        self.sWidth, self.sHeight = gameSettings.getWindowResolution()
        eventManager.registerListener(self)

    def parseSkill(self, skillData):
        try:
            tooltip = "{0}\n-----------------\n{1}, {2}\nEnergy Cost: {3}\nCooldown: {4}\nAccuracy: {5}\nBase Damage: {6}\n-----------------\n{7}".format(skillData.name, skillData.elementName, skillData.category, skillData.energy, skillData.cooldown, skillData.accuracy, skillData.baseDamage, skillData.description)
        except Exception as e:
            tooltip = f"Unknown Skill #{skillData.id}"

        return tooltip

    def onShowTooltip(self, data, x, y):
        if isinstance(data, ItemData):
            try:
                tooltip = "{0}\n----------------- \n{1}{2}".format(itemDB.name(data.nameId), itemDB.description(data.nameId), f" \nSell Price: ${data.sell}" if sessionService.shop else "")
            except Exception:
                tooltip = f"Unknown Item #{data.nameId}"

        elif isinstance(data, PokemonSkill):
            tooltip = self.parseSkill(data.skillInfo)
        else:
            if isinstance(data, SkillInfo):
                tooltip = self.parseSkill(data)
            elif isinstance(data, EggIncubator):
                if data.egg:
                    tooltip = f'Egg Incubator\n-----------------\n(Incubating Egg)\nParents: {pokemonDB.name(data.egg.parentOne).title()}, {pokemonDB.name(data.egg.parentTwo).title()}\n\nEgg Laid On: {datetime.utcfromtimestamp(data.egg.laidTime).strftime("%Y-%m-%d %H:%M:%S")}'
                else:
                    tooltip = "Egg Incubator\n-----------------\nCurrently Unoccupied"
                if data.maxUses > 0:
                    count = data.maxUses - data.currentUses
                    amount = None if count < 1 else count
                    tooltip += f"\n\nUses Remaining: {amount}"
            else:
                if isinstance(data, str):
                    tooltip = data
            self.window.description.text = tooltip
            width, height = self.window.getSize()
            if height + y > self.sHeight:
                y -= height
            if width + x > self.sWidth:
                x -= width + 45
            self.window.setPosition(x + 20, y)
            if not self.window.visible:
                self.window.show()
        self.window.fitToContent()

    def onCloseTooltip(self):
        if self.window.visible:
            self.window.hide()


tooltips = Tooltip()
