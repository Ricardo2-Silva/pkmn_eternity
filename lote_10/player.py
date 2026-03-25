# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: shared\container\player.py
"""
Created on Jan 16, 2019

@author: Admin
"""

class Appearance:
    __slots__ = [
     "id", "databaseId", "color"]

    def __init__(self, id, color):
        self.databaseId = 0
        self.id = id
        self.color = color

    def __eq__(self, other):
        return self.id == other.id and self.color == other.color


class AppearanceItem:
    __slots__ = [
     "type", "id", "color", "databaseId"]

    def __init__(self, type, id, color):
        self.type = type
        self.id = id
        self.color = color
        self.databaseId = 0


class PlayerAppearance:

    def __init__(self, gender, skintone, body, hairId, hairColor, clotheId, clotheColor, accessoryId, accessoryColor):
        self.gender = gender
        self.skintone = skintone
        self.body = body
        self.eyeId = 0
        self.hair = Appearance(hairId, hairColor)
        self.clothe = Appearance(clotheId, clotheColor)
        self.accessory = Appearance(accessoryId, accessoryColor)
        self.inventory = []

    def __eq__(self, other):
        return self.body == other.body and self.gender == other.gender and self.skintone == other.skintone and self.hair == other.hair and self.clothe == other.clothe and self.accessory == other.accessory

    def data(self):
        return (
         self.gender, self.skintone, self.body, self.hair.id, self.hair.color, self.clothe.id, self.clothe.color, self.accessory.id, self.accessory.color)
