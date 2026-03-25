# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: lxml\html\soupparser.py
"""External interface to the BeautifulSoup HTML parser.
"""
__all__ = [
 "fromstring", "parse", "convert_tree"]
import re
from lxml import etree, html
try:
    from bs4 import BeautifulSoup, Tag, Comment, ProcessingInstruction, NavigableString, Declaration, Doctype
    _DECLARATION_OR_DOCTYPE = (
     Declaration, Doctype)
except ImportError:
    from BeautifulSoup import BeautifulSoup, Tag, Comment, ProcessingInstruction, NavigableString, Declaration
    _DECLARATION_OR_DOCTYPE = Declaration

def fromstring(data, beautifulsoup=None, makeelement=None, **bsargs):
    """Parse a string of HTML data into an Element tree using the
    BeautifulSoup parser.

    Returns the root ``<html>`` Element of the tree.

    You can pass a different BeautifulSoup parser through the
    `beautifulsoup` keyword, and a diffent Element factory function
    through the `makeelement` keyword.  By default, the standard
    ``BeautifulSoup`` class and the default factory of `lxml.html` are
    used.
    """
    return _parse(data, beautifulsoup, makeelement, **bsargs)


def parse(file, beautifulsoup=None, makeelement=None, **bsargs):
    """Parse a file into an ElemenTree using the BeautifulSoup parser.

    You can pass a different BeautifulSoup parser through the
    `beautifulsoup` keyword, and a diffent Element factory function
    through the `makeelement` keyword.  By default, the standard
    ``BeautifulSoup`` class and the default factory of `lxml.html` are
    used.
    """
    if not hasattr(file, "read"):
        file = open(file)
    root = _parse(file, beautifulsoup, makeelement, **bsargs)
    return etree.ElementTree(root)


def convert_tree(beautiful_soup_tree, makeelement=None):
    """Convert a BeautifulSoup tree to a list of Element trees.

    Returns a list instead of a single root Element to support
    HTML-like soup with more than one root element.

    You can pass a different Element factory through the `makeelement`
    keyword.
    """
    root = _convert_tree(beautiful_soup_tree, makeelement)
    children = root.getchildren()
    for child in children:
        root.remove(child)

    return children


def _parse(source, beautifulsoup, makeelement, **bsargs):
    if beautifulsoup is None:
        beautifulsoup = BeautifulSoup
    elif hasattr(beautifulsoup, "HTML_ENTITIES"):
        if "convertEntities" not in bsargs:
            bsargs["convertEntities"] = "html"
    else:
        if hasattr(beautifulsoup, "DEFAULT_BUILDER_FEATURES"):
            if "features" not in bsargs:
                bsargs["features"] = "html.parser"
        tree = beautifulsoup(source, **bsargs)
        root = _convert_tree(tree, makeelement)
        if len(root) == 1:
            if root[0].tag == "html":
                return root[0]
    root.tag = "html"
    return root


_parse_doctype_declaration = re.compile('(?:\\s|[<!])*DOCTYPE\\s*HTML(?:\\s+PUBLIC)?(?:\\s+(\\\'[^\\\']*\\\'|"[^"]*"))?(?:\\s+(\\\'[^\\\']*\\\'|"[^"]*"))?', re.IGNORECASE).match

class _PseudoTag:

    def __init__(self, contents):
        self.name = "html"
        self.attrs = []
        self.contents = contents

    def __iter__(self):
        return self.contents.__iter__()


