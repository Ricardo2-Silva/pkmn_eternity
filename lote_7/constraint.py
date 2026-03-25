# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyasn1\type\constraint.py
import sys
from pyasn1.type import error
__all__ = [
 'SingleValueConstraint', 'ContainedSubtypeConstraint', 
 'ValueRangeConstraint', 
 'ValueSizeConstraint', 
 'PermittedAlphabetConstraint', 'InnerTypeConstraint', 
 'ConstraintsExclusion', 
 'ConstraintsIntersection', 
 'ConstraintsUnion']

class AbstractConstraint(object):

    def __init__(self, *values):
        self._valueMap = set()
        self._setValues(values)
        self._AbstractConstraint__hash = hash((self.__class__.__name__, self._values))

    def __call__(self, value, idx=None):
        if not self._values:
            return
        try:
            self._testValue(value, idx)
        except error.ValueConstraintError:
            raise error.ValueConstraintError("%s failed at: %r" % (self, sys.exc_info()[1]))

    def __repr__(self):
        representation = "%s object at 0x%x" % (self.__class__.__name__, id(self))
        if self._values:
            representation += " consts %s" % ", ".join([repr(x) for x in self._values])
        return "<%s>" % representation

    def __eq__(self, other):
        return self is other and True or self._values == other

    def __ne__(self, other):
        return self._values != other

    def __lt__(self, other):
        return self._values < other

    def __le__(self, other):
        return self._values <= other

    def __gt__(self, other):
        return self._values > other

    def __ge__(self, other):
        return self._values >= other

    if sys.version_info[0] <= 2:

        def __nonzero__(self):
            return self._values and True or False

    else:

        def __bool__(self):
            return self._values and True or False

    def __hash__(self):
        return self._AbstractConstraint__hash

    def _setValues(self, values):
        self._values = values

    def _testValue(self, value, idx):
        raise error.ValueConstraintError(value)

    def getValueMap(self):
        return self._valueMap

    def isSuperTypeOf(self, otherConstraint):
        return otherConstraint is self or not self._values or otherConstraint == self or self in otherConstraint.getValueMap()

    def isSubTypeOf(self, otherConstraint):
        return otherConstraint is self or not self or otherConstraint == self or otherConstraint in self._valueMap


class SingleValueConstraint(AbstractConstraint):
    __doc__ = "Create a SingleValueConstraint object.\n\n    The SingleValueConstraint satisfies any value that\n    is present in the set of permitted values.\n\n    The SingleValueConstraint object can be applied to\n    any ASN.1 type.\n\n    Parameters\n    ----------\n    \\*values: :class:`int`\n        Full set of values permitted by this constraint object.\n\n    Examples\n    --------\n    .. code-block:: python\n\n        class DivisorOfSix(Integer):\n            '''\n            ASN.1 specification:\n\n            Divisor-Of-6 ::= INTEGER (1 | 2 | 3 | 6)\n            '''\n            subtypeSpec = SingleValueConstraint(1, 2, 3, 6)\n\n        # this will succeed\n        divisor_of_six = DivisorOfSix(1)\n\n        # this will raise ValueConstraintError\n        divisor_of_six = DivisorOfSix(7)\n    "

    def _setValues(self, values):
        self._values = values
        self._set = set(values)

    def _testValue(self, value, idx):
        if value not in self._set:
            raise error.ValueConstraintError(value)


