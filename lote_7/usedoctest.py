# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: lxml\usedoctest.py
"""Doctest module for XML comparison.

Usage::

   >>> import lxml.usedoctest
   >>> # now do your XML doctests ...

See `lxml.doctestcompare`
"""
from lxml import doctestcompare
doctestcompare.temp_install(del_module=__name__)
