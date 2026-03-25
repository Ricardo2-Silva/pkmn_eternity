# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: lxml\html\html5parser.py
"""
An interface to html5lib that mimics the lxml.html interface.
"""
import sys, string
from html5lib import HTMLParser as _HTMLParser
from html5lib.treebuilders.etree_lxml import TreeBuilder
from lxml import etree
from lxml.html import Element, XHTML_NAMESPACE, _contains_block_level_tag
try:
    _strings = basestring
except NameError:
    _strings = (
     bytes, str)

try:
    from urllib2 import urlopen
except ImportError:
    from urllib.request import urlopen

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

class HTMLParser(_HTMLParser):
    __doc__ = "An html5lib HTML parser with lxml as tree."

    def __init__(self, strict=False, **kwargs):
        (_HTMLParser.__init__)(self, strict=strict, tree=TreeBuilder, **kwargs)


try:
    from html5lib import XHTMLParser as _XHTMLParser
except ImportError:
    pass
else:

    class XHTMLParser(_XHTMLParser):
        __doc__ = "An html5lib XHTML Parser with lxml as tree."

        def __init__(self, strict=False, **kwargs):
            (_XHTMLParser.__init__)(self, strict=strict, tree=TreeBuilder, **kwargs)


    xhtml_parser = XHTMLParser()

def _find_tag(tree, tag):
    elem = tree.find(tag)
    if elem is not None:
        return elem
    else:
        return tree.find("{%s}%s" % (XHTML_NAMESPACE, tag))


def document_fromstring(html, guess_charset=None, parser=None):
    """
    Parse a whole document into a string.

    If `guess_charset` is true, or if the input is not Unicode but a
    byte string, the `chardet` library will perform charset guessing
    on the string.
    """
    if not isinstance(html, _strings):
        raise TypeError("string required")
    else:
        if parser is None:
            parser = html_parser
        options = {}
        if guess_charset is None:
            if isinstance(html, bytes):
                guess_charset = True
        if guess_charset is not None:
            options["useChardet"] = guess_charset
    return (parser.parse)(html, **options).getroot()


def fragments_fromstring(html, no_leading_text=False, guess_charset=None, parser=None):
    """Parses several HTML elements, returning a list of elements.

    The first item in the list may be a string.  If no_leading_text is true,
    then it will be an error if there is leading text, and it will always be
    a list of only elements.

    If `guess_charset` is true, the `chardet` library will perform charset
    guessing on the string.
    """
    if not isinstance(html, _strings):
        raise TypeError("string required")
    elif parser is None:
        parser = html_parser
    else:
        options = {}
        if guess_charset is None:
            if isinstance(html, bytes):
                guess_charset = False
        if guess_charset is not None:
            options["useChardet"] = guess_charset
        children = (parser.parseFragment)(html, "div", **options)
        if children:
            if isinstance(children[0], _strings):
                if no_leading_text:
                    if children[0].strip():
                        raise etree.ParserError("There is leading text: %r" % children[0])
                    del children[0]
    return children


def fragment_fromstring(html, create_parent=False, guess_charset=None, parser=None):
    """Parses a single HTML element; it is an error if there is more than
    one element, or if anything but whitespace precedes or follows the
    element.

    If 'create_parent' is true (or is a tag name) then a parent node
    will be created to encapsulate the HTML in a single element.  In
    this case, leading or trailing text is allowed.

    If `guess_charset` is true, the `chardet` library will perform charset
    guessing on the string.
    """
    if not isinstance(html, _strings):
        raise TypeError("string required")
    accept_leading_text = bool(create_parent)
    elements = fragments_fromstring(html,
      guess_charset=guess_charset, parser=parser, no_leading_text=(not accept_leading_text))
    if create_parent:
        if not isinstance(create_parent, _strings):
            create_parent = "div"
        new_root = Element(create_parent)
        if elements:
            if isinstance(elements[0], _strings):
                new_root.text = elements[0]
                del elements[0]
            new_root.extend(elements)
        return new_root
    else:
        if not elements:
            raise etree.ParserError("No elements found")
        else:
            if len(elements) > 1:
                raise etree.ParserError("Multiple elements found")
            result = elements[0]
            if result.tail:
                if result.tail.strip():
                    raise etree.ParserError("Element followed by text: %r" % result.tail)
        result.tail = None
        return result


def fromstring(html, guess_charset=None, parser=None):
    """Parse the html, returning a single element/document.

    This tries to minimally parse the chunk of text, without knowing if it
    is a fragment or a document.

    'base_url' will set the document's base_url attribute (and the tree's
    docinfo.URL)

    If `guess_charset` is true, or if the input is not Unicode but a
    byte string, the `chardet` library will perform charset guessing
    on the string.
    """
    if not isinstance(html, _strings):
        raise TypeError("string required")
    else:
        doc = document_fromstring(html, parser=parser, guess_charset=guess_charset)
        start = html[:50]
        if isinstance(start, bytes):
            start = start.decode("ascii", "replace")
        start = start.lstrip().lower()
        if start.startswith("<html") or start.startswith("<!doctype"):
            return doc
    head = _find_tag(doc, "head")
    if len(head):
        return doc
    else:
        body = _find_tag(doc, "body")
        if len(body) == 1:
            if not body.text or not body.text.strip():
                if not body[-1].tail or not body[-1].tail.strip():
                    return body[0]
            if _contains_block_level_tag(body):
                body.tag = "div"
        else:
            body.tag = "span"
        return body


def parse(filename_url_or_file, guess_charset=None, parser=None):
    """Parse a filename, URL, or file-like object into an HTML document
    tree.  Note: this returns a tree, not an element.  Use
    ``parse(...).getroot()`` to get the document root.

    If ``guess_charset`` is true, the ``useChardet`` option is passed into
    html5lib to enable character detection.  This option is on by default
    when parsing from URLs, off by default when parsing from file(-like)
    objects (which tend to return Unicode more often than not), and on by
    default when parsing from a file path (which is read in binary mode).
    """
    if parser is None:
        parser = html_parser
    elif not isinstance(filename_url_or_file, _strings):
        fp = filename_url_or_file
        if guess_charset is None:
            guess_charset = False
        elif _looks_like_url(filename_url_or_file):
            fp = urlopen(filename_url_or_file)
            if guess_charset is None:
                guess_charset = True
    else:
        fp = open(filename_url_or_file, "rb")
        if guess_charset is None:
            guess_charset = True
    options = {}
    if guess_charset:
        options["useChardet"] = guess_charset
    return (parser.parse)(fp, **options)


def _looks_like_url(str):
    scheme = urlparse(str)[0]
    if not scheme:
        return False
    else:
        if sys.platform == "win32":
            if scheme in string.ascii_letters:
                if len(scheme) == 1:
                    return False
        return True


html_parser = HTMLParser()
