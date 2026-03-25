# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\window\key.py
"""Key constants and utilities for pyglet.window.

Usage::

    from pyglet.window import Window
    from pyglet.window import key

    window = Window()

    @window.event
    def on_key_press(symbol, modifiers):
        # Symbolic names:
        if symbol == key.RETURN:

        # Alphabet keys:
        elif symbol == key.Z:

        # Number keys:
        elif symbol == key._1:

        # Number keypad keys:
        elif symbol == key.NUM_1:

        # Modifiers:
        if modifiers & key.MOD_CTRL:

"""
from pyglet import compat_platform

class KeyStateHandler(dict):
    __doc__ = 'Simple handler that tracks the state of keys on the keyboard. If a\n    key is pressed then this handler holds a True value for it.\n\n    For example::\n\n        >>> win = window.Window\n        >>> keyboard = key.KeyStateHandler()\n        >>> win.push_handlers(keyboard)\n\n        # Hold down the "up" arrow...\n\n        >>> keyboard[key.UP]\n        True\n        >>> keyboard[key.DOWN]\n        False\n\n    '

    def on_key_press(self, symbol, modifiers):
        self[symbol] = True

    def on_key_release(self, symbol, modifiers):
        self[symbol] = False

    def __getitem__(self, key):
        return self.get(key, False)


def modifiers_string(modifiers):
    """Return a string describing a set of modifiers.

    Example::

        >>> modifiers_string(MOD_SHIFT | MOD_CTRL)
        'MOD_SHIFT|MOD_CTRL'

    :Parameters:
        `modifiers` : int
            Bitwise combination of modifier constants.

    :rtype: str
    """
    mod_names = []
    if modifiers & MOD_SHIFT:
        mod_names.append("MOD_SHIFT")
    if modifiers & MOD_CTRL:
        mod_names.append("MOD_CTRL")
    if modifiers & MOD_ALT:
        mod_names.append("MOD_ALT")
    if modifiers & MOD_CAPSLOCK:
        mod_names.append("MOD_CAPSLOCK")
    if modifiers & MOD_NUMLOCK:
        mod_names.append("MOD_NUMLOCK")
    if modifiers & MOD_SCROLLLOCK:
        mod_names.append("MOD_SCROLLLOCK")
    if modifiers & MOD_COMMAND:
        mod_names.append("MOD_COMMAND")
    if modifiers & MOD_OPTION:
        mod_names.append("MOD_OPTION")
    if modifiers & MOD_FUNCTION:
        mod_names.append("MOD_FUNCTION")
    return "|".join(mod_names)


def symbol_string(symbol):
    """Return a string describing a key symbol.

    Example::

        >>> symbol_string(BACKSPACE)
        'BACKSPACE'

    :Parameters:
        `symbol` : int
            Symbolic key constant.

    :rtype: str
    """
    if symbol < 4294967296:
        return _key_names.get(symbol, str(symbol))
    else:
        return "user_key(%x)" % (symbol >> 32)


def motion_string(motion):
    """Return a string describing a text motion.

    Example::

        >>> motion_string(MOTION_NEXT_WORD)
        'MOTION_NEXT_WORD'

    :Parameters:
        `motion` : int
            Text motion constant.

    :rtype: str
    """
    return _motion_names.get(motion, str(motion))


def user_key(scancode):
    """Return a key symbol for a key not supported by pyglet.

    This can be used to map virtual keys or scancodes from unsupported
    keyboard layouts into a machine-specific symbol.  The symbol will
    be meaningless on any other machine, or under a different keyboard layout.

    Applications should use user-keys only when user explicitly binds them
    (for example, mapping keys to actions in a game options screen).
    """
    assert scancode > 0
    return scancode << 32


MOD_SHIFT = 1
MOD_CTRL = 2
MOD_ALT = 4
MOD_CAPSLOCK = 8
MOD_NUMLOCK = 16
MOD_WINDOWS = 32
MOD_COMMAND = 64
MOD_OPTION = 128
MOD_SCROLLLOCK = 256
MOD_FUNCTION = 512
MOD_ACCEL = MOD_CTRL
if compat_platform == "darwin":
    MOD_ACCEL = MOD_COMMAND
