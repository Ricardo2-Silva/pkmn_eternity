# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: shared\controller\maths\maths.py
"""
Created on 29 sept. 2011

@author: Kami
"""
from shared.container.constants import MapSettings
from shared.service.geometry import roundPosition

def inBounds(value, min, max):
    if value < min or value > max:
        return False
    else:
        return True


def average(values):
    """Computes the arithmetic mean of a list of numbers.
    """
    return sum(values, 0.0) / len(values)


def sign(value):
    if value >= 0:
        return 1
    else:
        return -1


def positionToSquareIndex(x, y):
    x, y = roundPosition(8, x, y)
    return (int(y / MapSettings.SQUARE), int(x / MapSettings.SQUARE))


def lerp(start, end, a):
    return (1 - a) * start + a * end


def interpolate(val1, val2, t):
    return val1 * (1 - t) + val2 * t


def interpolatePosition(xxx_todo_changeme, xxx_todo_changeme1, per):
    x0, y0, z0 = xxx_todo_changeme
    x1, y1, z1 = xxx_todo_changeme1
    return (interpolate(x0, x1, per), interpolate(y0, y1, per), interpolate(z0, z1, per))


def interpolatePosition2D(xxx_todo_changeme2, xxx_todo_changeme3, per):
    x0, y0 = xxx_todo_changeme2
    x1, y1 = xxx_todo_changeme3
    return (interpolate(x0, x1, per), interpolate(y0, y1, per))
