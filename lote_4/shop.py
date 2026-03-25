# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\data\gui\shop.py


class ShopItem:
    __slots__ = ['nameId', 'price', 'quantity', 'currency', 'restockTime', 'lastPurchased']

    def __init__(self, nameId, price, quantity, currency, restockTime):
        self.nameId = nameId
        self.price = price
        self.quantity = quantity
        self.currency = currency
        self.restockTime = restockTime


class ShopPokemon:
    __slots__ = [
     'dexId', 'price', 'quantity', 'currency', 'restockTime', 'lastPurchased']

    def __init__(self, dexId, price, quantity, currency, restockTime):
        self.dexId = dexId
        self.price = price
        self.quantity = quantity
        self.currency = currency
        self.restockTime = restockTime
