# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\gui\textbox.py
from client.control.gui.button import Button
from client.data.gui import styleDB
from client.data.gui.button import TextboxType, ButtonState
from client.control.gui.label import Label
from client.data.settings import gameSettings
from pyglet.window import key
from client.render.gui import TextboxRender
from pyglet.window.key import MOTION_BACKSPACE, MOTION_DELETE, MOTION_UP, MOTION_DOWN, MOTION_LEFT, MOTION_RIGHT
from shared.service.utils import clamp
import time
from shared.container.constants import CursorMode
from client.data.utils.anchor import AnchorType
UI_SCALE = gameSettings.getUIScale()

class Textbox(Button):
    renderClass = TextboxRender
    maxDepth = 5

    def __init__(self, parent, text="", maxLetters=0, type=TextboxType.NORMAL, style=styleDB.defaultTextboxStyle, position=(0, 0), size=(0, 0), draggable=True, visible=True, enableEvents=True, keepFocus=False, scrollable=False):
        self.history = []
        self.cursor = len(text)
        self.maxLetters = maxLetters
        self.history_position = -1
        self.history_max = 10
        self.type = type
        self.keepFocus = keepFocus
        self.dragStart = 0
        self.dragEnd = 0
        self._click_count = 0
        self._click_time = 0
        self.scrollable = scrollable
        Button.__init__(self, parent, text, style, position, size, draggable, visible, (False,
                                                                                        True), enableEvents, AnchorType.LEFTCENTER)

    def getIdRange(self):
        return self.type

    @property
    def caret(self):
        return self._desktop.caret

    @property
    def highlight(self):
        return self._desktop.highlight

    @Label.text.getter
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        if self.maxLetters:
            text = text[:self.maxLetters]
            self.cursor = min(self.cursor, self.maxLetters)
        if len(text) == 0:
            self.cursor = 0
        super(Textbox, Textbox).text.__set__(self, text)
        self.renderer.updateCaret()

    def get_cursor(self):
        return self.cursor

    def add_to_history(self, text):
        self.history.insert(0, text)
        self.history_position = -1
        self.history = self.history[:self.history_max]

    def getPassword(self):
        """ Return the password view of the text """
        return "".rjust(len(self._text), "*")

    def get_from_history(self, val):
        self.history_position += val
        self.history_position = clamp(self.history_position, 0, len(self.history) - 1)
        return self.history[self.history_position]

    def set_cursor_position_from_mouse(self, x, y):
        self.cursor = self.renderer.getCursorPosition(x // UI_SCALE, y // UI_SCALE)
        self.renderer.updateCaret()

    def set_cursor(self, val):
        self.cursor = clamp(val, 0, len(self._text))
        self.renderer.updateCaret()

    def onMouseLeave(self, widget):
        if self.getState() == ButtonState.OVER:
            self.setState(ButtonState.NORMAL)
        self.desktop.cursor.mode = CursorMode.DEFAULT

    def onMouseOver(self, widget, x, y):
        if self.getState() != ButtonState.DOWN:
            self.setState(ButtonState.OVER)
        self.desktop.cursor.mode = CursorMode.TEXT

    def onMouseLeftClick(self, widget, x, y, modifiers):
        t = time.time()
        if t - self._click_time < 0.25:
            self._click_count += 1
        else:
            self._click_count = 1
        self._click_time = time.time()
        if self.getState() != ButtonState.DOWN:
            self.setState(ButtonState.DOWN)
        if self.type & TextboxType.RESET_ON_CLICK:
            self.text = ""
        if self._click_count == 1:
            self.set_cursor_position_from_mouse(x, y)
            self.highlight.hide()
        else:
            if self._click_count == 2:
                self.select_all_words()
        self.dragStart = None

    def select_all_words(self):
        self.cursor = len(self._text)
        self.renderer.updateCaret()
        self.highlight.setStartIndex(0)
        self.highlight.updateHighlightWidth(len(self._text))

    def on_key_press(self, symbol, modifiers):
        if symbol == key.A:
            if modifiers & key.MOD_CTRL:
                self.select_all_words()

    def on_text_motion_select(self, motion):
        if motion == MOTION_LEFT:
            self.set_cursor(self.cursor - 1)
            if self.highlight.startIndex == 0:
                self.highlight.setStartIndex(self.cursor + 1)
            self.highlight.updateHighlightWidth(self.cursor)
        elif motion == MOTION_RIGHT:
            self.set_cursor(self.cursor + 1)
            if self.highlight.startIndex == 0:
                self.highlight.setStartIndex(self.cursor - 1)
            self.highlight.updateHighlightWidth(self.cursor)

    def on_text_motion(self, motion):
        if motion == MOTION_BACKSPACE:
            if self.cursor == 0:
                if not self.highlight.getHighlightedText():
                    return
                elif self.highlight.getHighlightedText():
                    text = self.highlight.getUnhighlightedText()
                    self.highlight.hide()
                else:
                    text = self._text[:self.cursor - 1] + self._text[self.cursor:]
                    self.cursor -= 1
                self.text = text
            elif motion == MOTION_DELETE:
                if self.cursor == len(self._text) + 1:
                    return
                elif self.highlight.getHighlightedText():
                    text = self.highlight.getUnhighlightedText()
                    if self.highlight.endIndex >= self.highlight.startIndex:
                        self.cursor = self.highlight.startIndex
                    else:
                        if self.highlight.endIndex <= self.highlight.startIndex:
                            self.cursor = self.highlight.endIndex
                    self.highlight.hide()
                else:
                    text = self._text[:self.cursor] + self._text[self.cursor + 1:]
                self.text = text
            elif motion == key.MOTION_BEGINNING_OF_LINE:
                self.set_cursor(0)
            elif motion == key.MOTION_END_OF_LINE:
                self.set_cursor(len(self._text))
            elif motion == MOTION_UP:
                if self.history:
                    self.text = self.get_from_history(1)
                    self.set_cursor(len(self._text))
                elif motion == MOTION_DOWN:
                    if self.history:
                        self.text = self.get_from_history(-1)
                        self.set_cursor(len(self._text))
            elif motion == MOTION_LEFT:
                self.set_cursor(self.cursor - 1)
                if self.highlight.getHighlightedText():
                    self.highlight.hide()
        elif motion == MOTION_RIGHT:
            self.set_cursor(self.cursor + 1)
            if self.highlight.getHighlightedText():
                self.highlight.hide()

    def onKeyText(self, text):
        if text == "\r":
            return
        elif self.highlight.getHighlightedText():
            if self.highlight.endIndex >= self.highlight.startIndex:
                combinedText = self._text[:self.highlight.startIndex] + text + self._text[self.highlight.endIndex:]
                self.cursor = self.highlight.startIndex + 1
            else:
                if self.highlight.endIndex <= self.highlight.startIndex:
                    combinedText = self._text[:self.highlight.endIndex] + text + self._text[self.highlight.startIndex:]
                    self.cursor = self.highlight.endIndex + 1
            self.highlight.hide()
        else:
            combinedText = self._text[:self.cursor] + text + self._text[self.cursor:]
            self.cursor = self.cursor + 1
        if self.type == TextboxType.ONLY_INT:
            try:
                int(combinedText)
            except ValueError:
                return

        self.text = combinedText

    def onLostFocus(self, widget):
        self.dragStart = None
        self.setState(ButtonState.NORMAL)
        self.highlight.hide()
        self.caret.visible = False

    def onGainFocus(self, widget):
        self.setState(ButtonState.DOWN)
        self.caret.visible = True
        self.renderer.updateCaret()
        self.highlight.setFocus(self, self.cursor)

    def setCursorHighlight(self, mPos):
        return

    def onMouseDrop(self, widget, x, y, modifiers):
        return

    def onMouseDragBegin(self, widget, x, y, modifiers):
        self.desktop.cursor.mode = CursorMode.TEXT
        index = self.renderer.getCursorPosition(x, y)
        self.dragStart = self.highlight.setStartIndex(index)
        self.highlight.updateHighlightWidth(index)
        self.set_cursor_position_from_mouse(x, y)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.desktop.cursor.mode = CursorMode.TEXT
        index = self.renderer.getCursorPosition(x, y)
        self.highlight.updateHighlightWidth(index)
        self.set_cursor_position_from_mouse(x, y)

    def onKeyReturn(self):
        if self._text:
            self.add_to_history(self._text)
        if not self.keepFocus:
            self.onLostFocus(None)
