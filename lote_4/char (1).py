# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\data\world\char.py
from shared.container.constants import IdRange, CreatureAction, WalkMode, CharCategory, ControlType, Badges
from client.data.utils.color import Color
from client.data.world.object import BasicCharData
from shared.container.stat import StatData
from shared.container.constants import StatType
from shared.container.skill import SkillState, Skills
from shared.container.status import CharStatusData
import time
from twisted.internet import reactor, defer
from shared.container.player import PlayerAppearance
appearanceColors = [
 (255, 255, 255), 
 (250, 219, 160), 
 (238, 192, 83), 
 (246, 160, 59), 
 (216, 99, 53), 
 (255, 117, 177), 
 (212, 64, 64), 
 (161, 44, 44), 
 (108, 37, 37), 
 (210, 233, 101), 
 (58, 216, 103), 
 (56, 153, 77), 
 (36, 71, 43), 
 (100, 233, 213), 
 (63, 197, 241), 
 (77, 123, 241), 
 (51, 65, 100), 
 (204, 114, 246), 
 (143, 56, 184), 
 (97, 44, 122), 
 (254, 154, 232), 
 (222, 88, 180), 
 (173, 58, 137), 
 (106, 38, 84), 
 (186, 127, 91), 
 (140, 94, 66), 
 (92, 65, 49), 
 (72, 96, 96), 
 (88, 80, 96)]

class SkinTone:
    DEFAULT = 0
    SHADE_1 = 1
    SHADE_2 = 2
    SHADE_3 = 3
    SHADE_4 = 4
    SHADE_5 = 5
    SHADE_6 = 6
    SHADE_7 = 7
    SHADE_8 = 8
    SHADE_9 = 9
    SHADE_10 = 10
    SHADE_11 = 11
    SHADE_12 = 12
    SHADE_13 = 13
    SHADE_14 = 14
    SHADE_15 = 15
    SHADE_16 = 16
    SHADE_17 = 17
    SHADE_18 = 18
    SHADE_19 = 19
    SHADE_20 = 20
    rgb = [
     (255, 255, 255), 
     (240, 255, 255), 
     (255, 245, 245), 
     (237, 255, 238), 
     (222, 244, 255), 
     (239, 255, 214), 
     (220, 255, 244), 
     (225, 255, 222), 
     (231, 242, 209), 
     (215, 240, 255), 
     (205, 233, 255), 
     (215, 235, 235), 
     (209, 220, 225), 
     (214, 223, 207), 
     (219, 208, 198), 
     (201, 189, 166), 
     (201, 167, 150), 
     (191, 167, 140), 
     (191, 157, 130), 
     (181, 167, 150), 
     (155, 131, 111)]


class CharColor:
    fromType = {(IdRange.PC_POKEMON): (Color.WHITE), 
     (IdRange.PC_TRAINER): (Color.WHITE), 
     (IdRange.NPC_CHARACTER): (Color.NAME_PURPLE), 
     (IdRange.NPC_WILD_PKMN): (Color.GREY), 
     (IdRange.NPC_BATTLE_PKMN): (Color.NAME_ORANGE), 
     (IdRange.NPC_ITEM): (Color.NAME_YELLOW), 
     (IdRange.NPC_OBJECT): (Color.NAME_GREEN), 
     (IdRange.NPC_BERRY): (Color.NAME_GREEN)}


class FacingData:
    __slots__ = [
     "frames", "flip"]

    def __init__(self, frames, flip=0):
        self.frames = frames
        self.flip = flip


class TrainerGear:

    def __init__(self):
        self.received = False
        self.pokedex = 0
        self.axe = False
        self.worldMap = False
        self.swim = False
        self.dig = False
        self.bike = 0
        self.mine = 0
        self.dive = 0


