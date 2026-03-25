# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\interface\login.py
import sys, time
from distutils.version import StrictVersion
import requests
from twisted.internet import threads
from client.control.events.event import eventManager
from client.control.gui import Button, Label, Header
from client.control.gui import Window, Textbox
from client.control.system.anims import FadeToOpacity
from client.game import desktop
from client.control.system.background import backgroundController
from client.data.DB import messageDB
from client.data.gui.button import TextboxType
from client.data.settings import gameSettings
import client.data.gui.styleDB as styleDB
from client.data.utils.anchor import AnchorType, Alignment
from client.control.system.sound import mixerController
from client.control.gui.picture import Picture, AnimatedPicture
from client.render.cache import textureCache
from shared.service.direction import directionService
from shared.container.constants import CreatureAction, RefPointType, VERSION
from client.control.gui.char import PokemonWidget
import random, pyglet
from client.control.gui.container import Container
from client.data.sprite import Sheet, setAnchorPoint
import math
from shared.service.cycle import dayNight
from client.control.system.patcher import patchHandler
from client.control.gui.checkbox import Checkbox

class AnnounceWindow(Window):

    def __init__(self, parent):
        self._group = parent._group
        Window.__init__(self, parent, size=(220, 100), position=(AnchorType.TOPRIGHTFIXED), style=(styleDB.windowsDefaultStyle), autosize=(False,
                                                                                                                                           True),
          draggable=False,
          visible=False)
        Header(self, text="News", minimize=False, close=True)
        self.push = False
        self.displayLabel = Label(self, position=(AnchorType.TOPLEFT), size=(200, 0), text="Unknown", multiline=True)

    def setOnTop(self):
        return

    def setActive(self):
        return

    def checkForAnnouncement(self):
        d = threads.deferToThread(self._getAnnouncePage)
        d.addCallback(self._successText)
        d.addErrback(self._failedToGet)
        return d

    def _successText(self, text):
        if text is False or text == "":
            return
        if not self.visible:
            self.show()
        self.displayLabel.text = text
        self.fitToContent()

    def _failedToGet(self, result):
        print("Failed to get announcement page", result.value)

    def _getAnnouncePage(self):
        response = requests.get("https://bugs.eternityrpg.net/news.txt", timeout=4)
        if response.status_code != 200:
            return False
        else:
            return response.text

    @property
    def group(self):
        return self._group


class Login:

    def __init__(self):
        self.active = False
        self._group = pyglet.graphics.Group()
        self.entireContainer = LoginContainer(self._group)
        self.window = LoginWindows(self.entireContainer)
        self.window.connectButton.addCallback("onMouseLeftClick", self.connectClick, False)
        self.window.quitButton.addCallback("onMouseLeftClick", self.exitMenu)
        self.window.createButton.addCallback("onMouseLeftClick", self.connectClick, True)
        self.window.mailTextbox.addCallback("onKeyReturn", self.connectReturn)
        self.window.passTextbox.addCallback("onKeyReturn", self.connectReturn)
        eventManager.registerListener(self)
        self.password = ""
        self.username = ""
        self.announceWindow = AnnounceWindow(self.entireContainer)

    def on_enter(self):
        self.active = True
        try:
            mixerController.playMusic("Pokemon Eternity - Title Screen ( SNIPPET ).mp3")
        except Exception as err:
            eventManager.notify("onNotificationMessage", "Notification", "An exception occurred with playing audio, please contact an administrator.")
            sys.stderr.write(str(err) + "\n")

        self.window.group.visible = True
        self.window.updateBackground()
        self.setConnectionButtonState(True)
        self.entireContainer.forceUnHide()
        self.window.start()
        self.announceWindow.checkForAnnouncement()
        backgroundController.hideBlackOut()

    def on_exit(self):
        self.active = False
        self.saveLogin()
        self.window.stop()
        self.window.group.visible = False
        self.entireContainer.forceHide()
        self.announceWindow.forceHide()
        self.window.destroyPokemon()
        backgroundController.blackOut()
        backgroundController.hideBlackOut()

    def infosChecking(self, username, password):
        passwordLen = len(password)
        usernameLen = len(username)
        if passwordLen < 3:
            eventManager.notify("onNotificationMessage", "Notification", messageDB["PASSWORD_SHORT"])
            return False
        else:
            if usernameLen < 6 or usernameLen > 32:
                eventManager.notify("onNotificationMessage", "Notification", messageDB["USER_LENGTH"])
                return False
            return True

    def connectClick(self, widget, x, y, modifiers, creation=False):
        self.connect(creation)

    def connectReturn(self, creation=False):
        self.connect(creation)

    def connect(self, creation=False):
        self.window.connectButton.disableEvents()
        self.window.createButton.disableEvents()
        username, password = self.window.getLoginInfos()
        if not self.infosChecking(username, password):
            self.setConnectionButtonState(True)
            return False
        eventManager.notify("onDisplayNotification", "Connection", "Connecting...")
        self.username = username
        self.password = password
        d = patchHandler.needsPatching()
        d.addCallback(self._patchResponse, creation)
        d.addErrback(self._errorInPatching, creation)

    def _errorInPatching(self, result, creation):
        print("Error getting patch:", result.getErrorMessage())
        eventManager.notify("onDisplayNotification", "Connection", "Patch server unavailable, attempting game connection.")
        self._connect(creation)

    def _patchResponse(self, needsPatching, creation):
        if needsPatching is True:
            from client.scene.patching import PatchingScene
            from client.scene.manager import sceneManager
            eventManager.notify("onHideNotification", "Connection")
            sceneManager.add("Patcher", PatchingScene())
            sceneManager.changeScene("Patcher")
        else:
            self._connect(creation)

    def _connect(self, creation):
        from client.control.net.login.handler import loginNetHandler
        loginNetHandler.loginToServer(self.username, self.password, creation)

    def exitMenu(self, widget, x, y, modifiers):
        eventManager.notify("onNotificationMessage", "Exit", "")

    def saveLogin(self):
        if self.password != gameSettings.getLoginInfos()[1] or self.username != gameSettings.getLoginInfos()[0]:
            gameSettings.setLoginInfos(self.username, self.password)

    def setConnectionButtonState(self, state):
        if state is True:
            if self.window.connectButton.isEventsEnabled() is False:
                self.window.connectButton.enableEvents()
                self.window.createButton.enableEvents()
        elif self.window.connectButton.isEventsEnabled() is True:
            self.window.connectButton.disableEvents()
            self.window.createButton.disableEvents()

    def onAllowConnectButton(self, action):
        if self.active:
            self.setConnectionButtonState(action)


