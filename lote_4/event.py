# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\data\events\event.py
import random

class CallbackPriority:
    ON_START = 0
    ON_END = 1
    ALL_PRIORITY = [ON_START, ON_END]
