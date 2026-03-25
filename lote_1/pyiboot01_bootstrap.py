# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: PyInstaller\loader\pyiboot01_bootstrap.py
import sys, pyimod03_importers
pyimod03_importers.install()
import os
if not hasattr(sys, "frozen"):
    sys.frozen = True
sys.prefix = sys._MEIPASS
sys.exec_prefix = sys.prefix
sys.base_prefix = sys.prefix
sys.base_exec_prefix = sys.exec_prefix
VIRTENV = "VIRTUAL_ENV"
if VIRTENV in os.environ:
    os.environ[VIRTENV] = ""
    del os.environ[VIRTENV]
python_path = []
for pth in sys.path:
    python_path.append(os.path.abspath(pth))
    sys.path = python_path

class NullWriter:
    softspace = 0
    encoding = "UTF-8"

    def write(*args):
        return

    def flush(*args):
        return

    def isatty(self):
        return False


if sys.stdout is None:
    sys.stdout = NullWriter()
if sys.stderr is None:
    sys.stderr = NullWriter()
try:
    import encodings
except ImportError:
    pass

if sys.warnoptions:
    import warnings
import pyimod04_ctypes
pyimod04_ctypes.install()
d = "eggs"
d = os.path.join(sys._MEIPASS, d)
if os.path.isdir(d):
    for fn in os.listdir(d):
        sys.path.append(os.path.join(d, fn))
