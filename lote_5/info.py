# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\interface\pokemon\info.py
"""
Created on Jan 11, 2012

@author: Ragnarok
"""
from client.control.gui import Bar, Picture, Container, IconButton, Label, Datatable
from client.game import desktop
from shared.container.constants import Gender, PokemonColor, StatType, IdRange
from client.data.utils.anchor import AnchorType
from client.render.cache import textureCache
from client.data.gui import styleDB
from client.control.events.event import eventManager, eventDispatcher
from client.data.utils.color import Color
import time
from client.data.settings import gameSettings
from client.control.service.session import sessionService
import pyglet
from shared.service.ticks import UpdateTicks
import math

class BuffTimeKeeper(UpdateTicks):

    def __init__(self, infoBar):
        UpdateTicks.__init__(self)
        self.informationBar = infoBar

    def reset(self):
        self.clean()

    def update(self, dt):
        self.clean()
        for pokemonData in self.objectsToUpdate:
            if self.informationBar.currentPokemon == pokemonData:
                self.updateBuffs()
                self.updateDebuffs()

    def updateBuffs(self):
        for widget in self.informationBar.buffIconTable.getWidgets():
            duration = int(round(widget.modifierData.getMaxStackDuration() - (time.time() - widget.modifierData.getLatestStartTime())))
            if duration <= 0:
                self.informationBar.buffIconTable.deleteAndDestroy(widget)
                self.informationBar.buffIconTable.reorganize()
                continue
                if isinstance(widget, BuffIcon):
                    stacks = widget.modifierData.getStackCount()
                    if str(stacks) != widget.text:
                        widget.removeModifierCallbacks()
                        widget.setBuffCallbacks()
                        widget.text = str(stacks if stacks > 1 else "")

        for widget in self.informationBar.buffLabelTable.getWidgets():
            duration = int(round(widget.modifierData.getMaxStackDuration() - (time.time() - widget.modifierData.getLatestStartTime())))
            if duration <= 0:
                self.informationBar.buffLabelTable.deleteAndDestroy(widget)
                self.informationBar.buffLabelTable.reorganize()
                continue
                if isinstance(widget, BuffLabel):
                    widget.text = str(duration)

    def updateDebuffs(self):
        for widget in self.informationBar.debuffIconTable.getWidgets():
            duration = int(round(widget.modifierData.getMaxStackDuration() - (time.time() - widget.modifierData.getLatestStartTime())))
            if duration <= 0:
                self.informationBar.debuffIconTable.deleteAndDestroy(widget)
                self.informationBar.debuffIconTable.reorganize()
                continue
                if isinstance(widget, BuffIcon):
                    stacks = widget.modifierData.getStackCount()
                    if str(stacks) != widget.text:
                        widget.removeModifierCallbacks()
                        widget.setDebuffCallbacks()
                        widget.text = str(stacks if stacks > 1 else "")

        for widget in self.informationBar.debuffLabelTable.getWidgets():
            duration = int(round(widget.modifierData.getMaxStackDuration() - (time.time() - widget.modifierData.getLatestStartTime())))
            if duration <= 0:
                self.informationBar.debuffLabelTable.deleteAndDestroy(widget)
                self.informationBar.debuffLabelTable.reorganize()
                continue
                if isinstance(widget, BuffLabel):
                    widget.text = str(duration)


class InformationBar:

    def __init__(self):
        self.window = InfoWindow()
        self.currentPokemon = None
        eventManager.registerListener(self)
        eventDispatcher.push_handlers(self)

    def reset(self):
        pyglet.clock.unschedule(self._scheduleEnergy)
        self.window.reset()
        self.currentPokemon = None

    def _scheduleEnergy(self, dt, pokemonData):
        if pokemonData.stats.calculateEnergyTick():
            self.window.updateEnergy(pokemonData)

    def onPokemonExp(self, pokemonData, exp):
        if pokemonData == self.currentPokemon:
            self.window.updateEXP(pokemonData)

    def onPokemonEvolve(self, pokemonData, dexId):
        if pokemonData in sessionService.getClientPokemonsData():
            self.window.updatePokemon(pokemonData)
            self.window.fitToContent()

    def onPokemonLevelUp(self, pokemonData):
        if pokemonData == self.currentPokemon:
            self.window.updateEXP(pokemonData)
            self.window.updateHP(pokemonData)
            self.window.updateLevel(pokemonData)
            self.window.fitToContent()

    def onBuffUpdate(self, charData, statModifier):
        if charData == self.currentPokemon:
            self.window.updateBuffs(charData, statModifier)

    def onDebuffUpdate(self, charData, statModifier):
        if charData == self.currentPokemon:
            self.window.updateDebuffs(charData, statModifier)

    def onPokemonStatUpdate(self, pokemonData):
        if pokemonData == self.currentPokemon:
            self.window.updateHP(pokemonData)
            self.window.updateEnergy(pokemonData)
            self.window.fitToContent()

    def onPokemonHpUpdate(self, pokemonData):
        if pokemonData == self.currentPokemon:
            self.window.updateHP(pokemonData)

    def onCharSelection(self, char):
        if char.getIdRange() == IdRange.PC_POKEMON:
            if not self.window.visible:
                self.window.show()
            if self.currentPokemon != char.data:
                if self.currentPokemon is not None:
                    pyglet.clock.unschedule(self._scheduleEnergy)
                    self.window.buffTimeKeeper.delete(self.currentPokemon)
                    self.window.buffIconTable.emptyAndDestroy()
                    self.window.buffLabelTable.emptyAndDestroy()
                    self.window.debuffIconTable.emptyAndDestroy()
                    self.window.debuffLabelTable.emptyAndDestroy()
                    self.window.rebuildBuffsAndDebuffs(char.data)
                self.currentPokemon = char.data
                pyglet.clock.schedule_interval(self._scheduleEnergy, 0.1, self.currentPokemon)
                self.window.buffTimeKeeper.add(self.currentPokemon)
                self.window.currentPokemon = self.currentPokemon
            self.window.updatePokemon(char.data)
            self.window.buffTimeKeeper.updateBuffs()
            self.window.buffTimeKeeper.updateDebuffs()
        elif self.window.visible:
            self.window.hide()


