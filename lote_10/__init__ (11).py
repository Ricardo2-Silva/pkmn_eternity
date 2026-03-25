# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\__init__.py
"""
Twisted: The Framework Of Your Internet.
"""
from twisted._version import __version__ as version
__version__ = version.short()
from incremental import Version
from twisted.python.deprecate import deprecatedModuleAttribute
deprecatedModuleAttribute(Version("Twisted", 20, 3, 0), "morituri nolumus mori", "twisted", "news")
