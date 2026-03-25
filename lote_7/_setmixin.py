# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: lxml\html\_setmixin.py
from collections import MutableSet

class SetMixin(MutableSet):
    __doc__ = "\n    Mix-in for sets.  You must define __iter__, add, remove\n    "

    def __len__(self):
        length = 0
        for item in self:
            length += 1

        return length

    def __contains__(self, item):
        for has_item in self:
            if item == has_item:
                return True

        return False

    issubset = MutableSet.__le__
    issuperset = MutableSet.__ge__
    union = MutableSet.__or__
    intersection = MutableSet.__and__
    difference = MutableSet.__sub__
    symmetric_difference = MutableSet.__xor__

    def copy(self):
        return set(self)

    def update(self, other):
        self |= other

    def intersection_update(self, other):
        self &= other

    def difference_update(self, other):
        self -= other

    def symmetric_difference_update(self, other):
        self ^= other

    def discard(self, item):
        try:
            self.remove(item)
        except KeyError:
            pass

    @classmethod
    def _from_iterable(cls, it):
        return set(it)
