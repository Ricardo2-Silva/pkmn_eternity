# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: shared\service\utils.py
"""
Created on 30 oct. 2011

@author: Kami
"""
import struct

def clamp(val, minn, maxn):
    return max(min(maxn, val), minn)


def inRange(value, min, max):
    if value >= min:
        if value < max:
            return True
    return False


def inRange2(value, min, max):
    if value >= min:
        if value <= max:
            return True
    return False


def getParts(message):
    parts = []
    i = 0
    length = message[i]
    while True:
        splitPoint = length
        if splitPoint == 255:
            splitPoint = struct.unpack("!H", message[i + 1:i + 3])[0]
            parts.append(message[i + 3:i + 3 + splitPoint])
            i += 3 + splitPoint
            try:
                length = message[i]
            except Exception:
                break

        else:
            parts.append(message[i + 1:i + 1 + splitPoint])
            i += 1 + splitPoint
            try:
                length = message[i]
            except Exception:
                break

    return parts


def str2list(s):
    """Convert tuple-like strings to real tuples.
    eg '(1,2,3,4)' -> (1, 2, 3, 4)
    """
    if s[0] + s[-1] != "()":
        if s[0] + s[-1] != "[]":
            raise ValueError("Badly formatted string (missing brackets).")
    items = s[1:-1]
    items = items.split(",")
    L = [x.strip() for x in items]
    return L


def str2IntList(s):
    """Convert tuple-like strings to real tuples.
    eg '(1,2,3,4)' -> (1, 2, 3, 4)
    """
    if s[0] + s[-1] != "()":
        if s[0] + s[-1] != "[]":
            raise ValueError("Badly formatted string (missing brackets).")
    items = s[1:-1]
    items = items.split(",")
    L = [int(x.strip()) for x in items]
    return L


def str2IntTuple(s):
    """Convert tuple-like strings to real tuples.
    eg '(1,2,3,4)' -> (1, 2, 3, 4)
    """
    if s[0] + s[-1] != "()":
        if s[0] + s[-1] != "[]":
            raise ValueError("Badly formatted string (missing brackets).")
    items = s[1:-1]
    items = items.split(",")
    L = [int(x.strip()) for x in items]
    return tuple(L)


def list2String(list):
    string = ""
    for x in list:
        string = ",".join([string, str(x)])

    string = "".join(["[", string[1:-2], "]"])
    return string


def nullstrip(text):
    """Strip any null chars from string."""
    try:
        text = text.decode()
        text = text[:text.index("\x00")]
    except ValueError:
        pass

    return text
