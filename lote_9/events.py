# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\media\events.py
import time, pyglet

class MediaEvent:
    __doc__ = "Representation of a media event.\n\n    These events are used internally by some audio driver implementation to\n    communicate events to the :class:`~pyglet.media.player.Player`.\n    One example is the ``on_eos`` event.\n\n    Args:\n        timestamp (float): The time where this event happens.\n        event (str): Event description.\n        *args: Any required positional argument to go along with this event.\n    "

    def __init__(self, timestamp, event, *args):
        self.timestamp = timestamp
        self.event = event
        self.args = args

    def _sync_dispatch_to_player(self, player):
        (pyglet.app.platform_event_loop.post_event)(player, self.event, *self.args)
        time.sleep(0)

    def __repr__(self):
        return "%s(%r, %r, %r)" % (self.__class__.__name__,
         self.timestamp, self.event, self.args)

    def __lt__(self, other):
        return hash(self) < hash(other)
