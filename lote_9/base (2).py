# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\media\drivers\base.py
import math, weakref
from abc import ABCMeta, abstractmethod
from pyglet.util import with_metaclass

class AbstractAudioPlayer(with_metaclass(ABCMeta, object)):
    __doc__ = "Base class for driver audio players.\n    "
    AUDIO_DIFF_AVG_NB = 20
    AV_NOSYNC_THRESHOLD = 10.0

    def __init__(self, source, player):
        """Create a new audio player.

        :Parameters:
            `source` : `Source`
                Source to play from.
            `player` : `Player`
                Player to receive EOS and video frame sync events.

        """
        self.source = source
        self.player = weakref.proxy(player)
        self.audio_diff_avg_count = 0
        self.audio_diff_cum = 0.0
        self.audio_diff_avg_coef = math.exp(math.log10(0.01) / self.AUDIO_DIFF_AVG_NB)
        self.audio_diff_threshold = 0.1

    def on_driver_destroy(self):
        """Called before the audio driver is going to be destroyed (a planned destroy)."""
        return

    def on_driver_reset(self):
        """Called after the audio driver has been re-initialized."""
        return

    @abstractmethod
    def play(self):
        """Begin playback."""
        return

    @abstractmethod
    def stop(self):
        """Stop (pause) playback."""
        return

    @abstractmethod
    def delete(self):
        """Stop playing and clean up all resources used by player."""
        return

    def _play_group(self, audio_players):
        """Begin simultaneous playback on a list of audio players."""
        for player in audio_players:
            player.play()

    def _stop_group(self, audio_players):
        """Stop simultaneous playback on a list of audio players."""
        for player in audio_players:
            player.stop()

    @abstractmethod
    def clear(self):
        """Clear all buffered data and prepare for replacement data.

        The player should be stopped before calling this method.
        """
        self.audio_diff_avg_count = 0
        self.audio_diff_cum = 0.0

    @abstractmethod
    def get_time(self):
        """Return approximation of current playback time within current source.

        Returns ``None`` if the audio player does not know what the playback
        time is (for example, before any valid audio data has been read).

        :rtype: float
        :return: current play cursor time, in seconds.
        """
        return

    @abstractmethod
    def prefill_audio(self):
        """Prefill the audio buffer with audio data.

        This method is called before the audio player starts in order to 
        reduce the time it takes to fill the whole audio buffer.
        """
        return

    def get_audio_time_diff(self):
        """Queries the time difference between the audio time and the `Player`
        master clock.

        The time difference returned is calculated using a weighted average on
        previous audio time differences. The algorithms will need at least 20
        measurements before returning a weighted average.

        :rtype: float
        :return: weighted average difference between audio time and master
            clock from `Player`
        """
        audio_time = self.get_time() or 0
        p_time = self.player.time
        diff = audio_time - p_time
        if abs(diff) < self.AV_NOSYNC_THRESHOLD:
            self.audio_diff_cum = diff + self.audio_diff_cum * self.audio_diff_avg_coef
            if self.audio_diff_avg_count < self.AUDIO_DIFF_AVG_NB:
                self.audio_diff_avg_count += 1
        else:
            avg_diff = self.audio_diff_cum * (1 - self.audio_diff_avg_coef)
            if abs(avg_diff) > self.audio_diff_threshold:
                return avg_diff
            else:
                self.audio_diff_avg_count = 0
                self.audio_diff_cum = 0.0
        return 0.0

    def set_volume(self, volume):
        """See `Player.volume`."""
        return

    def set_position(self, position):
        """See :py:attr:`~pyglet.media.Player.position`."""
        return

    def set_min_distance(self, min_distance):
        """See `Player.min_distance`."""
        return

    def set_max_distance(self, max_distance):
        """See `Player.max_distance`."""
        return

    def set_pitch(self, pitch):
        """See :py:attr:`~pyglet.media.Player.pitch`."""
        return

    def set_cone_orientation(self, cone_orientation):
        """See `Player.cone_orientation`."""
        return

    def set_cone_inner_angle(self, cone_inner_angle):
        """See `Player.cone_inner_angle`."""
        return

    def set_cone_outer_angle(self, cone_outer_angle):
        """See `Player.cone_outer_angle`."""
        return

    def set_cone_outer_gain(self, cone_outer_gain):
        """See `Player.cone_outer_gain`."""
        return

    @property
    def source(self):
        """Source to play from."""
        return self._source

    @source.setter
    def source(self, value):
        self._source = weakref.proxy(value)


class AbstractAudioDriver(with_metaclass(ABCMeta, object)):

    @abstractmethod
    def create_audio_player(self, source, player):
        return

    @abstractmethod
    def get_listener(self):
        return

    @abstractmethod
    def delete(self):
        return
