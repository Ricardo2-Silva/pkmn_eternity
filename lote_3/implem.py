# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\gui\implem.py
"""
Created on 8 dec. 2011

@author: Kami
"""
from client.control.camera import worldCamera
from client.control.gui import Datatable, Picture, AnimatedPicture
from client.control.service.session import sessionService
from client.data.gui import styleDB
from client.data.settings import gameSettings
from client.data.sprite import Sheet
from client.data.utils.color import Color
from client.data.world.char import CharColor
from client.render.cache import textureCache
from shared.container.constants import IdRange, DamageNotificationTags, RefPointType
from twisted.internet import reactor
import client.render.gui as iCoreRender, time
from client.control.gui.container import Container
from client.control.gui.label import Label
from client.control.gui.bar import Bar
from client.data.utils.anchor import AnchorType, Alignment
import random, pyglet
from client.render.gui.label import LabelRender
from client.render.sprite import PygletSprite, GUIPygletSprite
from client.game import desktop
from client.scene.manager import sceneManager
from pyglet.gl.gl import GL_FALSE, GL_TRUE, glDepthMask
from shared.service.geometry import getDistanceBetweenTwoPoints

class WorldGUIContainer(Container):
    __doc__ = " This container holds all of the GUI objects that are used\n     in the game world. This is done to make sure.\n       1) It is rendered properly. GUI uses int clamp while world uses round.\n       2) GUI is not affected by world zoom, but we need these to be. So they\n         need to be rendered separately.\n    "

    def __init__(self, parent, position=(0, 0), size=(0, 0), draggable=False, visible=True, autosize=(True, True)):
        Container.__init__(self, parent, position=position, size=size, draggable=draggable, visible=visible, autosize=autosize)
        self._batch = pyglet.graphics.Batch()
        self._group = None
        self._transparent = pyglet.graphics.Batch()

    @property
    def batch(self):
        return self._batch

    @property
    def group(self):
        return self._group

    def draw(self):
        self._batch.draw()
        glDepthMask(GL_FALSE)
        self._transparent.draw()
        glDepthMask(GL_TRUE)


worldGUIContainer = WorldGUIContainer(desktop, size=(gameSettings.getWindowResolution()))

