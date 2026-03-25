# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\web\_newclient.py
"""
An U{HTTP 1.1<http://www.w3.org/Protocols/rfc2616/rfc2616.html>} client.

The way to use the functionality provided by this module is to:

  - Connect a L{HTTP11ClientProtocol} to an HTTP server
  - Create a L{Request} with the appropriate data
  - Pass the request to L{HTTP11ClientProtocol.request}
  - The returned Deferred will fire with a L{Response} object
  - Create a L{IProtocol} provider which can handle the response body
  - Connect it to the response with L{Response.deliverBody}
  - When the protocol's C{connectionLost} method is called, the response is
    complete.  See L{Response.deliverBody} for details.

Various other classes in this module support this usage:

  - HTTPParser is the basic HTTP parser.  It can handle the parts of HTTP which
    are symmetric between requests and responses.

  - HTTPClientParser extends HTTPParser to handle response-specific parts of
    HTTP.  One instance is created for each request to parse the corresponding
    response.
"""
from __future__ import division, absolute_import
__metaclass__ = type
import re
from zope.interface import implementer
from twisted.python.compat import networkString
from twisted.python.components import proxyForInterface
from twisted.python.reflect import fullyQualifiedName
from twisted.python.failure import Failure
from twisted.internet.interfaces import IConsumer, IPushProducer
from twisted.internet.error import ConnectionDone
from twisted.internet.defer import Deferred, succeed, fail, maybeDeferred
from twisted.internet.defer import CancelledError
from twisted.internet.protocol import Protocol
from twisted.protocols.basic import LineReceiver
from twisted.web.iweb import UNKNOWN_LENGTH, IResponse, IClientRequest
from twisted.web.http_headers import Headers
from twisted.web.http import NO_CONTENT, NOT_MODIFIED
from twisted.web.http import _DataLoss, PotentialDataLoss
from twisted.web.http import _IdentityTransferDecoder, _ChunkedTransferDecoder
from twisted.logger import Logger
STATUS = "STATUS"
HEADER = "HEADER"
BODY = "BODY"
DONE = "DONE"
_moduleLog = Logger()

class BadHeaders(Exception):
    __doc__ = "\n    Headers passed to L{Request} were in some way invalid.\n    "


class ExcessWrite(Exception):
    __doc__ = "\n    The body L{IBodyProducer} for a request tried to write data after\n    indicating it had finished writing data.\n    "


class ParseError(Exception):
    __doc__ = "\n    Some received data could not be parsed.\n\n    @ivar data: The string which could not be parsed.\n    "

    def __init__(self, reason, data):
        Exception.__init__(self, reason, data)
        self.data = data


class BadResponseVersion(ParseError):
    __doc__ = "\n    The version string in a status line was unparsable.\n    "


class _WrapperException(Exception):
    __doc__ = "\n    L{_WrapperException} is the base exception type for exceptions which\n    include one or more other exceptions as the low-level causes.\n\n    @ivar reasons: A L{list} of one or more L{Failure} instances encountered\n        during an HTTP request.  See subclass documentation for more details.\n    "

    def __init__(self, reasons):
        Exception.__init__(self, reasons)
        self.reasons = reasons


class RequestGenerationFailed(_WrapperException):
    __doc__ = "\n    There was an error while creating the bytes which make up a request.\n\n    @ivar reasons: A C{list} of one or more L{Failure} instances giving the\n        reasons the request generation was considered to have failed.\n    "


class RequestTransmissionFailed(_WrapperException):
    __doc__ = "\n    There was an error while sending the bytes which make up a request.\n\n    @ivar reasons: A C{list} of one or more L{Failure} instances giving the\n        reasons the request transmission was considered to have failed.\n    "


class ConnectionAborted(Exception):
    __doc__ = "\n    The connection was explicitly aborted by application code.\n    "


class WrongBodyLength(Exception):
    __doc__ = "\n    An L{IBodyProducer} declared the number of bytes it was going to\n    produce (via its C{length} attribute) and then produced a different number\n    of bytes.\n    "


class ResponseDone(Exception):
    __doc__ = "\n    L{ResponseDone} may be passed to L{IProtocol.connectionLost} on the\n    protocol passed to L{Response.deliverBody} and indicates that the entire\n    response has been delivered.\n    "


class ResponseFailed(_WrapperException):
    __doc__ = "\n    L{ResponseFailed} indicates that all of the response to a request was not\n    received for some reason.\n\n    @ivar reasons: A C{list} of one or more L{Failure} instances giving the\n        reasons the response was considered to have failed.\n\n    @ivar response: If specified, the L{Response} received from the server (and\n        in particular the status code and the headers).\n    "

    def __init__(self, reasons, response=None):
        _WrapperException.__init__(self, reasons)
        self.response = response


class ResponseNeverReceived(ResponseFailed):
    __doc__ = "\n    A L{ResponseFailed} that knows no response bytes at all have been received.\n    "


class RequestNotSent(Exception):
    __doc__ = "\n    L{RequestNotSent} indicates that an attempt was made to issue a request but\n    for reasons unrelated to the details of the request itself, the request\n    could not be sent.  For example, this may indicate that an attempt was made\n    to send a request using a protocol which is no longer connected to a\n    server.\n    "


def _callAppFunction(function):
    """
    Call C{function}.  If it raises an exception, log it with a minimal
    description of the source.

    @return: L{None}
    """
    try:
        function()
    except:
        _moduleLog.failure("Unexpected exception from {name}",
          name=(fullyQualifiedName(function)))


