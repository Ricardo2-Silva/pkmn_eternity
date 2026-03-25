# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: zope\interface\declarations.py
"""Implementation of interface declarations

There are three flavors of declarations:

  - Declarations are used to simply name declared interfaces.

  - ImplementsDeclarations are used to express the interfaces that a
    class implements (that instances of the class provides).

    Implements specifications support inheriting interfaces.

  - ProvidesDeclarations are used to express interfaces directly
    provided by objects.

"""
__docformat__ = "restructuredtext"
import sys
from types import FunctionType
from types import MethodType
from types import ModuleType
import weakref
from zope.interface.advice import addClassAdvisor
from zope.interface.interface import InterfaceClass
from zope.interface.interface import SpecificationBase
from zope.interface.interface import Specification
from zope.interface._compat import CLASS_TYPES as DescriptorAwareMetaClasses
from zope.interface._compat import PYTHON3
BuiltinImplementationSpecifications = {}
_ADVICE_ERROR = "Class advice impossible in Python3.  Use the @%s class decorator instead."
_ADVICE_WARNING = "The %s API is deprecated, and will not work in Python3  Use the @%s class decorator instead."

class named(object):

    def __init__(self, name):
        self.name = name

    def __call__(self, ob):
        ob.__component_name__ = self.name
        return ob


class Declaration(Specification):
    __doc__ = "Interface declarations"

    def __init__(self, *interfaces):
        Specification.__init__(self, _normalizeargs(interfaces))

    def changed(self, originally_changed):
        Specification.changed(self, originally_changed)
        try:
            del self._v_attrs
        except AttributeError:
            pass

    def __contains__(self, interface):
        """Test whether an interface is in the specification
        """
        return self.extends(interface) and interface in self.interfaces()

    def __iter__(self):
        """Return an iterator for the interfaces in the specification
        """
        return self.interfaces()

    def flattened(self):
        """Return an iterator of all included and extended interfaces
        """
        return iter(self.__iro__)

    def __sub__(self, other):
        """Remove interfaces from a specification
        """
        return Declaration(*[i for i in self.interfaces() if not [j for j in other.interfaces() if i.extends(j, 0)]])

    def __add__(self, other):
        """Add two specifications or a specification and an interface
        """
        seen = {}
        result = []
        for i in self.interfaces():
            seen[i] = 1
            result.append(i)

        for i in other.interfaces():
            if i not in seen:
                seen[i] = 1
                result.append(i)

        return Declaration(*result)

    __radd__ = __add__


class Implements(Declaration):
    inherit = None
    declared = ()
    __name__ = "?"

    @classmethod
    def named(cls, name, *interfaces):
        inst = cls.__new__(cls)
        inst.__name__ = name
        (inst.__init__)(*interfaces)
        return inst

    def __repr__(self):
        return "<implementedBy %s>" % self.__name__

    def __reduce__(self):
        return (
         implementedBy, (self.inherit,))

    def __cmp(self, other):
        if other is None:
            return -1
        else:
            n1 = (
             self.__name__, self.__module__)
            n2 = (getattr(other, "__name__", ""), getattr(other, "__module__", ""))
            return (n1 > n2) - (n1 < n2)

    def __hash__(self):
        return Declaration.__hash__(self)

    def __lt__(self, other):
        c = self._Implements__cmp(other)
        return c < 0

    def __le__(self, other):
        c = self._Implements__cmp(other)
        return c <= 0

    def __gt__(self, other):
        c = self._Implements__cmp(other)
        return c > 0

    def __ge__(self, other):
        c = self._Implements__cmp(other)
        return c >= 0


def _implements_name(ob):
    return (getattr(ob, "__module__", "?") or "?") + "." + (getattr(ob, "__name__", "?") or "?")


