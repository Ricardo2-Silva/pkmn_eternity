# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\protocols\basic.py
"""
Basic protocols, such as line-oriented, netstring, and int prefixed strings.
"""
from __future__ import absolute_import, division
import re
from struct import pack, unpack, calcsize
from io import BytesIO
import math
from zope.interface import implementer
from twisted.python.compat import _PY3
from twisted.internet import protocol, defer, interfaces
from twisted.python import log
if _PY3:

    def _formatNetstring(data):
        return (b'').join([str(len(data)).encode("ascii"), b':', data, b','])


else:

    def _formatNetstring(data):
        return b'%d:%s,' % (len(data), data)


_formatNetstring.__doc__ = "\nConvert some C{bytes} into netstring format.\n\n@param data: C{bytes} that will be reformatted.\n"
DEBUG = 0

class NetstringParseError(ValueError):
    __doc__ = "\n    The incoming data is not in valid Netstring format.\n    "


class IncompleteNetstring(Exception):
    __doc__ = "\n    Not enough data to complete a netstring.\n    "


class NetstringReceiver(protocol.Protocol):
    __doc__ = "\n    A protocol that sends and receives netstrings.\n\n    See U{http://cr.yp.to/proto/netstrings.txt} for the specification of\n    netstrings. Every netstring starts with digits that specify the length\n    of the data. This length specification is separated from the data by\n    a colon. The data is terminated with a comma.\n\n    Override L{stringReceived} to handle received netstrings. This\n    method is called with the netstring payload as a single argument\n    whenever a complete netstring is received.\n\n    Security features:\n        1. Messages are limited in size, useful if you don't want\n           someone sending you a 500MB netstring (change C{self.MAX_LENGTH}\n           to the maximum length you wish to accept).\n        2. The connection is lost if an illegal message is received.\n\n    @ivar MAX_LENGTH: Defines the maximum length of netstrings that can be\n        received.\n    @type MAX_LENGTH: C{int}\n\n    @ivar _LENGTH: A pattern describing all strings that contain a netstring\n        length specification. Examples for length specifications are C{b'0:'},\n        C{b'12:'}, and C{b'179:'}. C{b'007:'} is not a valid length\n        specification, since leading zeros are not allowed.\n    @type _LENGTH: C{re.Match}\n\n    @ivar _LENGTH_PREFIX: A pattern describing all strings that contain\n        the first part of a netstring length specification (without the\n        trailing comma). Examples are '0', '12', and '179'. '007' does not\n        start a netstring length specification, since leading zeros are\n        not allowed.\n    @type _LENGTH_PREFIX: C{re.Match}\n\n    @ivar _PARSING_LENGTH: Indicates that the C{NetstringReceiver} is in\n        the state of parsing the length portion of a netstring.\n    @type _PARSING_LENGTH: C{int}\n\n    @ivar _PARSING_PAYLOAD: Indicates that the C{NetstringReceiver} is in\n        the state of parsing the payload portion (data and trailing comma)\n        of a netstring.\n    @type _PARSING_PAYLOAD: C{int}\n\n    @ivar brokenPeer: Indicates if the connection is still functional\n    @type brokenPeer: C{int}\n\n    @ivar _state: Indicates if the protocol is consuming the length portion\n        (C{PARSING_LENGTH}) or the payload (C{PARSING_PAYLOAD}) of a netstring\n    @type _state: C{int}\n\n    @ivar _remainingData: Holds the chunk of data that has not yet been consumed\n    @type _remainingData: C{string}\n\n    @ivar _payload: Holds the payload portion of a netstring including the\n        trailing comma\n    @type _payload: C{BytesIO}\n\n    @ivar _expectedPayloadSize: Holds the payload size plus one for the trailing\n        comma.\n    @type _expectedPayloadSize: C{int}\n    "
    MAX_LENGTH = 99999
    _LENGTH = re.compile(b'(0|[1-9]\\d*)(:)')
    _LENGTH_PREFIX = re.compile(b'(0|[1-9]\\d*)$')
    _MISSING_LENGTH = "The received netstring does not start with a length specification."
    _OVERFLOW = "The length specification of the received netstring cannot be represented in Python - it causes an OverflowError!"
    _TOO_LONG = "The received netstring is longer than the maximum %s specified by self.MAX_LENGTH"
    _MISSING_COMMA = "The received netstring is not terminated by a comma."
    _PARSING_LENGTH, _PARSING_PAYLOAD = range(2)

    def makeConnection(self, transport):
        """
        Initializes the protocol.
        """
        protocol.Protocol.makeConnection(self, transport)
        self._remainingData = b''
        self._currentPayloadSize = 0
        self._payload = BytesIO()
        self._state = self._PARSING_LENGTH
        self._expectedPayloadSize = 0
        self.brokenPeer = 0

    def sendString(self, string):
        """
        Sends a netstring.

        Wraps up C{string} by adding length information and a
        trailing comma; writes the result to the transport.

        @param string: The string to send.  The necessary framing (length
            prefix, etc) will be added.
        @type string: C{bytes}
        """
        self.transport.write(_formatNetstring(string))

    def dataReceived(self, data):
        """
        Receives some characters of a netstring.

        Whenever a complete netstring is received, this method extracts
        its payload and calls L{stringReceived} to process it.

        @param data: A chunk of data representing a (possibly partial)
            netstring
        @type data: C{bytes}
        """
        self._remainingData += data
        while self._remainingData:
            try:
                self._consumeData()
            except IncompleteNetstring:
                break
            except NetstringParseError:
                self._handleParseError()
                break

    def stringReceived(self, string):
        """
        Override this for notification when each complete string is received.

        @param string: The complete string which was received with all
            framing (length prefix, etc) removed.
        @type string: C{bytes}

        @raise NotImplementedError: because the method has to be implemented
            by the child class.
        """
        raise NotImplementedError()

    def _maxLengthSize(self):
        """
        Calculate and return the string size of C{self.MAX_LENGTH}.

        @return: The size of the string representation for C{self.MAX_LENGTH}
        @rtype: C{float}
        """
        return math.ceil(math.log10(self.MAX_LENGTH)) + 1

    def _consumeData(self):
        """
        Consumes the content of C{self._remainingData}.

        @raise IncompleteNetstring: if C{self._remainingData} does not
            contain enough data to complete the current netstring.
        @raise NetstringParseError: if the received data do not
            form a valid netstring.
        """
        if self._state == self._PARSING_LENGTH:
            self._consumeLength()
            self._prepareForPayloadConsumption()
        if self._state == self._PARSING_PAYLOAD:
            self._consumePayload()

    def _consumeLength(self):
        """
        Consumes the length portion of C{self._remainingData}.

        @raise IncompleteNetstring: if C{self._remainingData} contains
            a partial length specification (digits without trailing
            comma).
        @raise NetstringParseError: if the received data do not form a valid
            netstring.
        """
        lengthMatch = self._LENGTH.match(self._remainingData)
        if not lengthMatch:
            self._checkPartialLengthSpecification()
            raise IncompleteNetstring()
        self._processLength(lengthMatch)

    def _checkPartialLengthSpecification(self):
        """
        Makes sure that the received data represents a valid number.

        Checks if C{self._remainingData} represents a number smaller or
        equal to C{self.MAX_LENGTH}.

        @raise NetstringParseError: if C{self._remainingData} is no
            number or is too big (checked by L{_extractLength}).
        """
        partialLengthMatch = self._LENGTH_PREFIX.match(self._remainingData)
        if not partialLengthMatch:
            raise NetstringParseError(self._MISSING_LENGTH)
        lengthSpecification = partialLengthMatch.group(1)
        self._extractLength(lengthSpecification)

    def _processLength(self, lengthMatch):
        """
        Processes the length definition of a netstring.

        Extracts and stores in C{self._expectedPayloadSize} the number
        representing the netstring size.  Removes the prefix
        representing the length specification from
        C{self._remainingData}.

        @raise NetstringParseError: if the received netstring does not
            start with a number or the number is bigger than
            C{self.MAX_LENGTH}.
        @param lengthMatch: A regular expression match object matching
            a netstring length specification
        @type lengthMatch: C{re.Match}
        """
        endOfNumber = lengthMatch.end(1)
        startOfData = lengthMatch.end(2)
        lengthString = self._remainingData[:endOfNumber]
        self._expectedPayloadSize = self._extractLength(lengthString) + 1
        self._remainingData = self._remainingData[startOfData:]

    def _extractLength(self, lengthAsString):
        """
        Attempts to extract the length information of a netstring.

        @raise NetstringParseError: if the number is bigger than
            C{self.MAX_LENGTH}.
        @param lengthAsString: A chunk of data starting with a length
            specification
        @type lengthAsString: C{bytes}
        @return: The length of the netstring
        @rtype: C{int}
        """
        self._checkStringSize(lengthAsString)
        length = int(lengthAsString)
        if length > self.MAX_LENGTH:
            raise NetstringParseError(self._TOO_LONG % (self.MAX_LENGTH,))
        return length

    def _checkStringSize(self, lengthAsString):
        """
        Checks the sanity of lengthAsString.

        Checks if the size of the length specification exceeds the
        size of the string representing self.MAX_LENGTH. If this is
        not the case, the number represented by lengthAsString is
        certainly bigger than self.MAX_LENGTH, and a
        NetstringParseError can be raised.

        This method should make sure that netstrings with extremely
        long length specifications are refused before even attempting
        to convert them to an integer (which might trigger a
        MemoryError).
        """
        if len(lengthAsString) > self._maxLengthSize():
            raise NetstringParseError(self._TOO_LONG % (self.MAX_LENGTH,))

    def _prepareForPayloadConsumption(self):
        """
        Sets up variables necessary for consuming the payload of a netstring.
        """
        self._state = self._PARSING_PAYLOAD
        self._currentPayloadSize = 0
        self._payload.seek(0)
        self._payload.truncate()

    def _consumePayload(self):
        """
        Consumes the payload portion of C{self._remainingData}.

        If the payload is complete, checks for the trailing comma and
        processes the payload. If not, raises an L{IncompleteNetstring}
        exception.

        @raise IncompleteNetstring: if the payload received so far
            contains fewer characters than expected.
        @raise NetstringParseError: if the payload does not end with a
        comma.
        """
        self._extractPayload()
        if self._currentPayloadSize < self._expectedPayloadSize:
            raise IncompleteNetstring()
        self._checkForTrailingComma()
        self._state = self._PARSING_LENGTH
        self._processPayload()

    def _extractPayload(self):
        """
        Extracts payload information from C{self._remainingData}.

        Splits C{self._remainingData} at the end of the netstring.  The
        first part becomes C{self._payload}, the second part is stored
        in C{self._remainingData}.

        If the netstring is not yet complete, the whole content of
        C{self._remainingData} is moved to C{self._payload}.
        """
        if self._payloadComplete():
            remainingPayloadSize = self._expectedPayloadSize - self._currentPayloadSize
            self._payload.write(self._remainingData[:remainingPayloadSize])
            self._remainingData = self._remainingData[remainingPayloadSize:]
            self._currentPayloadSize = self._expectedPayloadSize
        else:
            self._payload.write(self._remainingData)
            self._currentPayloadSize += len(self._remainingData)
            self._remainingData = b''

    def _payloadComplete(self):
        """
        Checks if enough data have been received to complete the netstring.

        @return: C{True} iff the received data contain at least as many
            characters as specified in the length section of the
            netstring
        @rtype: C{bool}
        """
        return len(self._remainingData) + self._currentPayloadSize >= self._expectedPayloadSize

    def _processPayload(self):
        """
        Processes the actual payload with L{stringReceived}.

        Strips C{self._payload} of the trailing comma and calls
        L{stringReceived} with the result.
        """
        self.stringReceived(self._payload.getvalue()[:-1])

    def _checkForTrailingComma(self):
        """
        Checks if the netstring has a trailing comma at the expected position.

        @raise NetstringParseError: if the last payload character is
            anything but a comma.
        """
        if self._payload.getvalue()[-1:] != b',':
            raise NetstringParseError(self._MISSING_COMMA)

    def _handleParseError(self):
        """
        Terminates the connection and sets the flag C{self.brokenPeer}.
        """
        self.transport.loseConnection()
        self.brokenPeer = 1


