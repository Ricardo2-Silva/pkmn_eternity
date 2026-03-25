# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\media\drivers\__init__.py
"""Drivers for playing back media."""
import atexit, pyglet
_debug = pyglet.options["debug_media"]

def get_audio_driver():
    """Get the preferred audio driver for the current platform.

    Currently pyglet supports DirectSound, PulseAudio and OpenAL drivers. If
    the platform supports more than one of those audio drivers, the
    application can give its preference with :data:`pyglet.options` ``audio``
    keyword. See the Programming guide, section
    :doc:`/programming_guide/media`.

    Returns:
        AbstractAudioDriver : The concrete implementation of the preferred 
        audio driver for this platform.
    """
    global _audio_driver
    if _audio_driver:
        return _audio_driver
    else:
        _audio_driver = None
        for driver_name in pyglet.options["audio"]:
            try:
                if driver_name == "pulse":
                    from . import pulse
                    _audio_driver = pulse.create_audio_driver()
                    break
                elif driver_name == "xaudio2":
                    pass
                from pyglet.libs.win32.constants import WINDOWS_8_OR_GREATER
                if WINDOWS_8_OR_GREATER:
                    from . import xaudio2
                    _audio_driver = xaudio2.create_audio_driver()
                    break
                elif driver_name == "directsound":
                    from . import directsound
                    _audio_driver = directsound.create_audio_driver()
                    break
                elif driver_name == "openal":
                    from . import openal
                    _audio_driver = openal.create_audio_driver()
                    break
                else:
                    if driver_name == "silent":
                        from . import silent
                        _audio_driver = silent.create_audio_driver()
                        break
            except Exception:
                if _debug:
                    print("Error importing driver %s:" % driver_name)
                    import traceback
                    traceback.print_exc()

        else:
            from . import silent
            _audio_driver = silent.create_audio_driver()

        return _audio_driver


def _delete_audio_driver():
    global _audio_driver
    from .. import Source
    for p in Source._players:
        p.on_player_eos = None
        del p

    del Source._players
    _audio_driver = None


_audio_driver = None
atexit.register(_delete_audio_driver)
