# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\net\world\parse\battle.py
from client.control.world.action.physics import ArcPath, Knockback
from client.data.container.char import charContainer
from client.data.settings import gameSettings
from shared.container.constants import IdRange, BattleUpdateType, RefPointType, TargetType, BattleCharUpdate, BattleType, Emotes
from client.control.events.event import eventManager
import struct
from client.control.world.action.skill_receive import skillController
from client.data.DB import skillDB
from client.control.service.session import sessionService
from client.control.world.action.status import statusEffectController
import sys
from client.data.world.map import EffectData
from client.data.world.animation import Animation
from twisted.internet import reactor
from client.interface.battle import playerChallenge
from shared.controller.net.packetStruct import RawUnpacker
import time
from client.control.world.action.battle import battleController
from shared.service.direction import directionService

def BattleUpdate(data):
    _, battleType, updateType, timeStamp = data
    if updateType == BattleUpdateType.BATTLE_CREATE:
        battleController.create(battleType)
    elif updateType == BattleUpdateType.BATTLE_START:
        battleController.start(timeStamp)
    elif updateType in (BattleUpdateType.BATTLE_END, BattleUpdateType.BATTLE_END_AREA, BattleUpdateType.BATTLE_END_LOSS, BattleUpdateType.BATTLE_WON):
        pass
    battleController.end(updateType)
    if battleType == BattleType.NPC:
        sessionService.npc = None


