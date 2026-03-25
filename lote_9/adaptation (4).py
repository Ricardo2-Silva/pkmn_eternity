# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\media\drivers\xaudio2\adaptation.py
import math, pyglet
from pyglet.media.drivers.base import AbstractAudioDriver, AbstractAudioPlayer
from pyglet.media.drivers.listener import AbstractListener
from pyglet.media.events import MediaEvent
from pyglet.util import debug_print
from . import interface
_debug = debug_print("debug_media")

def _convert_coordinates(coordinates):
    x, y, z = coordinates
    return (x, y, -z)


class XAudio2AudioPlayer(AbstractAudioPlayer):
    _cone_inner_angle = 360
    _cone_outer_angle = 360
    min_buffer_size = 9600
    max_buffer_count = 3

    def __init__(self, driver, xa2_driver, source, player):
        super(XAudio2AudioPlayer, self).__init__(source, player)
        self.driver = driver
        self._xa2_driver = xa2_driver
        self._flushing = False
        self._deleted = False
        self._playing = False
        self._write_cursor = 0
        self._play_cursor = 0
        self._events = []
        self._timestamps = []
        self.buffer_end_submitted = False
        self._buffers = []
        self._xa2_source_voice = self._xa2_driver.get_source_voice(source, self)
        self._buffer_size = int(source.audio_format.sample_rate * 2)

    def on_driver_destroy(self):
        self.stop()
        self._xa2_source_voice = None

    def on_driver_reset(self):
        self._xa2_source_voice = self._xa2_driver.get_source_voice(self.source, self)
        for cx2_buffer in self._buffers:
            self._xa2_source_voice.submit_buffer(cx2_buffer)

    def __del__(self):
        if self._xa2_source_voice:
            self._xa2_source_voice = None

    def delete(self):
        """Called from Player. Docs says to cleanup resources, but other drivers wait for GC to do it?"""
        if self._xa2_source_voice:
            self._deleted = True

    def play(self):
        if not _debug("XAudio2 play"):
            raise AssertionError
        else:
            if not self._playing:
                self._playing = True
                if not self._flushing:
                    self._xa2_source_voice.play()
            assert _debug("return XAudio2 play")

    def stop(self):
        if not _debug("XAudio2 stop"):
            raise AssertionError
        else:
            if self._playing:
                self._playing = False
                self.buffer_end_submitted = False
                self._xa2_source_voice.stop()
            assert _debug("return XAudio2 stop")

    def clear(self):
        assert _debug("XAudio2 clear")
        super(XAudio2AudioPlayer, self).clear()
        self._play_cursor = 0
        self._write_cursor = 0
        self.buffer_end_submitted = False
        self._deleted = False
        if self._buffers:
            self._flushing = True
        self._xa2_source_voice.flush()
        self._buffers.clear()
        del self._events[:]
        del self._timestamps[:]

    def _restart(self, dt):
        """Prefill audio and attempt to replay audio."""
        if self._playing:
            if self._xa2_source_voice:
                self.refill_source_player()
                self._xa2_source_voice.play()

    def refill_source_player(self):
        """Obtains audio data from the source, puts it into a buffer to submit to the voice.
        Unlike the other drivers this does not carve pieces of audio from the buffer and slowly
        consume it. This submits the buffer retrieved from the decoder in it's entirety.
        """
        buffers_queued = self._xa2_source_voice.buffers_queued
        while len(self._buffers) > buffers_queued:
            buffer = self._buffers.pop(0)
            self._play_cursor += buffer.AudioBytes
            del buffer

        if self._flushing:
            if buffers_queued == 0:
                self._flushing = False
                pyglet.clock.schedule_once(self._restart, 0)
            return
        if self._deleted:
            if buffers_queued == 0:
                self._deleted = False
                self._xa2_driver.return_voice(self._xa2_source_voice)
            return
        if self.buffer_end_submitted:
            if buffers_queued == 0:
                self._xa2_source_voice.stop()
                MediaEvent(0, "on_eos")._sync_dispatch_to_player(self.player)
        else:
            current_buffers = []
            while buffers_queued < self.max_buffer_count:
                audio_data = self.source.get_audio_data(self._buffer_size, 0.0)
                if audio_data:
                    assert _debug("Xaudio2: audio data - length: {}, duration: {}, buffer size: {}".format(audio_data.length, audio_data.duration, self._buffer_size))
                    if audio_data.length == 0:
                        continue
                        x2_buffer = self._xa2_driver.create_buffer(audio_data)
                        current_buffers.append(x2_buffer)
                        self._write_cursor += x2_buffer.AudioBytes
                        self._add_audiodata_events(audio_data)
                        self._add_audiodata_timestamp(audio_data)
                        buffers_queued += 1
                    else:
                        self.buffer_end_submitted = True
                        break

            for cx2_buffer in current_buffers:
                self._xa2_source_voice.submit_buffer(cx2_buffer)

            self._buffers.extend(current_buffers)
        self._dispatch_pending_events()

    def _dispatch_new_event(self, event_name):
        MediaEvent(0, event_name)._sync_dispatch_to_player(self.player)

    def _add_audiodata_events(self, audio_data):
        for event in audio_data.events:
            event_cursor = self._write_cursor + event.timestamp * self.source.audio_format.bytes_per_second
            assert _debug("Adding event", event, "at", event_cursor)
            self._events.append((event_cursor, event))

    def _add_audiodata_timestamp(self, audio_data):
        ts_cursor = self._write_cursor + audio_data.length
        self._timestamps.append((
         ts_cursor, audio_data.timestamp + audio_data.duration))

    def _dispatch_pending_events(self):
        pending_events = []
        while self._events and self._events[0][0] <= self._play_cursor:
            _, event = self._events.pop(0)
            pending_events.append(event)

        if not _debug("Dispatching pending events: {}".format(pending_events)):
            raise AssertionError
        elif not _debug("Remaining events: {}".format(self._events)):
            raise AssertionError
        for event in pending_events:
            event._sync_dispatch_to_player(self.player)

    def _cleanup_timestamps(self):
        while self._timestamps and self._timestamps[0][0] < self._play_cursor:
            del self._timestamps[0]

    def get_time(self):
        self.update_play_cursor()
        if self._timestamps:
            cursor, ts = self._timestamps[0]
            result = ts + (self._play_cursor - cursor) / float(self.source.audio_format.bytes_per_second)
        else:
            result = None
        return result

    def set_volume(self, volume):
        self._xa2_source_voice.volume = volume

    def set_position(self, position):
        if self._xa2_source_voice.is_emitter:
            self._xa2_source_voice.position = _convert_coordinates(position)

    def set_min_distance(self, min_distance):
        """Not a true min distance, but similar effect. Changes CurveDistanceScaler default is 1."""
        if self._xa2_source_voice.is_emitter:
            self._xa2_source_voice.distance_scaler = min_distance

    def set_max_distance(self, max_distance):
        """No such thing built into xaudio2"""
        return

    def set_pitch(self, pitch):
        self._xa2_source_voice.frequency = pitch

    def set_cone_orientation(self, cone_orientation):
        if self._xa2_source_voice.is_emitter:
            self._xa2_source_voice.cone_orientation = _convert_coordinates(cone_orientation)

    def set_cone_inner_angle(self, cone_inner_angle):
        if self._xa2_source_voice.is_emitter:
            self._cone_inner_angle = int(cone_inner_angle)
            self._set_cone_angles()

    def set_cone_outer_angle(self, cone_outer_angle):
        if self._xa2_source_voice.is_emitter:
            self._cone_outer_angle = int(cone_outer_angle)
            self._set_cone_angles()

    def _set_cone_angles(self):
        inner = min(self._cone_inner_angle, self._cone_outer_angle)
        outer = max(self._cone_inner_angle, self._cone_outer_angle)
        self._xa2_source_voice.set_cone_angles(math.radians(inner), math.radians(outer))

    def set_cone_outer_gain(self, cone_outer_gain):
        if self._xa2_source_voice.is_emitter:
            self._xa2_source_voice.cone_outside_volume = cone_outer_gain

    def prefill_audio(self):
        if not self._flushing:
            self.refill_source_player()


