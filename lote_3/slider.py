# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\gui\slider.py
from client.control.gui.container import Container
from client.data.utils.color import Color
from client.control.gui.picture import Picture
from client.render.cache import textureCache
from client.control.gui.button import Button
from client.data.gui import styleDB
import math, pyglet
from shared.container.constants import CursorMode
from shared.service.utils import clamp

class SlideButton(Button):

    def __init__(self, parent, *args, **kwargs):
        (Button.__init__)(self, parent, *args, **kwargs)
        self.container = parent

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.desktop.cursor.mode = CursorMode.DRAGGING
        self.container.slide(dx)

    def onMouseDrop(self, widget, x, y, modifiers):
        return

    def onKeyDown(self, symbol, modifiers):
        if symbol == pyglet.window.key.LEFT:
            self.container.keySlide(-1)
        elif symbol == pyglet.window.key.RIGHT:
            self.container.keySlide(1)


class Slider(Container):

    def __init__(self, parent, position=(0, 0), size=(100, 16), draggable=False, visible=True):
        Container.__init__(self, parent, position, size, draggable, visible, (False,
                                                                              True))
        self.bar = Picture(self, picture=(textureCache.getBackgroundColor(Color.GREY)), position=(0,
                                                                                                  7), size=(size[0], 2), autosize=(False,
                                                                                                                                   False))
        self.round = SlideButton(self, text="", style=(styleDB.roundButtonStyle), size=(17,
                                                                                        17), draggable=True)
        self.virtual_position = 0.0
        self.oldValue = None
        self.values = []
        self._value = None
        self.fitToContent()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        if val not in self.values:
            raise Exception("This value is not in the values set.", val)
        self.setSnap(val)
        self.oldValue = val
        self.virtual_position = self.round.relativeX / float(self.width - 17)
        self._value = self._getValue()
        self.runCallback("onValueChange", self._value)

    @property
    def numberOfValues(self):
        return len(self.values) - 1

    @property
    def threshhold(self):
        return 1.0 / len(self.values)

    @property
    def knobFloatPosition(self):
        return self.round.relativeX / float(self.width - 17)

    def setSnap(self, value):
        index = self.values.index(value)
        try:
            floatValue = index / float(self.numberOfValues)
        except ZeroDivisionError:
            floatValue = 0

        x = floatValue * float(self.width - 17)
        self.round.setRelativePosition(int(x), 0)

    def keySlide(self, dx):
        """ Calculates based on keyboard left and right """
        if self.numberOfValues:
            index = self.values.index(self._value) + dx
            value = self.values[clamp(index, 0, self.numberOfValues)]
            self.value = value

    def slide(self, dx):
        """ Calculates based on mouse DX """
        if self.numberOfValues:
            if self.round.relativeX + dx >= 0:
                if self.round.relativeX + dx <= self.width - 17:
                    self.virtual_position += dx / float(self.width - 17)
                    if abs(self.virtual_position - self.knobFloatPosition) >= self.threshhold:
                        self._value = self._getValue()
                        self.setSnap(self._value)
                        if self.value != self.oldValue:
                            self.oldValue = self._value
                            self.runCallback("onValueChange", self._value)

    def setValues(self, *values):
        self.values = values
        self.oldValue = values[0]
        self._value = self._getValue()

    def addValue(self, value):
        self.values.append(value)
        self._value = self._getValue()

    def _getValue(self):
        assert len(self.values) > 0, "There are no values for this slider."
        index = int(round(self.virtual_position * self.numberOfValues))
        return self.values[index]
