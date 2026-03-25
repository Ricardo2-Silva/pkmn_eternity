# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyasn1\debug.py
import logging
from pyasn1 import __version__
from pyasn1 import error
from pyasn1.compat.octets import octs2ints
__all__ = [
 "Debug", "setLogger", "hexdump"]
flagNone = 0
flagEncoder = 1
flagDecoder = 2
flagAll = 65535
flagMap = {
 'none': flagNone, 
 'encoder': flagEncoder, 
 'decoder': flagDecoder, 
 'all': flagAll}

class Printer(object):

    def __init__(self, logger=None, handler=None, formatter=None):
        if logger is None:
            logger = logging.getLogger("pyasn1")
        else:
            logger.setLevel(logging.DEBUG)
            if handler is None:
                handler = logging.StreamHandler()
            if formatter is None:
                formatter = logging.Formatter("%(asctime)s %(name)s: %(message)s")
        handler.setFormatter(formatter)
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        self._Printer__logger = logger

    def __call__(self, msg):
        self._Printer__logger.debug(msg)

    def __str__(self):
        return "<python logging>"


if hasattr(logging, "NullHandler"):
    NullHandler = logging.NullHandler
else:

    class NullHandler(logging.Handler):

        def emit(self, record):
            return


class Debug(object):
    defaultPrinter = Printer()

    def __init__(self, *flags, **options):
        self._flags = flagNone
        if "loggerName" in options:
            self._printer = Printer(logger=(logging.getLogger(options["loggerName"])),
              handler=(NullHandler()))
        elif "printer" in options:
            self._printer = options.get("printer")
        else:
            self._printer = self.defaultPrinter
        self._printer("running pyasn1 %s, debug flags %s" % (__version__, ", ".join(flags)))
        for flag in flags:
            inverse = flag and flag[0] in ('!', '~')
            if inverse:
                flag = flag[1:]
            try:
                if inverse:
                    self._flags &= ~flagMap[flag]
                else:
                    self._flags |= flagMap[flag]
            except KeyError:
                raise error.PyAsn1Error("bad debug flag %s" % flag)

            self._printer("debug category '%s' %s" % (flag, inverse and "disabled" or "enabled"))

    def __str__(self):
        return "logger %s, flags %x" % (self._printer, self._flags)

    def __call__(self, msg):
        self._printer(msg)

    def __and__(self, flag):
        return self._flags & flag

    def __rand__(self, flag):
        return flag & self._flags


logger = 0

def setLogger(userLogger):
    global logger
    if userLogger:
        logger = userLogger
    else:
        logger = 0


def hexdump(octets):
    return " ".join(["%s%.2X" % (n % 16 == 0 and "\n%.5d: " % n or "", x) for n, x in zip(range(len(octets)), octs2ints(octets))])


class Scope(object):

    def __init__(self):
        self._list = []

    def __str__(self):
        return ".".join(self._list)

    def push(self, token):
        self._list.append(token)

    def pop(self):
        return self._list.pop()


scope = Scope()
