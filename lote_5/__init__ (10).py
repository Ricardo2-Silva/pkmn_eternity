# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: constantly\__init__.py
from constantly._constants import NamedConstant, Names, ValueConstant, Values, FlagConstant, Flags
from ._version import get_versions
__version__ = get_versions()["version"]
del get_versions
__author__ = "Twisted Matrix Laboratories"
__license__ = "MIT"
__copyright__ = "Copyright 2011-2015 {0}".format(__author__)
__all__ = [
 'NamedConstant', 
 'ValueConstant', 
 'FlagConstant', 
 'Names', 
 'Values', 
 'Flags']
