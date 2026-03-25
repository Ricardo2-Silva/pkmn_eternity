# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\input\darwin_hid.py
import sys
from ctypes import CFUNCTYPE, byref, c_void_p, c_int, c_ubyte, c_bool, c_uint32, c_uint64
from .base import Device, AbsoluteAxis, RelativeAxis, Button
from .base import Joystick, AppleRemote
from pyglet.libs.darwin.cocoapy import CFSTR, CFIndex, CFTypeID, known_cftypes
from pyglet.libs.darwin.cocoapy import kCFRunLoopDefaultMode, CFAllocatorRef, cf
from pyglet.libs.darwin.cocoapy import cfset_to_set, cftype_to_value, cfarray_to_list
from pyglet.lib import load_library
__LP64__ = sys.maxsize > 4294967296
iokit = load_library(framework="IOKit")
kIOHIDOptionsTypeNone = 0
kIOHIDOptionsTypeSeizeDevice = 1
kIOHIDElementTypeInput_Misc = 1
kIOHIDElementTypeInput_Button = 2
kIOHIDElementTypeInput_Axis = 3
kIOHIDElementTypeInput_ScanCodes = 4
kIOHIDElementTypeOutput = 129
kIOHIDElementTypeFeature = 257
kIOHIDElementTypeCollection = 513
kHIDPage_GenericDesktop = 1
kHIDPage_Consumer = 12
kHIDUsage_GD_SystemSleep = 130
kHIDUsage_GD_SystemWakeUp = 131
kHIDUsage_GD_SystemAppMenu = 134
kHIDUsage_GD_SystemMenu = 137
kHIDUsage_GD_SystemMenuRight = 138
kHIDUsage_GD_SystemMenuLeft = 139
kHIDUsage_GD_SystemMenuUp = 140
kHIDUsage_GD_SystemMenuDown = 141
kHIDUsage_Csmr_Menu = 64
kHIDUsage_Csmr_FastForward = 179
kHIDUsage_Csmr_Rewind = 180
kHIDUsage_Csmr_Eject = 184
kHIDUsage_Csmr_Mute = 226
kHIDUsage_Csmr_VolumeIncrement = 233
kHIDUsage_Csmr_VolumeDecrement = 234
IOReturn = c_int
IOOptionBits = c_uint32
IOHIDElementType = c_int
IOHIDElementCollectionType = c_int
if __LP64__:
    IOHIDElementCookie = c_uint32
else:
    IOHIDElementCookie = c_void_p
