# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\gui\tables.py
from client.control.gui.container import Container
from client.control.maths.matrix import Matrix
from client.control.gui.widget import Widget
from client.data import exceptions
import math
from client.control.gui.button import Button
from client.data.gui import styleDB
from client.control.gui.label import Label
from shared.service.utils import clamp

class Datatable(Container):

    def __init__(self, parent, maxRows=0, maxCols=0, position=(0, 0), size=(0, 0), draggable=False, visible=True):
        self.matrix = Matrix(maxRows, maxCols, indexes=True)
        self.internalMargins = [0, 0]
        self.colsWidth = {}
        self.rowsHeight = {}
        Container.__init__(self, parent, position, size, draggable, visible)
        self._resetRowColSize()

    def getIndexes(self, widget):
        return self.matrix.getIndexes(widget)

    def getColsNbr(self):
        return self.matrix.getColsNbr()

    def getRowsNbr(self):
        return self.matrix.getRowsNbr()

    def getMaxRows(self):
        return self.matrix.getMaxRows()

    def getMaxCols(self):
        return self.matrix.getMaxCols()

    def widgetAdded(self):
        return

    def widgetDeleted(self):
        return

    def reorganize(self):
        """ When it finds a position with no widget, it takes the next one and put it at this place. """
        self.matrix.fillHoles()
        self.colsWidth = {}
        self.rowsHeight = {}
        self._resetRowColSize()
        self.updateContentPosition()
        self.contentChangedSize()

    def replaceAnchoredWidgets(self):
        return

    def childChangedSize(self, child):
        if self.isAutoFit():
            self.updateContentPosition()
            self.contentChangedSize()

    def contentChangedSize(self):
        self._resetRowColSize()
        self.updateContentPosition()
        Container.contentChangedSize(self)

    def setAutoFit(self):
        self._resetRowColSize()
        self.updateContentPosition()
        self.autoFit = True
        Container.contentChangedSize(self)

    def updateContentSize(self):
        self._setContentHeight()
        self._setContentWidth()

    def fitToContent(self):
        """ resize container to fit with the widgets inside """
        self._resetRowColSize()
        self.updateContentPosition()
        self.updateContentSize()
        Widget.setSize(self, self._getMinWidth(), self._getMinHeight())

    def _resetRowColSize(self):
        for row in range(0, self.matrix.getRowsNbr()):
            self.rowsHeight[row] = self._calcRowHeight(row)

        for col in range(0, self.matrix.getColsNbr()):
            self.colsWidth[col] = self._calcColWidth(col)

    def getRowHeight(self, row):
        return self.rowsHeight[row] + self.internalMargins[1]

    def getColWidth(self, col):
        return self.colsWidth[col] + self.internalMargins[0]

    def getTableWidth(self):
        return sum(self.colsWidth.values()) + self.internalMargins[0]

    def getTableHeight(self):
        return sum(self.rowsHeight.values()) + self.internalMargins[1]

    def get(self, row=None, col=None):
        return self.matrix.get(row, col)

    def empty(self):
        while len(self.widgets) > 0:
            widget = self.widgets.pop(0)
            self.delete(widget)

        if self.isAutoFit():
            self.contentChangedSize()

    def emptyMatrix(self):
        allwidgets = self.matrix.getAllSingle()
        for widget in allwidgets:
            row, col = self.matrix.getIndexes(widget)
            self.matrix.delete(row, col)

        if self.isAutoFit():
            self.contentChangedSize()

    def emptyAndDestroy(self):
        while len(self.widgets) > 0:
            widget = self.delete(self.widgets[0])
            widget.destroy()

        self.colsWidth = {}
        self.rowsHeight = {}
        if self.isAutoFit():
            self.contentChangedSize()

    def emptyAndHide(self):
        while len(self.widgets) > 0:
            widget = self.delete(self.widgets[0])
            widget.hide()

        if self.isAutoFit():
            self.contentChangedSize()

    def add(self, widget, row=None, col=None):
        """ Add a widget at position row,col """
        if widget.hasAnchor():
            raise Exception("Can not add widget with anchor in datatable.")
        else:
            if row is None:
                if col is None:
                    row, col = self.matrix.firstHole()
                if row is None:
                    row, col = self.matrix.firstHoleInCol(col=col)
                if col is None:
                    row, col = self.matrix.firstHoleInRow(row=row)
            else:
                if widget.parent != self:
                    raise Exception("Parent is not datatable.")
                if self.matrix.get(row, col) != self.matrix.default:
                    raise Exception("Trying to add a widget over another widget.")
            self.matrix.set(widget, row, col)
            if self.isAutoFit():
                self._checkRowsColsSize(widget, col, row)
                self.updateContentPosition()
                Container.contentChangedSize(self)

    def _calcColWidth(self, col):
        width = 0
        for row in range(0, self.matrix.getRowsNbr()):
            widget = self.matrix.get(row, col)
            if widget:
                width = max(width, widget.width)

        return width

    def _calcRowHeight(self, row):
        height = 0
        for col in range(0, self.matrix.getColsNbr()):
            widget = self.matrix.get(row, col)
            if widget:
                height = max(height, widget.height)

        return height

    def _updateRowColSize(self, row, col):
        self.rowsHeight[row] = self._calcRowHeight(row)
        self.colsWidth[col] = self._calcColWidth(col)

    def deleteAtPositionAndDestroy(self, row, col):
        widget = self.deleteAtPosition(row, col)
        widget.destroy()

    def deleteAndDestroy(self, widget):
        self.delete(widget)
        widget.destroy()

    def delete(self, widget):
        """ Remove a specific widget """
        row, col = self.matrix.getIndexes(widget)
        return self.deleteAtPosition(row, col)

    def getWidgetPos(self, widget):
        return self.matrix.getIndexes(widget)

    def destroyLine(self, row):
        for col in range(0, self.matrix.getColsNbr()):
            widget = self.deleteAtPosition(row, col)
            widget.destroy()

        self.reorganize()

    def deleteAtPosition(self, row, col):
        """ Delete the widget at position i,j """
        widget = self.matrix.get(row, col)
        if not widget:
            raise f"There is nothing to delete. {row} {col}"
        widget.setParent(self.parent)
        self.matrix.delete(row, col)
        if self.isAutoFit():
            self._updateRowColSize(row, col)
            self.updateContentPosition()
            Container.contentChangedSize(self)
        return widget

    def setInternalMargins(self, right, bottom):
        """ Set the margin between cells. """
        self.internalMargins = [
         right, bottom]
        if self.isAutoFit():
            self.updateContentPosition()

    def _checkRowsColsSize(self, widget, col, row):
        for cRow in range(0, row):
            if cRow not in self.rowsHeight:
                self.rowsHeight[cRow] = 0

        for cCol in range(0, col):
            if cCol not in self.colsWidth:
                self.colsWidth[cCol] = 0

        if row not in self.rowsHeight:
            self.rowsHeight[row] = widget.height
        else:
            self.rowsHeight[row] = max(widget.height, self.rowsHeight[row])
        if col not in self.colsWidth:
            self.colsWidth[col] = widget.width
        else:
            self.colsWidth[col] = max(widget.width, self.colsWidth[col])

    def updateContentPosition(self):
        """ This function must be called when margin are changed, or a widget is added. """
        x = 0
        y = 0
        for row in range(0, self.matrix.getRowsNbr()):
            for col in range(0, self.matrix.getColsNbr()):
                widget = self.matrix.get(row, col)
                if widget:
                    widget.setPosition(x, y)
                x += self.colsWidth[col] + self.internalMargins[0]

            x = 0
            y += self.rowsHeight[row] + self.internalMargins[1]

    def _setContentHeight(self):
        self._contentHeight += self.internalMargins[1]
        Container._setContentHeight(self)

    def _setContentWidth(self):
        self._contentWidth += self.internalMargins[0]
        Container._setContentWidth(self)


