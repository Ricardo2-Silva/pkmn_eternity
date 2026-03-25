# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\data\settings.py
"""
Created on 22 juil. 2011

@author: Kami
"""
import builtins, configparser, os
from distutils.version import StrictVersion
from cryptography.fernet import Fernet, InvalidToken
from pyglet.window import key
from shared.container.constants import VERSION

class ScreenMode:
    NORMAL = 0
    FULLSCREEN = 1


defaultKeys = {'hotkey1':key._1, 
 'hotkey2':key._2, 
 'hotkey3':key._3, 
 'hotkey4':key._4, 
 'hotkey5':key._5, 
 'hotkey6':key._6, 
 'hotkey7':key.Q, 
 'hotkey8':key.E, 
 'hotkey9':key.R, 
 'hotkey10':key.T, 
 'move_up':key.W, 
 'move_down':key.S, 
 'move_left':key.A, 
 'move_right':key.D, 
 'jump':key.SPACE, 
 'npc_interact':key.Z, 
 'bag':key.B, 
 'pokedex':key.C, 
 'pokeparty':key.X, 
 'friends':key.F, 
 'worldmap':key.M, 
 'questjournal':key.J, 
 'pokemon_summary':key.V, 
 'rotate_select':key.TAB}
guiHotkeyNames = ('bag', 'pokedex', 'pokeparty', 'pokemon_summary', 'worldmap', 'questjournal',
                  'friends')
restrictedKeys = (key.RALT, key.LALT, key.LSHIFT, key.RSHIFT, key.LCTRL, key.RCTRL, key.RETURN, key.ENTER)