class LoginContainer(Container):

    def __init__(self, group):
        self._group = group
        super().__init__(desktop, (0, 0), gameSettings.getScaledUIWindowResolution(), False, True, (False,
                                                                                                    False))
        self.push = False

    @property
    def group(self):
        return self._group


class LoginWindows(Window):

    def __init__(self, parent):
        gw, gh = gameSettings.getScaledUIWindowResolution()
        self._group = parent._group
        self.texture_mode = None
        self.entireContainer = parent
        self.setupBackground()
        Window.__init__(self, parent, size=(100, 100), position=(AnchorType.CENTER), style=(styleDB.windowsNoStyle), autosize=(True,
                                                                                                                               True),
          draggable=False)
        self.push = False
        self.setAutoFit()
        self.mailTextbox = Textbox(self, text=(gameSettings.getLoginInfos()[0]), maxLetters=100, position=(AnchorType.TOPCENTER),
          size=(178, 0),
          style=(styleDB.loginTextBoxStyle),
          scrollable=True)
        self.passTextbox = Textbox(self, text=(gameSettings.getLoginInfos()[1]), maxLetters=100, position=(AnchorType.TOPCENTER),
          size=(178, 0),
          type=(TextboxType.PASSWORD),
          style=(styleDB.loginTextBoxStyle),
          scrollable=True)
        self.rememberCheckbox = Checkbox(self, text="Remember Login", position=(75,
                                                                                54), style=(styleDB.loginCheckboxButtonStyle))
        self.rememberCheckbox.setSelected(gameSettings.canSavePassword())
        self.rememberCheckbox.addCallback("onMouseLeftClick", self.rememberPasswords)
        self.connectButton = Button(self, "Connect", position=(0, 75), style=(styleDB.blueButtonStyle), clickSound="ButtonSelect")
        self.createButton = Button(self, "Create", position=(70, 75), style=(styleDB.greenButtonStyle), clickSound="ButtonSelect")
        self.quitButton = Button(self, "Quit", position=(130, 75), size=(50, 0), autosize=(False,
                                                                                           True), style=(styleDB.redButtonStyle),
          clickSound="ButtonSelect")
        x, y = gw / 2 - self.width / 2, gh / 2 - self.height
        self.setPosition(x, y)
        self.logoTexture = textureCache.getImageFile("lib/system/logo.png", atlas=False)
        setAnchorPoint(self.logoTexture, RefPointType.BOTTOMCENTER)
        x, y = self.position
        self.logoPicture = Picture((self.entireContainer), position=(x + self.width / 2, y - self.logoTexture.height), picture=(self.logoTexture),
          refPointType=(RefPointType.BOTTOMCENTER))
        self.logoPicture.renderer.pictureSprite.batch = desktop.transparent
        patch_version = gameSettings.getCurrentPatchNumber()
        if patch_version > StrictVersion(VERSION):
            version = patch_version
        else:
            version = VERSION
        self.versionLabel = Label((self.entireContainer), style=(styleDB.whiteLabelStyle), position=(AnchorType.BOTTOMRIGHTFIXED), text=(str(version)),
          visible=True)
        print("OK")

    def setActive(self):
        return

    def setOnTop(self):
        return

    @property
    def group(self):
        return self._group

    def rememberPasswords(self, widget, x, y, modifiers):
        gameSettings.setSavePassword(str(widget.isSelected()))

    def updateBackground(self):
        if dayNight.isEvening():
            self.texture_mode = "sunset"
        else:
            if dayNight.isNight():
                self.texture_mode = "night"
            else:
                self.texture_mode = "day"
            if not self.stars:
                if dayNight.isNight():
                    self._createNightAccents()
                if dayNight.isNight():
                    cloud1_img = textureCache.getImageFile("lib/login/Login_Clouds_1_night.png")
                    cloud2_img = textureCache.getImageFile("lib/login/Login_Clouds_2_night.png")
            else:
                cloud1_img = textureCache.getImageFile("lib/login/Login_Clouds_1.png")
                cloud2_img = textureCache.getImageFile("lib/login/Login_Clouds_2.png")
        login_grass = textureCache.getImageFile(self.textures[self.texture_mode]["grass"])
        self.grassPicture.setPicture(login_grass)
        self.cloud1.setPicture(cloud1_img)
        self.cloud2.setPicture(cloud2_img)

    def _createNightAccents(self):
        width, height = gameSettings.getScaledUIWindowResolution()
        star_textures = [textureCache.getImageFile(f"lib/login/star{i}.png") for i in range(1, 3)]
        starcount = int(40 * height / 720)
        horizonHeight = height - 365
        for i in range(starcount):
            star = Picture(self.water, random.choice(star_textures))
            star.setPosition(random.randint(15, int(width - 15)), random.randint(0, int(horizonHeight - 25)))
            self.stars.append(star)

        self.moon = Picture(self.water, textureCache.getImageFile("lib/login/Login_night_moon.png", atlas=False))
        self.moon.setPosition(int(width * 0.3), int(height * 0.1))
        self.moon.renderer.pictureSprite.batch = desktop.transparent
        times = [
         1.0, 0.8, 0.6, 0.4, 0.3]
        random_flicks = random.randint(10, 20)
        for i in range(random_flicks):
            star = self.stars[i]
            picked = random.randint(100, 255)
            rand_time = random.choice(times)
            anim = FadeToOpacity(star.renderer.pictureSprite, picked, rand_time / 2)
            anim += FadeToOpacity((star.renderer.pictureSprite), 255, (rand_time / 2), startAlpha=picked)
            anim *= 0
            star.renderer.startAnim(anim)
            self.animatingStars.append(star)

    def setupBackground(self):
        self.max_pokemon = 5
        self.current_pokemon = []
        self.max_water = 1
        self.current_water = 0
        self.water = Container((self.entireContainer), position=(0, 0))
        self.groundBased = Container((self.entireContainer), position=(0, 0))
        width, height = gameSettings.getScaledUIWindowResolution()
        self.textures = {'night':{'horizon':"lib/login/Login_ocean_night[2]_(fast)_.png", 
          'grass':"lib/login/Login_Grass_night.png"}, 
         'sunset':{'horizon':"lib/login/Login_ocean_sunset[2]_(fast)_.png", 
          'grass':"lib/login/Login_Grass_sunset.png"}, 
         'day':{'horizon':"lib/login/Login_ocean[2]_(fast)_.png", 
          'grass':"lib/login/Login_Grass.png"}}
        if dayNight.isEvening():
            self.texture_mode = "sunset"
        else:
            if dayNight.isNight():
                self.texture_mode = "night"
            else:
                self.texture_mode = "day"
            horizonTexture = textureCache.getImageFile((self.textures[self.texture_mode]["horizon"]), atlas=False)
            sheet = Sheet(horizonTexture, (2, 1), 0.4)
            sheet.setGUIReferencePoint()
            self.waterHorizon = AnimatedPicture((self.water), sheet, size=(
             width, 0),
              position=(
             0, height),
              refPointType=(RefPointType.BOTTOMLEFT))
            self.animatingStars = []
            self.stars = []
            if dayNight.isNight():
                self._createNightAccents()
                cloud1_img = textureCache.getImageFile("lib/login/Login_Clouds_1_night.png", atlas=False)
                cloud2_img = textureCache.getImageFile("lib/login/Login_Clouds_2_night.png", atlas=False)
            else:
                cloud1_img = textureCache.getImageFile("lib/login/Login_Clouds_1.png", atlas=False)
                cloud2_img = textureCache.getImageFile("lib/login/Login_Clouds_2.png", atlas=False)
        self.cloud1 = Picture(self.water, cloud1_img)
        self.cloud1.setPosition(0, 0)
        self.cloud1.velocity = 0.008
        self.cloud2 = Picture(self.water, cloud2_img)
        self.cloud2.setPosition(0, int(height * 0.1))
        self.cloud2.velocity = 0.003
        login_grass = textureCache.getImageFile((self.textures[self.texture_mode]["grass"]), atlas=False)
        self.grassPicture = Picture((self.groundBased), position=(0, height - login_grass.height), size=(
         width if login_grass.width < width else 0, 0),
          picture=login_grass,
          refPointType=(RefPointType.BOTTOMLEFT))
        self.flying = [
         16, 17, 18, 21, 22, 41, 42]
        self.panCoords = (0, 3, 6, 9)

    def updateParse error at or near `POP_JUMP_IF_TRUE' instruction at offset 284_286

    def destroyPokemon(self):
        for widget in self.current_pokemon:
            widget.stopWalking()
            widget.destroy()

        self.current_pokemon.clear()

    def stop(self):
        pyglet.clock.unschedule(self.beginGeneratationRandomPokemon)
        self.waterHorizon.stopAnimation()
        for star in self.animatingStars:
            star.renderer.stopAnims()

    def start(self):
        self.current_pokemon = []
        self.waterHorizon.loopAnimation()
        pyglet.clock.schedule_interval(self.beginGeneratationRandomPokemon, 2)

    def beginGeneratationRandomPokemon(self, dt):
        if random.randint(1, 100) < 50:
            return
        if random.randint(1, 100) < 80:
            self._generatePokemon(random.randint(1, 151), directionService.RIGHT, False, False)
        else:
            if self.current_water >= self.max_water:
                return
            self._generatePokemon(random.choice([130, 131]), directionService.LEFT, False, True)

    def _generatePokemon(self, dexId, startDirection, flying, swimming):
        if len(self.current_pokemon) >= self.max_pokemon:
            return
        else:
            if swimming:
                self.current_water += 1
            else:
                x, y = gameSettings.getScaledUIWindowResolution()
                startPos = random.randint(10, 230)
                if swimming:
                    layer = self.water
                else:
                    layer = self.groundBased
                widget = PokemonWidget(layer, dexId, shadow=(False if flying else True))
                widget.swimming = False if not swimming else True
                if startDirection == directionService.RIGHT:
                    xPos = x
                    widget.setFacing(directionService.LEFT)
                    widget.originalDirection = directionService.LEFT
                else:
                    xPos = 0 - widget.width * 3
                    widget.setFacing(directionService.RIGHT)
                    widget.originalDirection = directionService.RIGHT
                if flying:
                    widget.flying = True
                else:
                    widget.setScale(3)
                    widget.flying = False
                if flying:
                    widget.setPosition(xPos, startPos)
                elif swimming:
                    widget.setPosition(xPos, y - 220)
                else:
                    widget.setPosition(xPos, y - startPos)
            widget.startWalking(0.15 if not flying else 0.05)
            widget.startTime = time.time()
            widget.makesStops = False
            widget.stopTime = 0
            if not flying or not swimming:
                if startPos >= 215:
                    widget.makesStops = True
        self.current_pokemon.append(widget)

    def getLoginInfos(self):
        return (
         self.mailTextbox.text, self.passTextbox.text)

    def forceHide(self):
        if self.visible:
            self.logoPicture.hide()
            self.water.hide()
            self.groundBased.hide()
            for star in self.stars:
                star.hide()

            if self.animatingStars:
                self.moon.hide()
            self.versionLabel.hide()
            Window.forceHide(self)

    def forceUnHide(self):
        for star in self.stars:
            star.show()

        self.water.show()
        self.groundBased.show()
        if self.animatingStars:
            self.moon.show()
        self.versionLabel.show()
        self.logoPicture.show()
        Window.forceUnHide(self)