# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\data\world\object.py
"""
Created on 21 juil. 2011

@author: Kami
"""
from shared.container.constants import IdRange, CharCategory, ControlType
from client.data.layer import LayerType

class WorldObjectData:
    __doc__ = " Abstract class which defines a data for a object. "
    fileId = None
    x = 0
    y = 0
    z = 0
    outOfView = False
    layerType = LayerType.LAYERED

    def __init__(self, fileId, x, y, z=0):
        self.x, self.y, self.z = x, y, z
        self.fileId = fileId
        self.name = ""

    def getPosition(self):
        return (
         self.x, self.y)

    def getPosition3D(self):
        return (
         self.x, self.y, self.z)

    def setPosition(self, x, y, z=0):
        self.x = x
        self.y = y
        self.z = z

    def getDefaultSize(self):
        return (24, 24)


class BasicCharData(WorldObjectData):
    __doc__ = " Abstract class which defines a data for a object. "
    id = 0
    idRange = IdRange.NONE
    category = CharCategory.NONE
    controlType = ControlType.NONE
    flags = 0
    dialogStatus = 0

    def __init__(self, id, idRange, category, controlType, fileId, position):
        self.id = id
        self.idRange = idRange
        self.category = category
        self.controlType = controlType
        (WorldObjectData.__init__)(self, fileId, *position)

    def getIdRange(self):
        return self.idRange

    def getId(self):
        return self.id
