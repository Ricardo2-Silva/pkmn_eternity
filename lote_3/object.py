# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\world\object.py
"""
Created on 22 juil. 2011

@author: Kami
"""
from shared.container.geometry import InterfacePositionable2D, InterfacePositionable3D
import client.data.exceptions as exceptions
from client.data.settings import gameSettings
import pyglet
from shared.container.constants import RefPointType
from shared.controller.maths.maths import interpolatePosition

class RenderedObject(object):
    renderClass = NotImplementedError
    renderer: renderClass

    def __init__(self):
        self.renderer = self.renderClass(self)

    def hide(self, dt=None):
        pyglet.clock.unschedule(self.hide)
        pyglet.clock.unschedule(self.show)
        self.renderer.hide()

    def show(self):
        pyglet.clock.unschedule(self.hide)
        pyglet.clock.unschedule(self.show)
        self.renderer.show()

    def delete(self):
        pyglet.clock.unschedule(self.hide)
        pyglet.clock.unschedule(self.show)
        self.renderer.delete()

    @property
    def fading(self):
        return self.renderer.fading

    @property
    def visible(self):
        return self.renderer.visible


class RenderedObject2D(RenderedObject, InterfacePositionable2D):

    def setPosition(self, x, y):
        InterfacePositionable2D.setPosition(self, x, y)
        if self.renderer.ready:
            self.renderer.updatePosition()

    def setX(self, x):
        InterfacePositionable2D.setX(self, x)
        if self.renderer.ready:
            self.renderer.updatePosition()

    def setY(self, y):
        InterfacePositionable2D.setY(self, y)
        if self.renderer.ready:
            self.renderer.updatePosition()

    def setSize(self, width, height):
        InterfacePositionable2D.setSize(self, width, height)
        if self.renderer.ready:
            self.renderer.updateSize()

    def setHeight(self, height):
        InterfacePositionable2D.setHeight(self, height)
        if self.renderer.ready:
            self.renderer.updateSize()

    def setWidth(self, width):
        InterfacePositionable2D.setWidth(self, width)
        if self.renderer.ready:
            self.renderer.updateSize()


class RenderedObject3D(RenderedObject, InterfacePositionable3D):

    def __init__(self, *args, refPointType):
        (InterfacePositionable3D.__init__)(self, *args, **{"refPointType": refPointType})
        self.previous_state = (self.getX(), self.getY(), self.getZ())
        self.current_state = self.previous_state
        self.interp_state = self.previous_state
        RenderedObject.__init__(self)

    def resetRenderState(self):
        self.previous_state = self.current_state
        if self.renderer.ready:
            self.renderer.resetRenderState()

    def setPosition(self, x, y, z=0):
        self.previous_state = (
         self.getX(), self.getY(), self.getZ())
        InterfacePositionable3D.setPosition(self, x, y, z)
        if self.renderer.ready:
            self.renderer.updatePosition()
        self.current_state = (self.getX(), self.getY(), self.getZ())

    def setPositionNoRender(self, x, y, z):
        self.previous_state = (
         self.getX(), self.getY(), self.getZ())
        InterfacePositionable3D.setPosition(self, x, y, z)
        self.current_state = (
         self.getX(), self.getY(), self.getZ())

    def setRenderPosition(self, interp):
        self.interp_state = interpolatePosition(self.previous_state, self.current_state, interp)
        if self.renderer.ready:
            (self.renderer.setRenderPosition)(*self.interp_state, *(interp,))

    def getCurrentState(self):
        return self.interp_state

    def setSize(self, width, height):
        InterfacePositionable3D.setSize(self, width, height)
        if self.renderer.ready:
            self.renderer.updateSize()

    def setX(self, x):
        InterfacePositionable3D.setX(self, x)
        if self.renderer.ready:
            self.renderer.updatePosition()

    def setY(self, y):
        InterfacePositionable3D.setY(self, y)
        if self.renderer.ready:
            self.renderer.updatePosition()

    def setZ(self, z):
        InterfacePositionable3D.setZ(self, z)
        if self.renderer.ready:
            self.renderer.updatePosition()

    def setHeight(self, height):
        InterfacePositionable3D.setHeight(self, height)
        if self.renderer.ready:
            self.renderer.updateSize()

    def setWidth(self, width):
        InterfacePositionable3D.setWidth(self, width)
        if self.renderer.ready:
            self.renderer.updateSize()


