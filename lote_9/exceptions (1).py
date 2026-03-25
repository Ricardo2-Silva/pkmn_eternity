# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\media\drivers\directsound\exceptions.py
from pyglet.media.exceptions import MediaException

class DirectSoundException(MediaException):
    return


class DirectSoundNativeError(DirectSoundException):

    def __init__(self, hresult):
        self.hresult = hresult

    def __repr__(self):
        return "{}: Error {}".format(self.__class__.__name__, self.hresult)
