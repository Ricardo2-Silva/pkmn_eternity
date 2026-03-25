# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\system\logout.py
from twisted.python import log
from client.control.camera import worldCamera
from client.control.events import eventManager
from client.control.world.action.battle import battleController
from client.control.world.action.buffs import buffTimeHandler
from client.control.world.action.idle import idleCharManager
from client.control.world.action.physics import physicsController
from client.control.world.action.status import statusTimeHandler
from client.control.world.action.walking import walkerPositionManager, areaChange
from client.control.world.animation import animationManager
from client.control.world.warp import warpController
from client.control.world.weather import weatherController
from client.data.container.effects import effectContainer
from client.game import desktop
from client.control.service.session import sessionService
from client.data.container.char import charContainer
from client.interface.bag import bag
from client.interface.chat.chat import chat
from client.interface.cycle import timeWindow
from client.interface.group import groupController
from client.interface.guild import guild
from client.interface.help import helpWindow
from client.interface.hotbar import hotbar
from client.interface.inputMenu import inputMenu
from client.interface.npc.dialog import dialog
from client.interface.npc.quest import quest
from client.interface.npc.shop import shop
from client.interface.npc.storage import storage
from client.interface.pokemon.choose import choicePokemonPick
from client.interface.pokemon.details import pokemonSummary
from client.interface.pokemon.info import infoBar
from client.interface.pokemon.menu import pokemonMenu
from client.interface.pokemon.new import newPokemonWindow
from client.interface.pokemon.party import pokemonParty
from client.interface.pokemon.pokedex import pokedex
from client.interface.social import friendsList
from client.interface.system import mainMenu
from client.interface.trade import trade
from client.interface.trainer import trainerCard, trainerMenu

class LogoutManager:
    __doc__ = " When logging out we need to purge a ton of data, reset a bunch of UI and a lot of other things.\n        While we can cache certain things, it's best not to as if they are logged off and server changes something,\n        then keeping any data will put them out of sync.\n    "

    def __init__(self):
        return

    def onGameLogout(self):
        print("Info: Logging out.")
        eventManager.registerListener(self)
        eventManager.notify("onLogout")
        try:
            walkerPositionManager.reset()
            physicsController.reset()
            idleCharManager.reset()
            effectContainer.reset()
            warpController.reset()
            statusTimeHandler.reset()
            buffTimeHandler.reset()
            worldCamera.reset()
            areaChange.reset()
            weatherController.disableWeather()
            battleController.reset()
            animationManager.reset()
            sessionService.reset()
            charContainer.reset()
            mainMenu.reset()
            desktop.reset()
            timeWindow.forceHide()
            inputMenu.reset()
            bag.reset()
            storage.reset()
            quest.reset()
            hotbar.reset()
            guild.reset()
            friendsList.reset()
            chat.reset()
            groupController.reset()
            helpWindow.reset()
            trade.reset()
            trainerCard.reset()
            trainerMenu.reset()
            dialog.reset()
            shop.reset()
            pokemonParty.reset()
            choicePokemonPick.reset()
            pokemonSummary.reset()
            infoBar.reset()
            pokemonMenu.reset()
            newPokemonWindow.reset()
            pokedex.reset()
        except Exception as err:
            log.err()
            print("Error attempting logout.", err)

        eventManager.unregisterListener(self)
        print("Info: Logout finished.")


logoutManager = LogoutManager()
