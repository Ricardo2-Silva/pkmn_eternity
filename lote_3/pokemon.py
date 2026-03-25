# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\net\world\parse\pokemon.py
from client.control.events.event import eventManager
from client.control.world.action.walking import outOfViewManager
from client.control.world.map import Effect
from client.data.world.animation import Animation
from client.data.world.eggs import EggIncubator, PokemonEgg
from client.data.world.map import EffectData
from shared.service.utils import nullstrip
from shared.controller.net.packetStruct import RawUnpacker
from shared.container.constants import IdRange, StatType, Direction, WalkMode, CreatureAction, Emotes, WildPkmnFlag
from client.data.world.char import PokemonData, WildPokemonData
from client.control.world.char import Pokemon, NPCBattlePokemon, NPCPokemon, PCPokemon
from client.data.container.char import charContainer
from client.control.service.session import sessionService
import client.data.DB as library
from client.control.world.action.physics import Jump
from client.data.DB import expDB, mapDB
from client.control.utils.localization import localeInt
from twisted.internet import reactor
from shared.container.skill import PokemonSkill
from client.control.world.effects import effectManager
from client.control.world.action.buffs import buffTimeHandler
from client.interface.pokemon.info import infoBar
from client.interface.pokemon.choose import choicePokemonPick
import sys
from shared.service.geometry import getAngleBetweenTwoPoints
from client.control.world.action.evolution import evolutionController

def PokemonSelection(data):
    _, dexId1, dexId2, dexId3, dexId4, dexId5, dexId6 = data
    choicePokemonPick.onPokemonChoiceSelection([dexId1, dexId2, dexId3, dexId4, dexId5, dexId6])


def PokemonCreation(data):
    """When you encounter a Pokemon on the map, we need these."""
    _, charId, idRange, name, dexId, gender, subspecies, shiny, currentSpeed, speed, trainerId, state, distanceFromTrainer, angleFromTrainer, level, curHp, maxHp, walkMode, released, mapId, x, y, z = data
    name = nullstrip(name)
    data = charContainer.getDataByIdIfAny(charId, idRange)
    if not data:
        data = PokemonData()
    trainerIdChanged = True if (data and trainerId != data.trainerId) else False
    evolved = True if (data and dexId != data.dexId) else False
    data.id = charId
    data.idRange = idRange
    data.name = name
    data.trainerId = trainerId
    data.trainerIdRange = IdRange.NPC_CHARACTER if idRange == IdRange.NPC_BATTLE_PKMN else IdRange.PC_TRAINER
    data.dexId = dexId
    data.subspecies = subspecies
    data.gender = gender
    data.distanceFromTrainer = distanceFromTrainer
    data.angleFromTrainer = angleFromTrainer
    data.level = level
    data.shiny = shiny
    data.walkMode = walkMode
    data.released = bool(released)
    data.stats.hp.set(curHp, maxHp)
    data.stats.speed.set(currentSpeed, speed)
    data.map = mapDB.getById(mapId)
    data.setWalkingSpeed(data.stats.speed.permanent, currentSpeed)
    trainer = charContainer.getCharById(trainerId, data.trainerIdRange)
    char = charContainer.getCharByIdIfAny(charId, idRange)
    char_state_exists = char is not None
    if not char:
        if idRange == IdRange.NPC_BATTLE_PKMN:
            char = NPCBattlePokemon(data)
        else:
            char = PCPokemon(data)
        if trainer == sessionService.trainer:
            charContainer.addClientChar(char)
        charContainer.addChar(char)
    else:
        if char.renderer.ready:
            if evolved:
                char.renderer.changeSprites()
            char.renderer.restoreCompletely()
        if data.trainerIdRange == IdRange.PC_TRAINER:
            if not char.isFainted():
                if walkMode == WalkMode.FOLLOW:
                    if char.followTarget != trainer:
                        char.startFollowing(trainer)
                    char.setFollowPosition()
                    char.resetRenderState()
                    char.applyEnvironmentEffects()
            elif walkMode == WalkMode.FREE:
                char.setPosition(x, y, z)
                char.applyEnvironmentEffects()
            else:
                char.setPosition(x, y, z)
                char.resetRenderState()
                char.applyEnvironmentEffects()
        else:
            char.setPosition(x, y, z)
            char.resetRenderState()
            char.applyEnvironmentEffects()
    if char_state_exists:
        outOfViewManager.setInView(char)


