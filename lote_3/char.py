# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\gui\char.py
"""
Created on Mar 17, 2016

@author: Admin
"""
from enum import Enum
from client.control.gui.widget import StylizedWidget, Widget
from client.render.cache import textureCache
from shared.container.constants import CreatureAction, RefPointType, PlayerAction
from client.data.gui import styleDB
from client.render.gui import PokemonWidgetRender, TrainerWidgetRender
from client.data.DB import sheetExperiment
from client.render.gui.sheet import NewTrainerWidgetRender

class SheetWidget(StylizedWidget):

    def getSheet(self):
        return self.sheet


class PokemonWidget(SheetWidget):
    renderClass = PokemonWidgetRender

    def __init__(self, parent, fileId=1, shadow=True, position=(0, 0), draggable=False, visible=True, enableEvents=True):
        self.charSheet = textureCache.getPokemon(fileId, 0, 0)
        self.shadow = shadow
        self.frameInfo = sheetExperiment.getPokemon(self.charSheet.dexId)
        StylizedWidget.__init__(self, styleDB.defaultPictureStyle, parent, position, (0,
                                                                                      0), draggable, visible, enableEvents)
        (Widget.setSize)(self, *self.renderer.getSize())

    def setScale(self, scale):
        self.renderer.setScale(scale)

    def setFacing(self, facing):
        self.renderer.setFacing(facing)

    def setAction(self, charAction):
        self.renderer.setAction(CreatureAction.WALK, charAction)

    def setFileId(self, fileId):
        self.charSheet = textureCache.getPokemon(fileId)
        self.frameInfo = sheetExperiment.getPokemon(self.charSheet.dexId)
        self.sheet = self.charSheet.get(CreatureAction.IDLE)
        self.renderer.refresh()
        (Widget.setSize)(self, *self.renderer.getSize())

    def startWalking(self, loopTime=0.15):
        self.renderer.loopAnimation(loopTime)

    def stopWalking(self):
        self.renderer.stopAnimation()


class TrainerWidget(SheetWidget):
    renderClass = TrainerWidgetRender

    def __init__(self, parent, fileId='m01', position=(0, 0), draggable=False, visible=True, enableEvents=True):
        self.charSheet = textureCache.getTrainer(fileId, referencePoint=(RefPointType.BOTTOMCENTER))
        self.sheet = self.charSheet.get(PlayerAction.WALK)
        StylizedWidget.__init__(self, styleDB.defaultPictureStyle, parent, position, (0,
                                                                                      0), draggable, visible, enableEvents)
        (Widget.setSize)(self, *self.renderer.getSize())

    def setFileId(self, fileId):
        self.charSheet = textureCache.getTrainer(fileId)
        self.sheet = self.charSheet.get(PlayerAction.WALK)
        self.renderer.refresh()
        (Widget.setSize)(self, *self.renderer.getSize())

    def stopWalking(self):
        self.renderer.stopAnimation()

    def setWalking(self):
        self.renderer.loopAnimation(0.2)


class NewStyleTrainerWidget(SheetWidget):
    renderClass = NewTrainerWidgetRender

    def __init__(self, parent, action=PlayerAction.WALK, position=(0, 0), draggable=False, visible=True, enableEvents=True, debug=False):
        """ Uses bottom center reference point because of hairstyles and accessorys cannot be referenced from top due to varying sizes"""
        self.action = action
        self.body, self.gender, self.skintone = ('default', 'm', 0)
        self.accessorySheet, self.accessoryMaskSheet = textureCache.getTrainerAccessory(1)
        self.hairSheet = textureCache.getTrainerHair(self.gender, 1)
        self.eyesSheet = textureCache.getTrainerEyes(self.body, 0)
        self.bodySheet, self.frameInfo = textureCache.getTrainerBody(self.body, self.gender)
        self.swimSheet = textureCache.getTrainerSwimSheet()
        self.clothSheet, self.clothMaskSheet = textureCache.getTrainerClothes(self.body, self.gender, 0)
        StylizedWidget.__init__(self, styleDB.defaultPictureStyle, parent, position, (0,
                                                                                      0), draggable, visible, enableEvents)
        (Widget.setSize)(self, *self.renderer.getSize())

    def setAction(self, actionId):
        self.action = actionId
        self.renderer.setAction()

    def setDirection(self, direction):
        self.direction = direction
        self.renderer.setDirection(direction)

    def setBodyType(self, bodyId, gender, skintone):
        self.body = bodyId
        self.skintone = skintone
        self.gender = gender
        self.bodySheet, self.frameInfo = textureCache.getTrainerBody(bodyId, gender)
        self.eyesSheet = textureCache.getTrainerEyes(self.body, 0)
        self.renderer.setBodyType()

    def setClothes(self, body, gender, number):
        self.clothSheet, self.clothMaskSheet = textureCache.getTrainerClothes(body, gender, number)
        self.renderer.setClothes()

    def setClothesColor(self, palleteId):
        self.renderer.setClothesColor(palleteId)

    def setAccessory(self, accessoryId):
        if accessoryId != 0:
            self.accessorySheet, self.accessoryMaskSheet = textureCache.getTrainerAccessory(accessoryId)
        self.renderer.setAccessory(int(accessoryId))
        self.accessoryId = accessoryId

    def setAccessoryColor(self, palleteId):
        self.renderer.setAccessoryColor(palleteId)

    def setHairstyle(self, gender, hairId):
        if hairId == 0 and gender == "m":
            pass
        else:
            self.hairSheet = textureCache.getTrainerHair(gender, hairId)
        self.renderer.setHairstyle(hairId)

    def setHairColor(self, palleteId):
        self.renderer.setHairColor(palleteId)

    def stopWalking(self):
        self.renderer.stopAnimation()

    def setWalking(self):
        self.renderer.loopAnimation(0.2)
