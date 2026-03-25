# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: shared\container\constants.py
import random
from enum import Enum, auto, IntFlag, IntEnum
INTERACT_RANGE = 70
RELEASE_TIME = 1
MRANGEX = 5
MRANGEY = 4
VERSION = "0.1.15"
ESCAPE_TIMEOUT = 15
MAX_GROUP_SIZE = 5
MAX_SKILL_SIZE = 6
FRIEND_MAX = 20
IGNORE_MAX = 20
MAX_BOX_STORAGE = 20
MAX_STORAGE_BOXES = 20
MAX_LEVEL = 100
CHAT_MESSAGE_WIDTH = 150
MAX_SERVER_CHANNEL = 255
MAX_PLAYER_CHANNEL = 10
MAX_GUILD_SIZE = 50
MAX_RANKS = 8
MIN_RANKS = 3

class BattleUpdateType:
    BATTLE_CREATE = 0
    BATTLE_START = 1
    BATTLE_END = 2
    BATTLE_END_LOSS = 3
    BATTLE_END_AREA = 4
    BATTLE_WON = 5


class BattleCharUpdate:
    ADD = 0
    DEL = 1


class PointDataType(object):
    LINEAR = "linear"
    LINEAR_SMALL_TREMBLING = "linear_small_random"
    LINEAR_LONG = "linear_long"
    TREMBLING = "trembling"
    LEAVE_IN_AIR = "leave_in_air"
    SMALL_BUBBLE = "small_bubble"
    BUBBLE_MOVE = "random_bubble_move_1"
    SWIPE = "swipe"


class FileType:
    DOCUMENT = 0
    IMAGE = 1
    TEXT = 2
    MUSIC = 3


class MapSettings:
    SQUARE = 128.0
    RANGEX = 3
    RANGEY = 2


class PokemonMode(IntEnum):
    NONE = 0
    STATUS_EFFECT_IMMUNE = auto()
    STUN_IMMUNE = auto()
    KNOCKBACK_IMMUNE = auto()
    PHYSICAL_MOVE_IMMUNE = auto()
    STATUS_MOVE_IMMUNE = auto()
    ELEMENTAL_MOVE_IMMUNE = auto()


class MapSystemFlag:
    NONE = 0
    NOTRADE = 1
    NOBATTLE = 2
    NORELEASE = 4
    NOSKILL = 8
    NOWEATHER = 16
    NOPOKEMON = 32
    NODUEL = 64
    INDOOR = 26
    SAFARI = NOTRADE | NORELEASE


class TradeType:
    ITEM = 0
    POKEMON = 1


class ChatFlag:
    SYSTEM = 1
    USER = 1


class TrainerGear(IntFlag):
    NONE = 0
    SWIM = auto()
    AXE = auto()
    BIKE = auto()
    DIG = auto()
    MINE = auto()
    DIVE = auto()
    FLASHLIGHT = auto()
    POKEDEX_1 = auto()
    POKEDEX_2 = auto()
    POKEDEX_3 = auto()


class TrainerClass(IntEnum):
    NONE = 0
    TRAINER = auto()
    COLLECTOR = auto()
    RESEARCHER = auto()
    BREEDER = auto()
    RANGER = auto()


class TargetType:
    NONE = 0
    SELF = 1
    POKEMON = 2
    HUMAN = 4
    OBJECT = 8
    CHAR = POKEMON | HUMAN | OBJECT
    COORDINATES = 16
    DIRECTION = 32
    AREA = 64
    RANDOM = 128
    MOUSE = 256
    VARIED_DURATION = 512
    ALLIES = 2048
    NOTARGETS = NONE
    toInt = {
     'NONE': NONE, 
     'SELF': SELF, 
     'POKEMON': POKEMON, 
     'HUMAN': HUMAN, 
     'OBJECT': OBJECT, 
     'CHAR': CHAR, 
     'COORDINATES': COORDINATES, 
     'DIRECTION': DIRECTION, 
     'AREA': AREA, 
     'RANDOM': RANDOM, 
     'TARGET': CHAR, 
     'VARIED_DURATION': VARIED_DURATION}
    toStruct = {NONE: "H", 
     POKEMON: "HB", 
     COORDINATES: "HH", 
     AREA: "HH", 
     DIRECTION: "H", 
     CHAR: "HB", 
     SELF: "HB", 
     VARIED_DURATION: "B"}


class Capture:
    FAILED = 0
    REFUSED = 1
    CAPTURED = 2


class Anchor:
    TOP = 1
    LEFT = 2
    RIGHT = 3
    CENTER = 4


class Color:
    RED = 1
    GREEN = 2
    BLUE = 3
    YELLOW = 4
    PINK = 5
    PURPLE = 6


class PokemonColor:
    NORMAL = 0
    SHINY = 1
    toString = {SHINY: "shiny", NORMAL: "normal"}


class Gender:
    MALE = 0
    FEMALE = 1
    NOGENDER = 2
    toString = {MALE: "m", FEMALE: "f", NOGENDER: "m"}
    toInt = {'m':MALE,  'f':FEMALE,  'n':NOGENDER}


class Appearance:
    ACCESSORY = 0
    CLOTHES = 1


class Element:
    UNKNOWN = 0
    GRASS = 1
    WATER = 2
    FIRE = 3
    ELECTRIC = 4
    STEEL = 15
    ROCK = 12
    PSYCHIC = 6
    FIGHTING = 7
    GROUND = 8
    POISON = 9
    BUG = 10
    FLYING = 5
    NORMAL = 17
    ICE = 11
    GHOST = 13
    DRAGON = 14
    DARK = 16
    toInt = {
     '???': UNKNOWN, 
     'GRASS': GRASS, 
     'WATER': WATER, 
     'FIRE': FIRE, 
     'ELECTRIC': ELECTRIC, 
     'STEEL': STEEL, 
     'ROCK': ROCK, 
     'PSYCHIC': PSYCHIC, 
     'FIGHTING': FIGHTING, 
     'GROUND': GROUND, 
     'POISON': POISON, 
     'BUG': BUG, 
     'FLYING': FLYING, 
     'NORMAL': NORMAL, 
     'ICE': ICE, 
     'GHOST': GHOST, 
     'DRAGON': DRAGON, 
     'DARK': DARK, 
     'QMARKS': UNKNOWN, 
     'NONE': UNKNOWN}
    toStr = {UNKNOWN: "???", 
     GRASS: "GRASS", 
     WATER: "WATER", 
     FIRE: "FIRE", 
     ELECTRIC: "ELECTRIC", 
     STEEL: "STEEL", 
     ROCK: "ROCK", 
     PSYCHIC: "PSYCHIC", 
     FIGHTING: "FIGHTING", 
     GROUND: "GROUND", 
     POISON: "POISON", 
     BUG: "BUG", 
     FLYING: "FLYING", 
     NORMAL: "NORMAL", 
     ICE: "ICE", 
     GHOST: "GHOST", 
     DRAGON: "DRAGON", 
     DARK: "DARK"}
    ALL = (
     UNKNOWN, GRASS, WATER, FIRE, ELECTRIC, STEEL, ROCK, PSYCHIC, FIGHTING, GROUND, POISON, BUG, FLYING, NORMAL, ICE,
     GHOST, DRAGON, DARK)


