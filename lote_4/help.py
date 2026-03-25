# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\data\system\help.py
import os, ujson
tips = ('pokemon_receive', 'pokemon_release', 'pokemon_selection', 'pokedex', 'item_pokeball')
defaultTipSettings = {}
for tip in tips:
    defaultTipSettings[tip] = False

class HelpDataManager(object):
    __doc__ = " This determines if the player has received help already, this way they don't get the same messages multiple times. "

    def __init__(self):
        self.config = None

    def setFilePath(self, path):
        self.file = os.path.join(path, "help.cfg")
        self.loadConfig()

    def loadConfig(self):
        try:
            with open(self.file, "r") as fp:
                self.config = ujson.load(fp)
        except ValueError:
            print("WARNING: Failed to load help config, creating new one.")
            self._createDefault()
        except FileNotFoundError:
            print("WARNING: Help config not found, creating new one.")
            self._createDefault()

    def _createDefault(self):
        self.config = defaultTipSettings.copy()
        with open(self.file, "w") as fp:
            ujson.dump(defaultTipSettings, fp)

    def needsHelp(self, name):
        try:
            return self.config[name] is False
        except KeyError:
            self.config[name] = False
            return True

    def gaveHelp(self, name):
        self.config[name] = True
        self.save()

    def save(self):
        with open(self.file, "w") as fp:
            ujson.dump(self.config, fp)


helpConfig = HelpDataManager()
