# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\data\gui\skins.py
"""
Created on Feb 8, 2012

@author: Ragnarok
"""

class Skin:

    def __init__(self, name):
        self.name = name
        self.elements = {}
        self.textStyles = {}

    def getElementPadding(self, element):
        return self.elements[element].padding

    def getElement(self, element):
        return self.elements[element]


class SkinElement:

    def __init__(self):
        self.padding = (0, 0, 0, 0)
        self.color = (0, 0, 0)
        self.data = None


class SkinTextStyle:

    def __init__(self, color, shadow):
        self.color = color
        self.shadow = shadow