class PlayerAction:
    STOP = 0
    IDLE = 1
    WALK = 2
    THROW = 3
    STOP_SWIM = 4
    SWIMMING = 5
    IDLE_BIKE = 6
    BIKING = 7
    NPC_TRAINER_ACTIONS = (
     STOP, WALK)
    toStr = {STOP: "STOP", 
     IDLE: "IDLE", 
     WALK: "WALK", 
     THROW: "THROW", 
     STOP_SWIM: "IDLE SWIM", 
     SWIMMING: "SWIMMING", 
     IDLE_BIKE: "IDLE BIKE", 
     BIKING: "BIKING"}
    ALL = (
     IDLE, WALK, THROW, STOP_SWIM, SWIMMING)


class CreatureAction:
    SPATK = 7
    DEAD = 3
    STOP = 0
    IDLE = 1
    WALK = 2
    SLEEP = 3
    HURT = 4
    ATK = 5
    CHARGE = 6
    SHOOT = 7
    STRIKE = 8
    CHOP = 9
    SCRATCH = 10
    PUNCH = 11
    SLAP = 12
    SLICE = 13
    MULTI_SCRATCH = 14
    MULTI_STRIKE = 15
    UPPERCUT = 16
    RICOCHET = 17
    BITE = 18
    SHAKE = 19
    JAB = 20
    KICK = 21
    LICK = 22
    SLAM = 23
    STOMP = 24
    APPEAL = 25
    DANCE = 26
    TWIRL = 27
    TAILWHIP = 28
    SING = 29
    SOUND = 30
    RUMBLE = 31
    FLAP_AROUND = 32
    GAS = 33
    SHOCK = 34
    EMIT = 35
    SPECIAL = 36
    WITHDRAW = 37
    REAR_UP = 38
    SWELL = 39
    SWING = 40
    DOUBLE = 41
    ROTATE = 42
    SPIN = 43
    JUMP = 44
    HIGH_JUMP = 45
    FLY = JUMP
    IDLE_WAITING = 55
    IDLE_FLYING = 56
    toRenderAction = {DEAD: SLEEP, IDLE_WAITING: IDLE, FLY: ATK, IDLE_FLYING: FLY}
    toString = {IDLE_WAITING: "idle_waiting", IDLE_FLYING: "idle_flying", IDLE: "idle", WALK: "walk", ATK: "atk", 
     SPATK: "atkspec", SLEEP: "sleep", FLY: "vol", HURT: "hurt", DEAD: "dead"}
    toInt = {'idle': IDLE, 'walk': WALK, 'atk': ATK, 'atkspec': SPATK, 'sleep': SLEEP, 'vol': FLY, 
     'hurt': HURT, 
     'dead': DEAD, 'attack': ATK, 'shooting': SPATK, 'charging': CHARGE}
    ALL_ACTIONS = (
     IDLE, WALK, ATK, SPATK, SLEEP, FLY, HURT, DEAD)
    NORMAL_POKEMON_ACTIONS = (
     IDLE, WALK, ATK, SPATK, HURT, FLY)
    NEW_ACTIONS = ('idle', 'walk', 'sleep', 'attack', 'attack_special', 'flying', 'hurt')


alwaysFlying = (12, 15, 22, 41, 42, 49, 92)
canFly = (16, 17, 18, 21)

class DamageNotificationTags:
    NONE = 0
    EFFECTIVE = 1
    RESIST = 2
    CRITICAL = 4
    MISS = 8
    IMMUNE = 16


class BodyTypes(Enum):
    DEFAULT = 1
    KID = 2
    OLD = 3


class Emotes(Enum):
    ANGRY_MARK = "mad2"
    AWAKING = "awak"
    BIG_SMILE = "HE"
    CROSS = "wr"
    CURIOUS = "o.o"
    DEAD = "dead"
    DISAGREE = "no"
    DOWN = "down"
    EMBARASSED = "embarassed"
    EPIC = "epic"
    FIRE = "fire"
    GOOD = "good"
    HAPPY = "hap"
    KARP = "karp"
    KIP = "kip"
    LOVE = "lov"
    MAD = "mad"
    MIAW = "=3"
    MUSIC = "zic"
    NOTICE = "!"
    PIKA = "pika"
    POKER_FACE = "._."
    QUESTION_MARK = "q"
    SAD = "sad1"
    SEA = "sea"
    SHINE = "shi"
    SHY = "shy"
    SICK = "sick"
    SLEEP = "sleep"
    SUPRISED = "oh"
    SWT = "swt"
    UP = "up"
    VERY_ANGRY = "grr"
    VERY_SAD = "sad"
    VERY_SHY = "shy2"
    VOMIT = "sick2"
    WAITING = "..."
    WOW = "wow"
    WTF = "wtf"
    ZZZ = "z"
    FOREVER = "4eva"
    CHEW = "chew"
    BEG = "beg"
    GAH = "gah"
    EYEROLL = "iroll"
    KISS = "kis"
    LAUGH = "lol"
    LOVE2 = "lov_"
    MAD2 = "mad2"
    SWEAT2 = "swt_"
    ZZZZ = "zzz_"
    HE = "he"


Emotes.ALL = list(Emotes)
Emotes.COUNT = len(Emotes.ALL)