class BuffIcon(IconButton):

    def __init__(self, parent, icon=None, text="", style=styleDB.blueButtonStyle, position=(0, 0), size=(0, 0), draggable=False, visible=True, autosize=(True, True), enableEvents=True):
        IconButton.__init__(self, parent, icon, AnchorType.CENTER, text, style, position, size, draggable, visible, autosize, enableEvents)
        self.modifierData = None
        self.addCallback("onMouseLeave", self.hideTooltip)

    def setBuffCallbacks(self):
        self.addCallback("onMouseOver", self.showTooltip, f'{StatType.toString[self.modifierData.statType].title()} {"increased" if self.modifierData.value > 1 else "decreased"} by {self.modifierData.getStackCount() * self.modifierData.value}%')

    def setDebuffCallbacks(self):
        self.addCallback("onMouseOver", self.showTooltip, f'{StatType.toString[self.modifierData.statType].title()} {"increased" if self.modifierData.value > 1 else "decreased"} by {self.modifierData.getStackCount() * self.modifierData.value}%')

    def removeModifierCallbacks(self):
        self.deleteCallback("onMouseOver")

    def showTooltip(self, widget, x, y, itemData):
        eventManager.notify("onShowTooltip", itemData, x, y)

    def hideTooltip(self, widget):
        eventManager.notify("onCloseTooltip")


class BuffLabel(Label):

    def __init__(self, parent, text="Label", style=styleDB.blackLabelStyle, position=(0, 0), size=(0, 0), draggable=False, visible=True, autosize=(True, True), enableEvents=False):
        Label.__init__(self, parent, text, style, position, size, draggable, visible, autosize, enableEvents)
        self.modifierData = None


