# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\interface\timing.py
"""
Created on Sep 13, 2017

@author: Admin
"""
from enum import Enum
from client.control.events import eventManager
from client.control.gui.windows import Window
from client.game import desktop
from client.data.utils.anchor import AnchorType
from client.data.gui import styleDB
from client.control.gui.label import Label
from client.control.gui.tables import Datatable
import time, pyglet
from twisted.internet import reactor
from client.interface.npc.quest import quest
from shared.container.constants import TimerTypes

class Timing:

    def __init__(self, sourceType, timerSource, timeStamp, duration, timeSourceLbl, timeLabel, timerWindow):
        self.sourceType = sourceType
        self.timerSource = timerSource
        self.timeStamp = timeStamp
        self.duration = duration
        self.timeSourceLbl = timeSourceLbl
        self.timeLabel = timeLabel
        self.timerWindow = timerWindow
        self.table = timerWindow.table
        pyglet.clock.schedule_interval(self.update, 1)

    def delete(self):
        pyglet.clock.unschedule(self.update)
        self.table.deleteAndDestroy(self.timeSourceLbl)
        self.table.deleteAndDestroy(self.timeLabel)
        self.table.fitToContent()
        if not self.table.getWidgets():
            self.table.parent.forceHide()

    def update(self, dt):
        secondsLeft = int(self.timeStamp - time.time() + self.duration)
        if secondsLeft <= 0:
            pyglet.clock.unschedule(self.update)
            self.timeLabel.text = "- Times Up!"
            reactor.callLater(3, self.timerWindow.removeSource, self.sourceType, self.timerSource)
            return
        timeStr = time.strftime("%M:%S", time.gmtime(secondsLeft))
        self.timeLabel.text = f"- Time Left: {timeStr}"


class TimerControl:

    def __init__(self):
        eventManager.registerListener(self)
        self.window = TimerDisplay()

    def addSource(self, timerType, timerSource, timeStamp, duration):
        self.window.addSource(timerType, timerSource, timeStamp, duration)

    def onQuestComplete(self, questId):
        self.window.removeSource(TimerTypes.QUEST.value, questId)


class TimerDisplay(Window):

    def __init__(self):
        Window.__init__(self, desktop, position=(AnchorType.TOPRIGHT), size=(130, 63), draggable=True, visible=False, style=(styleDB.windowsDefaultStyle))
        self.sources = {}
        self.table = Datatable(self, maxCols=1)
        self.fitToContent()

    def removeSource(self, sourceType, timerSource):
        key = (
         sourceType, timerSource)
        if key in self.sources:
            self.sources[key].delete()
            del self.sources[key]
        if not self.sources:
            if self.visible:
                self.forceHide()

    def addSource(self, timerType, timerSource, timeStamp, duration):
        key = (
         timerType, timerSource)
        if key in self.sources:
            self.sources[key].timeStamp = timeStamp
            self.sources[key].duration = duration
        else:
            if timerType == TimerTypes.QUEST.value:
                try:
                    qdata = quest.questData[timerSource]
                    timerName = qdata.title
                except KeyError:
                    timerName = "Unknown"

            else:
                timerName = TimerTypes(timerType).name.title()
            timeSourceLbl = Label((self.table), text=timerName, position=(1, 10), style=(styleDB.blackLabelStyle))
            timeLabel = Label((self.table), text="- Time Left: ...", position=(1, 20), style=(styleDB.blackLabelStyle))
            self.table.add(timeSourceLbl)
            self.table.add(timeLabel)
            self.sources[key] = Timing(timerType, timerSource, timeStamp, duration, timeSourceLbl, timeLabel, self)
            self.sources[key].update(None)
            self.table.fitToContent()
        if not self.visible:
            self.forceUnHide()


timerDisplay = TimerControl()