class CursorMode:
    DEFAULT = "DEFAULT"
    POINTER = "POINTER"
    DRAGBEGIN = "DRAGBEGIN"
    DRAGGING = "DRAGGING"
    TARGET = "TARGET"
    TEXT = "TEXT"
    CIRCLE = "CIRCLE"
    PLAYER_CIRCLE = "PLAYER_CIRCLE"
    TARGET_LIST = (
     TARGET, PLAYER_CIRCLE, CIRCLE)
    NO_TEXTURE = (CIRCLE, PLAYER_CIRCLE)


class StatusEffect:
    NONE = 0
    BURN = 1
    FREEZE = 2
    PARALYSIS = 4
    POISON = 8
    SLEEP = 16
    CONFUSED = 32
    SILENCE = 64
    ROOT = 128
    STUN = 256
    ALL = (
     NONE, BURN, FREEZE, PARALYSIS, POISON, SLEEP, CONFUSED, SILENCE, ROOT, STUN)
    toInt = {
     'None': NONE, 
     'BURN': BURN, 
     'FREEZE': FREEZE, 
     'PARALYSIS': PARALYSIS, 
     'PARA': PARALYSIS, 
     'PARALYZE': PARALYSIS, 
     'POISON': POISON, 
     'SLEEP': SLEEP, 
     'CONFUSED': CONFUSED, 
     'CONFUSION': CONFUSED, 
     'SILENCE': SILENCE, 
     'ROOT': ROOT, 
     'STUN': STUN}
    MOVEMENT_RESTRICT = (
     FREEZE, SLEEP, ROOT, STUN)


class Badges(IntFlag):
    NONE = 0
    ROCK = auto()
    GRASS = auto()
    WATER = auto()
    FIRE = auto()
    ELECTRIC = auto()
    STEEL = auto()
    PSYCHIC = auto()
    FIGHTING = auto()
    GROUND = auto()
    POISON = auto()
    BUG = auto()
    FLYING = auto()
    NORMAL = auto()
    ICE = auto()
    GHOST = auto()
    DRAGON = auto()
    DARK = auto()


class TrainerInfoType(Enum):
    BADGES = auto()
    GEAR = auto()


class ConditionTypes:
    NONE = 0
    QUEST_COMPLETE = 1
    QUEST_INCOMPLETE = 2
    ITEM_COUNT = 3
    POKEMON_COUNT = 4
    BADGE_COUNT = 5
    GENDER = 6
    MONEY = 7
    VARIABLE = 8
    QUEST_STATE = 9
    SCRIPT = 10
    BODY_TYPE = 11


class OptionChoice:
    CLOSE = 0
    DIALOG = 1
    QUEST = 2
    SHOP = 3
    STORAGE = 4
    MAILBOX = 5
    FULLHEAL = 6
    INSTANCE = 7


class NpcFlag:
    NONE = 0
    DIALOG = 1
    QUESTGIVER = 2
    SHOP = 4
    STORAGE = 8
    MAILBOX = 16
    BATTLE = 32
    CONTAINER = 64
    HEALER = 128


class PokemonFlag(IntFlag):
    NONE = 0
    NOTRADE = auto()
    NOSTORE = auto()
    NORELEASE = auto()
    NOXP = auto()
    NOEVOLVE = auto()
    NOLEARN = auto()
    NOHOLD = auto()
    NOBREED = auto()
    TEMPORARY = NOTRADE | NOSTORE | NOXP | NOEVOLVE | NOLEARN | NOHOLD


class ControlType:
    PC = 1
    NPC = 2
    NONE = 0


class CharCategory:
    POKEMON = 1
    TRN = 2
    OBJECT = 3
    ITEM = 4
    NONE = 0


class MoneyMessage(IntEnum):
    NONE = 0
    STANDARD = 1
    FLEE_PENALTY = 2
    ALL_FAINT = 3
    PLAYER_BET = 4
    SHOP = 5
    TRADE = 6


class IdRange:
    PC_TRAINER = 0
    PC_POKEMON = 1
    NPC_CHARACTER = 2
    NPC_OBJECT = 12
    NPC_ITEM = 4
    NPC_BERRY = 5
    NPC_BATTLE_PKMN = 11
    NPC_WILD_PKMN = 6
    WARP = 7
    NONE = 10
    ALIVE_TYPES = (
     PC_TRAINER, PC_POKEMON, NPC_CHARACTER, NPC_WILD_PKMN, NPC_BATTLE_PKMN)
    NPC = (NPC_CHARACTER, NPC_WILD_PKMN, NPC_BATTLE_PKMN)
    ALL_NPC_TYPES = (NPC_CHARACTER, NPC_OBJECT, NPC_ITEM, NPC_BATTLE_PKMN, NPC_WILD_PKMN, NPC_BERRY)
    OBJECTS = (NPC_OBJECT,)
    ASSOC_TRAINER = {PC_POKEMON: PC_TRAINER, NPC_BATTLE_PKMN: NPC_CHARACTER}
    POKEMON = (
     PC_POKEMON, NPC_BATTLE_PKMN, NPC_WILD_PKMN)
    ALL_PC_TYPES = (PC_TRAINER, PC_POKEMON)
    ALL_TYPES = (PC_TRAINER, PC_POKEMON, NPC_CHARACTER, NPC_WILD_PKMN, NPC_OBJECT, NPC_ITEM, NPC_BATTLE_PKMN, WARP, NPC_BERRY)
    toStr = {PC_TRAINER: "PC TRAINER", 
     PC_POKEMON: "PC POKEMON", 
     NPC_CHARACTER: "NPC CHARACTER", 
     NPC_OBJECT: "NPC OBJECT", 
     NPC_BATTLE_PKMN: "BATTLE POKEMON", 
     NPC_WILD_PKMN: "WILD POKEMON"}


class BattleType:
    WILD = 0
    NPC = 1
    PVP = 2
    PARTY = 3
    GYM = 4
    LEGENDARY = 5
    BOSS = 6
    SAFARI = 7
    EVENT = 8
    NPC_TRAINER_BATTLE = (
     GYM, NPC)


class ObjectFlags:
    NONE = 0
    COLLISION = 1
    DESTRUCTABLE_CUT = 2
    DESTRUCTABLE_SMASH = 4
    NO_INTERACT = 8
    PERMANENT = 16
    NO_SHADOW = 32


class DataType:
    ITEMS = 100
    GUILD = 101
    PARTY = 102
    MAIL = 103
    TIMING = 104
    EGG = 105
    INCUBATOR = 106


