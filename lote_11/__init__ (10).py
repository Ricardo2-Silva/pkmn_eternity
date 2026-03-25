# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: urllib3\__init__.py
"""
urllib3 - Thread-safe connection pooling and re-using.
"""
from __future__ import absolute_import
import warnings
from .connectionpool import HTTPConnectionPool, HTTPSConnectionPool, connection_from_url
from . import exceptions
from .filepost import encode_multipart_formdata
from .poolmanager import PoolManager, ProxyManager, proxy_from_url
from .response import HTTPResponse
from .util.request import make_headers
from .util.url import get_host
from .util.timeout import Timeout
from .util.retry import Retry
import logging
from logging import NullHandler
__author__ = "Andrey Petrov (andrey.petrov@shazow.net)"
__license__ = "MIT"
__version__ = "1.24.1"
__all__ = ('HTTPConnectionPool', 'HTTPSConnectionPool', 'PoolManager', 'ProxyManager',
           'HTTPResponse', 'Retry', 'Timeout', 'add_stderr_logger', 'connection_from_url',
           'disable_warnings', 'encode_multipart_formdata', 'get_host', 'make_headers',
           'proxy_from_url')
logging.getLogger(__name__).addHandler(NullHandler())

def add_stderr_logger(level=logging.DEBUG):
    """
    Helper for quickly adding a StreamHandler to the logger. Useful for
    debugging.

    Returns the handler after adding it.
    """
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(level)
    logger.debug("Added a stderr logging handler to logger: %s", __name__)
    return handler


del NullHandler
warnings.simplefilter("always", (exceptions.SecurityWarning), append=True)
warnings.simplefilter("default", (exceptions.SubjectAltNameWarning), append=True)
warnings.simplefilter("default", (exceptions.InsecurePlatformWarning), append=True)
warnings.simplefilter("default", (exceptions.SNIMissingWarning), append=True)

def disable_warnings(category=exceptions.HTTPWarning):
    """
    Helper for quickly disabling all urllib3 warnings.
    """
    warnings.simplefilter("ignore", category)