class CharData(BasicCharData):
    gender = 0
    id = 0
    idRange = IdRange.NONE
    walkingSpeed = 70
    action = CreatureAction.STOP
    map = None
    originalFacing = 270
    facing = 270
    walkMode = WalkMode.FREE
    unselectedMode = WalkMode.FOLLOW

    def __init__(self):
        """ Constructors of CharData are empty. Make sure to set all attributes before passing it to a WorldObject Controller."""
        return

    def setWalkingSpeed(self, speed, modified=None):
        self.walkingSpeed = self._calculateSpeed(speed)
        if modified is not None:
            self.walkingSpeed *= max(0.2, modified / speed)

    def _calculateSpeed(self, maxSpeed):
        return int(50 + float(maxSpeed) / 255.0 * 150)

    def hasTrainer(self):
        return

    def canMove(self):
        """ Tells if the char is allowed to move or not. """
        return True

    def canAttack(self):
        return True

    def canOpenMenu(self):
        """ Tells if the menu can be opened for the char or not. """
        return True

    def canBeSelected(self):
        return True

    def getMap(self, map):
        return self.map

    def setMap(self, map):
        self.map = map

    def isPCPokemon(self) -> bool:
        return bool(self.idRange == IdRange.PC_POKEMON)

    def isNPC(self) -> bool:
        return bool(self.idRange in IdRange.NPC)

    def isPCTrainer(self) -> bool:
        return bool(self.idRange == IdRange.PC_TRAINER)

    def isPC(self) -> bool:
        return bool(self.idRange in IdRange.ALL_PC_TYPES)

    def isNpcPokemon(self) -> bool:
        return bool(self.idRange == IdRange.NPC_BATTLE_PKMN)

    def isWildPokemon(self) -> bool:
        return bool(self.idRange == IdRange.NPC_WILD_PKMN)

    def isWorldObject(self) -> bool:
        return self.idRange == IdRange.NPC_OBJECT

    def isPokemon(self):
        return False


class PokemonData(CharData):
    __doc__ = " Data container of a pokemon "
    idRange = IdRange.PC_POKEMON
    trainerId = 0
    dexId = 0
    name = "Pokemon"
    lineupId = 0
    happiness = 0
    gender = 0
    state = 0
    level = 1
    ballId = 1
    abilityId = 0
    nature = 0
    heldNameId = 0
    exp = 0
    released = 0
    shiny = 0
    distanceFromTrainer = 20
    angleFromTrainer = 0
    code = 0
    frontVer = 0
    status = 0
    createdTime = 0
    createdMapId = 0
    createdLevel = 0
    expThisLevel = 0
    subspecies = 0
    walkMode = WalkMode.FOLLOW
    category = CharCategory.POKEMON
    predictionMovementLocked = False
    predictionSkillLocked = False
    evolving = False

    def __init__(self):
        self.skills = Skills()
        self.stats = StatData()
        self.status = CharStatusData()
        self.skillStates = SkillState()
        self.damageStates = SkillState()
        self.controlType = ControlType.PC
        self._preventAction = False
        self._stunned = False
        self._canMoveCallback = None

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"

    def setStunDuration(self, duration, func=None):
        self._stunned = True
        if self._preventAction:
            self._preventAction.cancel()
        self._preventAction = reactor.callLater(duration, self.stopStun, func)

    def stopStun(self, func):
        self._preventAction = False
        self._stunned = False
        self.verifyMovable()
        if func:
            func()

    def isStunned(self):
        return self._stunned

    def isCasting(self):
        return False

    def isReleased(self):
        return self.released

    def setReleased(self, value):
        if self.released == value:
            if value == True:
                raise Exception("The pokemon is already released.")
        self.released = value

    def getCallbackWhenMovable(self):
        self._canMoveCallback = defer.Deferred()
        return self._canMoveCallback

    def verifyMovable(self):
        if self._canMoveCallback:
            if self.canMove():
                self._canMoveCallback.callback("BLAH")
                self._canMoveCallback = None

    def canMove(self):
        if self.evolving:
            return False
        else:
            if self.isFainted():
                return False
            else:
                if self.predictionMovementLocked:
                    return False
                if self.status.isSleeping() or self.status.isFrozen() or self.status.isRooted():
                    return False
                if self.isStunned():
                    return False
            for skillList in self.skillStates.getAllSkills():
                for instance in skillList:
                    if not instance.skillInfo.allow_movement:
                        return False

            return True

    def canAttack(self):
        if self.evolving:
            return False
        else:
            if self.isFainted():
                return False
            else:
                if self.predictionSkillLocked:
                    return False
                if self.status.isSleeping() or self.status.isFrozen():
                    return False
                for skillList in self.skillStates.getAllSkills():
                    for instance in skillList:
                        if not instance.skillInfo.allow_skills:
                            return False

                if self.isStunned():
                    return False
            return True

    def canOpenMenu(self):
        if self.evolving:
            return False
        else:
            return True

    def canBeSelected(self):
        if self.evolving:
            return False
        else:
            if self.isFainted():
                return False
            return True

    def isFainted(self):
        if self.stats.hp.current < 1:
            return True
        else:
            return False

    def hasTrainer(self):
        return self.trainerId

    def getTrainerId(self):
        return self.trainerId

    def getFileId(self):
        return self.dexId

    def isPokemon(self):
        return True


