# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: shared\controller\net\packetStruct.py
from shared.container.constants import NameLength
from shared.container.net import lmsg, cmsg, smsg
import struct

def addLength(packet):
    """Adds a header that includes length to the front of the packet"""
    if len(packet) >= 255:
        return bytes((255, )) + struct.pack("!H", len(packet)) + packet
    else:
        return bytes((len(packet),)) + packet


def packBoolInfos(b8=0, b7=0, b6=0, b5=0, b4=0, b3=0, b2=0, b1=0):
    return 1 * b1 + 2 * b2 + 4 * b3 + 8 * b4 + 16 * b5 + 32 * b6 + 64 * b7 + 128 * b8


def unpackBoolInfos(i):
    return tuple((0, 1)[i >> j & 1] for j in range(7, -1, -1))


class RawPacker:
    __slots__ = [
     "data"]

    def __init__(self):
        self.data = b''

    def pack(self, fmt, *args):
        self.data = (b'').join((self.data, (struct.pack)(fmt, *args)))

    def packString(self, string, fmt='!B'):
        encoded = string.encode("utf-8")
        self.data = (b'').join((self.data, struct.pack(fmt + "%ds" % len(encoded), len(encoded), encoded)))

    def packData(self, data, fmt='!H'):
        self.data = (b'').join((self.data, struct.pack(fmt + "%ds" % len(data), len(data), data)))

    @property
    def packet(self):
        return self.data


class RawUnpacker:
    __slots__ = [
     "data"]

    def __init__(self, data):
        self.data = data

    def get(self, fmt):
        size = struct.calcsize(fmt)
        unpacked = struct.unpack(fmt, self.data[:size])
        if len(unpacked) == 1:
            unpacked = unpacked[0]
        self.data = self.data[size:]
        return unpacked

    def getString(self, fmt='!B'):
        size = struct.calcsize(fmt)
        length = struct.unpack(fmt, self.data[:size])
        message = self.data[size:length[0] + size]
        self.data = self.data[size + length[0]:]
        return message.decode("utf-8")

    def getData(self, fmt='!H'):
        size = struct.calcsize(fmt)
        length = struct.unpack(fmt, self.data[:size])
        message = self.data[size:length[0] + size]
        self.data = self.data[size + length[0]:]
        return message


