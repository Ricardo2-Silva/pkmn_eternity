# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\gui\label.py
from client.control.gui.widget import StylizedWidget
from client.data.gui import styleDB
import client.render.gui as iCoreRender
from client.data.utils.anchor import AnchorType, Alignment

class Label(StylizedWidget):
    __doc__ = " Create a widget that displays text.\n        Notes: Anchor depends on the background sprite, .\n         "
    renderClass = iCoreRender.LabelRender
    maxDepth = 4

    def __init__(self, parent, text="", style=styleDB.blackLabelStyle, position=(0, 0), size=(0, 0), draggable=False, visible=True, autosize=(True, True), alignment=Alignment.LEFT, anchor_x="left", anchor_y="baseline", multiline=False, enableEvents=False):
        self._text = text
        self.autosize = (
         size[0] == 0, size[1] == 0)
        self.width, self.height = size
        self.alignment = alignment
        self.multiline = multiline
        self.anchor_x = anchor_x
        self.anchor_y = anchor_y
        StylizedWidget.__init__(self, style, parent, position, size, draggable, visible, enableEvents)

    def hide(self):
        StylizedWidget.hide(self)

    def show(self):
        StylizedWidget.show(self)

    def showAndPlay(self):
        self.renderer.readOut()

    @property
    def name(self):
        return "".join([self.__class__.__name__, " :", self.text])

    def clone(self, parent):
        return Label(parent, self.text, self.style, self.getRelativePosition(), self.size, self.draggable, True, self.autosize, self.isEventsEnabled())

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        if self._text == text:
            return
        self._text = text
        if text:
            if not self.renderer.textSprite:
                self.renderer.createAndAddText()
                self.updateSize()
                return
        self.renderer.refresh()
        self.updateSize()

    def setStyle(self, style):
        if self.style == style:
            return
        else:
            updateSize = False
            if style.text.anchor != self.style.text.anchor:
                updateSize = True
            self.style = style
            self.renderer.refreshStyle()
            self.renderer.refresh()
            if updateSize:
                self.renderer.updateSize()

    def setTextColor(self, color):
        self.renderer.setTextColor(color)

    def setTextAnchor(self, anchor):
        self.getStyle().setTextAnchor(anchor)
        self.renderer.refresh()

    def setTextAnchors(self, anchor_x, anchor_y):
        """This differs from setTextAnchor in that it sets Pyglet's anchoring system. This way you can anchor
        background and sprite to look proper."""
        self.renderer.setTextAnchors(anchor_x, anchor_y)

    def updateSize(self):
        width, height = self.size
        w, h = self.renderer.getSize()
        if self.isAutoResizeHeight():
            height = h + self.getPadding().top + self.getPadding().bottom
        if self.isAutoResizeWidth():
            width = w + self.getPadding().left + self.getPadding().right
        StylizedWidget.setSize(self, width, height)

    def setSize(self, width, height):
        w, h = self.renderer.getSize()
        if self.isAutoResizeHeight():
            height = h + self.getPadding().top + self.getPadding().bottom
        if self.isAutoResizeWidth():
            width = w + self.getPadding().left + self.getPadding().right
        StylizedWidget.setSize(self, width, height)

    def getTextSize(self):
        return self.renderer.getSize()

    def isAutoResize(self):
        return self.autosize[0] and self.autosize[1]

    def isAutoResizeWidth(self):
        return self.autosize[0]

    def isAutoResizeHeight(self):
        return self.autosize[1]


class SpellingLabel(Label):
    renderClass = iCoreRender.SpellingLabelRender
