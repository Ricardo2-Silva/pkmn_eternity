# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\interface\settings.py
"""
Created on Sep 8, 2011

@author: Ragnarok
"""
from client.control.gui import Window, Tabs, DropDown, Button, Checkbox, Label, Textbox, ScrollableContainer, Datatable, Slider, Title, Header
from client.game import desktop
from client.data.gui import styleDB
from client.data.settings import gameSettings, restrictedKeys, defaultKeys
from client.control.events.event import eventManager
from client.interface.hotbar import hotbar
from client.interface.notification import confirmWindow
from shared.container.constants import PMSettings, WeatherFlag
from client.data.utils.anchor import AnchorType
from client.data.skins import skinDB
from client.control.system.sound import mixerController
from pyglet.window.key import symbol_string
from client.interface.cycle import bgDayNight
from client.control.world.weather import weatherController
import pyglet
from operator import attrgetter

class Settings:

    def __init__(self):
        self.window = SettingsWindow()
        eventManager.registerListener(self)


class VideoSettings:
    requiresRestart = False

    def __init__(self, videoWindow):
        self.window = videoWindow
        self.tabButton = videoWindow.tabControl.addTab("Video")
        self.tabButton.addCallback("onMouseLeftClick", (lambda widget, x, y, modifiers: self.showTab()))
        self.screenLbl = Label(videoWindow, position=(0, 0), text="Screen Resolution: 0x0", visible=False)
        self.resSlider = Slider(videoWindow, position=(0, 20), size=(240, 0), visible=False)
        self.resSlider.addCallback("onValueChange", self.showValue)
        self.fullScreenBox = Checkbox(videoWindow, position=(0, 60), text="Fullscreen Mode", visible=False)
        self.mouseBox = Checkbox(videoWindow, position=(0, 120), text="Mouse Hardware Acceleration", visible=False)
        self.validResolutions = []
        display = pyglet.canvas.get_display()
        screen = display.get_default_screen()
        modes = list(reversed(sorted((screen.get_modes()), key=(attrgetter("width")))))
        try:
            highest_refresh_rate = max(modes, key=(lambda screen: screen.rate)).rate
        except:
            highest_refresh_rate = 60

        for mode in modes:
            if not mode.rate < highest_refresh_rate:
                if not mode.width < 1024:
                    if mode.scaling != 0:
                        continue
                    if mode in self.validResolutions:
                        continue
                    self.validResolutions.append(mode)

        for value in sorted((self.validResolutions), key=(lambda x: (
         x.width, x.height))):
            self.resSlider.addValue(value)

    def _verifyFullscreenLock(self):
        if self.fullScreenBox.isSelected():
            if self.resSlider.isEventsEnabled():
                self.resSlider.disableEvents()
        elif not self.resSlider.isEventsEnabled():
            self.resSlider.enableEvents()

    def _fullscreenToggled(self, widget, x, y, modifiers):
        self._verifyFullscreenLock()

    def findMode(self, width, height):
        """ Ensure a proper resolution is pulled from config. """
        for mode in self.validResolutions:
            if mode.width == width:
                if mode.height == height:
                    return mode

        return

    def showValue(self, mode):
        self.screenLbl.text = f"Screen Resolution: {mode.width}x{mode.height}"

    def testVideo(self):
        resolution = self.resSlider.value

    def showTab(self):
        if self.window.currentTab != self:
            self.window.currentTab.hide()
            self.show()
            self.window.currentTab = self

    def show(self):
        self.screenLbl.show()
        self.fullScreenBox.show()
        self.resSlider.show()
        self.mouseBox.show()

    def hide(self):
        self.screenLbl.hide()
        self.fullScreenBox.hide()
        self.resSlider.hide()
        self.mouseBox.hide()

    def load(self):
        mode = gameSettings.getFullscreen()
        self.fullScreenBox.setSelected(bool(mode))
        width, height = gameSettings.getWindowResolution()
        mode = self.findMode(width, height)
        if mode:
            self.resSlider.value = mode
        self.screenLbl.text = f"Screen Resolution: {width}x{height}"
        self.mouseBox.setSelected(bool(gameSettings.getCursorAcceleration()))

    def save(self):
        requiresRestart = False
        resolution = self.resSlider.value
        fullscreen = self.fullScreenBox.isSelected()
        if fullscreen:
            display = pyglet.canvas.get_display()
            screen = display.get_default_screen()
            if (
             screen.width, screen.height) != gameSettings.getWindowResolution():
                gameSettings.config["Screen"]["height"] = str(screen.height)
                gameSettings.config["Screen"]["width"] = str(screen.width)
                requiresRestart = True
        elif resolution:
            pass
        if (resolution.width, resolution.height) != gameSettings.getWindowResolution():
            gameSettings.config["Screen"]["height"] = str(resolution.height)
            gameSettings.config["Screen"]["width"] = str(resolution.width)
            requiresRestart = True
        if gameSettings.config.getboolean("Screen", "fullscreen") != fullscreen:
            gameSettings.config["Screen"]["fullscreen"] = str(fullscreen)
            requiresRestart = True
        value = int(self.mouseBox.isSelected())
        if gameSettings.config.getint("Screen", "mouse") != value:
            gameSettings.config["Screen"]["mouse"] = str(value)
            requiresRestart = True
        return requiresRestart