class HTTPParser(LineReceiver):
    __doc__ = "\n    L{HTTPParser} handles the parsing side of HTTP processing. With a suitable\n    subclass, it can parse either the client side or the server side of the\n    connection.\n\n    @ivar headers: All of the non-connection control message headers yet\n        received.\n\n    @ivar state: State indicator for the response parsing state machine.  One\n        of C{STATUS}, C{HEADER}, C{BODY}, C{DONE}.\n\n    @ivar _partialHeader: L{None} or a C{list} of the lines of a multiline\n        header while that header is being received.\n    "
    delimiter = b'\n'
    CONNECTION_CONTROL_HEADERS = set([
     b'content-length', b'connection', b'keep-alive', b'te', 
     b'trailers', 
     b'transfer-encoding', b'upgrade', 
     b'proxy-connection'])

    def connectionMade(self):
        self.headers = Headers()
        self.connHeaders = Headers()
        self.state = STATUS
        self._partialHeader = None

    def switchToBodyMode(self, decoder):
        """
        Switch to body parsing mode - interpret any more bytes delivered as
        part of the message body and deliver them to the given decoder.
        """
        if self.state == BODY:
            raise RuntimeError("already in body mode")
        self.bodyDecoder = decoder
        self.state = BODY
        self.setRawMode()

    def lineReceived(self, line):
        """
        Handle one line from a response.
        """
        if line[-1:] == b'\r':
            line = line[:-1]
        elif self.state == STATUS:
            self.statusReceived(line)
            self.state = HEADER
        elif self.state == HEADER:
            if not line or line[0] not in b' \t':
                if self._partialHeader is not None:
                    header = (b'').join(self._partialHeader)
                    name, value = header.split(b':', 1)
                    value = value.strip()
                    self.headerReceived(name, value)
                if not line:
                    self.allHeadersReceived()
            else:
                self._partialHeader = [
                 line]
        else:
            self._partialHeader.append(line)

    def rawDataReceived(self, data):
        """
        Pass data from the message body to the body decoder object.
        """
        self.bodyDecoder.dataReceived(data)

    def isConnectionControlHeader(self, name):
        """
        Return C{True} if the given lower-cased name is the name of a
        connection control header (rather than an entity header).

        According to RFC 2616, section 14.10, the tokens in the Connection
        header are probably relevant here.  However, I am not sure what the
        practical consequences of either implementing or ignoring that are.
        So I leave it unimplemented for the time being.
        """
        return name in self.CONNECTION_CONTROL_HEADERS

    def statusReceived(self, status):
        """
        Callback invoked whenever the first line of a new message is received.
        Override this.

        @param status: The first line of an HTTP request or response message
            without trailing I{CR LF}.
        @type status: C{bytes}
        """
        return

    def headerReceived(self, name, value):
        """
        Store the given header in C{self.headers}.
        """
        name = name.lower()
        if self.isConnectionControlHeader(name):
            headers = self.connHeaders
        else:
            headers = self.headers
        headers.addRawHeader(name, value)

    def allHeadersReceived(self):
        """
        Callback invoked after the last header is passed to C{headerReceived}.
        Override this to change to the C{BODY} or C{DONE} state.
        """
        self.switchToBodyMode(None)


class HTTPClientParser(HTTPParser):
    __doc__ = "\n    An HTTP parser which only handles HTTP responses.\n\n    @ivar request: The request with which the expected response is associated.\n    @type request: L{Request}\n\n    @ivar NO_BODY_CODES: A C{set} of response codes which B{MUST NOT} have a\n        body.\n\n    @ivar finisher: A callable to invoke when this response is fully parsed.\n\n    @ivar _responseDeferred: A L{Deferred} which will be called back with the\n        response when all headers in the response have been received.\n        Thereafter, L{None}.\n\n    @ivar _everReceivedData: C{True} if any bytes have been received.\n    "
    NO_BODY_CODES = set([NO_CONTENT, NOT_MODIFIED])
    _transferDecoders = {b'chunked': _ChunkedTransferDecoder}
    bodyDecoder = None
    _log = Logger()

    def __init__(self, request, finisher):
        self.request = request
        self.finisher = finisher
        self._responseDeferred = Deferred()
        self._everReceivedData = False

    def dataReceived(self, data):
        """
        Override so that we know if any response has been received.
        """
        self._everReceivedData = True
        HTTPParser.dataReceived(self, data)

    def parseVersion(self, strversion):
        """
        Parse version strings of the form Protocol '/' Major '.' Minor. E.g.
        b'HTTP/1.1'.  Returns (protocol, major, minor).  Will raise ValueError
        on bad syntax.
        """
        try:
            proto, strnumber = strversion.split(b'/')
            major, minor = strnumber.split(b'.')
            major, minor = int(major), int(minor)
        except ValueError as e:
            raise BadResponseVersion(str(e), strversion)

        if major < 0 or minor < 0:
            raise BadResponseVersion("version may not be negative", strversion)
        return (
         proto, major, minor)

    def statusReceived(self, status):
        """
        Parse the status line into its components and create a response object
        to keep track of this response's state.
        """
        parts = status.split(b' ', 2)
        if len(parts) == 2:
            version, codeBytes = parts
            phrase = b''
        elif len(parts) == 3:
            version, codeBytes, phrase = parts
        else:
            raise ParseError("wrong number of parts", status)
        try:
            statusCode = int(codeBytes)
        except ValueError:
            raise ParseError("non-integer status code", status)

        self.response = Response._construct(self.parseVersion(version), statusCode, phrase, self.headers, self.transport, self.request)

    def _finished(self, rest):
        """
        Called to indicate that an entire response has been received.  No more
        bytes will be interpreted by this L{HTTPClientParser}.  Extra bytes are
        passed up and the state of this L{HTTPClientParser} is set to I{DONE}.

        @param rest: A C{bytes} giving any extra bytes delivered to this
            L{HTTPClientParser} which are not part of the response being
            parsed.
        """
        self.state = DONE
        self.finisher(rest)

    def isConnectionControlHeader(self, name):
        """
        Content-Length in the response to a HEAD request is an entity header,
        not a connection control header.
        """
        if self.request.method == b'HEAD':
            if name == b'content-length':
                return False
        return HTTPParser.isConnectionControlHeader(self, name)

    def allHeadersReceived(self):
        """
        Figure out how long the response body is going to be by examining
        headers and stuff.
        """
        if 100 <= self.response.code < 200:
            self._log.info("Ignoring unexpected {code} response",
              code=(self.response.code))
            self.connectionMade()
            del self.response
            return
        elif self.response.code in self.NO_BODY_CODES or self.request.method == b'HEAD':
            self.response.length = 0
            self._finished(self.clearLineBuffer())
            self.response._bodyDataFinished()
        else:
            transferEncodingHeaders = self.connHeaders.getRawHeaders(b'transfer-encoding')
            if transferEncodingHeaders:
                transferDecoder = self._transferDecoders[transferEncodingHeaders[0].lower()]
            else:
                contentLengthHeaders = self.connHeaders.getRawHeaders(b'content-length')
                if contentLengthHeaders is None:
                    contentLength = None
                elif len(contentLengthHeaders) == 1:
                    contentLength = int(contentLengthHeaders[0])
                    self.response.length = contentLength
                else:
                    raise ValueError("Too many Content-Length headers; response is invalid")
                if contentLength == 0:
                    self._finished(self.clearLineBuffer())
                    transferDecoder = None
                else:
                    transferDecoder = lambda x, y: _IdentityTransferDecoder(contentLength, x, y)
                if transferDecoder is None:
                    self.response._bodyDataFinished()
                else:
                    self.transport.pauseProducing()
                    self.switchToBodyMode(transferDecoder(self.response._bodyDataReceived, self._finished))
        self._responseDeferred.callback(self.response)
        del self._responseDeferred

    def connectionLost(self, reason):
        if self.bodyDecoder is not None:
            try:
                try:
                    self.bodyDecoder.noMoreData()
                except PotentialDataLoss:
                    self.response._bodyDataFinished(Failure())
                except _DataLoss:
                    self.response._bodyDataFinished(Failure(ResponseFailed([reason, Failure()], self.response)))
                else:
                    self.response._bodyDataFinished()
            except:
                self._log.failure("")

        if self.state != DONE:
            if self._everReceivedData:
                exceptionClass = ResponseFailed
            else:
                exceptionClass = ResponseNeverReceived
            self._responseDeferred.errback(Failure(exceptionClass([reason])))
            del self._responseDeferred


