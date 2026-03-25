# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: shared\service\cycle.py
"""
Created on Sep 30, 2015

@author: Admin
"""
import datetime
from twisted.internet import reactor

class TimeOfDay:
    MORNING = 1
    AFTERNOON = 2
    EVENING = 4
    NIGHT = 8
    DAY = 7
    ALL_TIMES = 15
    order = [
     MORNING, AFTERNOON, EVENING, NIGHT]
    textToInt = {
     'MORNING': MORNING, 
     'AFTERNOON': AFTERNOON, 
     'EVENING': EVENING, 
     'NIGHT': NIGHT, 
     'DAY': DAY, 
     'ALL_TIMES': ALL_TIMES}


def getNext(day):
    nextTOD = TimeOfDay.order.index(day)
    if TimeOfDay.order[nextTOD] == TimeOfDay.order[-1]:
        return TimeOfDay.order[0]
    else:
        return TimeOfDay.order[nextTOD + 1]


timeZone = datetime.timezone(-datetime.timedelta(hours=5))

class TimeCycle:

    def __init__(self):
        self.timeRanges = {(TimeOfDay.MORNING): [6, 7, 8, 9, 10, 11], 
         (TimeOfDay.AFTERNOON): [12, 13, 14, 15, 16, 17], 
         (TimeOfDay.EVENING): [18, 19, 20], 
         (TimeOfDay.NIGHT): [21, 22, 23, 0, 1, 2, 3, 4, 5]}
        self.colorRanges = {(TimeOfDay.MORNING): [], 
         (TimeOfDay.AFTERNOON): [], 
         (TimeOfDay.EVENING): [], 
         (TimeOfDay.NIGHT): []}

    def getTimeOfDay(self, hour):
        """ Takes the hour given and returns what kind of day type it is """
        for dayType, hourList in list(self.timeRanges.items()):
            if hour in hourList:
                return dayType

    def getNextStartHour(self, tOD):
        """ Gets the hour the next time of day begins """
        return self.timeRanges[getNext(tOD)][0]

    def getTimeUntilHour(self, hour):
        """ Gets time until specific hour in seconds """
        tomorrow = datetime.datetime.replace((datetime.datetime.now()), hour=hour, minute=0, second=0)
        delta = tomorrow - datetime.datetime.now()
        return delta.seconds

    def getTimeUntilNextStartHour(self, tOD):
        return self.getTimeUntilHour(self.getNextStartHour(tOD))


timeCycle = TimeCycle()

class DayNightCycle:

    def __init__(self):
        self.timeCycle = TimeCycle()
        self.timeOfDay = 0
        self.setTimeOfDay()
        reactor.callLater(60, self.setTimeOfDay)

    def getTimeOfDay(self):
        return self.timeOfDay

    def setTimeOfDay(self):
        self.timeOfDay = self.timeCycle.getTimeOfDay(datetime.datetime.now(timeZone).hour)

    def getTime(self):
        return datetime.datetime.now(timeZone)

    def isSunny(self):
        return self.timeOfDay != TimeOfDay.NIGHT or self.timeOfDay != TimeOfDay.EVENING

    def isDay(self):
        return bool(self.timeOfDay != TimeOfDay.NIGHT)

    def isEvening(self):
        return bool(self.timeOfDay == TimeOfDay.EVENING)

    def isNight(self):
        return bool(self.timeOfDay == TimeOfDay.NIGHT)

    def getTimeUntilNext(self):
        return


dayNight = DayNightCycle()
