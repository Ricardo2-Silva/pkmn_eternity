# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: zope\interface\ro.py
"""Compute a resolution order for an object and its bases
"""
__docformat__ = "restructuredtext"

def _mergeOrderings(orderings):
    """Merge multiple orderings so that within-ordering order is preserved

    Orderings are constrained in such a way that if an object appears
    in two or more orderings, then the suffix that begins with the
    object must be in both orderings.

    For example:

    >>> _mergeOrderings([
    ... ['x', 'y', 'z'],
    ... ['q', 'z'],
    ... [1, 3, 5],
    ... ['z']
    ... ])
    ['x', 'y', 'q', 1, 3, 5, 'z']

    """
    seen = {}
    result = []
    for ordering in reversed(orderings):
        for o in reversed(ordering):
            if o not in seen:
                seen[o] = 1
                result.insert(0, o)

    return result


def _flatten(ob):
    result = [
     ob]
    i = 0
    for ob in iter(result):
        i += 1
        result[i:i] = ob.__bases__

    return result


def ro(object):
    """Compute a "resolution order" for an object
    """
    return _mergeOrderings([_flatten(object)])
