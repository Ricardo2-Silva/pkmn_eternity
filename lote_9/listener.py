# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\media\drivers\listener.py
from abc import ABCMeta, abstractmethod
from pyglet.util import with_metaclass

class AbstractListener(with_metaclass(ABCMeta, object)):
    __doc__ = "The listener properties for positional audio.\n\n    You can obtain the singleton instance of this class by calling\n    :meth:`AbstractAudioDriver.get_listener`.\n    "
    _volume = 1.0
    _position = (0, 0, 0)
    _forward_orientation = (0, 0, -1)
    _up_orientation = (0, 1, 0)

    @abstractmethod
    def _set_volume(self, volume):
        return

    volume = property((lambda self: self._volume), (lambda self, volume: self._set_volume(volume)),
      doc="The master volume for sound playback.\n\n        All sound volumes are multiplied by this master volume before being\n        played.  A value of 0 will silence playback (but still consume\n        resources).  The nominal volume is 1.0.\n\n        :type: float\n        ")

    @abstractmethod
    def _set_position(self, position):
        return

    position = property((lambda self: self._position), (lambda self, position: self._set_position(position)),
      doc="The position of the listener in 3D space.\n\n        The position is given as a tuple of floats (x, y, z).  The unit\n        defaults to meters, but can be modified with the listener\n        properties.\n\n        :type: 3-tuple of float\n        ")

    @abstractmethod
    def _set_forward_orientation(self, orientation):
        return

    forward_orientation = property((lambda self: self._forward_orientation), (lambda self, o: self._set_forward_orientation(o)),
      doc="A vector giving the direction the\n        listener is facing.\n\n        The orientation is given as a tuple of floats (x, y, z), and has\n        no unit.  The forward orientation should be orthagonal to the\n        up orientation.\n\n        :type: 3-tuple of float\n        ")

    @abstractmethod
    def _set_up_orientation(self, orientation):
        return

    up_orientation = property((lambda self: self._up_orientation), (lambda self, o: self._set_up_orientation(o)),
      doc='A vector giving the "up" orientation\n        of the listener.\n\n        The orientation is given as a tuple of floats (x, y, z), and has\n        no unit.  The up orientation should be orthagonal to the\n        forward orientation.\n\n        :type: 3-tuple of float\n        ')
