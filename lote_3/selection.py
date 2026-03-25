# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\system\selection.py
"""
Created on 8 oct. 2011

@author: Kami

"""
from twisted.internet import defer
from client.control.events.event import eventManager, eventDispatcher
from client.control.service.session import sessionService
from client.control.net.sending import packetManager
from shared.container.net import cmsg
from shared.container.constants import WalkMode, IdRange, INTERACT_RANGE
from pyglet.window import key
from client.scene.manager import sceneManager
from shared.service.geometry import getDistanceBetweenTwoPoints, getAngleBetweenTwoPoints
from client.data.settings import gameSettings
from client.data.container.char import charContainer
import operator
from pyglet.window import mouse
from shared.container.geometry import createQuadRotated
import rabbyt
from client.data.container.map import mapContainer

class SelectionService:
    __doc__ = " Controls the player's chars and the one currently selected. "

    def __init__(self):
        self.enabled = True
        eventManager.registerListener(self)
        sceneManager.window.push_handlers(self)
        eventDispatcher.push_handlers(self)
        self._selection_order = []

    def on_disable(self, packet=True):
        self.enabled = False

    def on_enable(self):
        self.enabled = True

    def selection_send(self, char):
        self._selection_order.append((char, char.getWalkOrderNum()))

    def selection_verified(self, char):
        if sessionService.waiting:
            sessionService.waiting = False
        first_char, walkOrder = self._selection_order.pop(0)
        if first_char == char:
            print("VERIFIED")
        else:
            print("FAILED VERIFICATION", first_char, char, char.getWalkOrderNum(), walkOrder)
            old_char = sessionService.getSelectedChar()
        if old_char != char:
            first_char.setWalkOrderNumber(walkOrder)
            eventDispatcher.dispatch_event("onCharSelection", char)
            if char.followTarget:
                char.stopFollow()

    def onCharSelection(self, new_selection):
        old_selection = sessionService.getSelectedChar()
        sessionService.selectChar(new_selection)
        if old_selection:
            if old_selection.isWalking():
                old_selection.stopWalking()
        if new_selection.data.isPokemon():
            if new_selection.isWalking():
                new_selection.stopWalking()
            if old_selection and (sessionService.battle.isActive() or old_selection.data.isPokemon()):
                if old_selection.data.walkMode == WalkMode.FREE:
                    if old_selection.data.unselectedMode == WalkMode.FOLLOW:
                        if old_selection.data.released:
                            if not old_selection.isFainted():
                                if not old_selection.isWalking():
                                    old_selection.startFollowing(sessionService.trainer)
        elif not old_selection.isWalking():
            pass
        if old_selection.followTarget:
            old_selection.walkToTarget()

    def autoSelectFromBattle(self, battleStart):
        """ Here we auto select based on parameters.
            If battle started, select a pokemon.
            If battle ended, select a trainer.
        """
        if self.enabled:
            selected_char = sessionService.getSelectedChar()
            if battleStart is True:
                if not selected_char.data.isPokemon():

                    def checkPokemonOnTrainerStop(cb):
                        if sessionService.isInBattle():
                            chars = sessionService.getClientPokemons()
                            chars.sort(key=(lambda pokemon: pokemon.data.lineupId))
                            for char in chars:
                                if char.visible:
                                    if not char.renderer.fading:
                                        if char.data.canBeSelected():

                                            def sendSelectionPacket(_):
                                                if sessionService.isInBattle():
                                                    if sessionService.getSelectedChar() == sessionService.getClientTrainer():
                                                        if self.canBeSelected(char):
                                                            self.selection_send(char)
                                                            eventDispatcher.dispatch_event("onCharSelection", char)
                                                            packetManager.queueSend(cmsg.CharSelection, char.getId(), char.getIdRange())

                                            if char.isWalking():
                                                pd = defer.Deferred()
                                                pd.addCallback(sendSelectionPacket)
                                                char.event = pd
                                            else:
                                                sendSelectionPacket(None)
                                            return

                    if selected_char.isWalking():
                        d = defer.Deferred()
                        d.addCallback(checkPokemonOnTrainerStop)
                        selected_char.event = d
                else:
                    checkPokemonOnTrainerStop(None)
            elif battleStart is False and selected_char.data.isPokemon():

                def checkTrainerOnPokemonStop(_):
                    trainer = sessionService.getClientTrainer()
                    if sessionService.getSelectedChar() != trainer:

                        def sendTrainerSelectionPacket(_):
                            if sessionService.getSelectedChar() != trainer:
                                self.selection_send(trainer)
                                eventDispatcher.dispatch_event("onCharSelection", trainer)
                                packetManager.queueSend(cmsg.CharSelection, trainer.getId(), trainer.getIdRange())

                        if trainer.isWalking():
                            td = defer.Deferred()
                            td.addCallback(sendTrainerSelectionPacket)
                            trainer.event = td
                        elif selected_char.canMove():
                            sendTrainerSelectionPacket(None)
                        else:
                            dpf = selected_char.data.getCallbackWhenMovable()
                            dpf.addCallback(sendTrainerSelectionPacket)

                if selected_char.isWalking():
                    d = defer.Deferred()
                    d.addCallback(checkTrainerOnPokemonStop)
                    selected_char.event = d
            else:
                checkTrainerOnPokemonStop(None)

    def on_key_press(self, symbol, modifiers):
        """ Select a char on tab """
        if self.enabled:
            if symbol == gameSettings.getKey("rotate_select"):
                chars = sessionService.getClientChars()
                charCount = len(chars)
                loopPrevent = 0
                if charCount > 1:
                    index = chars.index(sessionService.getSelectedChar()) + 1
                    if index == charCount:
                        index = 0
                    while not (chars[index].visible and not chars[index].renderer.fading and self.canBeSelected(chars[index])):
                        index += 1
                        if index == charCount:
                            index = 0
                        else:
                            loopPrevent += 1
                            if loopPrevent >= charCount:
                                return

                    self.selection_send(chars[index])
                    eventDispatcher.dispatch_event("onCharSelection", chars[index])
                    print("SENDING SELECTION PACKET", chars[index].getId(), chars[index].getIdRange())
                    packetManager.queueSend(cmsg.CharSelection, chars[index].getId(), chars[index].getIdRange())
            if symbol == gameSettings.getKey("npc_interact"):
                if sessionService.getSelectedChar():
                    direction = sessionService.getSelectedChar().getFacing()
                    x, y = sessionService.getSelectedChar().getPositionInFrontMiddle(direction, 0)
                    collidingChars = charContainer.getAllInteractablesInDirection(x, y, 0, direction, INTERACT_RANGE, 20)
                    if len(collidingChars) != 0:
                        sortChars = list(collidingChars)
                        sortChars.sort(key=(operator.attrgetter("_realY_")))
                        self.interactWithNpc(sortChars[0])

    def canBeSelected(self, char):
        if char.isWalking() or sessionService.getSelectedChar().isWalking():
            print("MOVING")
            return False
        else:
            if not char.canBeSelected():
                print("CANT BE SELECTED")
                return False
            else:
                if char.followTarget and char.followTarget.isWalking():
                    print("HAS A TARGET AND TARGET IS WALKING")
                    return False
                else:
                    if char == sessionService.getSelectedChar():
                        print("CHAR IS ALREADY SELECTED", char)
                        return False
                    mapContainer.isPositionWalkableForChar(char) or print("NOT ON SELECTABLE TERRAIN", char, char.getPosition2D())
                    return False
            return True

    def onCharMouseClick(self, x, y, button, char):
        if button == mouse.LEFT:
            if char in sessionService.getClientChars():
                if self.canBeSelected(char):
                    self.selection_send(char)
                    eventDispatcher.dispatch_event("onCharSelection", char)
                    print("SENDING CHAR SELECTION", char.getId(), char.getIdRange())
                    packetManager.queueSend(cmsg.CharSelection, char.getId(), char.getIdRange())
            else:
                self.interactWithNpc(char)

    def interactWithNpc(self, charData):
        if sessionService.npc:
            print("~~NPC Attached already.")
            return
        else:
            if sessionService.trade:
                return
            if charData:
                if getDistanceBetweenTwoPoints(sessionService.getSelectedPosition()[:2], charData.getPosition2D()) > INTERACT_RANGE:
                    return False
                else:
                    npcData = charData.data
                    if sessionService.getSelectedPosition()[:2] != charData.getPosition2D():
                        charAngle = getAngleBetweenTwoPoints(sessionService.getSelectedPosition()[:2], charData.getPosition2D())
                        npcAngle = getAngleBetweenTwoPoints(charData.getPosition2D(), sessionService.getSelectedPosition()[:2])
                    else:
                        charAngle = None
                    npcAngle = None
                if charData.getIdRange() == IdRange.NPC_CHARACTER:
                    if sessionService.isInBattle():
                        return
                if charAngle:
                    sessionService.getSelectedChar().setFacingNear(charAngle)
                if npcData.idRange == IdRange.NPC_CHARACTER:
                    if npcAngle:
                        charData.setFacingNear(npcAngle)
                    packetManager.queueSend(cmsg.NpcDialogHello, npcData.id)
                elif charData.getIdRange() == IdRange.NPC_OBJECT:
                    if sessionService.isInBattle():
                        return
                    if charAngle:
                        sessionService.getSelectedChar().setFacingNear(charAngle)
                    packetManager.queueSend(cmsg.NpcObjectInteract, npcData.id, npcData.idRange)
                elif charData.getIdRange() == IdRange.NPC_BERRY:
                    packetManager.queueSend(cmsg.NpcObjectInteract, npcData.id, npcData.idRange)
                elif charData.getIdRange() == IdRange.NPC_ITEM:
                    packetManager.queueSend(cmsg.NpcItemInteract, npcData.id)


selectionController = SelectionService()
