# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\system\target.py
"""
Created on 28 dec. 2011

@author: Kami
"""
from client.control.events.event import eventManager, eventDispatcher
from client.data.settings import gameSettings
from client.data.world.item import ItemData
from client.data.DB import itemDB
from shared.container.constants import TargetType, CursorMode, ItemType
from client.control.net.sending import packetManager
from shared.container.net import cmsg
from shared.container.skill import SkillInfo, PokemonSkill
from client.control.service.session import sessionService
from client.data.world.char import PokemonData
from client.control.camera import worldCamera
import pyglet
from client.scene.manager import sceneManager
from pyglet.window import mouse
from client.data.container.char import charContainer
from client.game import desktop
from client.control.system.cursor import cursor

class Targetting(object):
    __doc__ = " Controls the targetting system is essentially a layer over the GUI, if targetting is not active it will fall back to the other controllers. "

    def __init__(self):
        self.active = False
        self.targetClose = None
        self.data = None
        self.target_list = []
        eventManager.registerListener(self)
        eventDispatcher.push_handlers(self)

    def changeCursorName(self, text):
        if not cursor.label.visible:
            cursor.label.visible = True
        cursor.text = text

    def clearCursorName(self):
        if cursor.label.visible:
            cursor.label.visible = False
        desktop._focusWidget = None

    @property
    def not_targetting(self):
        return cursor.mode not in CursorMode.TARGET_LIST

    def onQuickCast(self, data):
        self.onTargetMode(None)
        from client.control.events.world import worldInputManager
        self.active = True
        self.data = data
        self.targetClose = True
        worldPos = worldCamera.toMapPosition(worldInputManager.x, worldInputManager.y)
        focusedChar = (charContainer.getCharAtPosition)(*worldPos)
        print("TEST", worldPos, worldInputManager.x, worldInputManager.y)
        self.onTargetClick((worldInputManager.x), (worldInputManager.y), (worldInputManager.getShiftState()), targetData=focusedChar)
        self.onTargetMode(None)

    def _wipeTargetMode(self):
        cursor.targeting = False
        cursor.mode = CursorMode.DEFAULT
        self.clearCursorName()
        if self.target_list:
            for target in self.target_list:
                target.removeCaptureStatus()

            self.target_list.clear()

    def onTargetMode(self, data, closeAfter=False):
        self.active = True if data else False
        self.data = data if data else None
        self.targetClose = closeAfter
        if data is not None:
            if isinstance(self.data, SkillInfo):
                self.changeCursorName(self.data.name.title())
        elif isinstance(self.data, PokemonSkill):
            self.changeCursorName(self.data.skillInfo.name.title())
            cursor.mode = CursorMode.TARGET
        elif isinstance(self.data, ItemData):
            self.changeCursorName(f"{self.data.name.title()} ({self.data.quantity}x)")
            if self.data.itemInfo.target & TargetType.AREA:
                if self.data.itemInfo.target & TargetType.SELF:
                    cursor.radius = data.radius
                    cursor.mode = CursorMode.PLAYER_CIRCLE
            else:
                cursor.radius = data.radius
                cursor.mode = CursorMode.CIRCLE
        else:
            cursor.mode = CursorMode.TARGET
        if self.data.itemInfo.target == TargetType.COORDINATES:
            if self.data.itemInfo.type == ItemType.POKEBALL:
                self.target_list = (charContainer.getAllWildPokemonInArea)(*sessionService.getClientTrainer().getPosition2D(), *(500,
                                                                                                                                 500))
                for pokemon in self.target_list:
                    pokemon.showCaptureStatus()

            elif isinstance(self.data, PokemonData):
                self.changeCursorName(f"Release {self.data.name.title()}")
                cursor.mode = CursorMode.TARGET
            cursor.targeting = True
        else:
            self._wipeTargetMode()

    def onBeforeMapLoad(self):
        if self.active:
            eventManager.notify("onTargetMode", None)

    def onLogout(self):
        self.onBeforeMapLoad()

    def getActionAfterClose(self):
        return self.targetClose

    def on_mouse_release(self, x, y, button, modifiers):
        if self.active:
            if button == mouse.LEFT:
                wX, wY = sceneManager.convert(x, y)
                widget = desktop.getCollidingWidget(wX, wY)
                if widget:
                    self.onTargetClick(wX, wY, modifiers, guiButton=widget)
                    return pyglet.event.EVENT_HANDLED
                else:
                    focusedChar = (charContainer.getCharAtPosition)(*worldCamera.toMapPosition(x, y))
                    if focusedChar:
                        self.onTargetClick(x, y, modifiers, targetData=focusedChar)
                        return pyglet.event.EVENT_HANDLED
                    self.onTargetClick(x, y, modifiers)
                    return pyglet.event.EVENT_HANDLED
            if button == mouse.RIGHT:
                eventManager.notify("onTargetMode", None)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.active:
            return pyglet.event.EVENT_HANDLED

    def onCharSelection(self, char):
        if self.active:
            eventManager.notify("onTargetMode", None)

    def onItemDelete(self, itemData, nameId):
        if isinstance(self.data, ItemData):
            if self.data.nameId == nameId:
                eventManager.notify("onTargetMode", None)

    def onTargetClick(self, x, y, modifiers, targetData=None, guiButton=None):
        if sessionService.trade:
            eventManager.notify("onSystemMessage", "You cannot perform this action while in a trade.")
            return
        if isinstance(self.data, ItemData):
            if self.data.itemInfo.target == TargetType.COORDINATES:
                if guiButton:
                    print("Not mPos !! In target click. WTF?")
                    return
                (packetManager.queueSend)(cmsg.ItemThrow, self.data.nameId, *list(map(int, worldCamera.toMapPosition(x, y))))
            elif targetData:
                targetData = targetData.data
            elif guiButton:
                if guiButton.id == "PokemonParty":
                    targetData = guiButton.pkmnData
            else:
                if self.data.itemInfo.target & TargetType.NOTARGETS:
                    targetData = sessionService.getClientData()
            if not targetData:
                return
            if itemDB.canUse(targetData, self.data.nameId):
                packetManager.queueSend(cmsg.ItemUse, targetData.id, targetData.idRange, self.data.nameId)
            eventManager.notify("onTargetMode", None)
        elif isinstance(self.data, SkillInfo):
            print("trying to use a skill !", x, y, worldCamera.toMapPosition(x, y))
            eventManager.notify("onUseSkill", self.data, worldCamera.toMapPosition(x, y), targetData)
        elif isinstance(self.data, PokemonSkill):
            print("trying to use a skill !", x, y, worldCamera.toMapPosition(x, y))
            eventManager.notify("onUseSkill", self.data, worldCamera.toMapPosition(x, y), targetData)
        elif isinstance(self.data, PokemonData):
            pass
        eventManager.notify("onReleaseAttempt", self.data, worldCamera.toMapPosition(x, y), modifiers)
        if self.data.isReleased():
            if gameSettings.getHotbarRecall():
                eventManager.notify("onRecallAttempt", self.data)


targetting = Targetting()
