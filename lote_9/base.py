# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\media\codecs\base.py
import io, pyglet
from pyglet.media.exceptions import MediaException, CannotSeekException, MediaEncodeException

class AudioFormat:
    __doc__ = "Audio details.\n\n    An instance of this class is provided by sources with audio tracks.  You\n    should not modify the fields, as they are used internally to describe the\n    format of data provided by the source.\n\n    Args:\n        channels (int): The number of channels: 1 for mono or 2 for stereo\n            (pyglet does not yet support surround-sound sources).\n        sample_size (int): Bits per sample; only 8 or 16 are supported.\n        sample_rate (int): Samples per second (in Hertz).\n    "

    def __init__(self, channels, sample_size, sample_rate):
        self.channels = channels
        self.sample_size = sample_size
        self.sample_rate = sample_rate
        self.bytes_per_sample = (sample_size >> 3) * channels
        self.bytes_per_second = self.bytes_per_sample * sample_rate

    def __eq__(self, other):
        if other is None:
            return False
        else:
            return self.channels == other.channels and self.sample_size == other.sample_size and self.sample_rate == other.sample_rate

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "%s(channels=%d, sample_size=%d, sample_rate=%d)" % (
         self.__class__.__name__, self.channels, self.sample_size,
         self.sample_rate)


class VideoFormat:
    __doc__ = "Video details.\n\n    An instance of this class is provided by sources with a video stream. You\n    should not modify the fields.\n\n    Note that the sample aspect has no relation to the aspect ratio of the\n    video image.  For example, a video image of 640x480 with sample aspect 2.0\n    should be displayed at 1280x480.  It is the responsibility of the\n    application to perform this scaling.\n\n    Args:\n        width (int): Width of video image, in pixels.\n        height (int): Height of video image, in pixels.\n        sample_aspect (float): Aspect ratio (width over height) of a single\n            video pixel.\n        frame_rate (float): Frame rate (frames per second) of the video.\n\n            .. versionadded:: 1.2\n    "

    def __init__(self, width, height, sample_aspect=1.0):
        self.width = width
        self.height = height
        self.sample_aspect = sample_aspect
        self.frame_rate = None

    def __eq__(self, other):
        if isinstance(other, VideoFormat):
            return self.width == other.width and self.height == other.height and self.sample_aspect == other.sample_aspect and self.frame_rate == other.frame_rate
        else:
            return False


class AudioData:
    __doc__ = "A single packet of audio data.\n\n    This class is used internally by pyglet.\n\n    Args:\n        data (str or ctypes array or pointer): Sample data.\n        length (int): Size of sample data, in bytes.\n        timestamp (float): Time of the first sample, in seconds.\n        duration (float): Total data duration, in seconds.\n        events (List[:class:`pyglet.media.events.MediaEvent`]): List of events\n            contained within this packet. Events are timestamped relative to\n            this audio packet.\n    "
    __slots__ = ('data', 'length', 'timestamp', 'duration', 'events')

    def __init__(self, data, length, timestamp, duration, events):
        self.data = data
        self.length = length
        self.timestamp = timestamp
        self.duration = duration
        self.events = events

    def __eq__(self, other):
        if isinstance(other, AudioData):
            return self.data == other.data and self.length == other.length and self.timestamp == other.timestamp and self.duration == other.duration and self.events == other.events
        else:
            return False

    def consume(self, num_bytes, audio_format):
        """Remove some data from the beginning of the packet.

        All events are cleared.

        Args:
            num_bytes (int): The number of bytes to consume from the packet.
            audio_format (:class:`.AudioFormat`): The packet audio format.
        """
        self.events = ()
        if num_bytes >= self.length:
            self.data = None
            self.length = 0
            self.timestamp += self.duration
            self.duration = 0.0
            return
        if num_bytes == 0:
            return
        self.data = self.data[num_bytes:]
        self.length -= num_bytes
        self.duration -= num_bytes / audio_format.bytes_per_second
        self.timestamp += num_bytes / audio_format.bytes_per_second

    def get_string_data(self):
        """Return data as a bytestring.

        Returns:
            bytes: Data as a (byte)string.
        """
        if self.data is None:
            return b''
        else:
            return memoryview(self.data).tobytes()[:self.length]


class SourceInfo:
    __doc__ = "Source metadata information.\n\n    Fields are the empty string or zero if the information is not available.\n\n    Args:\n        title (str): Title\n        author (str): Author\n        copyright (str): Copyright statement\n        comment (str): Comment\n        album (str): Album name\n        year (int): Year\n        track (int): Track number\n        genre (str): Genre\n\n    .. versionadded:: 1.2\n    "
    title = ""
    author = ""
    copyright = ""
    comment = ""
    album = ""
    year = 0
    track = 0
    genre = ""


