# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\lib.py
"""Functions for loading dynamic libraries.

These extend and correct ctypes functions.
"""
import os, re, sys, ctypes, ctypes.util, pyglet
_debug_lib = pyglet.options["debug_lib"]
_debug_trace = pyglet.options["debug_trace"]
_is_pyglet_doc_run = getattr(sys, "is_pyglet_doc_run", False)
if pyglet.options["search_local_libs"]:
    script_path = pyglet.resource.get_script_home()
    cwd = os.getcwd()
    _local_lib_paths = [script_path, os.path.join(script_path, "lib"), os.path.join(cwd, "lib")]
    if pyglet.compat_platform == "win32":
        os.environ["PATH"] += os.pathsep + os.pathsep.join(_local_lib_paths)
else:
    _local_lib_paths = None

class _TraceFunction:

    def __init__(self, func):
        self.__dict__["_func"] = func

    def __str__(self):
        return self._func.__name__

    def __call__(self, *args, **kwargs):
        return (self._func)(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(self._func, name)

    def __setattr__(self, name, value):
        setattr(self._func, name, value)


class _TraceLibrary:

    def __init__(self, library):
        self._library = library
        print(library)

    def __getattr__(self, name):
        func = getattr(self._library, name)
        f = _TraceFunction(func)
        return f


if _is_pyglet_doc_run:

    class LibraryMock:
        __doc__ = "Mock library used when generating documentation."

        def __getattr__(self, name):
            return LibraryMock()

        def __setattr__(self, name, value):
            return

        def __call__(self, *args, **kwargs):
            return LibraryMock()


else:

    class LibraryLoader:
        platform = pyglet.compat_platform
        if platform == "cygwin":
            platform = "win32"

        def load_library(self, *names, **kwargs):
            """Find and load a library.  
        
        More than one name can be specified, they will be tried in order.
        Platform-specific library names (given as kwargs) are tried first.

        Raises ImportError if library is not found.
        """
            if _is_pyglet_doc_run:
                return LibraryMock()
            elif "framework" in kwargs:
                if self.platform == "darwin":
                    return self.load_framework(kwargs["framework"])
                if not names:
                    raise ImportError("No library name specified")
                platform_names = kwargs.get(self.platform, [])
                if isinstance(platform_names, str):
                    platform_names = [
                     platform_names]
            else:
                if type(platform_names) is tuple:
                    platform_names = list(platform_names)
            if self.platform.startswith("linux"):
                for name in names:
                    libname = self.find_library(name)
                    platform_names.append(libname or "lib%s.so" % name)

            platform_names.extend(names)
            for name in platform_names:
                try:
                    lib = ctypes.cdll.LoadLibrary(name)
                    if _debug_lib:
                        print(name)
                    if _debug_trace:
                        lib = _TraceLibrary(lib)
                    return lib
                except OSError as o:
                    path = self.find_library(name)
                    if path:
                        try:
                            lib = ctypes.cdll.LoadLibrary(path)
                            if _debug_lib:
                                print(path)
                            if _debug_trace:
                                lib = _TraceLibrary(lib)
                            return lib
                        except OSError:
                            pass

                    if self.platform == "win32":
                        if o.winerror != 126:
                            raise ImportError("Unexpected error loading library %s: %s" % (name, str(o)))

            raise ImportError('Library "%s" not found.' % names[0])

        def find_library(self, name):
            return ctypes.util.find_library(name)

        @staticmethod
        def load_framework(name):
            raise RuntimeError("Can't load framework on this platform.")


    class MachOLibraryLoader(LibraryLoader):

        def __init__(self):
            if "LD_LIBRARY_PATH" in os.environ:
                self.ld_library_path = os.environ["LD_LIBRARY_PATH"].split(":")
            else:
                self.ld_library_path = []
            if _local_lib_paths:
                self.ld_library_path = _local_lib_paths + self.ld_library_path
                os.environ["LD_LIBRARY_PATH"] = ":".join(self.ld_library_path)
            elif "DYLD_LIBRARY_PATH" in os.environ:
                self.dyld_library_path = os.environ["DYLD_LIBRARY_PATH"].split(":")
            else:
                self.dyld_library_path = []
            if "DYLD_FALLBACK_LIBRARY_PATH" in os.environ:
                self.dyld_fallback_library_path = os.environ["DYLD_FALLBACK_LIBRARY_PATH"].split(":")
            else:
                self.dyld_fallback_library_path = [
                 os.path.expanduser("~/lib"), "/usr/local/lib", "/usr/lib"]

        def find_library(self, path):
            """Implements the dylib search as specified in Apple documentation:

        http://developer.apple.com/library/content/documentation/DeveloperTools/Conceptual/DynamicLibraries/100-Articles/DynamicLibraryUsageGuidelines.html

        Before commencing the standard search, the method first checks
        the bundle's ``Frameworks`` directory if the application is running
        within a bundle (OS X .app).
        """
            libname = os.path.basename(path)
            search_path = []
            if ".dylib" not in libname:
                libname = "lib" + libname + ".dylib"
            if getattr(sys, "frozen", None) == "macosx_app":
                if "RESOURCEPATH" in os.environ:
                    search_path.append(os.path.join(os.environ["RESOURCEPATH"], "..", "Frameworks", libname))
            if os.environ.get("CONDA_PREFIX", False):
                search_path.append(os.path.join(os.environ["CONDA_PREFIX"], "lib", libname))
            if hasattr(sys, "frozen"):
                if hasattr(sys, "_MEIPASS"):
                    if sys.frozen is True:
                        if pyglet.compat_platform == "darwin":
                            search_path.append(os.path.join(sys._MEIPASS, libname))
            if "/" in path:
                search_path.extend([os.path.join(p, libname) for p in self.dyld_library_path])
                search_path.append(path)
                search_path.extend([os.path.join(p, libname) for p in self.dyld_fallback_library_path])
            else:
                search_path.extend([os.path.join(p, libname) for p in self.ld_library_path])
                search_path.extend([os.path.join(p, libname) for p in self.dyld_library_path])
                search_path.append(path)
                search_path.extend([os.path.join(p, libname) for p in self.dyld_fallback_library_path])
            for path in search_path:
                if os.path.exists(path):
                    return path

            return

        @staticmethod
        def load_framework(name):
            path = ctypes.util.find_library(name)
            if path is None:
                frameworks = {'AGL': '"/System/Library/Frameworks/AGL.framework/AGL"', 
                 'IOKit': '"/System/Library/Frameworks/IOKit.framework/IOKit"', 
                 'OpenAL': '"/System/Library/Frameworks/OpenAL.framework/OpenAL"', 
                 'OpenGL': '"/System/Library/Frameworks/OpenGL.framework/OpenGL"'}
                path = frameworks.get(name)
            if path:
                lib = ctypes.cdll.LoadLibrary(path)
                if _debug_lib:
                    print(path)
                if _debug_trace:
                    lib = _TraceLibrary(lib)
                return lib
            raise ImportError("Can't find framework %s." % name)


    class LinuxLibraryLoader(LibraryLoader):
        _ld_so_cache = None
        _local_libs_cache = None

        @staticmethod
        def _find_libs(directories):
            cache = {}
            lib_re = re.compile("lib(.*)\\.so(?:$|\\.)")
            for directory in directories:
                try:
                    for file in os.listdir(directory):
                        match = lib_re.match(file)
                        if match:
                            path = os.path.join(directory, file)
                            if file not in cache:
                                cache[file] = path
                            library = match.group(1)
                            if library not in cache:
                                cache[library] = path

                except OSError:
                    pass

            return cache

        def _create_ld_so_cache(self):
            directories = []
            try:
                directories.extend(os.environ["LD_LIBRARY_PATH"].split(":"))
            except KeyError:
                pass

            try:
                with open("/etc/ld.so.conf") as fid:
                    directories.extend([dir.strip() for dir in fid])
            except IOError:
                pass

            directories.extend(["/lib", "/usr/lib"])
            self._ld_so_cache = self._find_libs(directories)

        def find_library(self, path):
            if _local_lib_paths:
                if not self._local_libs_cache:
                    self._local_libs_cache = self._find_libs(_local_lib_paths)
                if path in self._local_libs_cache:
                    return self._local_libs_cache[path]
            result = ctypes.util.find_library(path)
            if result:
                return result
            else:
                if self._ld_so_cache is None:
                    self._create_ld_so_cache()
                return self._ld_so_cache.get(path)


    if pyglet.compat_platform == "darwin":
        loader = MachOLibraryLoader()
    elif pyglet.compat_platform.startswith("linux"):
        loader = LinuxLibraryLoader()
    else:
        loader = LibraryLoader()
load_library = loader.load_library
