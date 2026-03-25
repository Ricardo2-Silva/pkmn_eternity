# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\gui\bar.py
from client.control.gui.widget import StylizedWidget
import time, client.render.gui as iCoreRender
from twisted.internet import reactor
from client.data.gui import styleDB
import pyglet
from shared.service.utils import clamp

class Bar(StylizedWidget):
    renderClass = iCoreRender.BarRender

    def __init__(self, parent, style=styleDB.defaultBarStyle, per=0, position=(0, 0), size=(35, 5), draggable=False, visible=True, reverseFill=False):
        self.per = per
        self.originalSize = size[0]
        self.reverseFill = reverseFill
        self.hideWhenFull = False
        self.duration = 0
        StylizedWidget.__init__(self, style, parent, position, size, draggable, visible)
        self._setPercent(per)

    def setStyle(self, style):
        self.style = style
        self.renderer.refresh()

    def forceHide(self):
        self.per = 0
        pyglet.clock.unschedule(self._updateFillBarInSeconds)
        pyglet.clock.unschedule(self.deleteTimerAndHide)
        StylizedWidget.forceHide(self)

    def getOriginalWidth(self):
        return self.originalSize

    def getPercent(self):
        return self.per

    def _setPercent(self, per):
        self.per = clamp(per, 0, 1.0)
        self.renderer.setBarColor(self.per)
        self.renderer.setPercent(self.per)

    def setPercent(self, current, maxHp):
        value = current / maxHp
        if self.per == value:
            return
        self.per = value
        if current == 0:
            self.per = 0
        self._setPercent(self.per)

    def setPercent2(self, per):
        self._setPercent(per)

    def fillPercent(self, per, seconds):
        self.fillBarInSeconds(seconds, per)

    def fillBarInSeconds(self, seconds, value=1):
        self.duration = seconds
        pyglet.clock.schedule_interval(self._updateFillBarInSeconds, 0.016666666666666666, value)
        pyglet.clock.schedule_once(self.deleteTimerAndHide, seconds)

    def _updateFillBarInSeconds(self, dt, value):
        if self.reverseFill:
            fill = -(dt * value / self.duration)
        else:
            fill = dt * value / self.duration
        self.setPercent2(self.per + fill)
        if not self.visible:
            self.forceUnHide()

    def deleteTimerAndHide(self, dt):
        if self.hideWhenFull:
            self.forceHide()
