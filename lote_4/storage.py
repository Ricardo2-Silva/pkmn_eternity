# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\data\system\storage.py
"""
Created on Nov 4, 2011

@author: Ragnarok
"""
import os, configparser
from shared.container.constants import MAX_STORAGE_BOXES
import ujson
filename = "storage.cfg"
defaultStorageConfig = {}
for i in range(1, MAX_STORAGE_BOXES):
    boxId = str(i)
    defaultStorageConfig[boxId] = {}
    defaultStorageConfig[boxId]["graphic"] = i - 1
    defaultStorageConfig[boxId]["name"] = f"Box {i}"

class StorageFileHandler:

    def __init__(self):
        self.file = ""

    def setFilePath(self, path):
        self.file = os.path.join(path, filename)
        self.loadConfig()

    def loadConfig(self):
        try:
            with open(self.file, "r") as fp:
                self.config = ujson.load(fp)
        except ValueError:
            print("WARNING: Failed to load storage config, creating new one.")
            self._createDefault()
        except FileNotFoundError:
            print("WARNING: Storage config not found, creating new one.")
            self._createDefault()

    def _createDefault(self):
        self.config = defaultStorageConfig.copy()
        with open(self.file, "w") as fp:
            ujson.dump(defaultStorageConfig, fp)

    def getStorageBox(self, boxId):
        return self.config[str(boxId)]

    def updateBox(self, storageBox):
        boxId = str(storageBox.boxId)
        self.config[boxId]["graphic"] = storageBox.imageId
        self.config[boxId]["name"] = storageBox.name

    def save(self):
        with open(self.file, "w") as fp:
            ujson.dump(self.config, fp)


storageConfig = StorageFileHandler()