def implementedByFallback(cls):
    """Return the interfaces implemented for a class' instances

      The value returned is an `~zope.interface.interfaces.IDeclaration`.
    """
    try:
        spec = cls.__dict__.get("__implemented__")
    except AttributeError:
        spec = getattr(cls, "__implemented__", None)
        if spec is None:
            spec = BuiltinImplementationSpecifications.get(cls)
            if spec is not None:
                return spec
            else:
                return _empty
        if spec.__class__ == Implements:
            return spec
        return Declaration(*_normalizeargs((spec,)))
    else:
        if isinstance(spec, Implements):
            return spec
        else:
            if spec is None:
                spec = BuiltinImplementationSpecifications.get(cls)
                if spec is not None:
                    return spec
            spec_name = _implements_name(cls)
            if spec is not None:
                spec = (spec,)
                spec = (Implements.named)(spec_name, *_normalizeargs(spec))
                spec.inherit = None
                del cls.__implemented__
            else:
                try:
                    bases = cls.__bases__
                except AttributeError:
                    if not callable(cls):
                        raise TypeError("ImplementedBy called for non-factory", cls)
                    bases = ()

                spec = (Implements.named)(spec_name, *[implementedBy(c) for c in bases])
                spec.inherit = cls
            try:
                cls.__implemented__ = spec
                if not hasattr(cls, "__providedBy__"):
                    cls.__providedBy__ = objectSpecificationDescriptor
                if isinstance(cls, DescriptorAwareMetaClasses):
                    if "__provides__" not in cls.__dict__:
                        cls.__provides__ = ClassProvides(cls, getattr(cls, "__class__", type(cls)))
            except TypeError:
                if not isinstance(cls, type):
                    raise TypeError("ImplementedBy called for non-type", cls)
                BuiltinImplementationSpecifications[cls] = spec

            return spec


implementedBy = implementedByFallback

def classImplementsOnly(cls, *interfaces):
    """Declare the only interfaces implemented by instances of a class

      The arguments after the class are one or more interfaces or interface
      specifications (`~zope.interface.interfaces.IDeclaration` objects).

      The interfaces given (including the interfaces in the specifications)
      replace any previous declarations.
    """
    spec = implementedBy(cls)
    spec.declared = ()
    spec.inherit = None
    classImplements(cls, *interfaces)


def classImplements(cls, *interfaces):
    """Declare additional interfaces implemented for instances of a class

      The arguments after the class are one or more interfaces or
      interface specifications (`~zope.interface.interfaces.IDeclaration` objects).

      The interfaces given (including the interfaces in the specifications)
      are added to any interfaces previously declared.
    """
    spec = implementedBy(cls)
    spec.declared += tuple(_normalizeargs(interfaces))
    bases = []
    seen = {}
    for b in spec.declared:
        if b not in seen:
            seen[b] = 1
            bases.append(b)

    if spec.inherit is not None:
        for c in spec.inherit.__bases__:
            b = implementedBy(c)
            if b not in seen:
                seen[b] = 1
                bases.append(b)

    spec.__bases__ = tuple(bases)


def _implements_advice(cls):
    interfaces, classImplements = cls.__dict__["__implements_advice_data__"]
    del cls.__implements_advice_data__
    classImplements(cls, *interfaces)
    return cls


class implementer(object):
    __doc__ = "Declare the interfaces implemented by instances of a class.\n\n      This function is called as a class decorator.\n\n      The arguments are one or more interfaces or interface\n      specifications (`~zope.interface.interfaces.IDeclaration` objects).\n\n      The interfaces given (including the interfaces in the\n      specifications) are added to any interfaces previously\n      declared.\n\n      Previous declarations include declarations for base classes\n      unless implementsOnly was used.\n\n      This function is provided for convenience. It provides a more\n      convenient way to call `classImplements`. For example::\n\n        @implementer(I1)\n        class C(object):\n            pass\n\n      is equivalent to calling::\n\n        classImplements(C, I1)\n\n      after the class has been created.\n      "

    def __init__(self, *interfaces):
        self.interfaces = interfaces

    def __call__(self, ob):
        if isinstance(ob, DescriptorAwareMetaClasses):
            classImplements(ob, *self.interfaces)
            return ob
        else:
            spec_name = _implements_name(ob)
            spec = (Implements.named)(spec_name, *self.interfaces)
            try:
                ob.__implemented__ = spec
            except AttributeError:
                raise TypeError("Can't declare implements", ob)

            return ob