iokit.IOHIDDeviceClose.restype = IOReturn
iokit.IOHIDDeviceClose.argtypes = [c_void_p, IOOptionBits]
iokit.IOHIDDeviceConformsTo.restype = c_ubyte
iokit.IOHIDDeviceConformsTo.argtypes = [c_void_p, c_uint32, c_uint32]
iokit.IOHIDDeviceCopyMatchingElements.restype = c_void_p
iokit.IOHIDDeviceCopyMatchingElements.argtypes = [c_void_p, c_void_p, IOOptionBits]
iokit.IOHIDDeviceGetProperty.restype = c_void_p
iokit.IOHIDDeviceGetProperty.argtypes = [c_void_p, c_void_p]
iokit.IOHIDDeviceGetTypeID.restype = CFTypeID
iokit.IOHIDDeviceGetTypeID.argtypes = []
iokit.IOHIDDeviceGetValue.restype = IOReturn
iokit.IOHIDDeviceGetValue.argtypes = [c_void_p, c_void_p, c_void_p]
iokit.IOHIDDeviceOpen.restype = IOReturn
iokit.IOHIDDeviceOpen.argtypes = [c_void_p, IOOptionBits]
iokit.IOHIDDeviceRegisterInputValueCallback.restype = None
iokit.IOHIDDeviceRegisterInputValueCallback.argtypes = [c_void_p, c_void_p, c_void_p]
iokit.IOHIDDeviceRegisterRemovalCallback.restype = None
iokit.IOHIDDeviceRegisterRemovalCallback.argtypes = [c_void_p, c_void_p, c_void_p]
iokit.IOHIDDeviceScheduleWithRunLoop.restype = None
iokit.IOHIDDeviceScheduleWithRunLoop.argtypes = [c_void_p, c_void_p, c_void_p]
iokit.IOHIDDeviceUnscheduleFromRunLoop.restype = None
iokit.IOHIDDeviceUnscheduleFromRunLoop.argtypes = [c_void_p, c_void_p, c_void_p]
iokit.IOHIDElementGetCollectionType.restype = IOHIDElementCollectionType
iokit.IOHIDElementGetCollectionType.argtypes = [c_void_p]
iokit.IOHIDElementGetCookie.restype = IOHIDElementCookie
iokit.IOHIDElementGetCookie.argtypes = [c_void_p]
iokit.IOHIDElementGetLogicalMax.restype = CFIndex
iokit.IOHIDElementGetLogicalMax.argtypes = [c_void_p]
iokit.IOHIDElementGetLogicalMin.restype = CFIndex
iokit.IOHIDElementGetLogicalMin.argtypes = [c_void_p]
iokit.IOHIDElementGetName.restype = c_void_p
iokit.IOHIDElementGetName.argtypes = [c_void_p]
iokit.IOHIDElementGetPhysicalMax.restype = CFIndex
iokit.IOHIDElementGetPhysicalMax.argtypes = [c_void_p]
iokit.IOHIDElementGetPhysicalMin.restype = CFIndex
iokit.IOHIDElementGetPhysicalMin.argtypes = [c_void_p]
iokit.IOHIDElementGetReportCount.restype = c_uint32
iokit.IOHIDElementGetReportCount.argtypes = [c_void_p]
iokit.IOHIDElementGetReportID.restype = c_uint32
iokit.IOHIDElementGetReportID.argtypes = [c_void_p]
iokit.IOHIDElementGetReportSize.restype = c_uint32
iokit.IOHIDElementGetReportSize.argtypes = [c_void_p]
iokit.IOHIDElementGetType.restype = IOHIDElementType
iokit.IOHIDElementGetType.argtypes = [c_void_p]
iokit.IOHIDElementGetTypeID.restype = CFTypeID
iokit.IOHIDElementGetTypeID.argtypes = []
iokit.IOHIDElementGetUnit.restype = c_uint32
iokit.IOHIDElementGetUnit.argtypes = [c_void_p]
iokit.IOHIDElementGetUnitExponent.restype = c_uint32
iokit.IOHIDElementGetUnitExponent.argtypes = [c_void_p]
iokit.IOHIDElementGetUsage.restype = c_uint32
iokit.IOHIDElementGetUsage.argtypes = [c_void_p]
iokit.IOHIDElementGetUsagePage.restype = c_uint32
iokit.IOHIDElementGetUsagePage.argtypes = [c_void_p]
iokit.IOHIDElementHasNullState.restype = c_bool
iokit.IOHIDElementHasNullState.argtypes = [c_void_p]
iokit.IOHIDElementHasPreferredState.restype = c_bool
iokit.IOHIDElementHasPreferredState.argtypes = [c_void_p]
iokit.IOHIDElementIsArray.restype = c_bool
iokit.IOHIDElementIsArray.argtypes = [c_void_p]
iokit.IOHIDElementIsNonLinear.restype = c_bool
iokit.IOHIDElementIsNonLinear.argtypes = [c_void_p]
iokit.IOHIDElementIsRelative.restype = c_bool
iokit.IOHIDElementIsRelative.argtypes = [c_void_p]
iokit.IOHIDElementIsVirtual.restype = c_bool
iokit.IOHIDElementIsVirtual.argtypes = [c_void_p]
iokit.IOHIDElementIsWrapping.restype = c_bool
iokit.IOHIDElementIsWrapping.argtypes = [c_void_p]
iokit.IOHIDManagerCreate.restype = c_void_p
iokit.IOHIDManagerCreate.argtypes = [CFAllocatorRef, IOOptionBits]
iokit.IOHIDManagerCopyDevices.restype = c_void_p
iokit.IOHIDManagerCopyDevices.argtypes = [c_void_p]
iokit.IOHIDManagerGetTypeID.restype = CFTypeID
iokit.IOHIDManagerGetTypeID.argtypes = []
iokit.IOHIDManagerRegisterDeviceMatchingCallback.restype = None
iokit.IOHIDManagerRegisterDeviceMatchingCallback.argtypes = [c_void_p, c_void_p, c_void_p]
iokit.IOHIDManagerScheduleWithRunLoop.restype = c_void_p
iokit.IOHIDManagerScheduleWithRunLoop.argtypes = [c_void_p, c_void_p, c_void_p]
iokit.IOHIDManagerSetDeviceMatching.restype = None
iokit.IOHIDManagerSetDeviceMatching.argtypes = [c_void_p, c_void_p]
iokit.IOHIDValueGetElement.restype = c_void_p
iokit.IOHIDValueGetElement.argtypes = [c_void_p]
iokit.IOHIDValueGetIntegerValue.restype = CFIndex
iokit.IOHIDValueGetIntegerValue.argtypes = [c_void_p]
iokit.IOHIDValueGetLength.restype = CFIndex
iokit.IOHIDValueGetLength.argtypes = [c_void_p]
iokit.IOHIDValueGetTimeStamp.restype = c_uint64
iokit.IOHIDValueGetTimeStamp.argtypes = [c_void_p]
iokit.IOHIDValueGetTypeID.restype = CFTypeID
iokit.IOHIDValueGetTypeID.argtypes = []
HIDManagerCallback = CFUNCTYPE(None, c_void_p, c_int, c_void_p, c_void_p)
HIDDeviceCallback = CFUNCTYPE(None, c_void_p, c_int, c_void_p)
HIDDeviceValueCallback = CFUNCTYPE(None, c_void_p, c_int, c_void_p, c_void_p)
_device_lookup = {}
_element_lookup = {}

