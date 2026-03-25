# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\service\map.py
"""
Created on 19 oct. 2011

@author: Kami
"""
from client.data.container.map import mapContainer

class MapService:
    __doc__ = " Bunch of services related to map. "

    def isInMap(self, x, y):
        if x < 0 or y > mapContainer.getMapSize()[1]:
            return False
        else:
            return True


mapService = MapService()
