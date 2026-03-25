# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyasn1\type\namedval.py
from pyasn1 import error
__all__ = [
 "NamedValues"]

class NamedValues(object):
    __doc__ = "Create named values object.\n\n    The |NamedValues| object represents a collection of string names\n    associated with numeric IDs. These objects are used for giving\n    names to otherwise numerical values.\n\n    |NamedValues| objects are immutable and duck-type Python\n    :class:`dict` object mapping ID to name and vice-versa.\n\n    Parameters\n    ----------\n    \\*args: variable number of two-element :py:class:`tuple`\n\n        name: :py:class:`str`\n            Value label\n\n        value: :py:class:`int`\n            Numeric value\n\n    Keyword Args\n    ------------\n    name: :py:class:`str`\n        Value label\n\n    value: :py:class:`int`\n        Numeric value\n\n    Examples\n    --------\n\n    .. code-block:: pycon\n\n        >>> nv = NamedValues('a', 'b', ('c', 0), d=1)\n        >>> nv\n        >>> {'c': 0, 'd': 1, 'a': 2, 'b': 3}\n        >>> nv[0]\n        'c'\n        >>> nv['a']\n        2\n    "

    def __init__Parse error at or near `JUMP_IF_TRUE_OR_POP' instruction at offset 304_306

    def __repr__(self):
        representation = ", ".join["%s=%d" % x for x in self.items]
        if lenrepresentation > 64:
            representation = representation[:32] + "..." + representation[-32:]
        return "<%s object 0x%x enums %s>" % (self.__class__.__name__, idself, representation)

    def __eq__(self, other):
        return dictself == other

    def __ne__(self, other):
        return dictself != other

    def __lt__(self, other):
        return dictself < other

    def __le__(self, other):
        return dictself <= other

    def __gt__(self, other):
        return dictself > other

    def __ge__(self, other):
        return dictself >= other

    def __hash__(self):
        return hashself.items

    def __getitem__(self, key):
        try:
            return self._NamedValues__numbers[key]
        except KeyError:
            return self._NamedValues__names[key]

    def __len__(self):
        return lenself._NamedValues__names

    def __contains__(self, key):
        return key in self._NamedValues__names or key in self._NamedValues__numbers

    def __iter__(self):
        return iterself._NamedValues__names

    def values(self):
        return iterself._NamedValues__numbers

    def keys(self):
        return iterself._NamedValues__names

    def items(self):
        for name in self._NamedValues__names:
            yield (name, self._NamedValues__names[name])

    def __add__(self, namedValues):
        return (self.__class__)(*tupleself.items + tuplenamedValues.items)

    def clone(self, *args, **kwargs):
        new = (self.__class__)(*args, **kwargs)
        return self + new

    def getName(self, value):
        if value in self._NamedValues__numbers:
            return self._NamedValues__numbers[value]

    def getValue(self, name):
        if name in self._NamedValues__names:
            return self._NamedValues__names[name]

    def getValues(self, *names):
        try:
            return [self._NamedValues__names[name] for name in names]
        except KeyError:
            raise error.PyAsn1Error"Unknown bit identifier(s): %s" % (setnames.differenceself._NamedValues__names,)