class PlayerTrainerAchievements:

    def __init__(self):
        self.pvpWins = 0
        self.pvpLosses = 0
        self.job = 0
        self.pokedexCaught = 0
        self.pokedexSeen = 0
        self.startTimeStamp = 0


class PlayerTrainerSkills:

    def __init__(self):
        self.swimming = False


class NpcTrainerData(CharData):
    fileId = "f28"
    facing = 270
    area = None
    name = "Character"
    idRange = IdRange.NPC_CHARACTER
    category = CharCategory.TRN
    flags = 0
    vendor = None
    controlType = ControlType.NPC


class PcTrainerData(CharData):
    __doc__ = " Data container of a trainer "
    partyId = 0
    teamId = 0
    guildName = ""
    saveX = 0
    saveY = 0
    saveMap = ""
    idRange = IdRange.PC_TRAINER
    name = "Unknown"
    category = CharCategory.TRN
    controlType = ControlType.PC
    badges = Badges.NONE

    def __init__(self):
        super().__init__()
        self.appearance = PlayerAppearance(0, 0, 1, 1, 0, 0, 0, 0, 0)
        self.stats = PlayerTrainerAchievements()
        self.skills = PlayerTrainerSkills()


class NpcPokemonData(PokemonData):

    def __init__(self):
        PokemonData.__init__(self)
        self.idRange = IdRange.NPC_CHARACTER
        self.category = CharCategory.POKEMON
        self.controlType = ControlType.NPC

    def isFainted(self):
        """ NPC Pokemon cannot be fainted, they are just NPCS """
        return False


class NpcWorldItemData(NpcTrainerData):

    def __init__(self):
        NpcTrainerData.__init__(self)
        self.fileId = "0"
        self.idRange = IdRange.NPC_ITEM
        self.category = CharCategory.ITEM
        self.controlType = ControlType.NPC


class NpcWorldObjectData(NpcTrainerData):

    def __init__(self):
        NpcTrainerData.__init__(self)
        self.fileId = "0"
        self.idRange = IdRange.NPC_OBJECT
        self.category = CharCategory.OBJECT
        self.controlType = ControlType.NPC
        self.renderingOrder = 0
        self.shadow = True


class WildPokemonData(PokemonData):
    facing = 270
    x = 0
    y = 0
    z = 0
    speed = 70
    area = None
    name = "Pokemon"
    idRange = IdRange.NPC_WILD_PKMN
    category = CharCategory.POKEMON
    walkMode = WalkMode.FREE
    controlType = ControlType.NPC
    released = True

    def __init__(self):
        PokemonData.__init__(self)
        self.tagged = False
        self.idRange = IdRange.NPC_WILD_PKMN
        self.category = CharCategory.POKEMON
        self.controlType = ControlType.NPC


class NpcBattlePokemonData(PokemonData):
    idRange = IdRange.NPC_BATTLE_PKMN
    controlType = ControlType.NPC