class XAudio2Driver(AbstractAudioDriver):

    def __init__(self):
        self._xa2_driver = interface.XAudio2Driver()
        self._xa2_listener = self._xa2_driver.create_listener()
        if not self._xa2_driver is not None:
            raise AssertionError
        elif not self._xa2_listener is not None:
            raise AssertionError

    def __del__(self):
        self.delete()

    def get_performance(self):
        assert self._xa2_driver is not None
        return self._xa2_driver.get_performance()

    def create_audio_player(self, source, player):
        assert self._xa2_driver is not None
        return XAudio2AudioPlayer(self, self._xa2_driver, source, player)

    def get_listener(self):
        if not self._xa2_driver is not None:
            raise AssertionError
        elif not self._xa2_listener is not None:
            raise AssertionError
        return XAudio2Listener(self._xa2_listener, self._xa2_driver)

    def delete(self):
        self._xa2_listener = None


class XAudio2Listener(AbstractListener):

    def __init__(self, xa2_listener, xa2_driver):
        self._xa2_listener = xa2_listener
        self._xa2_driver = xa2_driver

    def _set_volume(self, volume):
        self._volume = volume
        self._xa2_driver.volume = volume

    def _set_position(self, position):
        self._position = position
        self._xa2_listener.position = _convert_coordinates(position)

    def _set_forward_orientation(self, orientation):
        self._forward_orientation = orientation
        self._set_orientation()

    def _set_up_orientation(self, orientation):
        self._up_orientation = orientation
        self._set_orientation()

    def _set_orientation(self):
        self._xa2_listener.orientation = _convert_coordinates(self._forward_orientation) + _convert_coordinates(self._up_orientation)
