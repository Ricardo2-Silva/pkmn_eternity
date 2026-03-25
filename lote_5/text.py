# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\render\utils\text.py
"""
Created on 1 juil. 2011

@author: Kami
"""
from client.data.gui.style import ShadowType
import client.data.exceptions as exceptions
from client.data.font import fontDB
import time
from client.data.gui.styleDB import transparentTexture

class TextCache:

    def __init__(self, style):
        self.inline = {}
        self.wrapped = {}

    def getInlineText(self, text):
        return
        return

    def addInline(self, text, texture):
        self.inline[text] = texture

    def getWrapped(self, text, width, height):
        return
        return

    def addWrapped(self, text, width, height, texture):
        self.wrapped[(text, width, height)] = texture


import pyglet

class TextRender:
    __doc__ = " Render text in specific way and return the texture "

    def __init__(self):
        self.fontStyles = {}
        self.cache = {}
        self.atlas = pyglet.image.atlas.TextureBin()

    def getCache(self, style):
        if style not in self.fontStyles:
            self.fontStyles[style] = TextCache(style)
        return self.fontStyles[style].font

    def getStyle(self, style):
        if style not in self.fontStyles:
            self.fontStyles[style] = TextCache(style)
        return self.fontStyles[style]

    def getWidth(self, style, text):
        return fontDB.get_width(style.font, text)

    def calculateSize(self, font, text):
        return (
         fontDB.get_width(font, text), font.height)

    def renderText(self, style, text, wrap=0, width=0, height=0):
        """
           style: style of text (includes color, shadow/color)
           text: the string you want to display.
           wrap: This determines if the string will be allowed to wrap to a new line.
                 args: none, left, center, right

           width: If no width specified, will use the text renderer to determine width.
           height: If no height specified, will use the text renderer to dermine height.

           NOTE/QUIRK: Because of how aligning wrapped text works, it MUST conform to the specified width and will be forced.
           Non-wrapped text is always cropped to the smallest size regardless of width, so that normal label anchoring may work.
        """
        if not text:
            return (transparentTexture, 0)
        else:
            if wrap:
                lines = len(self.wrap_text(text, style.font, width))
                align = wrap - 1
            else:
                lines = 1
                align = 0
            if not wrap or height == 0:
                height = lines * style.font.height
            if style.shadow:
                texture = style.font.renderer.render_shadow_minimum(text, (style.color), (style.shadow.color), wrap, width=width, height=height, align=align)
            else:
                texture = style.font.renderer.render_color(text, (style.color), wrap, width=width, height=height, align=align)
            return (
             texture.get_texture(), lines)

    def wrap_text(self, text, font, width):
        """Wrap text to fit inside a given width when rendered.
        :param text: The text to be wrapped.
        :param font: The font the text will be rendered in.
        :param width: The width to wrap to.
        """
        text_lines = text.split("\n")
        if width is None or width == 0:
            return text_lines
        else:
            wrapped_lines = []
            for line in text_lines:
                line = line.rstrip() + " "
                if line == " ":
                    wrapped_lines.append(line)
                    continue
                    start = len(line) - len(line.lstrip())
                    start = line.index(" ", start)
                    while start + 1 < len(line):
                        next_line = line.index(" ", start + 1)
                        if fontDB.get_width(font, line[:next_line]) <= width:
                            start = next_line
                        else:
                            wrapped_lines.append(line[:start])
                            line = line[start + 1:]
                            start = line.index(" ")

                    line = line[:-1]
                    if line:
                        wrapped_lines.append(line)

            return wrapped_lines


class TextCursorRender(TextRender):
    __doc__ = " Renders text with a cursor. A cursor is a small vertical line between two letters."

    def findLetterPosition(self, style, width, text):
        """ return the position of the letter in text, touch by 'width'. """
        i = 0
        while fontDB.get_width(style.font, text[:i]) < width and i <= len(text):
            i += 1

        return i - 1


TextRenderer = TextRender()
TextCursorRenderer = TextCursorRender()
