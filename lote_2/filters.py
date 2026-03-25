# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: attr\filters.py
"""
Commonly useful filters for `attr.asdict`.
"""
from __future__ import absolute_import, division, print_function
from ._compat import isclass
from ._make import Attribute

def _split_what(what):
    """
    Returns a tuple of `frozenset`s of classes and attributes.
    """
    return (
     frozenset(cls for cls in what if isclass(cls)),
     frozenset(cls for cls in what if isinstance(cls, Attribute)))


def include(*what):
    r"""
    Whitelist *what*.

    :param what: What to whitelist.
    :type what: `list` of `type` or `attr.Attribute`\ s

    :rtype: `callable`
    """
    cls, attrs = _split_what(what)

    def include_(attribute, value):
        return value.__class__ in cls or attribute in attrs

    return include_


def exclude(*what):
    r"""
    Blacklist *what*.

    :param what: What to blacklist.
    :type what: `list` of classes or `attr.Attribute`\ s.

    :rtype: `callable`
    """
    cls, attrs = _split_what(what)

    def exclude_(attribute, value):
        return value.__class__ not in cls and attribute not in attrs

    return exclude_
