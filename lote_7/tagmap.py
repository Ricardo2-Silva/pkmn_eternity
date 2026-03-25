# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyasn1\type\tagmap.py
from pyasn1 import error
__all__ = [
 "TagMap"]

class TagMap(object):
    __doc__ = "Map *TagSet* objects to ASN.1 types\n\n    Create an object mapping *TagSet* object to ASN.1 type.\n\n    *TagMap* objects are immutable and duck-type read-only Python\n    :class:`dict` objects holding *TagSet* objects as keys and ASN.1\n    type objects as values.\n\n    Parameters\n    ----------\n    presentTypes: :py:class:`dict`\n        Map of :class:`~pyasn1.type.tag.TagSet` to ASN.1 objects considered\n        as being unconditionally present in the *TagMap*.\n\n    skipTypes: :py:class:`dict`\n        A collection of :class:`~pyasn1.type.tag.TagSet` objects considered\n        as absent in the *TagMap* even when *defaultType* is present.\n\n    defaultType: ASN.1 type object\n        An ASN.1 type object callee *TagMap* returns for any *TagSet* key not present\n        in *presentTypes* (unless given key is present in *skipTypes*).\n    "

    def __init__(self, presentTypes=None, skipTypes=None, defaultType=None):
        self._TagMap__presentTypes = presentTypes or {}
        self._TagMap__skipTypes = skipTypes or {}
        self._TagMap__defaultType = defaultType

    def __contains__(self, tagSet):
        return tagSet in self._TagMap__presentTypes or self._TagMap__defaultType is not None and tagSet not in self._TagMap__skipTypes

    def __getitem__(self, tagSet):
        try:
            return self._TagMap__presentTypes[tagSet]
        except KeyError:
            if self._TagMap__defaultType is None:
                raise KeyError()
            elif tagSet in self._TagMap__skipTypes:
                raise error.PyAsn1Error("Key in negative map")
            else:
                return self._TagMap__defaultType

    def __iter__(self):
        return iter(self._TagMap__presentTypes)

    def __repr__(self):
        representation = "%s object at 0x%x" % (self.__class__.__name__, id(self))
        if self._TagMap__presentTypes:
            representation += " present %s" % repr(self._TagMap__presentTypes)
        if self._TagMap__skipTypes:
            representation += " skip %s" % repr(self._TagMap__skipTypes)
        if self._TagMap__defaultType is not None:
            representation += " default %s" % repr(self._TagMap__defaultType)
        return "<%s>" % representation

    @property
    def presentTypes(self):
        """Return *TagSet* to ASN.1 type map present in callee *TagMap*"""
        return self._TagMap__presentTypes

    @property
    def skipTypes(self):
        """Return *TagSet* collection unconditionally absent in callee *TagMap*"""
        return self._TagMap__skipTypes

    @property
    def defaultType(self):
        """Return default ASN.1 type being returned for any missing *TagSet*"""
        return self._TagMap__defaultType

    def getPosMap(self):
        return self.presentTypes

    def getNegMap(self):
        return self.skipTypes

    def getDef(self):
        return self.defaultType