class HIDValue:

    def __init__(self, valueRef):
        if not valueRef:
            raise AssertionError
        else:
            assert cf.CFGetTypeID(valueRef) == iokit.IOHIDValueGetTypeID()
            self.valueRef = valueRef
            self.timestamp = iokit.IOHIDValueGetTimeStamp(valueRef)
            self.length = iokit.IOHIDValueGetLength(valueRef)
            if self.length <= 4:
                self.intvalue = iokit.IOHIDValueGetIntegerValue(valueRef)
            else:
                self.intvalue = None
        elementRef = c_void_p(iokit.IOHIDValueGetElement(valueRef))
        self.element = HIDDeviceElement.get_element(elementRef)


class HIDDevice:

    @classmethod
    def get_device(cls, deviceRef):
        if deviceRef.value in _device_lookup:
            return _device_lookup[deviceRef.value]
        else:
            device = HIDDevice(deviceRef)
            return device

    def __init__(self, deviceRef):
        if not deviceRef:
            raise AssertionError
        elif not cf.CFGetTypeID(deviceRef) == iokit.IOHIDDeviceGetTypeID():
            raise AssertionError
        _device_lookup[deviceRef.value] = self
        self.deviceRef = deviceRef
        self.transport = self.get_property("Transport")
        self.vendorID = self.get_property("VendorID")
        self.vendorIDSource = self.get_property("VendorIDSource")
        self.productID = self.get_property("ProductID")
        self.versionNumber = self.get_property("VersionNumber")
        self.manufacturer = self.get_property("Manufacturer")
        self.product = self.get_property("Product")
        self.serialNumber = self.get_property("SerialNumber")
        self.locationID = self.get_property("LocationID")
        self.primaryUsage = self.get_property("PrimaryUsage")
        self.primaryUsagePage = self.get_property("PrimaryUsagePage")
        self.elements = self._get_elements()
        self.value_observers = set()
        self.removal_observers = set()
        self.removal_callback = self._register_removal_callback()
        self.value_callback = self._register_input_value_callback()

    def dump_info(self):
        for x in ('manufacturer', 'product', 'transport', 'vendorID', 'vendorIDSource',
                  'productID', 'versionNumber', 'serialNumber', 'locationID', 'primaryUsage',
                  'primaryUsagePage'):
            value = getattr(self, x)
            print(x + ":", value)

    def unique_identifier(self):
        return (
         self.manufacturer, self.product, self.vendorID, self.productID,
         self.versionNumber, self.primaryUsage, self.primaryUsagePage)

    def get_property(self, name):
        cfname = CFSTR(name)
        cfvalue = c_void_p(iokit.IOHIDDeviceGetProperty(self.deviceRef, cfname))
        cf.CFRelease(cfname)
        return cftype_to_value(cfvalue)

    def open(self, exclusive_mode=False):
        if exclusive_mode:
            options = kIOHIDOptionsTypeSeizeDevice
        else:
            options = kIOHIDOptionsTypeNone
        return bool(iokit.IOHIDDeviceOpen(self.deviceRef, options))

    def close(self):
        return bool(iokit.IOHIDDeviceClose(self.deviceRef, kIOHIDOptionsTypeNone))

    def schedule_with_run_loop(self):
        iokit.IOHIDDeviceScheduleWithRunLoop(self.deviceRef, c_void_p(cf.CFRunLoopGetCurrent()), kCFRunLoopDefaultMode)

    def unschedule_from_run_loop(self):
        iokit.IOHIDDeviceUnscheduleFromRunLoop(self.deviceRef, c_void_p(cf.CFRunLoopGetCurrent()), kCFRunLoopDefaultMode)

    def _get_elements(self):
        cfarray = c_void_p(iokit.IOHIDDeviceCopyMatchingElements(self.deviceRef, None, 0))
        if not cfarray:
            return []
        else:
            elements = cfarray_to_list(cfarray)
            cf.CFRelease(cfarray)
            return elements

    def conforms_to(self, page, usage):
        return bool(iokit.IOHIDDeviceConformsTo(self.deviceRef, page, usage))

    def is_pointer(self):
        return self.conforms_to(1, 1)

    def is_mouse(self):
        return self.conforms_to(1, 2)

    def is_joystick(self):
        return self.conforms_to(1, 4)

    def is_gamepad(self):
        return self.conforms_to(1, 5)

    def is_keyboard(self):
        return self.conforms_to(1, 6)

    def is_keypad(self):
        return self.conforms_to(1, 7)

    def is_multi_axis(self):
        return self.conforms_to(1, 8)

    def py_removal_callback(self, context, result, sender):
        self = _device_lookup[sender]
        for x in self.removal_observers:
            if hasattr(x, "device_removed"):
                x.device_removed(self)

        del _device_lookup[sender]
        to_remove = [k for k, v in _element_lookup.items() if v in self.elements]
        for key in to_remove:
            del _element_lookup[key]

    def _register_removal_callback(self):
        removal_callback = HIDDeviceCallback(self.py_removal_callback)
        iokit.IOHIDDeviceRegisterRemovalCallback(self.deviceRef, removal_callback, None)
        return removal_callback

    def add_removal_observer(self, observer):
        self.removal_observers.add(observer)

    def py_value_callback(self, context, result, sender, value):
        v = HIDValue(c_void_p(value))
        for x in self.value_observers:
            if hasattr(x, "device_value_changed"):
                x.device_value_changed(self, v)

    def _register_input_value_callback(self):
        value_callback = HIDDeviceValueCallback(self.py_value_callback)
        iokit.IOHIDDeviceRegisterInputValueCallback(self.deviceRef, value_callback, None)
        return value_callback

    def add_value_observer(self, observer):
        self.value_observers.add(observer)

    def get_value(self, element):
        valueRef = c_void_p()
        iokit.IOHIDDeviceGetValue(self.deviceRef, element.elementRef, byref(valueRef))
        if valueRef:
            return HIDValue(valueRef)
        else:
            return