def _convert_tree(beautiful_soup_tree, makeelement):
    if makeelement is None:
        makeelement = html.html_parser.makeelement
    else:
        first_element_idx = last_element_idx = None
        html_root = declaration = None
        for i, e in enumerate(beautiful_soup_tree):
            if isinstance(e, Tag):
                if first_element_idx is None:
                    first_element_idx = i
                last_element_idx = i
                if html_root is None and e.name and e.name.lower() == "html":
                    html_root = e
            else:
                if declaration is None:
                    if isinstance(e, _DECLARATION_OR_DOCTYPE):
                        declaration = e

        if first_element_idx is None:
            pre_root = post_root = []
            roots = beautiful_soup_tree.contents
        else:
            pre_root = beautiful_soup_tree.contents[:first_element_idx]
            roots = beautiful_soup_tree.contents[first_element_idx:last_element_idx + 1]
            post_root = beautiful_soup_tree.contents[last_element_idx + 1:]
        if html_root is not None:
            i = roots.index(html_root)
            html_root.contents = roots[:i] + html_root.contents + roots[i + 1:]
        else:
            html_root = _PseudoTag(roots)
    convert_node = _init_node_converters(makeelement)
    res_root = convert_node(html_root)
    prev = res_root
    for e in reversed(pre_root):
        converted = convert_node(e)
        if converted is not None:
            prev.addprevious(converted)
            prev = converted

    prev = res_root
    for e in post_root:
        converted = convert_node(e)
        if converted is not None:
            prev.addnext(converted)
            prev = converted

    if declaration is not None:
        try:
            doctype_string = declaration.output_ready()
        except AttributeError:
            doctype_string = declaration.string

        match = _parse_doctype_declaration(doctype_string)
        if not match:
            pass
        else:
            external_id, sys_uri = match.groups()
            docinfo = res_root.getroottree().docinfo
            docinfo.public_id = external_id and external_id[1:-1]
            docinfo.system_url = sys_uri and sys_uri[1:-1]
    return res_root


def _init_node_converters(makeelement):
    converters = {}
    ordered_node_types = []

    def converter(*types):

        def add(handler):
            for t in types:
                converters[t] = handler
                ordered_node_types.append(t)

            return handler

        return add

    def find_best_converter(node):
        for t in ordered_node_types:
            if isinstance(node, t):
                return converters[t]

        return

    def convert_node(bs_node, parent=None):
        try:
            handler = converters[type(bs_node)]
        except KeyError:
            handler = converters[type(bs_node)] = find_best_converter(bs_node)

        if handler is None:
            return
        else:
            return handler(bs_node, parent)

    def map_attrs(bs_attrs):
        if isinstance(bs_attrs, dict):
            attribs = {}
            for k, v in bs_attrs.items():
                if isinstance(v, list):
                    v = " ".join(v)
                attribs[k] = unescape(v)

        else:
            attribs = dict((k, unescape(v)) for k, v in bs_attrs)
        return attribs

    def append_text(parent, text):
        if len(parent) == 0:
            parent.text = (parent.text or "") + text
        else:
            parent[-1].tail = (parent[-1].tail or "") + text

    @converter(Tag, _PseudoTag)
    def convert_tag(bs_node, parent):
        attrs = bs_node.attrs
        if parent is not None:
            attribs = map_attrs(attrs) if attrs else None
            res = etree.SubElement(parent, (bs_node.name), attrib=attribs)
        else:
            attribs = map_attrs(attrs) if attrs else {}
            res = makeelement((bs_node.name), attrib=attribs)
        for child in bs_node:
            try:
                handler = converters[type(child)]
            except KeyError:
                pass
            else:
                if handler is not None:
                    handler(child, res)
                    continue
                convert_node(child, res)

        return res

    @converter(Comment)
    def convert_comment(bs_node, parent):
        res = html.HtmlComment(bs_node)
        if parent is not None:
            parent.append(res)
        return res

    @converter(ProcessingInstruction)
    def convert_pi(bs_node, parent):
        if bs_node.endswith("?"):
            bs_node = bs_node[:-1]
        res = (etree.ProcessingInstruction)(*bs_node.split(" ", 1))
        if parent is not None:
            parent.append(res)
        return res

    @converter(NavigableString)
    def convert_text(bs_node, parent):
        if parent is not None:
            append_text(parent, unescape(bs_node))
        return

    return convert_node


try:
    from html.entities import name2codepoint
except ImportError:
    from htmlentitydefs import name2codepoint

handle_entities = re.compile("&(\\w+);").sub
try:
    unichr
except NameError:
    unichr = chr

def unescape(string):
    if not string:
        return ""
    else:

        def unescape_entity(m):
            try:
                return unichr(name2codepoint[m.group(1)])
            except KeyError:
                return m.group(0)

        return handle_entities(unescape_entity, string)
