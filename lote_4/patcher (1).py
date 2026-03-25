# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\interface\patcher.py
"""
Created on Sep 22, 2011

@author: Ragnarok
"""
from client.control.gui import Window, Bar, Label
from client.control.events.event import eventManager
from client.data.utils.anchor import AnchorType, Alignment
from client.game import desktop
from twisted.internet import reactor

class PatchWindow(Window):

    def __init__(self):
        Window.__init__(self, desktop, position=(AnchorType.CENTER), autosize=(True,
                                                                               True), size=(240,
                                                                                            100), visible=True, draggable=False)
        self.label = Label(self, position=(AnchorType.CENTERTOP),
          size=(200, 0),
          alignment=(Alignment.CENTER),
          autosize=(False, True),
          text="An update was found.\n\nAttempting to downloading patches.",
          multiline=True)
        self.progressBar = Bar(self, position=(AnchorType.CENTERTOP), size=(175, 10))
        self.progressBar.setPercent(0, 100)
        self.progressBar.setRelativePosition(self.progressBar.relativeX, self.label.relativeY + self.label.height + 20)
        self.setId("Patcher")

    def hide(self):
        Window.hide(self)

    def show(self):
        Window.show(self)
        from client.control.system.patcher import patchHandler
        reactor.callLater(0.5, patchHandler.downloadPatches)


class Patcher:

    def __init__(self):
        eventManager.registerListener(self)
        self.window = PatchWindow()

    def on_enter(self):
        self.window.show()

    def on_exit(self):
        self.window.hide()

    def onPatchMessage(self, message):
        self.window.label.text = message
        self.window.progressBar.relativeY = self.window.label.relativeY + self.window.label.height + 20

    def onPatchProgress(self, current, total):
        self.window.progressBar.setPercent(current, total)


patchControl = Patcher()