_VALID_METHOD = re.compile(b'\\A[%s]+\\Z' % (
 bytes().join((b'!', b'#', b'$', b'%', b'&', b"'", b'*', b'+', b'-', b'.', b'^', b'_',
              b'`', b'|', b'~', b'0-9', b'A-Z', b'a-z')),))

def _ensureValidMethod(method):
    r"""
    An HTTP method is an HTTP token, which consists of any visible
    ASCII character that is not a delimiter (i.e. one of
    C{"(),/:;<=>?@[\]{}}.)

    @param method: the method to check
    @type method: L{bytes}

    @return: the method if it is valid
    @rtype: L{bytes}

    @raise ValueError: if the method is not valid

    @see: U{https://tools.ietf.org/html/rfc7230#section-3.1.1},
        U{https://tools.ietf.org/html/rfc7230#section-3.2.6},
        U{https://tools.ietf.org/html/rfc5234#appendix-B.1}
    """
    if _VALID_METHOD.match(method):
        return method
    raise ValueError("Invalid method {!r}".format(method))


_VALID_URI = re.compile(b'\\A[\\x21-\\x7e]+\\Z')

def _ensureValidURI(uri):
    """
    A valid URI cannot contain control characters (i.e., characters
    between 0-32, inclusive and 127) or non-ASCII characters (i.e.,
    characters with values between 128-255, inclusive).

    @param uri: the URI to check
    @type uri: L{bytes}

    @return: the URI if it is valid
    @rtype: L{bytes}

    @raise ValueError: if the URI is not valid

    @see: U{https://tools.ietf.org/html/rfc3986#section-3.3},
        U{https://tools.ietf.org/html/rfc3986#appendix-A},
        U{https://tools.ietf.org/html/rfc5234#appendix-B.1}
    """
    if _VALID_URI.match(uri):
        return uri
    raise ValueError("Invalid URI {!r}".format(uri))