class ContainedSubtypeConstraint(AbstractConstraint):
    __doc__ = "Create a ContainedSubtypeConstraint object.\n\n    The ContainedSubtypeConstraint satisfies any value that\n    is present in the set of permitted values and also\n    satisfies included constraints.\n\n    The ContainedSubtypeConstraint object can be applied to\n    any ASN.1 type.\n\n    Parameters\n    ----------\n    \\*values:\n        Full set of values and constraint objects permitted\n        by this constraint object.\n\n    Examples\n    --------\n    .. code-block:: python\n\n        class DivisorOfEighteen(Integer):\n            '''\n            ASN.1 specification:\n\n            Divisors-of-18 ::= INTEGER (INCLUDES Divisors-of-6 | 9 | 18)\n            '''\n            subtypeSpec = ContainedSubtypeConstraint(\n                SingleValueConstraint(1, 2, 3, 6), 9, 18\n            )\n\n        # this will succeed\n        divisor_of_eighteen = DivisorOfEighteen(9)\n\n        # this will raise ValueConstraintError\n        divisor_of_eighteen = DivisorOfEighteen(10)\n    "

    def _testValue(self, value, idx):
        for constraint in self._values:
            if isinstance(constraint, AbstractConstraint):
                constraint(value, idx)
            else:
                if value not in self._set:
                    raise error.ValueConstraintError(value)


class ValueRangeConstraint(AbstractConstraint):
    __doc__ = "Create a ValueRangeConstraint object.\n\n    The ValueRangeConstraint satisfies any value that\n    falls in the range of permitted values.\n\n    The ValueRangeConstraint object can only be applied\n    to :class:`~pyasn1.type.univ.Integer` and\n    :class:`~pyasn1.type.univ.Real` types.\n\n    Parameters\n    ----------\n    start: :class:`int`\n        Minimum permitted value in the range (inclusive)\n\n    end: :class:`int`\n        Maximum permitted value in the range (inclusive)\n\n    Examples\n    --------\n    .. code-block:: python\n\n        class TeenAgeYears(Integer):\n            '''\n            ASN.1 specification:\n\n            TeenAgeYears ::= INTEGER (13 .. 19)\n            '''\n            subtypeSpec = ValueRangeConstraint(13, 19)\n\n        # this will succeed\n        teen_year = TeenAgeYears(18)\n\n        # this will raise ValueConstraintError\n        teen_year = TeenAgeYears(20)\n    "

    def _testValue(self, value, idx):
        if value < self.start or value > self.stop:
            raise error.ValueConstraintError(value)

    def _setValues(self, values):
        if len(values) != 2:
            raise error.PyAsn1Error("%s: bad constraint values" % (self.__class__.__name__,))
        self.start, self.stop = values
        if self.start > self.stop:
            raise error.PyAsn1Error("%s: screwed constraint values (start > stop): %s > %s" % (
             self.__class__.__name__,
             self.start, self.stop))
        AbstractConstraint._setValues(self, values)


class ValueSizeConstraint(ValueRangeConstraint):
    __doc__ = "Create a ValueSizeConstraint object.\n\n    The ValueSizeConstraint satisfies any value for\n    as long as its size falls within the range of\n    permitted sizes.\n\n    The ValueSizeConstraint object can be applied\n    to :class:`~pyasn1.type.univ.BitString`,\n    :class:`~pyasn1.type.univ.OctetString` (including\n    all :ref:`character ASN.1 types <type.char>`),\n    :class:`~pyasn1.type.univ.SequenceOf`\n    and :class:`~pyasn1.type.univ.SetOf` types.\n\n    Parameters\n    ----------\n    minimum: :class:`int`\n        Minimum permitted size of the value (inclusive)\n\n    maximum: :class:`int`\n        Maximum permitted size of the value (inclusive)\n\n    Examples\n    --------\n    .. code-block:: python\n\n        class BaseballTeamRoster(SetOf):\n            '''\n            ASN.1 specification:\n\n            BaseballTeamRoster ::= SET SIZE (1..25) OF PlayerNames\n            '''\n            componentType = PlayerNames()\n            subtypeSpec = ValueSizeConstraint(1, 25)\n\n        # this will succeed\n        team = BaseballTeamRoster()\n        team.extend(['Jan', 'Matej'])\n        encode(team)\n\n        # this will raise ValueConstraintError\n        team = BaseballTeamRoster()\n        team.extend(['Jan'] * 26)\n        encode(team)\n\n    Note\n    ----\n    Whenever ValueSizeConstraint is applied to mutable types\n    (e.g. :class:`~pyasn1.type.univ.SequenceOf`,\n    :class:`~pyasn1.type.univ.SetOf`), constraint\n    validation only happens at the serialisation phase rather\n    than schema instantiation phase (as it is with immutable\n    types).\n    "

    def _testValue(self, value, idx):
        valueSize = len(value)
        if valueSize < self.start or valueSize > self.stop:
            raise error.ValueConstraintError(value)