def NpcPkmnRelease(data):
    _, charId, trainerId, ballId, x, y = data
    char_data = charContainer.getDataByIdIfAny(charId, IdRange.NPC_BATTLE_PKMN)
    char = charContainer.getCharByIdIfAny(charId, IdRange.NPC_BATTLE_PKMN)
    if not char_data:
        if char:
            raise Exception("The char exist when the data doesn't...")
        if not char_data:
            char_data = PokemonData()
            char_data.idRange = IdRange.NPC_BATTLE_PKMN
    else:
        char_data.stats.fullHeal()
    trainer = charContainer.getCharByIdIfAny(trainerId, IdRange.NPC_CHARACTER)
    if trainer is None:
        sys.stderr.write(" ***ERROR*** We got a release packet for a trainer that is not registered to the char service.\n")
        return
    if not char:
        char = NPCBattlePokemon(char_data)
    char_data.ballId = ballId
    charContainer.addCharIfNotExist(char)
    eventManager.notify("onPokemonRelease", trainer, char, x, y)


def PokemonRelease(data):
    """ Only received when client initiates a release manually. """
    _, charId, trainerId, ballId, x, y = data
    if charId == 0:
        if trainerId == 0:
            if ballId == 0:
                if x == 0:
                    if y == 0:
                        sessionService.waiting = False
                        return
            pokemon = charContainer.getCharByIdIfAny(charId, IdRange.PC_POKEMON)
            trainer = charContainer.getCharByIdIfAny(trainerId, IdRange.PC_TRAINER)
            if trainer:
                if not trainer.visible:
                    trainer.renderer.restoreCompletely()
        else:
            sys.stderr.write("Error : Received release a Pokemon with no info on his trainer! Not in Cache or Game. \n")
            return
        if pokemon:
            if not pokemon.visible:
                pokemon.renderer.restoreCompletely()
    else:
        sys.stderr.write("Error : We received release for Pokemon we have no information on! Not in Cache or Game. \n")
        return
    pokemon.data.ballId = ballId
    eventManager.notify("onPokemonRelease", trainer, pokemon, x, y)


def PokemonRecall(data):
    _, charId, charIdRange = data
    char = charContainer.getCharByIdIfAny(charId, charIdRange)
    if not char:
        sys.stderr.write("Warning: Received a recall for a Pokemon we do not know.\n")
        return
    eventManager.notify("onPokemonRecall", char)


