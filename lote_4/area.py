# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\interface\area.py
"""
Created on Aug 25, 2018

@author: Admin
"""
from client.control.gui.windows import Window
from client.game import desktop
from client.data.settings import gameSettings
from client.control.gui.label import Label
import pyglet
from client.data.utils.anchor import AnchorType
import rabbyt
from client.control.gui.container import StylizedContainer
from client.control.system.anims import MoveBy, ParallelAnims, FadeIn, modify_time, Animable

class MoveByEaseOut(MoveBy):

    def init(self, target, coordinates, duration):
        self.target = target
        self.start_position = self.target.position
        self.end_position = (self.start_position[0] + coordinates[0], self.start_position[1] + coordinates[1])
        self.duration = duration

    def start(self):
        self.start_position = self.target.position

    def update(self, t):
        t = modify_time(t, "ease_out")
        self.target.setPosition(self.start_position[0] + (self.end_position[0] - self.start_position[0]) * t, self.start_position[1] + (self.end_position[1] - self.start_position[1]) * t)


class FadeInGUI(Animable):

    def init(self, target, duration):
        self.target = target
        self.duration = duration

    def update(self, t):
        self.target.setAlpha(255 * t)


class AreaDisplay(Window):

    def __init__(self):
        self.original_position = (-100, 100)
        Window.__init__(self, desktop, size=(100, 30), position=(self.original_position), draggable=False, visible=False, autosize=(True,
                                                                                                                                    True))
        self.focusEnabled = False
        self.area_lbl = Label(self, text="Test", position=(AnchorType.CENTER))

    def reset(self):
        pyglet.clock.unschedule(self.hide_it)
        self.renderer.stopAnims()
        self.forceHide()

    def set_area(self, area):
        pyglet.clock.unschedule(self.hide_it)
        self.renderer.stopAnims()
        (self.setPosition)(*self.original_position)
        self.show()
        self.area_lbl.text = area.name
        self.fitToContent()
        x, y = self.area_lbl.position
        self.renderer.setAlpha(0)
        pyglet.clock.schedule_once(self.hide_it, 4)
        anim = FadeInGUI(self, 1)
        anim |= MoveByEaseOut(self, (110, 0), 1)
        self.renderer.startAnim(anim)
        desktop._focusWidget = None

    def hide_it(self, dt):
        StylizedContainer.hide(self)

    def display_area(self):
        Window.show(self)


areaDisplay = AreaDisplay()
