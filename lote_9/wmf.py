# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\media\codecs\wmf.py
import os, platform, warnings
from pyglet import com, image
from pyglet.util import debug_print
from pyglet.libs.win32 import _kernel32 as kernel32
from pyglet.libs.win32 import _ole32 as ole32
from pyglet.libs.win32.constants import *
from pyglet.libs.win32.types import *
from pyglet.media import Source, MediaDecodeException
from pyglet.media.codecs import AudioFormat, AudioData, VideoFormat, MediaDecoder, StaticSource
_debug = debug_print("debug_media")
try:
    mfreadwrite = "mfreadwrite"
    mfplat = "mfplat"
    if platform.architecture()[0] == "32bit":
        if platform.machine().endswith("64"):
            mfreadwrite = os.path.join(os.environ["WINDIR"], "SysWOW64", "mfreadwrite.dll")
            mfplat = os.path.join(os.environ["WINDIR"], "SysWOW64", "mfplat.dll")
    mfreadwrite_lib = ctypes.windll.LoadLibrary(mfreadwrite)
    mfplat_lib = ctypes.windll.LoadLibrary(mfplat)
except OSError:
    raise ImportError("Could not load WMF library.")

MF_SOURCE_READERF_ERROR = 1
MF_SOURCE_READERF_ENDOFSTREAM = 2
MF_SOURCE_READERF_NEWSTREAM = 4
MF_SOURCE_READERF_NATIVEMEDIATYPECHANGED = 16
MF_SOURCE_READERF_CURRENTMEDIATYPECHANGED = 32
MF_SOURCE_READERF_STREAMTICK = 256
MF_LOW_LATENCY = com.GUID(2619836698, 60794, 16609, 136, 232, 178, 39, 39, 160, 36, 238)
MF_MT_ALL_SAMPLES_INDEPENDENT = com.GUID(3373741881, 24150, 17948, 183, 19, 70, 251, 153, 92, 185, 95)
MF_MT_FIXED_SIZE_SAMPLES = com.GUID(3102470063, 46872, 19972, 176, 169, 17, 103, 117, 227, 50, 27)
MF_MT_SAMPLE_SIZE = com.GUID(3671305080, 6544, 16523, 188, 226, 235, 166, 115, 218, 204, 16)
MF_MT_COMPRESSED = com.GUID(989662446, 6386, 19365, 161, 16, 139, 234, 80, 46, 31, 146)
MF_MT_WRAPPED_TYPE = com.GUID(1296005923, 53295, 20076, 155, 238, 228, 191, 44, 108, 105, 93)
MF_MT_AUDIO_NUM_CHANNELS = com.GUID(937724917, 25694, 19547, 137, 222, 173, 169, 226, 155, 105, 106)
MF_MT_AUDIO_SAMPLES_PER_SECOND = com.GUID(1605298919, 656, 19505, 158, 138, 197, 52, 246, 141, 157, 186)
MF_MT_AUDIO_FLOAT_SAMPLES_PER_SECOND = com.GUID(4214977098, 53173, 17177, 174, 254, 110, 66, 178, 64, 97, 50)
MF_MT_AUDIO_AVG_BYTES_PER_SECOND = com.GUID(447444424, 53231, 17692, 171, 149, 172, 3, 75, 142, 23, 49)
MF_MT_AUDIO_BLOCK_ALIGNMENT = com.GUID(841867824, 40683, 17341, 171, 122, 255, 65, 34, 81, 84, 29)
MF_MT_AUDIO_BITS_PER_SAMPLE = com.GUID(4074681727, 16634, 18276, 170, 51, 237, 79, 45, 31, 246, 105)
MF_MT_AUDIO_VALID_BITS_PER_SAMPLE = com.GUID(3653209450, 38192, 19324, 157, 223, 255, 111, 213, 139, 189, 6)
MF_MT_AUDIO_SAMPLES_PER_BLOCK = com.GUID(2863749804, 57658, 18837, 146, 34, 80, 30, 161, 92, 104, 119)
MF_MT_AUDIO_CHANNEL_MASK = com.GUID(1442535269, 25674, 19631, 132, 121, 147, 137, 131, 187, 21, 136)
MF_PD_DURATION = com.GUID(1821969715, 48014, 18298, 133, 152, 13, 93, 150, 252, 216, 138)
MF_MT_MAJOR_TYPE = com.GUID(1223401870, 63689, 18055, 191, 17, 10, 116, 201, 249, 106, 143)
MF_MT_SUBTYPE = com.GUID(4158868634, 17128, 18196, 183, 75, 203, 41, 215, 44, 53, 229)
MFMediaType_Audio = com.GUID(1935963489, 0, 16, 128, 0, 0, 170, 0, 56, 155, 113)
MFMediaType_Video = com.GUID(1935960438, 0, 16, 128, 0, 0, 170, 0, 56, 155, 113)
MFMediaType_Protected = com.GUID(2068541414, 40196, 17556, 190, 20, 126, 11, 208, 118, 200, 228)
MFMediaType_Image = com.GUID(1914145827, 58459, 4565, 188, 42, 0, 176, 208, 243, 244, 171)
MFMediaType_HTML = com.GUID(1914145828, 58459, 4565, 188, 42, 0, 176, 208, 243, 244, 171)
MFMediaType_Subtitle = com.GUID(2798728577, 60752, 20069, 174, 8, 38, 6, 85, 118, 170, 204)
D3DFMT_X8R8G8B8 = 22
D3DFMT_P8 = 41
D3DFMT_A8R8G8B8 = 21
MFVideoFormat_RGB32 = com.GUID(D3DFMT_X8R8G8B8, 0, 16, 128, 0, 0, 170, 0, 56, 155, 113)
MFVideoFormat_RGB8 = com.GUID(D3DFMT_P8, 0, 16, 128, 0, 0, 170, 0, 56, 155, 113)
MFVideoFormat_ARGB32 = com.GUID(D3DFMT_A8R8G8B8, 0, 16, 128, 0, 0, 170, 0, 56, 155, 113)
MFVideoInterlace_Progressive = 2
MF_MT_INTERLACE_MODE = com.GUID(3799141304, 58998, 18438, 180, 178, 168, 214, 239, 180, 76, 205)
MF_MT_FRAME_SIZE = com.GUID(374522685, 54962, 16402, 184, 52, 114, 3, 8, 73, 163, 125)
MF_MT_FRAME_RATE = com.GUID(3294208744, 15660, 20036, 177, 50, 254, 229, 21, 108, 123, 176)
MF_MT_PIXEL_ASPECT_RATIO = com.GUID(3325520414, 36106, 16423, 190, 69, 109, 154, 10, 211, 155, 182)
MF_MT_DRM_FLAGS = com.GUID(2272457507, 13658, 19655, 187, 120, 109, 97, 160, 72, 174, 130)
MF_MT_DEFAULT_STRIDE = com.GUID(1682656840, 7682, 17686, 176, 235, 192, 28, 169, 212, 154, 198)
WAVE_FORMAT_PCM = 1
WAVE_FORMAT_IEEE_FLOAT = 3
MFAudioFormat_PCM = com.GUID(WAVE_FORMAT_PCM, 0, 16, 128, 0, 0, 170, 0, 56, 155, 113)
MFAudioFormat_Float = com.GUID(WAVE_FORMAT_IEEE_FLOAT, 0, 16, 128, 0, 0, 170, 0, 56, 155, 113)
MFImageFormat_RGB32 = com.GUID(22, 0, 16, 128, 0, 0, 170, 0, 56, 155, 113)
MFImageFormat_JPEG = com.GUID(434415018, 22114, 20421, 160, 192, 23, 88, 2, 142, 16, 87)
MF_READWRITE_ENABLE_HARDWARE_TRANSFORMS = com.GUID(2788469020, 33323, 16825, 164, 148, 77, 228, 100, 54, 18, 176)
MF_SOURCE_READER_ENABLE_VIDEO_PROCESSING = com.GUID(4214837053, 52465, 17134, 187, 179, 249, 184, 69, 213, 104, 29)
MF_SOURCE_READER_D3D_MANAGER = com.GUID(3967954338, 57833, 19241, 160, 216, 86, 60, 113, 159, 82, 105)
MF_MEDIA_ENGINE_DXGI_MANAGER = com.GUID(106365658, 4244, 18541, 134, 23, 238, 124, 196, 238, 70, 72)
MF_SOURCE_READER_ENABLE_ADVANCED_VIDEO_PROCESSING = com.GUID(260168236, 46391, 18034, 168, 178, 166, 129, 177, 115, 7, 163)
MF_E_INVALIDSTREAMNUMBER = -1072875853
MF_E_UNSUPPORTED_BYTESTREAM_TYPE = -1072875836
MF_E_NO_MORE_TYPES = 3222091449
MF_E_TOPO_CODEC_NOT_FOUND = -1072868846
VT_I8 = 20

