# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\media\drivers\openal\adaptation.py
import weakref
from . import interface
from pyglet.util import debug_print
from pyglet.media.events import MediaEvent
from pyglet.media.drivers.base import AbstractAudioDriver, AbstractAudioPlayer
from pyglet.media.mediathreads import PlayerWorkerThread
from pyglet.media.drivers.listener import AbstractListener
_debug = debug_print("debug_media")

class OpenALDriver(AbstractAudioDriver):

    def __init__(self, device_name=None):
        super().__init__()
        self.device = interface.OpenALDevice(device_name)
        self.context = self.device.create_context()
        self.context.make_current()
        self._listener = OpenALListener(self)
        self.worker = PlayerWorkerThread()
        self.worker.start()

    def __del__(self):
        assert _debug("Delete OpenALDriver")
        self.delete()

    def create_audio_player(self, source, player):
        assert self.device is not None, "Device was closed"
        return OpenALAudioPlayer(self, source, player)

    def delete(self):
        self.worker.stop()
        self.context = None

    def have_version(self, major, minor):
        return (
         major, minor) <= self.get_version()

    def get_version(self):
        assert self.device is not None, "Device was closed"
        return self.device.get_version()

    def get_extensions(self):
        assert self.device is not None, "Device was closed"
        return self.device.get_extensions()

    def have_extension(self, extension):
        return extension in self.get_extensions()

    def get_listener(self):
        return self._listener


class OpenALListener(AbstractListener):

    def __init__(self, driver):
        self._driver = weakref.proxy(driver)
        self._al_listener = interface.OpenALListener()

    def __del__(self):
        assert _debug("Delete OpenALListener")

    def _set_volume(self, volume):
        self._al_listener.gain = volume
        self._volume = volume

    def _set_position(self, position):
        self._al_listener.position = position
        self._position = position

    def _set_forward_orientation(self, orientation):
        self._al_listener.orientation = orientation + self._up_orientation
        self._forward_orientation = orientation

    def _set_up_orientation(self, orientation):
        self._al_listener.orientation = self._forward_orientation + orientation
        self._up_orientation = orientation


