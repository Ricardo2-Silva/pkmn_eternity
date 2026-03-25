# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\data\exceptions.py
"""
Created on 1 juil. 2011

@author: Kami
"""

class MustBeImplemented(Exception):

    def __init__(self, *args):
        (Exception.__init__)(self, "This method must be implemented.", *args)