@implementer(IClientRequest)
class Request:
    __doc__ = "\n    A L{Request} instance describes an HTTP request to be sent to an HTTP\n    server.\n\n    @ivar method: See L{__init__}.\n    @ivar uri: See L{__init__}.\n    @ivar headers: See L{__init__}.\n    @ivar bodyProducer: See L{__init__}.\n    @ivar persistent: See L{__init__}.\n\n    @ivar _parsedURI: Parsed I{URI} for the request, or L{None}.\n    @type _parsedURI: L{twisted.web.client.URI} or L{None}\n    "
    _log = Logger()

    def __init__(self, method, uri, headers, bodyProducer, persistent=False):
        """
        @param method: The HTTP method for this request, ex: b'GET', b'HEAD',
            b'POST', etc.
        @type method: L{bytes}

        @param uri: The relative URI of the resource to request.  For example,
            C{b'/foo/bar?baz=quux'}.
        @type uri: L{bytes}

        @param headers: Headers to be sent to the server.  It is important to
            note that this object does not create any implicit headers.  So it
            is up to the HTTP Client to add required headers such as 'Host'.
        @type headers: L{twisted.web.http_headers.Headers}

        @param bodyProducer: L{None} or an L{IBodyProducer} provider which
            produces the content body to send to the remote HTTP server.

        @param persistent: Set to C{True} when you use HTTP persistent
            connection, defaults to C{False}.
        @type persistent: L{bool}
        """
        self.method = _ensureValidMethod(method)
        self.uri = _ensureValidURI(uri)
        self.headers = headers
        self.bodyProducer = bodyProducer
        self.persistent = persistent
        self._parsedURI = None

    @classmethod
    def _construct(cls, method, uri, headers, bodyProducer, persistent=False, parsedURI=None):
        """
        Private constructor.

        @param method: See L{__init__}.
        @param uri: See L{__init__}.
        @param headers: See L{__init__}.
        @param bodyProducer: See L{__init__}.
        @param persistent: See L{__init__}.
        @param parsedURI: See L{Request._parsedURI}.

        @return: L{Request} instance.
        """
        request = cls(method, uri, headers, bodyProducer, persistent)
        request._parsedURI = parsedURI
        return request

    @property
    def absoluteURI(self):
        """
        The absolute URI of the request as C{bytes}, or L{None} if the
        absolute URI cannot be determined.
        """
        return getattr(self._parsedURI, "toBytes", (lambda: None))()

    def _writeHeaders(self, transport, TEorCL):
        hosts = self.headers.getRawHeaders(b'host', ())
        if len(hosts) != 1:
            raise BadHeaders("Exactly one Host header required")
        requestLines = []
        requestLines.append((b' ').join([
         _ensureValidMethod(self.method),
         _ensureValidURI(self.uri),
         b'HTTP/1.1\r\n']))
        if not self.persistent:
            requestLines.append(b'Connection: close\r\n')
        if TEorCL is not None:
            requestLines.append(TEorCL)
        for name, values in self.headers.getAllRawHeaders():
            requestLines.extend([name + b': ' + v + b'\r\n' for v in values])

        requestLines.append(b'\r\n')
        transport.writeSequence(requestLines)

    def _writeToBodyProducerChunked(self, transport):
        """
        Write this request to the given transport using chunked
        transfer-encoding to frame the body.

        @param transport: See L{writeTo}.
        @return: See L{writeTo}.
        """
        self._writeHeaders(transport, b'Transfer-Encoding: chunked\r\n')
        encoder = ChunkedEncoder(transport)
        encoder.registerProducer(self.bodyProducer, True)
        d = self.bodyProducer.startProducing(encoder)

        def cbProduced(ignored):
            encoder.unregisterProducer()

        def ebProduced(err):
            encoder._allowNoMoreWrites()
            transport.unregisterProducer()
            return err

        d.addCallbacks(cbProduced, ebProduced)
        return d

    def _writeToBodyProducerContentLength(self, transport):
        """
        Write this request to the given transport using content-length to frame
        the body.

        @param transport: See L{writeTo}.
        @return: See L{writeTo}.
        """
        self._writeHeaders(transport, networkString("Content-Length: %d\r\n" % (self.bodyProducer.length,)))
        finishedConsuming = Deferred()
        encoder = LengthEnforcingConsumer(self.bodyProducer, transport, finishedConsuming)
        transport.registerProducer(self.bodyProducer, True)
        finishedProducing = self.bodyProducer.startProducing(encoder)

        def combine(consuming, producing):

            def cancelConsuming(ign):
                finishedProducing.cancel()

            ultimate = Deferred(cancelConsuming)
            state = [
             None]

            def ebConsuming(err):
                if state == [None]:
                    state[0] = 1
                    ultimate.errback(err)
                else:
                    self._log.failure("Buggy state machine in {request}/[{state}]: ebConsuming called",
                      failure=err,
                      request=(repr(self)),
                      state=(state[0]))

            def cbProducing(result):
                if state == [None]:
                    state[0] = 2
                    try:
                        encoder._noMoreWritesExpected()
                    except:
                        ultimate.errback()
                    else:
                        ultimate.callback(None)

            def ebProducing(err):
                if state == [None]:
                    state[0] = 3
                    encoder._allowNoMoreWrites()
                    ultimate.errback(err)
                else:
                    self._log.failure("Producer is buggy", failure=err)

            consuming.addErrback(ebConsuming)
            producing.addCallbacks(cbProducing, ebProducing)
            return ultimate

        d = combine(finishedConsuming, finishedProducing)

        def f(passthrough):
            transport.unregisterProducer()
            return passthrough

        d.addBoth(f)
        return d

    def _writeToEmptyBodyContentLength(self, transport):
        """
        Write this request to the given transport using content-length to frame
        the (empty) body.

        @param transport: See L{writeTo}.
        @return: See L{writeTo}.
        """
        self._writeHeaders(transport, b'Content-Length: 0\r\n')
        return succeed(None)

    def writeTo(self, transport):
        """
        Format this L{Request} as an HTTP/1.1 request and write it to the given
        transport.  If bodyProducer is not None, it will be associated with an
        L{IConsumer}.

        @param transport: The transport to which to write.
        @type transport: L{twisted.internet.interfaces.ITransport} provider

        @return: A L{Deferred} which fires with L{None} when the request has
            been completely written to the transport or with a L{Failure} if
            there is any problem generating the request bytes.
        """
        if self.bodyProducer is None:
            if self.method in (b'PUT', b'POST'):
                self._writeToEmptyBodyContentLength(transport)
            else:
                self._writeHeaders(transport, None)
        else:
            if self.bodyProducer.length is UNKNOWN_LENGTH:
                return self._writeToBodyProducerChunked(transport)
            else:
                return self._writeToBodyProducerContentLength(transport)

    def stopWriting(self):
        """
        Stop writing this request to the transport.  This can only be called
        after C{writeTo} and before the L{Deferred} returned by C{writeTo}
        fires.  It should cancel any asynchronous task started by C{writeTo}.
        The L{Deferred} returned by C{writeTo} need not be fired if this method
        is called.
        """
        _callAppFunction(self.bodyProducer.stopProducing)