class GroundType:
    NOTHING = 1
    HIGH_GRASS = 2
    LOW_GRASS = 4
    SHALLOW_WATER = 8
    DEEP_WATER = 16
    LAVA = 32
    DOWN_ONLY = 64
    LEFT_ONLY = 128
    RIGHT_ONLY = 256
    SAND = 512
    MUD = 1024
    SNOW = 2048
    ICE = 4096
    BRIDGE = 8192
    ALL_WATER = SHALLOW_WATER | DEEP_WATER
    ALL_GRASS = HIGH_GRASS | LOW_GRASS
    ALL_DIRECTIONS = DOWN_ONLY | LEFT_ONLY | RIGHT_ONLY
    NOTHING_DEFAULT = (
     NOTHING,)
    WATER = (
     DEEP_WATER, SHALLOW_WATER)
    GRASS = (LOW_GRASS, HIGH_GRASS)
    JUMP = (DOWN_ONLY, LEFT_ONLY, RIGHT_ONLY)
    textToInt = {'NONE':NOTHING, 
     'HIGH_GRASS':HIGH_GRASS, 
     'LOW_GRASS':LOW_GRASS, 
     'SHALLOW_WATER':SHALLOW_WATER, 
     'DEEP_WATER':DEEP_WATER, 
     'WATER':DEEP_WATER | SHALLOW_WATER, 
     'GRASS':LOW_GRASS | HIGH_GRASS, 
     'ICE':ICE, 
     'MUD':MUD, 
     'SNOW':SNOW, 
     'BRIDGE':BRIDGE, 
     'SAND':SAND, 
     'LAVA':LAVA}
    GROUND_WALKABLE = NOTHING | LOW_GRASS | HIGH_GRASS | BRIDGE
    NPC_WALKABLE = GROUND_WALKABLE | SHALLOW_WATER | DEEP_WATER | ALL_DIRECTIONS


class ChatMessageType:
    AREA = 0
    CHANNEL = 1
    WHISPER = 2
    PARTY = 3
    GUILD = 4
    ANNOUNCE = 5
    BATTLE = 10
    GLOBAL = 6
    SYSTEM = 11
    DISPLAYED = (AREA, PARTY)
    CLIENT = (
     AREA, CHANNEL, WHISPER, PARTY, GUILD, BATTLE, SYSTEM)
    ALL_PLAYER_TYPE = (
     AREA, CHANNEL, WHISPER, PARTY, GUILD)


class StatType:
    HP = 1
    ATK = 2
    SPATK = 3
    DEF = 4
    SPDEF = 5
    SPEED = 6
    EXP = 7
    ENERGY = 8
    STAMINA = 8
    CRIT_CHANCE = 9
    EVASION = 10
    ACCURACY = 11
    MOVEMENT_SPEED = 12
    ENERGY_COST = 13
    PHYSICAL_DAMAGE = 14
    ELEMENTAL_DAMAGE = 15
    MIN = 0
    MAX = 1
    BOTH = 2
    ALL_STATS = (
     HP, ATK, SPATK, DEF, SPDEF, SPEED, EXP, ENERGY, CRIT_CHANCE, EVASION, ACCURACY)
    toString = {HP: "hp", ATK: "atk", SPATK: "spatk", DEF: "defense", SPDEF: "spdef", SPEED: "speed", EXP: "exp", 
     ENERGY: "energy", CRIT_CHANCE: "critical", EVASION: "evasion", ACCURACY: "accuracy"}
    toBuffType = {}
    toInt = {
     'ATK': ATK, 
     'ATTACK': ATK, 
     'HP': HP, 
     'SPATK': SPATK, 
     'SPECIAL_ATTACK': SPATK, 
     'DEF': DEF, 
     'DEFENCE': DEF, 
     'DEFENSE': DEF, 
     'SPDEF': SPDEF, 
     'SPECIAL_DEFENCE': SPDEF, 
     'SPECIAL_DEFENSE': SPDEF, 
     'SPEED': SPEED, 
     'ENERGY': ENERGY, 
     'CRIT_CHANCE': CRIT_CHANCE, 
     'CRIT': CRIT_CHANCE, 
     'EVASION': EVASION, 
     'ACCURACY': ACCURACY}


class BuffTypes:
    __doc__ = "To be used for the Skill Database."
    HP = 1
    ATK = 2
    SPATK = 4
    DEF = 8
    SPDEF = 16
    SPEED = 32
    ENERGY = 64
    CRIT_CHANCE = 128
    EVASION = 256
    ACCURACY = 512
    ALL_BUFFS = [
     HP, ATK, SPATK, DEF, SPDEF, SPEED, ENERGY, CRIT_CHANCE, EVASION, 
     ACCURACY]
    toInt = {
     'ATK': ATK, 
     'ATTACK': ATK, 
     'HP': HP, 
     'SPATK': SPATK, 
     'SPECIAL_ATTACK': SPATK, 
     'DEF': DEF, 
     'DEFENCE': DEF, 
     'DEFENSE': DEF, 
     'SPDEF': SPDEF, 
     'SPECIAL_DEFENCE': SPDEF, 
     'SPECIAL_DEFENSE': SPDEF, 
     'SPEED': SPEED, 
     'ENERGY': ENERGY, 
     'CRIT_CHANCE': CRIT_CHANCE, 
     'CRIT': CRIT_CHANCE, 
     'EVASION': EVASION, 
     'ACCURACY': ACCURACY}
    toStatType = {HP: (StatType.HP), 
     ATK: (StatType.ATK), 
     SPATK: (StatType.SPATK), 
     DEF: (StatType.DEF), 
     SPDEF: (StatType.SPDEF), 
     SPEED: (StatType.SPEED), 
     ENERGY: (StatType.ENERGY), 
     CRIT_CHANCE: (StatType.CRIT_CHANCE), 
     EVASION: (StatType.EVASION), 
     ACCURACY: (StatType.ACCURACY)}


StatType.toBuffType = {(StatType.HP): (BuffTypes.HP), 
 (StatType.ATK): (BuffTypes.ATK), 
 (StatType.SPATK): (BuffTypes.SPATK), 
 (StatType.DEF): (BuffTypes.DEF), 
 (StatType.SPDEF): (BuffTypes.SPDEF), 
 (StatType.SPEED): (BuffTypes.SPEED), 
 (StatType.ENERGY): (BuffTypes.ENERGY), 
 (StatType.CRIT_CHANCE): (BuffTypes.CRIT_CHANCE), 
 (StatType.EVASION): (BuffTypes.EVASION), 
 (StatType.ACCURACY): (BuffTypes.ACCURACY)}

