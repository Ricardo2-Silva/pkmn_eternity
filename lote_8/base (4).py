# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\input\base.py
"""Interface classes for `pyglet.input`.

.. versionadded:: 1.2
"""
import sys
from pyglet.event import EventDispatcher
_is_pyglet_doc_run = hasattr(sys, "is_pyglet_doc_run") and sys.is_pyglet_doc_run

class DeviceException(Exception):
    return


class DeviceOpenException(DeviceException):
    return


class DeviceExclusiveException(DeviceException):
    return


class Device:
    __doc__ = "Input device.\n\n    :Ivariables:\n        display : `pyglet.canvas.Display`\n            Display this device is connected to.\n        name : str\n            Name of the device, as described by the device firmware.\n        manufacturer : str\n            Name of the device manufacturer, or ``None`` if the information is\n            not available.\n    "

    def __init__(self, display, name):
        self.display = display
        self.name = name
        self.manufacturer = None
        self.is_open = False

    def open(self, window=None, exclusive=False):
        """Open the device to begin receiving input from it.

        :Parameters:
            `window` : Window
                Optional window to associate with the device.  The behaviour
                of this parameter is device and operating system dependant.
                It can usually be omitted for most devices.
            `exclusive` : bool
                If ``True`` the device will be opened exclusively so that no
                other application can use it.  The method will raise
                `DeviceExclusiveException` if the device cannot be opened this
                way (for example, because another application has already
                opened it).
        """
        if self.is_open:
            raise DeviceOpenException("Device is already open.")
        self.is_open = True

    def close(self):
        """Close the device. """
        self.is_open = False

    def get_controls(self):
        """Get a list of controls provided by the device.

        :rtype: list of `Control`
        """
        raise NotImplementedError("abstract")

    def __repr__(self):
        return "%s(name=%s)" % (self.__class__.__name__, self.name)


class Control(EventDispatcher):
    __doc__ = "Single value input provided by a device.\n\n    A control's value can be queried when the device is open.  Event handlers\n    can be attached to the control to be called when the value changes.\n\n    The `min` and `max` properties are provided as advertised by the\n    device; in some cases the control's value will be outside this range.\n\n    :Ivariables:\n        `name` : str\n            Name of the control, or ``None`` if unknown\n        `raw_name` : str\n            Unmodified name of the control, as presented by the operating\n            system; or ``None`` if unknown.\n        `inverted` : bool\n            If ``True``, the value reported is actually inverted from what the\n            device reported; usually this is to provide consistency across\n            operating systems.\n    "

    def __init__(self, name, raw_name=None):
        self.name = name
        self.raw_name = raw_name
        self.inverted = False
        self._value = None

    @property
    def value(self):
        """Current value of the control.

        The range of the value is device-dependent; for absolute controls
        the range is given by ``min`` and ``max`` (however the value may exceed
        this range); for relative controls the range is undefined.

        :type: float
        """
        return self._value

    @value.setter
    def value(self, newvalue):
        if newvalue == self._value:
            return
        self._value = newvalue
        self.dispatch_event("on_change", newvalue)

    def __repr__(self):
        if self.name:
            return "%s(name=%s, raw_name=%s)" % (
             self.__class__.__name__, self.name, self.raw_name)
        else:
            return "%s(raw_name=%s)" % (self.__class__.__name__, self.raw_name)

    if _is_pyglet_doc_run:

        def on_change(self, value):
            """The value changed.

            :Parameters:
                `value` : float
                    Current value of the control.

            :event:
            """
            return


Control.register_event_type("on_change")

class RelativeAxis(Control):
    __doc__ = "An axis whose value represents a relative change from the previous\n    value.\n    "
    X = "x"
    Y = "y"
    Z = "z"
    RX = "rx"
    RY = "ry"
    RZ = "rz"
    WHEEL = "wheel"

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, newvalue):
        self._value = newvalue
        self.dispatch_event("on_change", newvalue)