class PermittedAlphabetConstraint(SingleValueConstraint):
    __doc__ = "Create a PermittedAlphabetConstraint object.\n\n    The PermittedAlphabetConstraint satisfies any character\n    string for as long as all its characters are present in\n    the set of permitted characters.\n\n    The PermittedAlphabetConstraint object can only be applied\n    to the :ref:`character ASN.1 types <type.char>` such as\n    :class:`~pyasn1.type.char.IA5String`.\n\n    Parameters\n    ----------\n    \\*alphabet: :class:`str`\n        Full set of characters permitted by this constraint object.\n\n    Examples\n    --------\n    .. code-block:: python\n\n        class BooleanValue(IA5String):\n            '''\n            ASN.1 specification:\n\n            BooleanValue ::= IA5String (FROM ('T' | 'F'))\n            '''\n            subtypeSpec = PermittedAlphabetConstraint('T', 'F')\n\n        # this will succeed\n        truth = BooleanValue('T')\n        truth = BooleanValue('TF')\n\n        # this will raise ValueConstraintError\n        garbage = BooleanValue('TAF')\n    "

    def _setValues(self, values):
        self._values = values
        self._set = set(values)

    def _testValue(self, value, idx):
        if not self._set.issuperset(value):
            raise error.ValueConstraintError(value)


class InnerTypeConstraint(AbstractConstraint):
    __doc__ = "Value must satisfy the type and presence constraints"

    def _testValue(self, value, idx):
        if self._InnerTypeConstraint__singleTypeConstraint:
            self._InnerTypeConstraint__singleTypeConstraint(value)
        elif self._InnerTypeConstraint__multipleTypeConstraint:
            if idx not in self._InnerTypeConstraint__multipleTypeConstraint:
                raise error.ValueConstraintError(value)
            constraint, status = self._InnerTypeConstraint__multipleTypeConstraint[idx]
            if status == "ABSENT":
                raise error.ValueConstraintError(value)
            constraint(value)

    def _setValues(self, values):
        self._InnerTypeConstraint__multipleTypeConstraint = {}
        self._InnerTypeConstraint__singleTypeConstraint = None
        for v in values:
            if isinstance(v, tuple):
                self._InnerTypeConstraint__multipleTypeConstraint[v[0]] = (
                 v[1], v[2])
            else:
                self._InnerTypeConstraint__singleTypeConstraint = v

        AbstractConstraint._setValues(self, values)


class ConstraintsExclusion(AbstractConstraint):
    __doc__ = 'Create a ConstraintsExclusion logic operator object.\n\n    The ConstraintsExclusion logic operator succeeds when the\n    value does *not* satisfy the operand constraint.\n\n    The ConstraintsExclusion object can be applied to\n    any constraint and logic operator object.\n\n    Parameters\n    ----------\n    constraint:\n        Constraint or logic operator object.\n\n    Examples\n    --------\n    .. code-block:: python\n\n        class Lipogramme(IA5STRING):\n            \'\'\'\n            ASN.1 specification:\n\n            Lipogramme ::=\n                IA5String (FROM (ALL EXCEPT ("e"|"E")))\n            \'\'\'\n            subtypeSpec = ConstraintsExclusion(\n                PermittedAlphabetConstraint(\'e\', \'E\')\n            )\n\n        # this will succeed\n        lipogramme = Lipogramme(\'A work of fiction?\')\n\n        # this will raise ValueConstraintError\n        lipogramme = Lipogramme(\'Eel\')\n\n    Warning\n    -------\n    The above example involving PermittedAlphabetConstraint might\n    not work due to the way how PermittedAlphabetConstraint works.\n    The other constraints might work with ConstraintsExclusion\n    though.\n    '

    def _testValue(self, value, idx):
        try:
            self._values[0](value, idx)
        except error.ValueConstraintError:
            return
        else:
            raise error.ValueConstraintError(value)

    def _setValues(self, values):
        if len(values) != 1:
            raise error.PyAsn1Error("Single constraint expected")
        AbstractConstraint._setValues(self, values)


