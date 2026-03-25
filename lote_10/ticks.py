# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: shared\service\ticks.py
"""
Created on 22 oct. 2011

@author: Kami
"""
from twisted.internet import task
from shared.controller.utils import Thread

class UpdateTicks:

    def __init__(self):
        self.objectsToUpdate = []
        self.objectsToDelete = []
        self.objectsToAdd = []

    def stop(self):
        self.ltask.stop()

    def run(self, loopTime):
        self.ltask = task.LoopingCall(self.update)
        self.ltask.start(loopTime)

    def update(self):
        self.clean()
        for t in self.objectsToUpdate:
            t.update()

    def clean(self):
        self.objectsToUpdate.extend(self.objectsToAdd)
        for t in self.objectsToDelete:
            self.objectsToUpdate.remove(t)

        del self.objectsToDelete[:]
        del self.objectsToAdd[:]

    def delete(self, object):
        if object in self.objectsToAdd:
            self.objectsToAdd.remove(object)
            return
        elif object not in self.objectsToDelete:
            self.objectsToDelete.append(object)
        else:
            Exception("Already added into the list")

    def add(self, object):
        if object in self.objectsToDelete:
            self.objectsToDelete.remove(object)
            return
        elif object not in self.objectsToAdd:
            self.objectsToAdd.append(object)
        else:
            Exception("Already added into the list")