def timestamp_from_wmf(timestamp):
    return float(timestamp) / 10000000


def timestamp_to_wmf(timestamp):
    return int(timestamp * 10000000)


class IMFAttributes(com.pIUnknown):
    _methods_ = [
     (
      "GetItem",
      com.STDMETHOD()),
     (
      "GetItemType",
      com.STDMETHOD()),
     (
      "CompareItem",
      com.STDMETHOD()),
     (
      "Compare",
      com.STDMETHOD()),
     (
      "GetUINT32",
      com.STDMETHOD(com.REFIID, POINTER(c_uint32))),
     (
      "GetUINT64",
      com.STDMETHOD(com.REFIID, POINTER(c_uint64))),
     (
      "GetDouble",
      com.STDMETHOD()),
     (
      "GetGUID",
      com.STDMETHOD(com.REFIID, POINTER(com.GUID))),
     (
      "GetStringLength",
      com.STDMETHOD()),
     (
      "GetString",
      com.STDMETHOD()),
     (
      "GetAllocatedString",
      com.STDMETHOD()),
     (
      "GetBlobSize",
      com.STDMETHOD()),
     (
      "GetBlob",
      com.STDMETHOD()),
     (
      "GetAllocatedBlob",
      com.STDMETHOD()),
     (
      "GetUnknown",
      com.STDMETHOD()),
     (
      "SetItem",
      com.STDMETHOD()),
     (
      "DeleteItem",
      com.STDMETHOD()),
     (
      "DeleteAllItems",
      com.STDMETHOD()),
     (
      "SetUINT32",
      com.STDMETHOD(com.REFIID, c_uint32)),
     (
      "SetUINT64",
      com.STDMETHOD()),
     (
      "SetDouble",
      com.STDMETHOD()),
     (
      "SetGUID",
      com.STDMETHOD(com.REFIID, com.REFIID)),
     (
      "SetString",
      com.STDMETHOD()),
     (
      "SetBlob",
      com.STDMETHOD()),
     (
      "SetUnknown",
      com.STDMETHOD(com.REFIID, com.pIUnknown)),
     (
      "LockStore",
      com.STDMETHOD()),
     (
      "UnlockStore",
      com.STDMETHOD()),
     (
      "GetCount",
      com.STDMETHOD()),
     (
      "GetItemByIndex",
      com.STDMETHOD()),
     (
      "CopyAllItems",
      com.STDMETHOD(c_void_p))]


