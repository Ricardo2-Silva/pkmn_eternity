# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: zope\interface\interfaces.py
"""Interface Package Interfaces
"""
__docformat__ = "restructuredtext"
from zope.interface.interface import Attribute
from zope.interface.interface import Interface
from zope.interface.declarations import implementer
_BLANK = ""

class IElement(Interface):
    __doc__ = "Objects that have basic documentation and tagged values.\n    "
    __name__ = Attribute("__name__", "The object name")
    __doc__ = Attribute("__doc__", "The object doc string")

    def getTaggedValue(tag):
        """Returns the value associated with `tag`.

        Raise a `KeyError` of the tag isn't set.
        """
        return

    def queryTaggedValue(tag, default=None):
        """Returns the value associated with `tag`.

        Return the default value of the tag isn't set.
        """
        return

    def getTaggedValueTags():
        """Returns a list of all tags."""
        return

    def setTaggedValue(tag, value):
        """Associates `value` with `key`."""
        return


class IAttribute(IElement):
    __doc__ = "Attribute descriptors"
    interface = Attribute("interface", "Stores the interface instance in which the attribute is located.")


class IMethod(IAttribute):
    __doc__ = "Method attributes"

    def getSignatureInfo():
        """Returns the signature information.

        This method returns a dictionary with the following keys:

        o `positional` - All positional arguments.

        o `required` - A list of all required arguments.

        o `optional` - A list of all optional arguments.

        o `varargs` - The name of the varargs argument.

        o `kwargs` - The name of the kwargs argument.
        """
        return

    def getSignatureString():
        """Return a signature string suitable for inclusion in documentation.

        This method returns the function signature string. For example, if you
        have `func(a, b, c=1, d='f')`, then the signature string is `(a, b,
        c=1, d='f')`.
        """
        return


class ISpecification(Interface):
    __doc__ = "Object Behavioral specifications"

    def providedBy(object):
        """Test whether the interface is implemented by the object

        Return true of the object asserts that it implements the
        interface, including asserting that it implements an extended
        interface.
        """
        return

    def implementedBy(class_):
        """Test whether the interface is implemented by instances of the class

        Return true of the class asserts that its instances implement the
        interface, including asserting that they implement an extended
        interface.
        """
        return

    def isOrExtends(other):
        """Test whether the specification is or extends another
        """
        return

    def extends(other, strict=True):
        """Test whether a specification extends another

        The specification extends other if it has other as a base
        interface or if one of it's bases extends other.

        If strict is false, then the specification extends itself.
        """
        return

    def weakref(callback=None):
        """Return a weakref to the specification

        This method is, regrettably, needed to allow weakrefs to be
        computed to security-proxied specifications.  While the
        zope.interface package does not require zope.security or
        zope.proxy, it has to be able to coexist with it.

        """
        return

    __bases__ = Attribute("Base specifications\n\n    A tuple if specifications from which this specification is\n    directly derived.\n\n    ")
    __sro__ = Attribute("Specification-resolution order\n\n    A tuple of the specification and all of it's ancestor\n    specifications from most specific to least specific.\n\n    (This is similar to the method-resolution order for new-style classes.)\n    ")
    __iro__ = Attribute("Interface-resolution order\n\n    A tuple of the of the specification's ancestor interfaces from\n    most specific to least specific.  The specification itself is\n    included if it is an interface.\n\n    (This is similar to the method-resolution order for new-style classes.)\n    ")

    def get(name, default=None):
        """Look up the description for a name

        If the named attribute is not defined, the default is
        returned.
        """
        return