class AbsoluteAxis(Control):
    __doc__ = "An axis whose value represents a physical measurement from the device.\n\n    The value is advertised to range over ``min`` and ``max``.\n\n    :Ivariables:\n        `min` : float\n            Minimum advertised value.\n        `max` : float \n            Maximum advertised value.\n    "
    X = "x"
    Y = "y"
    Z = "z"
    RX = "rx"
    RY = "ry"
    RZ = "rz"
    HAT = "hat"
    HAT_X = "hat_x"
    HAT_Y = "hat_y"

    def __init__(self, name, min, max, raw_name=None):
        super(AbsoluteAxis, self).__init__(name, raw_name)
        self.min = min
        self.max = max


class Button(Control):
    __doc__ = "A control whose value is boolean. "

    @property
    def value(self):
        return bool(self._value)

    @value.setter
    def value(self, newvalue):
        if newvalue == self._value:
            return
        else:
            self._value = newvalue
            self.dispatch_event("on_change", bool(newvalue))
            if newvalue:
                self.dispatch_event("on_press")
            else:
                self.dispatch_event("on_release")

    if _is_pyglet_doc_run:

        def on_press(self):
            """The button was pressed.

            :event:
            """
            return

        def on_release(self):
            """The button was released.

            :event:
            """
            return


Button.register_event_type("on_press")
Button.register_event_type("on_release")