class IMFMediaBuffer(com.pIUnknown):
    _methods_ = [
     (
      "Lock",
      com.STDMETHOD(POINTER(POINTER(BYTE)), POINTER(DWORD), POINTER(DWORD))),
     (
      "Unlock",
      com.STDMETHOD()),
     (
      "GetCurrentLength",
      com.STDMETHOD(POINTER(DWORD))),
     (
      "SetCurrentLength",
      com.STDMETHOD(DWORD)),
     (
      "GetMaxLength",
      com.STDMETHOD(POINTER(DWORD)))]


class IMFSample(IMFAttributes, com.pIUnknown):
    _methods_ = [
     (
      "GetSampleFlags",
      com.STDMETHOD()),
     (
      "SetSampleFlags",
      com.STDMETHOD()),
     (
      "GetSampleTime",
      com.STDMETHOD()),
     (
      "SetSampleTime",
      com.STDMETHOD()),
     (
      "GetSampleDuration",
      com.STDMETHOD(POINTER(c_ulonglong))),
     (
      "SetSampleDuration",
      com.STDMETHOD(DWORD, IMFMediaBuffer)),
     (
      "GetBufferCount",
      com.STDMETHOD(POINTER(DWORD))),
     (
      "GetBufferByIndex",
      com.STDMETHOD(DWORD, IMFMediaBuffer)),
     (
      "ConvertToContiguousBuffer",
      com.STDMETHOD(POINTER(IMFMediaBuffer))),
     (
      "AddBuffer",
      com.STDMETHOD(POINTER(DWORD))),
     (
      "RemoveBufferByIndex",
      com.STDMETHOD()),
     (
      "RemoveAllBuffers",
      com.STDMETHOD()),
     (
      "GetTotalLength",
      com.STDMETHOD(POINTER(DWORD))),
     (
      "CopyToBuffer",
      com.STDMETHOD())]