class HIDDeviceElement:

    @classmethod
    def get_element(cls, elementRef):
        if elementRef.value in _element_lookup:
            return _element_lookup[elementRef.value]
        else:
            element = HIDDeviceElement(elementRef)
            return element

    def __init__(self, elementRef):
        if not elementRef:
            raise AssertionError
        else:
            assert cf.CFGetTypeID(elementRef) == iokit.IOHIDElementGetTypeID()
            _element_lookup[elementRef.value] = self
            self.elementRef = elementRef
            self.cookie = iokit.IOHIDElementGetCookie(elementRef)
            self.type = iokit.IOHIDElementGetType(elementRef)
            if self.type == kIOHIDElementTypeCollection:
                self.collectionType = iokit.IOHIDElementGetCollectionType(elementRef)
            else:
                self.collectionType = None
        self.usagePage = iokit.IOHIDElementGetUsagePage(elementRef)
        self.usage = iokit.IOHIDElementGetUsage(elementRef)
        self.isVirtual = bool(iokit.IOHIDElementIsVirtual(elementRef))
        self.isRelative = bool(iokit.IOHIDElementIsRelative(elementRef))
        self.isWrapping = bool(iokit.IOHIDElementIsWrapping(elementRef))
        self.isArray = bool(iokit.IOHIDElementIsArray(elementRef))
        self.isNonLinear = bool(iokit.IOHIDElementIsNonLinear(elementRef))
        self.hasPreferredState = bool(iokit.IOHIDElementHasPreferredState(elementRef))
        self.hasNullState = bool(iokit.IOHIDElementHasNullState(elementRef))
        self.name = cftype_to_value(iokit.IOHIDElementGetName(elementRef))
        self.reportID = iokit.IOHIDElementGetReportID(elementRef)
        self.reportSize = iokit.IOHIDElementGetReportSize(elementRef)
        self.reportCount = iokit.IOHIDElementGetReportCount(elementRef)
        self.unit = iokit.IOHIDElementGetUnit(elementRef)
        self.unitExponent = iokit.IOHIDElementGetUnitExponent(elementRef)
        self.logicalMin = iokit.IOHIDElementGetLogicalMin(elementRef)
        self.logicalMax = iokit.IOHIDElementGetLogicalMax(elementRef)
        self.physicalMin = iokit.IOHIDElementGetPhysicalMin(elementRef)
        self.physicalMax = iokit.IOHIDElementGetPhysicalMax(elementRef)