def PokemonFull(data):
    """ Client receives full data for their own Pokemon."""
    _, id, dexId, name, lineupId, gender, level, cur_hp, max_hp, max_atk, max_def, max_atkSpec, max_defSpec, max_speed, nature, abilityId, ballId, shiny, itemId, released, frontVer, ot, subspecies, createdTime, createdMapId, createdLevel, flags, currentExp, maxExp, currentEnergy, maxEnergy = data
    name = nullstrip(name)
    ot = nullstrip(ot)
    data = charContainer.getDataByIdIfAny(id, IdRange.PC_POKEMON)
    if data:
        char = charContainer.getCharByIdIfAny(id, IdRange.PC_POKEMON)
        if char:
            charContainer.delChar(char, True)
        else:
            charContainer.delData(data)
    d = PokemonData()
    d.id = id
    d.trainerId = sessionService.trainer.data.id
    d.dexId = dexId
    d.name = name
    d.ot = ot
    d.gender = gender
    d.level = level
    d.nature = nature
    d.abilityId = abilityId
    d.ballId = ballId
    d.shiny = shiny
    d.heldNameId = itemId
    d.released = released
    d.lineupId = lineupId
    d.frontVer = frontVer
    d.subspecies = subspecies
    d.createdTime = createdTime
    d.createdMapId = createdMapId
    d.createdLevel = createdLevel
    d.flags = flags
    d.expThisLevel = expDB.calcExpByLevel(d.dexId, d.level)
    s = d.stats
    s.atk.set(max_atk, max_atk)
    s.spatk.set(max_atkSpec, max_atkSpec)
    s.defense.set(max_def, max_def)
    s.spdef.set(max_defSpec, max_defSpec)
    s.speed.set(max_speed, max_speed)
    s.hp.set(cur_hp, max_hp)
    s.exp.set(currentExp, maxExp)
    s.energy.set(currentEnergy, maxEnergy)
    charContainer.addDataIfNotExist(d)
    charContainer.addClientData(d)
    if d.lineupId:
        eventManager.notify("onPokemonReceived", d)


def PokemonDelete(data):
    _, pokemonId = data
    pokemonChar = charContainer.getCharByIdIfAny(pokemonId, IdRange.PC_POKEMON)
    if pokemonChar:
        charContainer.delChar(pokemonChar, False)
        charContainer.delClientChar(pokemonChar)
    pkmnData = charContainer.getDataByIdIfAny(pokemonId, IdRange.PC_POKEMON)
    if pkmnData:
        charContainer.delData(pkmnData)
        charContainer.delClientData(pkmnData)
    eventManager.notify("onPokemonDelete", pokemonId)


def WildPokemonCreate(data):
    _, isTagged, charId, name, dexId, subspecies, shiny, level, flags, currentSpeed, speed, mapId, x, y, z, facing, curHp, maxHp = data
    name = nullstrip(name)
    facing = Direction.toDeg[facing]
    pkmnData = charContainer.getDataByIdIfAny(charId, IdRange.NPC_WILD_PKMN)
    if not pkmnData:
        pkmnData = WildPokemonData()
    pkmnData.id = charId
    pkmnData.name = name
    pkmnData.level = level
    pkmnData.dexId = dexId
    pkmnData.subspecies = subspecies
    pkmnData.facing = facing
    pkmnData.map = mapDB.getById(mapId)
    pkmnData.x = x
    pkmnData.y = y
    pkmnData.shiny = shiny
    pkmnData.stats.hp.set(curHp, maxHp)
    pkmnData.stats.speed.set(currentSpeed, speed)
    pkmnData.tagged = bool(isTagged)
    pkmnData.flags = flags
    pkmnData.setWalkingSpeed(pkmnData.stats.speed.permanent, currentSpeed)
    c = Pokemon(pkmnData)
    if pkmnData.flags & WildPkmnFlag.ELITE:
        c.addEliteIcon()
    c.setFacingNear(facing)
    charContainer.addCharIfNotExist(c)
    c.spawn()
    if pkmnData.tagged:
        sessionService.trainer.emote(Emotes.NOTICE)
        if sessionService.getSelectedChar() is not sessionService.trainer:
            angle = getAngleBetweenTwoPoints((sessionService.trainer.data.x, sessionService.trainer.data.y), (x, y))
            sessionService.trainer.setFacingNear(angle)


def PokemonSkills(data):
    up = RawUnpacker(data)
    _, pkmnId, skillCount = up.get("!BHB")
    pkmnData = charContainer.getDataById(pkmnId, IdRange.PC_POKEMON)
    for _ in range(skillCount):
        skillId, isSaved = up.get("!HB")
        skillData = PokemonSkill(library.skillDB.getSkill(skillId))
        skillData.isSaved = isSaved
        if pkmnData:
            pkmnData.skills.addSkill(skillData)


