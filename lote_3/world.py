# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\events\world.py
"""
Created on 28 juil. 2011

@author: Kami
"""
import time
from client.control.net.sending import packetManager
from client.control.world.action.pathfinding import PathFinding
from client.data.container.char import charContainer
from client.control.service.session import sessionService
from client.control.events import eventManager
from client.control.camera import worldCamera
from client.control.system.target import targetting
from pyglet.window import mouse, key
import pyglet
from client.scene.manager import sceneManager
from client.data.settings import gameSettings
from shared.container.geometry import Rect
from shared.container.net import cmsg
from shared.service.direction import directionService
from pyglet.window.key import KeyStateHandler
from client.control.system.cursor import cursor
from shared.container.constants import CursorMode, WalkMode
from shared.container.euclid import Vector2

class WorldInputManager:
    __doc__ = " Gets input done from keyboard/mouse on the world and send the associated event. "

    def __init__(self):
        self.x = 0
        self.y = 0
        self.overedChar = None
        self.focusedChar = None
        self.desktopFocused = False
        eventManager.registerListener(self)
        self.keys = KeyStateHandler()
        self.move_state = {key: self.keys[key] for key in gameSettings.getDirectionKeys()}
        self.allowed = False
        self.enabled = True
        self.moveVector = Vector2()
        pyglet.clock.schedule_interval(self._move_key_test, 0.08333333333333333)
        self.followCooldown = time.time()

    def on_disable(self, packet=True):
        self.enabled = False
        self.releaseAllWalkingKeys(packet)

    def on_enable(self):
        self.enabled = True

    def releaseAllKeys(self):
        for key in self.keys:
            self.keys[key] = False

    def isKeyPressed(self, key):
        return self.keys[key]

    def _move_key_test(self, dt):
        key_states = {key: self.keys[key] for key in gameSettings.getDirectionKeys()}
        if self.enabled:
            if not self.desktopFocused:
                for key, state in key_states.items():
                    if state != self.move_state[key]:
                        if state is True:
                            eventManager.notify("onMovingKeyDown", key)
                        else:
                            eventManager.notify("onMovingKeyUp", key)

        self.move_state = key_states

    def on_key_press(self, symbol, modifiers):
        if not self.enabled:
            return
        else:
            self.desktopFocused = False
            if sessionService.selected == sessionService.trainer:
                if symbol == pyglet.window.key.H:
                    if time.time() - self.followCooldown > 0.4:
                        for pokemon in sessionService.getClientPokemons():
                            if pokemon.isReleased() and pokemon.data.walkMode == WalkMode.FREE:
                                pokemon.data.unselectedMode = pokemon.data.skillStates.inUse() or WalkMode.FOLLOW
                                packetManager.queueSend(cmsg.MakeFollow, pokemon.data.id, pokemon.data.idRange, sessionService.trainer.getId(), sessionService.trainer.getIdRange())

                        self.followCooldown = time.time()
            else:
                if symbol == pyglet.window.key.G:
                    if time.time() - self.followCooldown > 0.4:
                        for pokemon in sessionService.getClientPokemons():
                            if pokemon.isReleased() and pokemon.data.walkMode == WalkMode.FOLLOW:
                                pokemon.data.unselectedMode = WalkMode.FREE
                                packetManager.queueSend(cmsg.StopFollow, pokemon.data.id, pokemon.data.idRange)

                        self.followCooldown = time.time()
                eventManager.notify("onKeyDown", symbol, modifiers)
            if modifiers & pyglet.window.key.MOD_ALT:
                if symbol == pyglet.window.key.Z:
                    eventManager.notify("onToggleGui")

    def on_key_release(self, symbol, modifiers):
        if not self.enabled:
            return

    def on_mouse_release(self, x, y, button, modifiers):
        if not self.enabled:
            return
        else:
            focusedChar = (charContainer.getCharAtPosition)(*worldCamera.toMapPosition(x, y))
            if focusedChar:
                eventManager.notify("onCharMouseClick", x, y, button, focusedChar)
                if self.focusedChar != focusedChar:
                    self.focusedChar = sessionService.trainer
            elif self.focusedChar:
                pass
            if self.focusedChar != sessionService.trainer:
                self.focusedChar = sessionService.trainer
                eventManager.notify("onCharMouseLeftClick", self.focusedChar)
                return pyglet.event.EVENT_HANDLED
            return pyglet.event.EVENT_UNHANDLED

    def on_mouse_motion(self, x, y, dx, dy):
        """ Get char at specific position. """
        self.x, self.y = x, y
        overedChar = (charContainer.getCharAtPosition)(*worldCamera.toMapPosition(x, y))
        if overedChar:
            if self.overedChar:
                if self.overedChar != overedChar:
                    self.overedChar.unHighlight()
                    overedChar.highlight()
            else:
                overedChar.highlight()
                cursor.mode = CursorMode.POINTER
            self.overedChar = overedChar
            return pyglet.event.EVENT_UNHANDLED
        else:
            self.clearMouseOver()
            return pyglet.event.EVENT_UNHANDLED

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if scroll_y < 0:
            if self.isKeyPressed(key.LSHIFT):
                eventManager.notify("onZoom", -1.0)
                return pyglet.event.EVENT_HANDLED
        if scroll_y > 0:
            if self.isKeyPressed(key.LSHIFT):
                eventManager.notify("onZoom", 1.0)
                return pyglet.event.EVENT_HANDLED

    def clearMouseOver(self):
        if self.overedChar:
            self.overedChar.unHighlight()
            cursor.mode = CursorMode.DEFAULT
            self.overedChar = None

    def onBeforeMapLoad(self):
        self.clearMouseOver()

    def onLogout(self):
        self.onBeforeMapLoad()

    def isKeyUsedForWalking(self, key):
        return key in gameSettings.getDirectionKeys()

    def getShiftState(self):
        if self.keys.get(key.LSHIFT) is True or self.keys.get(key.RSHIFT) is True:
            return key.MOD_SHIFT
        else:
            return 0

    def releaseAllWalkingKeys(self, packet=True):
        was_held = False
        for keyboardKey in gameSettings.getDirectionKeys():
            if self.keys[keyboardKey]:
                was_held = True
                self.keys[keyboardKey] = False

        if was_held:
            print("RELEASE ALL FORCE STOP")
            eventManager.notify("onMoveForceStop", packet)

    def attemptAutoMove(self):
        """ Incase you are holding left or right, and something like stun interrupts. This makes it so you don't need to release and press again """
        for key in gameSettings.getDirectionKeys():
            if self.isKeyPressed(key):
                eventManager.notify("onMovingKeyDown", key)
                return

    def getDirectionFromKeyDown(self, keyDown):
        up, right, down, left = gameSettings.getDirectionKeys()
        if keyDown == up:
            if self.keys[right]:
                return directionService.UP_RIGHT
            else:
                if self.keys[left]:
                    return directionService.UP_LEFT
                return directionService.UP
        if keyDown == left:
            if self.keys[up]:
                return directionService.UP_LEFT
            else:
                if self.keys[down]:
                    return directionService.DOWN_LEFT
                return directionService.LEFT
        if keyDown == right:
            if self.keys[up]:
                return directionService.UP_RIGHT
            else:
                if self.keys[down]:
                    return directionService.DOWN_RIGHT
                return directionService.RIGHT
        if keyDown == down:
            if self.keys[left]:
                return directionService.DOWN_LEFT
            else:
                if self.keys[right]:
                    return directionService.DOWN_RIGHT
                return directionService.DOWN

    def getDirectionFromKeyUp(self, keyUp):
        up, right, down, left = gameSettings.getDirectionKeys()
        if keyUp == up:
            if self.keys[right]:
                return directionService.RIGHT
            else:
                if self.keys[left]:
                    return directionService.LEFT
                if self.keys[down]:
                    return directionService.DOWN
        elif keyUp == left:
            if self.keys[up]:
                if self.keys[right]:
                    return directionService.UP_RIGHT
                else:
                    return directionService.UP
            else:
                if self.keys[down]:
                    if self.keys[right]:
                        return directionService.DOWN_RIGHT
                    else:
                        return directionService.DOWN
                if self.keys[right]:
                    return directionService.RIGHT
        elif keyUp == right:
            pass
        if self.keys[up]:
            if self.keys[left]:
                return directionService.UP_LEFT
            else:
                return directionService.UP
        if self.keys[down]:
            if self.keys[left]:
                return directionService.DOWN_LEFT
            else:
                return directionService.DOWN
        if self.keys[left]:
            return directionService.LEFT
        else:
            if keyUp == down:
                if self.keys[left]:
                    return directionService.LEFT
            if self.keys[right]:
                return directionService.RIGHT
            else:
                if self.keys[up]:
                    return directionService.UP
                return

    def on_deactivate(self):
        self.releaseAllWalkingKeys()

    def onDesktopLostFocus(self):
        self.desktopFocused = False

    def onDesktopGetFocus(self):
        self.desktopFocused = True
        self.releaseAllWalkingKeys()


worldInputManager = WorldInputManager()