class OpenALAudioPlayer(AbstractAudioPlayer):
    min_buffer_size = 512
    _ideal_buffer_size = 1.0

    def __init__(self, driver, source, player):
        super(OpenALAudioPlayer, self).__init__(source, player)
        self.driver = driver
        self.alsource = driver.context.create_source()
        self._buffer_cursor = 0
        self._play_cursor = 0
        self._write_cursor = 0
        self._buffer_sizes = []
        self._buffer_timestamps = []
        self._underrun_timestamp = None
        self._events = []
        self._playing = False
        self._clearing = False
        self._audiodata_buffer = None
        self.refill(self.ideal_buffer_size)

    def __del__(self):
        self.delete()

    def delete(self):
        self.driver.worker.remove(self)
        self.alsource = None

    @property
    def ideal_buffer_size(self):
        return int(self._ideal_buffer_size * self.source.audio_format.bytes_per_second)

    def play(self):
        if not _debug("OpenALAudioPlayer.play()"):
            raise AssertionError
        else:
            if not self.driver is not None:
                raise AssertionError
            elif not self.alsource is not None:
                raise AssertionError
            if not self.alsource.is_playing:
                self.alsource.play()
        self._playing = True
        self._clearing = False
        self.driver.worker.add(self)

    def stop(self):
        self.driver.worker.remove(self)
        if not _debug("OpenALAudioPlayer.stop()"):
            raise AssertionError
        else:
            assert self.driver is not None
            assert self.alsource is not None
        self.alsource.pause()
        self._playing = False

    def clear(self):
        if not _debug("OpenALAudioPlayer.clear()"):
            raise AssertionError
        else:
            assert self.driver is not None
            assert self.alsource is not None
        super().clear()
        self.alsource.stop()
        self._handle_processed_buffers()
        self.alsource.clear()
        self.alsource.byte_offset = 0
        self._playing = False
        self._clearing = True
        self._audiodata_buffer = None
        self._buffer_cursor = 0
        self._play_cursor = 0
        self._write_cursor = 0
        del self._events[:]
        del self._buffer_sizes[:]
        del self._buffer_timestamps[:]

    def _update_play_cursor(self):
        if not self.driver is not None:
            raise AssertionError
        else:
            if not self.alsource is not None:
                raise AssertionError
            else:
                self._handle_processed_buffers()
                if self._clearing:
                    self._play_cursor = self._buffer_cursor
                else:
                    self._play_cursor = self._buffer_cursor + self.alsource.byte_offset
            assert self._check_cursors()
        self._dispatch_events()

    def _handle_processed_buffers(self):
        processed = self.alsource.unqueue_buffers()
        if processed > 0:
            if len(self._buffer_timestamps) == processed:
                if self._buffer_timestamps[-1] is not None:
                    assert _debug("OpenALAudioPlayer: Underrun")
                    self._underrun_timestamp = self._buffer_timestamps[-1] + self._buffer_sizes[-1] / float(self.source.audio_format.bytes_per_second)
            self._update_buffer_cursor(processed)
        return processed

    def _update_buffer_cursor(self, processed):
        self._buffer_cursor += sum(self._buffer_sizes[:processed])
        del self._buffer_sizes[:processed]
        del self._buffer_timestamps[:processed]

    def _dispatch_events(self):
        while self._events and self._events[0][0] <= self._play_cursor:
            _, event = self._events.pop(0)
            event._sync_dispatch_to_player(self.player)

    def get_write_size(self):
        self._update_play_cursor()
        buffer_size = int(self._write_cursor - self._play_cursor)
        write_size = max(self.ideal_buffer_size - buffer_size, 0)
        assert _debug("Write size {} bytes".format(write_size))
        return write_size

    def refill(self, write_size):
        if not _debug("refill", write_size):
            raise AssertionError
        else:
            while write_size > self.min_buffer_size:
                audio_data = self._get_audiodata()
                if audio_data is None:
                    break
                else:
                    length = min(write_size, audio_data.length)
                    if length == 0:
                        assert _debug("Empty AudioData. Discard it.")
                    else:
                        assert _debug("Writing {} bytes".format(length))
                        self._queue_audio_data(audio_data, length)
                    write_size -= length

            if self._playing:
                if not self.alsource.is_playing:
                    assert _debug("underrun")
                    self.alsource.play()

    def _get_audiodata(self):
        if self._audiodata_buffer is None or self._audiodata_buffer.length == 0:
            self._get_new_audiodata()
        return self._audiodata_buffer

    def _get_new_audiodata(self):
        if not _debug("Getting new audio data buffer."):
            raise AssertionError
        else:
            compensation_time = self.get_audio_time_diff()
            self._audiodata_buffer = self.source.get_audio_data(self.ideal_buffer_size, compensation_time)
            if self._audiodata_buffer is not None:
                assert _debug("New audio data available: {} bytes".format(self._audiodata_buffer.length))
                self._queue_events(self._audiodata_buffer)
            else:
                assert _debug("No audio data left")
                if self._has_underrun():
                    assert _debug("Underrun")
                    MediaEvent(0, "on_eos")._sync_dispatch_to_player(self.player)

    def _queue_audio_data(self, audio_data, length):
        buf = self.alsource.get_buffer()
        buf.data(audio_data, self.source.audio_format, length)
        self.alsource.queue_buffer(buf)
        self._update_write_cursor(audio_data, length)

    def _update_write_cursor(self, audio_data, length):
        self._write_cursor += length
        self._buffer_sizes.append(length)
        self._buffer_timestamps.append(audio_data.timestamp)
        audio_data.consume(length, self.source.audio_format)
        assert self._check_cursors()

    def _queue_events(self, audio_data):
        for event in audio_data.events:
            cursor = self._write_cursor + event.timestamp * self.source.audio_format.bytes_per_second
            self._events.append((cursor, event))

    def _has_underrun(self):
        return self.alsource.buffers_queued == 0

    def get_time(self):
        self._update_play_cursor()
        timestamp = self._buffer_timestamps or self._underrun_timestamp
        if not _debug("OpenALAudioPlayer: Return underrun timestamp"):
            raise AssertionError
        else:
            timestamp = self._buffer_timestamps[0]
            assert _debug("OpenALAudioPlayer: Buffer timestamp: {}".format(timestamp))
            if timestamp is not None:
                timestamp += (self._play_cursor - self._buffer_cursor) / float(self.source.audio_format.bytes_per_second)
            assert _debug("OpenALAudioPlayer: get_time = {}".format(timestamp))
        return timestamp

    def _check_cursors(self):
        if not self._play_cursor >= 0:
            raise AssertionError
        else:
            if not self._buffer_cursor >= 0:
                raise AssertionError
            else:
                if not self._write_cursor >= 0:
                    raise AssertionError
                elif not self._buffer_cursor <= self._play_cursor:
                    raise AssertionError
                assert self._play_cursor <= self._write_cursor
            assert _debug("Buffer[{}], Play[{}], Write[{}]".format(self._buffer_cursor, self._play_cursor, self._write_cursor))
        return True

    def set_volume(self, volume):
        self.alsource.gain = volume

    def set_position(self, position):
        self.alsource.position = position

    def set_min_distance(self, min_distance):
        self.alsource.reference_distance = min_distance

    def set_max_distance(self, max_distance):
        self.alsource.max_distance = max_distance

    def set_pitch(self, pitch):
        self.alsource.pitch = pitch

    def set_cone_orientation(self, cone_orientation):
        self.alsource.direction = cone_orientation

    def set_cone_inner_angle(self, cone_inner_angle):
        self.alsource.cone_inner_angle = cone_inner_angle

    def set_cone_outer_angle(self, cone_outer_angle):
        self.alsource.cone_outer_angle = cone_outer_angle

    def set_cone_outer_gain(self, cone_outer_gain):
        self.alsource.cone_outer_gain = cone_outer_gain

    def prefill_audio(self):
        write_size = self.get_write_size()
        self.refill(write_size)