class PageDatatable(Datatable):

    def __init__(self, parent, maxRows=3, maxCols=3, position=(0, 0), size=(0, 0), draggable=False, visible=True):
        self.page = 0
        Datatable.__init__(self, parent, 0, maxCols, position, size, draggable, visible)
        self.rowsByPage = maxRows

    def reorganize(self):
        self._hidePage(self.page)
        maxPage = self.getMaxPage()
        Datatable.reorganize(self)
        if maxPage != self.getMaxPage():
            self._setPage(self.page - 1)
        else:
            self._setPage(self.page)

    def getCurrentPage(self):
        return self.page

    def isInPage(self, row):
        if row < self.page * self.rowsByPage + self.rowsByPage:
            return True
        else:
            return False

    def add(self, widget, row=None, col=None):
        if row is None:
            if col is None:
                row, col = self.matrix.firstHole()
            if row is None:
                row, col = self.matrix.firstHoleInCol(col)
            if col is None:
                row, col = self.matrix.firstHoleInRow(row)
        else:
            if not self.isInPage(row=row):
                if widget.visible:
                    widget.hide()
        Datatable.add(self, widget, row=row, col=col)

    def _hidePage(self, page):
        fit = self.getFit()
        self.setManualFit()
        for row in range(page * self.rowsByPage, page * self.rowsByPage + self.rowsByPage):
            for col in range(0, self.matrix.getColsNbr()):
                widget = self.matrix.get(row, col)
                if widget:
                    widget.hide()

        self.setFit(fit)

    def _showPage(self, page):
        fit = self.getFit()
        self.setManualFit()
        for row in range(page * self.rowsByPage, page * self.rowsByPage + self.rowsByPage):
            for col in range(0, self.matrix.getColsNbr()):
                widget = self.matrix.get(row, col)
                if widget:
                    widget.show()

        self.setFit(fit)

    def getMaxPage(self):
        return max(1, int(math.ceil(self.getRowsNbr() / float(self.rowsByPage))))

    def nextPage(self):
        self.setPage(self.page + 1)

    def backPage(self):
        self.setPage(self.page - 1)

    def lastPage(self):
        self.setPage(self.getMaxPage())

    def firstPage(self):
        self.setPage(0)

    def _setPage(self, page):
        page = clamp(page, 0, self.getMaxPage() - 1)
        self.page = page
        self._showPage(page)

    def setPage(self, page):
        """ Go to page, page. """
        self._hidePage(self.page)
        self._setPage(page)
        if self.isAutoFit():
            self.updateContentPosition()
            self.contentChangedSize()

    def updateContentPosition(self):
        """ This function must be called when margin are changed, or a widget is added. """
        x = 0
        y = 0
        for row in range(0, self.matrix.getRowsNbr()):
            if row % self.rowsByPage == 0:
                y = 0
            for col in range(0, self.matrix.getColsNbr()):
                widget = self.matrix.get(row, col)
                if widget:
                    widget.setPosition(x, y)
                x += self.colsWidth[col] + self.internalMargins[0]

            x = 0
            y += self.rowsHeight[row] + self.internalMargins[1]