class UISettings:

    def __init__(self, window):
        self.window = window
        self.pmSettings = None
        self.currentSkin = None
        self.tabButton = window.tabControl.addTab("UI")
        self.tabButton.addCallback("onMouseLeftClick", (lambda widget, x, y, modifiers: self.showTab()))
        self.pmLbl = Label(window, position=(0, 0), text="Show PM Box:", visible=False)
        self.dropDown = DropDown(window, position=(5, 15), size=(100, 0), visible=False, style=(styleDB.dropdownButtonStyle))
        self.skinLbl = Label(window, position=(115, 0), text="Current Skin:", visible=False)
        self.skinDropDown = DropDown(window, position=(120, 15), size=(100, 0), visible=False, style=(styleDB.dropdownButtonStyle))
        self.hotbarLockBox = Checkbox(window, position=(0, 50), text="Lock Hotbar Ends", visible=False)
        self.hotbarRecallBox = Checkbox(window, position=(0, 75), text="Hotbar Can Recall", visible=False)
        self.quickCastBox = Checkbox(window, position=(0, 100), text="Quick Cast", visible=False)
        never = Button((self.dropDown), text="Never Show", style=(styleDB.dropdownButtonStyle))
        never.optionData = PMSettings.NONE
        never.addCallback("onMouseLeftClick", self.selectPM)
        always = Button((self.dropDown), text="Always Show", style=(styleDB.dropdownButtonStyle))
        always.optionData = PMSettings.ALL
        always.addCallback("onMouseLeftClick", self.selectPM)
        friendsOnly = Button((self.dropDown), text="Friends Only", style=(styleDB.dropdownButtonStyle))
        friendsOnly.optionData = PMSettings.FRIENDS
        friendsOnly.addCallback("onMouseLeftClick", self.selectPM)
        self.dropDown.addOption(never)
        self.dropDown.addOption(always)
        self.dropDown.addOption(friendsOnly)

    def loadSkins(self):
        self.currentSkin = gameSettings.getCurrentSkin()
        self.skinDropDown.emptyAndDestroy()
        for skin in skinDB.skins:
            skinButton = Button((self.skinDropDown), text=skin, style=(styleDB.dropdownButtonStyle))
            skinButton.addCallback("onMouseLeftClick", self.selectSkin)
            self.skinDropDown.addOption(skinButton)

        for widget in self.skinDropDown.getOptions():
            if widget.text == self.currentSkin:
                self.skinDropDown.setOption(widget)

    def selectSkin(self, widget, x, y, modifiers):
        self.currentSkin = widget.text

    def selectPM(self, widget, x, y, modifiers):
        self.pmSettings = widget.optionData

    def showTab(self):
        if self.window.currentTab != self:
            self.window.currentTab.hide()
            self.show()
            self.window.currentTab = self

    def show(self):
        self.pmLbl.show()
        self.dropDown.show()
        self.dropDown.startsVisible = True
        self.skinLbl.show()
        self.skinDropDown.show()
        self.skinDropDown.startsVisible = True
        self.hotbarRecallBox.show()
        self.hotbarLockBox.show()
        self.quickCastBox.show()

    def hide(self):
        self.pmLbl.hide()
        self.dropDown.hide()
        self.dropDown.startsVisible = False
        self.skinLbl.hide()
        self.skinDropDown.hide()
        self.skinDropDown.startsVisible = False
        self.hotbarRecallBox.hide()
        self.hotbarLockBox.hide()
        self.quickCastBox.hide()

    def loadPM(self):
        self.pmSettings = gameSettings.getPM()
        for widget in self.dropDown.getOptions():
            if widget.optionData == self.pmSettings:
                self.dropDown.setOption(widget)

    def load(self):
        self.loadPM()
        self.loadSkins()
        self.hotbarLockBox.setSelected(bool(gameSettings.getHotbarLock()))
        self.hotbarRecallBox.setSelected(bool(gameSettings.getHotbarRecall()))
        self.quickCastBox.setSelected(bool(gameSettings.getQuickCast()))

    def save(self):
        requiresRestart = False
        gameSettings["Game"]["pm"] = str(int(self.pmSettings))
        gameSettings["Game"]["hotbarlock"] = str(int(self.hotbarLockBox.isSelected()))
        gameSettings["Game"]["hotbar_recall"] = str(self.hotbarRecallBox.isSelected())
        gameSettings["Game"]["quick_cast"] = str(self.quickCastBox.isSelected())
        return requiresRestart


