# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\plugin.py
"""
Plugin system for Twisted.

@author: Jp Calderone
@author: Glyph Lefkowitz
"""
from __future__ import absolute_import, division
import os, sys
from zope.interface import Interface, providedBy

def _determinePickleModule():
    """
    Determine which 'pickle' API module to use.
    """
    try:
        import cPickle
        return cPickle
    except ImportError:
        import pickle
        return pickle


pickle = _determinePickleModule()
from twisted.python.components import getAdapterFactory
from twisted.python.reflect import namedAny
from twisted.python import log
from twisted.python.modules import getModule
from twisted.python.compat import iteritems

class IPlugin(Interface):
    __doc__ = "\n    Interface that must be implemented by all plugins.\n\n    Only objects which implement this interface will be considered for return\n    by C{getPlugins}.  To be useful, plugins should also implement some other\n    application-specific interface.\n    "


class CachedPlugin(object):

    def __init__(self, dropin, name, description, provided):
        self.dropin = dropin
        self.name = name
        self.description = description
        self.provided = provided
        self.dropin.plugins.append(self)

    def __repr__(self):
        return "<CachedPlugin %r/%r (provides %r)>" % (
         self.name, self.dropin.moduleName,
         ", ".join([i.__name__ for i in self.provided]))

    def load(self):
        return namedAny(self.dropin.moduleName + "." + self.name)

    def __conform__(self, interface, registry=None, default=None):
        for providedInterface in self.provided:
            if providedInterface.isOrExtends(interface):
                return self.load()
            if getAdapterFactory(providedInterface, interface, None) is not None:
                return interface(self.load(), default)

        return default

    getComponent = __conform__


class CachedDropin(object):
    __doc__ = "\n    A collection of L{CachedPlugin} instances from a particular module in a\n    plugin package.\n\n    @type moduleName: C{str}\n    @ivar moduleName: The fully qualified name of the plugin module this\n        represents.\n\n    @type description: C{str} or L{None}\n    @ivar description: A brief explanation of this collection of plugins\n        (probably the plugin module's docstring).\n\n    @type plugins: C{list}\n    @ivar plugins: The L{CachedPlugin} instances which were loaded from this\n        dropin.\n    "

    def __init__(self, moduleName, description):
        self.moduleName = moduleName
        self.description = description
        self.plugins = []


def _generateCacheEntry(provider):
    dropin = CachedDropin(provider.__name__, provider.__doc__)
    for k, v in iteritems(provider.__dict__):
        plugin = IPlugin(v, None)
        if plugin is not None:
            CachedPlugin(dropin, k, v.__doc__, list(providedBy(plugin)))

    return dropin


try:
    fromkeys = dict.fromkeys
except AttributeError:

    def fromkeys(keys, value=None):
        d = {}
        for k in keys:
            d[k] = value

        return d


def getCache(module):
    """
    Compute all the possible loadable plugins, while loading as few as
    possible and hitting the filesystem as little as possible.

    @param module: a Python module object.  This represents a package to search
    for plugins.

    @return: a dictionary mapping module names to L{CachedDropin} instances.
    """
    allCachesCombined = {}
    mod = getModule(module.__name__)
    buckets = {}
    for plugmod in mod.iterModules():
        fpp = plugmod.filePath.parent()
        if fpp not in buckets:
            buckets[fpp] = []
        bucket = buckets[fpp]
        bucket.append(plugmod)

    for pseudoPackagePath, bucket in iteritems(buckets):
        dropinPath = pseudoPackagePath.child("dropin.cache")
        try:
            lastCached = dropinPath.getModificationTime()
            with dropinPath.open("r") as f:
                dropinDotCache = pickle.load(f)
        except:
            dropinDotCache = {}
            lastCached = 0

        needsWrite = False
        existingKeys = {}
        for pluginModule in bucket:
            pluginKey = pluginModule.name.split(".")[-1]
            existingKeys[pluginKey] = True
            if pluginKey not in dropinDotCache or pluginModule.filePath.getModificationTime() >= lastCached:
                needsWrite = True
                try:
                    provider = pluginModule.load()
                except:
                    log.err()

                entry = _generateCacheEntry(provider)
                dropinDotCache[pluginKey] = entry

        for pluginKey in list(dropinDotCache.keys()):
            if pluginKey not in existingKeys:
                del dropinDotCache[pluginKey]
                needsWrite = True

        if needsWrite:
            try:
                dropinPath.setContent(pickle.dumps(dropinDotCache))
            except OSError as e:
                log.msg(format="Unable to write to plugin cache %(path)s: error number %(errno)d",
                  path=(dropinPath.path),
                  errno=(e.errno))
            except:
                log.err(None, "Unexpected error while writing cache file")

            allCachesCombined.update(dropinDotCache)

    return allCachesCombined


def getPlugins(interface, package=None):
    """
    Retrieve all plugins implementing the given interface beneath the given module.

    @param interface: An interface class.  Only plugins which implement this
    interface will be returned.

    @param package: A package beneath which plugins are installed.  For
    most uses, the default value is correct.

    @return: An iterator of plugins.
    """
    if package is None:
        import twisted.plugins as package
    allDropins = getCache(package)
    for key, dropin in iteritems(allDropins):
        for plugin in dropin.plugins:
            try:
                adapted = interface(plugin, None)
            except:
                log.err()
            else:
                if adapted is not None:
                    yield adapted


getPlugIns = getPlugins

def pluginPackagePaths(name):
    """
    Return a list of additional directories which should be searched for
    modules to be included as part of the named plugin package.

    @type name: C{str}
    @param name: The fully-qualified Python name of a plugin package, eg
        C{'twisted.plugins'}.

    @rtype: C{list} of C{str}
    @return: The absolute paths to other directories which may contain plugin
        modules for the named plugin package.
    """
    package = name.split(".")
    return [os.path.abspath((os.path.join)(x, *package)) for x in sys.path if not os.path.exists((os.path.join)(x, *package + ["__init__.py"]))]


__all__ = [
 "getPlugins", "pluginPackagePaths"]