from client.control.gui.implem import NamePlate, GlobalNamePlate
globalNamePlate = GlobalNamePlate()

class WorldObject(RenderedObject3D):
    __doc__ = " Abstract class for a world object. "
    referencePoint = RefPointType.BOTTOMCENTER

    def __init__(self, data):
        self.data = data
        self.camera = None
        self._diffEffectPosition = [
         0, 0, 0]
        (RenderedObject3D.__init__)(self, *(data.getPosition()), **{"refPointType": (self.referencePoint)})
        (InterfacePositionable3D.setSize)(self, *self.renderer.getSize())
        self.child_objects = []
        self._namePlate = None

    def createNamePlate(self):
        alwaysHaveWidget = gameSettings.getAlwaysNames()
        if alwaysHaveWidget:
            if alwaysHaveWidget == 1:
                if self.data.isNPC():
                    self._namePlate = NamePlate(self)
                    return self._namePlate
                else:
                    if alwaysHaveWidget == 2:
                        if self.data.isPCTrainer():
                            self._namePlate = NamePlate(self)
                            return self._namePlate
                    if alwaysHaveWidget == 3:
                        if self.data.isNPC() or self.data.isPCTrainer():
                            self._namePlate = NamePlate(self)
                            return self._namePlate
        return

    @property
    def namePlate(self):
        if self._namePlate:
            return self._namePlate
        else:
            if self.data.name:
                if self.createNamePlate():
                    return self._namePlate
                else:
                    globalNamePlate.setCharacter(self)
                    return globalNamePlate
            return

    def startAnim(self, anim):
        self.renderer.startAnim(anim)

    def getDiffEffectPosition(self):
        return (
         self._diffEffectPosition[0] + self.getX(), self._diffEffectPosition[1] + self.getY(), self._diffEffectPosition[2] + self.getZ())

    def getDiffEffectCurrentPosition(self):
        return self.interp_state

    def getDiffEffectProjection2D(self):
        x, y, z = self.getDiffEffectPosition()
        return (x, y - z)

    def setDiffEffectPosition(self, x, y, z=0):
        self._diffEffectPosition[0] = x
        self._diffEffectPosition[1] = y
        self._diffEffectPosition[2] = z
        if self.renderer.ready:
            self.renderer.updatePosition()

    def rotate(self, duration):
        """ Rotate for duration time with a specific speed. """
        if self.renderer.ready:
            self.renderer.rotate(duration)

    def delLinkedSkills(self):
        for effect in self.child_objects:
            if effect.__class__.__name__ in "SkillEffect":
                if effect.visible:
                    effect.hide()
                self.child_objects.remove(effect)

    def addLinkedObject(self, gameObject, offsetX=0, offsetY=0):
        self.child_objects.append(gameObject)

    def delLinkedObject(self, object):
        self.child_objects.remove(object)

    def setFollowedByCamera(self, camera):
        self.camera = camera

    def setNotFollowedByCamera(self):
        self.camera = None

    def forceHide(self):
        if self.visible:
            self.hide()

    def forceUnHide(self):
        if not self.visible:
            self.show()

    def highlight(self):
        """ When the char is overed it's highlighted. """
        if self.namePlate:
            self.namePlate.forceUnHide()

    def unHighlight(self):
        if self.namePlate:
            self.namePlate.forceHide()

    def setPosition(self, x, y, z=0):
        self.data.setPosition(x, y, z)
        RenderedObject3D.setPosition(self, x, y, z)

    def setPositionNoRender(self, x, y, z=0):
        self.data.setPosition(x, y, z)
        RenderedObject3D.setPositionNoRender(self, x, y, z)
