# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\plugins\__init__.py
"""
Plugins for services implemented in Twisted.

Plugins go in directories on your PYTHONPATH named twisted/plugins:
this is the only place where an __init__.py is necessary, thanks to
the __path__ variable.

@author: Jp Calderone
@author: Glyph Lefkowitz
"""
from twisted.plugin import pluginPackagePaths
__path__.extend(pluginPackagePaths(__name__))
__all__ = []
