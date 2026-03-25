# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\web\util.py
"""
An assortment of web server-related utilities.
"""
from __future__ import division, absolute_import
import linecache
from twisted.python import urlpath
from twisted.python.compat import _PY3, unicode, nativeString, escape
from twisted.python.reflect import fullyQualifiedName
from twisted.web import resource
from twisted.web.template import TagLoader, XMLString, Element, renderer
from twisted.web.template import flattenString

def _PRE(text):
    """
    Wraps <pre> tags around some text and HTML-escape it.

    This is here since once twisted.web.html was deprecated it was hard to
    migrate the html.PRE from current code to twisted.web.template.

    For new code consider using twisted.web.template.

    @return: Escaped text wrapped in <pre> tags.
    @rtype: C{str}
    """
    return "<pre>%s</pre>" % (escape(text),)


def redirectTo(URL, request):
    """
    Generate a redirect to the given location.

    @param URL: A L{bytes} giving the location to which to redirect.
    @type URL: L{bytes}

    @param request: The request object to use to generate the redirect.
    @type request: L{IRequest<twisted.web.iweb.IRequest>} provider

    @raise TypeError: If the type of C{URL} a L{unicode} instead of L{bytes}.

    @return: A C{bytes} containing HTML which tries to convince the client agent
        to visit the new location even if it doesn't respect the I{FOUND}
        response code.  This is intended to be returned from a render method,
        eg::

            def render_GET(self, request):
                return redirectTo(b"http://example.com/", request)
    """
    if isinstance(URL, unicode):
        raise TypeError("Unicode object not allowed as URL")
    request.setHeader(b'Content-Type', b'text/html; charset=utf-8')
    request.redirect(URL)
    content = '\n<html>\n    <head>\n        <meta http-equiv="refresh" content="0;URL=%(url)s">\n    </head>\n    <body bgcolor="#FFFFFF" text="#000000">\n    <a href="%(url)s">click here</a>\n    </body>\n</html>\n' % {"url": (nativeString(URL))}
    if _PY3:
        content = content.encode("utf8")
    return content


class Redirect(resource.Resource):
    isLeaf = True

    def __init__(self, url):
        resource.Resource.__init__(self)
        self.url = url

    def render(self, request):
        return redirectTo(self.url, request)

    def getChild(self, name, request):
        return self


class ChildRedirector(Redirect):
    isLeaf = 0

    def __init__(self, url):
        if url.find("://") == -1:
            if not url.startswith(".."):
                if not url.startswith("/"):
                    raise ValueError("It seems you've given me a redirect (%s) that is a child of myself! That's not good, it'll cause an infinite redirect." % url)
        Redirect.__init__(self, url)

    def getChild(self, name, request):
        newUrl = self.url
        if not newUrl.endswith("/"):
            newUrl += "/"
        newUrl += name
        return ChildRedirector(newUrl)


class ParentRedirect(resource.Resource):
    __doc__ = "\n    I redirect to URLPath.here().\n    "
    isLeaf = 1

    def render(self, request):
        return redirectTo(urlpath.URLPath.fromRequest(request).here(), request)

    def getChild(self, request):
        return self


class DeferredResource(resource.Resource):
    __doc__ = "\n    I wrap up a Deferred that will eventually result in a Resource\n    object.\n    "
    isLeaf = 1

    def __init__(self, d):
        resource.Resource.__init__(self)
        self.d = d

    def getChild(self, name, request):
        return self

    def render(self, request):
        self.d.addCallback(self._cbChild, request).addErrback(self._ebChild, request)
        from twisted.web.server import NOT_DONE_YET
        return NOT_DONE_YET

    def _cbChild(self, child, request):
        request.render(resource.getChildForRequest(child, request))

    def _ebChild(self, reason, request):
        request.processingFailed(reason)


class _SourceLineElement(Element):
    __doc__ = "\n    L{_SourceLineElement} is an L{IRenderable} which can render a single line of\n    source code.\n\n    @ivar number: A C{int} giving the line number of the source code to be\n        rendered.\n    @ivar source: A C{str} giving the source code to be rendered.\n    "

    def __init__(self, loader, number, source):
        Element.__init__(self, loader)
        self.number = number
        self.source = source

    @renderer
    def sourceLine(self, request, tag):
        """
        Render the line of source as a child of C{tag}.
        """
        return tag(self.source.replace("  ", " \xa0"))

    @renderer
    def lineNumber(self, request, tag):
        """
        Render the line number as a child of C{tag}.
        """
        return tag(str(self.number))


class _SourceFragmentElement(Element):
    __doc__ = "\n    L{_SourceFragmentElement} is an L{IRenderable} which can render several lines\n    of source code near the line number of a particular frame object.\n\n    @ivar frame: A L{Failure<twisted.python.failure.Failure>}-style frame object\n        for which to load a source line to render.  This is really a tuple\n        holding some information from a frame object.  See\n        L{Failure.frames<twisted.python.failure.Failure>} for specifics.\n    "

    def __init__(self, loader, frame):
        Element.__init__(self, loader)
        self.frame = frame

    def _getSourceLines(self):
        """
        Find the source line references by C{self.frame} and yield, in source
        line order, it and the previous and following lines.

        @return: A generator which yields two-tuples.  Each tuple gives a source
            line number and the contents of that source line.
        """
        filename = self.frame[1]
        lineNumber = self.frame[2]
        for snipLineNumber in range(lineNumber - 1, lineNumber + 2):
            yield (
             snipLineNumber,
             linecache.getline(filename, snipLineNumber).rstrip())

    @renderer
    def sourceLines(self, request, tag):
        """
        Render the source line indicated by C{self.frame} and several
        surrounding lines.  The active line will be given a I{class} of
        C{"snippetHighlightLine"}.  Other lines will be given a I{class} of
        C{"snippetLine"}.
        """
        for lineNumber, sourceLine in self._getSourceLines():
            newTag = tag.clone()
            if lineNumber == self.frame[2]:
                cssClass = "snippetHighlightLine"
            else:
                cssClass = "snippetLine"
            loader = TagLoader(newTag(**{"class": cssClass}))
            yield _SourceLineElement(loader, lineNumber, sourceLine)