class LengthEnforcingConsumer:
    __doc__ = "\n    An L{IConsumer} proxy which enforces an exact length requirement on the\n    total data written to it.\n\n    @ivar _length: The number of bytes remaining to be written.\n\n    @ivar _producer: The L{IBodyProducer} which is writing to this\n        consumer.\n\n    @ivar _consumer: The consumer to which at most C{_length} bytes will be\n        forwarded.\n\n    @ivar _finished: A L{Deferred} which will be fired with a L{Failure} if too\n        many bytes are written to this consumer.\n    "

    def __init__(self, producer, consumer, finished):
        self._length = producer.length
        self._producer = producer
        self._consumer = consumer
        self._finished = finished

    def _allowNoMoreWrites(self):
        """
        Indicate that no additional writes are allowed.  Attempts to write
        after calling this method will be met with an exception.
        """
        self._finished = None

    def write(self, bytes):
        """
        Write C{bytes} to the underlying consumer unless
        C{_noMoreWritesExpected} has been called or there are/have been too
        many bytes.
        """
        if self._finished is None:
            self._producer.stopProducing()
            raise ExcessWrite()
        elif len(bytes) <= self._length:
            self._length -= len(bytes)
            self._consumer.write(bytes)
        else:
            _callAppFunction(self._producer.stopProducing)
            self._finished.errback(WrongBodyLength("too many bytes written"))
            self._allowNoMoreWrites()

    def _noMoreWritesExpected(self):
        """
        Called to indicate no more bytes will be written to this consumer.
        Check to see that the correct number have been written.

        @raise WrongBodyLength: If not enough bytes have been written.
        """
        if self._finished is not None:
            self._allowNoMoreWrites()
            if self._length:
                raise WrongBodyLength("too few bytes written")


def makeStatefulDispatcher(name, template):
    """
    Given a I{dispatch} name and a function, return a function which can be
    used as a method and which, when called, will call another method defined
    on the instance and return the result.  The other method which is called is
    determined by the value of the C{_state} attribute of the instance.

    @param name: A string which is used to construct the name of the subsidiary
        method to invoke.  The subsidiary method is named like C{'_%s_%s' %
        (name, _state)}.

    @param template: A function object which is used to give the returned
        function a docstring.

    @return: The dispatcher function.
    """

    def dispatcher(self, *args, **kwargs):
        func = getattr(self, "_" + name + "_" + self._state, None)
        if func is None:
            raise RuntimeError("%r has no %s method in state %s" % (self, name, self._state))
        return func(*args, **kwargs)

    dispatcher.__doc__ = template.__doc__
    return dispatcher


_ClientRequestProxy = proxyForInterface(IClientRequest)

