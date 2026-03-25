# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\gui\windows.py
from client.control.gui.container import StylizedContainer, Container
from client.data.utils.anchor import AnchorType
from client.data.gui import styleDB
from client.render.gui import TitleRender
from client.control.gui.button import Button
from client.control.gui.label import Label
from client.data.utils.color import Color
from client.control.gui.tables import Datatable
from client.control.gui.checkbox import Tab
from client.data.settings import gameSettings
from shared.container.geometry import InterfacePositionable2D
from client.data.events.event import CallbackPriority
from client.render.gui.core import StylizedContainerRender

class Window(StylizedContainer):
    renderClass = StylizedContainerRender

    def __init__(self, parent, background=None, backgroundAnchor=AnchorType.TOPLEFT, style=styleDB.windowsDefaultStyle, position=(0, 0), size=(50, 50), draggable=True, visible=True, autosize=(False, False)):
        StylizedContainer.__init__(self, style, parent, position, size, draggable, visible, autosize)
        self.header = 0

    def getMinimizeButton(self):
        try:
            return self.header.minimize
        except Exception:
            raise Exception("Windows has no reduce button.")

    def show(self):
        StylizedContainer.show(self)
        self.setOnTop()
        self.setActive()

    def setHeader(self, label):
        if self.hasHeader():
            raise Exception("Can not add new header to the windows. It already has one.")
        self.header = label
        self.getStyle().padding.top += label.height

    def empty(self):
        """ delete all widget of container.."""
        widgets = [x for x in self.widgets if x != self.header]
        for widget in widgets:
            widget.setParent(self.parent)

    def emptyAndDestroy(self):
        """ delete all widget of container and destroy them.."""
        widgets = [x for x in self.widgets if x != self.header]
        for widget in widgets:
            widget.destroy()

    def setHeaderTitle(self, text):
        if self.hasHeader():
            self.header.title.text = text

    def setHeaderStyle(self, style):
        if self.hasHeader():
            self.header.title.setStyle(style)

    def getHeader(self):
        return self.header

    def hasHeader(self):
        return self.header

    def getPadding(self):
        return self.getStyle().padding

    def resetRendering(self):
        self.renderer.resetSprites()
        for widget in self.visibleWidgets:
            widget.resetRendering()

    def fitToContent(self):
        StylizedContainer.fitToContent(self)
        if self.hasHeader():
            self.header.updateSize()

    def contentChangedSize(self):
        StylizedContainer.contentChangedSize(self)
        if self.hasHeader():
            self.header.updateSize()

    def onMouseDrop(self, widget, x, y, modifiers):
        return

    def ignoreContainerArea(self):
        return False

    def open(self):
        """ Open a windowsif it's hidden """
        if not self.visible:
            self.show()

    def toggle(self):
        if not self.visible:
            self.open()
        else:
            self.close()

    def toggleEvent(self, widget, x, y, modifiers):
        self.toggle()

    def close(self):
        if self.visible:
            self.hide()


class Thumb(Window):
    __doc__ = " A thumbnail of the windows with an icon. "

    def __init__(self, window, text, position, style=styleDB.windowsDefaultStyleNoPadding, visible=False, reduceButton=False):
        if not window.hasHeader():
            if not reduceButton:
                raise Exception("The windows must have an header before setting a thumb, or specify reduce button manually..")
            Window.__init__(self, (window.desktop.minimizeArea), position=position, autosize=(True,
                                                                                              True), size=(40,
                                                                                                           20), draggable=True, visible=visible, style=style)
            self.maxButton = Button(self, text="", position=(AnchorType.LEFTCENTER), size=(16,
                                                                                           16), autosize=(False,
                                                                                                          False), style=(styleDB.maximizeButtonStyle))
            self.maxButton.addCallback("onMouseLeftClick", self.showWindowsAndHide)
            self.button = Label(self, text=text, position=(AnchorType.LEFTCENTER), enableEvents=True)
            self.button.addCallback("onMouseLeftClick", self.showWindowsAndHide)
            self.window = window
            if reduceButton:
                reduceButton.addCallback("onMouseLeftClick", self.hideWindowsAndShow)
        else:
            self.window.header.reduce.addCallback("onMouseLeftClick", self.hideWindowsAndShow)
        self.notifying = False
        self.fitToContent()

    @property
    def text(self):
        return self.button.text

    @text.setter
    def text(self, text):
        self.button.text = text

    def showWindowsAndHide(self, widget, x, y, modifiers):
        self.hide()
        self.window.show()
        if self.isNotifying():
            self.unNotify()

    def hideWindowsAndShow(self, widget, x, y, modifiers):
        self.window.hide()
        self.show()
        self.desktop.lostFocus()

    def isNotifying(self):
        return self.notifying

    def notify(self):
        if self.isNotifying():
            raise Exception("The thumb is already notifying.")
        self.notifying = True
        self.setBackgroundColor(Color.YELLOW)

    def unNotify(self):
        if self.isNotifying():
            raise Exception("The thumb is already notifying.")
        self.notifying = False
        self.setBackgroundColor(Color.WHITE)


