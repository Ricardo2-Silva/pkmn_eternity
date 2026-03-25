# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\net\world\handler.py
import queue
from twisted.internet import reactor, defer
from twisted.internet.error import ConnectionDone
from twisted.python import log
from twisted.internet.protocol import connectionDone
from twisted.protocols.basic import Int16StringReceiver
from client.control.events.event import eventManager
from shared.service.utils import getParts
import shared.controller.net.netbase as netb
from client.control.net.world.parseDB import GamePacketDB
import time
from twisted.internet.task import LoopingCall
from shared.controller.net.packetStruct import Packet, dynamicList
from shared.container.net import cmsg, lmsg
from shared.container.constants import Direction
TIMEOUT_INTERVAL = 10

def client_posanddir(struct_obj, header, obj, orderNum, dir):
    """ Movement packet sent to the game_server (Contains direction only)"""
    x, y = obj.getPosition()
    return struct_obj.pack(header, orderNum, obj.id, obj.getIdRange(), x, y, Direction.toInt[dir], time.time())


def client_stopanddir(struct_obj, header, obj, orderNum, dir):
    """ Movement packet sent to the game_server (Contains direction only)"""
    x, y = obj.getPosition()
    return struct_obj.pack(header, orderNum, obj.id, obj.getIdRange(), x, y, Direction.toInt[dir] + 10, time.time())


def client_posupdate(struct_obj, header, obj):
    """ Movement packet sent to the game_server (Contains direction only)"""
    return struct_obj.pack(header, obj.id, obj.getIdRange())


def client_chatmessage(struct_obj, header, obj):
    actid = struct_obj.pack(header, obj[0], obj[1])
    return actid + obj[2]


class ClientPacket(Packet):

    def __init__(self):
        Packet.__init__(self)
        self.funcs = {(cmsg.PosAndDir): client_posanddir, 
         (cmsg.StopAndDir): client_stopanddir, 
         (cmsg.ChatMessage): client_chatmessage}
        self.dynamic = dynamicList.server
        self.recvStruct = self.structs.server
        self.sendStruct = self.structs.client


class PacketQueueSystem:
    __doc__ = "When put in queue mode, the system will stop decoding packets and instead queue them. Once activated, it will\n    begin decoding all of the queued up packets using their respective functions.\n    This way we can ensure certain client side functions are done, before we start getting data that may or may not\n    exist.\n    "

    def __init__(self, gameNet):
        self.gameNet = gameNet
        self.queue = queue.Queue()
        self.packet_overrides = [1, 2, 3]
        self._active = False

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, value):
        self._active = value
        if value is False:
            self.replay_time()

    def replay_time(self):
        """Plays all stored packets since enabled."""
        for packet in self.queue.get():
            packetNum = packet[0]
            if packetNum in self.packet_overrides:
                data = self.gameNet.gamePacket.unpack(packetNum, packet)
                self.gameNet.parsing.func[packetNum](data)

    def add(self, decoded_packet):
        self.queue.put(decoded_packet)


class GameServerConnection(Int16StringReceiver):

    def __init__(self, addr, factory):
        super().__init__()
        self.addr = addr
        self.factory = factory

    def connectionMade(self):
        print("<Game Server> : We are now bound to the game server. Authenticating connection...")
        self.factory.established_connection = self
        self.sendData(self.factory.key)
        self.transport.setTcpNoDelay(True)

    def connectionLost(self, reason=connectionDone):
        print(f"<Game Server> : Connection to game server was lost: {reason.getErrorMessage()}")
        if reason.check(ConnectionDone) is None:
            eventManager.notify("onNotificationMessage", "Disconnect", "The connection to the game server was lost.")
        self.factory.established_connection = None

    def sendData(self, data):
        self.sendString(data)

    def send_data(self, packet_id, *args):
        self.sendString((self.factory.packets.create_data)(packet_id, *args))

    def stringReceived(self, data):
        if data == b'ok':
            self.timeout = time.time()
            if self.ping:
                self.ping_response = time.clock() - self.ping
                self.ping = 0
            return
        for pk in getParts(data):
            if not pk:
                break
            packetNum = pk[0]
            try:
                self.factory.parsing.func[packetNum](self.factory.gamePacket.unpack(packetNum, pk))
            except:
                log.err()

    def cleanDisconnect(self):
        self.transport.loseConnection()


class GameCommunicationHandler(netb.TCPClient):
    established_connection: GameServerConnection

    def __init__(self):
        super().__init__()
        self.parsing = GamePacketDB()
        self.gamePacket = ClientPacket()
        self.key = None
        self.packet_queue = []
        self.connection = None
        self._disconnect_defer = defer.Deferred()
        eventManager.registerListener(self)
        self.timeout = 0
        self.ping = 0
        self.ping_response = 0
        self.established_connection = None

    def clientConnectionLost(self, connector, reason):
        self._disconnect_defer.callback(reason)

    def sendData(self, data):
        try:
            self.established_connection.sendString(data)
        except AttributeError:
            print("Attempted to send data but connection is gone.")

    def buildProtocol(self, addr):
        return GameServerConnection(addr, self)

    def connect(self, host, port, useSSL=False):
        self._disconnect_defer = defer.Deferred()
        if useSSL:
            self.connection = reactor.connectSSL(host, port, self, ssl.ClientContextFactory())
        else:
            self.connection = reactor.connectTCP(host, port, self)

    def disconnect(self):
        if self.connection:
            self.connection.disconnect()
            return self._disconnect_defer
        else:
            return


class GameNetHandler(netb.UDPClient):
    __doc__ = " Receives packets "

    def __init__(self):
        self.parsing = GamePacketDB()
        self.gamePacket = ClientPacket()
        self.key = None
        self.packet_queue = []
        eventManager.registerListener(self)
        self.timeout = 0
        self.ping = 0
        self.ping_response = 0

    def isConnected(self):
        return self.connected

    def connectionMade(self):
        print(f"<GameNet> : We are now bound to {self.host}:{self.port}")
        self.connected = True
        self.sendData(self.key)

    def connectionRefused(self):
        print("PRINT GAME CRASHED")
        self.connected = False

    def connectionFail(self):
        print("PRINT GAME CRASHED")
        self.connected = False

    def _sendPing(self):
        self.sendData(b'ok')
        self.ping = time.clock()

    def onThreadStart(self, threadId):
        self.timeout = time.time()
        self.sendPings = LoopingCall(self._sendPing)
        self.sendPings.start(1)
        self.timeOutCheck = LoopingCall(self._checkTimeout)
        self.timeOutCheck.start(1)

    def _checkTimeout(self):
        if time.time() - self.timeout >= TIMEOUT_INTERVAL:
            eventManager.notify("onNotificationMessage", "Disconnect", "The server has gone offline.")
            self.sendPings.stop()
            self.timeOutCheck.stop()

    def datagramReceived(self, data, address):
        if data == b'ok':
            self.timeout = time.time()
            if self.ping:
                self.ping_response = time.clock() - self.ping
                self.ping = 0
            return
        for pk in getParts(data):
            if not pk:
                break
            packetNum = pk[0]
            self.parsing.func[packetNum](self.gamePacket.unpack(packetNum, pk))


gameNetHandler = GameCommunicationHandler()
import client.control.net.login.handler
