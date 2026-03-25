# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyasn1\type\namedtype.py
import sys
from pyasn1 import error
from pyasn1.type import tag
from pyasn1.type import tagmap
__all__ = [
 "NamedType", "OptionalNamedType", "DefaultedNamedType",
 "NamedTypes"]
try:
    any
except NameError:
    any = lambda x: bool(filter(bool, x))

class NamedType(object):
    __doc__ = "Create named field object for a constructed ASN.1 type.\n\n    The |NamedType| object represents a single name and ASN.1 type of a constructed ASN.1 type.\n\n    |NamedType| objects are immutable and duck-type Python :class:`tuple` objects\n    holding *name* and *asn1Object* components.\n\n    Parameters\n    ----------\n    name: :py:class:`str`\n        Field name\n\n    asn1Object:\n        ASN.1 type object\n    "
    isOptional = False
    isDefaulted = False

    def __init__(self, name, asn1Object, openType=None):
        self._NamedType__name = name
        self._NamedType__type = asn1Object
        self._NamedType__nameAndType = (name, asn1Object)
        self._NamedType__openType = openType

    def __repr__(self):
        representation = "%s=%r" % (self.name, self.asn1Object)
        if self.openType:
            representation += " openType: %r" % self.openType
        return "<%s object at 0x%x type %s>" % (self.__class__.__name__, id(self), representation)

    def __eq__(self, other):
        return self._NamedType__nameAndType == other

    def __ne__(self, other):
        return self._NamedType__nameAndType != other

    def __lt__(self, other):
        return self._NamedType__nameAndType < other

    def __le__(self, other):
        return self._NamedType__nameAndType <= other

    def __gt__(self, other):
        return self._NamedType__nameAndType > other

    def __ge__(self, other):
        return self._NamedType__nameAndType >= other

    def __hash__(self):
        return hash(self._NamedType__nameAndType)

    def __getitem__(self, idx):
        return self._NamedType__nameAndType[idx]

    def __iter__(self):
        return iter(self._NamedType__nameAndType)

    @property
    def name(self):
        return self._NamedType__name

    @property
    def asn1Object(self):
        return self._NamedType__type

    @property
    def openType(self):
        return self._NamedType__openType

    def getName(self):
        return self.name

    def getType(self):
        return self.asn1Object


class OptionalNamedType(NamedType):
    __doc__ = NamedType.__doc__
    isOptional = True


class DefaultedNamedType(NamedType):
    __doc__ = NamedType.__doc__
    isDefaulted = True


