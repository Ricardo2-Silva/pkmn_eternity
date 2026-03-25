# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\web\_stan.py
"""
An s-expression-like syntax for expressing xml in pure python.

Stan tags allow you to build XML documents using Python.

Stan is a DOM, or Document Object Model, implemented using basic Python types
and functions called "flatteners". A flattener is a function that knows how to
turn an object of a specific type into something that is closer to an HTML
string. Stan differs from the W3C DOM by not being as cumbersome and heavy
weight. Since the object model is built using simple python types such as lists,
strings, and dictionaries, the API is simpler and constructing a DOM less
cumbersome.

@var voidElements: the names of HTML 'U{void
    elements<http://www.whatwg.org/specs/web-apps/current-work/multipage/syntax.html#void-elements>}';
    those which can't have contents and can therefore be self-closing in the
    output.
"""
from __future__ import absolute_import, division
from twisted.python.compat import iteritems

class slot(object):
    __doc__ = "\n    Marker for markup insertion in a template.\n\n    @type name: C{str}\n    @ivar name: The name of this slot.  The key which must be used in\n        L{Tag.fillSlots} to fill it.\n\n    @type children: C{list}\n    @ivar children: The L{Tag} objects included in this L{slot}'s template.\n\n    @type default: anything flattenable, or L{None}\n    @ivar default: The default contents of this slot, if it is left unfilled.\n        If this is L{None}, an L{UnfilledSlot} will be raised, rather than\n        L{None} actually being used.\n\n    @type filename: C{str} or L{None}\n    @ivar filename: The name of the XML file from which this tag was parsed.\n        If it was not parsed from an XML file, L{None}.\n\n    @type lineNumber: C{int} or L{None}\n    @ivar lineNumber: The line number on which this tag was encountered in the\n        XML file from which it was parsed.  If it was not parsed from an XML\n        file, L{None}.\n\n    @type columnNumber: C{int} or L{None}\n    @ivar columnNumber: The column number at which this tag was encountered in\n        the XML file from which it was parsed.  If it was not parsed from an\n        XML file, L{None}.\n    "

    def __init__(self, name, default=None, filename=None, lineNumber=None, columnNumber=None):
        self.name = name
        self.children = []
        self.default = default
        self.filename = filename
        self.lineNumber = lineNumber
        self.columnNumber = columnNumber

    def __repr__(self):
        return "slot(%r)" % (self.name,)