class QuestStatus:
    NONE = 0
    COMPLETE = 1
    UNAVAILABLE = 2
    INCOMPLETE = 3
    AVAILABLE = 4
    FAILED = 5
    REWARDED = 6


class QuestQuery:
    DETAILS = 1
    REQUIREMENTS = 2
    REWARD = 3


class QuestReward:
    MONEY = 1
    ITEM = 2
    ITEMCHOICE = 3
    POKEMON = 4
    XP = 5
    SKILL = 6
    SCRIPT = 7
    MULTIPLE_POKEMON = 8
    EXCHANGE_POKEMON = 9


class QuestObjectives:
    MONEY = 1
    ITEM = 2
    WILDDEFEAT = 3
    WILDCAPTURE = 4
    TRAINERDEFEAT = 5
    NPCTALK = 6
    NPC_BATTLE_DEFEAT = 7
    CAPTURE_POKEMON = 8
    LOOT_DEFEAT = 9
    LOOT_CAPTURE = 10
    POKEDEX_SEEN_GLOBAL = 11
    POKEDEX_CAUGHT_GLOBAL = 12
    PVP_BATTLE = 19
    EVOLVE = 20
    CAPTURE_TYPE = 21
    POKEDEX_SEEN_POKEMON = 13
    POKEDEX_CAUGHT_POKEMON = 14
    POKEDEX_SEEN_TYPE = 15


class GroupUpdates:
    LEAVE = 1
    KICKED = 2
    DISBAND = 3
    ONLINE = 4
    OFFLINE = 5
    LEADER = 6


class NameLength:
    TRAINER = 12
    POKEMON = 20
    MAP = 12
    Npc = 18
    CHANNELS = 8
    GUILD = 16
    GUILD_RANK = 14
    OBJECT = 18


class ChallengeState:
    SENT = 0
    ACCEPTED = 1
    CANCELED = 2
    FORFEIT = 3
    INBATTLE = 4
    OFFLINE = 5
    LOSE = 6
    WIN = 7
    RANGE = 8
    BUSY = 9


class ItemType:
    ITEMS = 0
    MEDICINE = 1
    POKEBALL = 2
    TM = 3
    BERRY = 4
    MAIL = 5
    BATTLE = 6
    KEY = 7
    QUEST = 7
    SOMETHING = 8
    intToStr = {ITEMS: "ITEMS", 
     MEDICINE: "MEDICINE", 
     POKEBALL: "POKEBALL", 
     TM: "TM", 
     BERRY: "BERRY", 
     MAIL: "MAIL", 
     BATTLE: "BATTLE", 
     KEY: "KEY", 
     QUEST: "QUEST", 
     SOMETHING: "OTHER"}
    strToInt = {
     'ITEMS': ITEMS, 
     'MEDICINE': MEDICINE, 
     'POKEBALL': POKEBALL, 
     'TM': TM, 
     'BERRY': BERRY, 
     'MAIL': MAIL, 
     'BATTLE': BATTLE, 
     'KEY': KEY, 
     'QUEST': QUEST, 
     'OTHER': SOMETHING}


class Pokeball:
    MASTERBALL = 264
    ULTRABALL = 265
    GREATBALL = 266
    POKEBALL = 267
    SAFARIBALL = 268
    SPORTBALL = 269
    NETBALL = 270
    DIVEBALL = 271
    NESTBALL = 272
    REPEATBALL = 273
    TIMERBALL = 274
    LUXURYBALL = 275
    PREMIERBALL = 276
    DUSKBALL = 277
    HEALBALL = 278
    QUICKBALL = 279
    CHERISHBALL = 280
    FASTBALL = 281
    LEVELBALL = 282
    LUREBALL = 283
    HEAVYBALL = 284
    LOVEBALL = 285
    FRIENDBALL = 286
    MOONBALL = 287
    PARKBALL = 288
    CRYSTALBALL = 1001
    DREAMBALL = 290
    CLONEBALL = 1002
    BEASTBALL = 1000
    STONEBALL = 1003
    ETERNALBALL = 1004
    toItemId = {
     1: POKEBALL, 
     2: GREATBALL, 
     3: ULTRABALL, 
     4: SAFARIBALL, 
     5: MASTERBALL, 
     6: NESTBALL, 
     7: NETBALL, 
     8: DIVEBALL, 
     9: REPEATBALL, 
     10: TIMERBALL, 
     11: PREMIERBALL, 
     12: LUXURYBALL, 
     13: PARKBALL, 
     14: MOONBALL, 
     15: HEALBALL, 
     16: DUSKBALL, 
     17: CRYSTALBALL, 
     18: QUICKBALL, 
     19: CHERISHBALL, 
     20: HEAVYBALL, 
     21: DREAMBALL, 
     22: FRIENDBALL, 
     23: LEVELBALL, 
     24: CLONEBALL, 
     25: LOVEBALL, 
     26: LUREBALL, 
     27: BEASTBALL, 
     28: STONEBALL, 
     29: ETERNALBALL}
    toBackgroundId = {POKEBALL: 1, 
     MOONBALL: 2, 
     LUXURYBALL: 3, 
     HEALBALL: 4, 
     DUSKBALL: 5, 
     REPEATBALL: 6, 
     ULTRABALL: 7, 
     QUICKBALL: 8, 
     DIVEBALL: 9, 
     CHERISHBALL: 10, 
     PREMIERBALL: 11, 
     HEAVYBALL: 12, 
     PARKBALL: 13, 
     NETBALL: 14, 
     GREATBALL: 15, 
     MASTERBALL: 16, 
     CRYSTALBALL: 17, 
     TIMERBALL: 18, 
     SAFARIBALL: 19, 
     NESTBALL: 20, 
     DREAMBALL: 21, 
     FRIENDBALL: 22, 
     LEVELBALL: 23, 
     CLONEBALL: 24, 
     LOVEBALL: 25, 
     LUREBALL: 26, 
     BEASTBALL: 27, 
     STONEBALL: 28}
    toGraphicId = {POKEBALL: 1, 
     GREATBALL: 2, 
     ULTRABALL: 3, 
     SAFARIBALL: 4, 
     MASTERBALL: 5, 
     NESTBALL: 6, 
     NETBALL: 7, 
     DIVEBALL: 8, 
     REPEATBALL: 9, 
     TIMERBALL: 10, 
     PREMIERBALL: 11, 
     LUXURYBALL: 12, 
     PARKBALL: 13, 
     MOONBALL: 14, 
     HEALBALL: 15, 
     DUSKBALL: 16, 
     CRYSTALBALL: 17, 
     QUICKBALL: 18, 
     CHERISHBALL: 19, 
     HEAVYBALL: 20, 
     DREAMBALL: 21, 
     FRIENDBALL: 22, 
     LEVELBALL: 23, 
     CLONEBALL: 24, 
     LOVEBALL: 25, 
     LUREBALL: 26, 
     BEASTBALL: 27, 
     STONEBALL: 28, 
     ETERNALBALL: 29}


