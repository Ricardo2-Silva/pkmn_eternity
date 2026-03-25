# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\world\action\release.py
"""
Created on 30 juil. 2011

@author: Kami
"""
import pyglet
from client.control.events import eventManager
from client.control.events.event import eventDispatcher
from client.control.net.sending import packetManager
from client.control.service.map import mapService
from client.control.service.session import sessionService
from client.control.system.selection import selectionController
from client.control.world.item import Ball
from client.data.container.map import mapContainer
from client.data.world.item import BallData
from shared.container.constants import Pokeball, IdRange, PlayerAction, GroundType, WalkMode
from shared.container.net import cmsg
from shared.service.direction import directionService
from shared.service.geometry import getAngleBetweenTwoPoints, isNear

class ReleaseController:
    __doc__ = " Controls pokemon releasing in the world."

    def __init__(self):
        eventManager.registerListener(self)

    def isReleasePossible(self, pkmnData, position, walkMode):
        if pkmnData.isReleased():
            eventManager.notify("onBattleMessage", "You cannot release a Pokemon that is already released!", log=False)
            return False
        else:
            if not (mapContainer.isPositionWalkable)(pkmnData, sessionService.trainer.data.map, *position):
                eventManager.notify("onBattleMessage", "You cannot release a Pokemon on invalid terrain!", log=False)
                return False
            else:
                grounds = GroundType.NOTHING | GroundType.ALL_GRASS
                if sessionService.canSwim():
                    grounds |= GroundType.ALL_WATER
                direction = sessionService.trainer.data.facing
                if direction == directionService.DOWN:
                    grounds |= GroundType.DOWN_ONLY
                elif direction == directionService.LEFT:
                    grounds |= GroundType.LEFT_ONLY
                else:
                    if direction == directionService.RIGHT:
                        grounds |= GroundType.RIGHT_ONLY
                if not mapContainer.isPathWalkable((sessionService.trainer.data.map), (sessionService.trainer.getPosition2D()),
                  position,
                  allowedWallHeight=0,
                  allowedGroundTypes=grounds,
                  radius=18):
                    eventManager.notify("onBattleMessage", "You cannot release a Pokemon with any obstacles in your line of sight!", log=False)
                    return
                if not isNear(sessionService.trainer.getPosition2D(), position, 200):
                    eventManager.notify("onBattleMessage", "You cannot release a Pokemon that far from you!", log=False)
                    return False
                if sessionService.trade:
                    eventManager.notify("onBattleMessage", "You cannot perform this action while in a trade.", log=False)
                    return False
            return True

    def onReleaseAttempt(self, pokemonData, position, modifiers):
        if modifiers & pyglet.window.key.MOD_SHIFT:
            walkmode = WalkMode.FOLLOW
        else:
            walkmode = WalkMode.FREE
        if not self.isReleasePossible(pokemonData, position, walkmode):
            print("Release not possible")
            return
        if sessionService.waiting:
            return
        if walkmode == WalkMode.FREE:
            if not pokemonData.isFainted():
                eventManager.notify("onMoveForceStop", True)
                sessionService.waiting = True
        packetManager.queueSend(cmsg.PokemonRelease, pokemonData.lineupId, int(position[0]), int(position[1]), walkmode)

    def release(self, ballData, pkmn, trainer, toPosition):
        pkmn.setReleased(True)
        fromPosition = trainer.getPosition2D()
        ball = Ball(ballData)
        if pkmn.isWalking():
            pkmn.stopWalking()
        (pkmn.setPosition)(*toPosition, **{"applyEffects": False})
        if pkmn.visible:
            pkmn.hide()
        trainer.setFacingNear(getAngleBetweenTwoPoints(fromPosition, toPosition))

        def releaseAndSelectPokemon(_):
            ball.releasePokemon()
            pkmn.release()
            if pkmn.isFainted() or pkmn.data.walkMode == WalkMode.FREE:
                if pkmn in sessionService.getClientPokemons():
                    if sessionService.getSelectedChar() == trainer:
                        if trainer.isWalking():
                            trainer.stopWalking()
                    eventDispatcher.dispatch_event("onCharSelection", pkmn)
                    packetManager.queueSend(cmsg.CharSelection, pkmn.getId(), pkmn.getIdRange())
                    selectionController.selection_send(pkmn)
            else:
                curTarget = pkmn.followTarget
            if curTarget:
                pkmn.followTarget = None
                if not pkmn.isWalking():
                    pkmn.startFollowing(curTarget)

        cb = (trainer.throw)(ball, *toPosition)
        cb.addCallback(releaseAndSelectPokemon)
        cb.addErrback(self.fail)

    def fail(self, err):
        print(err)

    def onPokemonRelease(self, trainer, pokemon, x, y):
        data = BallData(0, Pokeball.toItemId[pokemon.data.ballId], trainer.getPosition2D())
        data.map = trainer.data.map
        self.release(data, pokemon, trainer, (x, y))


releaseController = ReleaseController()
