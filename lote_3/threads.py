# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\net\threads.py
from client.control.events.event import eventManager
from shared.container.net import cmsg
from shared.controller.utils import Thread
import shared.controller.net.packetStruct as packetStruct

class ThreadSend(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.packetQueue = []
        eventManager.registerListener(self)

    def run(self):
        while self.keepAlive:
            self.stop()
            combine = b''
            while self.packetQueue:
                combine = (b'').join((combine, self.packetQueue.pop(0)))

            if combine:
                gameNetHandler.sendData(combine)

    def onThreadStart(self, threadId):
        if not self.is_alive():
            self.start()
        else:
            self.restart()

    def onSendPing(self):
        gameNetHandler.sendData(packetStruct.addLength(gameNetHandler.gamePacket.create(cmsg.Ping, None)))

    def onSendPacket(self, packet, *values):
        packet = (gameNetHandler.gamePacket.create)(packet, *values)
        self.packetQueue.append(packetStruct.addLength(packet))
        self.restart()

    def onSendRawPacket(self, packet):
        self.packetQueue.append(packetStruct.addLength(packet))
        self.restart()

    def onQueuePacket(self, dataType, *args):
        packet = (gameNetHandler.gamePacket.create)(dataType, *args)
        self.packetQueue.append(packetStruct.addLength(packet))

    def onSendQueue(self):
        self.restart()


threadSend = ThreadSend()
from client.control.net.world.handler import gameNetHandler, ClientPacket
