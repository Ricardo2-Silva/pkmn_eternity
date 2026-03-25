# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\render\world\weather.py
"""
Created on Dec 17, 2015

@author: Admin
"""
from client.data.settings import gameSettings
from client.control.world.rain import Rain
from client.control.world.snow import Snow
from client.render.layer import weatherLayer

class WeatherRender:

    def __init__(self):
        self.angle = 265
        self.speed = 20
        self.intensity = 60
        self.enabled = True
        self.width = gameSettings.getWindowResolution()[0]
        self.height = gameSettings.getWindowResolution()[1]
        self.snow = Snow(self)
        self.rain = Rain(self)
        self.currentWeather = None
        weatherLayer.renderer = self

    def stopWeather(self):
        if self.currentWeather:
            self.currentWeather.stop()
        self.currentWeather = None

    def startWeather(self):
        if self.currentWeather:
            self.currentWeather.start()

    def setWeather(self, name, intensity):
        self.stopWeather()
        if name == "rain":
            self.currentWeather = self.rain
        elif name == "snow":
            self.currentWeather = self.snow
        else:
            self.currentWeather = None

    def update(self, dt):
        if self.enabled:
            if self.currentWeather:
                self.currentWeather.update(dt)

    def render(self):
        if self.enabled:
            if self.currentWeather:
                self.currentWeather.render()


weatherRender = WeatherRender()
