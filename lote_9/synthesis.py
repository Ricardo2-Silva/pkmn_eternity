# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\media\synthesis.py
import os, math, struct, random, ctypes
from .codecs.base import Source, AudioFormat, AudioData
from collections import deque

class Envelope:
    __doc__ = "Base class for SynthesisSource amplitude envelopes."

    def get_generator(self, sample_rate, duration):
        raise NotImplementedError


class FlatEnvelope(Envelope):
    __doc__ = "A flat envelope, providing basic amplitude setting.\n\n    :Parameters:\n        `amplitude` : float\n            The amplitude (volume) of the wave, from 0.0 to 1.0.\n            Values outside of this range will be clamped.\n    "

    def __init__(self, amplitude=0.5):
        self.amplitude = max(min(1.0, amplitude), 0)

    def get_generator(self, sample_rate, duration):
        amplitude = self.amplitude
        while True:
            yield amplitude


class LinearDecayEnvelope(Envelope):
    __doc__ = "A linearly decaying envelope.\n\n    This envelope linearly decays the amplitude from the peak value\n    to 0, over the length of the waveform.\n\n    :Parameters:\n        `peak` : float\n            The Initial peak value of the envelope, from 0.0 to 1.0.\n            Values outside of this range will be clamped.\n    "

    def __init__(self, peak=1.0):
        self.peak = max(min(1.0, peak), 0)

    def get_generator(self, sample_rate, duration):
        peak = self.peak
        total_bytes = int(sample_rate * duration)
        for i in range(total_bytes):
            yield (total_bytes - i) / total_bytes * peak


class ADSREnvelope(Envelope):
    __doc__ = "A four part Attack, Decay, Suspend, Release envelope.\n\n    This is a four part ADSR envelope. The attack, decay, and release\n    parameters should be provided in seconds. For example, a value of\n    0.1 would be 100ms. The sustain_amplitude parameter affects the\n    sustain volume. This defaults to a value of 0.5, but can be provided\n    on a scale from 0.0 to 1.0.\n\n    :Parameters:\n        `attack` : float\n            The attack time, in seconds.\n        `decay` : float\n            The decay time, in seconds.\n        `release` : float\n            The release time, in seconds.\n        `sustain_amplitude` : float\n            The sustain amplitude (volume), from 0.0 to 1.0.\n    "

    def __init__(self, attack, decay, release, sustain_amplitude=0.5):
        self.attack = attack
        self.decay = decay
        self.release = release
        self.sustain_amplitude = max(min(1.0, sustain_amplitude), 0)

    def get_generator(self, sample_rate, duration):
        sustain_amplitude = self.sustain_amplitude
        total_bytes = int(sample_rate * duration)
        attack_bytes = int(sample_rate * self.attack)
        decay_bytes = int(sample_rate * self.decay)
        release_bytes = int(sample_rate * self.release)
        sustain_bytes = total_bytes - attack_bytes - decay_bytes - release_bytes
        decay_step = (1 - sustain_amplitude) / decay_bytes
        release_step = sustain_amplitude / release_bytes
        for i in range(1, attack_bytes + 1):
            yield i / attack_bytes

        for i in range(1, decay_bytes + 1):
            yield 1 - i * decay_step

        for i in range(1, sustain_bytes + 1):
            yield sustain_amplitude

        for i in range(1, release_bytes + 1):
            yield sustain_amplitude - i * release_step


class TremoloEnvelope(Envelope):
    __doc__ = "A tremolo envelope, for modulation amplitude.\n\n    A tremolo envelope that modulates the amplitude of the\n    waveform with a sinusoidal pattern. The depth and rate\n    of modulation can be specified. Depth is calculated as\n    a percentage of the maximum amplitude. For example:\n    a depth of 0.2 and amplitude of 0.5 will fluctuate\n    the amplitude between 0.4 an 0.5.\n\n    :Parameters:\n        `depth` : float\n            The amount of fluctuation, from 0.0 to 1.0.\n        `rate` : float\n            The fluctuation frequency, in seconds.\n        `amplitude` : float\n            The peak amplitude (volume), from 0.0 to 1.0.\n    "

    def __init__(self, depth, rate, amplitude=0.5):
        self.depth = max(min(1.0, depth), 0)
        self.rate = rate
        self.amplitude = max(min(1.0, amplitude), 0)

    def get_generator(self, sample_rate, duration):
        total_bytes = int(sample_rate * duration)
        period = total_bytes / duration
        max_amplitude = self.amplitude
        min_amplitude = max(0.0, (1.0 - self.depth) * self.amplitude)
        step = math.pi * 2 / period / self.rate
        for i in range(total_bytes):
            value = math.sin(step * i)
            yield value * (max_amplitude - min_amplitude) + min_amplitude


