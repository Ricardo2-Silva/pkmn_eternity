# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: shared\container\utils\store.py
"""
Created on 25 sept. 2011

@author: Kami
"""

class DBId:

    def __init__(self, dictName, dataName):
        self.idToData = {}
        self._init()

    def _init(self):
        raise Exception("DB _init Must be implemented.")

    def getById(self, id):
        return self.idToData[id]

    def delById(self, id):
        del self.idToData[id]

    def setById(self, id, value):
        self._set(id, value)

    def getByIdIfAny(self, id):
        return self.idToData.get(id)

    def _set(self, id, value):
        self.idToData[id] = value

    def _append(self, key, value):
        if key not in self.idToData:
            self.idToData[key] = []
        self.idToData[key].append(value)

    def values(self):
        return list(self.idToData.values())

    def hasId(self, id):
        return id in self.idToData


class DBIdName(DBId):

    def __init__(self, dictName, dataName):
        self.nameToData = {}
        DBId.__init__(self, dictName, dataName)

    def delById(self, id):
        val = self.idToData[id]
        del self.idToData[id]
        del self.nameToData[val.name]

    def _set(self, id, name, value):
        self.idToData[id] = value
        self.nameToData[name] = value

    def getByName(self, name):
        return self.nameToData[name]

    def getByNameIfAny(self, name):
        return self.nameToData.get(name)

    def getByNameOrId(self, idOrName):
        if isinstance(idOrName, str):
            return self.getByName(idOrName)
        else:
            return self.getById(idOrName)
