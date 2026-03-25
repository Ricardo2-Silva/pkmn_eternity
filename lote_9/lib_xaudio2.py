# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\media\drivers\xaudio2\lib_xaudio2.py
from pyglet.media.events import MediaEvent
import pyglet, ctypes
from pyglet.libs.win32.constants import *
from pyglet.libs.win32.types import *
from pyglet import com
import platform, os
from pyglet.util import debug_print
_debug = debug_print("debug_media")

def load_xaudio2(dll_name):
    """This will attempt to load a version of XAudio2. Versions supported: 2.9, 2.8.
       While Windows 8 ships with 2.8 and Windows 10 ships with version 2.9, it is possible to install 2.9 on 8/8.1.
    """
    xaudio2 = dll_name
    if platform.architecture()[0] == "32bit":
        if platform.machine().endswith("64"):
            xaudio2 = os.path.join(os.environ["WINDIR"], "SysWOW64", "{}.dll".format(xaudio2))
    xaudio2_lib = ctypes.windll.LoadLibrary(xaudio2)
    x3d_lib = ctypes.cdll.LoadLibrary(xaudio2)
    return (xaudio2_lib, x3d_lib)


try:
    xaudio2_lib, x3d_lib = load_xaudio2("xaudio2_9")
except OSError:
    _debug("Could not load XAudio2.9 library")
    try:
        xaudio2_lib, x3d_lib = load_xaudio2("xaudio2_8")
    except OSError:
        _debug("Could not load XAudio2.8 library")
        raise ImportError("Could not locate a supported XAudio2 library.")

UINT32 = c_uint32
FLOAT32 = c_float

class XAUDIO2_DEBUG_CONFIGURATION(ctypes.Structure):
    _fields_ = [
     (
      "TraceMask", UINT32),
     (
      "BreakMask", UINT32),
     (
      "LogThreadID", BOOL),
     (
      "LogFileline", BOOL),
     (
      "LogFunctionName", BOOL),
     (
      "LogTiming", BOOL)]


class XAUDIO2_PERFORMANCE_DATA(ctypes.Structure):
    _fields_ = [
     (
      "AudioCyclesSinceLastQuery", c_uint64),
     (
      "TotalCyclesSinceLastQuery", c_uint64),
     (
      "MinimumCyclesPerQuantum", UINT32),
     (
      "MaximumCyclesPerQuantum", UINT32),
     (
      "MemoryUsageInBytes", UINT32),
     (
      "CurrentLatencyInSamples", UINT32),
     (
      "GlitchesSinceEngineStarted", UINT32),
     (
      "ActiveSourceVoiceCount", UINT32),
     (
      "TotalSourceVoiceCount", UINT32),
     (
      "ActiveSubmixVoiceCount", UINT32),
     (
      "ActiveResamplerCount", UINT32),
     (
      "ActiveMatrixMixCount", UINT32),
     (
      "ActiveXmaSourceVoices", UINT32),
     (
      "ActiveXmaStreams", UINT32)]

    def __repr__(self):
        return "XAUDIO2PerformanceData(active_voices={}, total_voices={}, glitches={}, latency={} samples, memory_usage={} bytes)".format(self.ActiveSourceVoiceCount, self.TotalSourceVoiceCount, self.GlitchesSinceEngineStarted, self.CurrentLatencyInSamples, self.MemoryUsageInBytes)


class XAUDIO2_VOICE_SENDS(ctypes.Structure):
    _fields_ = [
     (
      "SendCount", UINT32),
     (
      "pSends", c_void_p)]


class XAUDIO2_BUFFER(ctypes.Structure):
    _fields_ = [
     (
      "Flags", UINT32),
     (
      "AudioBytes", UINT32),
     (
      "pAudioData", POINTER(c_char)),
     (
      "PlayBegin", UINT32),
     (
      "PlayLength", UINT32),
     (
      "LoopBegin", UINT32),
     (
      "LoopLength", UINT32),
     (
      "LoopCount", UINT32),
     (
      "pContext", c_void_p)]


