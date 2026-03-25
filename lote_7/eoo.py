# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyasn1\codec\ber\eoo.py
from pyasn1.type import base
from pyasn1.type import tag
__all__ = [
 "endOfOctets"]

class EndOfOctets(base.AbstractSimpleAsn1Item):
    defaultValue = 0
    tagSet = tag.initTagSet(tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 0))
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = (object.__new__)(cls, *args, **kwargs)
        return cls._instance


endOfOctets = EndOfOctets()
