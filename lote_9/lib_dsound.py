# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\media\drivers\directsound\lib_dsound.py
import ctypes
from pyglet import com
lib = ctypes.oledll.dsound
DWORD = ctypes.c_uint32
LPDWORD = ctypes.POINTER(DWORD)
LONG = ctypes.c_long
LPLONG = ctypes.POINTER(LONG)
WORD = ctypes.c_uint16
HWND = DWORD
LPUNKNOWN = ctypes.c_void_p
D3DVALUE = ctypes.c_float
PD3DVALUE = ctypes.POINTER(D3DVALUE)

class D3DVECTOR(ctypes.Structure):
    _fields_ = [
     (
      "x", ctypes.c_float),
     (
      "y", ctypes.c_float),
     (
      "z", ctypes.c_float)]


PD3DVECTOR = ctypes.POINTER(D3DVECTOR)

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


LPWAVEFORMATEX = ctypes.POINTER(WAVEFORMATEX)
WAVE_FORMAT_PCM = 1

class DSCAPS(ctypes.Structure):
    _fields_ = [
     (
      "dwSize", DWORD),
     (
      "dwFlags", DWORD),
     (
      "dwMinSecondarySampleRate", DWORD),
     (
      "dwMaxSecondarySampleRate", DWORD),
     (
      "dwPrimaryBuffers", DWORD),
     (
      "dwMaxHwMixingAllBuffers", DWORD),
     (
      "dwMaxHwMixingStaticBuffers", DWORD),
     (
      "dwMaxHwMixingStreamingBuffers", DWORD),
     (
      "dwFreeHwMixingAllBuffers", DWORD),
     (
      "dwFreeHwMixingStaticBuffers", DWORD),
     (
      "dwFreeHwMixingStreamingBuffers", DWORD),
     (
      "dwMaxHw3DAllBuffers", DWORD),
     (
      "dwMaxHw3DStaticBuffers", DWORD),
     (
      "dwMaxHw3DStreamingBuffers", DWORD),
     (
      "dwFreeHw3DAllBuffers", DWORD),
     (
      "dwFreeHw3DStaticBuffers", DWORD),
     (
      "dwFreeHw3DStreamingBuffers", DWORD),
     (
      "dwTotalHwMemBytes", DWORD),
     (
      "dwFreeHwMemBytes", DWORD),
     (
      "dwMaxContigFreeHwMemBytes", DWORD),
     (
      "dwUnlockTransferRateHwBuffers", DWORD),
     (
      "dwPlayCpuOverheadSwBuffers", DWORD),
     (
      "dwReserved1", DWORD),
     (
      "dwReserved2", DWORD)]


LPDSCAPS = ctypes.POINTER(DSCAPS)

class DSBCAPS(ctypes.Structure):
    _fields_ = [
     (
      "dwSize", DWORD),
     (
      "dwFlags", DWORD),
     (
      "dwBufferBytes", DWORD),
     (
      "dwUnlockTransferRate", DWORD),
     (
      "dwPlayCpuOverhead", DWORD)]


LPDSBCAPS = ctypes.POINTER(DSBCAPS)

class DSBUFFERDESC(ctypes.Structure):
    _fields_ = [
     (
      "dwSize", DWORD),
     (
      "dwFlags", DWORD),
     (
      "dwBufferBytes", DWORD),
     (
      "dwReserved", DWORD),
     (
      "lpwfxFormat", LPWAVEFORMATEX)]

    def __repr__(self):
        return "DSBUFFERDESC(dwSize={}, dwFlags={}, dwBufferBytes={}, lpwfxFormat={})".format(self.dwSize, self.dwFlags, self.dwBufferBytes, self.lpwfxFormat.contents if self.lpwfxFormat else None)


LPDSBUFFERDESC = ctypes.POINTER(DSBUFFERDESC)

class DS3DBUFFER(ctypes.Structure):
    _fields_ = [
     (
      "dwSize", DWORD),
     (
      "vPosition", D3DVECTOR),
     (
      "vVelocity", D3DVECTOR),
     (
      "dwInsideConeAngle", DWORD),
     (
      "dwOutsideConeAngle", DWORD),
     (
      "vConeOrientation", D3DVECTOR),
     (
      "lConeOutsideVolume", LONG),
     (
      "flMinDistance", D3DVALUE),
     (
      "flMaxDistance", D3DVALUE),
     (
      "dwMode", DWORD)]


LPDS3DBUFFER = ctypes.POINTER(DS3DBUFFER)

