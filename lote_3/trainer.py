# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\net\world\parse\trainer.py
from client.control.events.event import eventManager, eventDispatcher
from client.control.net.sending import packetManager
from client.control.service.session import sessionService
from client.control.system.background import backgroundController
from client.control.world.char import PCTrainer, NewPCTrainer
from client.data.cache import pokedexCache, nameCache
from client.data.container.char import charContainer
from client.data.container.map import mapContainer
from client.data.system.chat import chatConfig
from client.data.world.char import PcTrainerData
from shared.container.constants import IdRange, Direction, TrainerInfoType, Badges, TrainerGear
from shared.container.net import cmsg
from shared.service.utils import nullstrip
from client.control.system.cache import cacheController
from client.data.DB import mapDB
from client.control.world.action.walking import outOfViewManager
from client.interface.map.loading import loadingScreen
from client.interface.trainer import trainerCard

def TrainerClient(data):
    """ Creation of the main character. """
    _, trainerId, name, gender, skintone, bodyId, hairId, hairColor, clotheId, clotheColor, accessoryId, accessoryColor, gear, badges, walkingSpeed, mapId, x, y, z, partyID, teamID, job = data
    name = nullstrip(name)
    mapInfo = mapDB.getById(mapId)
    data = PcTrainerData()
    data.name = name
    data.id = trainerId
    data.gender = gender
    data.gear = TrainerGear(gear)
    data.badges = Badges(badges)
    data.appearance.gender = gender
    data.appearance.skintone = skintone
    data.appearance.body = bodyId
    data.appearance.hair.id = hairId
    data.appearance.hair.color = hairColor
    data.appearance.clothe.id = clotheId
    data.appearance.clothe.color = clotheColor
    data.appearance.accessory.id = accessoryId
    data.appearance.accessory.color = accessoryColor
    data.map = mapInfo
    data.partyID = partyID
    data.teamID = teamID
    data.job = job
    data.charType = IdRange.PC_TRAINER
    data.x = x
    data.y = y
    data.z = z
    data.walkingSpeed = walkingSpeed
    charContainer.addData(data)
    eventManager.notify("onBeforeMapLoad")
    loadingScreen.updateLoadingBar()
    area = mapContainer.getAreasAtPosition(mapInfo, x, y)
    if area:
        area.sort(key=(lambda x: x.getHeight()))
        name = area[0].name
    else:
        name = mapInfo.displayName
    loadingScreen.setLoadingMessage(name)
    eventManager.notify("onMapLoad", data.map, (x, y))
    clientTrainer = NewPCTrainer(data)
    sessionService.setClientTrainer(clientTrainer)
    charContainer.addChar(clientTrainer)
    charContainer.addClientChar(clientTrainer)
    eventManager.notify("onClientTrainerLoaded")
    for channel in chatConfig.getChannels():
        packetManager.queueSend(cmsg.JoinChat, channel.encode())

    packetManager.queueSend(cmsg.PokedexChecksum, pokedexCache.getChecksum())
    eventDispatcher.dispatch_event("onCharSelection", sessionService.trainer)
    eventManager.notify("onAfterMapLoad")
    eventManager.notify("onHideLoadingScreen")
    backgroundController.endOfBlackOut()
    eventManager.notify("onInputUnblocked")
    eventManager.notify("onShowDefaultGUI")


def TrainerMin(data):
    _, trainerId, name, gender, skintone, bodyId, hairId, hairColor, clotheId, clotheColor, accessoryId, accessoryColor, gear, walkingSpeed, mapId, x, y, z, facing, partyID, teamID, job = data
    name = nullstrip(name)
    idRange = IdRange.PC_TRAINER
    data = charContainer.getDataByIdIfAny(trainerId, idRange)
    if not data:
        data = PcTrainerData()
    data.name = name
    data.facing = Direction.toDeg[facing]
    data.id = trainerId
    data.gender = gender
    data.gear = TrainerGear(gear)
    data.appearance.gender = gender
    data.appearance.skintone = skintone
    data.appearance.body = bodyId
    data.appearance.hair.id = hairId
    data.appearance.hair.color = hairColor
    data.appearance.clothe.id = clotheId
    data.appearance.clothe.color = clotheColor
    data.appearance.accessory.id = accessoryId
    data.appearance.accessory.color = accessoryColor
    data.map = mapDB.getById(mapId)
    data.teamID = teamID
    data.partyID = partyID
    data.walkingSpeed = walkingSpeed
    data.setPosition(x, y, z)
    char = charContainer.getCharByIdIfAny(trainerId, idRange)
    if not char:
        char = NewPCTrainer(data)
        charContainer.addChar(char)
    else:
        char.setFacingNear(Direction.toDeg[facing])
        char.setPosition(x, y, z)
        char.applyEnvironmentEffects()
    if not char.visible:
        outOfViewManager.setInView(char)