class implementer_only(object):
    __doc__ = "Declare the only interfaces implemented by instances of a class\n\n      This function is called as a class decorator.\n\n      The arguments are one or more interfaces or interface\n      specifications (`~zope.interface.interfaces.IDeclaration` objects).\n\n      Previous declarations including declarations for base classes\n      are overridden.\n\n      This function is provided for convenience. It provides a more\n      convenient way to call `classImplementsOnly`. For example::\n\n        @implementer_only(I1)\n        class C(object): pass\n\n      is equivalent to calling::\n\n        classImplementsOnly(I1)\n\n      after the class has been created.\n      "

    def __init__(self, *interfaces):
        self.interfaces = interfaces

    def __call__(self, ob):
        if isinstance(ob, (FunctionType, MethodType)):
            raise ValueError("The implementer_only decorator is not supported for methods or functions.")
        else:
            classImplementsOnly(ob, *self.interfaces)
            return ob


def _implements(name, interfaces, classImplements):
    frame = sys._getframe(2)
    locals = frame.f_locals
    if locals is frame.f_globals or "__module__" not in locals:
        raise TypeError(name + " can be used only from a class definition.")
    if "__implements_advice_data__" in locals:
        raise TypeError(name + " can be used only once in a class definition.")
    locals["__implements_advice_data__"] = (interfaces, classImplements)
    addClassAdvisor(_implements_advice, depth=3)


def implements(*interfaces):
    """Declare interfaces implemented by instances of a class

      This function is called in a class definition.

      The arguments are one or more interfaces or interface
      specifications (`~zope.interface.interfaces.IDeclaration` objects).

      The interfaces given (including the interfaces in the
      specifications) are added to any interfaces previously
      declared.

      Previous declarations include declarations for base classes
      unless `implementsOnly` was used.

      This function is provided for convenience. It provides a more
      convenient way to call `classImplements`. For example::

        implements(I1)

      is equivalent to calling::

        classImplements(C, I1)

      after the class has been created.
    """
    if PYTHON3:
        raise TypeError(_ADVICE_ERROR % "implementer")
    _implements("implements", interfaces, classImplements)


def implementsOnly(*interfaces):
    """Declare the only interfaces implemented by instances of a class

      This function is called in a class definition.

      The arguments are one or more interfaces or interface
      specifications (`~zope.interface.interfaces.IDeclaration` objects).

      Previous declarations including declarations for base classes
      are overridden.

      This function is provided for convenience. It provides a more
      convenient way to call `classImplementsOnly`. For example::

        implementsOnly(I1)

      is equivalent to calling::

        classImplementsOnly(I1)

      after the class has been created.
    """
    if PYTHON3:
        raise TypeError(_ADVICE_ERROR % "implementer_only")
    _implements("implementsOnly", interfaces, classImplementsOnly)


class Provides(Declaration):
    __doc__ = "Implement ``__provides__``, the instance-specific specification\n\n    When an object is pickled, we pickle the interfaces that it implements.\n    "

    def __init__(self, cls, *interfaces):
        self._Provides__args = (
         cls,) + interfaces
        self._cls = cls
        (Declaration.__init__)(self, *interfaces + (implementedBy(cls),))

    def __reduce__(self):
        return (
         Provides, self._Provides__args)

    __module__ = "zope.interface"

    def __get__(self, inst, cls):
        """Make sure that a class __provides__ doesn't leak to an instance
        """
        if inst is None:
            if cls is self._cls:
                return self
        raise AttributeError("__provides__")


ProvidesClass = Provides
InstanceDeclarations = weakref.WeakValueDictionary()

def Provides(*interfaces):
    """Cache instance declarations

      Instance declarations are shared among instances that have the same
      declaration. The declarations are cached in a weak value dictionary.
    """
    spec = InstanceDeclarations.get(interfaces)
    if spec is None:
        spec = ProvidesClass(*interfaces)
        InstanceDeclarations[interfaces] = spec
    return spec


Provides.__safe_for_unpickling__ = True

