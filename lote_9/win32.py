# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\media\devices\win32.py
import pyglet
from pyglet import com
from pyglet.libs.win32 import _ole32 as ole32
from pyglet.libs.win32.constants import CLSCTX_INPROC_SERVER
from pyglet.libs.win32.types import *
from pyglet.media.devices import base
from pyglet.util import debug_print
_debug = debug_print("debug_media")
EDataFlow = UINT
eRender = 0
eCapture = 1
eAll = 2
EDataFlow_enum_count = 3
ERole = UINT
eConsole = 0
eMultimedia = 1
eCommunications = 2
ERole_enum_count = 3
DEVICE_STATE_ACTIVE = 1
DEVICE_STATE_DISABLED = 2
DEVICE_STATE_NOTPRESENT = 4
DEVICE_STATE_UNPLUGGED = 8
DEVICE_STATEMASK_ALL = 15
STGM_READ = 0
STGM_WRITE = 1
STGM_READWRITE = 2
VT_LPWSTR = 31

class PROPERTYKEY(ctypes.Structure):
    _fields_ = [
     (
      "fmtid", com.GUID),
     (
      "pid", DWORD)]

    def __repr__(self):
        return "PROPERTYKEY({}, pid={})".format(self.fmtid, self.pid)


REFPROPERTYKEY = PROPERTYKEY
PKEY_Device_FriendlyName = PROPERTYKEY(com.GUID(2757502286, 57116, 20221, 128, 32, 103, 209, 70, 168, 80, 224), 14)
PKEY_Device_DeviceDesc = PROPERTYKEY(com.GUID(2757502286, 57116, 20221, 128, 32, 103, 209, 70, 168, 80, 224), 2)
PKEY_DeviceInterface_FriendlyName = PROPERTYKEY(com.GUID(40784238, 47124, 16715, 131, 205, 133, 109, 111, 239, 72, 34), 2)

class IPropertyStore(com.pIUnknown):
    _methods_ = [
     (
      "GetCount",
      com.STDMETHOD(POINTER(DWORD))),
     (
      "GetAt",
      com.STDMETHOD(DWORD, POINTER(PROPERTYKEY))),
     (
      "GetValue",
      com.STDMETHOD(REFPROPERTYKEY, POINTER(PROPVARIANT))),
     (
      "SetValue",
      com.STDMETHOD()),
     (
      "Commit",
      com.STDMETHOD())]


CLSID_MMDeviceEnumerator = com.GUID(3168666517, 58671, 18044, 142, 61, 196, 87, 146, 145, 105, 46)
IID_IMMDeviceEnumerator = com.GUID(2841011410, 38420, 20277, 167, 70, 222, 141, 182, 54, 23, 230)

class IMMNotificationClient(com.IUnknown):
    _methods_ = [
     (
      "OnDeviceStateChanged",
      com.METHOD(ctypes.c_void_p, ctypes.c_void_p, LPCWSTR, DWORD)),
     (
      "OnDeviceAdded",
      com.METHOD(ctypes.c_void_p, ctypes.c_void_p, LPCWSTR)),
     (
      "OnDeviceRemoved",
      com.METHOD(ctypes.c_void_p, ctypes.c_void_p, LPCWSTR)),
     (
      "OnDefaultDeviceChanged",
      com.METHOD(ctypes.c_void_p, ctypes.c_void_p, EDataFlow, ERole, LPCWSTR)),
     (
      "OnPropertyValueChanged",
      com.METHOD(ctypes.c_void_p, ctypes.c_void_p, LPCWSTR, PROPERTYKEY))]


class AudioNotificationCB(com.COMObject):
    _interfaces_ = [
     IMMNotificationClient]

    def __init__(self, audio_devices):
        super().__init__()
        self.audio_devices = audio_devices
        self._lost = False

    def OnDeviceStateChanged(self, this, pwstrDeviceId, dwNewState):
        device = self.audio_devices.get_cached_device(pwstrDeviceId)
        old_state = device.state
        assert _debug("Audio device {} changed state. From state: {} to state: {}".format(device.name, old_state, dwNewState))
        device.state = dwNewState
        self.audio_devices.dispatch_event("on_device_state_changed", device, old_state, dwNewState)

    def OnDeviceAdded(self, this, pwstrDeviceId):
        assert _debug("Audio device was added {}".format(pwstrDeviceId))
        self.audio_devices.dispatch_event("on_device_added", pwstrDeviceId)

    def OnDeviceRemoved(self, this, pwstrDeviceId):
        assert _debug("Audio device was removed {}".format(pwstrDeviceId))
        self.audio_devices.dispatch_event("on_device_removed", pwstrDeviceId)

    def OnDefaultDeviceChanged(self, this, flow, role, pwstrDeviceId):
        if role == 0:
            if pwstrDeviceId is None:
                device = None
            else:
                device = self.audio_devices.get_cached_device(pwstrDeviceId)
            self.audio_devices.dispatch_event("on_default_changed", device)

    def OnPropertyValueChanged(self, this, pwstrDeviceId, key):
        return


class IMMDevice(com.pIUnknown):
    _methods_ = [
     (
      "Activate",
      com.STDMETHOD(com.REFIID, DWORD, POINTER(PROPVARIANT))),
     (
      "OpenPropertyStore",
      com.STDMETHOD(UINT, POINTER(IPropertyStore))),
     (
      "GetId",
      com.STDMETHOD(POINTER(LPWSTR))),
     (
      "GetState",
      com.STDMETHOD(POINTER(DWORD)))]


