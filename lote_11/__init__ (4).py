# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\python\__init__.py
"""
Twisted Python: Utilities and Enhancements for Python.
"""
from __future__ import absolute_import, division
from .compat import unicode
from .versions import Version
from .deprecate import deprecatedModuleAttribute
deprecatedModuleAttribute(Version("Twisted", 16, 5, 0), "Please use constantly from PyPI instead.", "twisted.python", "constants")
deprecatedModuleAttribute(Version("Twisted", 17, 5, 0), "Please use hyperlink from PyPI instead.", "twisted.python", "url")
del Version
del deprecatedModuleAttribute
del unicode
