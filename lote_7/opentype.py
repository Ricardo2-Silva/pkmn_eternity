# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyasn1\type\opentype.py
__all__ = [
 "OpenType"]

class OpenType(object):
    __doc__ = "Create ASN.1 type map indexed by a value\n\n    The *DefinedBy* object models the ASN.1 *DEFINED BY* clause which maps\n    values to ASN.1 types in the context of the ASN.1 SEQUENCE/SET type.\n\n    OpenType objects are duck-type a read-only Python :class:`dict` objects,\n    however the passed `typeMap` is stored by reference.\n\n    Parameters\n    ----------\n    name: :py:class:`str`\n        Field name\n\n    typeMap: :py:class:`dict`\n        A map of value->ASN.1 type. It's stored by reference and can be\n        mutated later to register new mappings.\n\n    Examples\n    --------\n    .. code-block:: python\n\n        openType = OpenType(\n            'id',\n            {1: Integer(),\n             2: OctetString()}\n        )\n        Sequence(\n            componentType=NamedTypes(\n                NamedType('id', Integer()),\n                NamedType('blob', Any(), openType=openType)\n            )\n        )\n    "

    def __init__(self, name, typeMap=None):
        self._OpenType__name = name
        if typeMap is None:
            self._OpenType__typeMap = {}
        else:
            self._OpenType__typeMap = typeMap

    @property
    def name(self):
        return self._OpenType__name

    def values(self):
        return self._OpenType__typeMap.values()

    def keys(self):
        return self._OpenType__typeMap.keys()

    def items(self):
        return self._OpenType__typeMap.items()

    def __contains__(self, key):
        return key in self._OpenType__typeMap

    def __getitem__(self, key):
        return self._OpenType__typeMap[key]

    def __iter__(self):
        return iter(self._OpenType__typeMap)