class GameSettings:

    def __init__(self, window):
        self.window = window
        self.selectionMode = 0
        self.selectionLabel = Label(window, position=(0, 0), text="Auto-selections:", visible=False)
        self.selectionDropdown = DropDown(window, position=(5, 15), size=(100, 0), visible=False, style=(styleDB.dropdownButtonStyle))
        selectionNever = Button((self.selectionDropdown), text="Never", style=(styleDB.dropdownButtonStyle))
        selectionNever.selectionMode = 0
        selectionNever.addCallback("onMouseLeftClick", self.autoSelectionClick)
        selectionStart = Button((self.selectionDropdown), text="On Battle Start (Pokemon)", style=(styleDB.dropdownButtonStyle))
        selectionStart.selectionMode = 1
        selectionStart.addCallback("onMouseLeftClick", self.autoSelectionClick)
        selectionEnd = Button((self.selectionDropdown), text="On Battle End (Trainer)", style=(styleDB.dropdownButtonStyle))
        selectionEnd.selectionMode = 2
        selectionEnd.addCallback("onMouseLeftClick", self.autoSelectionClick)
        selectionBoth = Button((self.selectionDropdown), text="On Start and End", style=(styleDB.dropdownButtonStyle))
        selectionBoth.selectionMode = 3
        selectionBoth.addCallback("onMouseLeftClick", self.autoSelectionClick)
        self.selectionDropdown.addOption(selectionNever)
        self.selectionDropdown.addOption(selectionStart)
        self.selectionDropdown.addOption(selectionEnd)
        self.selectionDropdown.addOption(selectionBoth)
        self.tabButton = window.tabControl.addTab("Game")
        self.tabButton.addCallback("onMouseLeftClick", (lambda widget, x, y, modifiers: self.showTab()))
        self.weatherEnableBox = Checkbox(window, position=(0, 50), text="Weather", visible=False)
        self.barBox = Checkbox(window, position=(0, 75), text="Show HP Bars", visible=False)
        self.namesBox = Checkbox(window, position=(0, 100), text="Show Names", visible=False)
        self.useChunks = Checkbox(window, position=(0, 125), text="Chunk Loading", visible=False)
        self.cameraBox = Checkbox(window, position=(115, 50), text="Slow Camera", visible=False)
        self.alwaysDayBox = Checkbox(window, position=(115, 75), text="Always Day", visible=False)
        self.skipRename = Checkbox(window, position=(115, 100), text="Skip Renaming", visible=False)
        self.extraPreload = Checkbox(window, position=(115, 125), text="Extra Preload", visible=False)
        self.targetIndicator = Checkbox(window, position=(0, 150), text="Target Indicator", visible=False)

    def autoSelectionClick(self, widget, x, y, modifiers):
        self.selectionMode = widget.selectionMode

    def showTab(self):
        if self.window.currentTab != self:
            self.window.currentTab.hide()
            self.show()
            self.window.currentTab = self

    def show(self):
        self.weatherEnableBox.show()
        self.barBox.show()
        self.namesBox.show()
        self.selectionLabel.show()
        self.selectionDropdown.show()
        self.selectionDropdown.startsVisible = True
        self.alwaysDayBox.show()
        self.useChunks.show()
        self.cameraBox.show()
        self.skipRename.show()
        self.extraPreload.show()
        self.targetIndicator.show()

    def hide(self):
        self.weatherEnableBox.hide()
        self.barBox.hide()
        self.namesBox.hide()
        self.alwaysDayBox.hide()
        self.useChunks.hide()
        self.cameraBox.hide()
        self.skipRename.hide()
        self.extraPreload.hide()
        self.targetIndicator.hide()
        self.selectionLabel.hide()
        self.selectionDropdown.hide()
        self.selectionDropdown.startsVisible = False

    def load(self):
        for widget in self.selectionDropdown.getOptions():
            if widget.selectionMode == gameSettings.getAutoSelectionControl():
                self.selectionDropdown.setOption(widget)
                break

        self.barBox.setSelected(bool(gameSettings.getHPBars()))
        self.namesBox.setSelected(bool(gameSettings.getAlwaysNames()))
        self.weatherEnableBox.setSelected(bool(gameSettings.getWeather()))
        self.alwaysDayBox.setSelected(bool(gameSettings.getAlwaysDay()))
        self.useChunks.setSelected(bool(gameSettings.getGameChunks()))
        self.cameraBox.setSelected(bool(gameSettings.getCameraSpeed()))
        self.skipRename.setSelected(bool(gameSettings.getSkipRename()))
        self.extraPreload.setSelected(bool(gameSettings.getAdditionalPreload()))
        self.targetIndicator.setSelected(bool(gameSettings.getTargetIndicator()))

    def saveAlwaysDay(self):
        bl = int(self.alwaysDayBox.isSelected())
        if gameSettings.getAlwaysDay() != bl:
            gameSettings["Game"]["alwaysday"] = str(bl)
            if bl == 0:
                bgDayNight.addCycleBg(setTimeOfDay=True)
            elif bl == 1:
                bgDayNight.deleteCycleBg()
        return False

    def saveWeather(self):
        bl = int(self.weatherEnableBox.isSelected())
        if gameSettings.getWeather() != bl:
            gameSettings["Game"]["weather"] = str(bl)
            if bl == 0:
                weatherController.disableWeather()
            elif bl == 1:
                weatherController.weather = WeatherFlag.THUNDERSTORM
                weatherController.enableWeather()
        return False

    def save(self):
        requiresRestart = False
        gameSettings["Game"]["hpbars"] = str(int(self.barBox.isSelected()))
        gameSettings["Game"]["names"] = str(int(self.namesBox.isSelected()))
        gameSettings["Game"]["camera_slow"] = str(int(self.cameraBox.isSelected()))
        gameSettings["Game"]["skip_rename"] = str(int(self.skipRename.isSelected()))
        gameSettings["Game"]["target_indicator"] = str(self.targetIndicator.isSelected())
        self.saveAlwaysDay()
        self.saveWeather()
        from client.control.camera import worldCamera
        worldCamera.setCameraConfig()
        if self.useChunks.isSelected() != gameSettings.getGameChunks():
            requiresRestart = True
            gameSettings["Game"]["use_chunks"] = str(self.useChunks.isSelected())
        if self.extraPreload.isSelected() != gameSettings.getAdditionalPreload():
            requiresRestart = True
            gameSettings["Game"]["preload_extra"] = str(self.extraPreload.isSelected())
        gameSettings["Game"]["auto_selection"] = str(self.selectionMode)
        return requiresRestart


