# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: PyInstaller\hooks\rthooks\pyi_rth_pkgutil.py
import os, pkgutil, sys
from pyimod03_importers import FrozenImporter
_orig_pkgutil_iter_modules = pkgutil.iter_modules

def _pyi_pkgutil_iter_modules(path=None, prefix=''):
    yield from _orig_pkgutil_iter_modules(path, prefix)
    for importer in pkgutil.iter_importers():
        if isinstance(importer, FrozenImporter):
            break
    else:
        return

    if not path:
        for entry in importer.toc:
            if entry.count(".") != 0:
                pass
            else:
                is_pkg = importer.is_package(entry)
                yield pkgutil.ModuleInfo(importer, prefix + entry, is_pkg)

    else:
        SYS_PREFIX = sys._MEIPASS + os.path.sep
        SYS_PREFIXLEN = len(SYS_PREFIX)
        pkg_path = os.path.normpath(path[0])
        assert pkg_path.startswith(SYS_PREFIX)
        pkg_prefix = pkg_path[SYS_PREFIXLEN:]
        pkg_prefix = pkg_prefix.replace(os.path.sep, ".")
        if not pkg_prefix.endswith("."):
            pkg_prefix += "."
        pkg_prefix_len = len(pkg_prefix)
        for entry in importer.toc:
            if not entry.startswith(pkg_prefix):
                pass
            else:
                name = entry[pkg_prefix_len:]
                if name.count(".") != 0:
                    continue
                    is_pkg = importer.is_package(entry)
                    yield pkgutil.ModuleInfo(importer, prefix + name, is_pkg)


pkgutil.iter_modules = _pyi_pkgutil_iter_modules