class DS3DLISTENER(ctypes.Structure):
    _fields_ = [
     (
      "dwSize", DWORD),
     (
      "vPosition", D3DVECTOR),
     (
      "vVelocity", D3DVECTOR),
     (
      "vOrientFront", D3DVECTOR),
     (
      "vOrientTop", D3DVECTOR),
     (
      "flDistanceFactor", D3DVALUE),
     (
      "flRolloffFactor", D3DVALUE),
     (
      "flDopplerFactor", D3DVALUE)]


LPDS3DLISTENER = ctypes.POINTER(DS3DLISTENER)

class IDirectSoundBuffer(com.pIUnknown):
    _methods_ = [
     (
      "GetCaps",
      com.STDMETHOD(LPDSBCAPS)),
     (
      "GetCurrentPosition",
      com.STDMETHOD(LPDWORD, LPDWORD)),
     (
      "GetFormat",
      com.STDMETHOD(LPWAVEFORMATEX, DWORD, LPDWORD)),
     (
      "GetVolume",
      com.STDMETHOD(LPLONG)),
     (
      "GetPan",
      com.STDMETHOD(LPLONG)),
     (
      "GetFrequency",
      com.STDMETHOD(LPDWORD)),
     (
      "GetStatus",
      com.STDMETHOD(LPDWORD)),
     (
      "Initialize",
      com.STDMETHOD(ctypes.c_void_p, LPDSBUFFERDESC)),
     (
      "Lock",
      com.STDMETHOD(DWORD, DWORD, ctypes.POINTER(ctypes.c_void_p), LPDWORD, ctypes.POINTER(ctypes.c_void_p), LPDWORD, DWORD)),
     (
      "Play",
      com.STDMETHOD(DWORD, DWORD, DWORD)),
     (
      "SetCurrentPosition",
      com.STDMETHOD(DWORD)),
     (
      "SetFormat",
      com.STDMETHOD(LPWAVEFORMATEX)),
     (
      "SetVolume",
      com.STDMETHOD(LONG)),
     (
      "SetPan",
      com.STDMETHOD(LONG)),
     (
      "SetFrequency",
      com.STDMETHOD(DWORD)),
     (
      "Stop",
      com.STDMETHOD()),
     (
      "Unlock",
      com.STDMETHOD(ctypes.c_void_p, DWORD, ctypes.c_void_p, DWORD)),
     (
      "Restore",
      com.STDMETHOD())]


IID_IDirectSound3DListener = com.GUID(664468100, 18817, 4558, 165, 33, 0, 32, 175, 11, 229, 96)

class IDirectSound3DListener(com.pIUnknown):
    _methods_ = [
     (
      "GetAllParameters",
      com.STDMETHOD(LPDS3DLISTENER)),
     (
      "GetDistanceFactor",
      com.STDMETHOD(PD3DVALUE)),
     (
      "GetDopplerFactor",
      com.STDMETHOD(PD3DVALUE)),
     (
      "GetOrientation",
      com.STDMETHOD(PD3DVECTOR, PD3DVECTOR)),
     (
      "GetPosition",
      com.STDMETHOD(PD3DVECTOR)),
     (
      "GetRolloffFactor",
      com.STDMETHOD(PD3DVALUE)),
     (
      "GetVelocity",
      com.STDMETHOD(PD3DVECTOR)),
     (
      "SetAllParameters",
      com.STDMETHOD(LPDS3DLISTENER)),
     (
      "SetDistanceFactor",
      com.STDMETHOD(D3DVALUE, DWORD)),
     (
      "SetDopplerFactor",
      com.STDMETHOD(D3DVALUE, DWORD)),
     (
      "SetOrientation",
      com.STDMETHOD(D3DVALUE, D3DVALUE, D3DVALUE, D3DVALUE, D3DVALUE, D3DVALUE, DWORD)),
     (
      "SetPosition",
      com.STDMETHOD(D3DVALUE, D3DVALUE, D3DVALUE, DWORD)),
     (
      "SetRolloffFactor",
      com.STDMETHOD(D3DVALUE, DWORD)),
     (
      "SetVelocity",
      com.STDMETHOD(D3DVALUE, D3DVALUE, D3DVALUE, DWORD)),
     (
      "CommitDeferredSettings",
      com.STDMETHOD())]


IID_IDirectSound3DBuffer = com.GUID(664468102, 18817, 4558, 165, 33, 0, 32, 175, 11, 229, 96)

