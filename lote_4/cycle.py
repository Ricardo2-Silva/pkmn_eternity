# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\interface\cycle.py
"""
Created on Sep 30, 2015

@author: Admin
"""
from client.control.gui import Window, Label
from client.data.utils.anchor import AnchorType
from client.game import desktop
from shared.service.cycle import dayNight, TimeOfDay, timeCycle, getNext
from twisted.internet import reactor
from client.data.system.background import BackgroundOption, BackgroundData
from client.control.system.background import backgroundController
from pyglet.gl.gl import GL_ONE_MINUS_SRC_ALPHA, GL_SRC_ALPHA, GL_DST_COLOR, GL_ZERO
from client.data.settings import gameSettings
from client.control.system.light import lightController
from client.control.gui.picture import Picture
from client.render.cache import textureCache
from client.data.gui import styleDB
import pyglet
from shared.container.constants import WeatherFlag
from client.data.container.map import mapContainer

class BgEffects(object):

    def __init__(self):
        self.effectBgs = {'cave':backgroundController.add((BackgroundData("cave", "cave",
           option=(BackgroundOption.BETWEEN + BackgroundOption.STRECH_IF_SMALLER),
           color=(45, 45, 45),
           blending=(
          GL_DST_COLOR, GL_ZERO),
           alpha=255)),
           visible=False), 
         'fog':backgroundController.add((BackgroundData("fog", "fog",
           option=(BackgroundOption.BETWEEN + BackgroundOption.STRECH_IF_SMALLER),
           color=(255, 255, 255),
           alpha=165)),
           visible=False)}
        self.effectEnable = {'cave':self.enableCave, 
         'fog':self.enableFog}
        self.effectDisable = {'cave':self.disableCave,  'fog':self.disableFog}
        self.currentEffects = []

    def enableCave(self, mapData):
        self.currentEffects.append("cave")
        self.effectBgs["cave"].show()
        lightController.turnOnLights(mapData)

    def disableCave(self, mapData):
        self.effectBgs["cave"].hide()
        lightController.turnOffLights(mapData)
        self.currentEffects.remove("cave")

    def enableFog(self, mapData):
        self.currentEffects.append("fog")
        self.effectBgs["fog"].show()

    def disableFog(self, mapData):
        self.effectBgs["fog"].hide()
        self.currentEffects.remove("fog")

    def mapCheck(self, mapData):
        for effect in self.currentEffects:
            self.effectDisable[effect](mapData)

        for effect in mapData.information.getEffects():
            self.effectEnable[effect](mapData)


bgEffects = BgEffects()

class BackgroundDayNight:

    def __init__(self):
        self.timeOfDayColor = {(TimeOfDay.MORNING): (252, 212, 64), 
         (TimeOfDay.AFTERNOON): (255, 255, 255), 
         (TimeOfDay.EVENING): (247, 176, 170), 
         (TimeOfDay.NIGHT): (62, 93, 216)}
        self.cycleBg = backgroundController.add(BackgroundData("timeOfDayCycle", "timeOfDayCycle",
          option=(BackgroundOption.BETWEEN + BackgroundOption.STRECH_IF_SMALLER),
          color=(0, 0, 0),
          blending=(
         GL_DST_COLOR, GL_ZERO),
          alpha=255),
          visible=False)
        self.inside = False

    def mapCheck(self, mapData):
        """ This check is done to make sure inside maps don't have night time unless specified """
        if not gameSettings.getAlwaysDay():
            if mapData.information.inside is True:
                if self.inside is True:
                    return
                self.deleteCycleBg()
                self.inside = True
            elif mapData.information.inside is False:
                self.addCycleBg(True)
                self.inside = False

    def addCycleBg(self, setTimeOfDay=False):
        if not gameSettings.getAlwaysDay():
            if not self.cycleBg.visible:
                self.cycleBg.show()
        if setTimeOfDay:
            self.setTimeOfDay(mapContainer.game_map)

    def deleteCycleBg(self):
        if not self.inside or not gameSettings.getAlwaysDay():
            self.cycleBg.hide()
        if dayNight.timeOfDay == TimeOfDay.NIGHT:
            if mapContainer.game_map:
                lightController.turnOffLights(mapContainer.game_map)

    def setTimeOfDay(self, mapData):
        if gameSettings.getAlwaysDay():
            return
        else:
            backgroundController.setTimeCycle(self.timeOfDayColor[dayNight.timeOfDay])
            if dayNight.timeOfDay == TimeOfDay.NIGHT:
                lightController.turnOnLights(mapData)
            else:
                lightController.turnOffLights(mapData)
        self.startTowardsNextDay()

    def simulateDays(self):
        if self.inside:
            return
        tODlist = TimeOfDay.order
        i = 0
        for x in range(0, 4):
            reactor.callLater(8 * x, backgroundController.adjustTimeCycle, self.timeOfDayColor[tODlist[i]], 7)
            i += 1

    def startTowardsNextDay(self):
        """ Begins looping towards the color of the next day """
        if gameSettings.getAlwaysDay():
            return
        timeOfDay = dayNight.getTimeOfDay()
        seconds = timeCycle.getTimeUntilNextStartHour(timeOfDay)
        backgroundController.adjustTimeCycle(self.timeOfDayColor[getNext(timeOfDay)], seconds)

    def convertColorTime(self, color1, color2, currentSeconds=6, totalSeconds=5555.0):
        """ """
        r, g, b = color1
        r2, g2, b2 = color2
        difference = (r2 - r, g2 - g, b2 - b)
        perThrough = currentSeconds / totalSeconds
        rgb = []
        i = 0
        for lc in difference:
            rgb.append(color1[i] + lc * perThrough)
            i += 1