def directlyProvides(object, *interfaces):
    """Declare interfaces declared directly for an object

      The arguments after the object are one or more interfaces or interface
      specifications (`~zope.interface.interfaces.IDeclaration` objects).

      The interfaces given (including the interfaces in the specifications)
      replace interfaces previously declared for the object.
    """
    cls = getattr(object, "__class__", None)
    if cls is not None:
        if getattr(cls, "__class__", None) is cls:
            if not isinstance(object, DescriptorAwareMetaClasses):
                raise TypeError("Attempt to make an interface declaration on a non-descriptor-aware class")
    interfaces = _normalizeargs(interfaces)
    if cls is None:
        cls = type(object)
    else:
        issub = False
        for damc in DescriptorAwareMetaClasses:
            if issubclass(cls, damc):
                issub = True
                break

        if issub:
            object.__provides__ = ClassProvides(object, cls, *interfaces)
        else:
            object.__provides__ = Provides(cls, *interfaces)


def alsoProvides(object, *interfaces):
    """Declare interfaces declared directly for an object

    The arguments after the object are one or more interfaces or interface
    specifications (`~zope.interface.interfaces.IDeclaration` objects).

    The interfaces given (including the interfaces in the specifications) are
    added to the interfaces previously declared for the object.
    """
    directlyProvides(object, directlyProvidedBy(object), *interfaces)


def noLongerProvides(object, interface):
    """ Removes a directly provided interface from an object.
    """
    directlyProvides(object, directlyProvidedBy(object) - interface)
    if interface.providedBy(object):
        raise ValueError("Can only remove directly provided interfaces.")


class ClassProvidesBaseFallback(object):

    def __get__(self, inst, cls):
        if cls is self._cls:
            if inst is None:
                return self
            else:
                return self._implements
        raise AttributeError("__provides__")


ClassProvidesBasePy = ClassProvidesBaseFallback
ClassProvidesBase = ClassProvidesBaseFallback
try:
    import zope.interface._zope_interface_coptimizations
except ImportError:
    pass
else:
    from zope.interface._zope_interface_coptimizations import ClassProvidesBase

class ClassProvides(Declaration, ClassProvidesBase):
    __doc__ = "Special descriptor for class ``__provides__``\n\n    The descriptor caches the implementedBy info, so that\n    we can get declarations for objects without instance-specific\n    interfaces a bit quicker.\n    "

    def __init__(self, cls, metacls, *interfaces):
        self._cls = cls
        self._implements = implementedBy(cls)
        self._ClassProvides__args = (cls, metacls) + interfaces
        (Declaration.__init__)(self, *interfaces + (implementedBy(metacls),))

    def __reduce__(self):
        return (
         self.__class__, self._ClassProvides__args)

    __get__ = ClassProvidesBase.__get__


def directlyProvidedBy(object):
    """Return the interfaces directly provided by the given object

    The value returned is an `~zope.interface.interfaces.IDeclaration`.
    """
    provides = getattr(object, "__provides__", None)
    if provides is None or isinstance(provides, Implements):
        return _empty
    else:
        return Declaration(provides.__bases__[:-1])


def classProvides(*interfaces):
    """Declare interfaces provided directly by a class

      This function is called in a class definition.

      The arguments are one or more interfaces or interface specifications
      (`~zope.interface.interfaces.IDeclaration` objects).

      The given interfaces (including the interfaces in the specifications)
      are used to create the class's direct-object interface specification.
      An error will be raised if the module class has an direct interface
      specification. In other words, it is an error to call this function more
      than once in a class definition.

      Note that the given interfaces have nothing to do with the interfaces
      implemented by instances of the class.

      This function is provided for convenience. It provides a more convenient
      way to call `directlyProvides` for a class. For example::

        classProvides(I1)

      is equivalent to calling::

        directlyProvides(theclass, I1)

      after the class has been created.
    """
    if PYTHON3:
        raise TypeError(_ADVICE_ERROR % "provider")
    else:
        frame = sys._getframe(1)
        locals = frame.f_locals
        if locals is frame.f_globals or "__module__" not in locals:
            raise TypeError("classProvides can be used only from a class definition.")
        if "__provides__" in locals:
            raise TypeError("classProvides can only be used once in a class definition.")
    locals["__provides__"] = _normalizeargs(interfaces)
    addClassAdvisor(_classProvides_advice, depth=2)


