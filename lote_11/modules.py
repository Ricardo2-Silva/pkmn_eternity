# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\python\modules.py
"""
This module aims to provide a unified, object-oriented view of Python's
runtime hierarchy.

Python is a very dynamic language with wide variety of introspection utilities.
However, these utilities can be hard to use, because there is no consistent
API.  The introspection API in python is made up of attributes (__name__,
__module__, func_name, etc) on instances, modules, classes and functions which
vary between those four types, utility modules such as 'inspect' which provide
some functionality, the 'imp' module, the "compiler" module, the semantics of
PEP 302 support, and setuptools, among other things.

At the top, you have "PythonPath", an abstract representation of sys.path which
includes methods to locate top-level modules, with or without loading them.
The top-level exposed functions in this module for accessing the system path
are "walkModules", "iterModules", and "getModule".

From most to least specific, here are the objects provided::

                  PythonPath  # sys.path
                      |
                      v
                  PathEntry   # one entry on sys.path: an importer
                      |
                      v
                 PythonModule # a module or package that can be loaded
                      |
                      v
                 PythonAttribute # an attribute of a module (function or class)
                      |
                      v
                 PythonAttribute # an attribute of a function or class
                      |
                      v
                     ...

Here's an example of idiomatic usage: this is what you would do to list all of
the modules outside the standard library's python-files directory::

    import os
    stdlibdir = os.path.dirname(os.__file__)

    from twisted.python.modules import iterModules

    for modinfo in iterModules():
        if (modinfo.pathEntry.filePath.path != stdlibdir
            and not modinfo.isPackage()):
            print('unpackaged: %s: %s' % (
                modinfo.name, modinfo.filePath.path))

@var theSystemPath: The very top of the Python object space.
@type: L{PythonPath}
"""
from __future__ import division, absolute_import, print_function
__metaclass__ = type
from os.path import dirname, split as splitpath
import sys, inspect, warnings, zipimport
from zope.interface import Interface, implementer
from twisted.python.compat import nativeString
from twisted.python.components import registerAdapter
from twisted.python.filepath import FilePath, UnlistableError
from twisted.python.reflect import namedAny
from twisted.python.zippath import ZipArchive
_nothing = object()
PYTHON_EXTENSIONS = [
 ".py"]
OPTIMIZED_MODE = __doc__ is None
if OPTIMIZED_MODE:
    PYTHON_EXTENSIONS.append(".pyo")
else:
    PYTHON_EXTENSIONS.append(".pyc")

def _isPythonIdentifier(string):
    """
    cheezy fake test for proper identifier-ness.

    @param string: a L{str} which might or might not be a valid python
        identifier.
    @return: True or False
    """
    textString = nativeString(string)
    return " " not in textString and "." not in textString and "-" not in textString


def _isPackagePath(fpath):
    extless = fpath.splitext()[0]
    basend = splitpath(extless)[1]
    return basend == "__init__"