def TrainerCard(data):
    _, trainerId = data
    charData = charContainer.getDataById(trainerId, IdRange.PC_TRAINER)
    trainerCard.showTrainer(charData)


def TrainerAchievements(data):
    _, trainerId, pvpWins, pvpLosses, pokedexSeen, pokedexCaught, job, createDate = data
    charData = charContainer.getDataById(trainerId, IdRange.PC_TRAINER)
    if charData:
        charData.stats.pvpWins = pvpWins
        charData.stats.pvpLosses = pvpLosses
        charData.stats.pokedexCaught = pokedexCaught
        charData.stats.pokedexSeen = pokedexSeen
        charData.stats.job = job
        charData.stats.createDate = createDate


def PokedexChecksum(data):
    from client.interface.pokemon.pokedex import pokedex
    pokedex.checksumValidated()


def PokedexList(data):
    from client.interface.pokemon.pokedex import pokedex
    pokedex.onPokedexReceived(data)


def PokedexUpdate(data):
    _, dexId, value = data
    from client.interface.pokemon.pokedex import pokedex
    pokedex.onPokedexUpdate(dexId, value)


def AppearanceList(data):
    trainerCard.onAppearanceList(data)


def AppearanceItemUpdate(data):
    _, appearanceType, appearanceId, appearanceColor = data
    trainerCard.onAppearanceItemUpdate(appearanceType, appearanceId, appearanceColor)


def AppearanceChange(data):
    _, trainerId, gender, skintone, bodyId, eyeId, accessoryId, accessoryColor, clothesId, clothesColor, hairId, hairColor = data
    data = charContainer.getDataById(trainerId, IdRange.PC_TRAINER)
    genderChanged = data.appearance.gender != gender
    data.appearance.gender = gender
    skintoneChanged = data.appearance.skintone != skintone
    data.appearance.skintone = skintone
    bodyChanged = data.appearance.body != bodyId
    data.appearance.body = bodyId
    eyeChanged = data.appearance.eyeId != eyeId
    data.appearance.eyeId = eyeId
    accessoryChanged = data.appearance.accessory.id != accessoryId
    data.appearance.accessory.id = accessoryId
    data.appearance.accessory.color = accessoryColor
    clothesChanged = data.appearance.clothe.id != clothesId
    data.appearance.clothe.id = clothesId
    data.appearance.clothe.color = clothesColor
    hairChanged = data.appearance.hair.id != hairId
    data.appearance.hair.id = hairId
    data.appearance.hair.color = hairColor
    char = charContainer.getCharByIdIfAny(trainerId, IdRange.PC_TRAINER)
    if char:
        char.renderer.updateAppearanceState(genderChanged, skintoneChanged, bodyChanged, eyeChanged, hairChanged, accessoryChanged, clothesChanged)


def InfoUpdate(data):
    _, trainerId, infoType, value = data
    if infoType == TrainerInfoType.BADGES.value:
        value = Badges(value)
        trainerData = sessionService.getClientTrainer().data
        trainerData.badges |= value
        trainerCard.newBadgeReceived(value)
    elif infoType == TrainerInfoType.GEAR.value:
        charData = charContainer.getDataByIdIfAny(trainerId, IdRange.PC_TRAINER)
        if charData:
            charData.gear |= value
            if trainerId == sessionService.getClientId():
                tg = TrainerGear(value)
                if tg == TrainerGear.SWIM:
                    eventManager.notify("onSystemMessage", "You have earned the swimming floaties that enables you to swim!")
    else:
        print("Warning: Received gear information update for trainer, but we do not know of him.")
