# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\logger\_capture.py
"""
Context manager for capturing logs.
"""
from contextlib import contextmanager
from twisted.logger import globalLogPublisher

@contextmanager
def capturedLogs():
    events = []
    observer = events.append
    globalLogPublisher.addObserver(observer)
    yield events
    globalLogPublisher.removeObserver(observer)