class CustomPageLabel(Label):
    return


class PageContainer(Container):
    __doc__ = " Contains organized data and pages. "

    def __init__(self, parent, maxCols=3, maxRows=3, position=(0, 0), size=(0, 0), draggable=False, visible=True, slash=True, spacePadding=1):
        Container.__init__(self, parent, position, size, draggable, visible)
        self.nextButton = Button(self, text="", style=(styleDB.rightArrowButtonStyle), size=(22,
                                                                                             23), autosize=(False,
                                                                                                            False))
        self.backButton = Button(self, text="", style=(styleDB.leftArrowButtonStyle), size=(22,
                                                                                            23), autosize=(False,
                                                                                                           False))
        self.nextButton.addCallback("onMouseLeftClick", self.nextPage)
        self.backButton.addCallback("onMouseLeftClick", self.backPage)
        self.datatable = PageDatatable(self, maxRows, maxCols)
        self.spacePadding = spacePadding
        self.slash = slash
        self.pageLabel = CustomPageLabel(self, text=f'1{" / " if self.slash else " " * self.spacePadding}{self.datatable.getMaxPage()}')
        self.buttonPositionFixed = False

    def setLabelSpacing(self, value):
        self.spacePadding = value
        self._updatePageText()

    def setAutoFit(self):
        self.datatable.setAutoFit()
        Container.setAutoFit(self)

    def setManualFit(self):
        self.datatable.setManualFit()
        Container.setManualFit(self)

    def getTableWidgets(self):
        return self.datatable.getWidgets()

    def empty(self):
        self.datatable.empty()

    def emptyAndDestroy(self):
        self.datatable.emptyAndDestroy()

    def emptyAndHide(self):
        self.datatable.emptyAndHide()

    def setNextButtonPosition(self, x, y):
        self.nextButton.setPosition(x, y)

    def setBackButtonPosition(self, x, y):
        self.backButton.setPosition(x, y)

    def setPageNumberPosition(self, x, y):
        self.pageLabel.setPosition(x, y)

    def _updatePageText(self):
        self.pageLabel.text = f'{self.datatable.getCurrentPage() + 1}{" / " if self.slash else " " * self.spacePadding}{self.datatable.getMaxPage()}'

    def nextPage(self, widget, x, y, modifiers):
        self.datatable.nextPage()
        self._updatePageText()
        self.updateContentPosition()

    def backPage(self, widget, x, y, modifiers):
        self.datatable.backPage()
        self._updatePageText()
        self.updateContentPosition()

    def setInternalMargins(self, right, bottom):
        self.datatable.setInternalMargins(right, bottom)
        self.updateContentPosition()

    def updateContentPosition(self):
        if self.buttonPositionFixed:
            return
        height = self.datatable.getSize()[1]
        if height > self.nextButton.relativeY:
            self.nextButton.setPosition(30, height)
            self.backButton.setPosition(0, height)
            self.pageLabel.setPosition(60, height)

    def add(self, widget, row=None, col=None):
        if not widget.parent == self:
            if widget.parent != self.datatable:
                raise Exception("Parent is not pageContainer")
        else:
            if widget.parent == self:
                widget.setParent(self.datatable)
            self.datatable.add(widget, row, col)
            self._updatePageText()
            if self.isAutoFit():
                self.updateContentPosition()

    def delete(self, widget):
        """ Delete a widget and reorganize the table """
        self.datatable.delete(widget)
        self.updateContentPosition()

    def deleteAndDestroy(self, widget):
        self.delete(widget)
        widget.destroy()

    def deleteAtPosition(self, row, col):
        self.datatable.deleteAtPosition(row, col)
        self.updateContentPosition()

    def deleteAtPositionAndDestroy(self, row, col):
        widget = self.deleteAtPosition(row, col)
        if not widget:
            raise Exception("Trying to destroy unexisting widget.")
        widget.destroy()

    def reorganize(self):
        self.datatable.reorganize()
        self._updatePageText()
        self.updateContentPosition()

    def contentChangedSize(self):
        self.updateContentPosition()
        Container.contentChangedSize(self)

    def fitToContent(self):
        self.datatable.fitToContent()
        self.updateContentPosition()
        Container.fitToContent(self)