class XAUDIO2_VOICE_STATE(ctypes.Structure):
    _fields_ = [
     (
      "pCurrentBufferContext", c_void_p),
     (
      "BuffersQueued", UINT32),
     (
      "SamplesPlayed", UINT32)]

    def __repr__(self):
        return "XAUDIO2_VOICE_STATE(BuffersQueued={0}, SamplesPlayed={1})".format(self.BuffersQueued, self.SamplesPlayed)


class WAVEFORMATEX(ctypes.Structure):
    _fields_ = [
     (
      "wFormatTag", WORD),
     (
      "nChannels", WORD),
     (
      "nSamplesPerSec", DWORD),
     (
      "nAvgBytesPerSec", DWORD),
     (
      "nBlockAlign", WORD),
     (
      "wBitsPerSample", WORD),
     (
      "cbSize", WORD)]

    def __repr__(self):
        return "WAVEFORMATEX(wFormatTag={}, nChannels={}, nSamplesPerSec={}, nAvgBytesPersec={}, nBlockAlign={}, wBitsPerSample={}, cbSize={})".format(self.wFormatTag, self.nChannels, self.nSamplesPerSec, self.nAvgBytesPerSec, self.nBlockAlign, self.wBitsPerSample, self.cbSize)


XAUDIO2_USE_DEFAULT_PROCESSOR = 0
if WINDOWS_10_ANNIVERSARY_UPDATE_OR_GREATER:
    XAUDIO2_DEFAULT_PROCESSOR = XAUDIO2_USE_DEFAULT_PROCESSOR
else:
    XAUDIO2_DEFAULT_PROCESSOR = 1
XAUDIO2_LOG_ERRORS = 1
XAUDIO2_LOG_WARNINGS = 2
XAUDIO2_LOG_INFO = 4
XAUDIO2_LOG_DETAIL = 8
XAUDIO2_LOG_API_CALLS = 16
XAUDIO2_LOG_FUNC_CALLS = 32
XAUDIO2_LOG_TIMING = 64
XAUDIO2_LOG_LOCKS = 128
XAUDIO2_LOG_MEMORY = 256
XAUDIO2_LOG_STREAMING = 4096
XAUDIO2_MAX_BUFFER_BYTES = 2147483648
XAUDIO2_MAX_QUEUED_BUFFERS = 64
XAUDIO2_MAX_BUFFERS_SYSTEM = 2
XAUDIO2_MAX_AUDIO_CHANNELS = 64
XAUDIO2_MIN_SAMPLE_RATE = 1000
XAUDIO2_MAX_SAMPLE_RATE = 200000
XAUDIO2_MAX_VOLUME_LEVEL = 16777216.0
XAUDIO2_MIN_FREQ_RATIO = 0.0009765625
XAUDIO2_MAX_FREQ_RATIO = 1024.0
XAUDIO2_DEFAULT_FREQ_RATIO = 2.0
XAUDIO2_MAX_FILTER_ONEOVERQ = 1.5
XAUDIO2_MAX_FILTER_FREQUENCY = 1.0
XAUDIO2_MAX_LOOP_COUNT = 254
XAUDIO2_MAX_INSTANCES = 8
XAUDIO2_FILTER_TYPE = UINT
LowPassFilter = 0
BandPassFilter = 1
HighPassFilter = 2
NotchFilter = 3
LowPassOnePoleFilter = 4
HighPassOnePoleFilter = 5
XAUDIO2_NO_LOOP_REGION = 0
XAUDIO2_LOOP_INFINITE = 255
XAUDIO2_DEFAULT_CHANNELS = 0
XAUDIO2_DEFAULT_SAMPLERATE = 0
WAVE_FORMAT_PCM = 1
XAUDIO2_DEBUG_ENGINE = 1
XAUDIO2_VOICE_NOPITCH = 2
XAUDIO2_VOICE_NOSRC = 4
XAUDIO2_VOICE_USEFILTER = 8
XAUDIO2_PLAY_TAILS = 32
XAUDIO2_END_OF_STREAM = 64
XAUDIO2_SEND_USEFILTER = 128
XAUDIO2_VOICE_NOSAMPLESPLAYED = 256
XAUDIO2_STOP_ENGINE_WHEN_IDLE = 8192
XAUDIO2_1024_QUANTUM = 32768
XAUDIO2_NO_VIRTUAL_AUDIO_CLIENT = 65536

