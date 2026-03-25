# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\data\font.py
import configparser
from client.data.file import archive
from pyglet.font.win32 import *
from pyglet import font

class FontDB:
    FOLDER = "lib/font/"
    FILENAME = "lib/font/lang.cfg"
    DEFAULT_CHARACTERS = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz{}()[]<>!?.,:;\'"*&%$@#\\/|+=-_~` '

    def __init__(self):
        self.fonts = {}
        self.read()

    def get_width(self, fontObj, text):
        """ Faster way for getting text width.
            Note: Glyph's must have already been created or this will not work.
            Recommended to """
        i = 0
        for c in text:
            i += fontObj.glyphs[c].width

        return i

    def preloadGlyphs(self, ft):
        """ Preload all normal glyphs we use to allow retrieval of width values early.
            """
        for char in self.DEFAULT_CHARACTERS:
            ft.get_glyphs(char)

    def read(self):
        cfg = configparser.ConfigParser()
        cfg.read_string(archive.openFile(self.FILENAME).read().decode())
        for section in cfg.sections():
            if section == "fonts":
                items = cfg.items(section)
                for name, value in items:
                    filename, defSize, font_name = value.split(",")
                    defSize = int(defSize)
                    font.add_file(archive.openFile(self.FOLDER + filename))
                    ft = pyglet.font.load(name=font_name, size=defSize)
                    glyph = ft.get_glyphs("T")[0]
                    ft.height = glyph.height - 1
                    ft.get_width = self.get_width
                    ft.renderer = ft.glyph_renderer_class(ft)
                    self.preloadGlyphs(ft)
                    self.fonts[name] = ft

    def getFont(self, name):
        return self.fonts[name]


fontDB = FontDB()
# global fontDB ## Warning: Unused global