@implementer(IResponse)
class Response:
    __doc__ = "\n    A L{Response} instance describes an HTTP response received from an HTTP\n    server.\n\n    L{Response} should not be subclassed or instantiated.\n\n    @ivar _transport: See L{__init__}.\n\n    @ivar _bodyProtocol: The L{IProtocol} provider to which the body is\n        delivered.  L{None} before one has been registered with\n        C{deliverBody}.\n\n    @ivar _bodyBuffer: A C{list} of the strings passed to C{bodyDataReceived}\n        before C{deliverBody} is called.  L{None} afterwards.\n\n    @ivar _state: Indicates what state this L{Response} instance is in,\n        particularly with respect to delivering bytes from the response body\n        to an application-supplied protocol object.  This may be one of\n        C{'INITIAL'}, C{'CONNECTED'}, C{'DEFERRED_CLOSE'}, or C{'FINISHED'},\n        with the following meanings:\n\n          - INITIAL: This is the state L{Response} objects start in.  No\n            protocol has yet been provided and the underlying transport may\n            still have bytes to deliver to it.\n\n          - DEFERRED_CLOSE: If the underlying transport indicates all bytes\n            have been delivered but no application-provided protocol is yet\n            available, the L{Response} moves to this state.  Data is\n            buffered and waiting for a protocol to be delivered to.\n\n          - CONNECTED: If a protocol is provided when the state is INITIAL,\n            the L{Response} moves to this state.  Any buffered data is\n            delivered and any data which arrives from the transport\n            subsequently is given directly to the protocol.\n\n          - FINISHED: If a protocol is provided in the DEFERRED_CLOSE state,\n            the L{Response} moves to this state after delivering all\n            buffered data to the protocol.  Otherwise, if the L{Response} is\n            in the CONNECTED state, if the transport indicates there is no\n            more data, the L{Response} moves to this state.  Nothing else\n            can happen once the L{Response} is in this state.\n    @type _state: C{str}\n    "
    length = UNKNOWN_LENGTH
    _bodyProtocol = None
    _bodyFinished = False

    def __init__(self, version, code, phrase, headers, _transport):
        """
        @param version: HTTP version components protocol, major, minor. E.g.
            C{(b'HTTP', 1, 1)} to mean C{b'HTTP/1.1'}.

        @param code: HTTP status code.
        @type code: L{int}

        @param phrase: HTTP reason phrase, intended to give a short description
            of the HTTP status code.

        @param headers: HTTP response headers.
        @type headers: L{twisted.web.http_headers.Headers}

        @param _transport: The transport which is delivering this response.
        """
        self.version = version
        self.code = code
        self.phrase = phrase
        self.headers = headers
        self._transport = _transport
        self._bodyBuffer = []
        self._state = "INITIAL"
        self.request = None
        self.previousResponse = None

    @classmethod
    def _construct(cls, version, code, phrase, headers, _transport, request):
        """
        Private constructor.

        @param version: See L{__init__}.
        @param code: See L{__init__}.
        @param phrase: See L{__init__}.
        @param headers: See L{__init__}.
        @param _transport: See L{__init__}.
        @param request: See L{IResponse.request}.

        @return: L{Response} instance.
        """
        response = Response(version, code, phrase, headers, _transport)
        response.request = _ClientRequestProxy(request)
        return response

    def setPreviousResponse(self, previousResponse):
        self.previousResponse = previousResponse

    def deliverBody(self, protocol):
        """
        Dispatch the given L{IProtocol} depending of the current state of the
        response.
        """
        return

    deliverBody = makeStatefulDispatcher("deliverBody", deliverBody)

    def _deliverBody_INITIAL(self, protocol):
        """
        Deliver any buffered data to C{protocol} and prepare to deliver any
        future data to it.  Move to the C{'CONNECTED'} state.
        """
        protocol.makeConnection(self._transport)
        self._bodyProtocol = protocol
        for data in self._bodyBuffer:
            self._bodyProtocol.dataReceived(data)

        self._bodyBuffer = None
        self._state = "CONNECTED"
        self._transport.resumeProducing()

    def _deliverBody_CONNECTED(self, protocol):
        """
        It is invalid to attempt to deliver data to a protocol when it is
        already being delivered to another protocol.
        """
        raise RuntimeError("Response already has protocol %r, cannot deliverBody again" % (
         self._bodyProtocol,))

    def _deliverBody_DEFERRED_CLOSE(self, protocol):
        """
        Deliver any buffered data to C{protocol} and then disconnect the
        protocol.  Move to the C{'FINISHED'} state.
        """
        protocol.makeConnection(self._transport)
        for data in self._bodyBuffer:
            protocol.dataReceived(data)

        self._bodyBuffer = None
        protocol.connectionLost(self._reason)
        self._state = "FINISHED"

    def _deliverBody_FINISHED(self, protocol):
        """
        It is invalid to attempt to deliver data to a protocol after the
        response body has been delivered to another protocol.
        """
        raise RuntimeError("Response already finished, cannot deliverBody now.")

    def _bodyDataReceived(self, data):
        """
        Called by HTTPClientParser with chunks of data from the response body.
        They will be buffered or delivered to the protocol passed to
        deliverBody.
        """
        return

    _bodyDataReceived = makeStatefulDispatcher("bodyDataReceived", _bodyDataReceived)

    def _bodyDataReceived_INITIAL(self, data):
        """
        Buffer any data received for later delivery to a protocol passed to
        C{deliverBody}.

        Little or no data should be buffered by this method, since the
        transport has been paused and will not be resumed until a protocol
        is supplied.
        """
        self._bodyBuffer.append(data)

    def _bodyDataReceived_CONNECTED(self, data):
        """
        Deliver any data received to the protocol to which this L{Response}
        is connected.
        """
        self._bodyProtocol.dataReceived(data)

    def _bodyDataReceived_DEFERRED_CLOSE(self, data):
        """
        It is invalid for data to be delivered after it has been indicated
        that the response body has been completely delivered.
        """
        raise RuntimeError("Cannot receive body data after _bodyDataFinished")

    def _bodyDataReceived_FINISHED(self, data):
        """
        It is invalid for data to be delivered after the response body has
        been delivered to a protocol.
        """
        raise RuntimeError("Cannot receive body data after protocol disconnected")

    def _bodyDataFinished(self, reason=None):
        """
        Called by HTTPClientParser when no more body data is available.  If the
        optional reason is supplied, this indicates a problem or potential
        problem receiving all of the response body.
        """
        return

    _bodyDataFinished = makeStatefulDispatcher("bodyDataFinished", _bodyDataFinished)

    def _bodyDataFinished_INITIAL(self, reason=None):
        """
        Move to the C{'DEFERRED_CLOSE'} state to wait for a protocol to
        which to deliver the response body.
        """
        self._state = "DEFERRED_CLOSE"
        if reason is None:
            reason = Failure(ResponseDone("Response body fully received"))
        self._reason = reason

    def _bodyDataFinished_CONNECTED(self, reason=None):
        """
        Disconnect the protocol and move to the C{'FINISHED'} state.
        """
        if reason is None:
            reason = Failure(ResponseDone("Response body fully received"))
        self._bodyProtocol.connectionLost(reason)
        self._bodyProtocol = None
        self._state = "FINISHED"

    def _bodyDataFinished_DEFERRED_CLOSE(self):
        """
        It is invalid to attempt to notify the L{Response} of the end of the
        response body data more than once.
        """
        raise RuntimeError("Cannot finish body data more than once")

    def _bodyDataFinished_FINISHED(self):
        """
        It is invalid to attempt to notify the L{Response} of the end of the
        response body data more than once.
        """
        raise RuntimeError("Cannot finish body data after protocol disconnected")


@implementer(IConsumer)
class ChunkedEncoder:
    __doc__ = "\n    Helper object which exposes L{IConsumer} on top of L{HTTP11ClientProtocol}\n    for streaming request bodies to the server.\n    "

    def __init__(self, transport):
        self.transport = transport

    def _allowNoMoreWrites(self):
        """
        Indicate that no additional writes are allowed.  Attempts to write
        after calling this method will be met with an exception.
        """
        self.transport = None

    def registerProducer(self, producer, streaming):
        """
        Register the given producer with C{self.transport}.
        """
        self.transport.registerProducer(producer, streaming)

    def write(self, data):
        """
        Write the given request body bytes to the transport using chunked
        encoding.

        @type data: C{bytes}
        """
        if self.transport is None:
            raise ExcessWrite()
        self.transport.writeSequence((networkString("%x\r\n" % len(data)),
         data, b'\r\n'))

    def unregisterProducer(self):
        """
        Indicate that the request body is complete and finish the request.
        """
        self.write(b'')
        self.transport.unregisterProducer()
        self._allowNoMoreWrites()


