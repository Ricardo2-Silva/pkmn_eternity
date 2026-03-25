# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: zope\interface\exceptions.py
"""Interface-specific exceptions
"""

class Invalid(Exception):
    __doc__ = "A specification is violated\n    "


class DoesNotImplement(Invalid):
    __doc__ = " This object does not implement "

    def __init__(self, interface):
        self.interface = interface

    def __str__(self):
        return "An object does not implement interface %(interface)s\n\n        " % self.__dict__


class BrokenImplementation(Invalid):
    __doc__ = "An attribute is not completely implemented.\n    "

    def __init__(self, interface, name):
        self.interface = interface
        self.name = name

    def __str__(self):
        return "An object has failed to implement interface %(interface)s\n\n        The %(name)s attribute was not provided.\n        " % self.__dict__


class BrokenMethodImplementation(Invalid):
    __doc__ = "An method is not completely implemented.\n    "

    def __init__(self, method, mess):
        self.method = method
        self.mess = mess

    def __str__(self):
        return "The implementation of %(method)s violates its contract\n        because %(mess)s.\n        " % self.__dict__


class InvalidInterface(Exception):
    __doc__ = "The interface has invalid contents\n    "


class BadImplements(TypeError):
    __doc__ = "An implementation assertion is invalid\n\n    because it doesn't contain an interface or a sequence of valid\n    implementation assertions.\n    "