def BattleTarget(data):
    _, sourceId, sourceType, targetId, targetType = data
    if gameSettings.getTargetIndicator():
        sourceChar = charContainer.getCharByIdIfAny(sourceId, sourceType)
        targetChar = charContainer.getCharByIdIfAny(targetId, targetType)
        if sourceChar:
            if targetChar:
                arc = ArcPath(sourceChar, targetChar, source_offset=(0, sourceChar.getHeight() // 2), target_offset=(0, targetChar.getHeight() // 2), curveFactor=90, speed=11)
                arc.start()


def BattleInfo(data):
    _, startX, startY, radius = data
    battleController.setInfo(startX, startY, radius)


def TagStatus(data):
    _, charId, charType, tag = data
    char = charContainer.getCharByIdIfAny(charId, charType)
    if char:
        char.data.tagged = bool(tag)
        from client.control.world.object import globalNamePlate
        if globalNamePlate.char == char:
            globalNamePlate.setNamePlateColor()
        char.emote(Emotes.NOTICE)
    else:
        sys.stdout.write(f"Warning: Received tag for {charId}/{charType} but we don't know about it.\n")


def CharBattleUpdate(data):
    """ Updates about specific char in a battle. """
    _, charId, charIdRange, updateType = data
    char = charContainer.getCharByIdIfAny(charId, charIdRange)
    if char:
        if updateType == BattleCharUpdate.ADD:
            battleController.addChar(char)
    elif updateType == BattleCharUpdate.DEL:
        battleController.delChar(char)
    else:
        sys.stderr.write(f"""Error: We got a battle update of a character we don't know. Char ID: {charId}, Char Type: {charIdRange}, UpdateType: {"ADDED" if updateType == BattleCharUpdate.ADD else "DELETED"}\n""")


def CharDamage(data):
    _, charId, charIdRange, atkCharId, atkCharIdRange, skillid, skillInstanceId, damageType, hpPer, damageTags, extraData, timeStamp = data
    char = charContainer.getCharByIdIfAny(charId, charIdRange)
    atkChar = charContainer.getCharByIdIfAny(atkCharId, atkCharIdRange)
    if not char:
        sys.stderr.write(f"Warning: Received char damage from char that doesn't exist. Source: {charId}-{charIdRange}, Attacker: {atkCharId}-{atkCharIdRange}, Skill: {skillid}")
        return
    if not atkChar:
        sys.stderr.write(f"Warning: Received char damage from attacker that doesn't exist. Source: {charId}-{charIdRange}, Attacker: {atkCharId}-{atkCharIdRange}, Skill: {skillid}")
        return
    skill = skillDB.getById(skillid)
    eventManager.notify("onCharDamage", char, atkChar, skill, skillInstanceId, damageType, hpPer, damageTags, extraData, timeStamp)


def Damage(data):
    _, charId, charIdRange, skillid, damageType, hpPer, extraData, timeStamp = data
    charData = charContainer.getDataByIdIfAny(charId, charIdRange)
    char = charContainer.getCharByIdIfAny(charId, charIdRange)
    skill = skillDB.getByIdIfAny(skillid)
    eventManager.notify("onDamage", char, charData, skill, damageType, hpPer, extraData, timeStamp)


def Faint(data):
    _, charId, charIdRange, faintType = data
    char = charContainer.getCharByIdIfAny(charId, charIdRange)
    if char:
        char.faint(faintType)
    else:
        sys.stderr.write(f"Received Faint for Pokemon we don't have data for: {charId}/{charIdRange}\n")
        raise Exception(f"Received Faint for Pokemon we don't have data for: {charId}/{charIdRange}")


def Status(data):
    _, charId, charIdRange, status, duration, value = data
    char = charContainer.getCharById(charId, charIdRange)
    if char:
        if duration == 0:
            statusEffectController.cureStatus(char.data, status)
        else:
            statusEffectController.inflictStatus(char, status, duration, value)


def UseSkill(data):
    _, charId, charIdRange, skillId, instanceId, duration, timestamp = struct.unpack("!BHBHBBd", data[:16])
    char = charContainer.getCharByIdIfAny(charId, charIdRange)
    if char:
        if char in sessionService.getClientChars():
            pokemonSkill = char.data.skills.getActiveSkill(skillId)
            targetData = RawUnpacker(data[16:]).get("!" + pokemonSkill.skillInfo.struct)
            skillController.playerUseSkill(pokemonSkill, instanceId, char, duration, timestamp, targetData)
        else:
            skillInfo = skillDB.getById(skillId)
            targetData = RawUnpacker(data[16:]).get("!" + skillInfo.struct)
            skillController.useSkill(skillInfo, instanceId, char, duration, timestamp, targetData)


def SkillAck(data):
    _, charId, skillId, ack = data
    charData = charContainer.getDataByIdIfAny(charId, IdRange.PC_POKEMON)
    if charData:
        charData.predictionMovementLocked = False
        charData.predictionSkillLocked = False
        pokemonSkillData = charData.skills.getActiveSkill(skillId)
        if pokemonSkillData:
            if pokemonSkillData.awaitingAck:
                pokemonSkillData.awaitingAck = False
        elif ack == 0:
            print("FAILED ACK")
        elif ack == 1:
            print("SUCCESS ACK")
        elif ack == 2:
            eventManager.notify("onBattleMessage", f"{charData.name} hurt itself in its confusion!", log=True)
        else:
            print(f"WARNING: No skill data exists. {skillId}")
    else:
        print(f"WARNING: No char exists. {charId}")


def DeleteSkillInstance(data):
    """ Used to end skills early """
    _, charId, charIdRange, skillId, instanceId, skillOrDamageState = data
    charData = charContainer.getDataByIdIfAny(charId, charIdRange)
    if charData:
        if skillOrDamageState == 0:
            skillState = charData.damageStates.getSkill(skillDB.getById(skillId), instanceId)
        else:
            skillState = charData.skillStates.getSkill(skillDB.getById(skillId), instanceId)
        if skillState:
            skillState.stop(False)


SKILL_STATE = 0
DAMAGE_STATE = 1

def SkillDamageSource(data):
    _, charId, charIdRange, skillId, instanceId, result, targetId, targetIdRange, x, y, z, direction, radius, duration, timeStamp = data
    charData = charContainer.getDataByIdIfAny(charId, charIdRange)
    if charData:
        if result == SKILL_STATE:
            skillState = charData.skillStates.getSkill(skillDB.getById(skillId), instanceId)
        else:
            skillState = charData.damageStates.getSkill(skillDB.getById(skillId), instanceId)
        if skillState:
            skillState.onDamageSourceReceived(targetId, targetIdRange, x, y, z, direction, radius, duration, timeStamp)
        else:
            skillController.damageInstanceUse(skillId, targetId, targetIdRange, x, y, z, direction, radius, duration, timeStamp)


def SkillPositionUpdate(data):
    _, charId, charIdRange, skillId, instanceId, x, y = data
    charData = charContainer.getDataByIdIfAny(charId, charIdRange)
    if charData:
        skillState = charData.skillStates.getSkill(skillDB.getById(skillId), instanceId)
        if skillState:
            try:
                skillState.onPositionUpdate(x, y)
            except AttributeError:
                pass


def BattleKnockback(data):
    _, charId, charIdRange, direction, x, y, z, ts = data
    char = charContainer.getCharByIdIfAny(charId, charIdRange)
    if char:
        char.clearAllOrders()
        char.cancelAction()
        knockbackTime = 0.5 - (time.time() - ts)
        if char.direction != direction:
            char.direction = direction
        char.setStunDuration(knockbackTime)
        k = Knockback(char, (x, y, z), knockbackTime)
        k.start()


def DuelChallenge(data):
    _, trnId, itemUse, minLevel, maxLevel, maxPkmn, bet, party = data
    trnData = charContainer.getDataById(trnId, IdRange.PC_TRAINER)
    trnName = "Unknown"
    if trnData:
        trnName = trnData.name
    playerChallenge.onChallengeRequest(trnName, itemUse, minLevel, maxLevel, maxPkmn, bet, party)


def DuelResponse(data):
    _, response = data
    playerChallenge.onChallengeResponse(response)
