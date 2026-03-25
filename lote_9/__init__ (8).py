# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\media\drivers\pulse\__init__.py
from .adaptation import PulseAudioDriver
import pyglet
_debug = pyglet.options["debug_media"]

def create_audio_driver():
    driver = PulseAudioDriver()
    driver.connect()
    if _debug:
        driver.dump_debug_info()
    return driver