class IDirectSound3DBuffer(com.pIUnknown):
    _methods_ = [
     (
      "GetAllParameters",
      com.STDMETHOD(LPDS3DBUFFER)),
     (
      "GetConeAngles",
      com.STDMETHOD(LPDWORD, LPDWORD)),
     (
      "GetConeOrientation",
      com.STDMETHOD(PD3DVECTOR)),
     (
      "GetConeOutsideVolume",
      com.STDMETHOD(LPLONG)),
     (
      "GetMaxDistance",
      com.STDMETHOD(PD3DVALUE)),
     (
      "GetMinDistance",
      com.STDMETHOD(PD3DVALUE)),
     (
      "GetMode",
      com.STDMETHOD(LPDWORD)),
     (
      "GetPosition",
      com.STDMETHOD(PD3DVECTOR)),
     (
      "GetVelocity",
      com.STDMETHOD(PD3DVECTOR)),
     (
      "SetAllParameters",
      com.STDMETHOD(LPDS3DBUFFER, DWORD)),
     (
      "SetConeAngles",
      com.STDMETHOD(DWORD, DWORD, DWORD)),
     (
      "SetConeOrientation",
      com.STDMETHOD(D3DVALUE, D3DVALUE, D3DVALUE, DWORD)),
     (
      "SetConeOutsideVolume",
      com.STDMETHOD(LONG, DWORD)),
     (
      "SetMaxDistance",
      com.STDMETHOD(D3DVALUE, DWORD)),
     (
      "SetMinDistance",
      com.STDMETHOD(D3DVALUE, DWORD)),
     (
      "SetMode",
      com.STDMETHOD(DWORD, DWORD)),
     (
      "SetPosition",
      com.STDMETHOD(D3DVALUE, D3DVALUE, D3DVALUE, DWORD)),
     (
      "SetVelocity",
      com.STDMETHOD(D3DVALUE, D3DVALUE, D3DVALUE, DWORD))]


class IDirectSound(com.pIUnknown):
    _methods_ = [
     (
      "CreateSoundBuffer",
      com.STDMETHOD(LPDSBUFFERDESC, ctypes.POINTER(IDirectSoundBuffer), LPUNKNOWN)),
     (
      "GetCaps",
      com.STDMETHOD(LPDSCAPS)),
     (
      "DuplicateSoundBuffer",
      com.STDMETHOD(IDirectSoundBuffer, ctypes.POINTER(IDirectSoundBuffer))),
     (
      "SetCooperativeLevel",
      com.STDMETHOD(HWND, DWORD)),
     (
      "Compact",
      com.STDMETHOD()),
     (
      "GetSpeakerConfig",
      com.STDMETHOD(LPDWORD)),
     (
      "SetSpeakerConfig",
      com.STDMETHOD(DWORD)),
     (
      "Initialize",
      com.STDMETHOD(com.LPGUID))]
    _type_ = com.COMInterface


DirectSoundCreate = lib.DirectSoundCreate
DirectSoundCreate.argtypes = [
 com.LPGUID, ctypes.POINTER(IDirectSound), ctypes.c_void_p]