class AbstractConstraintSet(AbstractConstraint):

    def __getitem__(self, idx):
        return self._values[idx]

    def __iter__(self):
        return iter(self._values)

    def __add__(self, value):
        return (self.__class__)(*self._values + (value,))

    def __radd__(self, value):
        return (self.__class__)(*(value,) + self._values)

    def __len__(self):
        return len(self._values)

    def _setValues(self, values):
        self._values = values
        for constraint in values:
            if constraint:
                self._valueMap.add(constraint)
                self._valueMap.update(constraint.getValueMap())


class ConstraintsIntersection(AbstractConstraintSet):
    __doc__ = 'Create a ConstraintsIntersection logic operator object.\n\n    The ConstraintsIntersection logic operator only succeeds\n    if *all* its operands succeed.\n\n    The ConstraintsIntersection object can be applied to\n    any constraint and logic operator objects.\n\n    The ConstraintsIntersection object duck-types the immutable\n    container object like Python :py:class:`tuple`.\n\n    Parameters\n    ----------\n    \\*constraints:\n        Constraint or logic operator objects.\n\n    Examples\n    --------\n    .. code-block:: python\n\n        class CapitalAndSmall(IA5String):\n            \'\'\'\n            ASN.1 specification:\n\n            CapitalAndSmall ::=\n                IA5String (FROM ("A".."Z"|"a".."z"))\n            \'\'\'\n            subtypeSpec = ConstraintsIntersection(\n                PermittedAlphabetConstraint(\'A\', \'Z\'),\n                PermittedAlphabetConstraint(\'a\', \'z\')\n            )\n\n        # this will succeed\n        capital_and_small = CapitalAndSmall(\'Hello\')\n\n        # this will raise ValueConstraintError\n        capital_and_small = CapitalAndSmall(\'hello\')\n    '

    def _testValue(self, value, idx):
        for constraint in self._values:
            constraint(value, idx)


class ConstraintsUnion(AbstractConstraintSet):
    __doc__ = 'Create a ConstraintsUnion logic operator object.\n\n    The ConstraintsUnion logic operator only succeeds if\n    *at least a single* operand succeeds.\n\n    The ConstraintsUnion object can be applied to\n    any constraint and logic operator objects.\n\n    The ConstraintsUnion object duck-types the immutable\n    container object like Python :py:class:`tuple`.\n\n    Parameters\n    ----------\n    \\*constraints:\n        Constraint or logic operator objects.\n\n    Examples\n    --------\n    .. code-block:: python\n\n        class CapitalOrSmall(IA5String):\n            \'\'\'\n            ASN.1 specification:\n\n            CapitalOrSmall ::=\n                IA5String (FROM ("A".."Z") | FROM ("a".."z"))\n            \'\'\'\n            subtypeSpec = ConstraintsIntersection(\n                PermittedAlphabetConstraint(\'A\', \'Z\'),\n                PermittedAlphabetConstraint(\'a\', \'z\')\n            )\n\n        # this will succeed\n        capital_or_small = CapitalAndSmall(\'Hello\')\n\n        # this will raise ValueConstraintError\n        capital_or_small = CapitalOrSmall(\'hello!\')\n    '

    def _testValue(self, value, idx):
        for constraint in self._values:
            try:
                constraint(value, idx)
            except error.ValueConstraintError:
                pass
            else:
                return

        raise error.ValueConstraintError('all of %s failed for "%s"' % (self._values, value))