class SynthesisSource(Source):
    __doc__ = "Base class for synthesized waveforms.\n\n    :Parameters:\n        `duration` : float\n            The length, in seconds, of audio that you wish to generate.\n        `sample_rate` : int\n            Audio samples per second. (CD quality is 44100).\n        `sample_size` : int\n            The bit precision. Must be either 8 or 16.\n    "

    def __init__(self, duration, sample_rate=44800, sample_size=16, envelope=None):
        self._duration = float(duration)
        self.audio_format = AudioFormat(channels=1,
          sample_size=sample_size,
          sample_rate=sample_rate)
        self._offset = 0
        self._sample_rate = sample_rate
        self._sample_size = sample_size
        self._bytes_per_sample = sample_size >> 3
        self._bytes_per_second = self._bytes_per_sample * sample_rate
        self._max_offset = int(self._bytes_per_second * self._duration)
        self.envelope = envelope or FlatEnvelope(amplitude=1.0)
        self._envelope_generator = self.envelope.get_generator(sample_rate, duration)
        if self._bytes_per_sample == 2:
            self._max_offset &= 4294967294

    def get_audio_data(self, num_bytes, compensation_time=0.0):
        """Return `num_bytes` bytes of audio data."""
        num_bytes = min(num_bytes, self._max_offset - self._offset)
        if num_bytes <= 0:
            return
        else:
            timestamp = float(self._offset) / self._bytes_per_second
            duration = float(num_bytes) / self._bytes_per_second
            data = self._generate_data(num_bytes)
            self._offset += num_bytes
            return AudioData(data, num_bytes, timestamp, duration, [])

    def _generate_data(self, num_bytes):
        """Generate `num_bytes` bytes of data.

        Return data as ctypes array or string.
        """
        raise NotImplementedError("abstract")

    def seek(self, timestamp):
        self._offset = int(timestamp * self._bytes_per_second)
        self._offset = min(max(self._offset, 0), self._max_offset)
        if self._bytes_per_sample == 2:
            self._offset &= 4294967294
        self._envelope_generator = self.envelope.get_generator(self._sample_rate, self._duration)

    def save(self, filename):
        """Save the audio to disk as a standard RIFF Wave.

        A standard RIFF wave header will be added to the raw PCM
        audio data when it is saved to disk.

        :Parameters:
            `filename` : str
                The file name to save as.

        """
        self.seek(0)
        data = self.get_audio_data(self._max_offset).get_string_data()
        header = struct.pack("<4sI8sIHHIIHH4sI", b'RIFF', len(data) + 44 - 8, b'WAVEfmt ', 16, 1, 1, self._sample_rate, self._bytes_per_second, self._bytes_per_sample, self._sample_size, b'data', len(data))
        with open(filename, "wb") as f:
            f.write(header)
            f.write(data)


class Silence(SynthesisSource):
    __doc__ = "A silent waveform."

    def _generate_data(self, num_bytes):
        if self._bytes_per_sample == 1:
            return b'W' * num_bytes
        else:
            return b'\x00' * num_bytes


class WhiteNoise(SynthesisSource):
    __doc__ = "A white noise, random waveform."

    def _generate_data(self, num_bytes):
        return os.urandom(num_bytes)


