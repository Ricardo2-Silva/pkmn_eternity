# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\world\action\skill_client.py
"""
Created on Jul 13, 2017

@author: Admin

This module is for client to game_server skill use.

"""
from shared.container.skill import PokemonSkill
from shared.controller.net.packetStruct import RawPacker
from shared.container.constants import TargetType, IdRange
from client.control.events.event import eventManager
from client.control.service.session import sessionService
from shared.container.net import cmsg
from client.control.net.sending import packetManager
from client.control.camera import worldCamera
from shared.service.geometry import getAngleBetweenTwoPoints, getDistanceBetweenTwoPoints

class SkillRequest:
    __doc__ = " Send a skill request to the game_server. "

    def __init__(self):
        eventManager.registerListener(self)

    def _canUseSkill(self, pokemon, skillData: PokemonSkill, target, worldPosition):
        """ Security to make sure we cannot do unintended things. """
        if not pokemon.canAttack():
            print(" ***** Can not use skill because of evolving or dead.")
            return False
        else:
            print(f"Energy Currently : {pokemon.data.stats.energy.current}. Required: {skillData.skillInfo.energy}")
            if skillData.awaitingAck:
                print("Skill was already used, awaiting response from server.")
                return False
            if skillData.skillInfo.maxRange:
                if skillData.skillInfo.target & TargetType.CHAR:
                    if target:
                        dist = getDistanceBetweenTwoPoints(pokemon.getPosition2D(), target.getPosition2D())
                        if dist > skillData.skillInfo.maxRange:
                            eventManager.notify("onBattleMessage", "The target is too far away to use this skill.", log=False)
                            print(f" *** Failed to use skill {skillData.skillInfo} due to range limit of {skillData.skillInfo.maxRange}. Current range: {dist}")
                            return False
                    else:
                        print("Failed to use a target skill, character doesn't exist.")
                        return False
                if skillData.skillInfo.target & TargetType.COORDINATES:
                    dist = getDistanceBetweenTwoPoints(pokemon.getPosition2D(), worldPosition)
                    if dist > skillData.skillInfo.maxRange:
                        eventManager.notify("onBattleMessage", "The target is too far away to use this skill.", log=False)
                        print(f" *** Failed to use skill {skillData.skillInfo} due to range limit of {skillData.skillInfo.maxRange}. Current range: {dist}")
                        return False
            if not pokemon.data.stats.canUseEnergy(skillData.skillInfo.energy):
                eventManager.notify("onBattleMessage", "Not enough energy to use that skill.", log=False)
                print(" ***** Can not use skill because of energy.", skillData.skillInfo.energy, pokemon.data.stats.energy.current)
                return False
            if not sessionService.ticks.canUseSkill():
                eventManager.notify("onBattleMessage", "Cannot use skill due to global cooldown.", log=False)
                print(" ***** Can not use skill because of global cooldown.")
                return False
            if skillData.isSaved:
                eventManager.notify("onBattleMessage", "Cannot use skill, it is pending and not active.", log=False)
                return False
            if not skillData.canUse():
                eventManager.notify("onBattleMessage", "Cannot use skill due to skill cooldown.", log=False)
                print("Cannot use skill because of skill cooldown.")
                return False
            if skillData.skillInfo.target & TargetType.CHAR:
                if not target:
                    eventManager.notify("onBattleMessage", "You need a target to use this skill!", log=False)
                    return False
                if skillData.skillInfo.target & TargetType.POKEMON:
                    if target.data.idRange not in IdRange.POKEMON:
                        eventManager.notify("onBattleMessage", "You need a proper target to use this skill!", log=False)
                        return False
            return True

    def onUseSkill(self, skill: PokemonSkill, worldPosition, target=None):
        char = sessionService.getSelectedChar()
        if self._canUseSkill(char, skill, target, worldPosition):
            print(" ***** USING SKILL (REQUESTING)", skill.skillInfo)
            self._sendSkillUseAttempt(char, skill.skillInfo, worldPosition, target)
            sessionService.ticks.setSkill()
            skill.awaitingAck = True

    def _applyPrediction(self, char, skillInfo):
        if not skillInfo.allow_movement:
            if char.isWalking():
                char.stopWalking()
                char.stopPacket()
            char.data.predictionMovementLocked = True
        if not skillInfo.allow_skills:
            char.data.predictionSkillLocked = True

    def _sendSkillUseAttempt(self, char, skillInfo, worldPosition, target):
        if skillInfo.target & TargetType.COORDINATES:
            self._applyPrediction(char, skillInfo)
            self._skillUsingCoordinates(skillInfo, worldPosition)
        elif skillInfo.target & TargetType.MOUSE:
            self._applyPrediction(char, skillInfo)
            self._skillUsingCoordinates(skillInfo, worldPosition)
        elif skillInfo.target & TargetType.DIRECTION:
            self._applyPrediction(char, skillInfo)
            self._skillInDirection(skillInfo, worldPosition)
        elif skillInfo.target & TargetType.CHAR:
            if target:
                self._applyPrediction(char, skillInfo)
                self._skillUsingPlayer(skillInfo, target.getId(), target.getIdRange())
        elif skillInfo.target & TargetType.AREA:
            self._applyPrediction(char, skillInfo)
            self._skillUsingCoordinates(skillInfo, worldPosition)
        elif skillInfo.target & TargetType.SELF:
            self._applyPrediction(char, skillInfo)
            self._skillUsingPlayer(skillInfo, char.getId(), char.getIdRange())
        else:
            eventManager.notify("onBattleMessage", "Warning: Skill does not seem to be implemented. Check back later. Sorry!", log=False)

    def _skillInDirection(self, skillInfo, worldPosition):
        char = sessionService.getSelectedChar()
        direction = getAngleBetweenTwoPoints(char.getProjection2D(), worldPosition)
        self.sendSkillRequest(skillInfo, char, "H", int(direction))

    def _skillUsingCoordinates(self, skillInfo, worldPosition):
        (self.sendSkillRequest)(skillInfo, sessionService.getSelectedChar(), "HH", *list(map(int, worldPosition)))

    def _skillUsingPlayer(self, skillInfo, charId, charType):
        self.sendSkillRequest(skillInfo, sessionService.getSelectedChar(), "HB", charId, charType)

    def sendSkillRequest(self, skillInfo, char, fmt, *args):
        packer = RawPacker()
        (packer.pack)("!BHBH" + fmt, cmsg.UseSkill, char.getId(), char.getIdRange(), skillInfo.id, *args)
        packetManager.sendRaw(packer.packet)


skillRequest = SkillRequest()