class HIDManager:

    def __init__(self):
        self.managerRef = c_void_p(iokit.IOHIDManagerCreate(None, kIOHIDOptionsTypeNone))
        if not self.managerRef:
            raise AssertionError
        elif not cf.CFGetTypeID(self.managerRef) == iokit.IOHIDManagerGetTypeID():
            raise AssertionError
        self.schedule_with_run_loop()
        self.matching_observers = set()
        self.matching_callback = self._register_matching_callback()
        self.devices = self._get_devices()

    def _get_devices(self):
        try:
            iokit.IOHIDManagerSetDeviceMatching(self.managerRef, None)
            cfset = c_void_p(iokit.IOHIDManagerCopyDevices(self.managerRef))
            devices = cfset_to_set(cfset)
            cf.CFRelease(cfset)
        except:
            return set()
        else:
            return devices

    def open(self):
        iokit.IOHIDManagerOpen(self.managerRef, kIOHIDOptionsTypeNone)

    def close(self):
        iokit.IOHIDManagerClose(self.managerRef, kIOHIDOptionsTypeNone)

    def schedule_with_run_loop(self):
        iokit.IOHIDManagerScheduleWithRunLoop(self.managerRef, c_void_p(cf.CFRunLoopGetCurrent()), kCFRunLoopDefaultMode)

    def unschedule_from_run_loop(self):
        iokit.IOHIDManagerUnscheduleFromRunLoop(self.managerRef, c_void_p(cf.CFRunLoopGetCurrent()), kCFRunLoopDefaultMode)

    def _py_matching_callback(self, context, result, sender, device):
        d = HIDDevice.get_device(c_void_p(device))
        if d not in self.devices:
            self.devices.add(d)
            for x in self.matching_observers:
                if hasattr(x, "device_discovered"):
                    x.device_discovered(d)

    def _register_matching_callback(self):
        matching_callback = HIDManagerCallback(self._py_matching_callback)
        iokit.IOHIDManagerRegisterDeviceMatchingCallback(self.managerRef, matching_callback, None)
        return matching_callback


known_cftypes[iokit.IOHIDDeviceGetTypeID()] = HIDDevice.get_device
known_cftypes[iokit.IOHIDElementGetTypeID()] = HIDDeviceElement.get_element
_axis_names = {
 (1, 48): "x", 
 (1, 49): "y", 
 (1, 50): "z", 
 (1, 51): "rx", 
 (1, 52): "ry", 
 (1, 53): "rz", 
 (1, 56): "wheel", 
 (1, 57): "hat"}