class Sine(SynthesisSource):
    __doc__ = "A sinusoid (sine) waveform.\n\n    :Parameters:\n        `duration` : float\n            The length, in seconds, of audio that you wish to generate.\n        `frequency` : int\n            The frequency, in Hz of the waveform you wish to produce.\n        `sample_rate` : int\n            Audio samples per second. (CD quality is 44100).\n        `sample_size` : int\n            The bit precision. Must be either 8 or 16.\n    "

    def __init__(self, duration, frequency=440, **kwargs):
        (super(Sine, self).__init__)(duration, **kwargs)
        self.frequency = frequency

    def _generate_data(self, num_bytes):
        if self._bytes_per_sample == 1:
            samples = num_bytes
            bias = 127
            amplitude = 127
            data = ctypes.c_ubyte * samples()
        else:
            samples = num_bytes >> 1
            bias = 0
            amplitude = 32767
            data = ctypes.c_short * samples()
        step = self.frequency * (math.pi * 2) / self.audio_format.sample_rate
        envelope = self._envelope_generator
        for i in range(samples):
            data[i] = int(math.sin(step * i) * amplitude * next(envelope) + bias)

        return bytes(data)


class Triangle(SynthesisSource):
    __doc__ = "A triangle waveform.\n\n    :Parameters:\n        `duration` : float\n            The length, in seconds, of audio that you wish to generate.\n        `frequency` : int\n            The frequency, in Hz of the waveform you wish to produce.\n        `sample_rate` : int\n            Audio samples per second. (CD quality is 44100).\n        `sample_size` : int\n            The bit precision. Must be either 8 or 16.\n    "

    def __init__(self, duration, frequency=440, **kwargs):
        (super(Triangle, self).__init__)(duration, **kwargs)
        self.frequency = frequency

    def _generate_data(self, num_bytes):
        if self._bytes_per_sample == 1:
            samples = num_bytes
            value = 127
            maximum = 255
            minimum = 0
            data = ctypes.c_ubyte * samples()
        else:
            samples = num_bytes >> 1
            value = 0
            maximum = 32767
            minimum = -32768
            data = ctypes.c_short * samples()
        step = (maximum - minimum) * 2 * self.frequency / self.audio_format.sample_rate
        envelope = self._envelope_generator
        for i in range(samples):
            value += step
            if value > maximum:
                value = maximum - (value - maximum)
                step = -step
            if value < minimum:
                value = minimum - (value - minimum)
                step = -step
            data[i] = int(value * next(envelope))

        return bytes(data)


class Sawtooth(SynthesisSource):
    __doc__ = "A sawtooth waveform.\n\n    :Parameters:\n        `duration` : float\n            The length, in seconds, of audio that you wish to generate.\n        `frequency` : int\n            The frequency, in Hz of the waveform you wish to produce.\n        `sample_rate` : int\n            Audio samples per second. (CD quality is 44100).\n        `sample_size` : int\n            The bit precision. Must be either 8 or 16.\n    "

    def __init__(self, duration, frequency=440, **kwargs):
        (super(Sawtooth, self).__init__)(duration, **kwargs)
        self.frequency = frequency

    def _generate_data(self, num_bytes):
        if self._bytes_per_sample == 1:
            samples = num_bytes
            value = 127
            maximum = 255
            minimum = 0
            data = ctypes.c_ubyte * samples()
        else:
            samples = num_bytes >> 1
            value = 0
            maximum = 32767
            minimum = -32768
            data = ctypes.c_short * samples()
        step = (maximum - minimum) * self.frequency / self._sample_rate
        envelope = self._envelope_generator
        for i in range(samples):
            value += step
            if value > maximum:
                value = minimum + value % maximum
            data[i] = int(value * next(envelope))

        return bytes(data)


class Square(SynthesisSource):
    __doc__ = "A square (pulse) waveform.\n\n    :Parameters:\n        `duration` : float\n            The length, in seconds, of audio that you wish to generate.\n        `frequency` : int\n            The frequency, in Hz of the waveform you wish to produce.\n        `sample_rate` : int\n            Audio samples per second. (CD quality is 44100).\n        `sample_size` : int\n            The bit precision. Must be either 8 or 16.\n    "

    def __init__(self, duration, frequency=440, **kwargs):
        (super(Square, self).__init__)(duration, **kwargs)
        self.frequency = frequency

    def _generate_data(self, num_bytes):
        if self._bytes_per_sample == 1:
            samples = num_bytes
            bias = 127
            amplitude = 127
            data = ctypes.c_ubyte * samples()
        else:
            samples = num_bytes >> 1
            bias = 0
            amplitude = 32767
            data = ctypes.c_short * samples()
        half_period = self.audio_format.sample_rate / self.frequency / 2
        envelope = self._envelope_generator
        value = 1
        count = 0
        for i in range(samples):
            if count >= half_period:
                value = -value
                count %= half_period
            count += 1
            data[i] = int(value * amplitude * next(envelope) + bias)

        return bytes(data)