def DeleteSkill(data):
    _, pkmnId, skillId, isSaved = data
    pkmnData = charContainer.getDataById(pkmnId, IdRange.PC_POKEMON)
    if isSaved:
        pkmnData.skills.delPendingSkill(skillId)
    else:
        pkmnData.skills.delSkill(skillId)
    eventManager.notify("onPokemonDeleteSkill", pkmnData, skillId, isSaved)


def NewSkill(data):
    _, pkmnId, skillId, isSaved = data
    skillDBData = library.skillDB.getSkill(skillId)
    pkmnData = charContainer.getDataById(pkmnId, IdRange.PC_POKEMON)
    if isSaved == 2:
        eventManager.notify("onSystemMessage", f"{pkmnData.name} failed to learn {skillDBData.name}. It can't learn this skill.")
        return
    skillData = PokemonSkill(skillDBData)
    skillData.isSaved = isSaved
    pkmnData.skills.addSkill(skillData)
    eventManager.notify("onPokemonNewSkill", pkmnData, skillData)


def LevelUp(data):
    _, pkmnId, pkmnType, level, currentExp, maxExp = data
    d = charContainer.getDataByIdIfAny(pkmnId, pkmnType)
    if d:
        d.stats.exp.set(currentExp, maxExp)
        d.level = level
        d.expThisLevel = expDB.calcExpByLevel(d.dexId, d.level)
        char = charContainer.getCharByIdIfAny(pkmnId, pkmnType)
        if char:
            if char.data.isReleased():
                eventManager.notify("onCharPlayEffect", char, "LevelUp")
        eventManager.notify("onPokemonLevelUp", d)
        eventManager.notify("onSystemMessage", f"{d.name} reached Level {level}!")


def XPGain(data):
    _, pkmnId, exp = data
    d = charContainer.getDataByIdIfAny(pkmnId, IdRange.PC_POKEMON)
    if d:
        d.stats.exp.current += exp
        eventManager.notify("onPokemonExp", d, exp)
        eventManager.notify("onBattleMessage", f'{d.name.title()} gained {localeInt(exp)} experience {"points" if exp > 1 else "point"}!')


def Evolve(data):
    _, pkmnId, pkmnType, dexId, name = data
    name = nullstrip(name)
    d = charContainer.getDataByIdIfAny(pkmnId, pkmnType)
    if d:
        d.dexId = dexId
        if name:
            d.name = name
        eventManager.notify("onPokemonEvolve", d, dexId)


def StatUpdate(data):
    """ THis is only used for permanent stat updates. Usually on level up or evolution"""
    _, pkmnId, pkmnType, hp, atk, defense, spatk, spdef, speed = data
    pokemonData = charContainer.getDataByIdIfAny(pkmnId, pkmnType)
    if pokemonData:
        pokemonData.stats.hp.permanent = hp
        pokemonData.stats.atk.permanent = atk
        pokemonData.stats.defense.permanent = defense
        pokemonData.stats.spatk.permanent = spatk
        pokemonData.stats.spdef.permanent = spdef
        pokemonData.stats.speed.permanent = speed
        pokemonData.setWalkingSpeed(data.stats.speed.permanent)
        eventManager.notify("onPokemonStatUpdate", pokemonData)
        print("Got new stats!", hp, atk, defense, spatk, spdef, speed)


def BuffStat(data):
    _, charId, charType, fromId, fromType, statType, modifierType, statValue, duration, maxStacks, startTime = data
    buffTimeHandler.applyBuff(charId, charType, fromId, fromType, statType, modifierType, statValue, duration, maxStacks, startTime)


def DebuffStat(data):
    _, charId, charType, fromId, fromType, statType, modifierType, statValue, duration, maxStacks, startTime = data
    buffTimeHandler.applyDebuff(charId, charType, fromId, fromType, statType, modifierType, statValue, duration, maxStacks, startTime)