class IInterface(ISpecification, IElement):
    __doc__ = 'Interface objects\n\n    Interface objects describe the behavior of an object by containing\n    useful information about the object.  This information includes:\n\n    - Prose documentation about the object.  In Python terms, this\n      is called the "doc string" of the interface.  In this element,\n      you describe how the object works in prose language and any\n      other useful information about the object.\n\n    - Descriptions of attributes.  Attribute descriptions include\n      the name of the attribute and prose documentation describing\n      the attributes usage.\n\n    - Descriptions of methods.  Method descriptions can include:\n\n        - Prose "doc string" documentation about the method and its\n          usage.\n\n        - A description of the methods arguments; how many arguments\n          are expected, optional arguments and their default values,\n          the position or arguments in the signature, whether the\n          method accepts arbitrary arguments and whether the method\n          accepts arbitrary keyword arguments.\n\n    - Optional tagged data.  Interface objects (and their attributes and\n      methods) can have optional, application specific tagged data\n      associated with them.  Examples uses for this are examples,\n      security assertions, pre/post conditions, and other possible\n      information you may want to associate with an Interface or its\n      attributes.\n\n    Not all of this information is mandatory.  For example, you may\n    only want the methods of your interface to have prose\n    documentation and not describe the arguments of the method in\n    exact detail.  Interface objects are flexible and let you give or\n    take any of these components.\n\n    Interfaces are created with the Python class statement using\n    either `zope.interface.Interface` or another interface, as in::\n\n      from zope.interface import Interface\n\n      class IMyInterface(Interface):\n        \'\'\'Interface documentation\'\'\'\n\n        def meth(arg1, arg2):\n            \'\'\'Documentation for meth\'\'\'\n\n        # Note that there is no self argument\n\n     class IMySubInterface(IMyInterface):\n        \'\'\'Interface documentation\'\'\'\n\n        def meth2():\n            \'\'\'Documentation for meth2\'\'\'\n\n    You use interfaces in two ways:\n\n    - You assert that your object implement the interfaces.\n\n      There are several ways that you can assert that an object\n      implements an interface:\n\n      1. Call `zope.interface.implements` in your class definition.\n\n      2. Call `zope.interfaces.directlyProvides` on your object.\n\n      3. Call `zope.interface.classImplements` to assert that instances\n         of a class implement an interface.\n\n         For example::\n\n           from zope.interface import classImplements\n\n           classImplements(some_class, some_interface)\n\n         This approach is useful when it is not an option to modify\n         the class source.  Note that this doesn\'t affect what the\n         class itself implements, but only what its instances\n         implement.\n\n    - You query interface meta-data. See the IInterface methods and\n      attributes for details.\n\n    '

    def names(all=False):
        """Get the interface attribute names

        Return a sequence of the names of the attributes, including
        methods, included in the interface definition.

        Normally, only directly defined attributes are included. If
        a true positional or keyword argument is given, then
        attributes defined by base classes will be included.
        """
        return

    def namesAndDescriptions(all=False):
        """Get the interface attribute names and descriptions

        Return a sequence of the names and descriptions of the
        attributes, including methods, as name-value pairs, included
        in the interface definition.

        Normally, only directly defined attributes are included. If
        a true positional or keyword argument is given, then
        attributes defined by base classes will be included.
        """
        return

    def __getitem__(name):
        """Get the description for a name

        If the named attribute is not defined, a `KeyError` is raised.
        """
        return

    def direct(name):
        """Get the description for the name if it was defined by the interface

        If the interface doesn't define the name, returns None.
        """
        return

    def validateInvariants(obj, errors=None):
        """Validate invariants

        Validate object to defined invariants.  If errors is None,
        raises first Invalid error; if errors is a list, appends all errors
        to list, then raises Invalid with the errors as the first element
        of the "args" tuple."""
        return

    def __contains__(name):
        """Test whether the name is defined by the interface"""
        return

    def __iter__():
        """Return an iterator over the names defined by the interface

        The names iterated include all of the names defined by the
        interface directly and indirectly by base interfaces.
        """
        return

    __module__ = Attribute("The name of the module defining the interface")


