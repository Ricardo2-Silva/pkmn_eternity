# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\web\_element.py
from __future__ import division, absolute_import
from zope.interface import implementer
from twisted.web.iweb import IRenderable
from twisted.web.error import MissingRenderMethod, UnexposedMethodError
from twisted.web.error import MissingTemplateLoader

class Expose(object):
    __doc__ = "\n    Helper for exposing methods for various uses using a simple decorator-style\n    callable.\n\n    Instances of this class can be called with one or more functions as\n    positional arguments.  The names of these functions will be added to a list\n    on the class object of which they are methods.\n\n    @ivar attributeName: The attribute with which exposed methods will be\n    tracked.\n    "

    def __init__(self, doc=None):
        self.doc = doc

    def __call__(self, *funcObjs):
        """
        Add one or more functions to the set of exposed functions.

        This is a way to declare something about a class definition, similar to
        L{zope.interface.declarations.implementer}.  Use it like this::

            magic = Expose('perform extra magic')
            class Foo(Bar):
                def twiddle(self, x, y):
                    ...
                def frob(self, a, b):
                    ...
                magic(twiddle, frob)

        Later you can query the object::

            aFoo = Foo()
            magic.get(aFoo, 'twiddle')(x=1, y=2)

        The call to C{get} will fail if the name it is given has not been
        exposed using C{magic}.

        @param funcObjs: One or more function objects which will be exposed to
        the client.

        @return: The first of C{funcObjs}.
        """
        if not funcObjs:
            raise TypeError("expose() takes at least 1 argument (0 given)")
        for fObj in funcObjs:
            fObj.exposedThrough = getattr(fObj, "exposedThrough", [])
            fObj.exposedThrough.append(self)

        return funcObjs[0]

    _nodefault = object()

    def get(self, instance, methodName, default=_nodefault):
        """
        Retrieve an exposed method with the given name from the given instance.

        @raise UnexposedMethodError: Raised if C{default} is not specified and
        there is no exposed method with the given name.

        @return: A callable object for the named method assigned to the given
        instance.
        """
        method = getattr(instance, methodName, None)
        exposedThrough = getattr(method, "exposedThrough", [])
        if self not in exposedThrough:
            if default is self._nodefault:
                raise UnexposedMethodError(self, methodName)
            return default
        else:
            return method

    @classmethod
    def _withDocumentation(cls, thunk):
        """
        Slight hack to make users of this class appear to have a docstring to
        documentation generators, by defining them with a decorator.  (This hack
        should be removed when epydoc can be convinced to use some other method
        for documenting.)
        """
        return cls(thunk.__doc__)


exposer = Expose._withDocumentation

@exposer
def renderer():
    """
    Decorate with L{renderer} to use methods as template render directives.

    For example::

        class Foo(Element):
            @renderer
            def twiddle(self, request, tag):
                return tag('Hello, world.')

        <div xmlns:t="http://twistedmatrix.com/ns/twisted.web.template/0.1">
            <span t:render="twiddle" />
        </div>

    Will result in this final output::

        <div>
            <span>Hello, world.</span>
        </div>
    """
    return


@implementer(IRenderable)
class Element(object):
    __doc__ = '\n    Base for classes which can render part of a page.\n\n    An Element is a renderer that can be embedded in a stan document and can\n    hook its template (from the loader) up to render methods.\n\n    An Element might be used to encapsulate the rendering of a complex piece of\n    data which is to be displayed in multiple different contexts.  The Element\n    allows the rendering logic to be easily re-used in different ways.\n\n    Element returns render methods which are registered using\n    L{twisted.web._element.renderer}.  For example::\n\n        class Menu(Element):\n            @renderer\n            def items(self, request, tag):\n                ....\n\n    Render methods are invoked with two arguments: first, the\n    L{twisted.web.http.Request} being served and second, the tag object which\n    "invoked" the render method.\n\n    @type loader: L{ITemplateLoader} provider\n    @ivar loader: The factory which will be used to load documents to\n        return from C{render}.\n    '
    loader = None

    def __init__(self, loader=None):
        if loader is not None:
            self.loader = loader

    def lookupRenderMethod(self, name):
        """
        Look up and return the named render method.
        """
        method = renderer.get(self, name, None)
        if method is None:
            raise MissingRenderMethod(self, name)
        return method

    def render(self, request):
        """
        Implement L{IRenderable} to allow one L{Element} to be embedded in
        another's template or rendering output.

        (This will simply load the template from the C{loader}; when used in a
        template, the flattening engine will keep track of this object
        separately as the object to lookup renderers on and call
        L{Element.renderer} to look them up.  The resulting object from this
        method is not directly associated with this L{Element}.)
        """
        loader = self.loader
        if loader is None:
            raise MissingTemplateLoader(self)
        return loader.load()
