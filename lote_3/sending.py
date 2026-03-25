# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\net\sending.py
"""
Created on 8 oct. 2011

@author: Kami
"""
from client.control.net.threads import threadSend

class ClientPacketManager:

    def queue(self, datatype, *args):
        (threadSend.onQueuePacket)(datatype, *args)

    def send(self):
        threadSend.onSendQueue()

    def sendRaw(self, packet):
        threadSend.onSendRawPacket(packet)

    def queueSend(self, datatype, *args):
        """ Queue the packet and sends it. """
        (threadSend.onSendPacket)(datatype, *args)

    def ping(self):
        threadSend.onSendPing()


packetManager = ClientPacketManager()
