# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyasn1\error.py


class PyAsn1Error(Exception):
    __doc__ = "Create pyasn1 exception object\n\n    The `PyAsn1Error` exception represents generic, usually fatal, error.\n    "


class ValueConstraintError(PyAsn1Error):
    __doc__ = "Create pyasn1 exception object\n\n    The `ValueConstraintError` exception indicates an ASN.1 value\n    constraint violation.\n    "


class SubstrateUnderrunError(PyAsn1Error):
    __doc__ = "Create pyasn1 exception object\n\n    The `SubstrateUnderrunError` exception indicates insufficient serialised\n    data on input of a deserialisation routine.\n    "
