# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\net\world\parse\trade.py
from client.data.container.char import charContainer
from shared.container.constants import IdRange
from client.data.world.item import ItemData
from shared.service.utils import nullstrip
from client.data.world.char import PokemonData
from client.data.DB import skillDB
from shared.container.skill import PokemonSkill
from client.interface.trade import trade
from client.interface.bag import bag

def TradeRequest(data):
    _, trainerId, tradeType = data
    trainerData = charContainer.getDataById(trainerId, IdRange.PC_TRAINER)
    trade.onTradeRequest(trainerData.name, tradeType)


def TradeResponse(data):
    _, response, trainerId, tradeType = data
    trade.onTradeResponse(trainerId, tradeType, response)


def TradeItem(data):
    _, trainerId, task, nameId, quantity = data
    x = ItemData(nameId)
    x.quantity = quantity
    if task == 0:
        trade.onTradeItemAdd(trainerId, x)
        bag.onTradeItemAdd(trainerId, x)
    else:
        trade.onTradeItemDelete(trainerId, x)
        bag.onTradeItemDelete(trainerId, x)


def TradeMoney(data):
    _, money = data
    trade.onTradeMoney(money)


def TradeFinish(data):
    _, response = data
    trade.onTradeFinish(response)
    bag.onTradeFinish(response)


def TradePkmnAdd(data):
    _, trainerId, pkmnId, dexId, name, gender, level, cur_hp, max_hp, max_atk, max_def, max_atkSpec, max_defSpec, max_speed, nature, abilityId, skill1, skill2, skill3, skill4, skill5, skill6, ballId, shiny, itemId, frontVer, ot, subspecies, createdTime, createdMapId, createdLevel, currentExp, maxExp, currentEnergy, maxEnergy = data
    name = nullstrip(name)
    ot = nullstrip(ot)
    d = PokemonData()
    d.id = pkmnId
    d.dexId = dexId
    d.name = name
    d.ot = ot
    d.gender = gender
    d.level = level
    d.nature = nature
    d.abilityId = abilityId
    d.trainer_id = trainerId
    d.ballId = ballId
    d.shiny = shiny
    d.heldNameId = itemId
    d.frontVer = frontVer
    d.subspecies = subspecies
    d.createdTime = createdTime
    d.createdMapId = createdMapId
    d.createdLevel = createdLevel
    s = d.stats
    s.atk.set(max_atk, max_atk)
    s.spatk.set(max_atkSpec, max_atkSpec)
    s.defense.set(max_def, max_def)
    s.spdef.set(max_defSpec, max_defSpec)
    s.speed.set(max_speed, max_speed)
    s.hp.set(cur_hp, max_hp)
    s.exp.set(currentExp, maxExp)
    s.energy.set(currentEnergy, maxEnergy)
    skills = [
     skill1, skill2, skill3, skill4, skill5, skill6]
    for skillId in skills:
        if skillId > 0:
            skillData = PokemonSkill(skillDB.getSkill(skillId))
            d.skills.addSkill(skillData)

    trade.onTradePokemonAdd(trainerId, d)


def TradePkmnDel(data):
    _, trainerId, pkmnId = data
    trade.onTradePokemonDelete(trainerId, pkmnId)