class IXAudio2VoiceCallback(com.Interface):
    _methods_ = [
     (
      "OnVoiceProcessingPassStart",
      com.STDMETHOD(UINT32)),
     (
      "OnVoiceProcessingPassEnd",
      com.STDMETHOD()),
     (
      "onStreamEnd",
      com.STDMETHOD()),
     (
      "onBufferStart",
      com.STDMETHOD(ctypes.c_void_p)),
     (
      "OnBufferEnd",
      com.STDMETHOD(ctypes.c_void_p)),
     (
      "OnLoopEnd",
      com.STDMETHOD(ctypes.c_void_p))]


class XA2SourceCallback(com.COMObject):
    __doc__ = "Callback class used to trigger when buffers or streams end..\n           WARNING: Whenever a callback is running, XAudio2 cannot generate audio.\n           Make sure these functions run as fast as possible and do not block/delay more than a few milliseconds.\n           MS Recommendation:\n           At a minimum, callback functions must not do the following:\n                - Access the hard disk or other permanent storage\n                - Make expensive or blocking API calls\n                - Synchronize with other parts of client code\n                - Require significant CPU usage\n    "
    _interfaces_ = [IXAudio2VoiceCallback]

    def __init__(self, xa2_player):
        self.xa2_player = xa2_player

    def OnVoiceProcessingPassStart(self, bytesRequired):
        return

    def OnVoiceProcessingPassEnd(self):
        return

    def onStreamEnd(self):
        return

    def onBufferStart(self, pBufferContext):
        return

    def OnBufferEnd(self, pBufferContext):
        """At the end of playing one buffer, attempt to refill again.
        Even if the player is out of sources, it needs to be called to purge all buffers.
        """
        if self.xa2_player:
            self.xa2_player.refill_source_player()

    def OnLoopEnd(self, this, pBufferContext):
        return

    def onVoiceError(self, this, pBufferContext, hresult):
        raise Exception("Error occurred during audio playback.", hresult)


class XAUDIO2_EFFECT_DESCRIPTOR(Structure):
    _fields_ = [
     (
      "pEffect", com.pIUnknown),
     (
      "InitialState", c_bool),
     (
      "OutputChannels", UINT32)]


class XAUDIO2_EFFECT_CHAIN(ctypes.Structure):
    _fields_ = [
     (
      "EffectCount", UINT32),
     (
      "pEffectDescriptors", POINTER(XAUDIO2_EFFECT_DESCRIPTOR))]


class XAUDIO2_FILTER_PARAMETERS(Structure):
    _fields_ = [
     (
      "Type", XAUDIO2_FILTER_TYPE),
     (
      "Frequency", FLOAT),
     (
      "OneOverQ", FLOAT)]


class XAUDIO2_VOICE_DETAILS(Structure):
    _fields_ = [
     (
      "CreationFlags", UINT32),
     (
      "ActiveFlags", UINT32),
     (
      "InputChannels", UINT32),
     (
      "InputSampleRate", UINT32)]


class IXAudio2Voice(com.pInterface):
    _methods_ = [
     (
      "GetVoiceDetails",
      com.STDMETHOD(POINTER(XAUDIO2_VOICE_DETAILS))),
     (
      "SetOutputVoices",
      com.STDMETHOD()),
     (
      "SetEffectChain",
      com.STDMETHOD(POINTER(XAUDIO2_EFFECT_CHAIN))),
     (
      "EnableEffect",
      com.STDMETHOD()),
     (
      "DisableEffect",
      com.STDMETHOD()),
     (
      "GetEffectState",
      com.STDMETHOD()),
     (
      "SetEffectParameters",
      com.STDMETHOD()),
     (
      "GetEffectParameters",
      com.STDMETHOD()),
     (
      "SetFilterParameters",
      com.STDMETHOD(POINTER(XAUDIO2_FILTER_PARAMETERS), UINT32)),
     (
      "GetFilterParameters",
      com.STDMETHOD()),
     (
      "SetOutputFilterParameters",
      com.STDMETHOD()),
     (
      "GetOutputFilterParameters",
      com.STDMETHOD()),
     (
      "SetVolume",
      com.STDMETHOD(ctypes.c_float, UINT32)),
     (
      "GetVolume",
      com.STDMETHOD(POINTER(c_float))),
     (
      "SetChannelVolumes",
      com.STDMETHOD()),
     (
      "GetChannelVolumes",
      com.STDMETHOD()),
     (
      "SetOutputMatrix",
      com.STDMETHOD(c_void_p, UINT32, UINT32, POINTER(FLOAT), UINT32)),
     (
      "GetOutputMatrix",
      com.STDMETHOD()),
     (
      "DestroyVoice",
      com.STDMETHOD())]


