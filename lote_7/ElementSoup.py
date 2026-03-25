# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: lxml\html\ElementSoup.py
"""Legacy interface to the BeautifulSoup HTML parser.
"""
__all__ = [
 "parse", "convert_tree"]
from soupparser import convert_tree, parse as _parse

def parse(file, beautifulsoup=None, makeelement=None):
    root = _parse(file, beautifulsoup=beautifulsoup, makeelement=makeelement)
    return root.getroot()