class SoundSettings:

    def __init__(self, window):
        self.window = window
        numbers = [i for i in range(101)]
        self.tabButton = window.tabControl.addTab("Sound")
        self.tabButton.addCallback("onMouseLeftClick", (lambda widget, x, y, modifiers: self.showTab()))
        self.effectLbl = Label(window, position=(0, 0), visible=False)
        self.effectSlider = Slider(window, position=(0, 15), size=(230, 0), visible=False)
        self.effectSlider.addCallback("onValueChange", self.effectChanged)
        (self.effectSlider.setValues)(*numbers)
        self.bgmLbl = Label(window, position=(0, 35), visible=False)
        self.bgmSlider = Slider(window, position=(0, 50), size=(230, 0), visible=False)
        self.bgmSlider.addCallback("onValueChange", self.bgmChanged)
        (self.bgmSlider.setValues)(*numbers)
        self.battleBgmLbl = Label(window, position=(0, 75), visible=False)
        self.battleBgmSlider = Slider(window, position=(0, 90), size=(230, 0), visible=False)
        self.battleBgmSlider.addCallback("onValueChange", self.battleBgmChanged)
        (self.battleBgmSlider.setValues)(*numbers)
        self.guiLbl = Label(window, position=(0, 115), visible=False)
        self.guiSlider = Slider(window, position=(0, 130), size=(230, 0), visible=False)
        self.guiSlider.addCallback("onValueChange", self.guiChanged)
        (self.guiSlider.setValues)(*numbers)
        self.environmentLbl = Label(window, position=(0, 155), visible=False)
        self.environmentSlider = Slider(window, position=(0, 170), size=(230, 0), visible=False)
        self.environmentSlider.addCallback("onValueChange", self.environmentChanged)
        (self.environmentSlider.setValues)(*numbers)

    def environmentChanged(self, value):
        self.environmentLbl.text = f"Environmental Effects: {value}%"
        mixerController.environmentChannel.volume = value / 100

    def effectChanged(self, value):
        self.effectLbl.text = f"Sound Effects: {value}%"
        mixerController.effectChannel.volume = value / 100

    def bgmChanged(self, value):
        self.bgmLbl.text = f"Background Music: {value}%"
        mixerController.updateMusicVolume(value / 100)

    def guiChanged(self, value):
        self.guiLbl.text = f"GUI Sound: {value}%"
        mixerController.guiChannel.volume = value / 1000

    def battleBgmChanged(self, value):
        self.battleBgmLbl.text = f"Battle Music: {value}%"
        mixerController.updateBattleVolume(value / 100)

    def showTab(self):
        if self.window.currentTab != self:
            self.window.currentTab.hide()
            self.show()
            self.window.currentTab = self

    def show(self):
        self.effectLbl.show()
        self.effectSlider.show()
        self.battleBgmLbl.show()
        self.battleBgmSlider.show()
        self.bgmLbl.show()
        self.bgmSlider.show()
        self.guiLbl.show()
        self.guiSlider.show()
        self.environmentLbl.show()
        self.environmentSlider.show()

    def hide(self):
        self.effectLbl.hide()
        self.effectSlider.hide()
        self.battleBgmLbl.hide()
        self.battleBgmSlider.hide()
        self.bgmLbl.hide()
        self.bgmSlider.hide()
        self.guiLbl.hide()
        self.guiSlider.hide()
        self.environmentLbl.hide()
        self.environmentSlider.hide()

    def load(self):
        number = gameSettings.getBgmVolume()
        number = int(number)
        self.bgmLbl.text = f"Background Music: {number}%"
        self.bgmSlider.value = int(number)
        number = gameSettings.getEffectVolume()
        number = int(number)
        self.effectLbl.text = f"Sound Effects: {number}%"
        self.effectSlider.value = int(number)
        number = gameSettings.getGuiVolume()
        number = int(number)
        self.guiLbl.text = f"Gui Sounds: {number}%"
        self.guiSlider.value = int(number)
        number = gameSettings.getEnvironmentVolume()
        number = int(number)
        self.environmentLbl.text = f"Environmental Sounds: {number}%"
        self.environmentSlider.value = int(number)
        number = gameSettings.getBattleBgmVolume()
        number = int(number)
        self.battleBgmLbl.text = f"Battle Music: {number}%"
        self.battleBgmSlider.value = int(number)

    def save(self):
        gameSettings["Audio"]["effect_volume"] = str(self.effectSlider.value)
        gameSettings["Audio"]["bgm_volume"] = str(self.bgmSlider.value)
        gameSettings["Audio"]["gui_volume"] = str(self.guiSlider.value)
        gameSettings["Audio"]["environment_volume"] = str(self.environmentSlider.value)
        gameSettings["Audio"]["battle_volume"] = str(self.battleBgmSlider.value)
        return False