class LineOnlyReceiver(protocol.Protocol):
    __doc__ = "\n    A protocol that receives only lines.\n\n    This is purely a speed optimisation over LineReceiver, for the\n    cases that raw mode is known to be unnecessary.\n\n    @cvar delimiter: The line-ending delimiter to use. By default this is\n                     C{b'\\r\\n'}.\n    @cvar MAX_LENGTH: The maximum length of a line to allow (If a\n                      sent line is longer than this, the connection is dropped).\n                      Default is 16384.\n    "
    _buffer = b''
    delimiter = b'\r\n'
    MAX_LENGTH = 16384

    def dataReceived(self, data):
        """
        Translates bytes into lines, and calls lineReceived.
        """
        lines = (self._buffer + data).split(self.delimiter)
        self._buffer = lines.pop(-1)
        for line in lines:
            if self.transport.disconnecting:
                return
            if len(line) > self.MAX_LENGTH:
                return self.lineLengthExceeded(line)
            self.lineReceived(line)

        if len(self._buffer) > self.MAX_LENGTH:
            return self.lineLengthExceeded(self._buffer)

    def lineReceived(self, line):
        """
        Override this for when each line is received.

        @param line: The line which was received with the delimiter removed.
        @type line: C{bytes}
        """
        raise NotImplementedError

    def sendLine(self, line):
        """
        Sends a line to the other end of the connection.

        @param line: The line to send, not including the delimiter.
        @type line: C{bytes}
        """
        return self.transport.writeSequence((line, self.delimiter))

    def lineLengthExceeded(self, line):
        """
        Called when the maximum line length has been reached.
        Override if it needs to be dealt with in some special way.
        """
        return self.transport.loseConnection()