@implementer(IPushProducer)
class TransportProxyProducer:
    __doc__ = "\n    An L{twisted.internet.interfaces.IPushProducer} implementation which\n    wraps another such thing and proxies calls to it until it is told to stop.\n\n    @ivar _producer: The wrapped L{twisted.internet.interfaces.IPushProducer}\n    provider or L{None} after this proxy has been stopped.\n    "
    disconnecting = False

    def __init__(self, producer):
        self._producer = producer

    def stopProxying(self):
        """
        Stop forwarding calls of L{twisted.internet.interfaces.IPushProducer}
        methods to the underlying L{twisted.internet.interfaces.IPushProducer}
        provider.
        """
        self._producer = None

    def stopProducing(self):
        """
        Proxy the stoppage to the underlying producer, unless this proxy has
        been stopped.
        """
        if self._producer is not None:
            self._producer.stopProducing()

    def resumeProducing(self):
        """
        Proxy the resumption to the underlying producer, unless this proxy has
        been stopped.
        """
        if self._producer is not None:
            self._producer.resumeProducing()

    def pauseProducing(self):
        """
        Proxy the pause to the underlying producer, unless this proxy has been
        stopped.
        """
        if self._producer is not None:
            self._producer.pauseProducing()

    def loseConnection(self):
        """
        Proxy the request to lose the connection to the underlying producer,
        unless this proxy has been stopped.
        """
        if self._producer is not None:
            self._producer.loseConnection()


