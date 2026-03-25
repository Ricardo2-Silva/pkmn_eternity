# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\internet\_producer_helpers.py
"""
Helpers for working with producers.
"""
from __future__ import division, absolute_import
from zope.interface import implementer
from twisted.internet.interfaces import IPushProducer
from twisted.internet.task import cooperate
from twisted.python import log
from twisted.python.reflect import safe_str
__all__ = []

@implementer(IPushProducer)
class _PullToPush(object):
    __doc__ = "\n    An adapter that converts a non-streaming to a streaming producer.\n\n    Because of limitations of the producer API, this adapter requires the\n    cooperation of the consumer. When the consumer's C{registerProducer} is\n    called with a non-streaming producer, it must wrap it with L{_PullToPush}\n    and then call C{startStreaming} on the resulting object. When the\n    consumer's C{unregisterProducer} is called, it must call\n    C{stopStreaming} on the L{_PullToPush} instance.\n\n    If the underlying producer throws an exception from C{resumeProducing},\n    the producer will be unregistered from the consumer.\n\n    @ivar _producer: the underling non-streaming producer.\n\n    @ivar _consumer: the consumer with which the underlying producer was\n                     registered.\n\n    @ivar _finished: C{bool} indicating whether the producer has finished.\n\n    @ivar _coopTask: the result of calling L{cooperate}, the task driving the\n                     streaming producer.\n    "
    _finished = False

    def __init__(self, pullProducer, consumer):
        self._producer = pullProducer
        self._consumer = consumer

    def _pull(self):
        """
        A generator that calls C{resumeProducing} on the underlying producer
        forever.

        If C{resumeProducing} throws an exception, the producer is
        unregistered, which should result in streaming stopping.
        """
        while True:
            try:
                self._producer.resumeProducing()
            except:
                log.err(None, "%s failed, producing will be stopped:" % (
                 safe_str(self._producer),))
                try:
                    self._consumer.unregisterProducer()
                except:
                    log.err(None, "%s failed to unregister producer:" % (
                     safe_str(self._consumer),))
                    self._finished = True
                    return

            yield

    def startStreaming(self):
        """
        This should be called by the consumer when the producer is registered.

        Start streaming data to the consumer.
        """
        self._coopTask = cooperate(self._pull())

    def stopStreaming(self):
        """
        This should be called by the consumer when the producer is
        unregistered.

        Stop streaming data to the consumer.
        """
        if self._finished:
            return
        self._finished = True
        self._coopTask.stop()

    def pauseProducing(self):
        """
        @see: C{IPushProducer.pauseProducing}
        """
        self._coopTask.pause()

    def resumeProducing(self):
        """
        @see: C{IPushProducer.resumeProducing}
        """
        self._coopTask.resume()

    def stopProducing(self):
        """
        @see: C{IPushProducer.stopProducing}
        """
        self.stopStreaming()
        self._producer.stopProducing()
