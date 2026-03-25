# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\interface\map\loading.py
"""
Created on 16 oct. 2011

@author: Kami
"""
import random
from client.control.gui import Bar, Window, Picture, Label
from client.data.utils.anchor import AnchorType, Alignment
from client.control.events.event import eventManager
from client.data.gui import styleDB
from client.data.settings import gameSettings
from client.game import desktop
from client.scene.manager import sceneManager

class LoadingScreen:

    def __init__(self):
        self.backgroundNames = [
         "beach", "cave", "forest", "plains"]
        self.background = Picture(desktop, picture=(styleDB.blackTexture), size=(gameSettings.getScaledUIWindowResolution()), visible=True)
        self.windows = Window(desktop, size=(200, 70), position=(AnchorType.CENTER), visible=False, draggable=False)
        self.bar = Bar((self.windows), position=(AnchorType.BOTTOMCENTER), size=(180,
                                                                                 10))
        self.label = Label((self.windows), position=(AnchorType.TOPCENTER), size=(180,
                                                                                  0), autosize=(False,
                                                                                                True), text="Loading...",
          alignment=(Alignment.CENTER),
          multiline=True)
        eventManager.registerListener(self)
        self.currentStep = 0.0
        self.steps = 5.0

    def chooseBackground(self, gameMap):
        bg = random.choice(self.backgroundNames)
        num = random.randint(1, 2)
        filename = f"bgs/{bg}_{str(num).zfill(2)}.jpg"
        from client.render.cache import textureCache
        texture = textureCache.getImageFile(filename)
        self.background.setPicture(texture)

    def onShowLoadingScreen(self, text, steps=5):
        sceneManager.changeScene("Loading")
        self.background.show()
        self.chooseBackground(None)
        self.bar.setPercent(0, 100)
        self.steps = float(steps)
        self.currentStep = 0
        self.label.text = "Loading {0}...".format(text)
        eventManager.notify("onForceRender")
        self.windows.fitToContent()
        self.windows.show()
        self.windows.setOnTop()

    def setLoadingMessage(self, text):
        self.label.text = "Loading {0}...".format(text)
        self.windows.fitToContent()

    def updatePercentage(self, per):
        self.bar.setPercent(per, 1.0)

    def hide(self):
        self.background.hide()

    def onHideLoadingScreen(self):
        sceneManager.changeScene("World")
        self.background.hide()
        self.windows.hide()

    def updateLoadingBar(self, step=1):
        self.currentStep += step
        self.updatePercentage(float(self.currentStep) / self.steps)
        eventManager.notify("onForceRender")


loadingScreen = LoadingScreen()