class InfoWindow(Container):

    def __init__(self):
        wWidth, wHeight = gameSettings.getScaledUIWindowResolution()
        Container.__init__(self, desktop, position=(20, wHeight - 180), size=(255,
                                                                              240), draggable=True, visible=False, autosize=(False,
                                                                                                                             False))
        self.currentPokemon = None
        self.barImg = textureCache.getGuiImage("party/infobar")
        self.backPic = Picture(self, position=(0, -17), picture=(textureCache.getPokemonBack(3, PokemonColor.NORMAL, Gender.MALE)))
        c = Container(self, position=(AnchorType.TOPLEFT))
        self.barPic = Picture(c, position=(AnchorType.TOPLEFT), picture=(self.barImg))
        self.barPic.setMargins(0, 0, 0, 0)
        self.nameLbl = Label(c, position=(120, 2), text="Pokemon", style=(styleDB.whiteLabelStyle))
        self.lvlLbl = Label(c, position=(233, 2), size=(20, 17), autosize=(False, False), text="100", style=(styleDB.whiteLabelStyle))
        self.hpBar = Bar(c, position=(28, 20), size=(225, 19), style=(styleDB.hpBarStyle))
        self.energyBar = Bar(c, position=(123, 39), size=(130, 13), style=(styleDB.energyBarStyle))
        self.xpBar = Bar(c, position=(28, 39), size=(65, 13), style=(styleDB.xpInfoBarStyle))
        self.buffIconTable = Datatable(self, maxRows=1, maxCols=12, position=(0, 60))
        self.buffIconTable.setInternalMargins(6, 6)
        self.buffLabelTable = Datatable(self, maxRows=1, maxCols=12, position=(0, 85))
        self.buffLabelTable.setInternalMargins(6, 6)
        self.debuffIconTable = Datatable(self, maxRows=1, maxCols=12, position=(0,
                                                                                110))
        self.debuffIconTable.setInternalMargins(6, 6)
        self.debuffLabelTable = Datatable(self, maxRows=1, maxCols=12, position=(0,
                                                                                 135))
        self.debuffLabelTable.setInternalMargins(6, 6)
        self.buffTimeKeeper = BuffTimeKeeper(self)
        c.fitToContent()
        self.fitToContent()

    def reset(self):
        self.buffTimeKeeper.reset()
        self.buffIconTable.emptyAndDestroy()
        self.buffLabelTable.emptyAndDestroy()
        self.debuffIconTable.emptyAndDestroy()
        self.debuffLabelTable.emptyAndDestroy()
        self.currentPokemon = None
        if self.visible:
            self.hide()

    def updateBuffs(self, charData, statModifier):
        for widget in self.buffIconTable.getWidgets():
            if widget.modifierData == statModifier:
                return

        self.buff(statModifier)

    def updateDebuffs(self, charData, statModifier):
        for widget in self.debuffIconTable.getWidgets():
            if widget.modifierData == statModifier:
                return

        self.debuff(statModifier)

    def getBuffCount(self):
        return self.buffs

    def getDebuffs(self):
        return

    def rebuildBuffsAndDebuffs(self, pokemonData):
        for statBuffs in pokemonData.stats.getBuffs():
            for buffStatModifier in statBuffs:
                self.buff(buffStatModifier)

        for statDebuffs in pokemonData.stats.getDebuffs():
            for debuffStatModifier in statDebuffs:
                self.debuff(debuffStatModifier)

    def buff(self, statModifier):
        if statModifier.fromType == 0:
            texture = textureCache.getPokemonSkillIcon(statModifier.fromId)
        else:
            if statModifier.fromType == 1:
                texture = textureCache.getItemIcon(statModifier.fromId)
        buffIcon = BuffIcon((self.buffIconTable), icon=texture, text=(str(statModifier.getStackCount()) if statModifier.getStackCount() > 1 else ""), style=(styleDB.buffIconStyle))
        buffIcon.tintColor((204, 255, 204))
        buffIcon.modifierData = statModifier
        buffIcon.setBuffCallbacks()
        print("======================== BUFF", statModifier.getMaxStackDuration())
        label = BuffLabel((self.buffLabelTable), size=(buffIcon.width, 0), text=(str(statModifier.getMaxStackDuration())), style=(styleDB.buffLabelStyle))
        label.modifierData = statModifier
        self.buffIconTable.add(buffIcon)
        self.buffLabelTable.add(label)
        self.buffIconTable.fitToContent()
        self.buffLabelTable.fitToContent()

    def debuff(self, statModifier):
        if statModifier.fromType == 0:
            texture = textureCache.getPokemonSkillIcon(statModifier.fromId)
        else:
            if statModifier.fromType == 1:
                texture = textureCache.getItemIcon(statModifier.fromId)
        buffIcon = BuffIcon((self.debuffIconTable), icon=texture, text=(str(statModifier.getStackCount()) if statModifier.getStackCount() > 1 else ""), style=(styleDB.buffIconStyle))
        buffIcon.tintColor(Color.RED)
        buffIcon.modifierData = statModifier
        buffIcon.setDebuffCallbacks()
        label = BuffLabel((self.debuffLabelTable), size=(buffIcon.width, 0), text=(str(statModifier.getMaxStackDuration())), style=(styleDB.buffLabelStyle))
        label.modifierData = statModifier
        self.debuffIconTable.add(buffIcon)
        self.debuffLabelTable.add(label)
        self.debuffIconTable.fitToContent()
        self.debuffLabelTable.fitToContent()

    def ignoreContainerArea(self):
        return False

    def onMouseDrop(self, widget, x, y, modifiers):
        return

    def updatePokemon(self, pokemon):
        self.updatePicture(pokemon)
        self.updateHP(pokemon)
        self.updateEXP(pokemon)
        self.updateEnergy(pokemon)
        self.lvlLbl.text = str(pokemon.level)
        self.nameLbl.text = pokemon.name

    def updateLevel(self, pokemon):
        self.lvlLbl.text = str(pokemon.level)

    def updatePicture(self, pokemon):
        picture = textureCache.getPokemonBack(pokemon.dexId, pokemon.shiny, pokemon.gender)
        self.backPic.setPicture(picture)
        self.backPic.setPosition(0, -picture.height + 18)

    def updateEnergy(self, pokemon):
        min, max = pokemon.stats.energy.values
        if max < 1:
            min, max = (0, 1)
        self.energyBar.setPercent(min, max)

    def updateHP(self, pokemon):
        min, max = pokemon.stats.hp.values
        if max < 1:
            min, max = (0, 1)
        self.hpBar.setPercent(min, max)

    def updateEXP(self, pkmnData):
        minExp, maxExp = pkmnData.stats.exp.values
        if minExp < maxExp:
            self.xpBar.setPercent(minExp - pkmnData.expThisLevel, maxExp - pkmnData.expThisLevel)


infoBar = InformationBar()
