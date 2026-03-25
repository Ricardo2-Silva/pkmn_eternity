# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\media\devices\__init__.py
import atexit, pyglet

def get_audio_device_manager():
    global _audio_device_manager
    if _audio_device_manager:
        return _audio_device_manager
    else:
        _audio_device_manager = None
        if pyglet.compat_platform == "win32":
            from pyglet.media.devices.win32 import Win32AudioDeviceManager
            _audio_device_manager = Win32AudioDeviceManager()
        return _audio_device_manager


def _delete_manager():
    """Deletes existing manager. If audio device manager is stored anywhere.
    Required to remove handlers before exit, as it can cause problems with the event system's weakrefs."""
    global _audio_device_manager
    _audio_device_manager = None


_audio_device_manager = None
atexit.register(_delete_manager)