class ItemFlag:
    NONE = 0
    NOSELL = 1
    NOTRADE = 2
    NODESTROY = 4
    NOSTORE = 8
    QUEST = 11


class ItemUsage:
    NONE = 0
    USABLE_ONCE = 1
    REUSABLE = 2


class Direction:
    degrees = (0, 45, 90, 135, 180, 225, 270, 315)
    integer = (1, 2, 3, 4, 5, 6, 7, 8)
    toDeg = {1: 0, 2: 45, 3: 90, 4: 135, 5: 180, 6: 225, 7: 270, 8: 315}
    toInt = {0: 1, 45: 2, 90: 3, 135: 4, 180: 5, 225: 6, 270: 7, 315: 8}

    def convertToInt(self, degree):
        return self.integer[self.degrees.index(degree)]

    def convertToDeg(self, integer):
        return self.degrees[self.integer.index(integer)]


class SkillCategory:
    PHYSICAL = 0
    SPECIAL = 1
    STATUS = 2
    toInt = {'Physical':PHYSICAL,  'Special':SPECIAL, 
     'Status':STATUS}


class GroupResponses:
    REQUEST_SENT = 0
    REQUEST_ACCEPTED = 1
    REQUEST_DENIED = 2
    ALREADY_IN_PARTY = 3
    NOT_ONLINE = 4
    NO_REQUESTS = 5
    FULL = 6


class PMSettings:
    NONE = 0
    FRIENDS = 1
    ALL = 2


class FriendResponses:
    REQUEST_SENT = 0
    REQUEST_ACCEPTED = 1
    REQUEST_DENIED = 2
    NOT_ONLINE = 3
    FRIEND_ALREADY = 4
    IGNORE_ALREADY = 5
    IGNORE_FULL = 6
    OUR_IGNORE_FULL = 7
    OUR_FRIEND_FULL = 8
    TARGET_FRIEND_FULL = 9
    FRIEND_BUSY = 10
    CANNOT_ADD = 11
    IGNORE_SUCCESS = 12
    IGNORE_REMOVED = 13
    FRIEND_REMOVED = 14
    NOT_IN_LIST = 15


class TradeResponses:
    SENT = 0
    REJECTED = 1
    ACCEPTED = 2
    INTRADE = 3
    NORECALLED = 4
    OFFLINE = 5
    RANGE = 6
    BUSY = 7


class TradeFinishing:
    LOCK = 0
    CONFIRM = 1
    CANCEL = 2
    COMPLETED = 3
    CANCEL_POKEMON_SPACE = 4


class ChallengeResponses:
    SENT = 0
    ACCEPTED = 1
    CANCELED = 2
    FORFEIT = 3
    INBATTLE = 4
    OFFLINE = 5
    LOSE = 6
    WIN = 7
    RANGE = 8
    BUSY = 9
    INVALID_CONDITION = 10
    PARTY_MEMBER_RANGE_FAIL = 11
    PARTY_OPPONENTS_RANGE_FAIL = 12
    PARTY_MEMBER_DECLINED = 13
    PARTY_OPPONENTS_DECLINED = 14
    PARTY_MEMBER_MATCH = 15
    PARTY_OPPONENTS_MATCH = 16
    PARTY_MEMBER_BUSY = 17
    PARTY_OPPONENTS_BUSY = 18
    PARTY_OPPONENTS_NO_GROUP = 19
    PARTY_SAME_PARTY = 20
    PARTY_TIMEOUT = 21
    DUEL_TIMEOUT = 22
    PARTY_WIN = 23
    PARTY_LOSS = 24
    PARTY_REMOVED = 25


class GuildResponses:
    REQUEST_SENT = 0
    REQUEST_ACCEPTED = 1
    REQUEST_DENIED = 2
    ALREADY_IN_GUILD = 3
    NOT_ONLINE = 4
    NO_REQUESTS = 5
    GUILD_FULL = 6
    GUILD_CANNOTLEAVE = 7
    RANK_LOW = 8
    RANK_HIGH = 9


class GuildEvent:
    JOINED = 0
    LEFT = 1
    REMOVED = 2
    PROMOTED = 3
    DEMOTED = 4
    OFFLINE = 5
    ONLINE = 6
    LEADERCHANGE = 7
    DISBAND = 8


class WildPkmnFlag(IntFlag):
    NONE = 0
    NOCATCH = auto()
    EVENT = auto()
    INVULNERABLE = auto()
    NO_EXP = auto()
    NO_DROPS = auto()
    SAFARI = auto()
    ELITE = auto()
    AGGROS = auto()
    MULTIPLAYER = auto()
    SUB_ELITE = auto()
    BOSS = ELITE | NOCATCH | AGGROS | MULTIPLAYER
    QUEST = NOCATCH | NO_EXP | SUB_ELITE


class EggGroups(Enum):
    NONE = 0
    MONSTER = auto()
    WATER1 = auto()
    BUG = auto()
    FLYING = auto()
    FIELD = auto()
    FAIRY = auto()
    GRASS = auto()
    HUMANLIKE = auto()
    WATER3 = auto()
    MINERAL = auto()
    AMORPHOUS = auto()
    WATER2 = auto()
    DITTO = auto()
    DRAGON = auto()
    UNDISCOVERED = auto()


class TimerTypes(Enum):
    QUEST = auto()
    SAFARI = auto()
    REPEL = auto()


