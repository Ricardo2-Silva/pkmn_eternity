# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\window\mouse.py
"""Mouse constants and utilities for pyglet.window.
"""

class MouseStateHandler(dict):
    __doc__ = 'Simple handler that tracks the state of buttons from the mouse. If a\n    button is pressed then this handler holds a True value for it.\n\n    For example::\n\n        >>> win = window.Window()\n        >>> mousebuttons = mouse.MouseStateHandler()\n        >>> win.push_handlers(mousebuttons)\n\n        # Hold down the "left" button...\n\n        >>> mousebuttons[mouse.LEFT]\n        True\n        >>> mousebuttons[mouse.RIGHT]\n        False\n\n    '

    def on_mouse_press(self, x, y, button, modifiers):
        self[button] = True

    def on_mouse_release(self, x, y, button, modifiers):
        self[button] = False

    def __getitem__(self, key):
        return self.get(key, False)


def buttons_string(buttons):
    """Return a string describing a set of active mouse buttons.

    Example::

        >>> buttons_string(LEFT | RIGHT)
        'LEFT|RIGHT'

    :Parameters:
        `buttons` : int
            Bitwise combination of mouse button constants.

    :rtype: str
    """
    button_names = []
    if buttons & LEFT:
        button_names.append("LEFT")
    if buttons & MIDDLE:
        button_names.append("MIDDLE")
    if buttons & RIGHT:
        button_names.append("RIGHT")
    return "|".join(button_names)


LEFT = 1
MIDDLE = 2
RIGHT = 4