class _ModuleIteratorHelper:
    __doc__ = "\n    This mixin provides common behavior between python module and path entries,\n    since the mechanism for searching sys.path and __path__ attributes is\n    remarkably similar.\n    "

    def iterModulesParse error at or near `POP_JUMP_IF_FALSE' instruction at offset 246_248

    def walkModules(self, importPackages=False):
        """
        Similar to L{iterModules}, this yields self, and then every module in my
        package or entry, and every submodule in each package or entry.

        In other words, this is deep, and L{iterModules} is shallow.
        """
        yield self
        for package in self.iterModules():
            for module in package.walkModules(importPackages=importPackages):
                yield module

    def _subModuleName(self, mn):
        """
        This is a hook to provide packages with the ability to specify their names
        as a prefix to submodules here.
        """
        return mn

    def _packagePaths(self):
        """
        Implement in subclasses to specify where to look for modules.

        @return: iterable of FilePath-like objects.
        """
        raise NotImplementedError()

    def _getEntry(self):
        """
        Implement in subclasses to specify what path entry submodules will come
        from.

        @return: a PathEntry instance.
        """
        raise NotImplementedError()

    def __getitem__(self, modname):
        """
        Retrieve a module from below this path or package.

        @param modname: a str naming a module to be loaded.  For entries, this
        is a top-level, undotted package name, and for packages it is the name
        of the module without the package prefix.  For example, if you have a
        PythonModule representing the 'twisted' package, you could use::

            twistedPackageObj['python']['modules']

        to retrieve this module.

        @raise: KeyError if the module is not found.

        @return: a PythonModule.
        """
        for module in self.iterModules():
            if module.name == self._subModuleName(modname):
                return module

        raise KeyError(modname)

    def __iter__(self):
        """
        Implemented to raise NotImplementedError for clarity, so that attempting to
        loop over this object won't call __getitem__.

        Note: in the future there might be some sensible default for iteration,
        like 'walkEverything', so this is deliberately untested and undefined
        behavior.
        """
        raise NotImplementedError()


class PythonAttribute:
    __doc__ = "\n    I represent a function, class, or other object that is present.\n\n    @ivar name: the fully-qualified python name of this attribute.\n\n    @ivar onObject: a reference to a PythonModule or other PythonAttribute that\n    is this attribute's logical parent.\n\n    @ivar name: the fully qualified python name of the attribute represented by\n    this class.\n    "

    def __init__(self, name, onObject, loaded, pythonValue):
        """
        Create a PythonAttribute.  This is a private constructor.  Do not construct
        me directly, use PythonModule.iterAttributes.

        @param name: the FQPN
        @param onObject: see ivar
        @param loaded: always True, for now
        @param pythonValue: the value of the attribute we're pointing to.
        """
        self.name = name
        self.onObject = onObject
        self._loaded = loaded
        self.pythonValue = pythonValue

    def __repr__(self):
        return "PythonAttribute<%r>" % (self.name,)

    def isLoaded(self):
        """
        Return a boolean describing whether the attribute this describes has
        actually been loaded into memory by importing its module.

        Note: this currently always returns true; there is no Python parser
        support in this module yet.
        """
        return self._loaded

    def load(self, default=_nothing):
        """
        Load the value associated with this attribute.

        @return: an arbitrary Python object, or 'default' if there is an error
        loading it.
        """
        return self.pythonValue

    def iterAttributes(self):
        for name, val in inspect.getmembers(self.load()):
            yield PythonAttribute(self.name + "." + name, self, True, val)


class PythonModule(_ModuleIteratorHelper):
    __doc__ = "\n    Representation of a module which could be imported from sys.path.\n\n    @ivar name: the fully qualified python name of this module.\n\n    @ivar filePath: a FilePath-like object which points to the location of this\n    module.\n\n    @ivar pathEntry: a L{PathEntry} instance which this module was located\n    from.\n    "

    def __init__(self, name, filePath, pathEntry):
        """
        Create a PythonModule.  Do not construct this directly, instead inspect a
        PythonPath or other PythonModule instances.

        @param name: see ivar
        @param filePath: see ivar
        @param pathEntry: see ivar
        """
        _name = nativeString(name)
        assert not _name.endswith(".__init__")
        self.name = _name
        self.filePath = filePath
        self.parentPath = filePath.parent()
        self.pathEntry = pathEntry

    def _getEntry(self):
        return self.pathEntry

    def __repr__(self):
        """
        Return a string representation including the module name.
        """
        return "PythonModule<%r>" % (self.name,)

    def isLoaded(self):
        """
        Determine if the module is loaded into sys.modules.

        @return: a boolean: true if loaded, false if not.
        """
        return self.pathEntry.pythonPath.moduleDict.get(self.name) is not None

    def iterAttributes(self):
        """
        List all the attributes defined in this module.

        Note: Future work is planned here to make it possible to list python
        attributes on a module without loading the module by inspecting ASTs or
        bytecode, but currently any iteration of PythonModule objects insists
        they must be loaded, and will use inspect.getmodule.

        @raise NotImplementedError: if this module is not loaded.

        @return: a generator yielding PythonAttribute instances describing the
        attributes of this module.
        """
        if not self.isLoaded():
            raise NotImplementedError("You can't load attributes from non-loaded modules yet.")
        for name, val in inspect.getmembers(self.load()):
            yield PythonAttribute(self.name + "." + name, self, True, val)

    def isPackage(self):
        """
        Returns true if this module is also a package, and might yield something
        from iterModules.
        """
        return _isPackagePath(self.filePath)

    def load(self, default=_nothing):
        """
        Load this module.

        @param default: if specified, the value to return in case of an error.

        @return: a genuine python module.

        @raise: any type of exception.  Importing modules is a risky business;
        the erorrs of any code run at module scope may be raised from here, as
        well as ImportError if something bizarre happened to the system path
        between the discovery of this PythonModule object and the attempt to
        import it.  If you specify a default, the error will be swallowed
        entirely, and not logged.

        @rtype: types.ModuleType.
        """
        try:
            return self.pathEntry.pythonPath.moduleLoader(self.name)
        except:
            if default is not _nothing:
                return default
            raise

    def __eq__(self, other):
        """
        PythonModules with the same name are equal.
        """
        if not isinstance(other, PythonModule):
            return False
        else:
            return other.name == self.name

    def __ne__(self, other):
        """
        PythonModules with different names are not equal.
        """
        if not isinstance(other, PythonModule):
            return True
        else:
            return other.name != self.name

    def walkModules(self, importPackages=False):
        if importPackages:
            if self.isPackage():
                self.load()
        return super(PythonModule, self).walkModules(importPackages=importPackages)

    def _subModuleName(self, mn):
        """
        submodules of this module are prefixed with our name.
        """
        return self.name + "." + mn

    def _packagePaths(self):
        """
        Yield a sequence of FilePath-like objects which represent path segments.
        """
        if not self.isPackage():
            return
        elif self.isLoaded():
            load = self.load()
            if hasattr(load, "__path__"):
                for fn in load.__path__:
                    if fn == self.parentPath.path:
                        assert self.parentPath.exists()
                        yield self.parentPath
                    else:
                        smp = self.pathEntry.pythonPath._smartPath(fn)
                        if smp.exists():
                            yield smp

        else:
            yield self.parentPath


class PathEntry(_ModuleIteratorHelper):
    __doc__ = "\n    I am a proxy for a single entry on sys.path.\n\n    @ivar filePath: a FilePath-like object pointing at the filesystem location\n    or archive file where this path entry is stored.\n\n    @ivar pythonPath: a PythonPath instance.\n    "

    def __init__(self, filePath, pythonPath):
        """
        Create a PathEntry.  This is a private constructor.
        """
        self.filePath = filePath
        self.pythonPath = pythonPath

    def _getEntry(self):
        return self

    def __repr__(self):
        return "PathEntry<%r>" % (self.filePath,)

    def _packagePaths(self):
        yield self.filePath


class IPathImportMapper(Interface):
    __doc__ = "\n    This is an internal interface, used to map importers to factories for\n    FilePath-like objects.\n    "

    def mapPath(self, pathLikeString):
        """
        Return a FilePath-like object.

        @param pathLikeString: a path-like string, like one that might be
        passed to an import hook.

        @return: a L{FilePath}, or something like it (currently only a
        L{ZipPath}, but more might be added later).
        """
        return


@implementer(IPathImportMapper)
class _DefaultMapImpl:
    __doc__ = " Wrapper for the default importer, i.e. None.  "

    def mapPath(self, fsPathString):
        return FilePath(fsPathString)


_theDefaultMapper = _DefaultMapImpl()

@implementer(IPathImportMapper)
class _ZipMapImpl:
    __doc__ = " IPathImportMapper implementation for zipimport.ZipImporter.  "

    def __init__(self, importer):
        self.importer = importer

    def mapPath(self, fsPathString):
        """
        Map the given FS path to a ZipPath, by looking at the ZipImporter's
        "archive" attribute and using it as our ZipArchive root, then walking
        down into the archive from there.

        @return: a L{zippath.ZipPath} or L{zippath.ZipArchive} instance.
        """
        za = ZipArchive(self.importer.archive)
        myPath = FilePath(self.importer.archive)
        itsPath = FilePath(fsPathString)
        if myPath == itsPath:
            return za
        else:
            segs = itsPath.segmentsFrom(myPath)
            zp = za
            for seg in segs:
                zp = zp.child(seg)

            return zp


registerAdapter(_ZipMapImpl, zipimport.zipimporter, IPathImportMapper)

def _defaultSysPathFactory():
    """
    Provide the default behavior of PythonPath's sys.path factory, which is to
    return the current value of sys.path.

    @return: L{sys.path}
    """
    return sys.path


class PythonPath:
    __doc__ = "\n    I represent the very top of the Python object-space, the module list in\n    C{sys.path} and the modules list in C{sys.modules}.\n\n    @ivar _sysPath: A sequence of strings like C{sys.path}.  This attribute is\n    read-only.\n\n    @ivar sysPath: The current value of the module search path list.\n    @type sysPath: C{list}\n\n    @ivar moduleDict: A dictionary mapping string module names to module\n    objects, like C{sys.modules}.\n\n    @ivar sysPathHooks: A list of PEP-302 path hooks, like C{sys.path_hooks}.\n\n    @ivar moduleLoader: A function that takes a fully-qualified python name and\n    returns a module, like L{twisted.python.reflect.namedAny}.\n    "

    def __init__(self, sysPath=None, moduleDict=sys.modules, sysPathHooks=sys.path_hooks, importerCache=sys.path_importer_cache, moduleLoader=namedAny, sysPathFactory=None):
        """
        Create a PythonPath.  You almost certainly want to use
        modules.theSystemPath, or its aliased methods, rather than creating a
        new instance yourself, though.

        All parameters are optional, and if unspecified, will use 'system'
        equivalents that makes this PythonPath like the global L{theSystemPath}
        instance.

        @param sysPath: a sys.path-like list to use for this PythonPath, to
        specify where to load modules from.

        @param moduleDict: a sys.modules-like dictionary to use for keeping
        track of what modules this PythonPath has loaded.

        @param sysPathHooks: sys.path_hooks-like list of PEP-302 path hooks to
        be used for this PythonPath, to determie which importers should be
        used.

        @param importerCache: a sys.path_importer_cache-like list of PEP-302
        importers.  This will be used in conjunction with the given
        sysPathHooks.

        @param moduleLoader: a module loader function which takes a string and
        returns a module.  That is to say, it is like L{namedAny} - *not* like
        L{__import__}.

        @param sysPathFactory: a 0-argument callable which returns the current
        value of a sys.path-like list of strings.  Specify either this, or
        sysPath, not both.  This alternative interface is provided because the
        way the Python import mechanism works, you can re-bind the 'sys.path'
        name and that is what is used for current imports, so it must be a
        factory rather than a value to deal with modification by rebinding
        rather than modification by mutation.  Note: it is not recommended to
        rebind sys.path.  Although this mechanism can deal with that, it is a
        subtle point which some tools that it is easy for tools which interact
        with sys.path to miss.
        """
        if sysPath is not None:
            sysPathFactory = lambda: sysPath
        else:
            if sysPathFactory is None:
                sysPathFactory = _defaultSysPathFactory
        self._sysPathFactory = sysPathFactory
        self._sysPath = sysPath
        self.moduleDict = moduleDict
        self.sysPathHooks = sysPathHooks
        self.importerCache = importerCache
        self.moduleLoader = moduleLoader

    def _getSysPath(self):
        """
        Retrieve the current value of the module search path list.
        """
        return self._sysPathFactory()

    sysPath = property(_getSysPath)

    def _findEntryPathString(self, modobj):
        """
        Determine where a given Python module object came from by looking at path
        entries.
        """
        topPackageObj = modobj
        while "." in topPackageObj.__name__:
            topPackageObj = self.moduleDict[".".join(topPackageObj.__name__.split(".")[:-1])]

        if _isPackagePath(FilePath(topPackageObj.__file__)):
            rval = dirname(dirname(topPackageObj.__file__))
        else:
            rval = dirname(topPackageObj.__file__)
        if rval not in self.importerCache:
            warnings.warn(("%s (for module %s) not in path importer cache (PEP 302 violation - check your local configuration)." % (
             rval, modobj.__name__)),
              stacklevel=3)
        return rval

    def _smartPath(self, pathName):
        """
        Given a path entry from sys.path which may refer to an importer,
        return the appropriate FilePath-like instance.

        @param pathName: a str describing the path.

        @return: a FilePath-like object.
        """
        importr = self.importerCache.get(pathName, _nothing)
        if importr is _nothing:
            for hook in self.sysPathHooks:
                try:
                    importr = hook(pathName)
                except ImportError:
                    pass

            if importr is _nothing:
                importr = None
        return IPathImportMapper(importr, _theDefaultMapper).mapPath(pathName)

    def iterEntries(self):
        """
        Iterate the entries on my sysPath.

        @return: a generator yielding PathEntry objects
        """
        for pathName in self.sysPath:
            fp = self._smartPath(pathName)
            yield PathEntry(fp, self)

    def __getitem__(self, modname):
        """
        Get a python module by its given fully-qualified name.

        @param modname: The fully-qualified Python module name to load.

        @type modname: C{str}

        @return: an object representing the module identified by C{modname}

        @rtype: L{PythonModule}

        @raise KeyError: if the module name is not a valid module name, or no
            such module can be identified as loadable.
        """
        moduleObject = self.moduleDict.get(modname)
        if moduleObject is not None:
            pe = PathEntry(self._smartPath(self._findEntryPathString(moduleObject)), self)
            mp = self._smartPath(moduleObject.__file__)
            return PythonModule(modname, mp, pe)
        if "." in modname:
            pkg = self
            for name in modname.split("."):
                pkg = pkg[name]

            return pkg
        for module in self.iterModules():
            if module.name == modname:
                return module

        raise KeyError(modname)

    def __contains__(self, module):
        """
        Check to see whether or not a module exists on my import path.

        @param module: The name of the module to look for on my import path.
        @type module: C{str}
        """
        try:
            self.__getitem__(module)
            return True
        except KeyError:
            return False

    def __repr__(self):
        """
        Display my sysPath and moduleDict in a string representation.
        """
        return "PythonPath(%r,%r)" % (self.sysPath, self.moduleDict)

    def iterModules(self):
        """
        Yield all top-level modules on my sysPath.
        """
        for entry in self.iterEntries():
            for module in entry.iterModules():
                yield module

    def walkModules(self, importPackages=False):
        """
        Similar to L{iterModules}, this yields every module on the path, then every
        submodule in each package or entry.
        """
        for package in self.iterModules():
            for module in package.walkModules(importPackages=False):
                yield module


theSystemPath = PythonPath()

def walkModules(importPackages=False):
    """
    Deeply iterate all modules on the global python path.

    @param importPackages: Import packages as they are seen.
    """
    return theSystemPath.walkModules(importPackages=importPackages)


def iterModules():
    """
    Iterate all modules and top-level packages on the global Python path, but
    do not descend into packages.

    @param importPackages: Import packages as they are seen.
    """
    return theSystemPath.iterModules()


def getModule(moduleName):
    """
    Retrieve a module from the system path.
    """
    return theSystemPath[moduleName]