class GuildPermissions:
    LISTEN = 1
    TALK = 2
    INVITE = 4
    PROMOTE = 8
    DEMOTE = 16
    KICK = 32
    SETMOTD = 64
    ALL = 127


class FriendFlag:
    FRIEND = 1
    IGNORED = 2


class PlayerStatus:
    OFFLINE = 0
    ONLINE = 1
    AFK = 2
    DND = 3
    HIDDEN = 4
    MAPCHANGE = 5
    statusText = {OFFLINE: "Offline", 
     ONLINE: "Online", 
     AFK: "Away", 
     DND: "DND"}


class DefaultRanks:
    GUILDMASTER = 0
    OFFICER = 1
    VETERAN = 2
    MEMBER = 3
    INITIATE = 4
    names = {GUILDMASTER: "Guildmaster", OFFICER: "Officer", VETERAN: "Veteran", MEMBER: "Member", INITIATE: "Initiate"}
    rights = {GUILDMASTER: (GuildPermissions.ALL), OFFICER: (GuildPermissions.ALL), VETERAN: 7, MEMBER: 3, 
     INITIATE: 3}


class EvolutionType:
    LEVEL = 0
    HAPPINESS = 1
    HAPPINESS_DAY = 2
    HAPPINESS_NIGHT = 3
    LEVEL_FEMALE = 4
    LEVEL_MALE = 5
    BEAUTY = 6
    ATK_GREATER = 7
    DEF_GREATER = 8
    ATK_DEF_EQUAL = 9
    ITEM = 10
    TRADEITEM = 11
    TRADE = 12
    HASMOVE = 13
    DAYHOLDITEM = 14
    SILCOON = 15
    CASCOON = 16
    HASINPARTY = 17
    SHEDINJA = 18
    NINJASK = 19
    toInt = {
     'Level': LEVEL, 
     'Trade': TRADE, 
     'TradeItem': TRADEITEM, 
     'Happiness': HAPPINESS, 
     'HappinessDay': HAPPINESS_DAY, 
     'HappinessNight': HAPPINESS_NIGHT, 
     'LevelMale': LEVEL_MALE, 
     'LevelFemale': LEVEL_FEMALE, 
     'Beauty': BEAUTY, 
     'AttackGreater': ATK_GREATER, 
     'DefenseGreater': DEF_GREATER, 
     'AtkDefEqual': ATK_DEF_EQUAL, 
     'Cascoon': CASCOON, 
     'DayHoldItem': DAYHOLDITEM, 
     'HasInParty': HASINPARTY, 
     'HasMove': HASMOVE, 
     'Item': ITEM, 
     'Ninjask': NINJASK, 
     'Shedinja': SHEDINJA, 
     'Silcoon': SILCOON}
    ITEM_EVOLUTION = (
     ITEM, DAYHOLDITEM, TRADEITEM)


class ConsoleColor:
    GREEN = "\x1b[01;32m"
    RED = "\x1b[01;31m"


class DisappearType:
    IMMEDIATE = 0
    FADE_OUT = 1
    EXPLOSION = 2
    DESTROY_FADE = 3


class AreaStackType:
    UNSTACKABLE = 0
    STACKABLE = 1


class WalkMode:
    FOLLOW = 1
    FREE = 2


class DamageType:
    DEFAULT = 0


class Abilities:
    STENCH = 1
    DRIZZLE = 2
    SPEEDBOOST = 3
    BATTLEARMOR = 4
    STURDY = 5
    DAMP = 6
    LIMBER = 7
    SANDVEIL = 8
    STATIC = 9
    VOLTABSORB = 10
    WATERABSORB = 11
    OBLIVIOUS = 12
    CLOUDNINE = 13
    COMPOUNDEYES = 14
    INSOMNIA = 15
    COLORCHANGE = 16
    IMMUNITY = 17
    FLASHFIRE = 18
    SHIELDDUST = 19
    OWNTEMPO = 20
    SUCTIONCUPS = 21
    INTIMIDATE = 22
    SHADOWTAG = 23
    ROUGHSKIN = 24
    WONDERGUARD = 25
    LEVITATE = 26
    EFFECTSPORE = 27
    SYNCHRONIZE = 28
    CLEARBODY = 29
    NATURALCURE = 30
    LIGHTNINGROD = 31
    SERENEGRACE = 32
    SWIFTSWIM = 33
    CHLOROPHYLL = 34
    ILLUMINATE = 35
    TRACE = 36
    HUGEPOWER = 37
    POISONPOINT = 38
    INNERFOCUS = 39
    MAGMAARMOR = 40
    WATERVEIL = 41
    MAGNETPULL = 42
    SOUNDPROOF = 43
    RAINDISH = 44
    SANDSTREAM = 45
    PRESSURE = 46
    THICKFAT = 47
    EARLYBIRD = 48
    FLAMEBODY = 49
    RUNAWAY = 50
    KEENEYE = 51
    HYPERCUTTER = 52
    PICKUP = 53
    TRUANT = 54
    HUSTLE = 55
    CUTECHARM = 56
    PLUS = 57
    MINUS = 58
    FORECAST = 59
    STICKYHOLD = 60
    SHEDSKIN = 61
    GUTS = 62
    MARVELSCALE = 63
    LIQUIDOOZE = 64
    OVERGROW = 65
    BLAZE = 66
    TORRENT = 67
    SWARM = 68
    ROCKHEAD = 69
    DROUGHT = 70
    ARENATRAP = 71
    VITALSPIRIT = 72
    WHITESMOKE = 73
    PUREPOWER = 74
    SHELLARMOR = 75
    AIRLOCK = 76
    TANGLEDFEET = 77
    MOTORDRIVE = 78
    RIVALRY = 79
    STEADFAST = 80
    SNOWCLOAK = 81
    GLUTTONY = 82
    ANGERPOINT = 83
    UNBURDEN = 84
    HEATPROOF = 85
    SIMPLE = 86
    DRYSKIN = 87
    DOWNLOAD = 88
    IRONFIST = 89
    POISONHEAL = 90
    ADAPTABILITY = 91
    SKILLLINK = 92
    HYDRATION = 93
    SOLARPOWER = 94
    QUICKFEET = 95
    NORMALIZE = 96
    SNIPER = 97
    MAGICGUARD = 98
    NOGUARD = 99
    STALL = 100
    TECHNICIAN = 101
    LEAFGUARD = 102
    KLUTZ = 103
    MOLDBREAKER = 104
    SUPERLUCK = 105
    AFTERMATH = 106
    ANTICIPATION = 107
    FOREWARN = 108
    UNAWARE = 109
    TINTEDLENS = 110
    FILTER = 111
    SLOWSTART = 112
    SCRAPPY = 113
    STORMDRAIN = 114
    ICEBODY = 115
    SOLIDROCK = 116
    SNOWWARNING = 117
    HONEYGATHER = 118
    FRISK = 119
    RECKLESS = 120
    MULTITYPE = 121
    FLOWERGIFT = 122
    BADDREAMS = 123