class IXAudio2SubmixVoice(IXAudio2Voice):
    return


class IXAudio2SourceVoice(IXAudio2Voice):
    _methods_ = [
     (
      "Start",
      com.STDMETHOD(UINT32, UINT32)),
     (
      "Stop",
      com.STDMETHOD(UINT32, UINT32)),
     (
      "SubmitSourceBuffer",
      com.STDMETHOD(POINTER(XAUDIO2_BUFFER), c_void_p)),
     (
      "FlushSourceBuffers",
      com.STDMETHOD()),
     (
      "Discontinuity",
      com.STDMETHOD()),
     (
      "ExitLoop",
      com.STDMETHOD()),
     (
      "GetState",
      com.STDMETHOD(POINTER(XAUDIO2_VOICE_STATE), UINT32)),
     (
      "SetFrequencyRatio",
      com.STDMETHOD(FLOAT, UINT32)),
     (
      "GetFrequencyRatio",
      com.STDMETHOD(POINTER(c_float))),
     (
      "SetSourceSampleRate",
      com.STDMETHOD())]


class IXAudio2MasteringVoice(IXAudio2Voice):
    _methods_ = [
     (
      "GetChannelMask",
      com.STDMETHOD(POINTER(DWORD)))]


class IXAudio2EngineCallback(com.Interface):
    _methods_ = [
     (
      "OnProcessingPassStart",
      com.METHOD(ctypes.c_void_p)),
     (
      "OnProcessingPassEnd",
      com.METHOD(ctypes.c_void_p)),
     (
      "OnCriticalError",
      com.METHOD(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong))]


class XA2EngineCallback(com.COMObject):
    _interfaces_ = [
     IXAudio2EngineCallback]

    def OnProcessingPassStart(self):
        return

    def OnProcessingPassEnd(self):
        return

    def OnCriticalError(self, this, hresult):
        raise Exception("Critical Error:", hresult)


class X3DAUDIO_DISTANCE_CURVE_POINT(ctypes.Structure):
    _fields_ = [
     (
      "Distance", FLOAT32),
     (
      "DSPSetting", FLOAT32)]


class X3DAUDIO_DISTANCE_CURVE(ctypes.Structure):
    _fields_ = [
     (
      "pPoints", POINTER(X3DAUDIO_DISTANCE_CURVE_POINT)),
     (
      "PointCount", UINT32)]


class X3DAUDIO_VECTOR(ctypes.Structure):
    _fields_ = [
     (
      "x", c_float),
     (
      "y", c_float),
     (
      "z", c_float)]


class X3DAUDIO_CONE(Structure):
    _fields_ = [
     (
      "InnerAngle", FLOAT32),
     (
      "OuterAngle", FLOAT32),
     (
      "InnerVolume", FLOAT32),
     (
      "OuterVolume", FLOAT32),
     (
      "InnerLPF", FLOAT32),
     (
      "OuterLPF", FLOAT32),
     (
      "InnerReverb", FLOAT32),
     (
      "OuterReverb", FLOAT32)]


class X3DAUDIO_LISTENER(Structure):
    _fields_ = [
     (
      "OrientFront", X3DAUDIO_VECTOR),
     (
      "OrientTop", X3DAUDIO_VECTOR),
     (
      "Position", X3DAUDIO_VECTOR),
     (
      "Velocity", X3DAUDIO_VECTOR),
     (
      "pCone", POINTER(X3DAUDIO_CONE))]