class IMFMediaType(IMFAttributes, com.pIUnknown):
    _methods_ = [
     (
      "GetMajorType",
      com.STDMETHOD()),
     (
      "IsCompressedFormat",
      com.STDMETHOD()),
     (
      "IsEqual",
      com.STDMETHOD()),
     (
      "GetRepresentation",
      com.STDMETHOD()),
     (
      "FreeRepresentation",
      com.STDMETHOD())]


class IMFByteStream(com.pIUnknown):
    _methods_ = [
     (
      "GetCapabilities",
      com.STDMETHOD()),
     (
      "GetLength",
      com.STDMETHOD()),
     (
      "SetLength",
      com.STDMETHOD()),
     (
      "GetCurrentPosition",
      com.STDMETHOD()),
     (
      "SetCurrentPosition",
      com.STDMETHOD(c_ulonglong)),
     (
      "IsEndOfStream",
      com.STDMETHOD()),
     (
      "Read",
      com.STDMETHOD()),
     (
      "BeginRead",
      com.STDMETHOD()),
     (
      "EndRead",
      com.STDMETHOD()),
     (
      "Write",
      com.STDMETHOD(POINTER(BYTE), ULONG, POINTER(ULONG))),
     (
      "BeginWrite",
      com.STDMETHOD()),
     (
      "EndWrite",
      com.STDMETHOD()),
     (
      "Seek",
      com.STDMETHOD()),
     (
      "Flush",
      com.STDMETHOD()),
     (
      "Close",
      com.STDMETHOD())]


class IMFSourceReader(com.pIUnknown):
    _methods_ = [
     (
      "GetStreamSelection",
      com.STDMETHOD(DWORD, POINTER(BOOL))),
     (
      "SetStreamSelection",
      com.STDMETHOD(DWORD, BOOL)),
     (
      "GetNativeMediaType",
      com.STDMETHOD(DWORD, DWORD, POINTER(IMFMediaType))),
     (
      "GetCurrentMediaType",
      com.STDMETHOD(DWORD, POINTER(IMFMediaType))),
     (
      "SetCurrentMediaType",
      com.STDMETHOD(DWORD, POINTER(DWORD), IMFMediaType)),
     (
      "SetCurrentPosition",
      com.STDMETHOD(com.REFIID, POINTER(PROPVARIANT))),
     (
      "ReadSample",
      com.STDMETHOD(DWORD, DWORD, POINTER(DWORD), POINTER(DWORD), POINTER(c_longlong), POINTER(IMFSample))),
     (
      "Flush",
      com.STDMETHOD(DWORD)),
     (
      "GetServiceForStream",
      com.STDMETHOD()),
     (
      "GetPresentationAttribute",
      com.STDMETHOD(DWORD, com.REFIID, POINTER(PROPVARIANT)))]


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


MF_SOURCE_READER_ALL_STREAMS = 4294967294
MF_SOURCE_READER_ANY_STREAM = 4294967294
MF_SOURCE_READER_FIRST_AUDIO_STREAM = 4294967293
MF_SOURCE_READER_FIRST_VIDEO_STREAM = 4294967292
MF_SOURCE_READER_MEDIASOURCE = 4294967295
if WINDOWS_7_OR_GREATER:
    MF_SDK_VERSION = 2
else:
    MF_SDK_VERSION = 1
MF_API_VERSION = 112
MF_VERSION = MF_SDK_VERSION << 16 | MF_API_VERSION
MFStartup = mfplat_lib.MFStartup
MFStartup.restype = HRESULT
MFStartup.argtypes = [LONG, DWORD]
MFShutdown = mfplat_lib.MFShutdown
MFShutdown.restype = HRESULT
MFShutdown.argtypes = []
MFCreateAttributes = mfplat_lib.MFCreateAttributes
MFCreateAttributes.restype = HRESULT
MFCreateAttributes.argtypes = [POINTER(IMFAttributes), c_uint32]
MFCreateSourceReaderFromURL = mfreadwrite_lib.MFCreateSourceReaderFromURL
MFCreateSourceReaderFromURL.restype = HRESULT
MFCreateSourceReaderFromURL.argtypes = [LPCWSTR, IMFAttributes, POINTER(IMFSourceReader)]
MFCreateSourceReaderFromByteStream = mfreadwrite_lib.MFCreateSourceReaderFromByteStream
MFCreateSourceReaderFromByteStream.restype = HRESULT
MFCreateSourceReaderFromByteStream.argtypes = [IMFByteStream, IMFAttributes, POINTER(IMFSourceReader)]
if WINDOWS_7_OR_GREATER:
    MFCreateMFByteStreamOnStream = mfplat_lib.MFCreateMFByteStreamOnStream
    MFCreateMFByteStreamOnStream.restype = HRESULT
    MFCreateMFByteStreamOnStream.argtypes = [c_void_p, POINTER(IMFByteStream)]
