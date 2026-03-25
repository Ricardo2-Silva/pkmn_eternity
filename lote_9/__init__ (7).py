# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\media\drivers\openal\__init__.py
from .adaptation import OpenALDriver
import pyglet
_debug = pyglet.options["debug_media"]
_debug_buffers = pyglet.options.get("debug_media_buffers", False)

def create_audio_driver(device_name=None):
    _driver = OpenALDriver(device_name)
    if _debug:
        print("OpenAL", _driver.get_version())
    return _driver