class X3DAUDIO_EMITTER(Structure):
    _fields_ = [
     (
      "pCone", POINTER(X3DAUDIO_CONE)),
     (
      "OrientFront", X3DAUDIO_VECTOR),
     (
      "OrientTop", X3DAUDIO_VECTOR),
     (
      "Position", X3DAUDIO_VECTOR),
     (
      "Velocity", X3DAUDIO_VECTOR),
     (
      "InnerRadius", FLOAT32),
     (
      "InnerRadiusAngle", FLOAT32),
     (
      "ChannelCount", UINT32),
     (
      "ChannelRadius", FLOAT32),
     (
      "pChannelAzimuths", POINTER(FLOAT32)),
     (
      "pVolumeCurve", POINTER(X3DAUDIO_DISTANCE_CURVE)),
     (
      "pLFECurve", POINTER(X3DAUDIO_DISTANCE_CURVE)),
     (
      "pLPFDirectCurve", POINTER(X3DAUDIO_DISTANCE_CURVE)),
     (
      "pLPFReverbCurve", POINTER(X3DAUDIO_DISTANCE_CURVE)),
     (
      "pReverbCurve", POINTER(X3DAUDIO_DISTANCE_CURVE)),
     (
      "CurveDistanceScaler", FLOAT32),
     (
      "DopplerScaler", FLOAT32)]


class X3DAUDIO_DSP_SETTINGS(Structure):
    _fields_ = [
     (
      "pMatrixCoefficients", POINTER(FLOAT)),
     (
      "pDelayTimes", POINTER(FLOAT32)),
     (
      "SrcChannelCount", UINT32),
     (
      "DstChannelCount", UINT32),
     (
      "LPFDirectCoefficient", FLOAT32),
     (
      "LPFReverbCoefficient", FLOAT32),
     (
      "ReverbLevel", FLOAT32),
     (
      "DopplerFactor", FLOAT32),
     (
      "EmitterToListenerAngle", FLOAT32),
     (
      "EmitterToListenerDistance", FLOAT32),
     (
      "EmitterVelocityComponent", FLOAT32),
     (
      "ListenerVelocityComponent", FLOAT32)]