class Joystick(EventDispatcher):
    __doc__ = "High-level interface for joystick-like devices.  This includes analogue\n    and digital joysticks, gamepads, game controllers, and possibly even\n    steering wheels and other input devices.  There is unfortunately no way to\n    distinguish between these different device types.\n\n    To use a joystick, first call `open`, then in your game loop examine\n    the values of `x`, `y`, and so on.  These values are normalized to the\n    range [-1.0, 1.0]. \n\n    To receive events when the value of an axis changes, attach an \n    on_joyaxis_motion event handler to the joystick.  The :py:class:`~pyglet.input.Joystick` instance,\n    axis name, and current value are passed as parameters to this event.\n\n    To handle button events, you should attach on_joybutton_press and \n    on_joy_button_release event handlers to the joystick.  Both the :py:class:`~pyglet.input.Joystick`\n    instance and the index of the changed button are passed as parameters to \n    these events.\n\n    Alternately, you may attach event handlers to each individual button in \n    `button_controls` to receive on_press or on_release events.\n    \n    To use the hat switch, attach an on_joyhat_motion event handler to the\n    joystick.  The handler will be called with both the hat_x and hat_y values\n    whenever the value of the hat switch changes.\n\n    The device name can be queried to get the name of the joystick.\n\n    :Ivariables:\n        `device` : `Device`\n            The underlying device used by this joystick interface.\n        `x` : float\n            Current X (horizontal) value ranging from -1.0 (left) to 1.0\n            (right).\n        `y` : float\n            Current y (vertical) value ranging from -1.0 (top) to 1.0\n            (bottom).\n        `z` : float\n            Current Z value ranging from -1.0 to 1.0.  On joysticks the Z\n            value is usually the throttle control.  On game controllers the Z\n            value is usually the secondary thumb vertical axis.\n        `rx` : float\n            Current rotational X value ranging from -1.0 to 1.0.\n        `ry` : float\n            Current rotational Y value ranging from -1.0 to 1.0.\n        `rz` : float\n            Current rotational Z value ranging from -1.0 to 1.0.  On joysticks\n            the RZ value is usually the twist of the stick.  On game\n            controllers the RZ value is usually the secondary thumb horizontal\n            axis.\n        `hat_x` : int\n            Current hat (POV) horizontal position; one of -1 (left), 0\n            (centered) or 1 (right).\n        `hat_y` : int\n            Current hat (POV) vertical position; one of -1 (bottom), 0\n            (centered) or 1 (top).\n        `buttons` : list of bool\n            List of boolean values representing current states of the buttons.\n            These are in order, so that button 1 has value at ``buttons[0]``,\n            and so on.\n        `x_control` : `AbsoluteAxis`\n            Underlying control for `x` value, or ``None`` if not available.\n        `y_control` : `AbsoluteAxis`\n            Underlying control for `y` value, or ``None`` if not available.\n        `z_control` : `AbsoluteAxis`\n            Underlying control for `z` value, or ``None`` if not available.\n        `rx_control` : `AbsoluteAxis`\n            Underlying control for `rx` value, or ``None`` if not available.\n        `ry_control` : `AbsoluteAxis`\n            Underlying control for `ry` value, or ``None`` if not available.\n        `rz_control` : `AbsoluteAxis`\n            Underlying control for `rz` value, or ``None`` if not available.\n        `hat_x_control` : `AbsoluteAxis`\n            Underlying control for `hat_x` value, or ``None`` if not available.\n        `hat_y_control` : `AbsoluteAxis`\n            Underlying control for `hat_y` value, or ``None`` if not available.\n        `button_controls` : list of `Button`\n            Underlying controls for `buttons` values.\n    "

    def __init__(self, device):
        self.device = device
        self.x = 0
        self.y = 0
        self.z = 0
        self.rx = 0
        self.ry = 0
        self.rz = 0
        self.hat_x = 0
        self.hat_y = 0
        self.buttons = []
        self.x_control = None
        self.y_control = None
        self.z_control = None
        self.rx_control = None
        self.ry_control = None
        self.rz_control = None
        self.hat_x_control = None
        self.hat_y_control = None
        self.button_controls = []

        def add_axis(control):
            name = control.name
            scale = 2.0 / (control.max - control.min)
            bias = -1.0 - control.min * scale
            if control.inverted:
                scale = -scale
                bias = -bias
            setattr(self, name + "_control", control)

            @control.event
            def on_change(value):
                normalized_value = value * scale + bias
                setattr(self, name, normalized_value)
                self.dispatch_event("on_joyaxis_motion", self, name, normalized_value)

        def add_button(control):
            i = len(self.buttons)
            self.buttons.append(False)
            self.button_controls.append(control)

            @control.event
            def on_change(value):
                self.buttons[i] = value

            @control.event
            def on_press():
                self.dispatch_event("on_joybutton_press", self, i)

            @control.event
            def on_release():
                self.dispatch_event("on_joybutton_release", self, i)

        def add_hat(control):
            self.hat_x_control = control
            self.hat_y_control = control

            @control.event
            def on_change(value):
                if value & 65535 == 65535:
                    self.hat_x = self.hat_y = 0
                else:
                    if control.max > 8:
                        value //= 4095
                    if 0 <= value < 8:
                        self.hat_x, self.hat_y = ((0, 1), (1, 1), (1, 0), (1, -1),
                                                  (0, -1), (-1, -1), (-1, 0), (-1, 1))[value]
                    else:
                        self.hat_x = self.hat_y = 0
                self.dispatch_event("on_joyhat_motion", self, self.hat_x, self.hat_y)

        for control in device.get_controls():
            if isinstance(control, AbsoluteAxis):
                if control.name in ('x', 'y', 'z', 'rx', 'ry', 'rz', 'hat_x', 'hat_y'):
                    add_axis(control)
                elif control.name == "hat":
                    add_hat(control)
                else:
                    if isinstance(control, Button):
                        add_button(control)

    def open(self, window=None, exclusive=False):
        """Open the joystick device.  See `Device.open`. """
        self.device.open(window, exclusive)

    def close(self):
        """Close the joystick device.  See `Device.close`. """
        self.device.close()

    def on_joyaxis_motion(self, joystick, axis, value):
        """The value of a joystick axis changed.

        :Parameters:
            `joystick` : `Joystick`
                The joystick device whose axis changed.
            `axis` : string
                The name of the axis that changed.
            `value` : float
                The current value of the axis, normalized to [-1, 1].
        """
        return

    def on_joybutton_press(self, joystick, button):
        """A button on the joystick was pressed.

        :Parameters:
            `joystick` : `Joystick`
                The joystick device whose button was pressed.
            `button` : int
                The index (in `button_controls`) of the button that was pressed.
        """
        return

    def on_joybutton_release(self, joystick, button):
        """A button on the joystick was released.

        :Parameters:
            `joystick` : `Joystick`
                The joystick device whose button was released.
            `button` : int
                The index (in `button_controls`) of the button that was released.
        """
        return

    def on_joyhat_motion(self, joystick, hat_x, hat_y):
        """The value of the joystick hat switch changed.

        :Parameters:
            `joystick` : `Joystick`
                The joystick device whose hat control changed.
            `hat_x` : int
                Current hat (POV) horizontal position; one of -1 (left), 0
                (centered) or 1 (right).
            `hat_y` : int
                Current hat (POV) vertical position; one of -1 (bottom), 0
                (centered) or 1 (top).
        """
        return