class IMMDeviceCollection(com.pIUnknown):
    _methods_ = [
     (
      "GetCount",
      com.STDMETHOD(POINTER(UINT))),
     (
      "Item",
      com.STDMETHOD(UINT, POINTER(IMMDevice)))]


class IMMDeviceEnumerator(com.pIUnknown):
    _methods_ = [
     (
      "EnumAudioEndpoints",
      com.STDMETHOD(EDataFlow, DWORD, c_void_p)),
     (
      "GetDefaultAudioEndpoint",
      com.STDMETHOD(EDataFlow, ERole, ctypes.POINTER(IMMDevice))),
     (
      "GetDevice",
      com.STDMETHOD(LPCWSTR, POINTER(IMMDevice))),
     (
      "RegisterEndpointNotificationCallback",
      com.STDMETHOD(POINTER(IMMNotificationClient))),
     (
      "UnregisterEndpointNotificationCallback",
      com.STDMETHOD())]


class Win32AudioDevice(base.AudioDevice):
    _platform_state = {DEVICE_STATE_ACTIVE: (base.DeviceState.ACTIVE), 
     DEVICE_STATE_DISABLED: (base.DeviceState.DISABLED), 
     DEVICE_STATE_NOTPRESENT: (base.DeviceState.MISSING), 
     DEVICE_STATE_UNPLUGGED: (base.DeviceState.UNPLUGGED)}
    _platform_flow = {eRender: (base.DeviceFlow.OUTPUT), 
     eCapture: (base.DeviceFlow.INPUT), 
     eAll: (base.DeviceFlow.INPUT_OUTPUT)}


class Win32AudioDeviceManager(base.AbstractAudioDeviceManager):

    def __init__(self):
        self._device_enum = IMMDeviceEnumerator()
        ole32.CoCreateInstance(CLSID_MMDeviceEnumerator, None, CLSCTX_INPROC_SERVER, IID_IMMDeviceEnumerator, byref(self._device_enum))
        self.devices = self._query_all_devices()
        super().__init__()
        self._callback = AudioNotificationCB(self)
        self._device_enum.RegisterEndpointNotificationCallback(self._callback)

    def get_default_output(self):
        """Attempts to retrieve a default audio output for the system. Returns None if no available devices found."""
        try:
            device = IMMDevice()
            self._device_enum.GetDefaultAudioEndpoint(eRender, eConsole, byref(device))
            dev_id, name, desc, dev_state = self.get_device_info(device)
            device.Release()
            pid = self.get_cached_device(dev_id)
            pid.state = dev_state
            return pid
        except OSError:
            assert _debug("No default audio output was found.")
            return

    def get_default_input(self):
        """Attempts to retrieve a default audio input for the system. Returns None if no available devices found."""
        try:
            device = IMMDevice()
            self._device_enum.GetDefaultAudioEndpoint(eCapture, eConsole, byref(device))
            dev_id, name, desc, dev_state = self.get_device_info(device)
            device.Release()
            pid = self.get_cached_device(dev_id)
            pid.state = dev_state
            return pid
        except OSError:
            assert _debug("No default input output was found.")
            return

    def get_cached_device(self, dev_id):
        """Gets the cached devices, so we can reduce calls to COM and tell current state vs new states."""
        for device in self.devices:
            if device.id == dev_id:
                return device

        raise Exception("Attempted to get a device that does not exist.")

    def get_output_devices(self, state=DEVICE_STATE_ACTIVE):
        return [device for device in self.devices if device.state == state if device.flow == eRender]

    def get_input_devices(self, state=DEVICE_STATE_ACTIVE):
        return [device for device in self.devices if device.state == state if device.flow == eCapture]

    def get_all_devices(self):
        return self.devices

    def _query_all_devices(self):
        return self.get_devices(flow=eRender, state=DEVICE_STATEMASK_ALL) + self.get_devices(flow=eCapture, state=DEVICE_STATEMASK_ALL)

    def get_device_info(self, device):
        """Return the ID, Name, and Description of the Audio Device."""
        store = IPropertyStore()
        device.OpenPropertyStore(STGM_READ, byref(store))
        dev_id = LPWSTR()
        device.GetId(byref(dev_id))
        name = self.get_pkey_value(store, PKEY_Device_FriendlyName)
        description = self.get_pkey_value(store, PKEY_Device_DeviceDesc)
        state = DWORD()
        device.GetState(byref(state))
        store.Release()
        return (
         dev_id.value, name, description, state.value)

    def get_devices(self, flow=eRender, state=DEVICE_STATE_ACTIVE):
        """Get's all of the specified devices (by default, all output and active)."""
        collection = IMMDeviceCollection()
        self._device_enum.EnumAudioEndpoints(flow, state, byref(collection))
        count = UINT()
        collection.GetCount(byref(count))
        devices = []
        for i in range(count.value):
            dev_itf = IMMDevice()
            collection.Item(i, byref(dev_itf))
            dev_id, name, desc, dev_state = self.get_device_info(dev_itf)
            device = Win32AudioDevice(dev_id, name, desc, flow, dev_state)
            dev_itf.Release()
            devices.append(device)

        collection.Release()
        return devices

    @staticmethod
    def get_pkey_value(store, pkey):
        try:
            propvar = PROPVARIANT()
            store.GetValue(pkey, byref(propvar))
            value = propvar.pwszVal
            ole32.PropVariantClear(propvar)
        except Exception as err:
            value = "Unknown"

        return value
