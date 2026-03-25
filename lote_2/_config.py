# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: attr\_config.py
from __future__ import absolute_import, division, print_function
__all__ = [
 "set_run_validators", "get_run_validators"]
_run_validators = True

def set_run_validators(run):
    """
    Set whether or not validators are run.  By default, they are run.
    """
    global _run_validators
    if not isinstance(run, bool):
        raise TypeError("'run' must be bool.")
    _run_validators = run


def get_run_validators():
    """
    Return whether or not validators are run.
    """
    return _run_validators