SPEAKER_FRONT_LEFT = 1
SPEAKER_FRONT_RIGHT = 2
SPEAKER_FRONT_CENTER = 4
SPEAKER_LOW_FREQUENCY = 8
SPEAKER_BACK_LEFT = 16
SPEAKER_BACK_RIGHT = 32
SPEAKER_FRONT_LEFT_OF_CENTER = 64
SPEAKER_FRONT_RIGHT_OF_CENTER = 128
SPEAKER_BACK_CENTER = 256
SPEAKER_SIDE_LEFT = 512
SPEAKER_SIDE_RIGHT = 1024
SPEAKER_TOP_CENTER = 2048
SPEAKER_TOP_FRONT_LEFT = 4096
SPEAKER_TOP_FRONT_CENTER = 8192
SPEAKER_TOP_FRONT_RIGHT = 16384
SPEAKER_TOP_BACK_LEFT = 32768
SPEAKER_TOP_BACK_CENTER = 65536
SPEAKER_TOP_BACK_RIGHT = 131072
SPEAKER_RESERVED = 2147221504
SPEAKER_ALL = 2147483648
SPEAKER_MONO = SPEAKER_FRONT_CENTER
SPEAKER_STEREO = SPEAKER_FRONT_LEFT | SPEAKER_FRONT_RIGHT
SPEAKER_2POINT1 = SPEAKER_FRONT_LEFT | SPEAKER_FRONT_RIGHT | SPEAKER_LOW_FREQUENCY
SPEAKER_SURROUND = SPEAKER_FRONT_LEFT | SPEAKER_FRONT_RIGHT | SPEAKER_FRONT_CENTER | SPEAKER_BACK_CENTER
SPEAKER_QUAD = SPEAKER_FRONT_LEFT | SPEAKER_FRONT_RIGHT | SPEAKER_BACK_LEFT | SPEAKER_BACK_RIGHT
SPEAKER_4POINT1 = SPEAKER_FRONT_LEFT | SPEAKER_FRONT_RIGHT | SPEAKER_LOW_FREQUENCY | SPEAKER_BACK_LEFT | SPEAKER_BACK_RIGHT
SPEAKER_5POINT1 = SPEAKER_FRONT_LEFT | SPEAKER_FRONT_RIGHT | SPEAKER_FRONT_CENTER | SPEAKER_LOW_FREQUENCY | SPEAKER_BACK_LEFT | SPEAKER_BACK_RIGHT
SPEAKER_7POINT1 = SPEAKER_FRONT_LEFT | SPEAKER_FRONT_RIGHT | SPEAKER_FRONT_CENTER | SPEAKER_LOW_FREQUENCY | SPEAKER_BACK_LEFT | SPEAKER_BACK_RIGHT | SPEAKER_FRONT_LEFT_OF_CENTER | SPEAKER_FRONT_RIGHT_OF_CENTER
SPEAKER_5POINT1_SURROUND = SPEAKER_FRONT_LEFT | SPEAKER_FRONT_RIGHT | SPEAKER_FRONT_CENTER | SPEAKER_LOW_FREQUENCY | SPEAKER_SIDE_LEFT | SPEAKER_SIDE_RIGHT
SPEAKER_7POINT1_SURROUND = SPEAKER_FRONT_LEFT | SPEAKER_FRONT_RIGHT | SPEAKER_FRONT_CENTER | SPEAKER_LOW_FREQUENCY | SPEAKER_BACK_LEFT | SPEAKER_BACK_RIGHT | SPEAKER_SIDE_LEFT | SPEAKER_SIDE_RIGHT
DBL_DECIMAL_DIG = 17
DBL_DIG = 15
DBL_EPSILON = 2.220446049250313e-16
DBL_HAS_SUBNORM = 1
DBL_MANT_DIG = 53
DBL_MAX = 1.7976931348623157e+308
DBL_MAX_10_EXP = 308
DBL_MAX_EXP = 1024
DBL_MIN = 2.2250738585072014e-308
DBL_MIN_10_EXP = -307
DBL_MIN_EXP = -1021
_DBL_RADIX = 2
DBL_TRUE_MIN = 5e-324
FLT_DECIMAL_DIG = 9
FLT_DIG = 6
FLT_EPSILON = 1.192092896e-07
FLT_HAS_SUBNORM = 1
FLT_GUARD = 0
FLT_MANT_DIG = 24
FLT_MAX = 3.402823466e+38
FLT_MAX_10_EXP = 38
FLT_MAX_EXP = 128
FLT_MIN = 1.175494351e-38
FLT_MIN_10_EXP = -37
FLT_MIN_EXP = -125
FLT_NORMALIZE = 0
FLT_RADIX = 2
FLT_TRUE_MIN = 1.401298464e-45
LDBL_DIG = DBL_DIG
LDBL_EPSILON = DBL_EPSILON
LDBL_HAS_SUBNORM = DBL_HAS_SUBNORM
LDBL_MANT_DIG = DBL_MANT_DIG
LDBL_MAX = DBL_MAX
LDBL_MAX_10_EXP = DBL_MAX_10_EXP
LDBL_MAX_EXP = DBL_MAX_EXP
LDBL_MIN = DBL_MIN
LDBL_MIN_10_EXP = DBL_MIN_10_EXP
LDBL_MIN_EXP = DBL_MIN_EXP
_LDBL_RADIX = _DBL_RADIX
LDBL_TRUE_MIN = DBL_TRUE_MIN
DECIMAL_DIG = DBL_DECIMAL_DIG
X3DAUDIO_HANDLE_BYTESIZE = 20
X3DAUDIO_HANDLE = BYTE * X3DAUDIO_HANDLE_BYTESIZE
X3DAUDIO_SPEED_OF_SOUND = 343.5
X3DAUDIO_CALCULATE_MATRIX = 1
X3DAUDIO_CALCULATE_DELAY = 2
X3DAUDIO_CALCULATE_LPF_DIRECT = 4
X3DAUDIO_CALCULATE_LPF_REVERB = 8
X3DAUDIO_CALCULATE_REVERB = 16
X3DAUDIO_CALCULATE_DOPPLER = 32
X3DAUDIO_CALCULATE_EMITTER_ANGLE = 64
X3DAUDIO_CALCULATE_ZEROCENTER = 65536
X3DAUDIO_CALCULATE_REDIRECT_TO_LFE = 131072
default_dsp_calculation = X3DAUDIO_CALCULATE_MATRIX | X3DAUDIO_CALCULATE_DOPPLER
X3DAudioInitialize = x3d_lib.X3DAudioInitialize
X3DAudioInitialize.restype = HRESULT
X3DAudioInitialize.argtypes = [c_int, c_float, c_void_p]
X3DAudioCalculate = x3d_lib.X3DAudioCalculate
X3DAudioCalculate.restype = c_void
X3DAudioCalculate.argtypes = [POINTER(X3DAUDIO_HANDLE), POINTER(X3DAUDIO_LISTENER), POINTER(X3DAUDIO_EMITTER), UINT32, POINTER(X3DAUDIO_DSP_SETTINGS)]
AudioCategory_Other = 0
AudioCategory_ForegroundOnlyMedia = 1
AudioCategory_Communications = 3
AudioCategory_Alerts = 4
AudioCategory_SoundEffects = 5
AudioCategory_GameEffects = 6
AudioCategory_GameMedia = 7
AudioCategory_GameChat = 8
AudioCategory_Speech = 9
AudioCategory_Movie = 10
AudioCategory_Media = 11