class IDeclaration(ISpecification):
    __doc__ = "Interface declaration\n\n    Declarations are used to express the interfaces implemented by\n    classes or provided by objects.\n    "

    def __contains__(interface):
        """Test whether an interface is in the specification

        Return true if the given interface is one of the interfaces in
        the specification and false otherwise.
        """
        return

    def __iter__():
        """Return an iterator for the interfaces in the specification
        """
        return

    def flattened():
        """Return an iterator of all included and extended interfaces

        An iterator is returned for all interfaces either included in
        or extended by interfaces included in the specifications
        without duplicates. The interfaces are in "interface
        resolution order". The interface resolution order is such that
        base interfaces are listed after interfaces that extend them
        and, otherwise, interfaces are included in the order that they
        were defined in the specification.
        """
        return

    def __sub__(interfaces):
        """Create an interface specification with some interfaces excluded

        The argument can be an interface or an interface
        specifications.  The interface or interfaces given in a
        specification are subtracted from the interface specification.

        Removing an interface that is not in the specification does
        not raise an error. Doing so has no effect.

        Removing an interface also removes sub-interfaces of the interface.

        """
        return

    def __add__(interfaces):
        """Create an interface specification with some interfaces added

        The argument can be an interface or an interface
        specifications.  The interface or interfaces given in a
        specification are added to the interface specification.

        Adding an interface that is already in the specification does
        not raise an error. Doing so has no effect.
        """
        return

    def __nonzero__():
        """Return a true value of the interface specification is non-empty
        """
        return


