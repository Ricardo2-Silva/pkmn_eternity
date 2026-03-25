# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\data\layer.py
"""
Created on 19 juil. 2011

@author: Kami
"""

class LayerType:
    BELOW_2 = -2
    BELOW_1 = -1
    BELOW_0 = 0
    LAYERED = "layered"
    LAYERED_FIXED = 10
    PARTICLES = "particles"
    LIGHT = "light"
    ALL_MAP_LAYERS = (BELOW_2, BELOW_1, BELOW_0, LAYERED_FIXED)
    ALL_LAYERS = (BELOW_2, BELOW_1, BELOW_0, LAYERED_FIXED, LAYERED)
    TILE_LAYERS = (BELOW_2, BELOW_1, BELOW_0)
    BACKGROUND_BEHIND = -2999
    BACKGROUND_MIDDLE = 15
    BACKGROUND_FRONT = 2999
    GUI = 30
    GROUND_START = -2998
    OBJECT_SHADOWS = GROUND_START + 10
    ABOVE_PLAYER = 0


class LayerMode:
    PENDING = 1
    NORMAL = 0
