# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\_threads\__init__.py
"""
Twisted integration with operating system threads.
"""
from __future__ import absolute_import, division, print_function
from ._threadworker import ThreadWorker, LockWorker
from ._ithreads import IWorker, AlreadyQuit
from ._team import Team
from ._memory import createMemoryWorker
from ._pool import pool
__all__ = [
 'ThreadWorker', 
 'LockWorker', 
 'IWorker', 
 'AlreadyQuit', 
 'Team', 
 'createMemoryWorker', 
 'pool']