Joystick.register_event_type("on_joyaxis_motion")
Joystick.register_event_type("on_joybutton_press")
Joystick.register_event_type("on_joybutton_release")
Joystick.register_event_type("on_joyhat_motion")

class AppleRemote(EventDispatcher):
    __doc__ = "High-level interface for Apple remote control.\n\n    This interface provides access to the 6 button controls on the remote.\n    Pressing and holding certain buttons on the remote is interpreted as\n    a separate control.\n\n    :Ivariables:\n        `device` : `Device`\n            The underlying device used by this interface.\n        `left_control` : `Button`\n            Button control for the left (prev) button.\n        `left_hold_control` : `Button`\n            Button control for holding the left button (rewind).\n        `right_control` : `Button`\n            Button control for the right (next) button.\n        `right_hold_control` : `Button`\n            Button control for holding the right button (fast forward).\n        `up_control` : `Button`\n            Button control for the up (volume increase) button.\n        `down_control` : `Button`\n            Button control for the down (volume decrease) button.\n        `select_control` : `Button`\n            Button control for the select (play/pause) button.\n        `select_hold_control` : `Button`\n            Button control for holding the select button.\n        `menu_control` : `Button`\n            Button control for the menu button.\n        `menu_hold_control` : `Button`\n            Button control for holding the menu button.\n    "

    def __init__(self, device):

        def add_button(control):
            setattr(self, control.name + "_control", control)

            @control.event
            def on_press():
                self.dispatch_event("on_button_press", control.name)

            @control.event
            def on_release():
                self.dispatch_event("on_button_release", control.name)

        self.device = device
        for control in device.get_controls():
            if control.name in ('left', 'left_hold', 'right', 'right_hold', 'up', 'down',
                                'menu', 'select', 'menu_hold', 'select_hold'):
                add_button(control)

    def open(self, window=None, exclusive=False):
        """Open the device.  See `Device.open`. """
        self.device.open(window, exclusive)

    def close(self):
        """Close the device.  See `Device.close`. """
        self.device.close()

    def on_button_press(self, button):
        """A button on the remote was pressed.

        Only the 'up' and 'down' buttons will generate an event when the
        button is first pressed.  All other buttons on the remote will wait
        until the button is released and then send both the press and release
        events at the same time.

        :Parameters:
            `button` : unicode
                The name of the button that was pressed. The valid names are
                'up', 'down', 'left', 'right', 'left_hold', 'right_hold',
                'menu', 'menu_hold', 'select', and 'select_hold'
                
        :event:
        """
        return

    def on_button_release(self, button):
        """A button on the remote was released.

        The 'select_hold' and 'menu_hold' button release events are sent
        immediately after the corresponding press events regardless of
        whether or not the user has released the button.

        :Parameters:
            `button` : unicode
                The name of the button that was released. The valid names are
                'up', 'down', 'left', 'right', 'left_hold', 'right_hold',
                'menu', 'menu_hold', 'select', and 'select_hold'

        :event:
        """
        return


