# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\system\background.py
"""
Created on 22 juil. 2011

@author: Kami
"""
from client.control.world.object import RenderedObject2D
from client.data.system.background import BackgroundData
from client.data.utils.color import Color
from client.render.system.background import BackgroundRender

class Background(RenderedObject2D):
    renderClass = BackgroundRender

    def __init__(self, data):
        self.data = data
        RenderedObject2D.__init__(self)

    def add(self):
        self.renderer.add()

    def remove(self):
        self.renderer.remove()

    def setAlpha(self, alpha):
        self.renderer.setAlpha(alpha)

    def setColor(self, *args):
        (self.renderer.setColor)(*args)

    def fadeColor(self, rgb, duration, startColor=None):
        self.renderer.fadeColor(rgb, duration, startColor)

    def fadeTo(self, *args):
        return (self.renderer.fadeTo)(*args)

    def fadeOut(self, *args):
        return (self.renderer.fadeOut)(*args)

    def fadeInAndOut(self, *args):
        return (self.renderer.fadeInAndOut)(*args)

    def destroy(self):
        self.renderer.destroy()


class BackgroundController:
    __doc__ = " Stores backgrounds, renders them and allow effect on them. "

    def __init__(self):
        self.bgs = {}
        self.blackedOut = True
        blackout = self.add(BackgroundData("blackout", color=(Color.BLACK), alpha=0), False)
        blackout.renderer.sprite.z = 20

    def adjustTimeCycle(self, rgb, duration=0.5):
        if "timeOfDayCycle" in self.bgs:
            bg = self.bgs["timeOfDayCycle"]
            bg.fadeColor(rgb, duration)

    def setTimeCycle(self, rgb):
        if "timeOfDayCycle" in self.bgs:
            bg = self.bgs["timeOfDayCycle"]
            (bg.setColor)(*rgb)

    def blackOut(self, duration=0.5):
        """ Fade to black """
        bg = self.bgs["blackout"]
        if not bg.visible:
            bg.show()
        bg.setAlpha(0)
        return self.fadeTo("blackout", duration, 255)

    def hideBlackOut(self):
        bg = self.bgs["blackout"]
        bg.hide()

    def endOfBlackOut(self, duration=1.0, color=Color.BLACK):
        """ Fade to black """
        bg = self.bgs["blackout"]
        if not bg.visible:
            bg.show()
        bg.setAlpha(255)
        return self.fadeOut("blackout", duration)

    def add(self, backgroundData, visible=True):
        background = Background(backgroundData)
        self.bgs[backgroundData.id] = background
        if not visible:
            background.hide()
        return background

    def exists(self, id):
        if id in self.bgs:
            return True
        else:
            return False

    def delete(self, id):
        background = self.bgs[id]
        background.destroy()
        del self.bgs[id]

    def fadeOut(self, bgId, duration):
        background = self.bgs[bgId]
        return background.fadeOut(duration)

    def fadeTo(self, bgId, duration, toAlpha=255):
        background = self.bgs[bgId]
        return background.fadeTo(duration, toAlpha)

    def fadeInAndOut(self, bgId, inDuration, outDuration, inAlpha, outAlpha):
        background = self.bgs[bgId]
        return background.fadeInAndOut(inDuration, outDuration, inAlpha, outAlpha)


backgroundController = BackgroundController()
