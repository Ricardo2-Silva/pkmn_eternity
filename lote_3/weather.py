# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\world\weather.py
"""
Created on 22 juil. 2011

@author: Kami
"""
from client.control.service.session import sessionService
from client.control.system.anims import ParallelAnims, FadeToOpacity, AnimCallable, Delay, FadeIn
from client.control.world.map import WeatherEffect, ShaderEffect
import math
from client.data.DB import mapDB
from client.data.sprite import Sheet
from client.data.world.animation import Animation
from client.data.world.map import EffectData
from client.control.system.background import backgroundController
from client.render.cache import textureCache
from client.render.shader.default_sprite import lightray_shader
from pyglet.gl import *
import random
from client.data.container.map import mapContainer
from client.control.events.event import eventManager
from twisted.internet import reactor
from client.data.system.background import BackgroundData, BackgroundOption
from client.control.system.sound import mixerController
from client.data.settings import gameSettings
import time
from client.render.world.weather import weatherRender
from client.interface.cycle import timeWindow
from shared.container.constants import WeatherFlag, RefPointType

class WindEffect(WeatherEffect):
    return


class CloudEffect(WeatherEffect):
    return


class FogEffect(WeatherEffect):
    return


class SunrayEffect(ShaderEffect):
    return


class Weather:

    def __init__(self, intensity=5, clouds=False, cloudThickness=0, rain=False, snow=False, lightning=False, fog=False, windy=False, variation=None, size_variation=None, sunrays=None):
        self.intensity = intensity
        self.clouds = clouds
        self.cloudThickness = cloudThickness
        self.rain = rain
        self.snow = snow
        self.lightning = lightning
        self.fog = fog
        self.windy = windy
        self.variation = variation
        self.size_variation = size_variation
        self.sunrays = sunrays