def _classProvides_advice(cls):
    interfaces = cls.__dict__["__provides__"]
    del cls.__provides__
    directlyProvides(cls, *interfaces)
    return cls


class provider(object):
    __doc__ = "Class decorator version of classProvides"

    def __init__(self, *interfaces):
        self.interfaces = interfaces

    def __call__(self, ob):
        directlyProvides(ob, *self.interfaces)
        return ob


def moduleProvides(*interfaces):
    """Declare interfaces provided by a module

    This function is used in a module definition.

    The arguments are one or more interfaces or interface specifications
    (`~zope.interface.interfaces.IDeclaration` objects).

    The given interfaces (including the interfaces in the specifications) are
    used to create the module's direct-object interface specification.  An
    error will be raised if the module already has an interface specification.
    In other words, it is an error to call this function more than once in a
    module definition.

    This function is provided for convenience. It provides a more convenient
    way to call directlyProvides. For example::

      moduleImplements(I1)

    is equivalent to::

      directlyProvides(sys.modules[__name__], I1)
    """
    frame = sys._getframe(1)
    locals = frame.f_locals
    if locals is not frame.f_globals or "__name__" not in locals:
        raise TypeError("moduleProvides can only be used from a module definition.")
    if "__provides__" in locals:
        raise TypeError("moduleProvides can only be used once in a module definition.")
    locals["__provides__"] = Provides(ModuleType, *_normalizeargs(interfaces))


def ObjectSpecification(direct, cls):
    """Provide object specifications

    These combine information for the object and for it's classes.
    """
    return Provides(cls, direct)


def getObjectSpecificationFallback(ob):
    provides = getattr(ob, "__provides__", None)
    if provides is not None:
        if isinstance(provides, SpecificationBase):
            return provides
    try:
        cls = ob.__class__
    except AttributeError:
        return _empty
    else:
        return implementedBy(cls)


getObjectSpecification = getObjectSpecificationFallback

def providedByFallback(ob):
    try:
        r = ob.__providedBy__
    except AttributeError:
        return getObjectSpecification(ob)
    else:
        try:
            r.extends
        except AttributeError:
            try:
                r = ob.__provides__
            except AttributeError:
                return implementedBy(ob.__class__)
            else:
                try:
                    cp = ob.__class__.__provides__
                except AttributeError:
                    return r

            if r is cp:
                return implementedBy(ob.__class__)

        return r


providedBy = providedByFallback

class ObjectSpecificationDescriptorFallback(object):
    __doc__ = "Implement the `__providedBy__` attribute\n\n    The `__providedBy__` attribute computes the interfaces peovided by\n    an object.\n    "

    def __get__(self, inst, cls):
        """Get an object specification for an object
        """
        if inst is None:
            return getObjectSpecification(cls)
        else:
            provides = getattr(inst, "__provides__", None)
            if provides is not None:
                return provides
            return implementedBy(cls)


ObjectSpecificationDescriptor = ObjectSpecificationDescriptorFallback

def _normalizeargs(sequence, output=None):
    """Normalize declaration arguments

    Normalization arguments might contain Declarions, tuples, or single
    interfaces.

    Anything but individial interfaces or implements specs will be expanded.
    """
    if output is None:
        output = []
    else:
        cls = sequence.__class__
        if InterfaceClass in cls.__mro__ or Implements in cls.__mro__:
            output.append(sequence)
        else:
            for v in sequence:
                _normalizeargs(v, output)

    return output


_empty = Declaration()
try:
    import zope.interface._zope_interface_coptimizations
except ImportError:
    pass
else:
    from zope.interface._zope_interface_coptimizations import implementedBy
    from zope.interface._zope_interface_coptimizations import providedBy
    from zope.interface._zope_interface_coptimizations import getObjectSpecification
    from zope.interface._zope_interface_coptimizations import ObjectSpecificationDescriptor
objectSpecificationDescriptor = ObjectSpecificationDescriptor()
