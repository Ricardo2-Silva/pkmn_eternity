# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\system\light.py
"""
Created on Oct 11, 2015

@author: Admin
"""
from client.control.world.object import RenderedObject2D
from client.render.system.light import LightRender
from client.control.events.event import eventManager
from client.data.container.map import mapContainer

class LightModes:
    NONE = "none"
    PULSE_SLOW = "slow"
    PULSE_FAST = "fast"


class Light(RenderedObject2D):
    renderClass = LightRender

    def __init__(self, data):
        self.data = data
        self.renderer = self.renderClass(self)
        (self.setColor)(*self.data.rgb)
        self.setMode(self.data.mode)
        (self.setSize)(*self.data.size)

    def _nearest_even(self, value):
        return value + 1 & -2

    def setSize(self, width, height):
        self.renderer.setSize(self._nearest_even(width), self._nearest_even(height))

    def setPosition(self, x, y):
        super().setPosition(self._nearest_even(x), self._nearest_even(y))

    def setMode(self, name):
        if name == LightModes.NONE:
            self.pulse(0, 1, 1.1)
        else:
            if name == LightModes.PULSE_SLOW:
                self.pulse(0, 1, 1.1)
        if name == LightModes.PULSE_FAST:
            self.pulse(0, 0.5, 1.1)

    def setAlpha(self, alpha):
        self.renderer.setAlpha(alpha)

    def pulse(self, pulseCount, duration, scale=1.2):
        self.renderer.pulse(pulseCount, duration, scale)

    def setColor(self, *args):
        (self.renderer.setColor)(*args)

    def lerpColor(self, r, g, b, a=255, dt=1):
        self.renderer.lerpColor(r, g, b, a, dt)

    def fadeOut(self, duration):
        self.renderer.setAlpha(0)

    def fadeIn(self, duration):
        self.renderer.setAlpha(255)

    def resetRenderState(self):
        self.renderer.resetRenderState()

    def setRenderPosition(self, interp):
        self.renderer.setRenderPosition(interp)

    def updateFromObjectRender(self, interp):
        if self.visible:
            self.setRenderPosition(interp)


class CharLight(Light):

    def __init__(self, lightsDict, char, data):
        Light.__init__(self, data)
        self.lightsDict = lightsDict
        self.char = char
        self.char.addLinkedObject(self)
        self.updatePosition()
        self.resetRenderState()
        self.show()

    def updatePosition(self):
        if not self.visible:
            return
        (self.data.setPosition)(*self.char.getCenter())
        self.renderer._updatePosition()

    def hide(self):
        """ Here we destroy it because once we recall or change maps we no longer need it.
            Sometimes called multiple times at once such as recall. Check if object exists first.
         """
        if self in self.char.child_objects:
            self.char.delLinkedObject(self)
            Light.hide(self)
            if self.char in self.lightsDict:
                del self.lightsDict[self.char]

    def updateFromObject(self):
        if self.visible:
            self.updatePosition()


class LightController(object):
    __doc__ = " Handles the current state of character and map lights "

    def __init__(self):
        self.charLights = {}
        self.lightsOn = False

    def turnOnLights(self, mapData):
        """ Turns on all light sources on the map, usually when it goes to night"""
        if not self.lightsOn:
            for light in mapData.lights:
                light.show()

        self.lightsOn = True

    def turnOffLights(self, mapData):
        """ Disables all light sources on the map """
        if self.lightsOn:
            for light in mapData.lights:
                light.hide()

        self.lightsOn = False

    def addCharLight(self, char, lightData):
        light = self.charLights.get(char, None)
        if light:
            light.setSize(light.data.size[0] * 2, light.data.size[1] * 2)
        else:
            self.charLights[char] = CharLight(self.charLights, char, lightData)

    def destroyCharLights(self):
        for light in self.charLights.values():
            light.delete()

        self.charLights.clear()

    def changingMap(self, mapData):
        self.destroyCharLights()
        self.turnOffLights(mapData)


lightController = LightController()
