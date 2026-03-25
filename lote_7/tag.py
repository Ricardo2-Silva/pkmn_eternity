# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyasn1\type\tag.py
from pyasn1 import error
__all__ = [
 'tagClassUniversal', 'tagClassApplication', 'tagClassContext', 
 'tagClassPrivate', 
 'tagFormatSimple', 'tagFormatConstructed', 
 'tagCategoryImplicit', 'tagCategoryExplicit', 
 'tagCategoryUntagged', 
 'Tag', 'TagSet']
tagClassUniversal = 0
tagClassApplication = 64
tagClassContext = 128
tagClassPrivate = 192
tagFormatSimple = 0
tagFormatConstructed = 32
tagCategoryImplicit = 1
tagCategoryExplicit = 2
tagCategoryUntagged = 4

class Tag(object):
    __doc__ = "Create ASN.1 tag\n\n    Represents ASN.1 tag that can be attached to a ASN.1 type to make\n    types distinguishable from each other.\n\n    *Tag* objects are immutable and duck-type Python :class:`tuple` objects\n    holding three integer components of a tag.\n\n    Parameters\n    ----------\n    tagClass: :py:class:`int`\n        Tag *class* value\n\n    tagFormat: :py:class:`int`\n        Tag *format* value\n\n    tagId: :py:class:`int`\n        Tag ID value\n    "

    def __init__(self, tagClass, tagFormat, tagId):
        if tagId < 0:
            raise error.PyAsn1Error("Negative tag ID (%s) not allowed" % tagId)
        self._Tag__tagClass = tagClass
        self._Tag__tagFormat = tagFormat
        self._Tag__tagId = tagId
        self._Tag__tagClassId = (tagClass, tagId)
        self._Tag__hash = hash(self._Tag__tagClassId)

    def __repr__(self):
        representation = "[%s:%s:%s]" % (self._Tag__tagClass, self._Tag__tagFormat, self._Tag__tagId)
        return "<%s object at 0x%x tag %s>" % (self.__class__.__name__, id(self), representation)

    def __eq__(self, other):
        return self._Tag__tagClassId == other

    def __ne__(self, other):
        return self._Tag__tagClassId != other

    def __lt__(self, other):
        return self._Tag__tagClassId < other

    def __le__(self, other):
        return self._Tag__tagClassId <= other

    def __gt__(self, other):
        return self._Tag__tagClassId > other

    def __ge__(self, other):
        return self._Tag__tagClassId >= other

    def __hash__(self):
        return self._Tag__hash

    def __getitem__(self, idx):
        if idx == 0:
            return self._Tag__tagClass
        else:
            if idx == 1:
                return self._Tag__tagFormat
            if idx == 2:
                return self._Tag__tagId
        raise IndexError()

    def __iter__(self):
        yield self._Tag__tagClass
        yield self._Tag__tagFormat
        yield self._Tag__tagId

    def __and__(self, otherTag):
        return self.__class__(self._Tag__tagClass & otherTag.tagClass, self._Tag__tagFormat & otherTag.tagFormat, self._Tag__tagId & otherTag.tagId)

    def __or__(self, otherTag):
        return self.__class__(self._Tag__tagClass | otherTag.tagClass, self._Tag__tagFormat | otherTag.tagFormat, self._Tag__tagId | otherTag.tagId)

    @property
    def tagClass(self):
        """ASN.1 tag class

        Returns
        -------
        : :py:class:`int`
            Tag class
        """
        return self._Tag__tagClass

    @property
    def tagFormat(self):
        """ASN.1 tag format

        Returns
        -------
        : :py:class:`int`
            Tag format
        """
        return self._Tag__tagFormat

    @property
    def tagId(self):
        """ASN.1 tag ID

        Returns
        -------
        : :py:class:`int`
            Tag ID
        """
        return self._Tag__tagId