class FaintType:
    LEAVE = 0
    KO = 1
    REFUSE = 2
    AFRAID = 3
    BLOWN_AWAY = 4
    WILD_FAINTS = (
     LEAVE, REFUSE, AFRAID, KO)
    PET_FAINTS = (KO, REFUSE, AFRAID)
    MOVING_FAINTS = (BLOWN_AWAY, LEAVE)

    @staticmethod
    def getRandomWild():
        i = random.randint(0, 100)
        if i < 7:
            return FaintType.REFUSE
        if i < 14:
            return FaintType.AFRAID
        if i < 21:
            return FaintType.KO
        if i <= 100:
            return FaintType.LEAVE

    @staticmethod
    def getRandomPet():
        return random.choice(FaintType.PET_FAINTS)


class LoginResponses:
    BAD_PASSWORD = 0
    BAD_ACCOUNT = 1
    AUTHORIZATION_FAIL = 2
    ACCOUNT_EXISTS = 3
    OUTDATED = 4
    SERVER_FULL = 5
    IPBANNED = 6
    ALREADY_LOGGED_IN = 7
    NO_TRAINERS = 8
    LOGIN_OK = 9
    ACCOUNT_CREATED_IPLIMIT = 13
    ACCOUNT_CREATED = 14
    NO_SERVERS = 15
    QUEUE = 16
    ACCOUNT_CREATION_CLOSED = 17
    MAINTENENCE = 18
    BANNED = 19
    CREATION_OK = 10
    CREATION_NAME_EXISTS = 11
    CREATION_NAME_LENGTH = 12


class JobClass:
    NOVICE = 0
    TRAINER = 1
    BREEDER = 2
    PROFESSOR = 3


class WeatherFlag:
    NONE = 0
    RAIN = 1
    THUNDERSTORM = 2
    SNOW = 3
    CLOUDY = 4
    FOG = 5
    LIGHT_WIND = 6
    HEAVY_WIND = 7
    BREEZE = 8
    SUNNY = 9
    ALL = (
     NONE, RAIN, THUNDERSTORM, SNOW, CLOUDY, FOG, HEAVY_WIND, LIGHT_WIND, BREEZE, SUNNY)


class SpawnWeathers(Enum):
    RAIN = (
     WeatherFlag.RAIN, WeatherFlag.THUNDERSTORM)
    CLOUDY = (WeatherFlag.CLOUDY,)
    SNOW = (WeatherFlag.SNOW,)
    WIND = (WeatherFlag.LIGHT_WIND, WeatherFlag.HEAVY_WIND, WeatherFlag.BREEZE)
    FOG = (WeatherFlag.FOG,)
    SUNNY = (WeatherFlag.SUNNY,)
    NONE = (WeatherFlag.NONE,)
    ALL = NONE + WIND + SUNNY + RAIN + CLOUDY + SNOW + FOG


class DialogEnding:
    CLOSE = 0
    NEXT = 1
    BATTLE = 2
    TIMED_CLOSE = 3
    TIMED_CONTINUE = 4


class RefPointType:
    BOTTOM = 1
    TOP = 2
    LEFT = 4
    RIGHT = 8
    CENTERX = 16
    CENTERY = 32
    TOPLEFT = 6
    TOPRIGHT = 10
    BOTTOMLEFT = 5
    BOTTOMRIGHT = 9
    BOTTOMCENTER = 17
    TOPCENTER = 18
    LEFTCENTER = 36
    RIGHTCENTER = 40
    CENTER = 48


class Messages(Enum):
    LOGIN_INCORRECT = auto()
    LOGIN_CONNECTION_FAIL = auto()
    LOGIN_AUTHFAIL = auto()
    LOGIN_LOGGED_IN = auto()
    LOGIN_FULL = auto()
    LOGIN_PERM_BAN = auto()
    LOGIN_TEMP_BAN = auto()
    LOGIN_OLD = auto()
    CREATION_ACCOUNT_EXISTS = auto()
    CREATION_SUCCESS = auto()
    CREATION_LIMIT = auto()
    LOGIN_INVALID = auto()
    LOGIN_NO_SERVER = auto()
    CREATION_CLOSED = auto()
    LOGIN_MAINTENENCE = auto()
    LOGIN_UNKNOWN = auto()
    CONNECT = auto()
    QUIT = auto()
    OK = auto()
    CANCEL = auto()
    CLOSE = auto()
    NO = auto()
    YES = auto()
    QUIT_GAME_CHECK = auto()
    USER_LENGTH = auto()
    PASSWORD_SHORT = auto()
    USER_SHORT = auto()
    CHAR_LENGTH = auto()
    CHAR_ILLEGAL = auto()
    CREATION_CHOICE = auto()
    CREATION_TRAINER_EXISTS = auto()
    PLAYER_OFFLINE = auto()
    TRADE_ACCEPTED = auto()
    TRADE_DENIED = auto()
    TRADE_CANCEL = auto()
    TRADE_SUCCESS = auto()
    TRADE_REQUEST = auto()
    ACCEPT = auto()
    DENY = auto()
    CONFIRM_TRADE = auto()
    TRADE_EXISTS = auto()
    TRADE_POKEMON_DENY_T = auto()
    TRADE_POKEMON_DENY = auto()
    DISCONNECTED = auto()
    CHANNEL_JOIN = auto()
    CHANNEL_LEAVE = auto()
    CHANNEL_INVALID = auto()
    CHANNEL_PASSWORD = auto()
    CHANNEL_KICK = auto()
    CHANNEL_KICK_RESPONSE = auto()
    MUTE = auto()
    BATTLE_EXISTS = auto()
    BATTLE_TIMER = auto()
    ALREADY_RECEIVED_ITEM = auto()
