# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\data\patcher.py
"""
Created on Sep 22, 2011

@author: Ragnarok
"""
import os

class PatchSettings:
    patchFolder = "patches/"
    patchStorage = os.path.join(os.curdir, "patches")


libs = ('.zip', '.pe')

class PatchFile:

    def __init__(self, filename):
        self.filename = filename
        self.downloaded = False
        self.isZip = os.path.splitext(filename)[1] in libs


class BuildInfo:
    __doc__ = "Contains information on patch files"

    def __init__(self, build):
        self.version = build["version"]
        self.add_files = build["add-files"]
        self.del_files = build["del-files"]
        self.del_library = build["del-library"]
        self.files_to_download = [PatchFile(filename) for filename in self.add_files]

    @property
    def completed(self):
        for patchfile in self.files_to_download:
            if patchfile.downloaded is False:
                return False

        return True