class ControlTextbox(Textbox):

    def __init__(self, settings, parent, keyTag, **kwargs):
        self.settings = settings
        self.keyTag = keyTag
        self.currentKey = gameSettings.getKey(keyTag)
        (Textbox.__init__)(self, parent, size=(80, 15), text=self.get_key_string(self.currentKey), **kwargs)
        self.addCallback("onGainFocus", self.clearKey)
        self.addCallback("onLostFocus", self.resetKey)

    @staticmethod
    def get_key_string(symbol):
        return symbol_string(symbol).lstrip("_")

    def clearKey(self, widget):
        self.text = "<press key>"

    def resetKey(self, widget):
        if self.text == "" or self.text == "<press key>":
            self.updateKeyText()

    def updateKeyText(self):
        self.text = self.get_key_string(self.currentKey)

    def onKeyDown(self, symbol, modifiers):
        if symbol in self.settings.getCurrentKeysUsed() or symbol in restrictedKeys:
            self.updateKeyText()
            return
        if self.text == "<press key>":
            self.currentKey = symbol
            self.updateKeyText()
            self.settings.keyUpdated = True
            desktop.lostFocus()

    def onKeyText(self, text):
        return


class ControlSettings:

    def __init__(self, window):
        self.window = window
        self.keyUpdated = False
        self.tabButton = window.tabControl.addTab("Controls")
        self.tabButton.addCallback("onMouseLeftClick", (lambda widget, x, y, modifiers: self.showTab()))
        self.scrollBox = ScrollableContainer(window, position=(0, 4), size=(240, 170), visible=False)
        self.dataTable = Datatable((self.scrollBox.content), position=(AnchorType.TOPCENTER), maxCols=2)
        self.dataTable.setInternalMargins(2, 4)
        for x in range(1, 7):
            self.dataTable.add(Label((self.dataTable), text=("Selected Key #{0}".format(x))))
            self.dataTable.add(ControlTextbox(self, self.dataTable, "hotkey{0}".format(x)))

        for x in range(1, 5):
            self.dataTable.add(Label((self.dataTable), text=("Shared Key #{0}".format(x))))
            self.dataTable.add(ControlTextbox(self, self.dataTable, "hotkey{0}".format(x + 6)))

        self.dataTable.add(Label((self.dataTable), text="Move Up"))
        self.dataTable.add(ControlTextbox(self, self.dataTable, "move_up"))
        self.dataTable.add(Label((self.dataTable), text="Move Down"))
        self.dataTable.add(ControlTextbox(self, self.dataTable, "move_down"))
        self.dataTable.add(Label((self.dataTable), text="Move Left"))
        self.dataTable.add(ControlTextbox(self, self.dataTable, "move_left"))
        self.dataTable.add(Label((self.dataTable), text="Move Right"))
        self.dataTable.add(ControlTextbox(self, self.dataTable, "move_right"))
        self.dataTable.add(Label((self.dataTable), text="Toggle Bag"))
        self.dataTable.add(ControlTextbox(self, self.dataTable, "bag"))
        self.dataTable.add(Label((self.dataTable), text="Toggle Pokedex"))
        self.dataTable.add(ControlTextbox(self, self.dataTable, "pokedex"))
        self.dataTable.add(Label((self.dataTable), text="Toggle Party"))
        self.dataTable.add(ControlTextbox(self, self.dataTable, "pokeparty"))
        self.dataTable.add(Label((self.dataTable), text="Toggle Map"))
        self.dataTable.add(ControlTextbox(self, self.dataTable, "worldmap"))
        self.dataTable.add(Label((self.dataTable), text="Toggle Quest Journal"))
        self.dataTable.add(ControlTextbox(self, self.dataTable, "questjournal"))
        self.dataTable.add(Label((self.dataTable), text="Toggle Summary"))
        self.dataTable.add(ControlTextbox(self, self.dataTable, "pokemon_summary"))
        self.dataTable.add(Label((self.dataTable), text="Toggle Friends List"))
        self.dataTable.add(ControlTextbox(self, self.dataTable, "friends"))
        self.dataTable.add(Label((self.dataTable), text="NPC Interact"))
        self.dataTable.add(ControlTextbox(self, self.dataTable, "npc_interact"))
        self.dataTable.add(Label((self.dataTable), text="Rotate Selection"))
        self.dataTable.add(ControlTextbox(self, self.dataTable, "rotate_select"))
        self.dataTable.add(Label((self.dataTable), text="Jump (Visual)"))
        self.dataTable.add(ControlTextbox(self, self.dataTable, "jump"))
        self.dataTable.fitToContent()
        self.resetButton = Button((self.scrollBox.content), text="Reset Keys to Default", position=(AnchorType.BOTTOMCENTER))
        self.resetButton.addCallback("onMouseLeftClick", self._resetControlEvent)
        self.scrollBox.fitToContent()

    def _resetControlEvent(self, widget, x, y, modifiers):
        confirmWindow.verify("This will reset all of your keys back to default.\nAre you sure?", self.resetControls)

    def resetControls(self):
        for widget in self.dataTable.getWidgets():
            if isinstance(widget, ControlTextbox):
                widget.currentKey = defaultKeys[widget.keyTag]
                widget.updateKeyText()

    def getCurrentKeysUsed(self):
        return [widget.currentKey for widget in self.dataTable.getWidgets() if isinstance(widget, ControlTextbox)]

    def showTab(self):
        if self.window.currentTab != self:
            self.window.currentTab.hide()
            self.show()
            self.window.currentTab = self

    def show(self):
        self.scrollBox.show()

    def hide(self):
        self.scrollBox.hide()

    def save(self):
        for widget in self.dataTable.getWidgets():
            if isinstance(widget, Textbox):
                gameSettings["Keyboard"][widget.keyTag] = str(widget.currentKey)

        if self.keyUpdated:
            hotbar.window.updateKeys()
        self.keyUpdated = False
        return False

    def load(self):
        for widget in self.dataTable.getWidgets():
            if isinstance(widget, Textbox):
                widget.currentKey = gameSettings.getKey(widget.keyTag)