class IInterfaceDeclaration(Interface):
    __doc__ = "Declare and check the interfaces of objects\n\n    The functions defined in this interface are used to declare the\n    interfaces that objects provide and to query the interfaces that have\n    been declared.\n\n    Interfaces can be declared for objects in two ways:\n\n    - Interfaces are declared for instances of the object's class\n\n    - Interfaces are declared for the object directly.\n\n    The interfaces declared for an object are, therefore, the union of\n    interfaces declared for the object directly and the interfaces\n    declared for instances of the object's class.\n\n    Note that we say that a class implements the interfaces provided\n    by it's instances.  An instance can also provide interfaces\n    directly.  The interfaces provided by an object are the union of\n    the interfaces provided directly and the interfaces implemented by\n    the class.\n    "

    def providedBy(ob):
        """Return the interfaces provided by an object

        This is the union of the interfaces directly provided by an
        object and interfaces implemented by it's class.

        The value returned is an `IDeclaration`.
        """
        return

    def implementedBy(class_):
        """Return the interfaces implemented for a class' instances

        The value returned is an `IDeclaration`.
        """
        return

    def classImplements(class_, *interfaces):
        """Declare additional interfaces implemented for instances of a class

        The arguments after the class are one or more interfaces or
        interface specifications (`IDeclaration` objects).

        The interfaces given (including the interfaces in the
        specifications) are added to any interfaces previously
        declared.

        Consider the following example::

          class C(A, B):
             ...

          classImplements(C, I1, I2)

        Instances of ``C`` provide ``I1``, ``I2``, and whatever interfaces
        instances of ``A`` and ``B`` provide.
        """
        return

    def implementer(*interfaces):
        """Create a decorator for declaring interfaces implemented by a factory.

        A callable is returned that makes an implements declaration on
        objects passed to it.
        """
        return

    def classImplementsOnly(class_, *interfaces):
        """Declare the only interfaces implemented by instances of a class

        The arguments after the class are one or more interfaces or
        interface specifications (`IDeclaration` objects).

        The interfaces given (including the interfaces in the
        specifications) replace any previous declarations.

        Consider the following example::

          class C(A, B):
             ...

          classImplements(C, IA, IB. IC)
          classImplementsOnly(C. I1, I2)

        Instances of ``C`` provide only ``I1``, ``I2``, and regardless of
        whatever interfaces instances of ``A`` and ``B`` implement.
        """
        return

    def implementer_only(*interfaces):
        """Create a decorator for declaring the only interfaces implemented

        A callable is returned that makes an implements declaration on
        objects passed to it.
        """
        return

    def directlyProvidedBy(object):
        """Return the interfaces directly provided by the given object

        The value returned is an `IDeclaration`.
        """
        return

    def directlyProvides(object, *interfaces):
        """Declare interfaces declared directly for an object

        The arguments after the object are one or more interfaces or
        interface specifications (`IDeclaration` objects).

        The interfaces given (including the interfaces in the
        specifications) replace interfaces previously
        declared for the object.

        Consider the following example::

          class C(A, B):
             ...

          ob = C()
          directlyProvides(ob, I1, I2)

        The object, ``ob`` provides ``I1``, ``I2``, and whatever interfaces
        instances have been declared for instances of ``C``.

        To remove directly provided interfaces, use `directlyProvidedBy` and
        subtract the unwanted interfaces. For example::

          directlyProvides(ob, directlyProvidedBy(ob)-I2)

        removes I2 from the interfaces directly provided by
        ``ob``. The object, ``ob`` no longer directly provides ``I2``,
        although it might still provide ``I2`` if it's class
        implements ``I2``.

        To add directly provided interfaces, use `directlyProvidedBy` and
        include additional interfaces.  For example::

          directlyProvides(ob, directlyProvidedBy(ob), I2)

        adds I2 to the interfaces directly provided by ob.
        """
        return

    def alsoProvides(object, *interfaces):
        """Declare additional interfaces directly for an object::

          alsoProvides(ob, I1)

        is equivalent to::

          directlyProvides(ob, directlyProvidedBy(ob), I1)
        """
        return

    def noLongerProvides(object, interface):
        """Remove an interface from the list of an object's directly
        provided interfaces::

          noLongerProvides(ob, I1)

        is equivalent to::

          directlyProvides(ob, directlyProvidedBy(ob) - I1)

        with the exception that if ``I1`` is an interface that is
        provided by ``ob`` through the class's implementation,
        `ValueError` is raised.
        """
        return

    def implements(*interfaces):
        """Declare interfaces implemented by instances of a class

        This function is called in a class definition (Python 2.x only).

        The arguments are one or more interfaces or interface
        specifications (`IDeclaration` objects).

        The interfaces given (including the interfaces in the
        specifications) are added to any interfaces previously
        declared.

        Previous declarations include declarations for base classes
        unless implementsOnly was used.

        This function is provided for convenience. It provides a more
        convenient way to call `classImplements`. For example::

          implements(I1)

        is equivalent to calling::

          classImplements(C, I1)

        after the class has been created.

        Consider the following example (Python 2.x only)::

          class C(A, B):
            implements(I1, I2)

        Instances of ``C`` implement ``I1``, ``I2``, and whatever interfaces
        instances of ``A`` and ``B`` implement.
        """
        return

    def implementsOnly(*interfaces):
        """Declare the only interfaces implemented by instances of a class

        This function is called in a class definition (Python 2.x only).

        The arguments are one or more interfaces or interface
        specifications (`IDeclaration` objects).

        Previous declarations including declarations for base classes
        are overridden.

        This function is provided for convenience. It provides a more
        convenient way to call `classImplementsOnly`. For example::

          implementsOnly(I1)

        is equivalent to calling::

          classImplementsOnly(I1)

        after the class has been created.

        Consider the following example (Python 2.x only)::

          class C(A, B):
            implementsOnly(I1, I2)

        Instances of ``C`` implement ``I1``, ``I2``, regardless of what
        instances of ``A`` and ``B`` implement.
        """
        return

    def classProvides(*interfaces):
        """Declare interfaces provided directly by a class

        This function is called in a class definition.

        The arguments are one or more interfaces or interface
        specifications (`IDeclaration` objects).

        The given interfaces (including the interfaces in the
        specifications) are used to create the class's direct-object
        interface specification.  An error will be raised if the module
        class has an direct interface specification.  In other words, it is
        an error to call this function more than once in a class
        definition.

        Note that the given interfaces have nothing to do with the
        interfaces implemented by instances of the class.

        This function is provided for convenience. It provides a more
        convenient way to call `directlyProvides` for a class. For example::

          classProvides(I1)

        is equivalent to calling::

          directlyProvides(theclass, I1)

        after the class has been created.
        """
        return

    def provider(*interfaces):
        """A class decorator version of `classProvides`"""
        return

    def moduleProvides(*interfaces):
        """Declare interfaces provided by a module

        This function is used in a module definition.

        The arguments are one or more interfaces or interface
        specifications (`IDeclaration` objects).

        The given interfaces (including the interfaces in the
        specifications) are used to create the module's direct-object
        interface specification.  An error will be raised if the module
        already has an interface specification.  In other words, it is
        an error to call this function more than once in a module
        definition.

        This function is provided for convenience. It provides a more
        convenient way to call `directlyProvides` for a module. For example::

          moduleImplements(I1)

        is equivalent to::

          directlyProvides(sys.modules[__name__], I1)
        """
        return

    def Declaration(*interfaces):
        """Create an interface specification

        The arguments are one or more interfaces or interface
        specifications (`IDeclaration` objects).

        A new interface specification (`IDeclaration`) with
        the given interfaces is returned.
        """
        return