class Structs:

    def __init__(self):
        self.login = {(lmsg.PlayerConnect): (struct.Struct("!B")), 
         (lmsg.Key): (struct.Struct("!B36s")), 
         (lmsg.PlayerLogin): (struct.Struct("!B9s32s64s")), 
         (lmsg.CreateAccount): (struct.Struct("!B9s32s64s")), 
         (lmsg.Response): (struct.Struct("!BB")), 
         (lmsg.ServerInfo): (struct.Struct("!B15sH")), 
         (lmsg.Ban): (struct.Struct("!Bd")), 
         (lmsg.CreateTrainer): (struct.Struct("!B12sBBBBBB")), 
         (lmsg.QueueInfo): (struct.Struct("!BHH"))}
        self.client = {(cmsg.Jump): (struct.Struct("!BIB")), 
         (cmsg.PosAndDir): (struct.Struct("!BBIBddBd")), 
         (cmsg.StopAndDir): (struct.Struct("!BBIBddBd")), 
         (cmsg.MakeFollow): (struct.Struct("!BIBIB")), 
         (cmsg.StopFollow): (struct.Struct("!BIB")), 
         (cmsg.Stuck): (struct.Struct("!B")), 
         (cmsg.NewPokemon): (struct.Struct("!BI%ds" % NameLength.POKEMON)), 
         (cmsg.PokemonRelease): (struct.Struct("!BIHHB")), 
         (cmsg.PokemonReturn): (struct.Struct("!BI")), 
         (cmsg.PokemonLineup): (struct.Struct("!BBB")), 
         (cmsg.PokemonDelete): (struct.Struct("!BII")), 
         (cmsg.PokemonSelection): (struct.Struct("!BH")), 
         (cmsg.ItemThrow): (struct.Struct("!BHHH")), 
         (cmsg.ItemUse): (struct.Struct("!BIBH")), 
         (cmsg.TrainerCard): (struct.Struct("!BH")), 
         (cmsg.ItemDelete): (struct.Struct("!BHHB")), 
         (cmsg.ItemEquip): (struct.Struct("!BIH")), 
         (cmsg.ItemUnequip): (struct.Struct("!BI")), 
         (cmsg.PrivateMessage): (struct.Struct("!B%ds" % NameLength.TRAINER)), 
         (cmsg.JoinChat): (struct.Struct("!B%ds" % NameLength.CHANNELS)), 
         (cmsg.ChatMessage): (struct.Struct("!BB%ds" % NameLength.TRAINER)), 
         (cmsg.LeaveChat): (struct.Struct("!B%ds" % NameLength.CHANNELS)), 
         (cmsg.Disconnect): (struct.Struct("!B")), 
         (cmsg.Ping): (struct.Struct("!B")), 
         (cmsg.OnlineCount): (struct.Struct("!B")), 
         (cmsg.QueryName): (struct.Struct("!BBIB")), 
         (cmsg.MassQueryName): (struct.Struct("!B")), 
         (cmsg.QueryDialogText): (struct.Struct("!BHBH")), 
         (cmsg.CharSelection): (struct.Struct("!BIB")), 
         (cmsg.UseAction): (struct.Struct("!BIBB")), 
         (cmsg.Emote): (struct.Struct("!BIBB")), 
         (cmsg.NpcDialogHello): (struct.Struct("!BH")), 
         (cmsg.NpcOpenShop): (struct.Struct("!BH")), 
         (cmsg.OpenStorage): (struct.Struct("!BH")), 
         (cmsg.NpcQuestHello): (struct.Struct("!BH")), 
         (cmsg.NpcClose): (struct.Struct("!B")), 
         (cmsg.NpcContinue): (struct.Struct("!B")), 
         (cmsg.NpcSell): (struct.Struct("!BHHH")), 
         (cmsg.NpcBuy): (struct.Struct("!BBHHH")), 
         (cmsg.NpcQuestStatus): (struct.Struct("!BHB")), 
         (cmsg.NpcSelectOption): (struct.Struct("!BB")), 
         (cmsg.NpcObjectInteract): (struct.Struct("!BHB")), 
         (cmsg.NpcItemInteract): (struct.Struct("!BH")), 
         (cmsg.QuestDetailsQuery): (struct.Struct("!BHBHB")), 
         (cmsg.QuestAccept): (struct.Struct("!BHBH")), 
         (cmsg.QuestAbandon): (struct.Struct("!BH")), 
         (cmsg.QuestComplete): (struct.Struct("!BHBH")), 
         (cmsg.QuestChooseReward): (struct.Struct("!BHBH")), 
         (cmsg.StorageMove): (struct.Struct("H")), 
         (cmsg.StorageGetBox): (struct.Struct("!BHB")), 
         (cmsg.StoragePkmnStore): (struct.Struct("!BHIB")), 
         (cmsg.StoragePkmnWithdraw): (struct.Struct("!BHII")), 
         (cmsg.StoragePreview): (struct.Struct("!BHI")), 
         (cmsg.PokedexScan): (struct.Struct("!BIB")), 
         (cmsg.PokedexChecksum): (struct.Struct("!BI")), 
         (cmsg.TradeRequest): (struct.Struct("!BHB")), 
         (cmsg.TradeResponse): (struct.Struct("!BB")), 
         (cmsg.TradeItem): (struct.Struct("!BBHH")), 
         (cmsg.TradeMoney): (struct.Struct("!BI")), 
         (cmsg.TradeConfirm): (struct.Struct("!BB")), 
         (cmsg.TradePokemon): (struct.Struct("!BBI")), 
         (cmsg.FriendRequest): (struct.Struct("!B%ds" % NameLength.TRAINER)), 
         (cmsg.FriendDelete): (struct.Struct("!BH")), 
         (cmsg.FriendResponse): (struct.Struct("!BB")), 
         (cmsg.FriendIgnoreAdd): (struct.Struct("!B%ds" % NameLength.TRAINER)), 
         (cmsg.FriendIgnoreDel): (struct.Struct("!BH")), 
         (cmsg.PlayerStatus): (struct.Struct("!BB")), 
         (cmsg.GroupInvite): (struct.Struct("!B%ds" % NameLength.TRAINER)), 
         (cmsg.GroupResponse): (struct.Struct("!BB")), 
         (cmsg.GroupList): (struct.Struct("B12sB")), 
         (cmsg.GroupInfo): (struct.Struct("!BBB")), 
         (cmsg.GroupUpdate): (struct.Struct("!BIB")), 
         (cmsg.GuildCreate): (struct.Struct("!B%ds" % NameLength.GUILD)), 
         (cmsg.GuildInvite): (struct.Struct("!B%ds" % NameLength.TRAINER)), 
         (cmsg.GuildResponse): (struct.Struct("!BB")), 
         (cmsg.GuildUpdate): (struct.Struct("!BHB")), 
         (cmsg.GuildMotd): (struct.Struct("!B")), 
         (cmsg.GuildCreateRank): (struct.Struct("!B%dsB" % NameLength.GUILD_RANK)), 
         (cmsg.GuildRankRename): (struct.Struct("!BB%ds" % NameLength.GUILD_RANK)), 
         (cmsg.GuildRankPermissions): (struct.Struct("!BBB")), 
         (cmsg.GuildSwapRank): (struct.Struct("!BBB")), 
         (cmsg.GuildDeleteRank): (struct.Struct("!BB")), 
         (cmsg.UseSkill): (struct.Struct("!BIH")), 
         (cmsg.SwapSkill): (struct.Struct("!BIHH")), 
         (cmsg.SkillUpdatePosition): (struct.Struct("!BHBHBHH")), 
         (cmsg.DuelChallenge): (struct.Struct("!BHBBBBIB")), 
         (cmsg.DuelResponse): (struct.Struct("!BH")), 
         (cmsg.AppearanceChange): (struct.Struct("BBBBBBB")), 
         (cmsg.DaycareUpdate): (struct.Struct("!BBIB"))}
        self.server = {(smsg.CharWarp): (struct.Struct("!BHBHB")), 
         (smsg.ClientCharWarp): (struct.Struct("!BHBHHH")), 
         (smsg.WarpPoint): (struct.Struct("!BHHHHHB")), 
         (smsg.Ping): (struct.Struct("!B")), 
         (smsg.StopFollow): (struct.Struct("!BHBHH")), 
         (smsg.MakeFollow): (struct.Struct("!BHBHB")), 
         (smsg.PosAndDir): (struct.Struct("!BBIBddB")), 
         (smsg.Jump): (struct.Struct("!BHB")), 
         (smsg.GotoPosition): (struct.Struct("!BHBHHH")), 
         (smsg.StopGotoPosition): (struct.Struct("!BHBHHH")), 
         (smsg.Fly): (struct.Struct("!BHBB")), 
         (smsg.Direction): (struct.Struct("!BHBB")), 
         (smsg.SpeedChange): (struct.Struct("!BHBHB")), 
         (smsg.TrainerCreation): (struct.Struct("!BI%dsBBBBBBBBBBIHHHHBHHB" % NameLength.TRAINER)), 
         (smsg.TrainerClient): (struct.Struct("!BI%dsBBBBBBBBBIIHHddHHHB" % NameLength.TRAINER)), 
         (smsg.WildPokemonCreation): (struct.Struct("!BBI%dsHBBBHHHHHHHBHH" % NameLength.POKEMON)), 
         (smsg.PokemonCreation): (struct.Struct("!BHB%dsHBBBHHHBbbbHHbBBHHH" % NameLength.POKEMON)), 
         (smsg.PokemonFullData): (struct.Struct(f"!BIH{NameLength.POKEMON}sBBHHHHHHHHBHHBHBB{NameLength.TRAINER}sBdBBBIIBB")), 
         (smsg.TrainerInfoUpdate): (struct.Struct("!BIBI")), 
         (smsg.PokemonRelease): (struct.Struct("!BIHBHH")), 
         (smsg.NpcPokemonRelease): (struct.Struct("!BHHBHH")), 
         (smsg.PokemonReturn): (struct.Struct("!BIB")), 
         (smsg.NewPokemon): (struct.Struct("!BIHB")), 
         (smsg.PokemonDelete): (struct.Struct("!BI")), 
         (smsg.PokemonLineup): (struct.Struct("!BBB")), 
         (smsg.PokemonCaptureResult): (struct.Struct("!BHIHHBBB")), 
         (smsg.PokemonSelection): (struct.Struct("!BHHHHHH")), 
         (smsg.PokedexList): (struct.Struct("!B")), 
         (smsg.PokedexUpdate): (struct.Struct("!BHB")), 
         (smsg.PokedexChecksum): (struct.Struct("!B")), 
         (smsg.SendBag): (struct.Struct("!B")), 
         (smsg.TrainerCard): (struct.Struct("!BI")), 
         (smsg.TrainerAchievements): (struct.Struct("!BHHHHHBd")), 
         (smsg.ItemThrow): (struct.Struct("!BHBHHHH")), 
         (smsg.ItemUse): (struct.Struct("!BIBHB")), 
         (smsg.ItemDelete): (struct.Struct("!BHH")), 
         (smsg.ItemAdd): (struct.Struct("!BHHBHB")), 
         (smsg.ItemEquip): (struct.Struct("!BIH")), 
         (smsg.ItemUnequip): (struct.Struct("!BI")), 
         (smsg.Money): (struct.Struct("!BiB")), 
         (smsg.ItemObject): (struct.Struct("!BHHBHHBB")), 
         (smsg.NpcCreation): (struct.Struct("!BHBB%ds4sBBHHHBBBB" % NameLength.Npc)), 
         (smsg.NpcMessage): (struct.Struct("!B")), 
         (smsg.NpcClose): (struct.Struct("!B")), 
         (smsg.NpcDialogMessage): (struct.Struct("!B")), 
         (smsg.NpcOpenShop): (struct.Struct("HH")), 
         (smsg.NpcRemove): (struct.Struct("!BHB")), 
         (smsg.NpcObject): (struct.Struct("!BHB%ds%dsBHHHBBb" % (NameLength.Npc, NameLength.OBJECT))), 
         (smsg.Disappear): (struct.Struct("!BHBB")), 
         (smsg.NpcQuestStatus): (struct.Struct("!BHBB")), 
         (smsg.NpcQuestHello): (struct.Struct("!BHH")), 
         (smsg.QuestQueryDetails): (struct.Struct("!B")), 
         (smsg.QuestAccept): (struct.Struct("!BH")), 
         (smsg.QuestResponse): (struct.Struct("!BHB")), 
         (smsg.QuestAbandon): (struct.Struct("!BH")), 
         (smsg.QuestFail): (struct.Struct("!BH")), 
         (smsg.QuestComplete): (struct.Struct("!BH")), 
         (smsg.QuestRequireUpdate): (struct.Struct("!BHBI")), 
         (smsg.QuestList): (struct.Struct("!B")), 
         (smsg.QuestNpcList): (struct.Struct("!B")), 
         (smsg.QuestState): (struct.Struct("!BHB")), 
         (smsg.ReBattleTime): (struct.Struct("!BHBdB")), 
         (smsg.UseAction): (struct.Struct("!BIBBB")), 
         (smsg.Emote): (struct.Struct("!BHBB")), 
         (smsg.CharSelection): (struct.Struct("!BHB")), 
         (smsg.OnlineCount): (struct.Struct("!BH")), 
         (smsg.Disconnect): (struct.Struct("!BH")), 
         (smsg.QueryNameResponse): (struct.Struct(f"!BHB{NameLength.TRAINER}s")), 
         (smsg.MassQueryNameResponse): (struct.Struct("!B")), 
         (smsg.ServerInfo): (struct.Struct("!BB")), 
         (smsg.InstanceTransition): (struct.Struct("!BHH")), 
         (smsg.MapStatus): (struct.Struct("!BBBB")), 
         (smsg.TradeRequestTo): (struct.Struct("!BHB")), 
         (smsg.TradeResponse): (struct.Struct("!BBHB")), 
         (smsg.TradeItem): (struct.Struct("!BHBHH")), 
         (smsg.TradePokemonDel): (struct.Struct("!BHH")), 
         (smsg.TradePokemonAdd): (struct.Struct(f"!BHHH{NameLength.POKEMON}sBHHHHHHHHBHHHHHHHHBHB{NameLength.TRAINER}sBdBBIIBB")), 
         (smsg.TradeMoney): (struct.Struct("!BI")), 
         (smsg.TradeConfirm): (struct.Struct("!BB")), 
         (smsg.OpenStorage): (struct.Struct("!BH")), 
         (smsg.StorageMove): (struct.Struct("!H")), 
         (smsg.StorageSendBox): (struct.Struct(f"HHBBB{NameLength.POKEMON}sBBHB")), 
         (smsg.StoragePkmnStore): (struct.Struct("!BIB")), 
         (smsg.StoragePkmnWithdraw): (struct.Struct("!BIB")), 
         (smsg.StoragePreview): (struct.Struct("!BI")), 
         (smsg.PrivateMessage): (struct.Struct(f"!BB{NameLength.TRAINER}s")), 
         (smsg.JoinChat): (struct.Struct(f"!BB{NameLength.TRAINER}s")), 
         (smsg.ChatMessage): (struct.Struct(f"!BB{NameLength.TRAINER}sB")), 
         (smsg.ChatMessageArea): (struct.Struct("!BIB")), 
         (smsg.Announce): (struct.Struct("!B")), 
         (smsg.LeaveChat): (struct.Struct("!BB")), 
         (smsg.Message): (struct.Struct("!BB")), 
         (smsg.SpecialText): (struct.Struct("!BBBB")), 
         (smsg.FriendInvite): (struct.Struct(f"!B{NameLength.TRAINER}s")), 
         (smsg.FriendAdd): (struct.Struct(f"!BHBB{NameLength.TRAINER}s")), 
         (smsg.FriendDelete): (struct.Struct("!BH")), 
         (smsg.FriendResponse): (struct.Struct("!BB")), 
         (smsg.FriendList): (struct.Struct("!B")), 
         (smsg.FriendIgnoreAdd): (struct.Struct(f"!{NameLength.TRAINER}s")), 
         (smsg.FriendIgnoreDel): (struct.Struct("!BH")), 
         (smsg.FriendStatus): (struct.Struct("!BHB")), 
         (smsg.PlayerStatus): (struct.Struct("!BHBH")), 
         (smsg.GroupInvite): (struct.Struct(f"!B{NameLength.TRAINER}s")), 
         (smsg.GroupResponse): (struct.Struct("!BB")), 
         (smsg.GroupList): (struct.Struct("!B")), 
         (smsg.GroupOptions): (struct.Struct("!BBB")), 
         (smsg.GroupUpdate): (struct.Struct("!BHB")), 
         (smsg.GroupAddPlayer): (struct.Struct(f"!BH{NameLength.TRAINER}sBB")), 
         (smsg.GuildRoster): (struct.Struct("!B")), 
         (smsg.GuildInvite): (struct.Struct(f"!B{NameLength.TRAINER}s{NameLength.GUILD}s")), 
         (smsg.GuildResponse): (struct.Struct("!BB")), 
         (smsg.GuildAddPlayer): (struct.Struct("!B")), 
         (smsg.GuildUpdate): (struct.Struct("!BHHB")), 
         (smsg.GuildMotd): (struct.Struct("!B")), 
         (smsg.GuildCreateRank): (struct.Struct(f"!BB{NameLength.GUILD_RANK}sB")), 
         (smsg.GuildRankRename): (struct.Struct(f"!BB{NameLength.GUILD_RANK}s")), 
         (smsg.GuildRankPermissions): (struct.Struct("!BBB")), 
         (smsg.GuildSwapRank): (struct.Struct("!BBB")), 
         (smsg.GuildDeleteRank): (struct.Struct("!BB")), 
         (smsg.DuelChallenge): (struct.Struct("!BHBBBBIB")), 
         (smsg.DuelResponse): (struct.Struct("!BH")), 
         (smsg.Evolve): (struct.Struct(f"!BHBH{NameLength.POKEMON}s")), 
         (smsg.XPGain): (struct.Struct("!BHi")), 
         (smsg.LevelUp): (struct.Struct("!BHBBII")), 
         (smsg.StatUpdateAll): (struct.Struct("!BHBHHHHHH")), 
         (smsg.StatUpdateSingle): (struct.Struct("!BHBBhh")), 
         (smsg.BattleUpdate): (struct.Struct("!BBBd")), 
         (smsg.CharBattleUpdate): (struct.Struct("!BHBB")), 
         (smsg.CharDamage): (struct.Struct("!BHBHBHBBHBBd")), 
         (smsg.Damage): (struct.Struct("!BHBHBHBd")), 
         (smsg.Faint): (struct.Struct("!BHBB")), 
         (smsg.Status): (struct.Struct("!BHBHBB")), 
         (smsg.BattleInfo): (struct.Struct("!BHHH")), 
         (smsg.BattleTarget): (struct.Struct("!BIBIB")), 
         (smsg.TagStatus): (struct.Struct("!BIBB")), 
         (smsg.UseSkill): (struct.Struct("!B")), 
         (smsg.SkillAck): (struct.Struct("!BIHB")), 
         (smsg.DeleteSkill): (struct.Struct("!BIHB")), 
         (smsg.NewSkill): (struct.Struct("!BIHB")), 
         (smsg.SkillList): (struct.Struct("!B")), 
         (smsg.Buff): (struct.Struct("!BIBHBBBhHBd")), 
         (smsg.Debuff): (struct.Struct("!BIBHBBBhHBd")), 
         (smsg.DelSkillInstance): (struct.Struct("!BIBHBB")), 
         (smsg.SkillDamageSource): (struct.Struct("!BIBHBBHBHHHHHBd")), 
         (smsg.SkillPositionUpdate): (struct.Struct("!BIBHBHH")), 
         (smsg.Knockback): (struct.Struct("!BIBBddBd")), 
         (smsg.TimerStart): (struct.Struct("!BBHdH")), 
         (smsg.InputDisable): (struct.Struct("!BBH")), 
         (smsg.PlayEffect): (struct.Struct("!BBH")), 
         (smsg.PlayAnimation): (struct.Struct("!BIBBfB")), 
         (smsg.PlaySound): (struct.Struct("!BBB")), 
         (smsg.PlayBgm): (struct.Struct("!BBB")), 
         (smsg.CameraFocus): (struct.Struct("!BBH")), 
         (smsg.WeatherChange): (struct.Struct("!BBBBBBB")), 
         (smsg.AppearanceChange): (struct.Struct("!BHBBBBBBBBBB")), 
         (smsg.AppearanceList): (struct.Struct("!B")), 
         (smsg.AppearanceItemUpdate): (struct.Struct("!BBBB")), 
         (smsg.EggData): (struct.Struct("!BIHHdBBBB")), 
         (smsg.EggIncubator): (struct.Struct("!BBBIdBB")), 
         (smsg.DaycareOpen): (struct.Struct("!BBBBB")), 
         (smsg.DaycareInformation): (struct.Struct("!B")), 
         (smsg.DaycareUpdate): (struct.Struct("!BBBIdd?"))}


