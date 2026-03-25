# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\gui\lines.py
from client.control.gui.button import Button
from client.control.gui.container import Container
from client.control.gui.tables import Datatable
from client.data.gui import styleDB
from client.control.gui.label import Label
from client.control.gui.widget import Widget, StylizedWidget
from client.data.utils.color import Color

class Line(Button):
    __doc__ = " Special button used for line tables. Not to be used directly "

    def __init__(self, parent, linkedDatatable, row):
        self.linkedDatatable = linkedDatatable
        self.row = row
        Button.__init__(self, parent, text="", style=(styleDB.whiteLineStyle), size=(20,
                                                                                     10), autosize=(False,
                                                                                                    False))


class LineTable(Container):
    __doc__ = " A line table is a table with callbacks on lines. Lines can contains anything and are columns most of the time. "

    def __init__(self, parent, maxCols=0, position=(0, 0), visible=True):
        Container.__init__(self, parent, position, visible=True)
        self.datatableBehind = Datatable(self, maxCols=1)
        self.datatableBehind.setInternalMargins(0, 1)
        self.datatable = Datatable(self, maxCols=0)
        self.setInternalMargins(1, 1)
        self.colNames = []
        self.colNameRefs = {}

    def setAutoFit(self):
        self.datatable.setAutoFit()
        Container.setAutoFit(self)

    def setManualFit(self):
        self.datatable.setManualFit()
        Container.setManualFit(self)

    def fitToContent(self):
        self.datatable.fitToContent()
        self._updateLineBehind()
        self.updateLineBehindSize()
        self.datatableBehind.fitToContent()
        Container.fitToContent(self)

    def setInternalMargins(self, right, bottom):
        self.datatable.setInternalMargins(right, bottom)
        if self.isAutoFit():
            self.contentChangedSize()

    def contentChangedSize(self):
        Container.contentChangedSize(self)
        fit = self.getFit()
        self.setManualFit()
        self._updateLineBehind()
        self.setFitSilent(fit)

    def childChangedSize(self, child):
        if child == self.datatable:
            if self.isAutoFit():
                self.contentChangedSize()

    def setHeaders(self, headers, style=styleDB.whiteShadowLabelStyle):
        if len(headers) < len(self.colNames):
            raise Exception("Columns number bigger than headers names.")
        for i in range(0, len(self.colNames)):
            self._addData(0, self.colNames[i], Label(text=(headers[i]), style=style))

    def setColumns(self, colNames):
        self.colNames = colNames
        for i in range(0, len(colNames)):
            self.colNameRefs[colNames[i]] = i

        self.datatable.matrix.maxCols = len(colNames)

    def addColumn(self, name):
        if name in self.colNames:
            raise Exception("This column name already exist !")
        pos = len(self.colNames)
        self.colNames.append(name)
        if name in self.colNameRefs:
            raise Exception("Overwriting a column name !")
        self.colNameRefs[name] = pos

    def _updateLineBehind(self):
        for row in range(0, self.datatable.getRowsNbr()):
            lineButton = self.datatableBehind.get(row, 0)
            lineButton.row = row

        self.updateLineBehindSize()
        if self.visible:
            self.datatable.setOnTop()

    def updateLineBehindSize(self):
        fit = self.datatableBehind.getFit()
        self.datatableBehind.setManualFit()
        for row in range(0, self.datatable.getRowsNbr()):
            lineButton = self.datatableBehind.get(row, 0)
            lineButton.setSize(self.datatable.width, self.datatable.getRowHeight(row) - 1)

        self.datatableBehind.fitToContent()
        self.datatableBehind.setFitSilent(fit)

    def getLineButton(self, row):
        return self.datatableBehind.get(row, 0)

    def getLines(self):
        return self.datatableBehind.getWidgets()

    def getData(self, row, colName):
        if colName not in self.colNameRefs:
            raise Exception("This col doesn't exist.")
        col = self.colNameRefs[colName]
        return self.datatable.get(row, col)

    def delData(self, row, colName):
        if colName not in self.colNameRefs:
            raise Exception("This col doesn't exist.")
        col = self.colNameRefs[colName]
        self.datatable.deleteAtPosition(row, col)
        self._updateLineBehind()

    def empty(self):
        self.datatable.empty()
        self.datatableBehind.empty()

    def emptyAndDestroy(self):
        self.datatable.emptyAndDestroy()
        self.datatableBehind.emptyAndDestroy()

    def delLine(self, rowOrLine):
        if not self.datatable.getMaxCols():
            raise Exception("You didn't specify the max columns for the LineTable. Impossible to delete a line. (See maxCols)")
        else:
            row = rowOrLine
            if isinstance(rowOrLine, Line):
                row = rowOrLine.row
            self.datatable.destroyLine(row)
            self.datatableBehind.destroyLine(row)
            if self.isAutoFit():
                self._updateLineBehind()

    def _addData(self, row, colName, widget):
        self.datatable.add(widget, row, self.colNameRefs[colName])

    def addData(self, row=None, **kwargs):
        if row == None:
            row = self.datatable.getRowsNbr()
        if self.datatableBehind.get(row, 0):
            raise Exception("(Linetable) There is already data at this position.")
        fit0 = self.getFit()
        self.setManualFit()
        fit1 = self.datatableBehind.getFit()
        self.datatableBehind.setManualFit()
        fit2 = self.datatable.getFit()
        self.datatable.setManualFit()
        for key in kwargs:
            widget = kwargs[key]
            if not widget.parent == self:
                raise Exception("Parent must be linetable.")
            widget.setParent(self.datatable)
            if not isinstance(widget, Widget):
                raise Exception("Data can only be widgets.")
            if key not in self.colNames:
                raise Exception("Key should be the name of a column. It's not.")
            if self.datatable.get(row, self.colNameRefs[key]):
                raise Exception("There is already a widget at this position.")
            self.datatable.add(widget, row, self.colNameRefs[key])

        lineButton = Line(self.datatableBehind, self.datatable, row)
        self.datatableBehind.add(lineButton, row=row, col=0)
        lineButton.row = row
        self.datatable.setFit(fit2)
        self.datatableBehind.setFit(fit1)
        self.setFit(fit0)
        return self.datatableBehind.get(row, 0)


class Area(StylizedWidget):

    def __init__(self, parent, position, size, styleNormal, styleColor, alpha, color):
        if color != Color.TRANSPARENT:
            StylizedWidget.__init__(self, styleColor, parent, position, size, False, enableEvents=False)
            (self.setColor)(*color)
        else:
            StylizedWidget.__init__(self, styleNormal, parent, position, size, False, enableEvents=False)
        self.setAlpha(alpha)


class ShadowArea(Area):

    def __init__(self, parent, position, size, alpha=20, color=Color.TRANSPARENT):
        Area.__init__(self, parent, position, size, styleDB.shadowWidgetStyle, styleDB.shadowColorWidgetStyle, alpha, color)


class LineRoundedArea(ShadowArea):

    def __init__(self, parent, position, size, alpha=30, color=Color.TRANSPARENT):
        Area.__init__(self, parent, position, size, styleDB.lineRoundedStyle, styleDB.lineFullRoundedStyle, alpha, color)