bgDayNight = BackgroundDayNight()

class TimeWindow(Window):

    def __init__(self):
        self.timeOfDayText = {(TimeOfDay.MORNING): "Morning", 
         (TimeOfDay.AFTERNOON): "Afternoon", 
         (TimeOfDay.EVENING): "Evening", 
         (TimeOfDay.NIGHT): "Night"}
        Window.__init__(self, desktop, position=(AnchorType.TOPRIGHT), size=(92, 63), draggable=True, visible=False, style=(styleDB.timeWindowStyle))
        self.setMargins(0, 0, 0, 0)
        self.hoursToImg = {
         6: 1, 
         7: 2, 
         8: 3, 
         9: 4, 
         10: 5, 
         11: 6, 
         12: 7, 
         13: 7, 
         14: 8, 
         15: 9, 
         16: 10, 
         17: 11, 
         18: 12, 
         19: 13, 
         20: 14, 
         21: 15, 
         22: 16, 
         23: 17, 
         0: 17, 
         1: 18, 
         2: 19, 
         3: 20, 
         4: 21, 
         5: 22}
        self.bg = Picture(self, (textureCache.getGuiImage("clock/background")), position=(AnchorType.TOPLEFT))
        self.timeLabel = Label(self, text="Current Time", position=(1, 5), style=(styleDB.whiteLabelStyle))
        self.dayLabel = Label(self, text="Date", position=(1, 24), style=(styleDB.whiteLabelStyle))
        self.timeOfDay = Label(self, text="TimeOfDay", position=(1, 43), enableEvents=True, style=(styleDB.whiteLabelStyle))
        self.dayNightImage = Picture(self, picture=(textureCache.getGuiImage("clock/1")), position=(64,
                                                                                                    5))
        self.weatherImages = {(WeatherFlag.RAIN): (textureCache.getGuiImage("clock/raining")), 
         (WeatherFlag.SNOW): (textureCache.getGuiImage("clock/snowing")), 
         (WeatherFlag.NONE): (textureCache.getGuiImage("clock/neutralweather")), 
         (WeatherFlag.CLOUDY): (textureCache.getGuiImage("clock/cloudy")), 
         (WeatherFlag.THUNDERSTORM): (textureCache.getGuiImage("clock/storm")), 
         (WeatherFlag.SUNNY): (textureCache.getGuiImage("clock/sunny")), 
         (WeatherFlag.HEAVY_WIND): (textureCache.getGuiImage("clock/windy")), 
         (WeatherFlag.LIGHT_WIND): (textureCache.getGuiImage("clock/windy")), 
         (WeatherFlag.BREEZE): (textureCache.getGuiImage("clock/windy"))}
        self.weatherPicture = Picture(self, picture=(self.weatherImages[WeatherFlag.NONE]), position=(64,
                                                                                                      33), size=(25,
                                                                                                                 26), autosize=(False,
                                                                                                                                False))
        pyglet.clock.schedule_interval(self.setTime, 1)

    def setDayImage(self, hour):
        self.dayNightImage.setPicture(textureCache.getGuiImage("clock/{}".format(self.hoursToImg[int(hour)])))

    def updateWeather(self, weather):
        if weather in self.weatherImages:
            picture = self.weatherImages[weather]
        else:
            picture = self.weatherImages[WeatherFlag.NONE]
        self.weatherPicture.setPicture(picture)

    def setTimeOfDay(self):
        """ Tell what time in the day it is (Morning, Afternoon, Evening, Night) """
        timeOfDay = dayNight.getTimeOfDay()
        if self.timeOfDayText[timeOfDay] != self.timeOfDay.text:
            self.timeOfDay.text = self.timeOfDayText[timeOfDay]
            bgDayNight.startTowardsNextDay()

    def setTime(self, dt=None):
        """ Here we set the time of day only if it changes, then we update the day and time of day if applicable """
        dt = dayNight.getTime()
        if dt.strftime("%I:%M%p") != self.timeLabel.text:
            self.timeLabel.text = dt.strftime("%I:%M%p")
            self.setDayImage(dt.strftime("%H"))
            self.setDay()
            self.setTimeOfDay()

    def setDay(self):
        """ Tell what day in the week it is """
        dt = dayNight.getTime()
        if dt.strftime("%A") != self.dayLabel.text:
            self.dayLabel.text = dt.strftime("%A")


timeWindow = TimeWindow()
