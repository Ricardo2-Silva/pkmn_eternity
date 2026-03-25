# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\net\login\handler.py
"""
Created on Jul 12, 2017

@author: Admin
"""
from client.control.service.session import sessionService
from client.control.events.event import eventManager
from shared.container.net import lmsg
from shared.service.utils import getParts
from client.data.settings import gameSettings
from client.control.net.login.parseDB import LoginPacketDB
from shared.controller.net import packetStruct
import shared.controller.net.netbase as netb
from client.data.DB import messageDB
from shared.container.constants import VERSION
from twisted.internet.protocol import Protocol
from twisted.internet import error
from client.interface.notification import notificationControl

class LoginConnection(Protocol):

    def connectionMade(self):
        print(f"------<LoginNet> : We are now bound to {(self.factory.host, self.factory.port)}")
        self.factory.main_protocol = self
        print("<LoginNet> : Sending player connect data.")
        self.send_data(lmsg.PlayerConnect, None)
        self.transport.setTcpNoDelay(True)

    def send_data(self, packet_id, *args):
        self.transport.write((self.factory.packets.create_data)(packet_id, *args))

    def dataReceived(self, data):
        for pk in getParts(data):
            if not pk:
                break
            packet_num = pk[0]
            if packet_num in self.factory.parsing.func:
                self.factory.parsing.func[packet_num](self.factory.packets.unpack(packet_num, pk), self.factory)


class LoginNetHandler(netb.TCPClient):

    def __init__(self):
        self.host = gameSettings.getServerIP("eternity")
        self.port = gameSettings.getServerPort("eternity")
        self.connected = False
        self.main_protocol = None
        self.parsing = LoginPacketDB()
        self.packets = packetStruct.LoginPacket(self)
        self.username = None
        self.password = None
        self.creation = None
        self.state = None
        eventManager.registerListener(self)

    def buildProtocol(self, addr):
        protocol = LoginConnection()
        protocol.factory = self
        return protocol

    def create(self, trainerName, bodyId, gender, skintone, hairId, hairColor, clothesColor):
        self.main_protocol.send_data(lmsg.CreateTrainer, trainerName, bodyId, gender, skintone, hairId, hairColor, clothesColor)

    def keyReceived(self, key):
        self.key = key
        gameNetHandler.key = key
        eventManager.notify("onDisplayNotification", "Connection", "Received response, logging in...")
        if self.creation:
            packet = lmsg.CreateAccount
        else:
            packet = lmsg.PlayerLogin
        self.main_protocol.send_data(packet, VERSION.encode("utf-8"), self.username.strip().encode("utf-8"), self.password.strip().encode("utf-8"))

    def readyToGetData(self):
        """ Tell login server to tell game server that we are ready for data """
        sessionService.ingame = True
        self.main_protocol.send_data(lmsg.Response, lmsg.LOGIN_OK)

    def resetData(self):
        self.connected = False
        self.username = None
        self.password = None
        self.creation = None
        self.key = None
        self.state = None

    def clientConnectionLost(self, connector, reason):
        self.resetData()
        if not isinstance(reason.value, error.ConnectionDone):
            eventManager.notify("onNotificationMessage", "Notification", messageDB["LOGIN_CONNECTION_FAIL"])
            eventManager.notify("onHideNotification", "Connection")

    def clientConnectionFailed(self, connector, reason):
        print(f"<LoginNet> : Failed to connect to {self.host}:{self.port}")
        eventManager.notify("onNotificationMessage", "Notification", messageDB["LOGIN_CONNECTION_FAIL"])
        eventManager.notify("onHideNotification", "Connection")

    def loginToServer(self, username, password, creation=False):
        print("<LoginNet To game server> : Login Connection Request.")
        eventManager.notify("onDisplayNotification", "Connection", "Establishing a connection...")
        self.username = username
        self.password = password
        self.creation = creation
        self.connect(self.host, self.port)


loginNetHandler = LoginNetHandler()
from client.control.net.world.handler import gameNetHandler
