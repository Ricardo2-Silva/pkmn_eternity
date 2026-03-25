# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: constantly\_version.py
import json, sys
version_json = '\n{\n "dirty": false,\n "error": null,\n "full-revisionid": "c8375a7e3431792ea1b1b44678f3f6878d5e8c9a",\n "version": "15.1.0"\n}\n'

def get_versions():
    return json.loads(version_json)
