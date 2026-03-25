# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\data\gui\padding.py
"""
Created on 27 juil. 2011

@author: Kami
"""
from copy import copy

class PaddingData:

    def __init__(self, top, bottom, left, right):
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right

    def copy(self):
        return PaddingData(self.top, self.bottom, self.left, self.right)

    def __repr__(self):
        return f"PaddingData({self.top}, {self.bottom}, {self.left}, {self.right})"


defaultPadding = PaddingData(0, 0, 0, 0)
