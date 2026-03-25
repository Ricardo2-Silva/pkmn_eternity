# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: decimal.py
try:
    from _decimal import *
    from _decimal import __doc__
    from _decimal import __version__
    from _decimal import __libmpdec_version__
except ImportError:
    from _pydecimal import *
    from _pydecimal import __doc__
    from _pydecimal import __version__
    from _pydecimal import __libmpdec_version__