class XAUDIO2FX_REVERB_PARAMETERS(Structure):
    _fields_ = [
     (
      "WetDryMix", c_float),
     (
      "ReflectionsDelay", UINT32),
     (
      "ReverbDelay", BYTE),
     (
      "RearDelay", UINT32),
     (
      "SideDelay", UINT32),
     (
      "PositionLeft", BYTE),
     (
      "PositionRight", BYTE),
     (
      "PositionMatrixLeft", BYTE),
     (
      "PositionMatrixRight", BYTE),
     (
      "EarlyDiffusion", BYTE),
     (
      "LateDiffusion", BYTE),
     (
      "LowEQGain", BYTE),
     (
      "LowEQCutoff", BYTE),
     (
      "LowEQCutoff", BYTE),
     (
      "HighEQCutoff", BYTE),
     (
      "RoomFilterFreq", c_float),
     (
      "RoomFilterMain", c_float),
     (
      "RoomFilterHF", c_float),
     (
      "ReflectionsGain", c_float),
     (
      "ReverbGain", c_float),
     (
      "DecayTime", c_float),
     (
      "Density", c_float),
     (
      "RoomSize", c_float),
     (
      "DisableLateField", c_bool)]


class IXAudio2(com.pIUnknown):
    _methods_ = [
     (
      "RegisterForCallbacks",
      com.STDMETHOD(POINTER(IXAudio2EngineCallback))),
     (
      "UnregisterForCallbacks",
      com.METHOD(ctypes.c_void_p, POINTER(IXAudio2EngineCallback))),
     (
      "CreateSourceVoice",
      com.STDMETHOD(POINTER(IXAudio2SourceVoice), POINTER(WAVEFORMATEX), UINT32, c_float, POINTER(IXAudio2VoiceCallback), POINTER(XAUDIO2_VOICE_SENDS), POINTER(XAUDIO2_EFFECT_CHAIN))),
     (
      "CreateSubmixVoice",
      com.STDMETHOD(POINTER(IXAudio2SubmixVoice), UINT32, UINT32, UINT32, UINT32, POINTER(XAUDIO2_VOICE_SENDS), POINTER(XAUDIO2_EFFECT_CHAIN))),
     (
      "CreateMasteringVoice",
      com.STDMETHOD(POINTER(IXAudio2MasteringVoice), UINT32, UINT32, UINT32, LPCWSTR, POINTER(XAUDIO2_EFFECT_CHAIN), UINT32)),
     (
      "StartEngine",
      com.STDMETHOD()),
     (
      "StopEngine",
      com.STDMETHOD()),
     (
      "CommitChanges",
      com.STDMETHOD(UINT32)),
     (
      "GetPerformanceData",
      com.METHOD(c_void, POINTER(XAUDIO2_PERFORMANCE_DATA))),
     (
      "SetDebugConfiguration",
      com.STDMETHOD(POINTER(XAUDIO2_DEBUG_CONFIGURATION), c_void_p))]


XAudio2Create = xaudio2_lib.XAudio2Create
XAudio2Create.restype = HRESULT
XAudio2Create.argtypes = [POINTER(IXAudio2), UINT32, UINT32]
CreateAudioReverb = xaudio2_lib.CreateAudioReverb
CreateAudioReverb.restype = HRESULT
CreateAudioReverb.argtypes = [POINTER(com.pIUnknown)]