class Menu(Window):

    def __init__(self, desktop):
        Window.__init__(self, desktop, position=(100, 100), size=(20, 20), autosize=(True,
                                                                                     True), visible=False, draggable=False, style=(styleDB.windowsDefaultStyleNoPadding))
        self.setPadding(0, 0, 0, 0)

    def setAutoFit(self):
        Window.setAutoFit(self)

    def fitToContent(self):
        Window.fitToContent(self)

    def setManualFit(self):
        Window.setManualFit(self)

    def widgetAdded(self):
        return

    def widgetDeleted(self):
        return

    def hideAllOptions(self):
        """ Hide all the options """
        self.hidevisibleWidgets()

    def add(self, widget):
        if not widget.parent == self:
            raise Exception("Parent is not menu. ")
        else:
            if widget.getAnchor() != AnchorType.TOPLEFT:
                widget.setAnchor(AnchorType.TOPLEFT)
            widget.show()
            if not widget.hasCallback("onMouseLeftClick", CallbackPriority.ON_END, self.closeWindowClick):
                widget.addCallbackEnd("onMouseLeftClick", self.closeWindowClick)
            if not widget.hasCallback("onLostFocus", CallbackPriority.ON_END, self.closeWindowLostFocus):
                widget.addCallbackEnd("onLostFocus", self.closeWindowLostFocus)
        widget.setMargins(0, 0, 0, 0)

    def onLostFocus(self, widget):
        if self.visible:
            if widget.parent != self:
                self.closeWindow()

    def closeWindowClick(self, widget, x, y, modifiers):
        self.closeWindow()

    def closeWindowLostFocus(self, widget):
        self.closeWindow()

    def closeWindow(self):
        if self.visible:
            self.hide()


