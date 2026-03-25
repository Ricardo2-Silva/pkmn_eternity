# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\render\system\loop.py
import pyglet

class FixedTimeStepLoop:

    def __init__(self, update_func, draw_func, step, max_step):
        self.update_func = update_func
        self.draw_func = draw_func
        self.step = step
        self.max_step = max_step
        self.accumulator = 0.0

    @property
    def current_interp(self):
        return self.accumulator / self.step

    def start(self):
        pyglet.clock.schedule(self._tick)

    def stop(self):
        pyglet.clock.unschedule(self._tick)

    def _tick(self, dt):
        if dt > self.max_step:
            dt = self.max_step
        self.accumulator += dt
        while self.accumulator >= self.step:
            self.update_func(self.step)
            self.accumulator -= self.step

        self.draw_func(self.accumulator / self.step)
