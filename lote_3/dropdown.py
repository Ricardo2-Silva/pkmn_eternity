# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\gui\dropdown.py
from client.control.gui.container import Container
from client.control.gui.button import Button
from client.data.gui import styleDB
from client.control.gui.tables import Datatable
from client.data import exceptions
from client.control.gui.widget import Widget
from client.data.utils.anchor import AnchorType

class DropDown(Container):

    def __init__(self, parent, position=(0, 0), size=(90, 0), draggable=False, visible=True, style=styleDB.blueButtonStyle, defaultOption="-Select-", direction="down"):
        Container.__init__(self, parent, position=position, size=size, draggable=draggable, visible=visible, autosize=(False,
                                                                                                                       True))
        self.buttonStyle = style
        self.startsVisible = visible
        self.direction = direction
        self.defaultOption = defaultOption
        self.createDefaultOption()
        self.menu = Datatable(self, position=(0, self.selectedOption.height), visible=False)
        self.menu.setAlwaysOnTop()
        self.createArrow()
        if parent.isAutoFit():
            parent.contentChangedSize()
        self.setMinHeight(self.selectedOption.height)
        self.setMinWidth(self.selectedOption.width)
        self.fitToContent()

    def show(self):
        Container.show(self)

    def hide(self):
        Container.hide(self)

    def setOption(self, widget):
        self._select(widget)

    def setAutoFit(self):
        self.menu.setAutoFit()
        Container.setAutoFit(self)

    def setManualFit(self):
        self.menu.setManualFit()
        Container.setManualFit(self)

    def addOption(self, widget):
        if widget.parent != self:
            raise Exception("Dropdown is not the parent")
        else:
            if widget.parent != self:
                if widget.parent != self.menu:
                    raise Exception("Parent is not dropdown or the dropdown's menu.")
            if widget.parent == self:
                widget.setParent(self.menu)
            if widget.__class__.__name__ not in ('Widget', 'Button', 'Label', 'IconButton'):
                raise Exception("This widget class is not supported.")
        self.menu.add(widget, col=0)
        widget.addCallbackEnd("onMouseLeftClick", self.selectClick)
        widget.addCallbackEnd("onLostFocus", self.hideOnLostFocus)
        widget.root = self.menu
        if self.autosize[0] == False:
            selectWidth = self.width
            widgetWidth = widget.width
            if widgetWidth > selectWidth:
                Widget.setWidth(self, widgetWidth)
                self.selectedOption.setWidth(widgetWidth)
                for widget in self.menu.getWidgets():
                    widget.setWidth(widgetWidth)

                self._updateArrowPosition()
            elif widgetWidth < selectWidth:
                widget.setWidth(selectWidth)
        widget.renderer.visible = False
        self.fitToContent()

    @property
    def left(self):
        return self.x

    @property
    def right(self):
        return self.x + self.width

    @property
    def top(self):
        if self.direction == "up":
            return self.y + self.height
        else:
            return self.y + self.height

    @property
    def bottom(self):
        if self.direction == "up":
            return self.y - self.menu.getTableHeight()
        else:
            return self.y

    def getOptions(self):
        return self.menu.getWidgets()

    def getOption(self, optionName):
        for option in self.getOptions():
            if option.text == optionName:
                return option

        return False

    def fitToContent(self):
        self.menu.fitToContent()
        Container.fitToContent(self)
        if self.visible:
            self.arrowButton.setOnTop()

    def setOnTop(self):
        Container.setOnTop(self)
        self.parent.pushToTop(self)
        self.arrowButton.setOnTop()

    def hideOnLostFocus(self, widget):
        if widget.root != self.menu:
            self._hideMenu(widget)

    def createDefaultOption(self):
        self.selectedOption = Button(self, (self.defaultOption), position=(0, 0), size=(self.width, 0), autosize=(False,
                                                                                                                  True),
          style=(self.buttonStyle))
        self.selectedOption.setTextAnchor(AnchorType.LEFT + AnchorType.CENTER)
        self.selectedOption.addCallbackEnd("onMouseLeftClick", self._toggleMenu)
        self.selectedOption.addCallbackEnd("onLostFocus", self.hideOnLostFocus)

    def createArrow(self):
        pos = (
         self.selectedOption.width - 22, self.selectedOption.height // 2 - 6)
        self.arrowButton = Button(self, "", style=(styleDB.downArrowButtonStyle), position=pos, size=(16,
                                                                                                      12), autosize=(False,
                                                                                                                     False))
        (self.arrowButton.setPosition)(*pos)
        self.arrowButton.addCallbackEnd("onMouseLeftClick", self._toggleMenu)
        self.arrowButton.addCallbackEnd("onLostFocus", self._hideMenu)

    def emptyAndDestroy(self):
        self.menu.emptyAndDestroy()

    def empty(self):
        self.menu.empty()
        self._updateArrowPosition()

    def _toggleMenu(self, widget, x, y, modifiers):
        if not self.menu.visible:
            self.menu.show()
            self.setOnTop()
            self._desktop.reactingWidgets.insert(0, self)
        else:
            self.menu.hide()
            self._desktop.reactingWidgets.remove(self)
        self.fitToContent()
        if self.direction == "up":
            t = -self.menu.getTableHeight()
            self.menu.setPosition(0, t)

    def _updateArrowPosition(self):
        self.arrowButton.setPosition(self.selectedOption.width - 23, self.selectedOption.height // 2 - 6)

    def _hideMenu(self, widget):
        if self.menu.visible:
            self.menu.hide()
            self.fitToContent()

    def selectClick(self, widget, x, y, modifiers):
        self._select(widget)

    def getCurrentOption(self):
        return self.selectedOption

    def _select(self, widget):
        self.selectedOption.text = widget.text
        if not self.autosize[0]:
            self.selectedOption.setWidth(self.width)
        else:
            self.selectedOption.setWidth(self.selectedOption.width + 20)
        self.menu.setPosition(0, widget.height)
        self._hideMenu(widget)