class WeatherController(object):
    __doc__ = " Stores backgrounds, renders them and allow effect on them. "

    def __init__(self):
        self.database = {(WeatherFlag.RAIN): (Weather(clouds=True, intensity=3, cloudThickness=30, rain=True, variation=["cloud1_[1]"], size_variation=(100,
                                                                                                           500))), 
         (WeatherFlag.THUNDERSTORM): (Weather(clouds=True, intensity=6, cloudThickness=70, rain=True, lightning=True, variation=["cloud2_[1]", "cloud1_[1]"], size_variation=(100,
                                                                                                                                         300))), 
         (WeatherFlag.SNOW): (Weather(clouds=True, intensity=3, cloudThickness=30, snow=True, variation=["cloud1_[1]"], size_variation=(100,
                                                                                                           500))), 
         (WeatherFlag.CLOUDY): (Weather(clouds=True, intensity=4, cloudThickness=100, variation=["cloud2_[1]"], size_variation=(300,
                                                                                                 500))), 
         (WeatherFlag.FOG): (Weather(intensity=12, fog=True)), 
         (WeatherFlag.HEAVY_WIND): (Weather(intensity=20, windy=True, variation=(50, 500))), 
         (WeatherFlag.LIGHT_WIND): (Weather(intensity=10, windy=True, variation=(50, 150))), 
         (WeatherFlag.BREEZE): (Weather(intensity=3, windy=True, variation=(50, 75))), 
         (WeatherFlag.SUNNY): (Weather(intensity=(random.randint(10, 15)), variation=(50, 75), sunrays=True))}
        self.effectPool = []
        self.activeEffects = []
        self.callLaters = []
        self.stopLightning = True
        eventManager.registerListener(self)
        thunderBg = BackgroundData("lightning", "lightning",
          option=(BackgroundOption.BETWEEN + BackgroundOption.STRECH_IF_SMALLER),
          color=(255, 255, 222),
          blending=(
         GL_DST_COLOR, GL_ONE_MINUS_SRC_ALPHA),
          alpha=0)
        backgroundController.add(thunderBg)
        self.fogBg = BackgroundData("fog_weather", "fog_weather",
          option=(BackgroundOption.IN_FRONT + BackgroundOption.STRECH_IF_SMALLER),
          color=(255, 255, 255),
          alpha=165)
        self.windySheet = None
        self.windDirection = 315
        self.weather = WeatherFlag.NONE
        self.ingame = False

    def getFromPool(self, effectType):
        for effect in list(self.effectPool):
            if isinstance(effect, effectType):
                new_effect = self.effectPool.pop(self.effectPool.index(effect))
                new_effect.show()
                return new_effect

        return

    def changingMap(self):
        self.ingame = True
        self.disableWeather()

    def mapCheck(self, mapInfo):
        return

    def setWeatherFromServer(self, mapId, weatherId, intensity, speed, duration, temporary):
        mapInfo = mapDB.getById(mapId)
        mapInfo.information.weatherType = weatherId
        self.setWeather(weatherId, mapInfo.information.inside)

    def setWeather(self, weather, inside):
        if self.weather == weather:
            return
        if gameSettings.getWeather():
            if inside:
                if self.weather:
                    self.disableWeather()
        else:
            self.disableWeather()
            self.weather = weather
            if weather != WeatherFlag.NONE:
                self.enableWeather()
            else:
                self.weather = weather
            timeWindow.updateWeather(self.weather)

    def getWeatherData(self, name):
        return self.database[name]

    def enableWeather(self):
        if self.ingame:
            self.startWeather()

    def disableWeather(self):
        while self.activeEffects:
            effect = self.activeEffects.pop(0)
            effect.hide()
            self.effectPool.append(effect)

        while self.callLaters:
            call = self.callLaters.pop(0)
            if call.active():
                call.cancel()

        if backgroundController.exists("fog_weather"):
            backgroundController.delete("fog_weather")
        self.stopLightning = True
        weatherRender.stopWeather()
        mixerController.stopRain()
        self.weather = None

    def startWeather(self):
        if self.weather:
            weatherData = self.getWeatherData(self.weather)
            if weatherData.clouds:
                self.addClouds(weatherData.intensity * 2, weatherData.variation, weatherData.cloudThickness, weatherData.size_variation)
            if weatherData.rain:
                weatherRender.setWeather("rain", weatherData.intensity)
                mixerController.playRain()
            if weatherData.snow:
                weatherRender.setWeather("snow", weatherData.intensity)
            if weatherData.lightning:
                self.stopLightning = False
                self.flashLightning()
            else:
                self.stopLightning = True
            if weatherData.sunrays:
                self.addSunray(weatherData.intensity, 2)
            if weatherData.fog:
                bg = backgroundController.add(self.fogBg)
                self.addFogList(weatherData.intensity * 3, ('fog1_[1]', 'fog2_[1]',
                                                            'fog3_[1]'))
            else:
                if backgroundController.exists("fog_weather"):
                    backgroundController.delete(self.fogBg)
            if weatherData.windy:
                if not self.windySheet:
                    self.windySheet = Sheet(textureCache.getImageFile("lib/effects/wind_02.png", atlas=False), frames=(1,
                                                                                                                       18),
                      referencePoint=(RefPointType.BOTTOMCENTER))
                self.addWind(weatherData.intensity, weatherData.variation)
            weatherRender.startWeather()

    def addClouds(self, amount, filename, thickness=60, size_variation=(100, 500)):
        effect_count = sum(isinstance(i, CloudEffect) for i in self.activeEffects)
        for i in range(amount - effect_count):
            if len(filename) == 1:
                new_filename = filename[0]
            else:
                new_filename = random.choices(filename, weights=(2, 1))[0]
            self.generateCloud(new_filename, thickness, size_variation)

    def addFogList(self, amount, filename_list):
        effect_count = sum(isinstance(i, FogEffect) for i in self.activeEffects)
        for i in range(amount - effect_count):
            self.callLaters.append(reactor.callLater(i, self.generateFogCloud, random.choice(filename_list)))

    def flashLightning(self):
        if not self.stopLightning:
            cb = backgroundController.fadeInAndOut("lightning", 0.1, 0.3, 80, 0)
            cb.addCallback(self.removeLightning)

    def addWind(self, amount, variation):
        effect_count = sum(isinstance(i, WindEffect) for i in self.activeEffects)
        for i in range(amount - effect_count):
            self.callLaters.append(reactor.callLater(i * 2, self.generateWind, "wind_02", variation))

    def addSunray(self, amount, variation):
        effect_count = sum(isinstance(i, SunrayEffect) for i in self.activeEffects)
        for i in range(amount - effect_count):
            self.callLaters.append(reactor.callLater(i * 2, self.generateSunray, "wind_02", variation))

    def generateSunray(self, filename, variation):
        """Generates a moving particle that can rotate, fade, and shrink as well as scroll"""
        x, y = mapContainer.getMapSize()
        effect_x, effect_y = random.randint(0, x), random.randint(0, y)
        effect = self.getFromPool(SunrayEffect)
        if not effect:
            effect = SunrayEffect(EffectData("lib/effects/LightBeam_01.png", position=(effect_x, effect_y), refPointType=(RefPointType.BOTTOMCENTER)))
            effect.renderer.setShader(lightray_shader)
            effect.setAlpha(254)
        else:
            effect.setPosition(effect_x, effect_y)
        pos = effect.getPosition()
        self.activeEffects.append(effect)

    def removeLightning(self, result):
        if not self.stopLightning:
            self.callLaters.append(reactor.callLater(random.randint(1, 20), self.flashLightning))

    def generateFogCloud(self, filename):
        """Generates a moving particle that can rotate, fade, and shrink as well as scroll"""
        x, y = mapContainer.getMapSize()
        effect = self.getFromPool(FogEffect)
        if not effect:
            effect = FogEffect(EffectData(filename, (
             random.randint(0, x), random.randint(0, y)),
              refPointType=(RefPointType.CENTER)))
        effect.setRotation(random.randint(0, 315))
        effect.setAlpha(0)
        effect.fadeTo(random.randint(3, 10), 254)
        w, h = effect.renderer.getSize()
        reduction = random.randint(5, 100) / 100.0
        effect.setSize(int(w * reduction), h * reduction)
        pos = effect.getPosition()
        life = random.randint(30, 60)
        new_x = pos[0] + x * math.cos(math.radians(self.windDirection))
        new_y = pos[1] + y * math.sin(math.radians(self.windDirection))
        move_anim = effect.moveTo(life, new_x, new_y)
        move_anim += AnimCallable(self._resetFog, effect)
        self.activeEffects.append(effect)

    def generateWind(self, filename, variation):
        """Generates a moving particle that can rotate, fade, and shrink as well as scroll"""
        x, y = mapContainer.getMapSize()
        effect_x, effect_y = random.randint(0, x), random.randint(0, y)
        effect = self.getFromPool(WindEffect)
        if not effect:
            effect = WindEffect(EffectData((self.windySheet), (
             effect_x, effect_y),
              refPointType=(RefPointType.BOTTOMCENTER),
              animation=Animation(delay=0.145, duration=0)))
        effect.setAlpha(0)
        effect.renderer._startTransparency()
        effect.renderer.stopAnims()
        anim = FadeIn(effect.renderer.sprite, 0.1)
        anim += Delay(2.61)
        anim += FadeToOpacity((effect.renderer.sprite), 0, 0.1, startAlpha=255)
        anim += AnimCallable(self.resetWind, effect)
        effect.startAnim(anim)
        w, h = effect.renderer.getSize()
        reduction = (random.randint)(*variation) / 100.0
        effect.setSize(int(w * reduction), int(h * reduction))
        pos = effect.getPosition()
        self.activeEffects.append(effect)

    def resetWind(self, effect):
        x, y = mapContainer.getMapSize()
        effect.setAlpha(0)
        effect.renderer._startTransparency()
        effect.renderer.stopAnims()
        anim = FadeIn(effect.renderer.sprite, 0.5)
        anim += Delay(2.61)
        anim += FadeToOpacity((effect.renderer.sprite), 0, 0.1, startAlpha=255)
        anim += AnimCallable(self.resetWind, effect)
        effect.startAnim(anim)
        effect.setPosition(random.randint(0, x), random.randint(0, y))
        life = random.randint(1, 2)
        pos = effect.getPosition()

    def generateCloud(self, filename, thickness, size_variation):
        """Generates a moving particle that can rotate, fade, and shrink as well as scroll"""
        x, y = mapContainer.getMapSize()
        effect = self.getFromPool(CloudEffect)
        if not effect:
            effect = CloudEffect(EffectData(filename, (
             random.randint(0, x), random.randint(0, y)),
              refPointType=(RefPointType.CENTER),
              renderingOrder=(-1)))
        else:
            if effect.data.fileId != filename:
                effect.updateTexture(filename)
        effect.setColor(0, 0, 0)
        effect.setRotation(random.randint(0, 315))
        effect.setAlpha(20)
        effect.fadeTo(random.randint(3, 10), random.randint(thickness - 10, thickness + 10))
        w, h = effect.renderer.getSize()
        reduction = (random.randint)(*size_variation) / 100.0
        effect.setSize(int(w * reduction), int(h * reduction))
        pos = effect.getPosition()
        life = random.randint(30, 60)
        move_anim = effect.moveTo(life, pos[0] + (x - pos[0]) * math.cos(math.radians(self.windDirection)), pos[1] + (y - pos[1]) * math.sin(math.radians(self.windDirection)))
        move_anim += AnimCallable(self.resetCloud, effect, thickness)
        self.activeEffects.append(effect)

    def _resetFog(self, effect):
        x, y = mapContainer.getMapSize()
        effect.renderer.stopAnims()
        effect.setPosition(random.randint(-100, x), random.randint(-200, y))
        effect.setAlpha(0)
        effect.fadeTo(random.randint(3, 10), 254)
        life = random.randint(30, 60)
        pos = effect.getPosition()
        new_x = pos[0] + (x - pos[0]) * math.cos(math.radians(self.windDirection))
        new_y = pos[1] + (y - pos[1]) * math.sin(math.radians(self.windDirection))
        move_anim = effect.moveTo(life, new_x, new_y)
        move_anim += AnimCallable(self._resetFog, effect)

    def resetCloud(self, effect, thickness):
        x, y = mapContainer.getMapSize()
        effect.setAlpha(0)
        effect.setPosition(random.randint(0, x), random.randint(0, y))
        effect.fadeTo(random.randint(3, 10), thickness)
        life = random.randint(30, 60)
        pos = effect.getPosition()
        move_anim = effect.moveTo(life, pos[0] + x * math.cos(math.radians(self.windDirection)), math.sin(math.radians(self.windDirection)) * y + pos[1])
        move_anim += AnimCallable(self.resetCloud, effect, thickness)


weatherController = WeatherController()