class Tabs(Container):

    def __init__(self, parent, desktop, linkedPosition=(0, -26), style=styleDB.defaultTabStyle):
        self.style = style
        position = (
         linkedPosition[0], linkedPosition[1] - parent.getPadding().top)
        Container.__init__(self, parent, position, (0, 0), False, True, (True, True))
        self.startsVisible = True
        self.datatable = Datatable(self, position=(1, 1), maxCols=10)
        self.curTab = None
        if self.visible:
            self.makeClickable()

    def show(self):
        Container.show(self)
        self.makeClickable()

    def hide(self):
        Container.hide(self)
        self.removeClickable()

    def makeClickable(self):
        """Needs to be in the desktop layer since the buttons are out of the attached parent's rect."""
        if self not in self._desktop.reactingWidgets:
            self._desktop.reactingWidgets.append(self)

    def removeClickable(self):
        if self in self._desktop.reactingWidgets:
            self._desktop.reactingWidgets.remove(self)

    def setAutofit(self):
        self.datatable.setAutoFit()
        Container.setAutoFit(self)

    def setManualfit(self):
        self.datatable.setManualFit()
        Container.setManualFit(self)

    def fitToContent(self):
        self.datatable.fitToContent()
        Container.fitToContent(self)

    def setActiveTab(self, tab):
        self.curTab = tab
        tab.setSelected(True)

    def getTabByText(self, text):
        for tab in self.datatable.getWidgets():
            if tab.text == text:
                return tab

        raise Exception("The tab with this text <" + text + "> doesn't exist.")

    def addTab(self, text):
        if self.datatable.width > self.parent.width:
            print(f"Cannot add tab {text}")
            return
        else:
            tab = Tab(self.datatable, text, self.style)
            if self.datatable.width + tab.width > self.parent.width:
                print(f"Cannot add tab {text}, exceeds length of the window. Table: {self.datatable.width} | Tab: {tab.width} | Parent: {self.parent.width}")
                tab.destroy()
                del tab
                return
            self.datatable.add(tab, row=0)
            self._addDefaultCallbacks(tab)
            if not self.curTab:
                self.setActiveTab(tab)
            self.fitToContent()
            return tab

    def renameTab(self, oldText, newText):
        tab = self.getTabByText(oldText)
        tab.text = newText
        self.fitToContent()
        if self.datatable.width > self.parent.width:
            tab.text = oldText
            self.fitToContent()
            return False
        else:
            return True

    def delTab(self, text):
        tab = self.getTabByText(text)
        _, col = self.datatable.getIndexes(tab)
        self.datatable.deleteAndDestroy(tab)
        if tab == self.curTab:
            newTab = self.datatable.get(0, col + 1)
            if not newTab:
                newTab = self.datatable.get(0, col - 1)
            if newTab:
                self.setActiveTab(newTab)
        self.datatable.reorganize()
        self.fitToContent()

    def _getMaxTab(self):
        """ Retrieve the tab with the largest text, maybe useful? """
        width = 0
        cTab = None
        for tab in self.datatable.getWidgets():
            if len(tab.text) >= width:
                cTab = tab
                width = len(tab.text)

        return cTab

    def _addDefaultCallbacks(self, tab):
        tab.addCallbackEnd("onMouseLeftClick", self._clickOnTab)

    def _clickOnTab(self, widget, x, y, modifiers):
        if self.curTab:
            self.curTab.unSelect()
        widget.select()
        self.curTab = widget


class Title(Label):
    renderClass = TitleRender


class Header(Container):
    __doc__ = " A generic header for windows "

    def __init__(self, parent, text='', close=False, minimize=False):
        Container.__init__(self, parent, (0, 0), size=(parent.getPaddedWidth(), 20), draggable=False, visible=True)
        self.title = None
        self.close = None
        self.minimize = None
        self.parent = parent
        if text:
            self.title = Title(self, text, styleDB.titleLabelStyle, (-self.parent.getPadding().left, 0), (parent.width, 20), False, True, (False,
                                                                                                                                           False), AnchorType.LEFTCENTER)
        if close:
            self.close = Button(self, "", position=(AnchorType.RIGHTCENTER), size=(16,
                                                                                   16), style=(styleDB.closeButtonStyle), autosize=(False,
                                                                                                                                    False))
            self.close.addCallback("onMouseLeftClick", self.headerClose)
        if minimize:
            self.reduce = Button(self, "", position=(AnchorType.RIGHTCENTER), size=(16,
                                                                                    16), style=(styleDB.reduceButtonStyle), autosize=(False,
                                                                                                                                      False))
            self.reduce.addCallback("onMouseLeftClick", self.minimizeClick)
        parent.setHeader(self)
        self.fitToContent()

    def minimizeClick(self, widget, x, y, modifiers):
        return

    def headerClose(self, widget, x, y, modifiers):
        self.parent.close()

    def getTitle(self):
        return self.title

    def getCloseButton(self):
        return self.close

    def getMinimizeButton(self):
        return self.minimize

    def contentChangedSize(self):
        return

    def updateSize(self):
        self.width = self.parent.getPaddedWidth()
        if self.title:
            self.title.setWidth(self.parent.width)
        self.replaceAnchoredWidgets()

    def setPosition(self, x, y):
        """ set the position of a widget, relatively to its parent's position. Add padding."""
        self.relativeX = x
        self.relativeY = y
        self.x, self.y = self.parent.getTopLeftPadded(x, y - self.parent.getPadding().top)
        self.updateChildsPosition()

    def updatePosition(self):
        self.x, self.y = self.parent.getTopLeftPadded(self.relativeX, self.relativeY - self.parent.getPadding().top)
        self.updateChildsPosition()

    def updatePositionDragging(self):
        self.updatePosition()
