# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: lxml\cssselect.py
"""CSS Selectors based on XPath.

This module supports selecting XML/HTML tags based on CSS selectors.
See the `CSSSelector` class for details.

This is a thin wrapper around cssselect 0.7 or later.
"""
from __future__ import absolute_import
from . import etree
try:
    import cssselect as external_cssselect
except ImportError:
    raise ImportError("cssselect does not seem to be installed. See http://packages.python.org/cssselect/")

SelectorSyntaxError = external_cssselect.SelectorSyntaxError
ExpressionError = external_cssselect.ExpressionError
SelectorError = external_cssselect.SelectorError
__all__ = [
 "SelectorSyntaxError", "ExpressionError", "SelectorError",
 "CSSSelector"]

class LxmlTranslator(external_cssselect.GenericTranslator):
    __doc__ = "\n    A custom CSS selector to XPath translator with lxml-specific extensions.\n    "

    def xpath_contains_function(self, xpath, function):
        if function.argument_types() not in (["STRING"], ["IDENT"]):
            raise ExpressionError("Expected a single string or ident for :contains(), got %r" % function.arguments)
        value = function.arguments[0].value
        return xpath.add_condition("contains(__lxml_internal_css:lower-case(string(.)), %s)" % self.xpath_literal(value.lower()))


class LxmlHTMLTranslator(LxmlTranslator, external_cssselect.HTMLTranslator):
    __doc__ = "\n    lxml extensions + HTML support.\n    "


def _make_lower_case(context, s):
    return s.lower()


ns = etree.FunctionNamespace("http://codespeak.net/lxml/css/")
ns.prefix = "__lxml_internal_css"
ns["lower-case"] = _make_lower_case

class CSSSelector(etree.XPath):
    __doc__ = 'A CSS selector.\n\n    Usage::\n\n        >>> from lxml import etree, cssselect\n        >>> select = cssselect.CSSSelector("a tag > child")\n\n        >>> root = etree.XML("<a><b><c/><tag><child>TEXT</child></tag></b></a>")\n        >>> [ el.tag for el in select(root) ]\n        [\'child\']\n\n    To use CSS namespaces, you need to pass a prefix-to-namespace\n    mapping as ``namespaces`` keyword argument::\n\n        >>> rdfns = \'http://www.w3.org/1999/02/22-rdf-syntax-ns#\'\n        >>> select_ns = cssselect.CSSSelector(\'root > rdf|Description\',\n        ...                                   namespaces={\'rdf\': rdfns})\n\n        >>> rdf = etree.XML((\n        ...     \'<root xmlns:rdf="%s">\'\n        ...       \'<rdf:Description>blah</rdf:Description>\'\n        ...     \'</root>\') % rdfns)\n        >>> [(el.tag, el.text) for el in select_ns(rdf)]\n        [(\'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description\', \'blah\')]\n\n    '

    def __init__(self, css, namespaces=None, translator='xml'):
        if translator == "xml":
            translator = LxmlTranslator()
        elif translator == "html":
            translator = LxmlHTMLTranslator()
        else:
            if translator == "xhtml":
                translator = LxmlHTMLTranslator(xhtml=True)
        path = translator.css_to_xpath(css)
        etree.XPath.__init__(self, path, namespaces=namespaces)
        self.css = css

    def __repr__(self):
        return "<%s %s for %r>" % (
         self.__class__.__name__,
         hex(abs(id(self)))[2:],
         self.css)
