# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: attr\exceptions.py
from __future__ import absolute_import, division, print_function

class FrozenError(AttributeError):
    __doc__ = "\n    A frozen/immutable instance or attribute haave been attempted to be\n    modified.\n\n    It mirrors the behavior of ``namedtuples`` by using the same error message\n    and subclassing `AttributeError`.\n\n    .. versionadded:: 20.1.0\n    "
    msg = "can't set attribute"
    args = [msg]


class FrozenInstanceError(FrozenError):
    __doc__ = "\n    A frozen instance has been attempted to be modified.\n\n    .. versionadded:: 16.1.0\n    "


class FrozenAttributeError(FrozenError):
    __doc__ = "\n    A frozen attribute has been attempted to be modified.\n\n    .. versionadded:: 20.1.0\n    "


class AttrsAttributeNotFoundError(ValueError):
    __doc__ = "\n    An ``attrs`` function couldn't find an attribute that the user asked for.\n\n    .. versionadded:: 16.2.0\n    "


class NotAnAttrsClassError(ValueError):
    __doc__ = "\n    A non-``attrs`` class has been passed into an ``attrs`` function.\n\n    .. versionadded:: 16.2.0\n    "


class DefaultAlreadySetError(RuntimeError):
    __doc__ = "\n    A default has been set using ``attr.ib()`` and is attempted to be reset\n    using the decorator.\n\n    .. versionadded:: 17.1.0\n    "


class UnannotatedAttributeError(RuntimeError):
    __doc__ = "\n    A class with ``auto_attribs=True`` has an ``attr.ib()`` without a type\n    annotation.\n\n    .. versionadded:: 17.3.0\n    "


class PythonTooOldError(RuntimeError):
    __doc__ = "\n    It was attempted to use an ``attrs`` feature that requires a newer Python\n    version.\n\n    .. versionadded:: 18.2.0\n    "


class NotCallableError(TypeError):
    __doc__ = "\n    A ``attr.ib()`` requiring a callable has been set with a value\n    that is not callable.\n\n    .. versionadded:: 19.2.0\n    "

    def __init__(self, msg, value):
        super(TypeError, self).__init__(msg, value)
        self.msg = msg
        self.value = value

    def __str__(self):
        return str(self.msg)
