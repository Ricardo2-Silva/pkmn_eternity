# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\python\win32.py
"""
Win32 utilities.

See also twisted.python.shortcut.

@var O_BINARY: the 'binary' mode flag on Windows, or 0 on other platforms, so it
    may safely be OR'ed into a mask for os.open.
"""
from __future__ import division, absolute_import
import re, os
ERROR_FILE_NOT_FOUND = 2
ERROR_PATH_NOT_FOUND = 3
ERROR_INVALID_NAME = 123
ERROR_DIRECTORY = 267
O_BINARY = getattr(os, "O_BINARY", 0)

class FakeWindowsError(OSError):
    __doc__ = "\n    Stand-in for sometimes-builtin exception on platforms for which it\n    is missing.\n    "


try:
    WindowsError = WindowsError
except NameError:
    WindowsError = FakeWindowsError

_cmdLineQuoteRe = re.compile('(\\\\*)"')
_cmdLineQuoteRe2 = re.compile("(\\\\+)\\Z")

def cmdLineQuote(s):
    """
    Internal method for quoting a single command-line argument.

    @param s: an unquoted string that you want to quote so that something that
        does cmd.exe-style unquoting will interpret it as a single argument,
        even if it contains spaces.
    @type s: C{str}

    @return: a quoted string.
    @rtype: C{str}
    """
    quote = (" " in s or "\t" in s or '"' in s or s == "") and '"' or ""
    return quote + _cmdLineQuoteRe2.sub("\\1\\1", _cmdLineQuoteRe.sub('\\1\\1\\\\"', s)) + quote


def quoteArguments(arguments):
    """
    Quote an iterable of command-line arguments for passing to CreateProcess or
    a similar API.  This allows the list passed to C{reactor.spawnProcess} to
    match the child process's C{sys.argv} properly.

    @param arglist: an iterable of C{str}, each unquoted.

    @return: a single string, with the given sequence quoted as necessary.
    """
    return " ".join([cmdLineQuote(a) for a in arguments])


class _ErrorFormatter(object):
    __doc__ = "\n    Formatter for Windows error messages.\n\n    @ivar winError: A callable which takes one integer error number argument\n        and returns an L{exceptions.WindowsError} instance for that error (like\n        L{ctypes.WinError}).\n\n    @ivar formatMessage: A callable which takes one integer error number\n        argument and returns a C{str} giving the message for that error (like\n        L{win32api.FormatMessage}).\n\n    @ivar errorTab: A mapping from integer error numbers to C{str} messages\n        which correspond to those erorrs (like I{socket.errorTab}).\n    "

    def __init__(self, WinError, FormatMessage, errorTab):
        self.winError = WinError
        self.formatMessage = FormatMessage
        self.errorTab = errorTab

    def fromEnvironment(cls):
        """
        Get as many of the platform-specific error translation objects as
        possible and return an instance of C{cls} created with them.
        """
        try:
            from ctypes import WinError
        except ImportError:
            WinError = None

        try:
            from win32api import FormatMessage
        except ImportError:
            FormatMessage = None

        try:
            from socket import errorTab
        except ImportError:
            errorTab = None

        return cls(WinError, FormatMessage, errorTab)

    fromEnvironment = classmethod(fromEnvironment)

    def formatError(self, errorcode):
        """
        Returns the string associated with a Windows error message, such as the
        ones found in socket.error.

        Attempts direct lookup against the win32 API via ctypes and then
        pywin32 if available), then in the error table in the socket module,
        then finally defaulting to C{os.strerror}.

        @param errorcode: the Windows error code
        @type errorcode: C{int}

        @return: The error message string
        @rtype: C{str}
        """
        if self.winError is not None:
            return self.winError(errorcode).strerror
        else:
            if self.formatMessage is not None:
                return self.formatMessage(errorcode)
            if self.errorTab is not None:
                result = self.errorTab.get(errorcode)
                if result is not None:
                    return result
            return os.strerror(errorcode)


formatError = _ErrorFormatter.fromEnvironment().formatError
