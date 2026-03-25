# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: attr\_version_info.py
from __future__ import absolute_import, division, print_function
from functools import total_ordering
from ._funcs import astuple
from ._make import attrib, attrs

@total_ordering
@attrs(eq=False, order=False, slots=True, frozen=True)
class VersionInfo(object):
    __doc__ = '\n    A version object that can be compared to tuple of length 1--4:\n\n    >>> attr.VersionInfo(19, 1, 0, "final")  <= (19, 2)\n    True\n    >>> attr.VersionInfo(19, 1, 0, "final") < (19, 1, 1)\n    True\n    >>> vi = attr.VersionInfo(19, 2, 0, "final")\n    >>> vi < (19, 1, 1)\n    False\n    >>> vi < (19,)\n    False\n    >>> vi == (19, 2,)\n    True\n    >>> vi == (19, 2, 1)\n    False\n\n    .. versionadded:: 19.2\n    '
    year = attrib(type=int)
    minor = attrib(type=int)
    micro = attrib(type=int)
    releaselevel = attrib(type=str)

    @classmethod
    def _from_version_string(cls, s):
        """
        Parse *s* and return a _VersionInfo.
        """
        v = s.split(".")
        if len(v) == 3:
            v.append("final")
        return cls(year=(int(v[0])),
          minor=(int(v[1])),
          micro=(int(v[2])),
          releaselevel=(v[3]))

    def _ensure_tuple(self, other):
        """
        Ensure *other* is a tuple of a valid length.

        Returns a possibly transformed *other* and ourselves as a tuple of
        the same length as *other*.
        """
        if self.__class__ is other.__class__:
            other = astuple(other)
        elif not isinstance(other, tuple):
            raise NotImplementedError
        if not 1 <= len(other) <= 4:
            raise NotImplementedError
        return (astuple(self)[:len(other)], other)

    def __eq__(self, other):
        try:
            us, them = self._ensure_tuple(other)
        except NotImplementedError:
            return NotImplemented
        else:
            return us == them

    def __lt__(self, other):
        try:
            us, them = self._ensure_tuple(other)
        except NotImplementedError:
            return NotImplemented
        else:
            return us < them
