# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\data\world\item.py
"""
Created on 22 juil. 2011

@author: Kami
"""
from client.data.world.object import WorldObjectData, BasicCharData
from shared.container.constants import IdRange, CharCategory, ControlType
from client.data.DB import itemDB

class ItemData:

    def __init__(self, nameId):
        self.nameId = nameId
        self.itemInfo = itemDB.getItem(nameId)
        self.quantity = 0
        self.type = 0
        self.sell = 0

    @property
    def name(self):
        return self.itemInfo.formatted

    @property
    def graphicId(self):
        return self.itemInfo.graphicId


class WorldItemData(BasicCharData):

    def __init__(self, id, fileId, position):
        BasicCharData.__init__(self, id, IdRange.NPC_ITEM, CharCategory.ITEM, ControlType.NPC, fileId, position)

    def isWorldObject(self) -> bool:
        return False


class BallData(WorldItemData):
    return