MFCreateTempFile = mfplat_lib.MFCreateTempFile
MFCreateTempFile.restype = HRESULT
MFCreateTempFile.argtypes = [UINT, UINT, UINT, POINTER(IMFByteStream)]
MFCreateMediaType = mfplat_lib.MFCreateMediaType
MFCreateMediaType.restype = HRESULT
MFCreateMediaType.argtypes = [POINTER(IMFMediaType)]
MFCreateWaveFormatExFromMFMediaType = mfplat_lib.MFCreateWaveFormatExFromMFMediaType
MFCreateWaveFormatExFromMFMediaType.restype = HRESULT
MFCreateWaveFormatExFromMFMediaType.argtypes = [IMFMediaType, POINTER(POINTER(WAVEFORMATEX)), POINTER(c_uint32), c_uint32]

class WMFSource(Source):
    low_latency = True
    decode_audio = True
    decode_video = True

    def __init__(self, filename, file=None):
        if not any([self.decode_audio, self.decode_video]):
            raise AssertionError("Source must decode audio, video, or both, not none.")
        else:
            self._current_audio_sample = None
            self._current_audio_buffer = None
            self._current_video_sample = None
            self._current_video_buffer = None
            self._timestamp = 0
            self._attributes = None
            self._stream_obj = None
            self._imf_bytestream = None
            self._wfx = None
            self._stride = None
            self.set_config_attributes()
            self._source_reader = IMFSourceReader()
            if file is not None:
                data = file.read()
                self._imf_bytestream = IMFByteStream()
                data_len = len(data)
                if WINDOWS_7_OR_GREATER:
                    hglob = kernel32.GlobalAlloc(GMEM_MOVEABLE, data_len)
                    ptr = kernel32.GlobalLock(hglob)
                    ctypes.memmove(ptr, data, data_len)
                    kernel32.GlobalUnlock(hglob)
                    self._stream_obj = com.pIUnknown()
                    ole32.CreateStreamOnHGlobal(hglob, True, ctypes.byref(self._stream_obj))
                    MFCreateMFByteStreamOnStream(self._stream_obj, ctypes.byref(self._imf_bytestream))
                else:
                    MFCreateTempFile(MF_ACCESSMODE_READWRITE, MF_OPENMODE_DELETE_IF_EXIST, MF_FILEFLAGS_NONE, ctypes.byref(self._imf_bytestream))
                    wrote_length = ULONG()
                    data_ptr = cast(data, POINTER(BYTE))
                    self._imf_bytestream.Write(data_ptr, data_len, ctypes.byref(wrote_length))
                    self._imf_bytestream.SetCurrentPosition(0)
                    if wrote_length.value != data_len:
                        raise MediaDecodeException("Could not write all of the data to the bytestream file.")
                    try:
                        MFCreateSourceReaderFromByteStream(self._imf_bytestream, self._attributes, ctypes.byref(self._source_reader))
                    except OSError as err:
                        raise MediaDecodeException(err) from None

            else:
                try:
                    MFCreateSourceReaderFromURL(filename, self._attributes, ctypes.byref(self._source_reader))
                except OSError as err:
                    raise MediaDecodeException(err) from None

                if self.decode_audio:
                    self._load_audio()
                if self.decode_video:
                    self._load_video()
                if not self.audio_format:
                    assert self.video_format, "Source was decoded, but no video or audio streams were found."
                    try:
                        prop = PROPVARIANT()
                        self._source_reader.GetPresentationAttribute(MF_SOURCE_READER_MEDIASOURCE, ctypes.byref(MF_PD_DURATION), ctypes.byref(prop))
                        self._duration = timestamp_from_wmf(prop.llVal)
                        ole32.PropVariantClear(ctypes.byref(prop))
                    except OSError:
                        warnings.warn("Could not determine duration of media file: '{}'.".format(filename))

    def _load_audio(self, stream=MF_SOURCE_READER_FIRST_AUDIO_STREAM):
        """ Prepares the audio stream for playback by detecting if it's compressed and attempting to decompress to PCM.
            Default: Only get the first available audio stream.
        """
        self._audio_stream_index = stream
        imfmedia = IMFMediaType()
        try:
            self._source_reader.GetNativeMediaType(self._audio_stream_index, 0, ctypes.byref(imfmedia))
        except OSError as err:
            if err.winerror == MF_E_INVALIDSTREAMNUMBER:
                if not _debug("WMFAudioDecoder: No audio stream found."):
                    raise AssertionError
            return

        guid_audio_type = com.GUID(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        imfmedia.GetGUID(MF_MT_MAJOR_TYPE, ctypes.byref(guid_audio_type))
        if guid_audio_type == MFMediaType_Audio:
            assert _debug("WMFAudioDecoder: Found Audio Stream.")
            if not self.decode_video:
                self._source_reader.SetStreamSelection(MF_SOURCE_READER_ANY_STREAM, False)
            self._source_reader.SetStreamSelection(MF_SOURCE_READER_FIRST_AUDIO_STREAM, True)
            guid_compressed = com.GUID(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
            imfmedia.GetGUID(MF_MT_SUBTYPE, ctypes.byref(guid_compressed))
            if guid_compressed == MFAudioFormat_PCM or guid_compressed == MFAudioFormat_Float:
                if not _debug("WMFAudioDecoder: Found Uncompressed Audio:", guid_compressed):
                    raise AssertionError
                else:
                    assert _debug("WMFAudioDecoder: Found Compressed Audio:", guid_compressed)
                    mf_mediatype = IMFMediaType()
                    MFCreateMediaType(ctypes.byref(mf_mediatype))
                    mf_mediatype.SetGUID(MF_MT_MAJOR_TYPE, MFMediaType_Audio)
                    mf_mediatype.SetGUID(MF_MT_SUBTYPE, MFAudioFormat_PCM)
                try:
                    self._source_reader.SetCurrentMediaType(self._audio_stream_index, None, mf_mediatype)
                except OSError as err:
                    raise MediaDecodeException(err) from None

                decoded_media_type = IMFMediaType()
                self._source_reader.GetCurrentMediaType(self._audio_stream_index, ctypes.byref(decoded_media_type))
                wfx_length = ctypes.c_uint32()
                wfx = POINTER(WAVEFORMATEX)()
                MFCreateWaveFormatExFromMFMediaType(decoded_media_type, ctypes.byref(wfx), ctypes.byref(wfx_length), 0)
                self._wfx = wfx.contents
                self.audio_format = AudioFormat(channels=(self._wfx.nChannels), sample_size=(self._wfx.wBitsPerSample),
                  sample_rate=(self._wfx.nSamplesPerSec))
        assert _debug("WMFAudioDecoder: Audio stream not found")

    def get_format(self):
        """Returns the WAVEFORMATEX data which has more information thah audio_format"""
        return self._wfx

    def _load_video(self, stream=MF_SOURCE_READER_FIRST_VIDEO_STREAM):
        self._video_stream_index = stream
        imfmedia = IMFMediaType()
        try:
            self._source_reader.GetCurrentMediaType(self._video_stream_index, ctypes.byref(imfmedia))
        except OSError as err:
            if err.winerror == MF_E_INVALIDSTREAMNUMBER:
                if not _debug("WMFVideoDecoder: No video stream found."):
                    raise AssertionError
            return

        if not _debug("WMFVideoDecoder: Found Video Stream"):
            raise AssertionError
        else:
            uncompressed_mt = IMFMediaType()
            MFCreateMediaType(ctypes.byref(uncompressed_mt))
            imfmedia.CopyAllItems(uncompressed_mt)
            imfmedia.Release()
            uncompressed_mt.SetGUID(MF_MT_SUBTYPE, MFVideoFormat_RGB32)
            uncompressed_mt.SetUINT32(MF_MT_INTERLACE_MODE, MFVideoInterlace_Progressive)
            uncompressed_mt.SetUINT32(MF_MT_ALL_SAMPLES_INDEPENDENT, 1)
            try:
                self._source_reader.SetCurrentMediaType(self._video_stream_index, None, uncompressed_mt)
            except OSError as err:
                raise MediaDecodeException(err) from None

            height, width = self._get_attribute_size(uncompressed_mt, MF_MT_FRAME_SIZE)
            self.video_format = VideoFormat(width=width, height=height)
            assert _debug("WMFVideoDecoder: Frame width: {} height: {}".format(width, height))
        den, num = self._get_attribute_size(uncompressed_mt, MF_MT_FRAME_RATE)
        self.video_format.frame_rate = num / den
        if not _debug("WMFVideoDecoder: Frame Rate: {} / {} = {}".format(num, den, self.video_format.frame_rate)):
            raise AssertionError
        else:
            if self.video_format.frame_rate < 0:
                self.video_format.frame_rate = 29.97002997002997
                if not _debug("WARNING: Negative frame rate, attempting to use default, but may experience issues."):
                    raise AssertionError
            den, num = self._get_attribute_size(uncompressed_mt, MF_MT_PIXEL_ASPECT_RATIO)
            self.video_format.sample_aspect = num / den
            assert _debug("WMFVideoDecoder: Pixel Ratio: {} / {} = {}".format(num, den, self.video_format.sample_aspect))

    def get_audio_data(self, num_bytes, compensation_time=0.0):
        flags = DWORD()
        timestamp = ctypes.c_longlong()
        audio_data_length = DWORD()
        if self._current_audio_sample:
            self._current_audio_buffer.Release()
            self._current_audio_sample.Release()
        self._current_audio_sample = IMFSample()
        self._current_audio_buffer = IMFMediaBuffer()
        while 1:
            self._source_reader.ReadSample(self._audio_stream_index, 0, None, ctypes.byref(flags), ctypes.byref(timestamp), ctypes.byref(self._current_audio_sample))
            if flags.value & MF_SOURCE_READERF_CURRENTMEDIATYPECHANGED:
                assert _debug("WMFAudioDecoder: Data is no longer valid.")
                break
            if flags.value & MF_SOURCE_READERF_ENDOFSTREAM:
                assert _debug("WMFAudioDecoder: End of data from stream source.")
                break
            if not (self._current_audio_sample or _debug("WMFAudioDecoder: No sample.")):
                raise AssertionError
                continue
            self._current_audio_sample.ConvertToContiguousBuffer(ctypes.byref(self._current_audio_buffer))
            audio_data_ptr = POINTER(BYTE)()
            self._current_audio_buffer.Lock(ctypes.byref(audio_data_ptr), None, ctypes.byref(audio_data_length))
            self._current_audio_buffer.Unlock()
            audio_data = create_string_buffer(audio_data_length.value)
            memmove(audio_data, audio_data_ptr, audio_data_length.value)
            return AudioData(audio_data, audio_data_length.value, timestamp_from_wmf(timestamp.value), audio_data_length.value / self.audio_format.sample_rate, [])

        return

    def get_next_video_frame(self, skip_empty_frame=True):
        video_data_length = DWORD()
        flags = DWORD()
        timestamp = ctypes.c_longlong()
        if self._current_video_sample:
            self._current_video_buffer.Release()
            self._current_video_sample.Release()
        self._current_video_sample = IMFSample()
        self._current_video_buffer = IMFMediaBuffer()
        while 1:
            self._source_reader.ReadSample(self._video_stream_index, 0, None, ctypes.byref(flags), ctypes.byref(timestamp), ctypes.byref(self._current_video_sample))
            if flags.value & MF_SOURCE_READERF_CURRENTMEDIATYPECHANGED:
                assert _debug("WMFVideoDecoder: Data is no longer valid.")
                new = IMFMediaType()
                self._source_reader.GetCurrentMediaType(self._video_stream_index, ctypes.byref(new))
                stride = ctypes.c_uint32()
                new.GetUINT32(MF_MT_DEFAULT_STRIDE, ctypes.byref(stride))
                self._stride = stride.value
            if flags.value & MF_SOURCE_READERF_ENDOFSTREAM:
                self._timestamp = None
                assert _debug("WMFVideoDecoder: End of data from stream source.")
                break
            if not (self._current_video_sample or _debug("WMFVideoDecoder: No sample.")):
                raise AssertionError
                continue
            self._current_video_buffer = IMFMediaBuffer()
            self._current_video_sample.ConvertToContiguousBuffer(ctypes.byref(self._current_video_buffer))
            video_data = POINTER(BYTE)()
            self._current_video_buffer.Lock(ctypes.byref(video_data), None, ctypes.byref(video_data_length))
            width = self.video_format.width
            height = self.video_format.height
            self._timestamp = timestamp_from_wmf(timestamp.value)
            self._current_video_buffer.Unlock()
            return image.ImageData(width, height, "BGRA", video_data, self._stride)

        return

    def get_next_video_timestamp(self):
        return self._timestamp

    def seek(self, timestamp):
        timestamp = min(timestamp, self._duration) if self._duration else timestamp
        prop = PROPVARIANT()
        prop.vt = VT_I8
        prop.llVal = timestamp_to_wmf(timestamp)
        pos_com = com.GUID(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        try:
            self._source_reader.SetCurrentPosition(pos_com, prop)
        except OSError as err:
            warnings.warn(str(err))

        ole32.PropVariantClear(ctypes.byref(prop))

    @staticmethod
    def _get_attribute_size(attributes, guidKey):
        """ Convert int64 attributes to int32"""
        size = ctypes.c_uint64()
        attributes.GetUINT64(guidKey, size)
        lParam = size.value
        x = ctypes.c_int32(lParam).value
        y = ctypes.c_int32(lParam >> 32).value
        return (x, y)

    def set_config_attributes(self):
        """ Here we set user specified attributes, by default we try to set low latency mode. (Win7+)"""
        if self.low_latency or self.decode_video:
            self._attributes = IMFAttributes()
            MFCreateAttributes(ctypes.byref(self._attributes), 3)
        else:
            if self.low_latency:
                if WINDOWS_7_OR_GREATER:
                    self._attributes.SetUINT32(ctypes.byref(MF_LOW_LATENCY), 1)
                    assert _debug("WMFAudioDecoder: Setting configuration attributes.")
            if self.decode_video:
                self._attributes.SetUINT32(ctypes.byref(MF_READWRITE_ENABLE_HARDWARE_TRANSFORMS), 1)
                self._attributes.SetUINT32(ctypes.byref(MF_SOURCE_READER_ENABLE_VIDEO_PROCESSING), 1)
                assert _debug("WMFVideoDecoder: Setting configuration attributes.")

    def __del__(self):
        if self._stream_obj:
            self._stream_obj.Release()
        else:
            if self._imf_bytestream:
                self._imf_bytestream.Release()
            if self._current_audio_sample:
                self._current_audio_buffer.Release()
                self._current_audio_sample.Release()
            if self._current_video_sample:
                self._current_video_buffer.Release()
                self._current_video_sample.Release()


class WMFDecoder(MediaDecoder):

    def __init__(self):
        self.ole32 = None
        self.MFShutdown = None
        try:
            ole32.CoInitializeEx(None, COINIT_MULTITHREADED)
        except OSError as err:
            warnings.warn(str(err))

        try:
            MFStartup(MF_VERSION, 0)
        except OSError as err:
            raise ImportError("WMF could not startup:", err.strerror)

        self.extensions = self._build_decoder_extensions()
        self.ole32 = ole32
        self.MFShutdown = MFShutdown
        assert _debug("Windows Media Foundation: Initialized.")

    @staticmethod
    def _build_decoder_extensions():
        """Extension support varies depending on OS version."""
        extensions = []
        if WINDOWS_VISTA_OR_GREATER:
            extensions.extend(['.asf', '.wma', '.wmv', 
             '.mp3', 
             '.sami', 
             '.smi'])
        if WINDOWS_7_OR_GREATER:
            extensions.extend(['.3g2', '.3gp', '.3gp2', '.3gp', 
             '.aac', 
             '.adts', 
             '.avi', 
             '.m4a', 
             '.m4v', '.mov', '.mp4'])
        if WINDOWS_10_ANNIVERSARY_UPDATE_OR_GREATER:
            extensions.extend([".mkv", ".flac", ".ogg"])
        return extensions

    def get_file_extensions(self):
        return self.extensions

    def decode(self, file, filename, streaming=True):
        if streaming:
            return WMFSource(filename, file)
        else:
            return StaticSource(WMFSource(filename, file))

    def __del__(self):
        if self.MFShutdown is not None:
            self.MFShutdown()
        if self.ole32 is not None:
            self.ole32.CoUninitialize()


def get_decoders():
    return [
     WMFDecoder()]


def get_encoders():
    return []