_button_names = {(
 kHIDPage_GenericDesktop, kHIDUsage_GD_SystemSleep): "sleep", 
 (
 kHIDPage_GenericDesktop, kHIDUsage_GD_SystemWakeUp): "wakeup", 
 (
 kHIDPage_GenericDesktop, kHIDUsage_GD_SystemAppMenu): "menu", 
 (
 kHIDPage_GenericDesktop, kHIDUsage_GD_SystemMenu): "select", 
 (
 kHIDPage_GenericDesktop, kHIDUsage_GD_SystemMenuRight): "right", 
 (
 kHIDPage_GenericDesktop, kHIDUsage_GD_SystemMenuLeft): "left", 
 (
 kHIDPage_GenericDesktop, kHIDUsage_GD_SystemMenuUp): "up", 
 (
 kHIDPage_GenericDesktop, kHIDUsage_GD_SystemMenuDown): "down", 
 (
 kHIDPage_Consumer, kHIDUsage_Csmr_FastForward): "right_hold", 
 (
 kHIDPage_Consumer, kHIDUsage_Csmr_Rewind): "left_hold", 
 (
 kHIDPage_Consumer, kHIDUsage_Csmr_Menu): "menu_hold", 
 (65281, 35): "select_hold", 
 (
 kHIDPage_Consumer, kHIDUsage_Csmr_Eject): "eject", 
 (
 kHIDPage_Consumer, kHIDUsage_Csmr_Mute): "mute", 
 (
 kHIDPage_Consumer, kHIDUsage_Csmr_VolumeIncrement): "volume_up", 
 (
 kHIDPage_Consumer, kHIDUsage_Csmr_VolumeDecrement): "volume_down"}

class PygletDevice(Device):

    def __init__(self, display, device, manager):
        super(PygletDevice, self).__init__(display, device.product)
        self.device = device
        self.device_identifier = self.device.unique_identifier()
        self.device.add_value_observer(self)
        self.device.add_removal_observer(self)
        manager.matching_observers.add(self)
        self._create_controls()
        self._is_open = False
        self._is_exclusive = False

    def open(self, window=None, exclusive=False):
        super(PygletDevice, self).open(window, exclusive)
        self.device.open(exclusive)
        self.device.schedule_with_run_loop()
        self._is_open = True
        self._is_exclusive = exclusive
        self._set_initial_control_values()

    def close(self):
        super(PygletDevice, self).close()
        self.device.close()
        self._is_open = False

    def get_controls(self):
        return list(self._controls.values())

    def device_removed(self, hid_device):
        self.device = None

    def device_discovered(self, hid_device):
        if not self.device:
            if self.device_identifier == hid_device.unique_identifier():
                self.device = hid_device
                self.device.add_value_observer(self)
                self.device.add_removal_observer(self)
                if self._is_open:
                    self.device.open(self._is_exclusive)
                    self.device.schedule_with_run_loop()

    def device_value_changed(self, hid_device, hid_value):
        control = self._controls[hid_value.element.cookie]
        control.value = hid_value.intvalue

    def _create_controls(self):
        self._controls = {}
        for element in self.device.elements:
            raw_name = element.name or "0x%x:%x" % (element.usagePage, element.usage)
            if element.type in (kIOHIDElementTypeInput_Misc, kIOHIDElementTypeInput_Axis):
                name = _axis_names.get((element.usagePage, element.usage))
                if element.isRelative:
                    control = RelativeAxis(name, raw_name)
                else:
                    control = AbsoluteAxis(name, element.logicalMin, element.logicalMax, raw_name)
            elif element.type == kIOHIDElementTypeInput_Button:
                name = _button_names.get((element.usagePage, element.usage))
                control = Button(name, raw_name)
            else:
                continue
            control._cookie = element.cookie
            self._controls[control._cookie] = control

    def _set_initial_control_values(self):
        for element in self.device.elements:
            if element.cookie in self._controls:
                control = self._controls[element.cookie]
                hid_value = self.device.get_value(element)
                if hid_value:
                    control.value = hid_value.intvalue


_manager = HIDManager()

def get_devices(display=None):
    return [PygletDevice(display, device, _manager) for device in _manager.devices]


def get_joysticks(display=None):
    return [Joystick(PygletDevice(display, device, _manager)) for device in _manager.devices if device.is_joystick() or device.is_gamepad() or device.is_multi_axis()]


def get_apple_remote(display=None):
    for device in _manager.devices:
        if device.product == "Apple IR":
            return AppleRemote(PygletDevice(display, device, _manager))
