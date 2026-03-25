# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\cred\error.py
"""
Cred errors.
"""
from __future__ import division, absolute_import

class Unauthorized(Exception):
    __doc__ = "Standard unauthorized error."


class LoginFailed(Exception):
    __doc__ = "\n    The user's request to log in failed for some reason.\n    "


class UnauthorizedLogin(LoginFailed, Unauthorized):
    __doc__ = "The user was not authorized to log in.\n    "


class UnhandledCredentials(LoginFailed):
    __doc__ = "A type of credentials were passed in with no knowledge of how to check\n    them.  This is a server configuration error - it means that a protocol was\n    connected to a Portal without a CredentialChecker that can check all of its\n    potential authentication strategies.\n    "


class LoginDenied(LoginFailed):
    __doc__ = "\n    The realm rejected this login for some reason.\n\n    Examples of reasons this might be raised include an avatar logging in\n    too frequently, a quota having been fully used, or the overall server\n    load being too high.\n    "
