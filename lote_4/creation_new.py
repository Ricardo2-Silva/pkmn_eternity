# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\interface\creation_new.py
"""
Created on Mar 10, 2018

@author: Admin
"""
import math, pyglet
from client.control.gui import LineRoundedContainer
from client.control.gui.windows import Window
from client.control.system.background import backgroundController
from client.control.system.sound import mixerController
from client.data.system.background import BackgroundData, BackgroundOption
from client.game import desktop
from client.scene.manager import sceneManager
from shared.container.constants import RefPointType, NameLength, Gender, PlayerAction, BodyTypes
from client.render.cache import textureCache
from client.control.gui.picture import AnimatedPicture, Picture
from client.control.gui.char import NewStyleTrainerWidget
from client.control.gui.slider import Slider
from client.control.gui.button import Button
from client.data.gui import styleDB
from client.control.gui.label import Label
from client.control.gui.tables import Datatable
from client.control.gui.textbox import Textbox
from client.data.utils.anchor import AnchorType, Alignment
from client.data.world.char import appearanceColors
from client.control.events.event import eventManager
from client.data.DB import messageDB
import sys
debug = "-creation" in sys.argv
if debug:
    import os, re
    hairStyle = {'m':[],  'f':[]}
    for filename in [f for f in os.listdir("trainer_debug/hair") if os.path.isfile(os.path.join("trainer_debug/hair", f))]:
        foundHair = re.search("hair_(\\d+)_([a-z])", filename)
        if foundHair:
            if foundHair.group(2) == "m":
                key = "m"
            else:
                key = "f"
            hairStyle[key].append(int(foundHair.group(1)))

else:
    hairStyle = {'m':list(range(1, 25)), 
     'f':list(range(1, 18))}

def createCreationBackground():
    image = textureCache.getImageData("lib/bg/creation.png")
    nearest_width = int(math.ceil(sceneManager.window.width / image.width)) * image.width
    nearest_height = int(math.ceil(sceneManager.window.height / image.height)) * image.height
    texture = pyglet.image.Texture.create(nearest_width, nearest_height)
    width = int(round(nearest_width / image.width))
    height = int(round(nearest_height / image.height))
    for x in range(width):
        for y in range(height):
            texture.blit_into(image, image.width * x, image.height * y, 0)

    return texture


velocity = 0.02
SCALE = 1.0

class TooltipSlider(Window):

    def __init__(self):
        Window.__init__(self, desktop, size=(10, 10), position=(170, 100), visible=False, autosize=(True,
                                                                                                    True), draggable=False)
        self.setManualFit()
        self.description = Label(self, position=(AnchorType.TOPLEFT), size=(125, 0), text="", autosize=(False,
                                                                                                        True), alignment=(Alignment.CENTER))

    def show(self):
        self.desktop.pushToTop(self)