class FM(SynthesisSource):
    __doc__ = "A simple FM waveform.\n\n    This is a simplistic frequency modulated waveform, based on the\n    concepts by John Chowning. Basic sine waves are used for both\n    frequency carrier and modulator inputs, of which the frequencies can\n    be provided. The modulation index, or amplitude, can also be adjusted.\n\n    :Parameters:\n        `duration` : float\n            The length, in seconds, of audio that you wish to generate.\n        `carrier` : int\n            The carrier frequency, in Hz.\n        `modulator` : int\n            The modulator frequency, in Hz.\n        `mod_index` : int\n            The modulation index.\n        `sample_rate` : int\n            Audio samples per second. (CD quality is 44100).\n        `sample_size` : int\n            The bit precision. Must be either 8 or 16.\n    "

    def __init__(self, duration, carrier=440, modulator=440, mod_index=1, **kwargs):
        (super(FM, self).__init__)(duration, **kwargs)
        self.carrier = carrier
        self.modulator = modulator
        self.mod_index = mod_index

    def _generate_data(self, num_bytes):
        if self._bytes_per_sample == 1:
            samples = num_bytes
            bias = 127
            amplitude = 127
            data = ctypes.c_ubyte * samples()
        else:
            samples = num_bytes >> 1
            bias = 0
            amplitude = 32767
            data = ctypes.c_short * samples()
        car_step = 2 * math.pi * self.carrier
        mod_step = 2 * math.pi * self.modulator
        mod_index = self.mod_index
        sample_rate = self._sample_rate
        envelope = self._envelope_generator
        sin = math.sin
        for i in range(samples):
            increment = i / sample_rate
            data[i] = int(sin(car_step * increment + mod_index * sin(mod_step * increment)) * amplitude * next(envelope) + bias)

        return bytes(data)


class Digitar(SynthesisSource):
    __doc__ = "A guitar-like waveform.\n\n    A guitar-like waveform, based on the Karplus-Strong algorithm.\n    The sound is similar to a plucked guitar string. The resulting\n    sound decays over time, and so the actual length will vary\n    depending on the frequency. Lower frequencies require a longer\n    `length` parameter to prevent cutting off abruptly.\n\n    :Parameters:\n        `duration` : float\n            The length, in seconds, of audio that you wish to generate.\n        `frequency` : int\n            The frequency, in Hz of the waveform you wish to produce.\n        `decay` : float\n            The decay rate of the effect. Defaults to 0.996.\n        `sample_rate` : int\n            Audio samples per second. (CD quality is 44100).\n        `sample_size` : int\n            The bit precision. Must be either 8 or 16.\n    "

    def __init__(self, duration, frequency=440, decay=0.996, **kwargs):
        (super(Digitar, self).__init__)(duration, **kwargs)
        self.frequency = frequency
        self.decay = decay
        self.period = int(self._sample_rate / self.frequency)

    def _generate_data(self, num_bytes):
        if self._bytes_per_sample == 1:
            samples = num_bytes
            bias = 127
            amplitude = 127
            data = ctypes.c_ubyte * samples()
        else:
            samples = num_bytes >> 1
            bias = 0
            amplitude = 32767
            data = ctypes.c_short * samples()
        random.seed(10)
        period = self.period
        ring_buffer = deque([random.uniform(-1, 1) for _ in range(period)], maxlen=period)
        decay = self.decay
        for i in range(samples):
            data[i] = int(ring_buffer[0] * amplitude + bias)
            ring_buffer.append(decay * (ring_buffer[0] + ring_buffer[1]) / 2)

        return bytes(data)
