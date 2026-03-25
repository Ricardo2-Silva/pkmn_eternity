# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\python\lockfile.py
"""
Filesystem-based interprocess mutex.
"""
from __future__ import absolute_import, division
import errno, os
from time import time as _uniquefloat
from twisted.python.runtime import platform
from twisted.python.compat import _PY3

def unique():
    return str(int(_uniquefloat() * 1000))


from os import rename
if not platform.isWindows():
    from os import kill
    from os import symlink
    from os import readlink
    from os import remove as rmlink
    _windows = False
else:
    _windows = True
    try:
        from win32api import OpenProcess
        import pywintypes
    except ImportError:
        kill = None
    else:
        ERROR_ACCESS_DENIED = 5
        ERROR_INVALID_PARAMETER = 87

        def kill(pid, signal):
            try:
                OpenProcess(0, 0, pid)
            except pywintypes.error as e:
                if e.args[0] == ERROR_ACCESS_DENIED:
                    return
                if e.args[0] == ERROR_INVALID_PARAMETER:
                    raise OSError(errno.ESRCH, None)
                raise
            else:
                raise RuntimeError("OpenProcess is required to fail.")


    _open = open

    def symlink(value, filename):
        """
        Write a file at C{filename} with the contents of C{value}. See the
        above comment block as to why this is needed.
        """
        newlinkname = filename + "." + unique() + ".newlink"
        newvalname = os.path.join(newlinkname, "symlink")
        os.mkdir(newlinkname)
        if _PY3:
            mode = "w"
        else:
            mode = "wc"
        with _open(newvalname, mode) as f:
            f.write(value)
            f.flush()
        try:
            rename(newlinkname, filename)
        except:
            os.remove(newvalname)
            os.rmdir(newlinkname)
            raise


    def readlink(filename):
        """
        Read the contents of C{filename}. See the above comment block as to why
        this is needed.
        """
        try:
            fObj = _open(os.path.join(filename, "symlink"), "r")
        except IOError as e:
            if e.errno == errno.ENOENT or e.errno == errno.EIO:
                raise OSError(e.errno, None)
            raise
        else:
            with fObj:
                result = fObj.read()
            return result


    def rmlink(filename):
        os.remove(os.path.join(filename, "symlink"))
        os.rmdir(filename)


class FilesystemLock(object):
    __doc__ = "\n    A mutex.\n\n    This relies on the filesystem property that creating\n    a symlink is an atomic operation and that it will\n    fail if the symlink already exists.  Deleting the\n    symlink will release the lock.\n\n    @ivar name: The name of the file associated with this lock.\n\n    @ivar clean: Indicates whether this lock was released cleanly by its\n        last owner.  Only meaningful after C{lock} has been called and\n        returns True.\n\n    @ivar locked: Indicates whether the lock is currently held by this\n        object.\n    "
    clean = None
    locked = False

    def __init__(self, name):
        self.name = name

    def lock(self):
        """
        Acquire this lock.

        @rtype: C{bool}
        @return: True if the lock is acquired, false otherwise.

        @raise: Any exception os.symlink() may raise, other than
        EEXIST.
        """
        clean = True
        while 1:
            try:
                symlink(str(os.getpid()), self.name)
            except OSError as e:
                if _windows:
                    if e.errno in (errno.EACCES, errno.EIO):
                        return False
                if e.errno == errno.EEXIST:
                    try:
                        pid = readlink(self.name)
                    except (IOError, OSError) as e:
                        if e.errno == errno.ENOENT:
                            continue
                        elif _windows:
                            pass
                        if e.errno == errno.EACCES:
                            return False
                        raise

                    try:
                        if kill is not None:
                            kill(int(pid), 0)
                    except OSError as e:
                        if e.errno == errno.ESRCH:
                            try:
                                rmlink(self.name)
                            except OSError as e:
                                if e.errno == errno.ENOENT:
                                    continue
                                raise

                            clean = False
                            continue
                        raise

                    return False
                raise

            self.locked = True
            self.clean = clean
            return True

    def unlock(self):
        """
        Release this lock.

        This deletes the directory with the given name.

        @raise: Any exception os.readlink() may raise, or
        ValueError if the lock is not owned by this process.
        """
        pid = readlink(self.name)
        if int(pid) != os.getpid():
            raise ValueError("Lock %r not owned by this process" % (self.name,))
        rmlink(self.name)
        self.locked = False


def isLocked(name):
    """
    Determine if the lock of the given name is held or not.

    @type name: C{str}
    @param name: The filesystem path to the lock to test

    @rtype: C{bool}
    @return: True if the lock is held, False otherwise.
    """
    l = FilesystemLock(name)
    result = None
    try:
        result = l.lock()
    finally:
        if result:
            l.unlock()

    return not result


__all__ = [
 "FilesystemLock", "isLocked"]
