# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\data\container\effects.py
"""
Created on Aug 10, 2016

@author: Admin
"""
from client.control.events.event import eventManager

class EffectContainer:

    def __init__(self):
        self.effects = []
        eventManager.registerListener(self)

    def onBeforeMapLoad(self):
        return

    def reset(self):
        self.wipeEffects()

    def wipeEffects(self):
        for effect in self.effects:
            try:
                effect.delete()
            except AttributeError:
                print(f"Warn: Trying to delete effect {effect.data.fileId} but was already deleted.")

        self.effects.clear()


effectContainer = EffectContainer()