class DynamicListing:

    def __init__(self):
        self.login = []
        self.client = [
         cmsg.MassQueryName,
         cmsg.StorageMove,
         cmsg.GroupList,
         cmsg.GuildMotd,
         cmsg.ChatMessage,
         cmsg.UseSkill]
        self.server = [
         smsg.ChatMessage,
         smsg.ChatMessageArea,
         smsg.PokedexList,
         smsg.SendBag,
         smsg.NpcMessage,
         smsg.NpcOpenShop,
         smsg.QuestQueryDetails,
         smsg.QuestList,
         smsg.QuestNpcList,
         smsg.MassQueryNameResponse,
         smsg.NpcDialogMessage,
         smsg.StorageMove,
         smsg.StorageSendBox,
         smsg.FriendList,
         smsg.GroupList,
         smsg.GuildRoster,
         smsg.GuildAddPlayer,
         smsg.GuildMotd,
         smsg.UseSkill,
         smsg.SkillList,
         smsg.AppearanceList,
         smsg.ServerInfo,
         smsg.DaycareInformation]


dynamicList = DynamicListing()

class Packet:

    def __init__(self):
        self.structs = Structs()
        self.dynamic = []

    def create(self, name, *args):
        if name in self.funcs:
            buffer = (self.funcs[name])(self.sendStruct[name], name, *args)
        elif args[0] is not None:
            buffer = (self.sendStruct[name].pack)(name, *args)
        else:
            buffer = self.sendStruct[name].pack(name)
        return buffer

    def messageCreate(self, name, message, *args):
        packet = (self.sendStruct[name].pack)(name, *args)
        return packet + message[:120]

    def sizeCheck(self, packet_num, buffer):
        return

    def unpack(self, packetNum, data):
        structObj = self.recvStruct[packetNum]
        if packetNum in self.dynamic:
            return data
        else:
            if len(data) != structObj.size:
                return
            return structObj.unpack(data[:structObj.size])


class LoginPacket(Packet):

    def __init__(self, loginNet):
        Packet.__init__(self)
        self.loginNet = loginNet
        self.funcs = {}
        self.dynamic = dynamicList.login
        self.recvStruct = self.structs.login
        self.sendStruct = self.structs.login

    def create_data(self, data_type, *args):
        return addLength((self.create)(data_type, *args))

    def send(self, dataType, *args):
        packet = addLength((self.create)(dataType, *args))
        self.loginNet.sendData(packet)

    def sendTo(self, socket, dataType, *args):
        packet = addLength((self.create)(dataType, *args))
        self.loginNet.sendTo(socket, packet)