class Source:
    __doc__ = "An audio and/or video source.\n\n    Args:\n        audio_format (:class:`.AudioFormat`): Format of the audio in this\n            source, or ``None`` if the source is silent.\n        video_format (:class:`.VideoFormat`): Format of the video in this\n            source, or ``None`` if there is no video.\n        info (:class:`.SourceInfo`): Source metadata such as title, artist,\n            etc; or ``None`` if the` information is not available.\n\n            .. versionadded:: 1.2\n\n    Attributes:\n        is_player_source (bool): Determine if this source is a player\n            current source.\n\n            Check on a :py:class:`~pyglet.media.player.Player` if this source\n            is the current source.\n    "
    _duration = None
    _players = []
    audio_format = None
    video_format = None
    info = None
    is_player_source = False

    @property
    def duration(self):
        """float: The length of the source, in seconds.

        Not all source durations can be determined; in this case the value
        is ``None``.

        Read-only.
        """
        return self._duration

    def play(self):
        """Play the source.

        This is a convenience method which creates a Player for
        this source and plays it immediately.

        Returns:
            :class:`.Player`
        """
        from pyglet.media.player import Player
        player = Player()
        player.queue(self)
        player.play()
        Source._players.append(player)

        def _on_player_eos():
            Source._players.remove(player)
            player.on_player_eos = None

        player.on_player_eos = _on_player_eos
        return player

    def get_animation(self):
        """
        Import all video frames into memory.

        An empty animation will be returned if the source has no video.
        Otherwise, the animation will contain all unplayed video frames (the
        entire source, if it has not been queued on a player). After creating
        the animation, the source will be at EOS (end of stream).

        This method is unsuitable for videos running longer than a
        few seconds.

        .. versionadded:: 1.1

        Returns:
            :class:`pyglet.image.Animation`
        """
        from pyglet.image import Animation, AnimationFrame
        if not self.video_format:
            return Animation([])
        else:
            frames = []
            last_ts = 0
            next_ts = self.get_next_video_timestamp()
            while next_ts is not None:
                image = self.get_next_video_frame()
                if image is not None:
                    delay = next_ts - last_ts
                    frames.append(AnimationFrame(image, delay))
                    last_ts = next_ts
                next_ts = self.get_next_video_timestamp()

            return Animation(frames)

    def get_next_video_timestamp(self):
        """Get the timestamp of the next video frame.

        .. versionadded:: 1.1

        Returns:
            float: The next timestamp, or ``None`` if there are no more video
            frames.
        """
        return

    def get_next_video_frame(self):
        """Get the next video frame.

        .. versionadded:: 1.1

        Returns:
            :class:`pyglet.image.AbstractImage`: The next video frame image,
            or ``None`` if the video frame could not be decoded or there are
            no more video frames.
        """
        return

    def save(self, filename, file=None, encoder=None):
        """Save this Source to a file.

        :Parameters:
            `filename` : str
                Used to set the file format, and to open the output file
                if `file` is unspecified.
            `file` : file-like object or None
                File to write audio data to.
            `encoder` : MediaEncoder or None
                If unspecified, all encoders matching the filename extension
                are tried.  If all fail, the exception from the first one
                attempted is raised.

        """
        if not file:
            file = open(filename, "wb")
        if encoder:
            encoder.encode(self, file, filename)
        else:
            first_exception = None
            for encoder in pyglet.media.get_encoders(filename):
                try:
                    encoder.encode(self, file, filename)
                    return
                except MediaEncodeException as e:
                    first_exception = first_exception or e
                    file.seek(0)

            if not first_exception:
                raise MediaEncodeException(f"No Encoders are available for this extension: '{filename}'")
            raise first_exception
        file.close()

    def seek(self, timestamp):
        """Seek to given timestamp.

        Args:
            timestamp (float): Time where to seek in the source. The
                ``timestamp`` will be clamped to the duration of the source.
        """
        raise CannotSeekException()

    def get_queue_source(self):
        """Return the ``Source`` to be used as the queue source for a player.

        Default implementation returns self.
        """
        return self

    def get_audio_data(self, num_bytes, compensation_time=0.0):
        """Get next packet of audio data.

        Args:
            num_bytes (int): Maximum number of bytes of data to return.
            compensation_time (float): Time in sec to compensate due to a
                difference between the master clock and the audio clock.

        Returns:
            :class:`.AudioData`: Next packet of audio data, or ``None`` if
            there is no (more) data.
        """
        return


class StreamingSource(Source):
    __doc__ = "A source that is decoded as it is being played.\n\n    The source can only be played once at a time on any\n    :class:`~pyglet.media.player.Player`.\n    "

    def get_queue_source(self):
        """Return the ``Source`` to be used as the source for a player.

        Default implementation returns self.

        Returns:
            :class:`.Source`
        """
        if self.is_player_source:
            raise MediaException("This source is already queued on a player.")
        self.is_player_source = True
        return self

    def delete(self):
        """Release the resources held by this StreamingSource."""
        return


