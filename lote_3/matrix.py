# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\maths\matrix.py
"""
Created on 1 juil. 2011

@author: Kami
"""

class Matrix(object):

    def __init__(self, maxRows=0, maxCols=0, default=False, indexes=False):
        self.data = {}
        self.default = default
        self.colsNbr = 0
        self.rowsNbr = 0
        self.maxRows = maxRows
        self.maxCols = maxCols
        if indexes:
            self.indexes = {}
        else:
            self.indexes = False

    def getIndexes(self, value):
        if self.indexes == False:
            raise Exception("Indexes are not activated for this table")
        if value not in self.indexes:
            raise Exception("The value is not indexed in the table")
        return self.indexes[value]

    def firstHole(self):
        if not self.maxRows:
            if not self.maxCols:
                raise Exception("The max values of rows or cols aren't set. Impossible to add without specifying one of them.")
        elif self.maxCols and self.maxRows:
            for row in range(0, self.maxRows):
                for col in range(0, self.maxCols):
                    if self.get(row, col) == self.default:
                        return (
                         row, col)

        elif self.maxCols:
            for col in range(0, self.maxCols):
                for row in range(0, self.rowsNbr):
                    if self.get(row, col) == self.default:
                        return (
                         row, col)

            return (
             self.rowsNbr, 0)
        if self.maxRows:
            for row in range(0, self.maxRows):
                for col in range(0, self.colsNbr):
                    if self.get(row, col) == self.default:
                        return (
                         row, col)

            return (
             0, self.colsNbr)
        raise Exception("Unable to find a hole in the matrix...")

    def firstHoleInRow(self, row):
        """return the position of the first hole """
        col = 0
        for col in range(0, self.maxCols):
            if self.get(row, col) == self.default:
                return (
                 row, col)

        return (
         row, self.colsNbr)

    def firstHoleInCol(self, col):
        """return the position of the first hole """
        row = 0
        for row in range(0, self.maxRows):
            if self.get(row, col) == self.default:
                return (
                 row, col)

        return (
         self.rowsNbr, col)

    def getMaxCols(self):
        return self.maxCols

    def getMaxRows(self):
        return self.maxRows

    def getColsNbr(self):
        return self.colsNbr

    def getRowsNbr(self):
        return self.rowsNbr

    def isRowEmpty(self, row):
        for col in range(0, self.colsNbr):
            if self.get(row, col) != self.default:
                return False

        return True

    def isColEmpty(self, col):
        for row in range(0, self.rowsNbr):
            if self.get(row, col) != self.default:
                return False

        return True

    def _deleteRow(self, row):
        del self.data[row]
        self.rowsNbr -= 1

    def _deleteCol(self, col):
        for row in range(0, self.maxRows):
            self._del(row, col)

        self.colsNbr -= 1

    def deleteLastRows(self):
        """ Check the last Row and delete them if empty. """
        while self.isRowEmpty(self.getRowsNbr() - 1) and self.getRowsNbr() > 0:
            self._deleteRow(self.getRowsNbr() - 1)

    def deleteLastCols(self):
        """ Check the last Col and delete them if empty. """
        while self.isColEmpty(self.getColsNbr() - 1) and self.getColsNbr() > 0:
            self._deleteCol(self.getColsNbr() - 1)

    def deleteLastIfEmpty(self):
        self.deleteLastCols()
        self.deleteLastRows()

    def deleteValue(self, value):
        row, col = self.getIndexes(value)
        self.delete(row, col)

    def delete(self, row, col):
        """ Delete the element at position i, j. do not reorganize table. """
        value = self.get(row, col)
        if self.indexes is not False:
            if value not in self.indexes:
                raise Exception("Value does not exist.")
            del self.indexes[value]
        self._del(row, col)
        self.deleteLastIfEmpty()

    def append(self, value, row, col):
        """ Assume that each case is a list. """
        if row in self.data:
            if col not in self.data[row]:
                self.data[row][col] = []
        else:
            self.data[row] = {}
            self.data[row][col] = []
        self.data[row][col].append(value)

    def set(self, value, row, col):
        """ Set the value of element in position i, j. Change the number of Col & lines. """
        if row in self.data:
            self.data[row][col] = value
        else:
            self.data[row] = {}
            self.data[row][col] = value
        self.colsNbr = max(self.colsNbr, col + 1)
        self.rowsNbr = max(self.rowsNbr, row + 1)
        if self.indexes is not False:
            self.indexes[value] = (
             row, col)

    def get(self, row, col):
        """ Get the value of element at position i, j. If no element there, return default value. """
        try:
            return self.data[row][col]
        except KeyError:
            return self.default

    def getAll(self):
        values = []
        for row in self.data:
            for col in self.data[row]:
                value = self.get(row, col)
                if value != self.default:
                    values.extend(value)

        return values

    def getAllSingle(self):
        values = []
        for row in self.data:
            for col in self.data[row]:
                value = self.get(row, col)
                if value != self.default:
                    values.append(value)

        return values

    def _del(self, row, col):
        if row in self.data:
            if col in self.data[row]:
                del self.data[row][col]

    def _convertToCoords(self, number):
        if not self.maxCols:
            raise Exception("The matrix doesn't have bounds. Impossible to convert to coords.")
        row = int(number / self.getMaxCols())
        col = number % self.getMaxCols()
        return (row, col)

    def getByNumber(self, number):
        return (self.get)(*self._convertToCoords(number))

    def setByNumber(self, value, number):
        (self.set)(value, *self._convertToCoords(number))

    def setByCoord(self, value, row, col):
        self.set(value, row, col)

    def _cloneData(self):
        cdata = {}
        for row in range(0, self.rowsNbr):
            cdata[row] = {}
            for col in range(0, self.colsNbr):
                cdata[row][col] = self.get(row, col)

        return cdata

    def fillHoles(self):
        """ fill the empty hole in the matrix with the next value found. """
        cdata = self._cloneData()
        rowsNbr = self.rowsNbr
        colsNbr = self.colsNbr
        self.colsNbr = 0
        self.rowsNbr = 0
        self.data = {}
        if self.indexes is not False:
            self.indexes = {}
        number = 0
        for row in range(0, rowsNbr):
            for col in range(0, colsNbr):
                if cdata[row][col] != self.default:
                    self.setByNumber(cdata[row][col], number)
                    number += 1
