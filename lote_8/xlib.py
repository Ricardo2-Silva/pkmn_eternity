# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\app\xlib.py
import os, select, threading
from pyglet import app
from pyglet.app.base import PlatformEventLoop
from pyglet.util import asbytes

class XlibSelectDevice:

    def fileno(self):
        """Get the file handle for ``select()`` for this device.

        :rtype: int
        """
        raise NotImplementedError("abstract")

    def select(self):
        """Perform event processing on the device.

        Called when ``select()`` returns this device in its list of active
        files.
        """
        raise NotImplementedError("abstract")

    def poll(self):
        """Check if the device has events ready to process.

        :rtype: bool
        :return: True if there are events to process, False otherwise.
        """
        return False


class NotificationDevice(XlibSelectDevice):

    def __init__(self):
        self._sync_file_read, self._sync_file_write = os.pipe()
        self._event = threading.Event()

    def fileno(self):
        return self._sync_file_read

    def set(self):
        self._event.set()
        os.write(self._sync_file_write, asbytes("1"))

    def select(self):
        self._event.clear()
        os.read(self._sync_file_read, 1)
        app.platform_event_loop.dispatch_posted_events()

    def poll(self):
        return self._event.isSet()


class XlibEventLoop(PlatformEventLoop):

    def __init__(self):
        super(XlibEventLoop, self).__init__()
        self._notification_device = NotificationDevice()
        self._select_devices = set()
        self._select_devices.add(self._notification_device)

    def notify(self):
        self._notification_device.set()

    def step(self, timeout=None):
        pending_devices = []
        for device in self._select_devices:
            if device.poll():
                pending_devices.append(device)

        if not pending_devices:
            pending_devices, _, _ = select.select(self._select_devices, (), (), timeout)
        if not pending_devices:
            return False
        else:
            for device in pending_devices:
                device.select()

            return True