AppleRemote.register_event_type("on_button_press")
AppleRemote.register_event_type("on_button_release")

class Tablet:
    __doc__ = "High-level interface to tablet devices.\n\n    Unlike other devices, tablets must be opened for a specific window,\n    and cannot be opened exclusively.  The `open` method returns a\n    `TabletCanvas` object, which supports the events provided by the tablet.\n\n    Currently only one tablet device can be used, though it can be opened on\n    multiple windows.  If more than one tablet is connected, the behaviour is\n    undefined.\n    "

    def open(self, window):
        """Open a tablet device for a window.

        :Parameters:
            `window` : `Window`
                The window on which the tablet will be used.

        :rtype: `TabletCanvas`
        """
        raise NotImplementedError("abstract")


class TabletCanvas(EventDispatcher):
    __doc__ = "Event dispatcher for tablets.\n\n    Use `Tablet.open` to obtain this object for a particular tablet device and\n    window.  Events may be generated even if the tablet stylus is outside of\n    the window; this is operating-system dependent.\n\n    The events each provide the `TabletCursor` that was used to generate the\n    event; for example, to distinguish between a stylus and an eraser.  Only\n    one cursor can be used at a time, otherwise the results are undefined.\n\n    :Ivariables:\n        `window` : Window\n            The window on which this tablet was opened.\n    "

    def __init__(self, window):
        self.window = window

    def close(self):
        """Close the tablet device for this window.
        """
        raise NotImplementedError("abstract")

    if _is_pyglet_doc_run:

        def on_enter(self, cursor):
            """A cursor entered the proximity of the window.  The cursor may
            be hovering above the tablet surface, but outside of the window
            bounds, or it may have entered the window bounds.

            Note that you cannot rely on `on_enter` and `on_leave` events to
            be generated in pairs; some events may be lost if the cursor was
            out of the window bounds at the time.

            :Parameters:
                `cursor` : `TabletCursor`
                    The cursor that entered proximity.

            :event:
            """
            return

        def on_leave(self, cursor):
            """A cursor left the proximity of the window.  The cursor may have
            moved too high above the tablet surface to be detected, or it may
            have left the bounds of the window.

            Note that you cannot rely on `on_enter` and `on_leave` events to
            be generated in pairs; some events may be lost if the cursor was
            out of the window bounds at the time.

            :Parameters:
                `cursor` : `TabletCursor`
                    The cursor that left proximity.

            :event:
            """
            return

        def on_motion(self, cursor, x, y, pressure):
            """The cursor moved on the tablet surface.

            If `pressure` is 0, then the cursor is actually hovering above the
            tablet surface, not in contact.

            :Parameters:
                `cursor` : `TabletCursor`
                    The cursor that moved.
                `x` : int
                    The X position of the cursor, in window coordinates.
                `y` : int
                    The Y position of the cursor, in window coordinates.
                `pressure` : float
                    The pressure applied to the cursor, in range 0.0 (no
                    pressure) to 1.0 (full pressure).
                `tilt_x` : float
                    Currently undefined.
                `tilt_y` : float
                    Currently undefined.

            :event:
            """
            return


TabletCanvas.register_event_type("on_enter")
TabletCanvas.register_event_type("on_leave")
TabletCanvas.register_event_type("on_motion")

class TabletCursor:
    __doc__ = "A distinct cursor used on a tablet.\n\n    Most tablets support at least a *stylus* and an *erasor* cursor; this\n    object is used to distinguish them when tablet events are generated.\n\n    :Ivariables:\n        `name` : str\n            Name of the cursor.\n    "

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.name)