class HTTP11ClientProtocol(Protocol):
    __doc__ = "\n    L{HTTP11ClientProtocol} is an implementation of the HTTP 1.1 client\n    protocol.  It supports as few features as possible.\n\n    @ivar _parser: After a request is issued, the L{HTTPClientParser} to\n        which received data making up the response to that request is\n        delivered.\n\n    @ivar _finishedRequest: After a request is issued, the L{Deferred} which\n        will fire when a L{Response} object corresponding to that request is\n        available.  This allows L{HTTP11ClientProtocol} to fail the request\n        if there is a connection or parsing problem.\n\n    @ivar _currentRequest: After a request is issued, the L{Request}\n        instance used to make that request.  This allows\n        L{HTTP11ClientProtocol} to stop request generation if necessary (for\n        example, if the connection is lost).\n\n    @ivar _transportProxy: After a request is issued, the\n        L{TransportProxyProducer} to which C{_parser} is connected.  This\n        allows C{_parser} to pause and resume the transport in a way which\n        L{HTTP11ClientProtocol} can exert some control over.\n\n    @ivar _responseDeferred: After a request is issued, the L{Deferred} from\n        C{_parser} which will fire with a L{Response} when one has been\n        received.  This is eventually chained with C{_finishedRequest}, but\n        only in certain cases to avoid double firing that Deferred.\n\n    @ivar _state: Indicates what state this L{HTTP11ClientProtocol} instance\n        is in with respect to transmission of a request and reception of a\n        response.  This may be one of the following strings:\n\n          - QUIESCENT: This is the state L{HTTP11ClientProtocol} instances\n            start in.  Nothing is happening: no request is being sent and no\n            response is being received or expected.\n\n          - TRANSMITTING: When a request is made (via L{request}), the\n            instance moves to this state.  L{Request.writeTo} has been used\n            to start to send a request but it has not yet finished.\n\n          - TRANSMITTING_AFTER_RECEIVING_RESPONSE: The server has returned a\n            complete response but the request has not yet been fully sent\n            yet.  The instance will remain in this state until the request\n            is fully sent.\n\n          - GENERATION_FAILED: There was an error while the request.  The\n            request was not fully sent to the network.\n\n          - WAITING: The request was fully sent to the network.  The\n            instance is now waiting for the response to be fully received.\n\n          - ABORTING: Application code has requested that the HTTP connection\n            be aborted.\n\n          - CONNECTION_LOST: The connection has been lost.\n    @type _state: C{str}\n\n    @ivar _abortDeferreds: A list of C{Deferred} instances that will fire when\n        the connection is lost.\n    "
    _state = "QUIESCENT"
    _parser = None
    _finishedRequest = None
    _currentRequest = None
    _transportProxy = None
    _responseDeferred = None
    _log = Logger()

    def __init__(self, quiescentCallback=(lambda c: None)):
        self._quiescentCallback = quiescentCallback
        self._abortDeferreds = []

    @property
    def state(self):
        return self._state

    def request(self, request):
        """
        Issue C{request} over C{self.transport} and return a L{Deferred} which
        will fire with a L{Response} instance or an error.

        @param request: The object defining the parameters of the request to
           issue.
        @type request: L{Request}

        @rtype: L{Deferred}
        @return: The deferred may errback with L{RequestGenerationFailed} if
            the request was not fully written to the transport due to a local
            error.  It may errback with L{RequestTransmissionFailed} if it was
            not fully written to the transport due to a network error.  It may
            errback with L{ResponseFailed} if the request was sent (not
            necessarily received) but some or all of the response was lost.  It
            may errback with L{RequestNotSent} if it is not possible to send
            any more requests using this L{HTTP11ClientProtocol}.
        """
        if self._state != "QUIESCENT":
            return fail(RequestNotSent())
        else:
            self._state = "TRANSMITTING"
            _requestDeferred = maybeDeferred(request.writeTo, self.transport)

            def cancelRequest(ign):
                if self._state in ('TRANSMITTING', 'TRANSMITTING_AFTER_RECEIVING_RESPONSE'):
                    _requestDeferred.cancel()
                else:
                    self.transport.abortConnection()
                    self._disconnectParser(Failure(CancelledError()))

            self._finishedRequest = Deferred(cancelRequest)
            self._currentRequest = request
            self._transportProxy = TransportProxyProducer(self.transport)
            self._parser = HTTPClientParser(request, self._finishResponse)
            self._parser.makeConnection(self._transportProxy)
            self._responseDeferred = self._parser._responseDeferred

            def cbRequestWritten(ignored):
                if self._state == "TRANSMITTING":
                    self._state = "WAITING"
                    self._responseDeferred.chainDeferred(self._finishedRequest)

            def ebRequestWriting(err):
                if self._state == "TRANSMITTING":
                    self._state = "GENERATION_FAILED"
                    self.transport.abortConnection()
                    self._finishedRequest.errback(Failure(RequestGenerationFailed([err])))
                else:
                    self._log.failure("Error writing request, but not in valid state to finalize request: {state}",
                      failure=err,
                      state=(self._state))

            _requestDeferred.addCallbacks(cbRequestWritten, ebRequestWriting)
            return self._finishedRequest

    def _finishResponse(self, rest):
        """
        Called by an L{HTTPClientParser} to indicate that it has parsed a
        complete response.

        @param rest: A C{bytes} giving any trailing bytes which were given to
            the L{HTTPClientParser} which were not part of the response it
            was parsing.
        """
        return

    _finishResponse = makeStatefulDispatcher("finishResponse", _finishResponse)

    def _finishResponse_WAITING(self, rest):
        if self._state == "WAITING":
            self._state = "QUIESCENT"
        else:
            self._state = "TRANSMITTING_AFTER_RECEIVING_RESPONSE"
            self._responseDeferred.chainDeferred(self._finishedRequest)
        if self._parser is None:
            return
        reason = ConnectionDone("synthetic!")
        connHeaders = self._parser.connHeaders.getRawHeaders(b'connection', ())
        if b'close' in connHeaders or self._state != "QUIESCENT" or not self._currentRequest.persistent:
            self._giveUp(Failure(reason))
        else:
            self.transport.resumeProducing()
            try:
                self._quiescentCallback(self)
            except:
                self._log.failure("")
                self.transport.loseConnection()

            self._disconnectParser(reason)

    _finishResponse_TRANSMITTING = _finishResponse_WAITING

    def _disconnectParser(self, reason):
        """
        If there is still a parser, call its C{connectionLost} method with the
        given reason.  If there is not, do nothing.

        @type reason: L{Failure}
        """
        if self._parser is not None:
            parser = self._parser
            self._parser = None
            self._currentRequest = None
            self._finishedRequest = None
            self._responseDeferred = None
            self._transportProxy.stopProxying()
            self._transportProxy = None
            parser.connectionLost(reason)

    def _giveUp(self, reason):
        """
        Lose the underlying connection and disconnect the parser with the given
        L{Failure}.

        Use this method instead of calling the transport's loseConnection
        method directly otherwise random things will break.
        """
        self.transport.loseConnection()
        self._disconnectParser(reason)

    def dataReceived(self, bytes):
        """
        Handle some stuff from some place.
        """
        try:
            self._parser.dataReceived(bytes)
        except:
            self._giveUp(Failure())

    def connectionLost(self, reason):
        """
        The underlying transport went away.  If appropriate, notify the parser
        object.
        """
        return

    connectionLost = makeStatefulDispatcher("connectionLost", connectionLost)

    def _connectionLost_QUIESCENT(self, reason):
        """
        Nothing is currently happening.  Move to the C{'CONNECTION_LOST'}
        state but otherwise do nothing.
        """
        self._state = "CONNECTION_LOST"

    def _connectionLost_GENERATION_FAILED(self, reason):
        """
        The connection was in an inconsistent state.  Move to the
        C{'CONNECTION_LOST'} state but otherwise do nothing.
        """
        self._state = "CONNECTION_LOST"

    def _connectionLost_TRANSMITTING(self, reason):
        """
        Fail the L{Deferred} for the current request, notify the request
        object that it does not need to continue transmitting itself, and
        move to the C{'CONNECTION_LOST'} state.
        """
        self._state = "CONNECTION_LOST"
        self._finishedRequest.errback(Failure(RequestTransmissionFailed([reason])))
        del self._finishedRequest
        self._currentRequest.stopWriting()

    def _connectionLost_TRANSMITTING_AFTER_RECEIVING_RESPONSE(self, reason):
        """
        Move to the C{'CONNECTION_LOST'} state.
        """
        self._state = "CONNECTION_LOST"

    def _connectionLost_WAITING(self, reason):
        """
        Disconnect the response parser so that it can propagate the event as
        necessary (for example, to call an application protocol's
        C{connectionLost} method, or to fail a request L{Deferred}) and move
        to the C{'CONNECTION_LOST'} state.
        """
        self._disconnectParser(reason)
        self._state = "CONNECTION_LOST"

    def _connectionLost_ABORTING(self, reason):
        """
        Disconnect the response parser with a L{ConnectionAborted} failure, and
        move to the C{'CONNECTION_LOST'} state.
        """
        self._disconnectParser(Failure(ConnectionAborted()))
        self._state = "CONNECTION_LOST"
        for d in self._abortDeferreds:
            d.callback(None)

        self._abortDeferreds = []

    def abort(self):
        """
        Close the connection and cause all outstanding L{request} L{Deferred}s
        to fire with an error.
        """
        if self._state == "CONNECTION_LOST":
            return succeed(None)
        else:
            self.transport.loseConnection()
            self._state = "ABORTING"
            d = Deferred()
            self._abortDeferreds.append(d)
            return d
