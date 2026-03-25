# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\media\buffered_logger.py
"""
Responsabilities

    Handles accumulation of debug events while playing media_player and  saves
    when sample's play ends.
"""
import time, pickle

class BufferedLogger:

    def __init__(self, outfile):
        self.outfile = outfile
        self.log_entries = []
        self.start_wall_time = None
        self.on_close_callback_info = None

    def init_wall_time(self):
        self.start_wall_time = time.perf_counter()

    def log(self, *args):
        self.log_entries.append(args)

    def rebased_wall_time(self):
        return time.perf_counter() - self.start_wall_time

    def close(self):
        self.save_log_entries_as_pickle()
        if self.on_close_callback_info is not None:
            fn, args = self.on_close_callback_info
            fn(self.log_entries, *args)

    def save_log_entries_as_pickle(self):
        with open(self.outfile, "wb") as f:
            pickle.dump(self.log_entries, f)

    def clear(self):
        self.log_entries = []


logger = None