class IAdapterRegistry(Interface):
    __doc__ = 'Provide an interface-based registry for adapters\n\n    This registry registers objects that are in some sense "from" a\n    sequence of specification to an interface and a name.\n\n    No specific semantics are assumed for the registered objects,\n    however, the most common application will be to register factories\n    that adapt objects providing required specifications to a provided\n    interface.\n    '

    def register(required, provided, name, value):
        """Register a value

        A value is registered for a *sequence* of required specifications, a
        provided interface, and a name, which must be text.
        """
        return

    def registered(required, provided, name=_BLANK):
        """Return the component registered for the given interfaces and name

        name must be text.

        Unlike the lookup method, this methods won't retrieve
        components registered for more specific required interfaces or
        less specific provided interfaces.

        If no component was registered exactly for the given
        interfaces and name, then None is returned.

        """
        return

    def lookup(required, provided, name='', default=None):
        """Lookup a value

        A value is looked up based on a *sequence* of required
        specifications, a provided interface, and a name, which must be
        text.
        """
        return

    def queryMultiAdapter(objects, provided, name=_BLANK, default=None):
        """Adapt a sequence of objects to a named, provided, interface
        """
        return

    def lookup1(required, provided, name=_BLANK, default=None):
        """Lookup a value using a single required interface

        A value is looked up based on a single required
        specifications, a provided interface, and a name, which must be
        text.
        """
        return

    def queryAdapter(object, provided, name=_BLANK, default=None):
        """Adapt an object using a registered adapter factory.
        """
        return

    def adapter_hook(provided, object, name=_BLANK, default=None):
        """Adapt an object using a registered adapter factory.

        name must be text.
        """
        return

    def lookupAll(required, provided):
        """Find all adapters from the required to the provided interfaces

        An iterable object is returned that provides name-value two-tuples.
        """
        return

    def names(required, provided):
        """Return the names for which there are registered objects
        """
        return

    def subscribe(required, provided, subscriber, name=_BLANK):
        """Register a subscriber

        A subscriber is registered for a *sequence* of required
        specifications, a provided interface, and a name.

        Multiple subscribers may be registered for the same (or
        equivalent) interfaces.
        """
        return

    def subscriptions(required, provided, name=_BLANK):
        """Get a sequence of subscribers

        Subscribers for a *sequence* of required interfaces, and a provided
        interface are returned.
        """
        return

    def subscribers(objects, provided, name=_BLANK):
        """Get a sequence of subscription adapters
        """
        return


class ComponentLookupError(LookupError):
    __doc__ = "A component could not be found."


class Invalid(Exception):
    __doc__ = "A component doesn't satisfy a promise."


class IObjectEvent(Interface):
    __doc__ = "An event related to an object.\n\n    The object that generated this event is not necessarily the object\n    refered to by location.\n    "
    object = Attribute("The subject of the event.")


@implementer(IObjectEvent)
class ObjectEvent(object):

    def __init__(self, object):
        self.object = object


