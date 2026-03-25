# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\python\runtime.py
from __future__ import division, absolute_import
import os, sys, time, warnings
from twisted.python._oldstyle import _oldStyle

def shortPythonVersion():
    """
    Returns the Python version as a dot-separated string.
    """
    return "%s.%s.%s" % sys.version_info[:3]


knownPlatforms = {
 'nt': '"win32"', 
 'ce': '"win32"', 
 'posix': '"posix"', 
 'java': '"java"', 
 'org.python.modules.os': '"java"'}
_timeFunctions = {"win32": (time.time)}

@_oldStyle
class Platform:
    __doc__ = "\n    Gives us information about the platform we're running on.\n    "
    type = knownPlatforms.get(os.name)
    seconds = staticmethod(_timeFunctions.get(type, time.time))
    _platform = sys.platform

    def __init__(self, name=None, platform=None):
        if name is not None:
            self.type = knownPlatforms.get(name)
            self.seconds = _timeFunctions.get(self.type, time.time)
        if platform is not None:
            self._platform = platform

    def isKnown(self):
        """
        Do we know about this platform?

        @return: Boolean indicating whether this is a known platform or not.
        @rtype: C{bool}
        """
        return self.type != None

    def getType(self):
        """
        Get platform type.

        @return: Either 'posix', 'win32' or 'java'
        @rtype: C{str}
        """
        return self.type

    def isMacOSX(self):
        """
        Check if current platform is macOS.

        @return: C{True} if the current platform has been detected as macOS.
        @rtype: C{bool}
        """
        return self._platform == "darwin"

    def isWinNT(self):
        """
        Are we running in Windows NT?

        This is deprecated and always returns C{True} on win32 because
        Twisted only supports Windows NT-derived platforms at this point.

        @return: C{True} if the current platform has been detected as
            Windows NT.
        @rtype: C{bool}
        """
        warnings.warn("twisted.python.runtime.Platform.isWinNT was deprecated in Twisted 13.0. Use Platform.isWindows instead.",
          DeprecationWarning,
          stacklevel=2)
        return self.isWindows()

    def isWindows(self):
        """
        Are we running in Windows?

        @return: C{True} if the current platform has been detected as
            Windows.
        @rtype: C{bool}
        """
        return self.getType() == "win32"

    def isVista(self):
        """
        Check if current platform is Windows Vista or Windows Server 2008.

        @return: C{True} if the current platform has been detected as Vista
        @rtype: C{bool}
        """
        if getattr(sys, "getwindowsversion", None) is not None:
            return sys.getwindowsversion()[0] == 6
        else:
            return False

    def isLinux(self):
        """
        Check if current platform is Linux.

        @return: C{True} if the current platform has been detected as Linux.
        @rtype: C{bool}
        """
        return self._platform.startswith("linux")

    def isDocker(self, _initCGroupLocation='/proc/1/cgroup'):
        """
        Check if the current platform is Linux in a Docker container.

        @return: C{True} if the current platform has been detected as Linux
            inside a Docker container.
        @rtype: C{bool}
        """
        if not self.isLinux():
            return False
        else:
            from twisted.python.filepath import FilePath
            initCGroups = FilePath(_initCGroupLocation)
            if initCGroups.exists():
                controlGroups = [x.split(b':') for x in initCGroups.getContent().split(b'\n')]
                for group in controlGroups:
                    if len(group) == 3:
                        if group[2].startswith(b'/docker/'):
                            return True

            return False

    def _supportsSymlinks(self):
        """
        Check for symlink support usable for Twisted's purposes.

        @return: C{True} if symlinks are supported on the current platform,
                 otherwise C{False}.
        @rtype: L{bool}
        """
        if self.isWindows():
            return False
        else:
            try:
                os.symlink
            except AttributeError:
                return False

            return True

    def supportsThreads(self):
        """
        Can threads be created?

        @return: C{True} if the threads are supported on the current platform.
        @rtype: C{bool}
        """
        try:
            import threading
            return threading is not None
        except ImportError:
            return False

    def supportsINotify(self):
        """
        Return C{True} if we can use the inotify API on this platform.

        @since: 10.1
        """
        try:
            from twisted.python._inotify import INotifyError, init
        except ImportError:
            return False
        else:
            try:
                os.close(init())
            except INotifyError:
                return False
            else:
                return True


platform = Platform()
platformType = platform.getType()
seconds = platform.seconds
