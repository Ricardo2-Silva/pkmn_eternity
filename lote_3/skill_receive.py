# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\world\action\skill_receive.py
"""
Created on Jul 13, 2017

@author: Admin

This is for handling the moves that come in from the game_server.

"""
from client.data.DB import skillDB
from client.control.world.action.moves import *
from shared.container.constants import Element
from shared.container.skill import PokemonSkill, SkillInfo

class SkillController:

    def playerUseSkill(self, pokemonSkill: PokemonSkill, instanceId, char, duration, startTime, data):
        pokemonSkill.cooldownTick = startTime
        self.useSkill(pokemonSkill.skillInfo, instanceId, char, duration, startTime, data)

    def useSkill(self, skillInfo: SkillInfo, instanceId, char, duration, startTime, data):
        skillName = skillInfo.nameId.lower().title()
        char.data.stats.useEnergy(skillInfo.energy)
        char.setStunDuration(skillInfo.startup_delay)
        if skillName not in globals():
            print("SKILLNAME NOT FOUND", skillName)
            if skillInfo.isPhysical():
                skillName = "Scratch"
        elif skillInfo.isSpecial():
            print("~~~~~~~~~~~~~~~~~~~~~~~", skillInfo.element)
            if skillInfo.element == Element.FIRE:
                skillName = "Ember"
            elif skillInfo.element == Element.WATER:
                skillName = "Bubble"
            else:
                skillName = "Ember"
        else:
            skillName = "Tailwhip"
        classObject = globals()[skillName]
        existingDamage = char.damageStates.getSkillByName(skillName, instanceId)
        if existingDamage:
            existingDamage.callAgain(classObject, instanceId, skillInfo, char, data)
        else:
            classObject(skillInfo, char, data, instanceId, duration=duration)
        return True

    def damageInstanceUse(self, skillId, targetId, targetIdRange, x, y, z, direction, radius, duration, timeStamp):
        """Only for use with """
        skillInfo = skillDB.getById(skillId)
        if skillInfo:
            skillName = skillInfo.nameId.lower().title()
            classObject = globals()[skillName]
            classObject.onDamageSourceReceived(None, targetId, targetIdRange, x, y, z, direction, radius, duration, timeStamp)


skillController = SkillController()