class IComponentLookup(Interface):
    __doc__ = "Component Manager for a Site\n\n    This object manages the components registered at a particular site. The\n    definition of a site is intentionally vague.\n    "
    adapters = Attribute("Adapter Registry to manage all registered adapters.")
    utilities = Attribute("Adapter Registry to manage all registered utilities.")

    def queryAdapter(object, interface, name=_BLANK, default=None):
        """Look for a named adapter to an interface for an object

        If a matching adapter cannot be found, returns the default.
        """
        return

    def getAdapter(object, interface, name=_BLANK):
        """Look for a named adapter to an interface for an object

        If a matching adapter cannot be found, a `ComponentLookupError`
        is raised.
        """
        return

    def queryMultiAdapter(objects, interface, name=_BLANK, default=None):
        """Look for a multi-adapter to an interface for multiple objects

        If a matching adapter cannot be found, returns the default.
        """
        return

    def getMultiAdapter(objects, interface, name=_BLANK):
        """Look for a multi-adapter to an interface for multiple objects

        If a matching adapter cannot be found, a `ComponentLookupError`
        is raised.
        """
        return

    def getAdapters(objects, provided):
        """Look for all matching adapters to a provided interface for objects

        Return an iterable of name-adapter pairs for adapters that
        provide the given interface.
        """
        return

    def subscribers(objects, provided):
        """Get subscribers

        Subscribers are returned that provide the provided interface
        and that depend on and are comuted from the sequence of
        required objects.
        """
        return

    def handle(*objects):
        """Call handlers for the given objects

        Handlers registered for the given objects are called.
        """
        return

    def queryUtility(interface, name='', default=None):
        """Look up a utility that provides an interface.

        If one is not found, returns default.
        """
        return

    def getUtilitiesFor(interface):
        """Look up the registered utilities that provide an interface.

        Returns an iterable of name-utility pairs.
        """
        return

    def getAllUtilitiesRegisteredFor(interface):
        """Return all registered utilities for an interface

        This includes overridden utilities.

        An iterable of utility instances is returned.  No names are
        returned.
        """
        return


class IRegistration(Interface):
    __doc__ = "A registration-information object\n    "
    registry = Attribute("The registry having the registration")
    name = Attribute("The registration name")
    info = Attribute("Information about the registration\n\n    This is information deemed useful to people browsing the\n    configuration of a system. It could, for example, include\n    commentary or information about the source of the configuration.\n    ")


class IUtilityRegistration(IRegistration):
    __doc__ = "Information about the registration of a utility\n    "
    factory = Attribute("The factory used to create the utility. Optional.")
    component = Attribute("The object registered")
    provided = Attribute("The interface provided by the component")


class _IBaseAdapterRegistration(IRegistration):
    __doc__ = "Information about the registration of an adapter\n    "
    factory = Attribute("The factory used to create adapters")
    required = Attribute("The adapted interfaces\n\n    This is a sequence of interfaces adapters by the registered\n    factory.  The factory will be caled with a sequence of objects, as\n    positional arguments, that provide these interfaces.\n    ")
    provided = Attribute("The interface provided by the adapters.\n\n    This interface is implemented by the factory\n    ")


class IAdapterRegistration(_IBaseAdapterRegistration):
    __doc__ = "Information about the registration of an adapter\n    "


class ISubscriptionAdapterRegistration(_IBaseAdapterRegistration):
    __doc__ = "Information about the registration of a subscription adapter\n    "


class IHandlerRegistration(IRegistration):
    handler = Attribute("An object called used to handle an event")
    required = Attribute("The handled interfaces\n\n    This is a sequence of interfaces handled by the registered\n    handler.  The handler will be caled with a sequence of objects, as\n    positional arguments, that provide these interfaces.\n    ")


class IRegistrationEvent(IObjectEvent):
    __doc__ = "An event that involves a registration"


@implementer(IRegistrationEvent)
class RegistrationEvent(ObjectEvent):
    __doc__ = "There has been a change in a registration\n    "

    def __repr__(self):
        return "%s event:\n%r" % (self.__class__.__name__, self.object)


class IRegistered(IRegistrationEvent):
    __doc__ = "A component or factory was registered\n    "


@implementer(IRegistered)
class Registered(RegistrationEvent):
    return


class IUnregistered(IRegistrationEvent):
    __doc__ = "A component or factory was unregistered\n    "


@implementer(IUnregistered)
class Unregistered(RegistrationEvent):
    __doc__ = "A component or factory was unregistered\n    "
    return