class GlobalNamePlate(Label):

    def __init__(self):
        self.char = None
        self.pcOffset = 0
        self.offset = (0, 0)
        Label.__init__(self, worldGUIContainer, text="Unknown", style=(styleDB.nameStyle), size=(0,
                                                                                                 11), autosize=(True,
                                                                                                                False), enableEvents=True, visible=False)
        self.startVisible = False

    def fadeOut(self, duration):
        return

    def fadeTo(self, duration, alpha):
        return

    def fadeIn(self, duration):
        return

    def setNamePlateColor(self):
        if self.char.getIdRange() == IdRange.NPC_WILD_PKMN:
            if self.char.data.tagged == True:
                self.setTextColor(Color.NAME_RED)
            else:
                self.setTextColor(Color.GREY)
        else:
            self.setTextColor(CharColor.fromType.get(self.char.getIdRange(), CharColor.fromType.get(IdRange.NPC_OBJECT)))

    def setCharacter(self, char):
        if char == self.char:
            return
        else:
            if gameSettings.getAlwaysNames():
                if char._namePlate is not None:
                    return
            if self.char:
                self.char.delLinkedObject(self)
        self.char = char
        self.setNamePlateColor()
        self._changeText()
        self.char.addLinkedObject(self)

    def _changeText(self):
        if self.char.getIdRange() in (IdRange.NPC_WILD_PKMN, IdRange.NPC_BATTLE_PKMN):
            name = f"Lv. {self.char.data.level} {self.char.name}"
        else:
            name = self.char.name
        self.text = name
        if self.char.getIdRange() in (IdRange.NPC_CHARACTER,):
            self.pcOffset = 0
        else:
            self.pcOffset = 4
        if not self.renderer.visible:
            self.renderer.setAlpha(255)
        self.offset = (-self.width // 2, self.char.getHeight() + self.height + self.pcOffset)
        self.updateFromObject()
        self.resetRenderState()

    def setColor(self, r, g, b):
        return

    def updatePosition(self):
        return

    def updateFromObject(self):
        x, y = (sceneManager.convert)(*[x + y for x, y in zip(self.char.getPosition2D(), self.offset)])
        self.setPosition(x, y)

    def updateFromObjectNoRender(self):
        x, y = (sceneManager.convert)(*[x + y for x, y in zip(self.char.getPosition2D(), self.offset)])
        self.setPositionNoRender(x, y)

    def updateFromObjectRender(self, interp):
        self.setRenderPosition(interp)

    @property
    def batch(self):
        return self.parent.batch


class NamePlate(Label):

    def __init__(self, char):
        if char.getIdRange() == IdRange.NPC_WILD_PKMN:
            name = f"Lv. {char.data.level} {char.name}"
        else:
            name = char.name
        Label.__init__(self, worldGUIContainer, text=name, style=(styleDB.nameStyle), size=(0,
                                                                                            11), autosize=(True,
                                                                                                           False), enableEvents=True, visible=True)
        self.setTextColor(CharColor.fromType[char.getIdRange()])
        self.char = char
        self.char.addLinkedObject(self)
        self.startVisible = False
        self.offset = (-self.width // 2, self.char.getHeight() + self.height)
        self.updateFromObject()
        self.resetRenderState()

    def setColor(self, r, g, b):
        return

    def updatePosition(self):
        return

    def forceHide(self):
        if gameSettings.getAlwaysNames():
            return
        if self.visible:
            self.hide()

    def forceUnHide(self):
        if not self.visible:
            self.unHide()

    def updateFromObject(self):
        x, y = (sceneManager.convert)(*[x + y for x, y in zip(self.char.getPosition2D(), self.offset)])
        self.setPosition(round(x), round(y))

    def updateFromObjectNoRender(self):
        x, y = (sceneManager.convert)(*[x + y for x, y in zip(self.char.getPosition2D(), self.offset)])
        self.setPositionNoRender(round(x), round(y))

    def updateFromObjectRender(self, interp):
        self.setRenderPosition(interp)

    @property
    def batch(self):
        return self.parent.batch


flagToText = {(DamageNotificationTags.MISS): "Miss", 
 (DamageNotificationTags.CRITICAL): "Critical Hit!", 
 (DamageNotificationTags.IMMUNE): "Immune", 
 (DamageNotificationTags.RESIST): "Resistant", 
 (DamageNotificationTags.EFFECTIVE): "Super Effective!"}
from client.data.utils.color import Color
flagToColor = {(DamageNotificationTags.MISS): (Color.WHITE), 
 (DamageNotificationTags.CRITICAL): (Color.RED), 
 (DamageNotificationTags.IMMUNE): (Color.GREY), 
 (DamageNotificationTags.RESIST): (Color.LIGHT_BLUE), 
 (DamageNotificationTags.EFFECTIVE): (Color.LIGHT_GREEN)}

class DamageNotificationText(Label):
    __doc__ = " Displays visually in text what damage notification there is, even though Damage Notification Tags have multiple packed in, this label will only display one at a time. "

    def __init__(self, char, damageFlag):
        x, y = char.getPosition2D()
        Label.__init__(self, worldGUIContainer, text="", position=(worldCamera.toScreenPosition(x, y)), style=(styleDB.nameStyle), size=(0,
                                                                                                                                         50), autosize=(True,
                                                                                                                                                        False), visible=True)
        self.startVisible = True


class HpBar(Bar):
    VISIBLE_TIME = 1

    def __init__(self, char, size=(20, 5), style=styleDB.defaultBarStyle):
        Bar.__init__(self, worldGUIContainer, per=0, size=size, style=style, visible=True)
        self.startVisible = False
        self.hideWhenFull = True
        self.char = char
        self.timer = 0
        self.offset = (-self.width // 2, -2)
        self.char.addLinkedObject(self)
        self.updateFromObject()
        self.resetRenderState()

    @property
    def transparentBatch(self):
        return self.parent.batch

    def updateHp(self, per):
        self.setPercent2(per)
        if per == 0:
            self.forceHide()
            return
        else:
            self.forceUnHide()
            if self.timer:
                self.timer = time.time() + self.VISIBLE_TIME
            else:
                self.timer = time.time() + self.VISIBLE_TIME
        reactor.callLater(self.VISIBLE_TIME + 0.1, self.deleteTimerAndHide, None)

    def updatePosition(self):
        return

    def updateFromObject(self):
        x, y = (sceneManager.convert)(*[x + y for x, y in zip(self.char.getPosition2D(), self.offset)])
        self.setPosition(int(x), int(y))

    def updateFromObjectNoRender(self):
        x, y = (sceneManager.convert)(*[x + y for x, y in zip(self.char.getPosition2D(), self.offset)])
        self.setPositionNoRender(int(x), int(y))

    def updateFromObjectRender(self, interp):
        self.setRenderPosition(interp)


class CastBar(HpBar):

    def __init__(self, char):
        HpBar.__init__(self, char, size=(30, 5), style=(styleDB.castBarStyle))
        self.hideWhenFull = True
        self.offset = (
         -self.width // 2, -8)
        self.updateFromObject()
        self.resetRenderState()

    def updatePosition(self):
        return

    def cancelCast(self):
        self.timer = 0
        self.forceHide()

    def startCast(self, seconds):
        self.reverseFill = False
        self.fillBarInSeconds(seconds)

    def startChannel(self, seconds):
        self.reverseFill = True
        self.setPercent2(100)
        self.fillBarInSeconds(seconds)


class ChatMessage(Label):

    def __init__(self, char):
        Label.__init__(self, worldGUIContainer,
          position=(200, 200),
          text="Default",
          style=(styleDB.chatMessageWindowStyle),
          size=(150, 0),
          autosize=(True, True),
          multiline=True,
          visible=True)
        self.startVisible = False
        self.renderer.backgroundSprite.batch = worldGUIContainer._transparent
        self.renderer.backgroundSprite.setAlpha(100)
        if char.name in ('Spira', 'Chuck', 'Pills'):
            self.setTextColor(Color.YELLOW)
        self.char = char
        self.offset = (-self.width // 2, self.char.getHeight() + self.height)
        self.char.addLinkedObject(self)
        self.updateFromObject()
        self.resetRenderState()

    def fadeIn(self, duration):
        return

    def setAlpha(self, alpha):
        return

    @Label.text.getter
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        if not self.visible:
            self.show()
        self.lastUpdated = time.time()
        super(ChatMessage, ChatMessage).text.__set__(self, text)
        self.offset = (
         -self.width // 2, self.char.getHeight() + self.height)
        if self.renderer.textSprite.opacity != 255:
            self.renderer.textSprite.opacity = 255
        self.renderer.backgroundSprite.setAlpha(100)
        self.updateFromObject()
        self.resetRenderState()
        pyglet.clock.unschedule(self.hideFunc)
        pyglet.clock.schedule_once(self.hideFunc, 7)

    def hideFunc(self, dt):
        self.hide()

    def hide(self):
        if not self.visible:
            return
        Label.hide(self)

    def updatePosition(self):
        return

    def updateFromObject(self):
        x, y = (sceneManager.convert)(*[x + y for x, y in zip(self.char.getPosition2D(), self.offset)])
        self.setPosition(round(x), round(y))

    def updateFromObjectNoRender(self):
        x, y = (sceneManager.convert)(*[x + y for x, y in zip(self.char.getPosition2D(), self.offset)])
        self.setPositionNoRender(round(x), round(y))

    def updateFromObjectRender(self, interp):
        self.setRenderPosition(interp)


watching_sheet = textureCache.getEffect("watching_01[6]", referencePoint=(RefPointType.TOPLEFT))
watching_sheet.setGUIReferencePoint()

class CharacterIconTable(Datatable):

    def __init__(self, char):
        Datatable.__init__(self, worldGUIContainer,
          maxRows=1,
          maxCols=4,
          position=(0, 0),
          size=(0, 0),
          draggable=False,
          visible=True)
        self.char = char
        self.setAutoFit()
        self.watching = None
        self.elite = None
        self.nocatch = None
        self.char.addLinkedObject(self)
        self.startVisible = False
        self.offset = (-self.getTableWidth() // 2, self.char.getHeight() + self.height + 10)
        self.updateFromObject()

    def fadeOut(self, duration):
        return

    def fadeTo(self, duration, alpha):
        return

    def addNoCatch(self):
        if not self.nocatch:
            self.nocatch = Picture(self, picture=(textureCache.getImageFile("lib/effects/no_catch_01.png")))
            self.add(self.nocatch)
            self.offset = (-self.getTableWidth() // 2, self.char.getHeight() + self.height + 10)
            self.updateFromObject()

    def removeNoCatch(self):
        self.deleteAndDestroy(self.nocatch)
        self.nocatch = None
        self.offset = (-self.getTableWidth() // 2, self.char.getHeight() + self.height + 10)
        self.updateFromObject()

    def addEyeIcon(self):
        self.watching = AnimatedPicture(self, picture=watching_sheet)
        self.add(self.watching)
        self.offset = (-self.getTableWidth() // 2, self.char.getHeight() + 5)
        self.updateFromObject()

    def hideWatched(self):
        if self.watching:
            if self.watching.visible:
                self.watching.hide()

    def updateWatched(self, distance):
        if not self.watching:
            self.addEyeIcon()
        else:
            if not self.visible:
                self.show()
            if distance >= 155.0:
                if self.watching.visible:
                    self.watching.hide()
            else:
                if not self.watching.visible:
                    self.watching.show()
            if distance >= 120:
                self.watching.setFrame(0)
            elif distance >= 100:
                self.watching.setFrame(1)
            elif distance >= 70:
                self.watching.setFrame(2)
            elif distance >= 60:
                self.watching.setFrame(3)
            elif distance >= 40:
                self.watching.setFrame(4)
            elif distance <= 20:
                self.watching.setFrame(5)

    def addEliteIcon(self):
        self.elite = Picture(self, picture=(textureCache.getImageFile("lib/effects/elite_01.png")))
        self.elite.setColor(126, 126, 126)
        self.add(self.elite)
        self.offset = (
         -self.getTableWidth() // 2, self.char.getHeight() + self.height + 10)
        self.updateFromObject()

    def setColor(self, r, g, b):
        return

    def updatePosition(self):
        return

    def forceHide(self):
        if self.visible:
            self.hide()

    def forceUnHide(self):
        if not self.visible:
            self.unHide()

    def updateFromObject(self):
        x, y = (sceneManager.convert)(*[x + y for x, y in zip(self.char.getPosition2D(), self.offset)])
        self.setPosition(x, y)

    def updateFromObjectNoRender(self):
        x, y = (sceneManager.convert)(*[x + y for x, y in zip(self.char.getPosition2D(), self.offset)])
        self.setPositionNoRender(x, y)

    def updateFromObjectRender(self, interp):
        self.setRenderPosition(interp)

    def setRenderPosition(self, interp):
        x, y = (sceneManager.convert)(*[x + y for x, y in zip(self.char.interp_state, self.offset)])
        self.setPosition(x, y)

    def setPositionNoRender(self, x, y):
        return

    @property
    def batch(self):
        return self.parent.batch