class Tag(object):
    __doc__ = '\n    A L{Tag} represents an XML tags with a tag name, attributes, and children.\n    A L{Tag} can be constructed using the special L{twisted.web.template.tags}\n    object, or it may be constructed directly with a tag name. L{Tag}s have a\n    special method, C{__call__}, which makes representing trees of XML natural\n    using pure python syntax.\n\n    @ivar tagName: The name of the represented element.  For a tag like\n        C{<div></div>}, this would be C{"div"}.\n    @type tagName: C{str}\n\n    @ivar attributes: The attributes of the element.\n    @type attributes: C{dict} mapping C{str} to renderable objects.\n\n    @ivar children: The child L{Tag}s of this C{Tag}.\n    @type children: C{list} of renderable objects.\n\n    @ivar render: The name of the render method to use for this L{Tag}.  This\n        name will be looked up at render time by the\n        L{twisted.web.template.Element} doing the rendering, via\n        L{twisted.web.template.Element.lookupRenderMethod}, to determine which\n        method to call.\n    @type render: C{str}\n\n    @type filename: C{str} or L{None}\n    @ivar filename: The name of the XML file from which this tag was parsed.\n        If it was not parsed from an XML file, L{None}.\n\n    @type lineNumber: C{int} or L{None}\n    @ivar lineNumber: The line number on which this tag was encountered in the\n        XML file from which it was parsed.  If it was not parsed from an XML\n        file, L{None}.\n\n    @type columnNumber: C{int} or L{None}\n    @ivar columnNumber: The column number at which this tag was encountered in\n        the XML file from which it was parsed.  If it was not parsed from an\n        XML file, L{None}.\n\n    @type slotData: C{dict} or L{None}\n    @ivar slotData: The data which can fill slots.  If present, a dictionary\n        mapping slot names to renderable values.  The values in this dict might\n        be anything that can be present as the child of a L{Tag}; strings,\n        lists, L{Tag}s, generators, etc.\n    '
    slotData = None
    filename = None
    lineNumber = None
    columnNumber = None

    def __init__(self, tagName, attributes=None, children=None, render=None, filename=None, lineNumber=None, columnNumber=None):
        self.tagName = tagName
        self.render = render
        if attributes is None:
            self.attributes = {}
        else:
            self.attributes = attributes
        if children is None:
            self.children = []
        else:
            self.children = children
        if filename is not None:
            self.filename = filename
        if lineNumber is not None:
            self.lineNumber = lineNumber
        if columnNumber is not None:
            self.columnNumber = columnNumber

    def fillSlots(self, **slots):
        """
        Remember the slots provided at this position in the DOM.

        During the rendering of children of this node, slots with names in
        C{slots} will be rendered as their corresponding values.

        @return: C{self}. This enables the idiom C{return tag.fillSlots(...)} in
            renderers.
        """
        if self.slotData is None:
            self.slotData = {}
        self.slotData.update(slots)
        return self

    def __call__(self, *children, **kw):
        """
        Add children and change attributes on this tag.

        This is implemented using __call__ because it then allows the natural
        syntax::

          table(tr1, tr2, width="100%", height="50%", border="1")

        Children may be other tag instances, strings, functions, or any other
        object which has a registered flatten.

        Attributes may be 'transparent' tag instances (so that
        C{a(href=transparent(data="foo", render=myhrefrenderer))} works),
        strings, functions, or any other object which has a registered
        flattener.

        If the attribute is a python keyword, such as 'class', you can add an
        underscore to the name, like 'class_'.

        There is one special keyword argument, 'render', which will be used as
        the name of the renderer and saved as the 'render' attribute of this
        instance, rather than the DOM 'render' attribute in the attributes
        dictionary.
        """
        self.children.extend(children)
        for k, v in iteritems(kw):
            if k[-1] == "_":
                k = k[:-1]
            if k == "render":
                self.render = v
            else:
                self.attributes[k] = v

        return self

    def _clone(self, obj, deep):
        """
        Clone an arbitrary object; used by L{Tag.clone}.

        @param obj: an object with a clone method, a list or tuple, or something
            which should be immutable.

        @param deep: whether to continue cloning child objects; i.e. the
            contents of lists, the sub-tags within a tag.

        @return: a clone of C{obj}.
        """
        if hasattr(obj, "clone"):
            return obj.clone(deep)
        else:
            if isinstance(obj, (list, tuple)):
                return [self._clone(x, deep) for x in obj]
            return obj

    def clone(self, deep=True):
        """
        Return a clone of this tag. If deep is True, clone all of this tag's
        children. Otherwise, just shallow copy the children list without copying
        the children themselves.
        """
        if deep:
            newchildren = [self._clone(x, True) for x in self.children]
        else:
            newchildren = self.children[:]
        newattrs = self.attributes.copy()
        for key in newattrs.keys():
            newattrs[key] = self._clone(newattrs[key], True)

        newslotdata = None
        if self.slotData:
            newslotdata = self.slotData.copy()
            for key in newslotdata:
                newslotdata[key] = self._clone(newslotdata[key], True)

        newtag = Tag((self.tagName),
          attributes=newattrs,
          children=newchildren,
          render=(self.render),
          filename=(self.filename),
          lineNumber=(self.lineNumber),
          columnNumber=(self.columnNumber))
        newtag.slotData = newslotdata
        return newtag

    def clear(self):
        """
        Clear any existing children from this tag.
        """
        self.children = []
        return self

    def __repr__(self):
        rstr = ""
        if self.attributes:
            rstr += ", attributes=%r" % self.attributes
        if self.children:
            rstr += ", children=%r" % self.children
        return "Tag(%r%s)" % (self.tagName, rstr)


voidElements = ('img', 'br', 'hr', 'base', 'meta', 'link', 'param', 'area', 'input',
                'col', 'basefont', 'isindex', 'frame', 'command', 'embed', 'keygen',
                'source', 'track', 'wbs')

class CDATA(object):
    __doc__ = '\n    A C{<![CDATA[]]>} block from a template.  Given a separate representation in\n    the DOM so that they may be round-tripped through rendering without losing\n    information.\n\n    @ivar data: The data between "C{<![CDATA[}" and "C{]]>}".\n    @type data: C{unicode}\n    '

    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return "CDATA(%r)" % (self.data,)


class Comment(object):
    __doc__ = '\n    A C{<!-- -->} comment from a template.  Given a separate representation in\n    the DOM so that they may be round-tripped through rendering without losing\n    information.\n\n    @ivar data: The data between "C{<!--}" and "C{-->}".\n    @type data: C{unicode}\n    '

    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return "Comment(%r)" % (self.data,)


class CharRef(object):
    __doc__ = "\n    A numeric character reference.  Given a separate representation in the DOM\n    so that non-ASCII characters may be output as pure ASCII.\n\n    @ivar ordinal: The ordinal value of the unicode character to which this is\n        object refers.\n    @type ordinal: C{int}\n\n    @since: 12.0\n    "

    def __init__(self, ordinal):
        self.ordinal = ordinal

    def __repr__(self):
        return "CharRef(%d)" % (self.ordinal,)