class NamedTypes(object):
    __doc__ = "Create a collection of named fields for a constructed ASN.1 type.\n\n    The NamedTypes object represents a collection of named fields of a constructed ASN.1 type.\n\n    *NamedTypes* objects are immutable and duck-type Python :class:`dict` objects\n    holding *name* as keys and ASN.1 type object as values.\n\n    Parameters\n    ----------\n    *namedTypes: :class:`~pyasn1.type.namedtype.NamedType`\n\n    Examples\n    --------\n\n    .. code-block:: python\n\n        class Description(Sequence):\n            '''\n            ASN.1 specification:\n\n            Description ::= SEQUENCE {\n                surname    IA5String,\n                first-name IA5String OPTIONAL,\n                age        INTEGER DEFAULT 40\n            }\n            '''\n            componentType = NamedTypes(\n                NamedType('surname', IA5String()),\n                OptionalNamedType('first-name', IA5String()),\n                DefaultedNamedType('age', Integer(40))\n            )\n\n        descr = Description()\n        descr['surname'] = 'Smith'\n        descr['first-name'] = 'John'\n    "

    def __init__(self, *namedTypes, **kwargs):
        self._NamedTypes__namedTypes = namedTypes
        self._NamedTypes__namedTypesLen = len(self._NamedTypes__namedTypes)
        self._NamedTypes__minTagSet = self._NamedTypes__computeMinTagSet()
        self._NamedTypes__nameToPosMap = self._NamedTypes__computeNameToPosMap()
        self._NamedTypes__tagToPosMap = self._NamedTypes__computeTagToPosMap()
        self._NamedTypes__ambiguousTypes = "terminal" not in kwargs and self._NamedTypes__computeAmbiguousTypes() or {}
        self._NamedTypes__uniqueTagMap = self._NamedTypes__computeTagMaps(unique=True)
        self._NamedTypes__nonUniqueTagMap = self._NamedTypes__computeTagMaps(unique=False)
        self._NamedTypes__hasOptionalOrDefault = any([True for namedType in self._NamedTypes__namedTypes if namedType.isDefaulted or namedType.isOptional])
        self._NamedTypes__hasOpenTypes = any([True for namedType in self._NamedTypes__namedTypes if namedType.openType])
        self._NamedTypes__requiredComponents = frozenset([idx for idx, nt in enumerate(self._NamedTypes__namedTypes) if not nt.isOptional if not nt.isDefaulted])
        self._NamedTypes__keys = frozenset([namedType.name for namedType in self._NamedTypes__namedTypes])
        self._NamedTypes__values = tuple([namedType.asn1Object for namedType in self._NamedTypes__namedTypes])
        self._NamedTypes__items = tuple([(namedType.name, namedType.asn1Object) for namedType in self._NamedTypes__namedTypes])

    def __repr__(self):
        representation = ", ".join(["%r" % x for x in self._NamedTypes__namedTypes])
        return "<%s object at 0x%x types %s>" % (self.__class__.__name__, id(self), representation)

    def __eq__(self, other):
        return self._NamedTypes__namedTypes == other

    def __ne__(self, other):
        return self._NamedTypes__namedTypes != other

    def __lt__(self, other):
        return self._NamedTypes__namedTypes < other

    def __le__(self, other):
        return self._NamedTypes__namedTypes <= other

    def __gt__(self, other):
        return self._NamedTypes__namedTypes > other

    def __ge__(self, other):
        return self._NamedTypes__namedTypes >= other

    def __hash__(self):
        return hash(self._NamedTypes__namedTypes)

    def __getitem__(self, idx):
        try:
            return self._NamedTypes__namedTypes[idx]
        except TypeError:
            return self._NamedTypes__namedTypes[self._NamedTypes__nameToPosMap[idx]]

    def __contains__(self, key):
        return key in self._NamedTypes__nameToPosMap

    def __iter__(self):
        return (x[0] for x in self._NamedTypes__namedTypes)

    if sys.version_info[0] <= 2:

        def __nonzero__(self):
            return self._NamedTypes__namedTypesLen > 0

    else:

        def __bool__(self):
            return self._NamedTypes__namedTypesLen > 0

    def __len__(self):
        return self._NamedTypes__namedTypesLen

    def values(self):
        return self._NamedTypes__values

    def keys(self):
        return self._NamedTypes__keys

    def items(self):
        return self._NamedTypes__items

    def clone(self):
        return (self.__class__)(*self._NamedTypes__namedTypes)

    class PostponedError(object):

        def __init__(self, errorMsg):
            self._PostponedError__errorMsg = errorMsg

        def __getitem__(self, item):
            raise error.PyAsn1Error(self._PostponedError__errorMsg)

    def __computeTagToPosMap(self):
        tagToPosMap = {}
        for idx, namedType in enumerate(self._NamedTypes__namedTypes):
            tagMap = namedType.asn1Object.tagMap
            if isinstance(tagMap, NamedTypes.PostponedError):
                return tagMap
            if not tagMap:
                pass
            else:
                for _tagSet in tagMap.presentTypes:
                    if _tagSet in tagToPosMap:
                        return NamedTypes.PostponedError("Duplicate component tag %s at %s" % (_tagSet, namedType))
                    tagToPosMap[_tagSet] = idx

        return tagToPosMap

    def __computeNameToPosMap(self):
        nameToPosMap = {}
        for idx, namedType in enumerate(self._NamedTypes__namedTypes):
            if namedType.name in nameToPosMap:
                return NamedTypes.PostponedError("Duplicate component name %s at %s" % (namedType.name, namedType))
            nameToPosMap[namedType.name] = idx

        return nameToPosMap

    def __computeAmbiguousTypes(self):
        ambigiousTypes = {}
        partialAmbigiousTypes = ()
        for idx, namedType in reversed(tuple(enumerate(self._NamedTypes__namedTypes))):
            if namedType.isOptional or namedType.isDefaulted:
                partialAmbigiousTypes = (
                 namedType,) + partialAmbigiousTypes
            else:
                partialAmbigiousTypes = (
                 namedType,)
            if len(partialAmbigiousTypes) == len(self._NamedTypes__namedTypes):
                ambigiousTypes[idx] = self
            else:
                ambigiousTypes[idx] = NamedTypes(*partialAmbigiousTypes, **dict(terminal=True))

        return ambigiousTypes

    def getTypeByPosition(self, idx):
        """Return ASN.1 type object by its position in fields set.

        Parameters
        ----------
        idx: :py:class:`int`
            Field index

        Returns
        -------
        :
            ASN.1 type

        Raises
        ------
        : :class:`~pyasn1.error.PyAsn1Error`
            If given position is out of fields range
        """
        try:
            return self._NamedTypes__namedTypes[idx].asn1Object
        except IndexError:
            raise error.PyAsn1Error("Type position out of range")

    def getPositionByType(self, tagSet):
        """Return field position by its ASN.1 type.

        Parameters
        ----------
        tagSet: :class:`~pysnmp.type.tag.TagSet`
            ASN.1 tag set distinguishing one ASN.1 type from others.

        Returns
        -------
        : :py:class:`int`
            ASN.1 type position in fields set

        Raises
        ------
        : :class:`~pyasn1.error.PyAsn1Error`
            If *tagSet* is not present or ASN.1 types are not unique within callee *NamedTypes*
        """
        try:
            return self._NamedTypes__tagToPosMap[tagSet]
        except KeyError:
            raise error.PyAsn1Error("Type %s not found" % (tagSet,))

    def getNameByPosition(self, idx):
        """Return field name by its position in fields set.

        Parameters
        ----------
        idx: :py:class:`idx`
            Field index

        Returns
        -------
        : :py:class:`str`
            Field name

        Raises
        ------
        : :class:`~pyasn1.error.PyAsn1Error`
            If given field name is not present in callee *NamedTypes*
        """
        try:
            return self._NamedTypes__namedTypes[idx].name
        except IndexError:
            raise error.PyAsn1Error("Type position out of range")

    def getPositionByName(self, name):
        """Return field position by filed name.

        Parameters
        ----------
        name: :py:class:`str`
            Field name

        Returns
        -------
        : :py:class:`int`
            Field position in fields set

        Raises
        ------
        : :class:`~pyasn1.error.PyAsn1Error`
            If *name* is not present or not unique within callee *NamedTypes*
        """
        try:
            return self._NamedTypes__nameToPosMap[name]
        except KeyError:
            raise error.PyAsn1Error("Name %s not found" % (name,))

    def getTagMapNearPosition(self, idx):
        """Return ASN.1 types that are allowed at or past given field position.

        Some ASN.1 serialisation allow for skipping optional and defaulted fields.
        Some constructed ASN.1 types allow reordering of the fields. When recovering
        such objects it may be important to know which types can possibly be
        present at any given position in the field sets.

        Parameters
        ----------
        idx: :py:class:`int`
            Field index

        Returns
        -------
        : :class:`~pyasn1.type.tagmap.TagMap`
            Map if ASN.1 types allowed at given field position

        Raises
        ------
        : :class:`~pyasn1.error.PyAsn1Error`
            If given position is out of fields range
        """
        try:
            return self._NamedTypes__ambiguousTypes[idx].tagMap
        except KeyError:
            raise error.PyAsn1Error("Type position out of range")

    def getPositionNearType(self, tagSet, idx):
        """Return the closest field position where given ASN.1 type is allowed.

        Some ASN.1 serialisation allow for skipping optional and defaulted fields.
        Some constructed ASN.1 types allow reordering of the fields. When recovering
        such objects it may be important to know at which field position, in field set,
        given *tagSet* is allowed at or past *idx* position.

        Parameters
        ----------
        tagSet: :class:`~pyasn1.type.tag.TagSet`
           ASN.1 type which field position to look up

        idx: :py:class:`int`
            Field position at or past which to perform ASN.1 type look up

        Returns
        -------
        : :py:class:`int`
            Field position in fields set

        Raises
        ------
        : :class:`~pyasn1.error.PyAsn1Error`
            If *tagSet* is not present or not unique within callee *NamedTypes*
            or *idx* is out of fields range
        """
        try:
            return idx + self._NamedTypes__ambiguousTypes[idx].getPositionByType(tagSet)
        except KeyError:
            raise error.PyAsn1Error("Type position out of range")

    def __computeMinTagSet(self):
        minTagSet = None
        for namedType in self._NamedTypes__namedTypes:
            asn1Object = namedType.asn1Object
            try:
                tagSet = asn1Object.minTagSet
            except AttributeError:
                tagSet = asn1Object.tagSet

            if minTagSet is None or tagSet < minTagSet:
                minTagSet = tagSet

        return minTagSet or tag.TagSet()

    @property
    def minTagSet(self):
        """Return the minimal TagSet among ASN.1 type in callee *NamedTypes*.

        Some ASN.1 types/serialisation protocols require ASN.1 types to be
        arranged based on their numerical tag value. The *minTagSet* property
        returns that.

        Returns
        -------
        : :class:`~pyasn1.type.tagset.TagSet`
            Minimal TagSet among ASN.1 types in callee *NamedTypes*
        """
        return self._NamedTypes__minTagSet

    def __computeTagMaps(self, unique):
        presentTypes = {}
        skipTypes = {}
        defaultType = None
        for namedType in self._NamedTypes__namedTypes:
            tagMap = namedType.asn1Object.tagMap
            if isinstance(tagMap, NamedTypes.PostponedError):
                return tagMap
            for tagSet in tagMap:
                if unique:
                    if tagSet in presentTypes:
                        return NamedTypes.PostponedError("Non-unique tagSet %s of %s at %s" % (tagSet, namedType, self))
                presentTypes[tagSet] = namedType.asn1Object

            skipTypes.update(tagMap.skipTypes)
            if defaultType is None:
                defaultType = tagMap.defaultType
            else:
                if tagMap.defaultType is not None:
                    return NamedTypes.PostponedError("Duplicate default ASN.1 type at %s" % (self,))

        return tagmap.TagMap(presentTypes, skipTypes, defaultType)

    @property
    def tagMap(self):
        """Return a *TagMap* object from tags and types recursively.

        Return a :class:`~pyasn1.type.tagmap.TagMap` object by
        combining tags from *TagMap* objects of children types and
        associating them with their immediate child type.

        Example
        -------
        .. code-block:: python

           OuterType ::= CHOICE {
               innerType INTEGER
           }

        Calling *.tagMap* on *OuterType* will yield a map like this:

        .. code-block:: python

           Integer.tagSet -> Choice
        """
        return self._NamedTypes__nonUniqueTagMap

    @property
    def tagMapUnique(self):
        """Return a *TagMap* object from unique tags and types recursively.

        Return a :class:`~pyasn1.type.tagmap.TagMap` object by
        combining tags from *TagMap* objects of children types and
        associating them with their immediate child type.

        Example
        -------
        .. code-block:: python

           OuterType ::= CHOICE {
               innerType INTEGER
           }

        Calling *.tagMapUnique* on *OuterType* will yield a map like this:

        .. code-block:: python

           Integer.tagSet -> Choice

        Note
        ----

        Duplicate *TagSet* objects found in the tree of children
        types would cause error.
        """
        return self._NamedTypes__uniqueTagMap

    @property
    def hasOptionalOrDefault(self):
        return self._NamedTypes__hasOptionalOrDefault

    @property
    def hasOpenTypes(self):
        return self._NamedTypes__hasOpenTypes

    @property
    def namedTypes(self):
        return tuple(self._NamedTypes__namedTypes)

    @property
    def requiredComponents(self):
        return self._NamedTypes__requiredComponents