class GameSettings:
    __doc__ = " Read all config and permit access to values. "
    _lock = b'nWZrbxtNQHyN_3NRs6FuFjZJLXvraLBbM0P_-3V_N_M='

    def __init__(self):
        self.default_config = self.generateDefaultKeys()
        self._readConfig()
        self.windowResolution = self.calculateWindowResolution()
        self.worldResolution = self.calculateWorldResolution()
        scale = self.getUIScale()
        self.scaledResolution = (self.windowResolution[0] // scale, self.windowResolution[1] // scale)

    def calculateWindowResolution(self):
        return (
         self.config.getint("Screen", "width"), self.config.getint("Screen", "height"))

    def getServerIP(self, name='eternity'):
        return self.config["Server"][name][:-5]

    def getFpsLoopingTime(self):
        return int(float(self.config["Screen"]["fps"]))

    def getVsync(self):
        try:
            return self.config.getboolean("Screen", "vsync")
        except:
            return False

    def getAutotilesValue(self):
        return True

    def getObjectsValue(self):
        return True

    def getTilesetsValue(self):
        return True

    def getEffectsValue(self):
        return True

    def getWallsValue(self):
        return True

    def getGroundsValue(self):
        return True

    def getServerPort(self, name='eternity'):
        return int(self.config["Server"][name][-4:])

    def getCursorAcceleration(self):
        return int(self.config["Screen"]["mouse"])

    def getFullscreen(self):
        return self.config.getboolean("Screen", "fullscreen")

    def getWindowResolution(self):
        return self.windowResolution

    def getScaledUIWindowResolution(self):
        return self.scaledResolution

    def getWorldResolution(self):
        """ Max ingame resolution of 1280 x 720 zoomed out """
        return self.worldResolution

    def getGUIResolution(self):
        """ Added this for future incase we want to scale or separate """
        return self.getWindowResolution()

    def getGameSize(self):
        width, height = self.getWindowResolution()

    def getScreenCenter(self):
        w, h = self.getWindowResolution()
        return (w / 2, h / 2)

    def calculateWorldResolution(self):
        """ Get Max screen resolution depending on aspect ratio of window.
            This prevents stretching in most cases. 16:9, 16:10, 4:3 are most common. """
        sixteen_nine = 1.7777777777777777
        sixteen_ten = 1.6
        w, h = self.getWindowResolution()
        divided_res = w / float(h)
        if divided_res >= sixteen_nine:
            resolution = (1280, 720)
        elif divided_res == sixteen_ten:
            resolution = (1280, 800)
        else:
            resolution = (1024, 768)
        if w > resolution[0] or h > resolution[1]:
            wn = min(w // 2, resolution[0])
            hn = min(h // 2, resolution[1])
            resolution = (wn, hn)
        return resolution

    def getGameChunks(self):
        try:
            return self.config.getboolean("Game", "use_chunks")
        except ValueError:
            return False

    def getCameraSpeed(self):
        try:
            return self.config.getboolean("Game", "camera_slow")
        except ValueError:
            return True

    def getAdditionalPreload(self):
        try:
            return self.config.getboolean("Game", "preload_extra")
        except ValueError:
            return False

    def getQuickCast(self):
        try:
            return self.config.getboolean("Game", "quick_cast")
        except ValueError:
            return False

    def getWindowCenter(self, width, height):
        """UI Only."""
        w, h = self.getScaledUIWindowResolution()
        return (w // 2 - width / 2, h // 2 - height // 2)

    def getGuiState(self):
        return self.config.getint("Audio", "gui")

    def getGuiVolume(self):
        try:
            return self.config.getint("Audio", "gui_volume")
        except ValueError:
            self.config["Audio"]["gui_volume"] = self.default_config["Audio"]["gui_volume"]
            return int(self.config["Audio"]["gui_volume"])

    def getBgmVolume(self):
        try:
            return self.config.getint("Audio", "bgm_volume")
        except ValueError:
            self.config["Audio"]["bgm_volume"] = self.default_config["Audio"]["bgm_volume"]
            return int(self.config["Audio"]["bgm_volume"])

    def getBattleBgmVolume(self):
        try:
            return self.config.getint("Audio", "battle_volume")
        except ValueError:
            self.config["Audio"]["battle_volume"] = self.default_config["Audio"]["battle_volume"]
            return int(self.config["Audio"]["battle_volume"])
        except configparser.NoOptionError:
            self.config["Audio"]["battle_volume"] = self.default_config["Audio"]["battle_volume"]
            return int(self.config["Audio"]["battle_volume"])

    def getEffectVolume(self):
        try:
            return self.config.getint("Audio", "effect_volume")
        except ValueError:
            self.config["Audio"]["effect_volume"] = self.default_config["Audio"]["effect_volume"]
            return int(self.config["Audio"]["effect_volume"])

    def getEnvironmentVolume(self):
        try:
            return self.config.getint("Audio", "environment_volume")
        except ValueError:
            self.config["Audio"]["environment_volume"] = self.default_config["Audio"]["environment_volume"]
            return int(self.config["Audio"]["environment_volume"])

    def getBgmState(self):
        return self.config.getint("Audio", "bgm")

    def getEffectState(self):
        return self.config.getint("Audio", "effect")

    def getLoginInfos(self):
        if self.canSavePassword():
            if self.config["Login"]["pass"]:
                try:
                    cipher_suite = Fernet(self._lock)
                    pwd = cipher_suite.decrypt(self.config["Login"]["pass"].encode()).decode()
                except InvalidToken:
                    pwd = ""

            else:
                pwd = ""
        else:
            pwd = ""
        return (self.config["Login"]["mail"], pwd)

    def setLoginInfos(self, username, password):
        if self.canSavePassword():
            cipher = Fernet(self._lock)
            pwd = cipher.encrypt(password.encode()).decode()
        else:
            pwd = ""
        self.config["Login"]["mail"] = username
        self.config["Login"]["pass"] = pwd
        self.saveConfig()

    def canSavePassword(self):
        return self.config.getboolean("Login", "save_password") is True

    def setSavePassword(self, value):
        self.config["Login"]["save_password"] = value
        self.saveConfig()

    def getHotkeyPressed(self, symbol):
        """Returns a hotkey if it exists that is not movement or battle related."""
        for hotkeyName, hotkey in defaultKeys.items():
            if hotkeyName in guiHotkeyNames:
                if symbol == self.getKey(hotkeyName):
                    return hotkeyName

        return

    def getDirectionKeys(self):
        return (
         self.config.getint("Keyboard", "move_up"),
         self.config.getint("Keyboard", "move_right"),
         self.config.getint("Keyboard", "move_down"),
         self.config.getint("Keyboard", "move_left"))

    def getAttackKeys(self):
        return (
         self.config.getint("Keyboard", "hotkey1"),
         self.config.getint("Keyboard", "hotkey2"),
         self.config.getint("Keyboard", "hotkey3"),
         self.config.getint("Keyboard", "hotkey4"),
         self.config.getint("Keyboard", "hotkey5"),
         self.config.getint("Keyboard", "hotkey6"))

    def getHotbarKeys(self):
        return (self.config.getint("Keyboard", f"hotkey{i}") for i in range(1, 11))

    def getHotbarKeyByNumber(self, num):
        hotkey = "hotkey{0}".format(num)
        return self.config.getint("Keyboard", hotkey, fallback=(defaultKeys[hotkey]))

    def getHotbarNumber(self, key):
        for i in range(1, 11):
            keyValue = "hotkey{0}".format(i)
            try:
                hotbarKey = self.config.getint("Keyboard", keyValue)
            except KeyError:
                hotbarKey = defaultKeys[keyValue]

            if hotbarKey == key:
                return i

        return

    def getZoom(self):
        return self.config.getfloat("Screen", "zoom")

    def getKey(self, keyName):
        try:
            return self.config.getint("Keyboard", keyName)
        except Exception:
            return defaultKeys[keyName]

    def getAutoSelectionControl(self):
        try:
            return self.config.getint("Game", "auto_selection")
        except Exception:
            return 0

    def getUIScale(self):
        try:
            return self.config.getint("Screen", "ui_scale")
        except Exception:
            return 1

    def getSkipRename(self):
        try:
            return self.config.getboolean("Game", "skip_rename")
        except Exception:
            return False

    def getPM(self):
        return self.config.getint("Game", "pm")

    def getHPBars(self):
        return self.config.getint("Game", "hpbars")

    def getHotbarLock(self):
        return self.config.getint("Game", "hotbarlock")

    def getHotbarRecall(self):
        try:
            return self.config.getboolean("Game", "hotbar_recall")
        except ValueError:
            return False
        except configparser.NoOptionError:
            return False
        except configparser.NoSectionError:
            return False

    def getWeather(self):
        return self.config.getint("Game", "weather")

    def getAlwaysDay(self):
        return self.config.getint("Game", "alwaysday", fallback=0)

    def getAlwaysNames(self):
        return 0

    def getTargetIndicator(self):
        try:
            return self.config.getboolean("Game", "target_indicator")
        except:
            return True

    def getCurrentSkin(self):
        return self.config["Game"]["skin"]

    def __getitem__(self, value):
        return self.config[value]

    def __setitem__(self, key, value):
        self.config[key] = value

    def _readConfig(self):
        self.config = configparser.ConfigParser()
        filename = "config.cfg"
        if not os.path.exists(filename):
            self._createConfig()
        self.config.read(filename)
        if not self._verify_config():
            self._createConfig()
            self.config.read(filename)

    def getCurrentPatchNumber(self):
        try:
            version = StrictVersion(self.config.get("Patch", "current"))
        except Exception:
            version = StrictVersion(VERSION)
            self.config.set("Patch", "current", VERSION)

        return version

    def getPatchServer(self):
        return self.config["Patch"]["server"]

    def saveConfig(self):
        try:
            with open("config.cfg", "w") as configfile:
                self.config.write(configfile)
            return True
        except builtins.PermissionError:
            pass

        return False

    def _verify_config(self):
        """We go over the config file to make sure all options needed are there."""
        for configSection, values in self.default_config.items():
            for keyName, value in values.items():
                try:
                    self.config[configSection][keyName]
                except KeyError:
                    self.config[configSection][keyName] = str(value)

        return True

    def getReportSettings(self):
        """Get the settings requested for the bug reporter."""
        return f"World: {self.worldResolution}\nScreen: {self.windowResolution}\nChunks: {self.getGameChunks()}\nPreload: {self.getAdditionalPreload()}\nWeather: {bool(self.getWeather())}\n"

    def generateDefaultKeys(self):
        keys = {'Server':{"eternity": "143.244.160.148:5679"}, 
         'Screen':{
          'width': '"1024"', 
          'height': '"768"', 
          'fullscreen': '"False"', 
          'mouse': '"1"', 
          'zoom': '"2.0"', 
          'ui_scale': '"1.0"', 
          'vsync': '"False"'}, 
         'Game':{
          'pm': '"1"', 
          'hpbars': '"1"', 
          'weather': '"1"', 
          'hotbarlock': '"0"', 
          'hotbar_recall': '"False"', 
          'alwaysday': '"0"', 
          'alwaysnames': '"0"', 
          'skin': '"Heart Gold"', 
          'use_chunks': '"False"', 
          'camera_slow': '"True"', 
          'skip_rename': '"False"', 
          'preload_extra': '"False"', 
          'target_indicator': '"True"', 
          'auto_selection': '"0"', 
          'quick_cast': '"False"'}, 
         'Audio':{
          'bgm': '"1"', 
          'bgm_volume': '"80"', 
          'battle_volume': '"80"', 
          'effects': '"1"', 
          'effect_volume': '"80"', 
          'gui': '"1"', 
          'gui_volume': '"80"', 
          'environment': '"1"', 
          'environment_volume': '"30"'}, 
         'Login':{'mail':"user@email.com", 
          'pass':"", 
          'save_password':"False"}, 
         'Keyboard':{},  'Patch':{'server':"patch.eternityrpg.net", 
          'current':"0"}}
        for key in defaultKeys:
            keys["Keyboard"][key] = str(defaultKeys[key])

        return keys

    def _createConfig(self):
        config = configparser.ConfigParser()
        for configSection, values in self.default_config.items():
            config.add_section(configSection)
            for keyName, value in values.items():
                config[configSection][keyName] = value

        with open("config.cfg", "w") as configfile:
            config.write(configfile)


gameSettings = GameSettings()