class TagSet(object):
    __doc__ = "Create a collection of ASN.1 tags\n\n    Represents a combination of :class:`~pyasn1.type.tag.Tag` objects\n    that can be attached to a ASN.1 type to make types distinguishable\n    from each other.\n\n    *TagSet* objects are immutable and duck-type Python :class:`tuple` objects\n    holding arbitrary number of :class:`~pyasn1.type.tag.Tag` objects.\n\n    Parameters\n    ----------\n    baseTag: :class:`~pyasn1.type.tag.Tag`\n        Base *Tag* object. This tag survives IMPLICIT tagging.\n\n    *superTags: :class:`~pyasn1.type.tag.Tag`\n        Additional *Tag* objects taking part in subtyping.\n\n    Examples\n    --------\n    .. code-block:: python\n\n        class OrderNumber(NumericString):\n            '''\n            ASN.1 specification\n\n            Order-number ::=\n                [APPLICATION 5] IMPLICIT NumericString\n            '''\n            tagSet = NumericString.tagSet.tagImplicitly(\n                Tag(tagClassApplication, tagFormatSimple, 5)\n            )\n\n        orderNumber = OrderNumber('1234')\n    "

    def __init__(self, baseTag=(), *superTags):
        self._TagSet__baseTag = baseTag
        self._TagSet__superTags = superTags
        self._TagSet__superTagsClassId = tuple([(superTag.tagClass, superTag.tagId) for superTag in superTags])
        self._TagSet__lenOfSuperTags = len(superTags)
        self._TagSet__hash = hash(self._TagSet__superTagsClassId)

    def __repr__(self):
        representation = "-".join(["%s:%s:%s" % (x.tagClass, x.tagFormat, x.tagId) for x in self._TagSet__superTags])
        if representation:
            representation = "tags " + representation
        else:
            representation = "untagged"
        return "<%s object at 0x%x %s>" % (self.__class__.__name__, id(self), representation)

    def __add__(self, superTag):
        return (self.__class__)(self._TagSet__baseTag, *self._TagSet__superTags + (superTag,))

    def __radd__(self, superTag):
        return (self.__class__)(self._TagSet__baseTag, *(superTag,) + self._TagSet__superTags)

    def __getitem__(self, i):
        if i.__class__ is slice:
            return (self.__class__)(self._TagSet__baseTag, *self._TagSet__superTags[i])
        else:
            return self._TagSet__superTags[i]

    def __eq__(self, other):
        return self._TagSet__superTagsClassId == other

    def __ne__(self, other):
        return self._TagSet__superTagsClassId != other

    def __lt__(self, other):
        return self._TagSet__superTagsClassId < other

    def __le__(self, other):
        return self._TagSet__superTagsClassId <= other

    def __gt__(self, other):
        return self._TagSet__superTagsClassId > other

    def __ge__(self, other):
        return self._TagSet__superTagsClassId >= other

    def __hash__(self):
        return self._TagSet__hash

    def __len__(self):
        return self._TagSet__lenOfSuperTags

    @property
    def baseTag(self):
        """Return base ASN.1 tag

        Returns
        -------
        : :class:`~pyasn1.type.tag.Tag`
            Base tag of this *TagSet*
        """
        return self._TagSet__baseTag

    @property
    def superTags(self):
        """Return ASN.1 tags

        Returns
        -------
        : :py:class:`tuple`
            Tuple of :class:`~pyasn1.type.tag.Tag` objects that this *TagSet* contains
        """
        return self._TagSet__superTags

    def tagExplicitly(self, superTag):
        """Return explicitly tagged *TagSet*

        Create a new *TagSet* representing callee *TagSet* explicitly tagged
        with passed tag(s). With explicit tagging mode, new tags are appended
        to existing tag(s).

        Parameters
        ----------
        superTag: :class:`~pyasn1.type.tag.Tag`
            *Tag* object to tag this *TagSet*

        Returns
        -------
        : :class:`~pyasn1.type.tag.TagSet`
            New *TagSet* object
        """
        if superTag.tagClass == tagClassUniversal:
            raise error.PyAsn1Error("Can't tag with UNIVERSAL class tag")
        if superTag.tagFormat != tagFormatConstructed:
            superTag = Tag(superTag.tagClass, tagFormatConstructed, superTag.tagId)
        return self + superTag

    def tagImplicitly(self, superTag):
        """Return implicitly tagged *TagSet*

        Create a new *TagSet* representing callee *TagSet* implicitly tagged
        with passed tag(s). With implicit tagging mode, new tag(s) replace the
        last existing tag.

        Parameters
        ----------
        superTag: :class:`~pyasn1.type.tag.Tag`
            *Tag* object to tag this *TagSet*

        Returns
        -------
        : :class:`~pyasn1.type.tag.TagSet`
            New *TagSet* object
        """
        if self._TagSet__superTags:
            superTag = Tag(superTag.tagClass, self._TagSet__superTags[-1].tagFormat, superTag.tagId)
        return self[:-1] + superTag

    def isSuperTagSetOf(self, tagSet):
        """Test type relationship against given *TagSet*

        The callee is considered to be a supertype of given *TagSet*
        tag-wise if all tags in *TagSet* are present in the callee and
        they are in the same order.

        Parameters
        ----------
        tagSet: :class:`~pyasn1.type.tag.TagSet`
            *TagSet* object to evaluate against the callee

        Returns
        -------
        : :py:class:`bool`
            `True` if callee is a supertype of *tagSet*
        """
        if len(tagSet) < self._TagSet__lenOfSuperTags:
            return False
        else:
            return self._TagSet__superTags == tagSet[:self._TagSet__lenOfSuperTags]

    def getBaseTag(self):
        return self._TagSet__baseTag


def initTagSet(tag):
    return TagSet(tag, tag)