class CharacterCreation(object):

    def __init__(self):
        self.window = Window(desktop, size=(420 * SCALE, 200 * SCALE), position=(AnchorType.CENTER))
        self.tooltip = TooltipSlider()
        self.window.setBackground(color=(204, 204, 204))
        backgroundTexture = createCreationBackground()
        bg = textureCache.getImageFile("lib/bg/characterbg.png")
        self.pictureBg = Picture((self.window), position=(260 * SCALE, 10 * SCALE), size=(bg.width * SCALE, bg.height * SCALE), picture=bg)
        self.backgroundSprite = pyglet.sprite.Sprite(backgroundTexture, x=0, y=0, z=41)
        self.newTrainer = NewStyleTrainerWidget((self.window), position=(335 * SCALE, 155 * SCALE))
        self.newTrainer.gender = "m"
        self.newTrainer.body = "default"
        self.newTrainer.skintone = 0
        self.newTrainer.renderer.setScale(2 * SCALE)
        self.dataTable = Datatable((self.window), maxCols=3, position=(10 * SCALE, 51 * SCALE))
        self.dataTable.setInternalMargins(10 * SCALE, 8 * SCALE)
        self.linedContainer = LineRoundedContainer((self.window), (0, 0), (250 * SCALE, 46 * SCALE), color=(180,
                                                                                                            180,
                                                                                                            180))
        self.bodySlider = Slider((self.linedContainer), position=(10 * SCALE, 0 * SCALE), size=(220 * SCALE, 16 * SCALE))
        self.bodySlider.addCallback("onValueChange", self.bodyChange)
        self.bodySlider.setValues("kid", "default", "old")
        self.bodySlider.value = "default"
        lbl = Label((self.linedContainer), text="Kid", position=(10 * SCALE, 20 * SCALE))
        lbl2 = Label((self.linedContainer), text="Adult", position=(107 * SCALE, 20 * SCALE))
        lbl3 = Label((self.linedContainer), text="Elderly", position=(200 * SCALE, 20 * SCALE))
        self.male = Button((self.window), position=(296 * SCALE, 160 * SCALE), text="♂")
        self.male.addCallback("onMouseLeftClick", self.chooseMale)
        self.female = Button((self.window), position=(336 * SCALE, 160 * SCALE), text="♀", style=(styleDB.redButtonStyle))
        self.female.addCallback("onMouseLeftClick", self.chooseFemale)
        self.leftButton = Button((self.window), position=(270 * SCALE, 162 * SCALE), style=(styleDB.leftArrowButtonStyle), text="", size=(22 * SCALE, 22 * SCALE), autosize=(False,
                                                                                                                                                                             False))
        self.leftButton.addCallback("onMouseLeftClick", self.rotateRight)
        self.rightButton = Button((self.window), position=(375 * SCALE, 162 * SCALE), style=(styleDB.rightArrowButtonStyle), text="", size=(22 * SCALE, 22 * SCALE), autosize=(False,
                                                                                                                                                                               False))
        self.rightButton.addCallback("onMouseLeftClick", self.rotateLeft)
        self.skinToneLabel = Label((self.dataTable), text="0")
        self.skinToneSlider = Slider((self.dataTable), size=(120 * SCALE, 16 * SCALE))
        self.skinToneSlider.addCallback("onValueChange", self.skinChange)
        (self.skinToneSlider.setValues)(*list(range(0, 21)))
        self.skinToneSlider.value = 0
        self.dataTable.add(Label((self.dataTable), text="Skin Tone:"))
        self.dataTable.add(self.skinToneSlider)
        self.dataTable.add(self.skinToneLabel)
        self.hairstyleLabel = Label((self.dataTable), text="0")
        self.hairStyleSlider = Slider((self.dataTable), size=(120 * SCALE, 16 * SCALE))
        (self.hairStyleSlider.setValues)(*hairStyle[self.newTrainer.gender])
        self.hairStyleSlider.value = 1
        self.hairStyleSlider.addCallback("onValueChange", self.hairStyleChange)
        self.dataTable.add(Label((self.dataTable), text="Hair Style:"))
        self.dataTable.add(self.hairStyleSlider)
        self.dataTable.add(self.hairstyleLabel)
        self.hairColorLbl = Label((self.dataTable), text="0")
        self.hairStyleColorSlider = Slider((self.dataTable), size=(120 * SCALE, 16 * SCALE))
        (self.hairStyleColorSlider.setValues)(*appearanceColors)
        self.hairStyleColorSlider.addCallback("onValueChange", self.hairStyleColorChange)
        self.dataTable.add(Label((self.dataTable), text="Hair Color:"))
        self.dataTable.add(self.hairStyleColorSlider)
        self.dataTable.add(self.hairColorLbl)
        self.hairStyleColorSlider.value = appearanceColors[1]
        self.clothColorLbl = Label((self.dataTable), text="0")
        self.clothesColorSlider = Slider((self.dataTable), size=(120 * SCALE, 16 * SCALE))
        self.clothesColorSlider.addCallback("onValueChange", self.clothesColorChange)
        (self.clothesColorSlider.setValues)(*appearanceColors)
        self.dataTable.add(Label((self.dataTable), text="Clothes Color:"))
        self.dataTable.add(self.clothesColorSlider)
        self.dataTable.add(self.clothColorLbl)
        self.newTrainer.setWalking()
        self.rotateDirections = (180, 135, 90, 45, 0, 315, 270, 225)
        self.direction = 270
        if debug is True:
            self._addDebug()
            self.window.autosize = (False, True)
        else:
            self._addCreation()
        self.dataTable.fitToContent()
        if debug:
            self.window.fitToContent()

    def skintoneTest(self, value):
        self.redLbl.text = (f"{self.red.value}")
        self.blueLbl.text = (f"{self.blue.value}")
        self.greenLbl.text = (f"{self.green.value}")
        self.newTrainer.renderer.bodySprite.setColor(self.red.value, self.green.value, self.blue.value)

    def on_enter(self):
        mixerController.playMusic("Pokemon Eternity - Title Screen ( SNIPPET ).mp3")

    def on_exit(self):
        mixerController.stopMusic()

    def update(self, dt):
        self.backgroundSprite._vertex_list.tex_coords[1] += dt * velocity
        self.backgroundSprite._vertex_list.tex_coords[4] += dt * velocity
        self.backgroundSprite._vertex_list.tex_coords[7] += dt * velocity
        self.backgroundSprite._vertex_list.tex_coords[10] += dt * velocity
        self.backgroundSprite._vertex_list.tex_coords[0] += dt * velocity
        self.backgroundSprite._vertex_list.tex_coords[3] += dt * velocity
        self.backgroundSprite._vertex_list.tex_coords[6] += dt * velocity
        self.backgroundSprite._vertex_list.tex_coords[9] += dt * velocity

    def draw(self):
        self.backgroundSprite.draw()

    def _addCreation(self):
        self.nameCreationTxt = Textbox((self.window), text="Enter character name", size=(150,
                                                                                         24), position=(10,
                                                                                                        160))
        self.nameCreationTxt.addCallback("onGainFocus", self._gainFocus)
        self.createButton = Button((self.window), text="Start", style=(styleDB.greenButtonStyle), position=(176,
                                                                                                            158))
        self.createButton.addCallback("onMouseLeftClick", self.createTrainer)

    def _gainFocus(self, widget):
        if widget.text == "Enter character name":
            widget.text = ""

    def createTrainer(self, widget, x, y, modifiers):
        from client.control.net.login.handler import loginNetHandler
        name = self.nameCreationTxt.text
        if name.isalpha() is False:
            eventManager.notify("onNotificationMessage", "Notification", messageDB["CHAR_ILLEGAL"])
            return
        if len(name) > NameLength.TRAINER or len(name) < 3:
            eventManager.notify("onNotificationMessage", "Notification", messageDB["CHAR_LENGTH"])
            return
        loginNetHandler.create(name.encode("utf-8"), BodyTypes[self.bodySlider.value.upper()].value, Gender.toInt[self.newTrainer.gender], self.skinToneSlider.value, self.hairStyleSlider.value, appearanceColors.index(self.hairStyleColorSlider.value), appearanceColors.index(self.clothesColorSlider.value))

    def _addDebug(self):
        """ For debugging clothes, etc. Does not have options for character name or submissions. """
        accessory = [
         0]
        for filename in [f for f in os.listdir("trainer_debug/accessory") if os.path.isfile(os.path.join("trainer_debug/accessory", f))]:
            foundAccessory = re.search("accessory_(\\d+)\\.png", filename)
            if foundAccessory:
                accessory.append(int(foundAccessory.group(1)))

        clothes = []
        for filename in [f for f in os.listdir("trainer_debug/cloth") if os.path.isfile(os.path.join("trainer_debug/cloth", f))]:
            foundClothes = re.search("cloth_default_(\\d+)_[a-z]\\.png", filename)
            if foundClothes:
                clothes.append(int(foundClothes.group(1)))

        clothes = list(set(clothes))
        self.accessoryLbl = Label((self.dataTable), text="0")
        self.accessorySlider = Slider((self.dataTable), size=(120 * SCALE, 16 * SCALE))
        self.accessorySlider.addCallback("onValueChange", self.accessoryChange)
        (self.accessorySlider.setValues)(*accessory)
        self.dataTable.add(Label((self.dataTable), text="Accessory:"))
        self.dataTable.add(self.accessorySlider)
        self.dataTable.add(self.accessoryLbl)
        self.accessoryColorLbl = Label((self.dataTable), text="0")
        self.accessoryColorSlider = Slider((self.dataTable), size=(120 * SCALE, 16 * SCALE))
        self.accessoryColorSlider.addCallback("onValueChange", self.accessoryColorChange)
        (self.accessoryColorSlider.setValues)(*appearanceColors)
        self.dataTable.add(Label((self.dataTable), text="Accessory Color:"))
        self.dataTable.add(self.accessoryColorSlider)
        self.dataTable.add(self.accessoryColorLbl)
        self.clothesLbl = Label((self.dataTable), text="0")
        self.clothesSlider = Slider((self.dataTable), size=(120 * SCALE, 16 * SCALE))
        (self.clothesSlider.setValues)(*clothes)
        self.clothesSlider.addCallback("onValueChange", self.clothesChange)
        self.dataTable.add(Label((self.dataTable), text="Clothes Type:"))
        self.dataTable.add(self.clothesSlider)
        self.dataTable.add(self.clothesLbl)
        self.actionLbl = Label((self.dataTable), text="Action Type:")
        self.actionSlider = Slider((self.dataTable), size=(120 * SCALE, 16 * SCALE))
        self.actionNameLbl = Label((self.dataTable), text="WALK")
        (self.actionSlider.setValues)(*[action for action in PlayerAction.ALL])
        self.actionSlider.addCallback("onValueChange", self.actionChange)
        self.actionSlider.value = PlayerAction.WALK
        self.dataTable.add(self.actionLbl)
        self.dataTable.add(self.actionSlider)
        self.dataTable.add(self.actionNameLbl)

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
        self.newTrainer.setDirection(self.direction)

    def rotateRight(self, widget, x, y, modifiers):
        self.direction = self.getNextRight(self.direction)
        self.newTrainer.setDirection(self.direction)

    def chooseMale(self, widget, x, y, modifiers):
        if self.newTrainer.gender != "m":
            self.newTrainer.gender = "m"
            (self.hairStyleSlider.setValues)(*hairStyle[self.newTrainer.gender])
            self.hairStyleSlider.value = 1
            self.setAll()

    def chooseFemale(self, widget, x, y, modifiers):
        if self.newTrainer.gender != "f":
            self.newTrainer.gender = "f"
            (self.hairStyleSlider.setValues)(*hairStyle[self.newTrainer.gender])
            self.hairStyleSlider.value = 1
            self.setAll()

    def setAll(self):
        self.newTrainer.setBodyType(self.newTrainer.body, self.newTrainer.gender, self.newTrainer.skintone)
        self.newTrainer.setClothes(self.newTrainer.body, self.newTrainer.gender, 0)
        self.newTrainer.setHairstyle(self.newTrainer.gender, 1)

    def skinChange(self, value):
        self.skinToneLabel.text = (f"{value}")
        self.newTrainer.setBodyType(self.newTrainer.body, self.newTrainer.gender, value)

    def accessoryChange(self, value):
        self.accessoryLbl.text = (f"{value}")
        self.newTrainer.setAccessory(value)

    def accessoryColorChange(self, value):
        self.accessoryColorLbl.text = (f"{appearanceColors.index(value)}")
        self.newTrainer.setAccessoryColor(value)

    def hairStyleChange(self, value):
        self.hairstyleLabel.text = (f"{value}")
        self.newTrainer.setHairstyle(self.newTrainer.gender, value)

    def hairStyleColorChange(self, value):
        self.hairColorLbl.text = (f"{appearanceColors.index(value)}")
        self.newTrainer.setHairColor(value)

    def clothesChange(self, value):
        self.clothesLbl.text = (f"{value}")
        self.newTrainer.setClothes(self.newTrainer.body, self.newTrainer.gender, value)

    def clothesColorChange(self, value):
        self.clothColorLbl.text = (f"{appearanceColors.index(value)}")
        self.newTrainer.setClothesColor(value)

    def bodyChange(self, value):
        self.newTrainer.setBodyType(value, self.newTrainer.gender, self.newTrainer.skintone)
        self.newTrainer.setClothes(value, self.newTrainer.gender, 0)

    def actionChange(self, value):
        self.newTrainer.setAction(value)
        self.actionNameLbl.text = PlayerAction.toStr[value]
