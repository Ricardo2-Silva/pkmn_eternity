# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: asyncio\__init__.py
"""The asyncio package, tracking PEP 3156."""
import sys
try:
    from . import selectors
except ImportError:
    import selectors

if sys.platform == "win32":
    try:
        from . import _overlapped
    except ImportError:
        import _overlapped

    from .base_events import *
    from .coroutines import *
    from .events import *
    from .futures import *
    from .locks import *
    from .protocols import *
    from .queues import *
    from .streams import *
    from .subprocess import *
    from .tasks import *
    from .transports import *
    __all__ = base_events.__all__ + coroutines.__all__ + events.__all__ + futures.__all__ + locks.__all__ + protocols.__all__ + queues.__all__ + streams.__all__ + subprocess.__all__ + tasks.__all__ + transports.__all__
    if sys.platform == "win32":
        from .windows_events import *
        __all__ += windows_events.__all__
else:
    from .unix_events import *
    __all__ += unix_events.__all__
