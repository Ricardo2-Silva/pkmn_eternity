# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: asyncio\protocols.py
"""Abstract Protocol class."""
__all__ = [
 "BaseProtocol", "Protocol", "DatagramProtocol",
 "SubprocessProtocol"]

class BaseProtocol:
    __doc__ = "Common base class for protocol interfaces.\n\n    Usually user implements protocols that derived from BaseProtocol\n    like Protocol or ProcessProtocol.\n\n    The only case when BaseProtocol should be implemented directly is\n    write-only transport like write pipe\n    "

    def connection_made(self, transport):
        """Called when a connection is made.

        The argument is the transport representing the pipe connection.
        To receive data, wait for data_received() calls.
        When the connection is closed, connection_lost() is called.
        """
        return

    def connection_lost(self, exc):
        """Called when the connection is lost or closed.

        The argument is an exception object or None (the latter
        meaning a regular EOF is received or the connection was
        aborted or closed).
        """
        return

    def pause_writing(self):
        """Called when the transport's buffer goes over the high-water mark.

        Pause and resume calls are paired -- pause_writing() is called
        once when the buffer goes strictly over the high-water mark
        (even if subsequent writes increases the buffer size even
        more), and eventually resume_writing() is called once when the
        buffer size reaches the low-water mark.

        Note that if the buffer size equals the high-water mark,
        pause_writing() is not called -- it must go strictly over.
        Conversely, resume_writing() is called when the buffer size is
        equal or lower than the low-water mark.  These end conditions
        are important to ensure that things go as expected when either
        mark is zero.

        NOTE: This is the only Protocol callback that is not called
        through EventLoop.call_soon() -- if it were, it would have no
        effect when it's most needed (when the app keeps writing
        without yielding until pause_writing() is called).
        """
        return

    def resume_writing(self):
        """Called when the transport's buffer drains below the low-water mark.

        See pause_writing() for details.
        """
        return


class Protocol(BaseProtocol):
    __doc__ = "Interface for stream protocol.\n\n    The user should implement this interface.  They can inherit from\n    this class but don't need to.  The implementations here do\n    nothing (they don't raise exceptions).\n\n    When the user wants to requests a transport, they pass a protocol\n    factory to a utility function (e.g., EventLoop.create_connection()).\n\n    When the connection is made successfully, connection_made() is\n    called with a suitable transport object.  Then data_received()\n    will be called 0 or more times with data (bytes) received from the\n    transport; finally, connection_lost() will be called exactly once\n    with either an exception object or None as an argument.\n\n    State machine of calls:\n\n      start -> CM [-> DR*] [-> ER?] -> CL -> end\n\n    * CM: connection_made()\n    * DR: data_received()\n    * ER: eof_received()\n    * CL: connection_lost()\n    "

    def data_received(self, data):
        """Called when some data is received.

        The argument is a bytes object.
        """
        return

    def eof_received(self):
        """Called when the other end calls write_eof() or equivalent.

        If this returns a false value (including None), the transport
        will close itself.  If it returns a true value, closing the
        transport is up to the protocol.
        """
        return


class DatagramProtocol(BaseProtocol):
    __doc__ = "Interface for datagram protocol."

    def datagram_received(self, data, addr):
        """Called when some datagram is received."""
        return

    def error_received(self, exc):
        """Called when a send or receive operation raises an OSError.

        (Other than BlockingIOError or InterruptedError.)
        """
        return


class SubprocessProtocol(BaseProtocol):
    __doc__ = "Interface for protocol for subprocess calls."

    def pipe_data_received(self, fd, data):
        """Called when the subprocess writes data into stdout/stderr pipe.

        fd is int file descriptor.
        data is bytes object.
        """
        return

    def pipe_connection_lost(self, fd, exc):
        """Called when a file descriptor associated with the child process is
        closed.

        fd is the int file descriptor that was closed.
        """
        return

    def process_exited(self):
        """Called when subprocess has exited."""
        return
