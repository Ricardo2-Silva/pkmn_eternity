# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\world\animation.py
"""
Created on 15 juil. 2011

@author: Kami
"""
from twisted.internet import task, defer, reactor
import pyglet
from client.data.world.animation import AnimationSpeed

class AnimationManager:
    __doc__ = " This manages animations for the world, as they all must be batched together to animate together such\n    as water or other groudn tiles.."

    def __init__(self):
        self._objects = {}
        self._loops = {}
        self._accumulator = {}
        for delay in AnimationSpeed.ALL:
            self._loops[delay] = self.getAnimationFunc()
            self._objects[delay] = []
            self._accumulator[delay] = 0

    def reset(self):
        for delay in AnimationSpeed.ALL:
            pyglet.clock.unschedule(self._loops[delay])
            self._objects[delay].clear()
            self._accumulator[delay] = 0

    def getCurrentFrame(self, delay, frames):
        """Uses the accmulator to make sure we are on the same frame as the rest."""
        return int(self._accumulator[delay] % frames)

    def getAnimationFunc(self):

        def animate(dt, delay):
            self._accumulator[delay] += 1
            for animableObject in self._objects[delay]:
                animableObject.animate()

        return animate

    def register(self, animableObject, delay):
        if not self._objects[delay]:
            pyglet.clock.schedule_interval(self._loops[delay], delay, delay)
        self._objects[delay].append(animableObject)

    def removeIfRegistered(self, animableObject, delay):
        if animableObject in self._objects[delay]:
            self.unRegister(animableObject, delay)

    def unRegister(self, animableObject, delay):
        if animableObject not in self._objects[delay]:
            raise Exception("The object is not in animation Manager")
        self._objects[delay].remove(animableObject)
        if not self._objects[delay]:
            pyglet.clock.unschedule(self._loops[delay])
            self._accumulator[delay] = 0


animationManager = AnimationManager()

class InterfaceAnimable:
    __doc__ = " Allows any object to be animated. "
    _animationDelay = 0
    _animationDuration = 0

    def runAnimation(self, animation):
        self.d = defer.Deferred()
        self._step = 0
        self._animationDelay = delay
        self._animationDuration = duration
        pyglet.clock.schedule_once(self._animate, self._animationDelay)
        return self.d

    def isAnimating(self):
        return self._step < self._animationDuration

    def stopAnimation(self):
        pyglet.clock.unschedule(self._animate)

    def _animate(self, dt):
        self._step += dt
        self.animate()
        if self._step >= self._animationDuration:
            self.d.callback("done")
            return
        pyglet.clock.schedule_once(self._animate, self._animationDelay)

    def animate(self):
        raise NotImplementedError