BACKSPACE = 65288
TAB = 65289
LINEFEED = 65290
CLEAR = 65291
RETURN = 65293
ENTER = 65293
PAUSE = 65299
SCROLLLOCK = 65300
SYSREQ = 65301
ESCAPE = 65307
SPACE = 65312
HOME = 65360
LEFT = 65361
UP = 65362
RIGHT = 65363
DOWN = 65364
PAGEUP = 65365
PAGEDOWN = 65366
END = 65367
BEGIN = 65368
DELETE = 65535
SELECT = 65376
PRINT = 65377
EXECUTE = 65378
INSERT = 65379
UNDO = 65381
REDO = 65382
MENU = 65383
FIND = 65384
CANCEL = 65385
HELP = 65386
BREAK = 65387
MODESWITCH = 65406
SCRIPTSWITCH = 65406
FUNCTION = 65490
MOTION_UP = UP
MOTION_RIGHT = RIGHT
MOTION_DOWN = DOWN
MOTION_LEFT = LEFT
MOTION_NEXT_WORD = 1
MOTION_PREVIOUS_WORD = 2
MOTION_BEGINNING_OF_LINE = 3
MOTION_END_OF_LINE = 4
MOTION_NEXT_PAGE = PAGEDOWN
MOTION_PREVIOUS_PAGE = PAGEUP
MOTION_BEGINNING_OF_FILE = 5
MOTION_END_OF_FILE = 6
MOTION_BACKSPACE = BACKSPACE
MOTION_DELETE = DELETE
NUMLOCK = 65407
NUM_SPACE = 65408
NUM_TAB = 65417
NUM_ENTER = 65421
NUM_F1 = 65425
NUM_F2 = 65426
NUM_F3 = 65427
NUM_F4 = 65428
NUM_HOME = 65429
NUM_LEFT = 65430
NUM_UP = 65431
NUM_RIGHT = 65432
NUM_DOWN = 65433
NUM_PRIOR = 65434
NUM_PAGE_UP = 65434
NUM_NEXT = 65435
NUM_PAGE_DOWN = 65435
NUM_END = 65436
NUM_BEGIN = 65437
NUM_INSERT = 65438
NUM_DELETE = 65439
NUM_EQUAL = 65469
NUM_MULTIPLY = 65450
NUM_ADD = 65451
NUM_SEPARATOR = 65452
NUM_SUBTRACT = 65453
NUM_DECIMAL = 65454
NUM_DIVIDE = 65455
NUM_0 = 65456
NUM_1 = 65457
NUM_2 = 65458
NUM_3 = 65459
NUM_4 = 65460
NUM_5 = 65461
NUM_6 = 65462
NUM_7 = 65463
NUM_8 = 65464
NUM_9 = 65465
F1 = 65470
F2 = 65471
F3 = 65472
F4 = 65473
F5 = 65474
F6 = 65475
F7 = 65476
F8 = 65477
F9 = 65478
F10 = 65479
F11 = 65480
F12 = 65481
F13 = 65482
F14 = 65483
F15 = 65484
F16 = 65485
F17 = 65486
F18 = 65487
F19 = 65488
F20 = 65489
LSHIFT = 65505
RSHIFT = 65506
LCTRL = 65507
RCTRL = 65508
CAPSLOCK = 65509
LMETA = 65511
RMETA = 65512
LALT = 65513
RALT = 65514
LWINDOWS = 65515
RWINDOWS = 65516
LCOMMAND = 65517
RCOMMAND = 65518
LOPTION = 65519
ROPTION = 65520
SPACE = 32
EXCLAMATION = 33
DOUBLEQUOTE = 34
HASH = 35
POUND = 35
DOLLAR = 36
PERCENT = 37
AMPERSAND = 38
APOSTROPHE = 39
PARENLEFT = 40
PARENRIGHT = 41
ASTERISK = 42
PLUS = 43
COMMA = 44
MINUS = 45
PERIOD = 46
SLASH = 47
_0 = 48
_1 = 49
_2 = 50
_3 = 51
_4 = 52
_5 = 53
_6 = 54
_7 = 55
_8 = 56
_9 = 57
COLON = 58
SEMICOLON = 59
LESS = 60
EQUAL = 61
GREATER = 62
QUESTION = 63
AT = 64
BRACKETLEFT = 91
BACKSLASH = 92
BRACKETRIGHT = 93
ASCIICIRCUM = 94
UNDERSCORE = 95
GRAVE = 96
QUOTELEFT = 96
A = 97
B = 98
C = 99
D = 100
E = 101
F = 102
G = 103
H = 104
I = 105
J = 106
K = 107
L = 108
M = 109
N = 110
O = 111
P = 112
Q = 113
R = 114
S = 115
T = 116
U = 117
V = 118
W = 119
X = 120
Y = 121
Z = 122
BRACELEFT = 123
BAR = 124
BRACERIGHT = 125
ASCIITILDE = 126
_key_names = {}
_motion_names = {}
for _name, _value in locals().copy().items():
    if _name[:2] != "__":
        if _name.upper() == _name and not _name.startswith("MOD_"):
            if _name.startswith("MOTION_"):
                _motion_names[_value] = _name
        else:
            _key_names[_value] = _name