def StatUpdateSingle(data):
    _, pkmnId, pkmnType, statType, minVal, maxVal = data
    charData = charContainer.getDataByIdIfAny(pkmnId, pkmnType)
    print("UPDATED STAT", pkmnId, pkmnType, charData)
    if charData:
        faintedOnMap = charData.isFainted() and charData.isReleased()
        charData.stats.get(statType).set(minVal, maxVal)
        eventManager.notify("onPokemonStatUpdate", charData)
        char = charContainer.getCharByIdIfAny(pkmnId, pkmnType)
        if char:
            if faintedOnMap:
                eventManager.notify("onCharPlayEffect", char, "Revive")
        elif statType == StatType.HP:
            eventManager.notify("onCharPlayEffect", char, "Heal")


def LineupChange(data):
    _, lineupId1, lineupId2 = data
    pokemon = [
     None, None]
    for pkmn in sessionService.getClientPokemonsData():
        if pkmn.lineupId == lineupId1:
            pokemon[0] = pkmn
        else:
            if pkmn.lineupId == lineupId2:
                pokemon[1] = pkmn

    pokemon[0].lineupId = lineupId2
    if pokemon[1] is not None:
        pokemon[1].lineupId = lineupId1
    eventManager.notify("onLineupSwitch", lineupId1, lineupId2)


def NewPokemon(data):
    _, pokemonId, dexId, gender = data
    if sessionService.incubators.hatching is False:
        eventManager.notify("onGetNewPokemon", pokemonId, dexId, gender)
    else:
        sessionService.incubators.waiting.append((pokemonId, dexId, gender))


def StatUpdateAll(data):
    _, pkmnId, pkmnType, hp, atk, defense, spatk, spdef, speed = data
    charData = charContainer.getDataById(pkmnId, pkmnType)
    charData.stats.hp.set(hp, hp)
    charData.stats.atk.permanent = atk
    charData.stats.defense.permanent = defense
    charData.stats.spatk.permanent = spatk
    charData.stats.spdef.permanent = spdef
    charData.stats.speed.permanent = speed
    eventManager.notify("onPokemonStatUpdate", charData)
    print("Got new stats!", hp, atk, defense, spatk, spdef, speed)


def EggIncubatorUpdate(data):
    _, createOrDel, incubatorId, eggId, startTime, currentUses, maxUses = data
    if createOrDel == 1:
        incubator = EggIncubator(incubatorId, None, startTime, currentUses, maxUses)
        sessionService.incubators.addIncubator(incubator)
        eventManager.notify("onIncubatorReceived", incubator)
    elif createOrDel == 0:
        sessionService.incubators.deleteIncubator(incubatorId)
        eventManager.notify("onIncubatorDeleted", incubatorId)
    elif createOrDel == 2:
        pass
    elif createOrDel == 3:
        incubator = sessionService.incubators.getIncubator(incubatorId)
        eventManager.notify("onEggHatch", incubator)


def EggDataReceived(data):
    _, eggId, parentOnedexId, parentTwoDexId, createTime, state, group, stored, incubatorId = data
    eggData = PokemonEgg(eggId, parentOnedexId, parentTwoDexId, createTime, state, group, stored, incubatorId)
    print("RECEIVED!", eggData)
    if stored == 0:
        incubator = sessionService.incubators.getIncubator(incubatorId)
        incubator.egg = eggData
        incubator.currentUses += 1
        eventManager.notify("onIncubatedEggReceive", incubator, eggData)


def DaycareOpen(data):
    _, daycareId, slots, costPerMinute, expPerMinute = data
    eventManager.notify("onDaycareOpen", daycareId, slots, costPerMinute, expPerMinute)


def DaycareUpdate(data):
    _, daycareId, status, pokemonId, addedTime, endTime, accruingDebt = data
    eventManager.notify("onDaycareUpdate", daycareId, status, pokemonId, addedTime, endTime, accruingDebt)


def DaycareInformation(data):
    eventManager.notify("onDaycareInformation", data)
