# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\data\gui\bag.py
"""
Created on Dec 18, 2011

@author: Ragnarok
"""

class BagData:

    def __init__(self):
        self.money = 0
        self.weight = 0
        self.items = {}

    def getQuantity(self, itemId):
        return self.items.get(itemId).quantity

    def addItem(self, item):
        self.items[item.nameId] = item

    def incrQuantity(self, nameId, value):
        item = self.items[nameId]
        item.quantity += value

    def decrQuantity(self, nameId, value):
        item = self.items[nameId]
        item.quantity -= value

    def delItem(self, nameId):
        del self.items[nameId]

    def hasItem(self, nameId, quantity=1):
        itemData = self.items.get(nameId)
        if not itemData:
            return False
        else:
            if not itemData.quantity >= quantity:
                return False
            return True

    def hasItems(self, items):
        """ Make sure that bag as all the items specified """
        for nameids in items:
            item = items[nameids]
            if not self.hasItem(item.nameId, item.quantity):
                return False

        return True

    def getItem(self, nameId):
        return self.items[nameId]

    def getItemIfAny(self, nameId):
        if nameId in self.items:
            return self.items[nameId]
        else:
            return

    def getItems(self):
        return list(self.items.values())