class StaticSource(Source):
    __doc__ = "A source that has been completely decoded in memory.\n\n    This source can be queued onto multiple players any number of times.\n\n    Construct a :py:class:`~pyglet.media.StaticSource` for the data in\n    ``source``.\n\n    Args:\n        source (Source):  The source to read and decode audio and video data\n            from.\n    "

    def __init__(self, source):
        source = source.get_queue_source()
        if source.video_format:
            raise NotImplementedError("Static sources not supported for video.")
        self.audio_format = source.audio_format
        if not self.audio_format:
            self._data = None
            self._duration = 0.0
            return
        buffer_size = 1048576
        data = io.BytesIO()
        while True:
            audio_data = source.get_audio_data(buffer_size)
            if not audio_data:
                break
            data.write(audio_data.get_string_data())

        self._data = data.getvalue()
        self._duration = len(self._data) / self.audio_format.bytes_per_second

    def get_queue_source(self):
        if self._data is not None:
            return StaticMemorySource(self._data, self.audio_format)

    def get_audio_data(self, num_bytes, compensation_time=0.0):
        """The StaticSource does not provide audio data.

        When the StaticSource is queued on a
        :class:`~pyglet.media.player.Player`, it creates a
        :class:`.StaticMemorySource` containing its internal audio data and
        audio format.

        Raises:
            RuntimeError
        """
        raise RuntimeError("StaticSource cannot be queued.")


class StaticMemorySource(StaticSource):
    __doc__ = "\n    Helper class for default implementation of :class:`.StaticSource`.\n\n    Do not use directly. This class is used internally by pyglet.\n\n    Args:\n        data (AudioData): The audio data.\n        audio_format (AudioFormat): The audio format.\n    "

    def __init__(self, data, audio_format):
        """Construct a memory source over the given data buffer."""
        self._file = io.BytesIO(data)
        self._max_offset = len(data)
        self.audio_format = audio_format
        self._duration = len(data) / float(audio_format.bytes_per_second)

    def seek(self, timestamp):
        """Seek to given timestamp.

        Args:
            timestamp (float): Time where to seek in the source.
        """
        offset = int(timestamp * self.audio_format.bytes_per_second)
        if self.audio_format.bytes_per_sample == 2:
            offset &= 4294967294
        else:
            if self.audio_format.bytes_per_sample == 4:
                offset &= 4294967292
        self._file.seek(offset)

    def get_audio_data(self, num_bytes, compensation_time=0.0):
        """Get next packet of audio data.

        Args:
            num_bytes (int): Maximum number of bytes of data to return.
            compensation_time (float): Not used in this class.

        Returns:
            :class:`.AudioData`: Next packet of audio data, or ``None`` if
            there is no (more) data.
        """
        offset = self._file.tell()
        timestamp = float(offset) / self.audio_format.bytes_per_second
        if self.audio_format.bytes_per_sample == 2:
            num_bytes &= 4294967294
        else:
            if self.audio_format.bytes_per_sample == 4:
                num_bytes &= 4294967292
        data = self._file.read(num_bytes)
        if not len(data):
            return
        else:
            duration = float(len(data)) / self.audio_format.bytes_per_second
            return AudioData(data, len(data), timestamp, duration, [])


class SourceGroup:
    __doc__ = "Group of like sources to allow gapless playback.\n\n    Seamlessly read data from a group of sources to allow for\n    gapless playback. All sources must share the same audio format.\n    The first source added sets the format.\n    "

    def __init__(self):
        self.audio_format = None
        self.video_format = None
        self.duration = 0.0
        self._timestamp_offset = 0.0
        self._dequeued_durations = []
        self._sources = []

    def seek(self, time):
        if self._sources:
            self._sources[0].seek(time)

    def add(self, source):
        self.audio_format = self.audio_format or source.audio_format
        source = source.get_queue_source()
        assert source.audio_format == self.audio_format, "Sources must share the same audio format."
        self._sources.append(source)
        self.duration += source.duration

    def has_next(self):
        return len(self._sources) > 1

    def get_queue_source(self):
        return self

    def _advance(self):
        if self._sources:
            self._timestamp_offset += self._sources[0].duration
            self._dequeued_durations.insert(0, self._sources[0].duration)
            old_source = self._sources.pop(0)
            self.duration -= old_source.duration
            if isinstance(old_source, StreamingSource):
                old_source.delete()
                del old_source

    def get_audio_data(self, num_bytes, compensation_time=0.0):
        """Get next audio packet.

        :Parameters:
            `num_bytes` : int
                Hint for preferred size of audio packet; may be ignored.

        :rtype: `AudioData`
        :return: Audio data, or None if there is no more data.
        """
        if not self._sources:
            return
        else:
            buffer = b''
            duration = 0.0
            timestamp = 0.0
            while len(buffer) < num_bytes:
                if self._sources:
                    audiodata = self._sources[0].get_audio_data(num_bytes)
                    if audiodata:
                        buffer += audiodata.data
                        duration += audiodata.duration
                        timestamp += self._timestamp_offset
                else:
                    self._advance()

            return AudioData(buffer, len(buffer), timestamp, duration, [])