class _FrameElement(Element):
    __doc__ = "\n    L{_FrameElement} is an L{IRenderable} which can render details about one\n    frame from a L{Failure<twisted.python.failure.Failure>}.\n\n    @ivar frame: A L{Failure<twisted.python.failure.Failure>}-style frame object\n        for which to load a source line to render.  This is really a tuple\n        holding some information from a frame object.  See\n        L{Failure.frames<twisted.python.failure.Failure>} for specifics.\n    "

    def __init__(self, loader, frame):
        Element.__init__(self, loader)
        self.frame = frame

    @renderer
    def filename(self, request, tag):
        """
        Render the name of the file this frame references as a child of C{tag}.
        """
        return tag(self.frame[1])

    @renderer
    def lineNumber(self, request, tag):
        """
        Render the source line number this frame references as a child of
        C{tag}.
        """
        return tag(str(self.frame[2]))

    @renderer
    def function(self, request, tag):
        """
        Render the function name this frame references as a child of C{tag}.
        """
        return tag(self.frame[0])

    @renderer
    def source(self, request, tag):
        """
        Render the source code surrounding the line this frame references,
        replacing C{tag}.
        """
        return _SourceFragmentElement(TagLoader(tag), self.frame)


class _StackElement(Element):
    __doc__ = "\n    L{_StackElement} renders an L{IRenderable} which can render a list of frames.\n    "

    def __init__(self, loader, stackFrames):
        Element.__init__(self, loader)
        self.stackFrames = stackFrames

    @renderer
    def frames(self, request, tag):
        """
        Render the list of frames in this L{_StackElement}, replacing C{tag}.
        """
        return [_FrameElement(TagLoader(tag.clone()), frame) for frame in self.stackFrames]


class FailureElement(Element):
    __doc__ = "\n    L{FailureElement} is an L{IRenderable} which can render detailed information\n    about a L{Failure<twisted.python.failure.Failure>}.\n\n    @ivar failure: The L{Failure<twisted.python.failure.Failure>} instance which\n        will be rendered.\n\n    @since: 12.1\n    "
    loader = XMLString('\n<div xmlns:t="http://twistedmatrix.com/ns/twisted.web.template/0.1">\n  <style type="text/css">\n    div.error {\n      color: red;\n      font-family: Verdana, Arial, helvetica, sans-serif;\n      font-weight: bold;\n    }\n\n    div {\n      font-family: Verdana, Arial, helvetica, sans-serif;\n    }\n\n    div.stackTrace {\n    }\n\n    div.frame {\n      padding: 1em;\n      background: white;\n      border-bottom: thin black dashed;\n    }\n\n    div.frame:first-child {\n      padding: 1em;\n      background: white;\n      border-top: thin black dashed;\n      border-bottom: thin black dashed;\n    }\n\n    div.location {\n    }\n\n    span.function {\n      font-weight: bold;\n      font-family: "Courier New", courier, monospace;\n    }\n\n    div.snippet {\n      margin-bottom: 0.5em;\n      margin-left: 1em;\n      background: #FFFFDD;\n    }\n\n    div.snippetHighlightLine {\n      color: red;\n    }\n\n    span.code {\n      font-family: "Courier New", courier, monospace;\n    }\n  </style>\n\n  <div class="error">\n    <span t:render="type" />: <span t:render="value" />\n  </div>\n  <div class="stackTrace" t:render="traceback">\n    <div class="frame" t:render="frames">\n      <div class="location">\n        <span t:render="filename" />:<span t:render="lineNumber" /> in\n        <span class="function" t:render="function" />\n      </div>\n      <div class="snippet" t:render="source">\n        <div t:render="sourceLines">\n          <span class="lineno" t:render="lineNumber" />\n          <code class="code" t:render="sourceLine" />\n        </div>\n      </div>\n    </div>\n  </div>\n  <div class="error">\n    <span t:render="type" />: <span t:render="value" />\n  </div>\n</div>\n')

    def __init__(self, failure, loader=None):
        Element.__init__(self, loader)
        self.failure = failure

    @renderer
    def type(self, request, tag):
        """
        Render the exception type as a child of C{tag}.
        """
        return tag(fullyQualifiedName(self.failure.type))

    @renderer
    def value(self, request, tag):
        """
        Render the exception value as a child of C{tag}.
        """
        return tag(unicode(self.failure.value).encode("utf8"))

    @renderer
    def traceback(self, request, tag):
        """
        Render all the frames in the wrapped
        L{Failure<twisted.python.failure.Failure>}'s traceback stack, replacing
        C{tag}.
        """
        return _StackElement(TagLoader(tag), self.failure.frames)


def formatFailure(myFailure):
    """
    Construct an HTML representation of the given failure.

    Consider using L{FailureElement} instead.

    @type myFailure: L{Failure<twisted.python.failure.Failure>}

    @rtype: C{bytes}
    @return: A string containing the HTML representation of the given failure.
    """
    result = []
    flattenString(None, FailureElement(myFailure)).addBoth(result.append)
    if isinstance(result[0], bytes):
        return result[0].decode("utf-8").encode("ascii", "xmlcharrefreplace")
    result[0].raiseException()


__all__ = [
 'redirectTo', 'Redirect', 'ChildRedirector', 'ParentRedirect', 
 'DeferredResource', 
 'FailureElement', 'formatFailure']
