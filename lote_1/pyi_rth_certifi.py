# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: _pyinstaller_hooks_contrib\hooks\rthooks\pyi_rth_certifi.py
import os, ssl, sys
if ssl.get_default_verify_paths().cafile is None:
    os.environ["SSL_CERT_FILE"] = os.path.join(sys._MEIPASS, "certifi", "cacert.pem")