DSCAPS_PRIMARYMONO = 1
DSCAPS_PRIMARYSTEREO = 2
DSCAPS_PRIMARY8BIT = 4
DSCAPS_PRIMARY16BIT = 8
DSCAPS_CONTINUOUSRATE = 16
DSCAPS_EMULDRIVER = 32
DSCAPS_CERTIFIED = 64
DSCAPS_SECONDARYMONO = 256
DSCAPS_SECONDARYSTEREO = 512
DSCAPS_SECONDARY8BIT = 1024
DSCAPS_SECONDARY16BIT = 2048
DSSCL_NORMAL = 1
DSSCL_PRIORITY = 2
DSSCL_EXCLUSIVE = 3
DSSCL_WRITEPRIMARY = 4
DSSPEAKER_DIRECTOUT = 0
DSSPEAKER_HEADPHONE = 1
DSSPEAKER_MONO = 2
DSSPEAKER_QUAD = 3
DSSPEAKER_STEREO = 4
DSSPEAKER_SURROUND = 5
DSSPEAKER_5POINT1 = 6
DSSPEAKER_7POINT1 = 7
DSSPEAKER_GEOMETRY_MIN = 5
DSSPEAKER_GEOMETRY_NARROW = 10
DSSPEAKER_GEOMETRY_WIDE = 20
DSSPEAKER_GEOMETRY_MAX = 180
DSBCAPS_PRIMARYBUFFER = 1
DSBCAPS_STATIC = 2
DSBCAPS_LOCHARDWARE = 4
DSBCAPS_LOCSOFTWARE = 8
DSBCAPS_CTRL3D = 16
DSBCAPS_CTRLFREQUENCY = 32
DSBCAPS_CTRLPAN = 64
DSBCAPS_CTRLVOLUME = 128
DSBCAPS_CTRLPOSITIONNOTIFY = 256
DSBCAPS_CTRLFX = 512
DSBCAPS_STICKYFOCUS = 16384
DSBCAPS_GLOBALFOCUS = 32768
DSBCAPS_GETCURRENTPOSITION2 = 65536
DSBCAPS_MUTE3DATMAXDISTANCE = 131072
DSBCAPS_LOCDEFER = 262144
DSBPLAY_LOOPING = 1
DSBPLAY_LOCHARDWARE = 2
DSBPLAY_LOCSOFTWARE = 4
DSBPLAY_TERMINATEBY_TIME = 8
DSBPLAY_TERMINATEBY_DISTANCE = 16
DSBPLAY_TERMINATEBY_PRIORITY = 32
DSBSTATUS_PLAYING = 1
DSBSTATUS_BUFFERLOST = 2
DSBSTATUS_LOOPING = 4
DSBSTATUS_LOCHARDWARE = 8
DSBSTATUS_LOCSOFTWARE = 16
DSBSTATUS_TERMINATED = 32
DSBLOCK_FROMWRITECURSOR = 1
DSBLOCK_ENTIREBUFFER = 2
DSBFREQUENCY_MIN = 100
DSBFREQUENCY_MAX = 100000
DSBFREQUENCY_ORIGINAL = 0
DSBPAN_LEFT = -10000
DSBPAN_CENTER = 0
DSBPAN_RIGHT = 10000
DSBVOLUME_MIN = -10000
DSBVOLUME_MAX = 0
DSBSIZE_MIN = 4
DSBSIZE_MAX = 268435455
DSBSIZE_FX_MIN = 150
DS3DMODE_NORMAL = 0
DS3DMODE_HEADRELATIVE = 1
DS3DMODE_DISABLE = 2
DS3D_IMMEDIATE = 0
DS3D_DEFERRED = 1
DS3D_MINDISTANCEFACTOR = -1000000.0
DS3D_MAXDISTANCEFACTOR = 1000000.0
DS3D_DEFAULTDISTANCEFACTOR = 1.0
DS3D_MINROLLOFFFACTOR = 0.0
DS3D_MAXROLLOFFFACTOR = 10.0
DS3D_DEFAULTROLLOFFFACTOR = 1.0
DS3D_MINDOPPLERFACTOR = 0.0
DS3D_MAXDOPPLERFACTOR = 10.0
DS3D_DEFAULTDOPPLERFACTOR = 1.0
DS3D_DEFAULTMINDISTANCE = 1.0
DS3D_DEFAULTMAXDISTANCE = 1000000000.0
DS3D_MINCONEANGLE = 0
DS3D_MAXCONEANGLE = 360
DS3D_DEFAULTCONEANGLE = 360
DS3D_DEFAULTCONEOUTSIDEVOLUME = DSBVOLUME_MAX
DS_OK = 0
DSERR_OUTOFMEMORY = 7
DSERR_NOINTERFACE = 430
DS_NO_VIRTUALIZATION = 142082058
DS_INCOMPLETE = 142082068
DSERR_UNSUPPORTED = 2147500033
DSERR_GENERIC = 2147500037
DSERR_ACCESSDENIED = 2147942405
DSERR_INVALIDPARAM = 2147942487
DSERR_ALLOCATED = 2289565706
DSERR_CONTROLUNAVAIL = 2289565726
DSERR_INVALIDCALL = 2289565746
DSERR_PRIOLEVELNEEDED = 2289565766
DSERR_BADFORMAT = 2289565796
DSERR_NODRIVER = 2289565816
DSERR_ALREADYINITIALIZED = 2289565826
DSERR_BUFFERLOST = 2289565846
DSERR_OTHERAPPHASPRIO = 2289565856
DSERR_UNINITALIZED = 2289565866
DSERR_BUFFERTOOSMALL = 2289569972
DSERR_DS8_REQUIRED = 2289569982
DSERR_SENDLOOP = 2289569992
DSERR_BADSENDBUFFERGUID = 2289570002
DSERR_FXUNAVAILABLE = 2289570012
DSERR_OBJECTNOTFOUND = 2289570145
DSBSTATUS_PLAYING = 1
DSBSTATUS_BUFFERLOST = 2
DSBSTATUS_LOOPING = 4
