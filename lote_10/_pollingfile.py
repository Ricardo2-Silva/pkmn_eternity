# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\internet\_pollingfile.py
"""
Implements a simple polling interface for file descriptors that don't work with
select() - this is pretty much only useful on Windows.
"""
from __future__ import absolute_import, division
from zope.interface import implementer
from twisted.internet.interfaces import IConsumer, IPushProducer
from twisted.python.compat import unicode
MIN_TIMEOUT = 1e-09
MAX_TIMEOUT = 0.1

class _PollableResource:
    active = True

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False


class _PollingTimer:

    def __init__(self, reactor):
        self.reactor = reactor
        self._resources = []
        self._pollTimer = None
        self._currentTimeout = MAX_TIMEOUT
        self._paused = False

    def _addPollableResource(self, res):
        self._resources.append(res)
        self._checkPollingState()

    def _checkPollingState(self):
        for resource in self._resources:
            if resource.active:
                self._startPolling()
                break
        else:
            self._stopPolling()

    def _startPolling(self):
        if self._pollTimer is None:
            self._pollTimer = self._reschedule()

    def _stopPolling(self):
        if self._pollTimer is not None:
            self._pollTimer.cancel()
            self._pollTimer = None

    def _pause(self):
        self._paused = True

    def _unpause(self):
        self._paused = False
        self._checkPollingState()

    def _reschedule(self):
        if not self._paused:
            return self.reactor.callLater(self._currentTimeout, self._pollEvent)

    def _pollEvent(self):
        workUnits = 0.0
        anyActive = []
        for resource in self._resources:
            if resource.active:
                workUnits += resource.checkWork()
                if resource.active:
                    anyActive.append(resource)

        newTimeout = self._currentTimeout
        if workUnits:
            newTimeout = self._currentTimeout / (workUnits + 1.0)
            if newTimeout < MIN_TIMEOUT:
                newTimeout = MIN_TIMEOUT
        else:
            newTimeout = self._currentTimeout * 2.0
        if newTimeout > MAX_TIMEOUT:
            newTimeout = MAX_TIMEOUT
        self._currentTimeout = newTimeout
        if anyActive:
            self._pollTimer = self._reschedule()


import win32pipe, win32file, win32api, pywintypes

@implementer(IPushProducer)
class _PollableReadPipe(_PollableResource):

    def __init__(self, pipe, receivedCallback, lostCallback):
        self.pipe = pipe
        self.receivedCallback = receivedCallback
        self.lostCallback = lostCallback

    def checkWork(self):
        finished = 0
        fullDataRead = []
        while True:
            try:
                buffer, bytesToRead, result = win32pipe.PeekNamedPipe(self.pipe, 1)
                if not bytesToRead:
                    break
                hr, data = win32file.ReadFile(self.pipe, bytesToRead, None)
                fullDataRead.append(data)
            except win32api.error:
                finished = 1
                break

        dataBuf = (b'').join(fullDataRead)
        if dataBuf:
            self.receivedCallback(dataBuf)
        if finished:
            self.cleanup()
        return len(dataBuf)

    def cleanup(self):
        self.deactivate()
        self.lostCallback()

    def close(self):
        try:
            win32api.CloseHandle(self.pipe)
        except pywintypes.error:
            pass

    def stopProducing(self):
        self.close()

    def pauseProducing(self):
        self.deactivate()

    def resumeProducing(self):
        self.activate()


FULL_BUFFER_SIZE = 65536

@implementer(IConsumer)
class _PollableWritePipe(_PollableResource):

    def __init__(self, writePipe, lostCallback):
        self.disconnecting = False
        self.producer = None
        self.producerPaused = False
        self.streamingProducer = 0
        self.outQueue = []
        self.writePipe = writePipe
        self.lostCallback = lostCallback
        try:
            win32pipe.SetNamedPipeHandleState(writePipe, win32pipe.PIPE_NOWAIT, None, None)
        except pywintypes.error:
            pass

    def close(self):
        self.disconnecting = True

    def bufferFull(self):
        if self.producer is not None:
            self.producerPaused = True
            self.producer.pauseProducing()

    def bufferEmpty(self):
        if self.producer is not None and (not self.streamingProducer or self.producerPaused):
            self.producer.producerPaused = False
            self.producer.resumeProducing()
            return True
        else:
            return False

    def registerProducer(self, producer, streaming):
        """Register to receive data from a producer.

        This sets this selectable to be a consumer for a producer.  When this
        selectable runs out of data on a write() call, it will ask the producer
        to resumeProducing(). A producer should implement the IProducer
        interface.

        FileDescriptor provides some infrastructure for producer methods.
        """
        if self.producer is not None:
            raise RuntimeError("Cannot register producer %s, because producer %s was never unregistered." % (
             producer, self.producer))
        if not self.active:
            producer.stopProducing()
        else:
            self.producer = producer
            self.streamingProducer = streaming
        if not streaming:
            producer.resumeProducing()

    def unregisterProducer(self):
        """Stop consuming data from a producer, without disconnecting.
        """
        self.producer = None

    def writeConnectionLost(self):
        self.deactivate()
        try:
            win32api.CloseHandle(self.writePipe)
        except pywintypes.error:
            pass

        self.lostCallback()

    def writeSequence(self, seq):
        """
        Append a C{list} or C{tuple} of bytes to the output buffer.

        @param seq: C{list} or C{tuple} of C{str} instances to be appended to
            the output buffer.

        @raise TypeError: If C{seq} contains C{unicode}.
        """
        if unicode in map(type, seq):
            raise TypeError("Unicode not allowed in output buffer.")
        self.outQueue.extend(seq)

    def write(self, data):
        """
        Append some bytes to the output buffer.

        @param data: C{str} to be appended to the output buffer.
        @type data: C{str}.

        @raise TypeError: If C{data} is C{unicode} instead of C{str}.
        """
        if isinstance(data, unicode):
            raise TypeError("Unicode not allowed in output buffer.")
        else:
            if self.disconnecting:
                return
            self.outQueue.append(data)
            if sum(map(len, self.outQueue)) > FULL_BUFFER_SIZE:
                self.bufferFull()

    def checkWork(self):
        numBytesWritten = 0
        if self.outQueue or self.disconnecting:
            self.writeConnectionLost()
            return 0
        else:
            try:
                win32file.WriteFile(self.writePipe, b'', None)
            except pywintypes.error:
                self.writeConnectionLost()
                return numBytesWritten

            while self.outQueue:
                data = self.outQueue.pop(0)
                errCode = 0
                try:
                    errCode, nBytesWritten = win32file.WriteFile(self.writePipe, data, None)
                except win32api.error:
                    self.writeConnectionLost()
                    break
                else:
                    numBytesWritten += nBytesWritten
                    if len(data) > nBytesWritten:
                        self.outQueue.insert(0, data[nBytesWritten:])
                        break
            else:
                resumed = self.bufferEmpty()
                if not resumed:
                    if self.disconnecting:
                        self.writeConnectionLost()

            return numBytesWritten
