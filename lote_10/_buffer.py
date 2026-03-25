# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\logger\_buffer.py
"""
Log observer that maintains a buffer.
"""
from collections import deque
from zope.interface import implementer
from ._observer import ILogObserver
_DEFAULT_BUFFER_MAXIMUM = 65536

@implementer(ILogObserver)
class LimitedHistoryLogObserver(object):
    __doc__ = "\n    L{ILogObserver} that stores events in a buffer of a fixed size::\n\n        >>> from twisted.logger import LimitedHistoryLogObserver\n        >>> history = LimitedHistoryLogObserver(5)\n        >>> for n in range(10): history({'n': n})\n        ...\n        >>> repeats = []\n        >>> history.replayTo(repeats.append)\n        >>> len(repeats)\n        5\n        >>> repeats\n        [{'n': 5}, {'n': 6}, {'n': 7}, {'n': 8}, {'n': 9}]\n        >>>\n    "

    def __init__(self, size=_DEFAULT_BUFFER_MAXIMUM):
        """
        @param size: The maximum number of events to buffer.  If L{None}, the
            buffer is unbounded.
        @type size: L{int}
        """
        self._buffer = deque(maxlen=size)

    def __call__(self, event):
        self._buffer.append(event)

    def replayTo(self, otherObserver):
        """
        Re-play the buffered events to another log observer.

        @param otherObserver: An observer to replay events to.
        @type otherObserver: L{ILogObserver}
        """
        for event in self._buffer:
            otherObserver(event)
