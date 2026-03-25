# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\python\_inotify.py
"""
Very low-level ctypes-based interface to Linux inotify(7).

ctypes and a version of libc which supports inotify system calls are
required.
"""
import ctypes, ctypes.util

class INotifyError(Exception):
    __doc__ = "\n    Unify all the possible exceptions that can be raised by the INotify API.\n    "


def init():
    """
    Create an inotify instance and return the associated file descriptor.
    """
    fd = libc.inotify_init()
    if fd < 0:
        raise INotifyError("INotify initialization error.")
    return fd


def add(fd, path, mask):
    """
    Add a watch for the given path to the inotify file descriptor, and return
    the watch descriptor.

    @param fd: The file descriptor returned by C{libc.inotify_init}.
    @type fd: L{int}

    @param path: The path to watch via inotify.
    @type path: L{twisted.python.filepath.FilePath}

    @param mask: Bitmask specifying the events that inotify should monitor.
    @type mask: L{int}
    """
    wd = libc.inotify_add_watch(fd, path.asBytesMode().path, mask)
    if wd < 0:
        raise INotifyError("Failed to add watch on '%r' - (%r)" % (path, wd))
    return wd


def remove(fd, wd):
    """
    Remove the given watch descriptor from the inotify file descriptor.
    """
    libc.inotify_rm_watch(fd, wd)


def initializeModule(libc):
    """
    Initialize the module, checking if the expected APIs exist and setting the
    argtypes and restype for C{inotify_init}, C{inotify_add_watch}, and
    C{inotify_rm_watch}.
    """
    for function in ('inotify_add_watch', 'inotify_init', 'inotify_rm_watch'):
        if getattr(libc, function, None) is None:
            raise ImportError("libc6 2.4 or higher needed")

    libc.inotify_init.argtypes = []
    libc.inotify_init.restype = ctypes.c_int
    libc.inotify_rm_watch.argtypes = [
     ctypes.c_int, ctypes.c_int]
    libc.inotify_rm_watch.restype = ctypes.c_int
    libc.inotify_add_watch.argtypes = [
     ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32]
    libc.inotify_add_watch.restype = ctypes.c_int


name = ctypes.util.find_library("c")
if not name:
    raise ImportError("Can't find C library.")
libc = ctypes.cdll.LoadLibrary(name)
initializeModule(libc)
