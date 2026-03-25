# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: PyInstaller\hooks\rthooks\pyi_rth_inspect.py
import inspect, os, sys
_orig_inspect_getsourcefile = inspect.getsourcefile

def _pyi_getsourcefile(object):
    filename = inspect.getfile(object)
    if not os.path.isabs(filename):
        main_file = sys.modules["__main__"].__file__
        if filename == os.path.basename(main_file):
            return main_file
        if filename.endswith(".py"):
            filename = os.path.normpath(os.path.join(sys._MEIPASS, filename + "c"))
            if filename.startswith(sys._MEIPASS):
                return filename
    else:
        if filename.startswith(sys._MEIPASS):
            if filename.endswith(".pyc"):
                return filename
        return _orig_inspect_getsourcefile(object)


inspect.getsourcefile = _pyi_getsourcefile