class IComponentRegistry(Interface):
    __doc__ = "Register components\n    "

    def registerUtility(component=None, provided=None, name=_BLANK, info=_BLANK, factory=None):
        """Register a utility

        :param factory:
           Factory for the component to be registered.

        :param component:
           The registered component

        :param provided:
           This is the interface provided by the utility.  If the
           component provides a single interface, then this
           argument is optional and the component-implemented
           interface will be used.

        :param name:
           The utility name.

        :param info:
           An object that can be converted to a string to provide
           information about the registration.

        Only one of *component* and *factory* can be used.

        A `IRegistered` event is generated with an `IUtilityRegistration`.
        """
        return

    def unregisterUtility(component=None, provided=None, name=_BLANK, factory=None):
        """Unregister a utility

        :returns:
            A boolean is returned indicating whether the registry was
            changed.  If the given *component* is None and there is no
            component registered, or if the given *component* is not
            None and is not registered, then the function returns
            False, otherwise it returns True.

        :param factory:
           Factory for the component to be unregistered.

        :param component:
           The registered component The given component can be
           None, in which case any component registered to provide
           the given provided interface with the given name is
           unregistered.

        :param provided:
           This is the interface provided by the utility.  If the
           component is not None and provides a single interface,
           then this argument is optional and the
           component-implemented interface will be used.

        :param name:
           The utility name.

        Only one of *component* and *factory* can be used.
        An `IUnregistered` event is generated with an `IUtilityRegistration`.
        """
        return

    def registeredUtilities():
        """Return an iterable of `IUtilityRegistration` instances.

        These registrations describe the current utility registrations
        in the object.
        """
        return

    def registerAdapter(factory, required=None, provided=None, name=_BLANK, info=_BLANK):
        """Register an adapter factory

        :param factory:
            The object used to compute the adapter

        :param required:
            This is a sequence of specifications for objects to be
            adapted.  If omitted, then the value of the factory's
            ``__component_adapts__`` attribute will be used.  The
            ``__component_adapts__`` attribute is
            normally set in class definitions using
            the `.adapter`
            decorator.  If the factory doesn't have a
            ``__component_adapts__`` adapts attribute, then this
            argument is required.

        :param provided:
            This is the interface provided by the adapter and
            implemented by the factory.  If the factory
            implements a single interface, then this argument is
            optional and the factory-implemented interface will be
            used.

        :param name:
            The adapter name.

        :param info:
           An object that can be converted to a string to provide
           information about the registration.

        A `IRegistered` event is generated with an `IAdapterRegistration`.
        """
        return

    def unregisterAdapter(factory=None, required=None, provided=None, name=_BLANK):
        """Unregister an adapter factory

        :returns:
            A boolean is returned indicating whether the registry was
            changed.  If the given component is None and there is no
            component registered, or if the given component is not
            None and is not registered, then the function returns
            False, otherwise it returns True.

        :param factory:
            This is the object used to compute the adapter. The
            factory can be None, in which case any factory
            registered to implement the given provided interface
            for the given required specifications with the given
            name is unregistered.

        :param required:
            This is a sequence of specifications for objects to be
            adapted.  If the factory is not None and the required
            arguments is omitted, then the value of the factory's
            __component_adapts__ attribute will be used.  The
            __component_adapts__ attribute attribute is normally
            set in class definitions using adapts function, or for
            callables using the adapter decorator.  If the factory
            is None or doesn't have a __component_adapts__ adapts
            attribute, then this argument is required.

        :param provided:
            This is the interface provided by the adapter and
            implemented by the factory.  If the factory is not
            None and implements a single interface, then this
            argument is optional and the factory-implemented
            interface will be used.

        :param name:
            The adapter name.

        An `IUnregistered` event is generated with an `IAdapterRegistration`.
        """
        return

    def registeredAdapters():
        """Return an iterable of `IAdapterRegistration` instances.

        These registrations describe the current adapter registrations
        in the object.
        """
        return

    def registerSubscriptionAdapter(factory, required=None, provides=None, name=_BLANK, info=""):
        """Register a subscriber factory

        :param factory:
            The object used to compute the adapter

        :param required:
            This is a sequence of specifications for objects to be
            adapted.  If omitted, then the value of the factory's
            ``__component_adapts__`` attribute will be used.  The
            ``__component_adapts__`` attribute is
            normally set using the adapter
            decorator.  If the factory doesn't have a
            ``__component_adapts__`` adapts attribute, then this
            argument is required.

        :param provided:
            This is the interface provided by the adapter and
            implemented by the factory.  If the factory implements
            a single interface, then this argument is optional and
            the factory-implemented interface will be used.

        :param name:
            The adapter name.

            Currently, only the empty string is accepted.  Other
            strings will be accepted in the future when support for
            named subscribers is added.

        :param info:
           An object that can be converted to a string to provide
           information about the registration.

        A `IRegistered` event is generated with an
        `ISubscriptionAdapterRegistration`.
        """
        return

    def unregisterSubscriptionAdapter(factory=None, required=None, provides=None, name=_BLANK):
        """Unregister a subscriber factory.

        :returns:
            A boolean is returned indicating whether the registry was
            changed.  If the given component is None and there is no
            component registered, or if the given component is not
            None and is not registered, then the function returns
            False, otherwise it returns True.

        :param factory:
            This is the object used to compute the adapter. The
            factory can be None, in which case any factories
            registered to implement the given provided interface
            for the given required specifications with the given
            name are unregistered.

        :param required:
            This is a sequence of specifications for objects to be
            adapted.  If omitted, then the value of the factory's
            ``__component_adapts__`` attribute will be used.  The
            ``__component_adapts__`` attribute is
            normally set using the adapter
            decorator.  If the factory doesn't have a
            ``__component_adapts__`` adapts attribute, then this
            argument is required.

        :param provided:
            This is the interface provided by the adapter and
            implemented by the factory.  If the factory is not
            None implements a single interface, then this argument
            is optional and the factory-implemented interface will
            be used.

        :param name:
            The adapter name.

            Currently, only the empty string is accepted.  Other
            strings will be accepted in the future when support for
            named subscribers is added.

        An `IUnregistered` event is generated with an
        `ISubscriptionAdapterRegistration`.
        """
        return

    def registeredSubscriptionAdapters():
        """Return an iterable of `ISubscriptionAdapterRegistration` instances.

        These registrations describe the current subscription adapter
        registrations in the object.
        """
        return

    def registerHandler(handler, required=None, name=_BLANK, info=""):
        """Register a handler.

        A handler is a subscriber that doesn't compute an adapter
        but performs some function when called.

        :param handler:
            The object used to handle some event represented by
            the objects passed to it.

        :param required:
            This is a sequence of specifications for objects to be
            adapted.  If omitted, then the value of the factory's
            ``__component_adapts__`` attribute will be used.  The
            ``__component_adapts__`` attribute is
            normally set using the adapter
            decorator.  If the factory doesn't have a
            ``__component_adapts__`` adapts attribute, then this
            argument is required.

        :param name:
            The handler name.

            Currently, only the empty string is accepted.  Other
            strings will be accepted in the future when support for
            named handlers is added.

        :param info:
           An object that can be converted to a string to provide
           information about the registration.

        A `IRegistered` event is generated with an `IHandlerRegistration`.
        """
        return

    def unregisterHandler(handler=None, required=None, name=_BLANK):
        """Unregister a handler.

        A handler is a subscriber that doesn't compute an adapter
        but performs some function when called.

        :returns: A boolean is returned indicating whether the registry was
            changed.

        :param handler:
            This is the object used to handle some event
            represented by the objects passed to it. The handler
            can be None, in which case any handlers registered for
            the given required specifications with the given are
            unregistered.

        :param required:
            This is a sequence of specifications for objects to be
            adapted.  If omitted, then the value of the factory's
            ``__component_adapts__`` attribute will be used.  The
            ``__component_adapts__`` attribute is
            normally set using the adapter
            decorator.  If the factory doesn't have a
            ``__component_adapts__`` adapts attribute, then this
            argument is required.

        :param name:
            The handler name.

            Currently, only the empty string is accepted.  Other
            strings will be accepted in the future when support for
            named handlers is added.

        An `IUnregistered` event is generated with an `IHandlerRegistration`.
        """
        return

    def registeredHandlers():
        """Return an iterable of `IHandlerRegistration` instances.

        These registrations describe the current handler registrations
        in the object.
        """
        return


class IComponents(IComponentLookup, IComponentRegistry):
    __doc__ = "Component registration and access\n    "
