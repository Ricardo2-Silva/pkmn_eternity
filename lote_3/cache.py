# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\system\cache.py
"""
Created on Oct 27, 2011

@author: Ragnarok
"""
from enum import Enum
from client.data.cache import nameCache
from shared.controller.net.packetStruct import RawPacker
from shared.container.net import cmsg
from shared.container.constants import IdRange
from client.control.net.sending import packetManager

class QueryType(Enum):
    friends = 0
    group = 1
    guild = 2
    quest = 3


class CacheController:

    def requestPCTrainerIds(self, queryType):
        self.requestIds(nameCache, IdRange.PC_TRAINER, QueryType[queryType])

    def requestIds(self, cache, idRange, queryType):
        charIds = cache.getIdsToGet(idRange)
        if charIds:
            packer = RawPacker()
            packer.pack("!BBBB", cmsg.MassQueryName, queryType.value, len(charIds), idRange)
            for charId in charIds:
                packer.pack("I", charId)

            packetManager.sendRaw(packer.packet)
        cache.clearIdsToGet(idRange)


cacheController = CacheController()
