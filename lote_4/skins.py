# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\data\skins.py
"""
Created on Feb 8, 2012

@author: Ragnarok
"""
import os, configparser
from client.data.gui.skins import Skin, SkinElement, SkinTextStyle
from shared.service.utils import str2IntTuple
import client.render.cache as cache
from client.render.utils.patch import PatchType
from client.data.gui.padding import PaddingData
from client.data.gui.style import BorderData, TextData
from client.data.utils.color import Color
from client.data.settings import gameSettings
import copy
from client.data.file import archive

class SkinDB:
    folder = "skins"
    defaultSkin = "Heart Gold"
    styleFile = "style.cfg"
    elements = [
     "Window",
     "Tab"]
    onlyPadding = [
     "Window"]

    def __init__(self):
        self.styleTypes = {'Window':self.loadBorder, 
         'Tab':self.loadButton}
        self.files = {'Window':"window.png", 
         'Tab':"tab.png"}
        self.currentBorder = None
        self.currentTab = None
        self.skins = {}
        self.textStyles = []
        self.realTextStyles = {}
        self.checkFolder(self.folder)
        self.read()
        self.convertDataToStyle()
        self.currentSkin = self.skins[gameSettings.getCurrentSkin()]

    def changeSkin(self, name):
        newSkin = self.skins[name]
        self.getWindowBorder().updateImages(newSkin.elements["Window"].data.images)
        self.getTabImage().updateBackgroundImage(newSkin.elements["Tab"].data, PatchType.FOUR_IMAGE)
        self.currentSkin = newSkin

    def getPrimaryColor(self):
        return self.currentSkin.textStyles["primary"].color

    def getSecondaryColor(self):
        return self.currentSkin.textStyles["secondary"].color

    def getPrimaryShadow(self):
        return self.currentSkin.textStyles["primary"].shadow

    def getSecondaryShadow(self):
        return self.currentSkin.textStyles["secondary"].shadow

    def getTabImage(self):
        return self.currentSkin.getElement("Tab").data

    def getWindowBorder(self):
        return self.currentSkin.getElement("Window").data

    def getWindowColor(self):
        return self.currentSkin.getElement("Window").color

    def loadBorder(self, styleData, element='Window'):
        elementData = styleData.getElement(element)
        image = cache.textureCache.getBorder("/".join([self.folder, styleData.name, self.files[element]]))
        elementData.data = BorderData(image, padding=PaddingData(*styleData.getElementPadding(element)))

    def loadButton(self, styleData, element='Tab'):
        elementData = styleData.getElement(element)
        elementData.data = cache.textureCache.getButtonBackground("/".join([self.folder, styleData.name, self.files[element]]), PatchType.THREE)

    def convertDataToStyle(self):
        for style in self.skins.values():
            try:
                for element in style.elements:
                    self.styleTypes[element](style, element)

            except KeyError as e:
                print(f"Warning: Section found for non-skinnable area. {e}")
                continue

    def checkFolder(self, folder):
        """ Makes sure folder exists, if not, creates it. """
        if not os.path.exists(folder):
            os.makedirs(folder)
        if not os.path.isdir(folder):
            os.remove(folder)
            os.makedirs(folder)

    def fileIntegrityCheck(self, folder):
        for file in self.files.values():
            path = os.path.join(folder, file)
            if not os.path.exists(path) or os.path.isdir(path):
                return False

        return True

    def checkIfTextStyleExists(self, textStyle):
        for style in self.styles:
            if style.color == textStyle.color:
                if style.shadow == textStyle.shadow:
                    return style

        return False

    def addStyle(self, style):
        self.styles.append(style)

    def read(self):
        for file in os.listdir(self.folder):
            path = os.path.join(self.folder, file)
            if os.path.isdir(path) and self.fileIntegrityCheck(path):
                try:
                    skinData = Skin(file)
                    cfg = configparser.RawConfigParser()
                    cfg.read(os.path.join(path, self.styleFile))
                    for element in cfg.sections():
                        if element == "Common":
                            for option, value in cfg.items(element):
                                v = value.split(";")
                                skinData.textStyles[option] = SkinTextStyle(str2IntTuple(v[0]), str2IntTuple(v[1]))

                        else:
                            skinElement = SkinElement()
                            for option, value in cfg.items(element):
                                if option == "padding":
                                    skinElement.padding = str2IntTuple(value)
                                else:
                                    if option == "color":
                                        skinElement.color = str2IntTuple(value)

                            skinData.elements[element] = skinElement

                    self.skins[file] = skinData
                except IOError:
                    print()
                    print(f"ERROR: Failure to properly load style config for skin {file}.")

        if not self.skins:
            self.createDefaultSkin()
            self.read()

    def createDefaultSkin(self):
        folder = os.path.join(os.curdir, "skins", self.defaultSkin)
        self.checkFolder(folder)
        libPath = f"lib/skins/{self.defaultSkin}/"
        for filename in archive.listDir(libPath):
            if filename:
                fileInfo = archive.getFile(f"{libPath}{filename}")
                fileInfo.filename = fileInfo.filename[len(libPath):]
                archive.extractFile(fileInfo, f"./skins/{self.defaultSkin}/")

    def getFont(self, name):
        return self.fonts[name]


skinDB = SkinDB()
# global skinDB ## Warning: Unused global