class _PauseableMixin:
    paused = False

    def pauseProducing(self):
        self.paused = True
        self.transport.pauseProducing()

    def resumeProducing(self):
        self.paused = False
        self.transport.resumeProducing()
        self.dataReceived(b'')

    def stopProducing(self):
        self.paused = True
        self.transport.stopProducing()


class LineReceiver(protocol.Protocol, _PauseableMixin):
    __doc__ = "\n    A protocol that receives lines and/or raw data, depending on mode.\n\n    In line mode, each line that's received becomes a callback to\n    L{lineReceived}.  In raw data mode, each chunk of raw data becomes a\n    callback to L{LineReceiver.rawDataReceived}.\n    The L{setLineMode} and L{setRawMode} methods switch between the two modes.\n\n    This is useful for line-oriented protocols such as IRC, HTTP, POP, etc.\n\n    @cvar delimiter: The line-ending delimiter to use. By default this is\n                     C{b'\\r\\n'}.\n    @cvar MAX_LENGTH: The maximum length of a line to allow (If a\n                      sent line is longer than this, the connection is dropped).\n                      Default is 16384.\n    "
    line_mode = 1
    _buffer = b''
    _busyReceiving = False
    delimiter = b'\r\n'
    MAX_LENGTH = 16384

    def clearLineBuffer(self):
        """
        Clear buffered data.

        @return: All of the cleared buffered data.
        @rtype: C{bytes}
        """
        b, self._buffer = self._buffer, b''
        return b

    def dataReceivedParse error at or near `POP_JUMP_IF_FALSE' instruction at offset 248_250

    def setLineMode(self, extra=b''):
        """
        Sets the line-mode of this receiver.

        If you are calling this from a rawDataReceived callback,
        you can pass in extra unhandled data, and that data will
        be parsed for lines.  Further data received will be sent
        to lineReceived rather than rawDataReceived.

        Do not pass extra data if calling this function from
        within a lineReceived callback.
        """
        self.line_mode = 1
        if extra:
            return self.dataReceived(extra)

    def setRawMode(self):
        """
        Sets the raw mode of this receiver.
        Further data received will be sent to rawDataReceived rather
        than lineReceived.
        """
        self.line_mode = 0

    def rawDataReceived(self, data):
        """
        Override this for when raw data is received.
        """
        raise NotImplementedError

    def lineReceived(self, line):
        """
        Override this for when each line is received.

        @param line: The line which was received with the delimiter removed.
        @type line: C{bytes}
        """
        raise NotImplementedError

    def sendLine(self, line):
        """
        Sends a line to the other end of the connection.

        @param line: The line to send, not including the delimiter.
        @type line: C{bytes}
        """
        return self.transport.write(line + self.delimiter)

    def lineLengthExceeded(self, line):
        """
        Called when the maximum line length has been reached.
        Override if it needs to be dealt with in some special way.

        The argument 'line' contains the remainder of the buffer, starting
        with (at least some part) of the line which is too long. This may
        be more than one line, or may be only the initial portion of the
        line.
        """
        return self.transport.loseConnection()


class StringTooLongError(AssertionError):
    __doc__ = "\n    Raised when trying to send a string too long for a length prefixed\n    protocol.\n    "


class _RecvdCompatHack(object):
    __doc__ = "\n    Emulates the to-be-deprecated C{IntNStringReceiver.recvd} attribute.\n\n    The C{recvd} attribute was where the working buffer for buffering and\n    parsing netstrings was kept.  It was updated each time new data arrived and\n    each time some of that data was parsed and delivered to application code.\n    The piecemeal updates to its string value were expensive and have been\n    removed from C{IntNStringReceiver} in the normal case.  However, for\n    applications directly reading this attribute, this descriptor restores that\n    behavior.  It only copies the working buffer when necessary (ie, when\n    accessed).  This avoids the cost for applications not using the data.\n\n    This is a custom descriptor rather than a property, because we still need\n    the default __set__ behavior in both new-style and old-style subclasses.\n    "

    def __get__(self, oself, type=None):
        return oself._unprocessed[oself._compatibilityOffset:]


class IntNStringReceiver(protocol.Protocol, _PauseableMixin):
    __doc__ = "\n    Generic class for length prefixed protocols.\n\n    @ivar _unprocessed: bytes received, but not yet broken up into messages /\n        sent to stringReceived.  _compatibilityOffset must be updated when this\n        value is updated so that the C{recvd} attribute can be generated\n        correctly.\n    @type _unprocessed: C{bytes}\n\n    @ivar structFormat: format used for struct packing/unpacking. Define it in\n        subclass.\n    @type structFormat: C{str}\n\n    @ivar prefixLength: length of the prefix, in bytes. Define it in subclass,\n        using C{struct.calcsize(structFormat)}\n    @type prefixLength: C{int}\n\n    @ivar _compatibilityOffset: the offset within C{_unprocessed} to the next\n        message to be parsed. (used to generate the recvd attribute)\n    @type _compatibilityOffset: C{int}\n    "
    MAX_LENGTH = 99999
    _unprocessed = b''
    _compatibilityOffset = 0
    recvd = _RecvdCompatHack()

    def stringReceived(self, string):
        """
        Override this for notification when each complete string is received.

        @param string: The complete string which was received with all
            framing (length prefix, etc) removed.
        @type string: C{bytes}
        """
        raise NotImplementedError

    def lengthLimitExceeded(self, length):
        """
        Callback invoked when a length prefix greater than C{MAX_LENGTH} is
        received.  The default implementation disconnects the transport.
        Override this.

        @param length: The length prefix which was received.
        @type length: C{int}
        """
        self.transport.loseConnection()

    def dataReceived(self, data):
        """
        Convert int prefixed strings into calls to stringReceived.
        """
        alldata = self._unprocessed + data
        currentOffset = 0
        prefixLength = self.prefixLength
        fmt = self.structFormat
        self._unprocessed = alldata
        while len(alldata) >= currentOffset + prefixLength and not self.paused:
            messageStart = currentOffset + prefixLength
            length, = unpack(fmt, alldata[currentOffset:messageStart])
            if length > self.MAX_LENGTH:
                self._unprocessed = alldata
                self._compatibilityOffset = currentOffset
                self.lengthLimitExceeded(length)
                return
            else:
                messageEnd = messageStart + length
                if len(alldata) < messageEnd:
                    break
                packet = alldata[messageStart:messageEnd]
                currentOffset = messageEnd
                self._compatibilityOffset = currentOffset
                self.stringReceived(packet)
                if "recvd" in self.__dict__:
                    alldata = self.__dict__.pop("recvd")
                    self._unprocessed = alldata
                    self._compatibilityOffset = currentOffset = 0
                    if alldata:
                        pass
                    else:
                        return

        self._unprocessed = alldata[currentOffset:]
        self._compatibilityOffset = 0

    def sendString(self, string):
        """
        Send a prefixed string to the other end of the connection.

        @param string: The string to send.  The necessary framing (length
            prefix, etc) will be added.
        @type string: C{bytes}
        """
        if len(string) >= 2 ** (8 * self.prefixLength):
            raise StringTooLongError("Try to send %s bytes whereas maximum is %s" % (
             len(string), 2 ** (8 * self.prefixLength)))
        self.transport.write(pack(self.structFormat, len(string)) + string)


class Int32StringReceiver(IntNStringReceiver):
    __doc__ = "\n    A receiver for int32-prefixed strings.\n\n    An int32 string is a string prefixed by 4 bytes, the 32-bit length of\n    the string encoded in network byte order.\n\n    This class publishes the same interface as NetstringReceiver.\n    "
    structFormat = "!I"
    prefixLength = calcsize(structFormat)


class Int16StringReceiver(IntNStringReceiver):
    __doc__ = "\n    A receiver for int16-prefixed strings.\n\n    An int16 string is a string prefixed by 2 bytes, the 16-bit length of\n    the string encoded in network byte order.\n\n    This class publishes the same interface as NetstringReceiver.\n    "
    structFormat = "!H"
    prefixLength = calcsize(structFormat)


class Int8StringReceiver(IntNStringReceiver):
    __doc__ = "\n    A receiver for int8-prefixed strings.\n\n    An int8 string is a string prefixed by 1 byte, the 8-bit length of\n    the string.\n\n    This class publishes the same interface as NetstringReceiver.\n    "
    structFormat = "!B"
    prefixLength = calcsize(structFormat)


class StatefulStringProtocol:
    __doc__ = "\n    A stateful string protocol.\n\n    This is a mixin for string protocols (L{Int32StringReceiver},\n    L{NetstringReceiver}) which translates L{stringReceived} into a callback\n    (prefixed with C{'proto_'}) depending on state.\n\n    The state C{'done'} is special; if a C{proto_*} method returns it, the\n    connection will be closed immediately.\n\n    @ivar state: Current state of the protocol. Defaults to C{'init'}.\n    @type state: C{str}\n    "
    state = "init"

    def stringReceived(self, string):
        """
        Choose a protocol phase function and call it.

        Call back to the appropriate protocol phase; this begins with
        the function C{proto_init} and moves on to C{proto_*} depending on
        what each C{proto_*} function returns.  (For example, if
        C{self.proto_init} returns 'foo', then C{self.proto_foo} will be the
        next function called when a protocol message is received.
        """
        try:
            pto = "proto_" + self.state
            statehandler = getattr(self, pto)
        except AttributeError:
            log.msg("callback", self.state, "not found")
        else:
            self.state = statehandler(string)
            if self.state == "done":
                self.transport.loseConnection()


@implementer(interfaces.IProducer)
class FileSender:
    __doc__ = "\n    A producer that sends the contents of a file to a consumer.\n\n    This is a helper for protocols that, at some point, will take a\n    file-like object, read its contents, and write them out to the network,\n    optionally performing some transformation on the bytes in between.\n    "
    CHUNK_SIZE = 16384
    lastSent = ""
    deferred = None

    def beginFileTransfer(self, file, consumer, transform=None):
        """
        Begin transferring a file

        @type file: Any file-like object
        @param file: The file object to read data from

        @type consumer: Any implementor of IConsumer
        @param consumer: The object to write data to

        @param transform: A callable taking one string argument and returning
        the same.  All bytes read from the file are passed through this before
        being written to the consumer.

        @rtype: C{Deferred}
        @return: A deferred whose callback will be invoked when the file has
        been completely written to the consumer. The last byte written to the
        consumer is passed to the callback.
        """
        self.file = file
        self.consumer = consumer
        self.transform = transform
        self.deferred = deferred = defer.Deferred()
        self.consumer.registerProducer(self, False)
        return deferred

    def resumeProducing(self):
        chunk = ""
        if self.file:
            chunk = self.file.read(self.CHUNK_SIZE)
        if not chunk:
            self.file = None
            self.consumer.unregisterProducer()
            if self.deferred:
                self.deferred.callback(self.lastSent)
                self.deferred = None
            return
        if self.transform:
            chunk = self.transform(chunk)
        self.consumer.write(chunk)
        self.lastSent = chunk[-1:]

    def pauseProducing(self):
        return

    def stopProducing(self):
        if self.deferred:
            self.deferred.errback(Exception("Consumer asked us to stop producing"))
            self.deferred = None