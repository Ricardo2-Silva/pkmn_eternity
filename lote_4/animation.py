# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\data\world\animation.py
"""
Created on 17 juil. 2011

@author: Kami
"""
import random

class AnimationSpeed:
    VERYFAST = 0.1
    FAST = 0.2
    NORMALFAST = 0.3
    NORMAL = 0.5
    NORMALSLOW = 0.8
    SLOW = 1
    VERYSLOW = 1.5
    NONE = 0
    WALKING0 = 0.2
    WALKING1 = WALKING0 + 0.02
    WALKING2 = WALKING0 - 0.02
    ALL_WALKING = [WALKING0, WALKING1, WALKING2]
    ALL = [
     VERYFAST, FAST, NORMALFAST, NORMAL, NORMALSLOW, SLOW, VERYSLOW]
    strToSpeed = {
     'veryfast': VERYFAST, 'fast': FAST, 'normalfast': NORMALFAST, 'normal': NORMAL, 
     'normalslow': NORMALSLOW, 'slow': SLOW, 'veryslow': VERYSLOW}


class AnimationEnd:
    STOP = 0
    RESTART = 1
    REVERSE = 2


class AnimType:
    ONCE = 0
    INFINITE = -1
    NONE = -2
    ONCE_STAY = 1


class AnimDirection:
    FORWARD = 0
    REVERSE = 1
    FORWARD_REVERSE = 2


def getRandomWalkingSpeed():
    return AnimationSpeed.ALL_WALKING[random.randint(0, len(AnimationSpeed.ALL_WALKING) - 1)]


class AnimationFrame:
    __slots__ = [
     "index", "duration"]

    def __init__(self, index, duration=0):
        self.index = index
        self.duration = duration

    def __repr__(self):
        return f"AnimationFrame(index={self.index}, duration={self.duration})"


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


class Animation(object):
    __doc__ = ' How an animation is played and controlled.\n     frames: A list containing at least 2 entries, index and duration.\n             default: All image slices.\n     duration: How long this effect will play before removal. In seconds. 0 = Infinite\n               default: sum of duration on AnimationFrame list.\n     end: AnimationEnd for what to do when an animation reaches the final frame.\n     period: Only specify this is if you want to override the frame period.\n     removal: Action to take on duration end. Valid arguments: False, "delete", "hide"\n     duration: \n    '

    def __init__(self, frames=None, duration=None, delay=None, end=AnimationEnd.RESTART, removal="delete"):
        self.delay = delay
        self._created = False
        self.frames = frames
        self.duration = duration
        self.end = end
        self.removal = removal

    def create(self, sheet):
        """ We need to create this data in the renderer to ensure all frames are accounted for. """
        self.sheet = sheet
        if not self._created:
            if self.frames:
                if self.delay is None:
                    self.frames = [AnimationFrame(*chunk) for chunk in chunks(self.frames, 2)]
                else:
                    self.frames = [AnimationFrame(frame, self.delay) for frame in self.frames]
            else:
                if self.delay is None:
                    self.delay = self.sheet.getAnimationDelay()
                elif not self.delay > 0:
                    raise AssertionError(f"The delay between frames cannot be {self.delay}.")
                self.frames = [AnimationFrame(idx, self.delay) for idx, frame in enumerate(sheet.grid)]
            if self.duration is None:
                self.duration = sum(frame.duration for frame in self.frames)
            self._created = True
