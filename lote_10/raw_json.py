# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: simplejson\raw_json.py
"""Implementation of RawJSON
"""

class RawJSON(object):
    __doc__ = "Wrap an encoded JSON document for direct embedding in the output\n\n    "

    def __init__(self, encoded_json):
        self.encoded_json = encoded_json
