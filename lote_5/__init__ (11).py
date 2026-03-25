# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: cryptography\__init__.py
from __future__ import absolute_import, division, print_function
import sys, warnings
from cryptography.__about__ import __author__, __copyright__, __email__, __license__, __summary__, __title__, __uri__, __version__
from cryptography.utils import CryptographyDeprecationWarning
__all__ = [
 '__title__', 
 '__summary__', 
 '__uri__', 
 '__version__', 
 '__author__', 
 '__email__', 
 '__license__', 
 '__copyright__']
if sys.version_info[0] == 2:
    warnings.warn("Python 2 is no longer supported by the Python core team. Support for it is now deprecated in cryptography, and will be removed in a future release.",
      CryptographyDeprecationWarning,
      stacklevel=2)
if sys.version_info[:2] == (3, 5):
    warnings.warn("Python 3.5 support will be dropped in the next release ofcryptography. Please upgrade your Python.",
      CryptographyDeprecationWarning,
      stacklevel=2)