class SettingsWindow(Window):

    def __init__(self):
        Window.__init__(self, desktop, position=(AnchorType.CENTER), size=(250, 250), autosize=(True,
                                                                                                True), visible=False)
        self.setManualFit()
        self.setId("Settings")
        Header(self, "Settings")
        self.saveBtn = Button(self, position=(AnchorType.CENTERBOTTOM), size=(75, 0), autosize=(False,
                                                                                                True), text="Save", style=(styleDB.greenButtonStyle),
          clickSound="ButtonSelect")
        self.saveBtn.addCallback("onMouseLeftClick", self.saveSettings)
        self.cancelBtn = Button(self, position=(AnchorType.CENTERBOTTOM), size=(75,
                                                                                0), autosize=(False,
                                                                                              True), text="Cancel",
          style=(styleDB.redButtonStyle),
          clickSound="ButtonSelect")
        self.cancelBtn.addCallback("onMouseLeftClick", self.hideClick)
        self.currentTab = None
        self.tabControl = Tabs(self, desktop)
        self.video = VideoSettings(self)
        self.sound = SoundSettings(self)
        self.game = GameSettings(self)
        self.ui = UISettings(self)
        self.controls = ControlSettings(self)
        self.loadSettings()
        self.currentTab = None
        self.fitToContent()

    def hide(self):
        Window.hide(self)
        self.tabControl.hide()

    def hideClick(self, widget, x, y, modifiers):
        self.hide()

    def unHide(self):
        Window.unHide(self)
        if self.currentTab is None:
            self.currentTab = self.video
            self.currentTab.show()
        if not self.tabControl.visible:
            self.tabControl.show()

    def loadSettings(self):
        self.video.load()
        self.sound.load()
        self.game.load()
        self.ui.load()
        self.controls.load()
        if not self.saveBtn.isEventsEnabled():
            self.saveBtn.enableEvents()

    def saveSettings(self, widget, x, y, modifiers):
        requiresRestart = False
        if self.video.save():
            requiresRestart = True
        if self.controls.save():
            requiresRestart = True
        if self.game.save():
            requiresRestart = True
        if self.sound.save():
            requiresRestart = True
        if self.ui.save():
            requiresRestart = True
        else:
            if not gameSettings.saveConfig():
                eventManager.notify("onNotificationMessage", "Notification", "Could not save to the configuration file. Try running as administrator or check antivirus settings")
                return
            if requiresRestart:
                eventManager.notify("onNotificationMessage", "Notification", "Your settings have been saved. Some options you changed will need a restart to take effect.")
            else:
                eventManager.notify("onNotificationMessage", "Notification", "Your settings have been saved.")


settingsControl = Settings()
