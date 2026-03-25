# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\world\warp.py
"""
Created on 21 juil. 2011

@author: Kami
"""
import rabbyt
from client.control.events.event import eventManager, eventDispatcher
from client.control.events.world import worldInputManager
from client.control.service.session import sessionService
from client.control.system.background import backgroundController
from client.control.world.map import WarpPoint
from client.data.DB import mapDB
from client.data.container.char import charContainer
from client.data.container.map import mapContainer
from client.data.world.map import WarpData
from shared.container.constants import WalkMode
from shared.container.geometry import Rect

class WarpController:

    def __init__(self):
        self.fadingOut = []
        eventManager.registerListener(self)
        self.warps = []
        self.in_range_warps = set()
        self.rect = Rect(0, 0, 64, 64)

    def reset(self):
        self.fadingOut.clear()

    def createWarp(self, warpId, x, y, width, height, graphicId):
        warp = WarpPoint(WarpData(graphicId, position=(x, y), size=(width, height)))
        if graphicId != 0:
            warp.hide()
            self.warps.append(warp)

    def update(self, dt):
        x, y, z = sessionService.getSelectedPosition()
        self.rect.position = (x - 32, y - 32)
        warpsNear = set(rabbyt.collisions.aabb_collide_single(self.rect, self.warps))
        newWarps = warpsNear - self.in_range_warps
        for warp in newWarps:
            if not warp.visible:
                warp.show()

        missingWarps = self.in_range_warps - warpsNear
        for warp in missingWarps:
            if warp.visible:
                warp.hide()

        self.in_range_warps = warpsNear

    def onCharWarp(self, char, mapId, entering):
        """ A char it's warping and it's not our char. Delete it from the map, and his pokemons too. """
        if entering == 1:
            pokemons = list(charContainer.getCharsByTrainerId(char.getId(), char.getIdRange()))
            for pokemon in pokemons:
                newPkmn = charContainer.getCharByIdIfAny(pokemon.getId(), pokemon.getIdRange())
                if newPkmn:
                    newPkmn.fadeIn(1)

            trainer = charContainer.getCharByIdIfAny(char.getId(), char.getIdRange())
            if trainer:
                eventManager.notify("onCharPlayEffect", char, "Warp")
                trainer.fadeIn(1)
        elif entering == 0:
            pokemons = list(charContainer.getCharsByTrainerId(char.getId(), char.getIdRange()))
            for pokemon in pokemons:
                pokemon.setReleased(False)
                if pokemon.isWalking():
                    pokemon.stopWalking()
                if pokemon.visible:
                    if not pokemon.renderer.fading:
                        d = pokemon.fadeOut(1)
                        d.addCallback(self._removeFading, pokemon)
                        self.fadingOut.append(pokemon)
                    else:
                        pokemon.hide()
                    charContainer.delChar(pokemon, True)

            if char.visible:
                eventManager.notify("onCharPlayEffect", char, "Warp")
                d = char.fadeOut(1)
                self.fadingOut.append(char)
                d.addCallback(self._removeFading, char)
            charContainer.delChar(char, True)

    def _deleteChar(self, dt, char):
        if charContainer.charExists(char.id, char.getIdRange()):
            charContainer.delChar(char, True)

    def _removeFading(self, result, char):
        if char in self.fadingOut:
            self.fadingOut.remove(char)

    def onBeforeMapLoad(self):
        r""" Before map loads we cancel all warp delays to \delete data since they will be deleted anyways."""
        self.warps.clear()
        self.in_range_warps.clear()
        for char in self.fadingOut:
            if char.renderer.fading:
                char.hide()

        self.fadingOut.clear()

    def onClientCharWarp(self, char, mapId, mapX, mapY):
        char = sessionService.getSelectedChar()
        if char.isWalking():
            char.stopWalking()
        else:
            worldInputManager.on_disable(False)
            for pokemon in sessionService.getClientPokemons():
                if pokemon.isWalking():
                    pokemon.stopWalking()

            eventManager.notify("onBeforeMapLoad")
            eventManager.notify("onBlockRendering")
            mapInfo = mapDB.getById(mapId)
            area = mapContainer.getAreasAtPosition(mapInfo, mapX, mapY)
            if area:
                area.sort(key=(lambda x: x.getHeight()))
                name = area[0].name
            else:
                name = mapInfo.displayName
        eventManager.notify("onShowLoadingScreen", name)
        eventManager.notify("onMapLoad", mapInfo, (mapX, mapY))
        trainer = sessionService.trainer
        trainer.data.setMap(mapInfo)
        trainer.show()
        trainer.setPosition(mapX, mapY)
        trainer.resetRenderState()
        trainer.applyEnvironmentEffects()
        eventManager.notify("onAfterMapLoad")
        if not sessionService.getSelectedChar() == trainer:
            eventDispatcher.dispatch_event("onCharSelection", trainer)
        for pokemon in sessionService.getClientPokemons():
            pokemon.data.setMap(mapInfo)
            if pokemon.isReleased():
                if pokemon.isWalking():
                    pokemon.stopWalking()
            if not pokemon.visible:
                if not pokemon.renderer.fading:
                    pokemon.show()
                    pokemon.renderer.restoreCompletely()
                if not pokemon.isFainted():
                    if not pokemon.data.walkMode == WalkMode.FOLLOW:
                        pokemon.data.walkMode = WalkMode.FOLLOW
                    if not pokemon.followTarget:
                        pokemon.followTarget = trainer
                    pokemon.setFollowPosition()
                    pokemon.resetRenderState()
                    pokemon.applyEnvironmentEffects()

        eventManager.notify("onHideLoadingScreen")
        backgroundController.endOfBlackOut()
        eventManager.notify("onInputUnblocked")
        worldInputManager.on_enable()


warpController = WarpController()
