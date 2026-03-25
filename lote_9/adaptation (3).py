# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\media\drivers\silent\adaptation.py
from pyglet.media.drivers.base import AbstractAudioDriver, AbstractAudioPlayer
from pyglet.media.drivers.listener import AbstractListener

class SilentAudioPlayer(AbstractAudioPlayer):

    def delete(self):
        return

    def play(self):
        return

    def stop(self):
        return

    def clear(self):
        return

    def get_write_size(self):
        return

    def write(self, audio_data, length):
        return

    def get_time(self):
        return 0

    def set_volume(self, volume):
        return

    def set_position(self, position):
        return

    def set_min_distance(self, min_distance):
        return

    def set_max_distance(self, max_distance):
        return

    def set_pitch(self, pitch):
        return

    def set_cone_orientation(self, cone_orientation):
        return

    def set_cone_inner_angle(self, cone_inner_angle):
        return

    def set_cone_outer_angle(self, cone_outer_angle):
        return

    def set_cone_outer_gain(self, cone_outer_gain):
        return

    def prefill_audio(self):
        return


class SilentDriver(AbstractAudioDriver):

    def create_audio_player(self, source, player):
        return SilentAudioPlayer(source, player)

    def get_listener(self):
        return SilentListener()

    def delete(self):
        return


class SilentListener(AbstractListener):

    def _set_volume(self, volume):
        return

    def _set_position(self, position):
        return

    def _set_forward_orientation(self, orientation):
        return

    def _set_up_orientation(self, orientation):
        return

    def _set_orientation(self):
        return
