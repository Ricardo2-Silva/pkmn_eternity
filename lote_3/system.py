# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\net\world\parse\system.py
from client.control.system.selection import selectionController
from shared.container.constants import ChatMessageType, IdRange, DisappearType
from shared.service.utils import nullstrip
from shared.controller.net.packetStruct import RawUnpacker
from client.control.events.event import eventManager, eventDispatcher
from client.data.container.char import charContainer
from client.data.DB import messageDB, mapDB
import time
from client.control.service.session import sessionService
from client.data.cache import nameCache
from client.control.world.action.walking import outOfViewManager
import sys
from client.control.world.weather import weatherController
from client.interface.chat.chat import chat
from client.interface.timing import timerDisplay
from twisted.internet import reactor

def PlayAnimation(data):
    _, charId, idRange, action, duration, setOrPlay = data
    char = charContainer.getCharByIdIfAny(charId, idRange)
    if char:
        if char.visible:
            if setOrPlay == 0:
                char.playAction(action, duration)
        elif setOrPlay == 1:
            char.setAction(action)


def InstanceTransition(data):
    _, charId, instanceId = data
    sessionService.instanceId = instanceId


class ServerTime:
    DAYLIGHT = 0
    NIGHTTIME = 1
    MORNING = 2


def Disappear(data):
    _, charId, idRange, disappearType = data
    char = charContainer.getCharByIdIfAny(charId, idRange)
    if char:
        if disappearType == DisappearType.EXPLOSION:
            eventManager.notify("onCharPlayEffect", char, "Explode")
            char.hide()
            charContainer.delChar(char)
        elif disappearType == DisappearType.FADE_OUT:
            outOfViewManager.setOutOfView(char)
        elif disappearType == DisappearType.DESTROY_FADE:

            def destroyChar(result, char):
                charContainer.delChar(char)

            d = char.renderer.fadeOut(0.3)
            d.addCallback(destroyChar, char)
        else:
            char.hide()
            charContainer.delChar(char)
    else:
        sys.stderr.write(f"Warning: Received Disappear for Char We do not know about. CharId: {charId} Char Type: {idRange}\n")


def CharSelection(data):
    _, charId, idRange = data
    char = charContainer.getCharById(charId, idRange)
    selectionController.selection_verified(char)


def Ping(data):
    now = time.perf_counter()
    pingTime = now - sessionService.pingTime
    pingTime *= 1000
    pingString = "%.2f" % pingTime
    chat.onShowMessage(f"Ping Response Time: {pingString}ms", style="SYSTEM", mType=(ChatMessageType.SYSTEM))


def ServerInfo(data):
    unpacker = RawUnpacker(data)
    _, serverTime, timeOfDay = unpacker.get("!BdB")
    motd = unpacker.getString()
    if motd:
        motd = motd.split("\n")
        if motd:
            for line in motd:
                chat.onShowMessage(line, style="SYSTEM", mType=(ChatMessageType.SYSTEM))

    currentTime = time.time()
    if currentTime < serverTime or currentTime - serverTime > 15:
        eventManager.notify("onSystemErrorMessage", "Your system time may not be accurate. Please correct your system's time settings or incorrect behavior will be observed.")


def MassNameQuery(data):
    packer = RawUnpacker(data)
    _, idCount, idRange = packer.get("!BBB")
    for _ in range(idCount):
        playerId = packer.get("I")
        name = packer.getString()
        nameCache.setPlayer(playerId, idRange, name)
        eventManager.notify("onNameQuery", playerId, idRange, name)

    nameCache.save()


def NameQuery(data):
    """ If for some reason the client needs name on an ID and doesn't have it. Request it. Usually for chat"""
    _, playerId, playerType, name = data
    name = nullstrip(name)
    nameCache.setPlayer(playerId, playerType, name)
    eventManager.notify("onNameQuery", playerId, playerType, name)


def OnlineCount(data):
    _, count = data
    if count == 1:
        string = f"There is {count} user connected."
    else:
        string = f"There are {count} users connected."
    eventManager.notify("onSystemMessage", string)


def MessageString(data):
    _, stringNum = data
    message = messageDB.getMessageByValue(stringNum)
    eventManager.notify("onSystemMessage", message)


def Disconnect(data):
    """ Disconnect packet """
    _, charId = data
    if charId == 0:
        sessionService.ingame = False
        eventManager.notify("onNotificationMessage", "Disconnect", "The game server has disconnected you.")
    else:
        char = charContainer.getCharByIdIfAny(charId, IdRange.PC_TRAINER)
        if char:
            pass
    if sessionService.isClientChar(char):
        sessionService.ingame = False
        eventManager.notify("onNotificationMessage", "Disconnect", "The game server has disconnected you.")
    elif char:
        if char.isWalking():
            char.stopWalking()
        charPokemon = list(charContainer.getCharsByTrainerId(char.getId(), char.getIdRange()))
        for pokemon in charPokemon:
            if char.followTarget:
                pokemon.stopFollow()
            if pokemon.isWalking():
                pokemon.stopWalking()
            pokemon.setReleased(False)
            pokemon.fadeOut(1)
            charContainer.delChar(pokemon, True)

        char.fadeOut(1)
        charContainer.delChar(char, True)
    else:
        print(f"Error: Tried to disconnect a character {charId} we don't have data for.")


def MapInfo(data):
    _, mapId, weatherId, flags = data
    mapInfo = mapDB.getById(mapId)
    mapInfo.information.weatherType = weatherId
    mapInfo.information.flags = flags
    weatherController.setWeather(mapInfo.information.weatherType, mapInfo.information.inside)


def TimerStart(data):
    _, timerType, timerSource, timeStamp, duration = data
    timerDisplay.addSource(timerType, timerSource, timeStamp, duration)


def InputDisable(data):
    """ Disable input of the client for specific events or otherwise:
        0 = Disable All
        1 = Enable All
    
     """
    _, timerType, duration = data
    from client.control.events.world import worldInputManager
    print("DISABLE PACKET", timerType)
    if timerType == 0:
        worldInputManager.on_disable()
        selectionController.on_disable()
        if duration:
            reactor.callLater(duration, worldInputManager.on_enable)
    else:
        worldInputManager.on_enable()
        selectionController.on_enable()


def UseAction(data):
    _, charId, charType, actionNum, setOrPlay = data
    char = charContainer.getCharByIdIfAny(charId, charType)
    if char:
        if setOrPlay == 0:
            char.playAction(actionNum)
        else:
            char.setAction(actionNum)


def WeatherChange(data):
    _, mapId, weatherId, intensity, speed, duration, temporary = data
    weatherController.setWeatherFromServer(mapId, weatherId, intensity, speed, duration, temporary)
