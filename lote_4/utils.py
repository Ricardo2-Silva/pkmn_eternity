# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\data\utils\utils.py
"""
Created on 17 juil. 2011

@author: Kami
"""
import os

class DynamicObject:
    __doc__ = " This is an object where you can set and get values dynamicly, like a dict. "

    def __init__(self, **kwargs):
        for key in kwargs:
            self.__dict__[key] = kwargs[key]

    def set(self, key, value):
        self.__dict__[key] = value

    def get(self, key):
        if key in self.__dict__:
            return self.__dict__[key]
        else:
            return


def checkFolder(folder):
    """ Makes sure folder exists, if not, creates it. """
    if not os.path.exists(folder):
        os.makedirs(folder)
    if not os.path.isdir(folder):
        os.remove(folder)
        os.makedirs(folder)


suffixes = [
 'B', 'KB', 'MB', 'GB', 'TB', 'PB']

def bytesToString(nbytes):
    i = 0
    while nbytes >= 1024 and i < len(suffixes) - 1:
        nbytes /= 1024.0
        i += 1

    f = ("%.2f" % nbytes).rstrip("0").rstrip(".")
    return f"{f} {suffixes[i]}"
