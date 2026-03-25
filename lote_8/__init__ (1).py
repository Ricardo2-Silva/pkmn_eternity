# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\app\__init__.py
"""Application-wide functionality.

Applications
------------

Most applications need only call :func:`run` after creating one or more 
windows to begin processing events.  For example, a simple application 
consisting of one window is::

    import pyglet

    win = pyglet.window.Window()
    pyglet.app.run()

Events
======

To handle events on the main event loop, instantiate it manually.  The
following example exits the application as soon as any window is closed (the
default policy is to wait until all windows are closed)::

    event_loop = pyglet.app.EventLoop()

    @event_loop.event
    def on_window_close(window):
        event_loop.exit()

.. versionadded:: 1.1
"""
import sys, weakref
from pyglet.app.base import EventLoop
from pyglet import compat_platform
_is_pyglet_doc_run = hasattr(sys, "is_pyglet_doc_run") and sys.is_pyglet_doc_run
if _is_pyglet_doc_run:
    from pyglet.app.base import PlatformEventLoop
elif compat_platform == "darwin":
    from pyglet.app.cocoa import CocoaEventLoop as PlatformEventLoop
elif compat_platform in ('win32', 'cygwin'):
    from pyglet.app.win32 import Win32EventLoop as PlatformEventLoop
else:
    from pyglet.app.xlib import XlibEventLoop as PlatformEventLoop

class AppException(Exception):
    return


windows = weakref.WeakSet()

def run():
    """Begin processing events, scheduled functions and window updates.

    This is a convenience function, equivalent to::

        pyglet.app.event_loop.run()

    """
    event_loop.run()


def exit():
    """Exit the application event loop.

    Causes the application event loop to finish, if an event loop is currently
    running.  The application may not necessarily exit (for example, there may
    be additional code following the `run` invocation).

    This is a convenience function, equivalent to::

        event_loop.exit()

    """
    event_loop.exit()


event_loop = EventLoop()
platform_event_loop = PlatformEventLoop()
