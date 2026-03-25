# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyasn1\codec\ber\decoder.py
from pyasn1 import debug
from pyasn1 import error
from pyasn1.codec.ber import eoo
from pyasn1.compat.integer import from_bytes
from pyasn1.compat.octets import oct2int, octs2ints, ints2octs, null
from pyasn1.type import base
from pyasn1.type import char
from pyasn1.type import tag
from pyasn1.type import tagmap
from pyasn1.type import univ
from pyasn1.type import useful
__all__ = [
 "decode"]
noValue = base.noValue

class AbstractDecoder(object):
    protoComponent = None

    def valueDecoder(self, substrate, asn1Spec, tagSet=None, length=None, state=None, decodeFun=None, substrateFun=None, **options):
        raise error.PyAsn1Error("Decoder not implemented for %s" % (tagSet,))

    def indefLenValueDecoder(self, substrate, asn1Spec, tagSet=None, length=None, state=None, decodeFun=None, substrateFun=None, **options):
        raise error.PyAsn1Error("Indefinite length mode decoder not implemented for %s" % (tagSet,))


class AbstractSimpleDecoder(AbstractDecoder):

    @staticmethod
    def substrateCollector(asn1Object, substrate, length):
        return (substrate[:length], substrate[length:])

    def _createComponent(self, asn1Spec, tagSet, value, **options):
        if options.get("native"):
            return value
        else:
            if asn1Spec is None:
                return self.protoComponent.clone(value, tagSet=tagSet)
            if value is noValue:
                return asn1Spec
            return asn1Spec.clone(value)


class ExplicitTagDecoder(AbstractSimpleDecoder):
    protoComponent = univ.Any("")

    def valueDecoder(self, substrate, asn1Spec, tagSet=None, length=None, state=None, decodeFun=None, substrateFun=None, **options):
        if substrateFun:
            return substrateFun((self._createComponent)(asn1Spec, tagSet, "", **options), substrate, length)
        else:
            head, tail = substrate[:length], substrate[length:]
            value, _ = decodeFun(head, asn1Spec, tagSet, length, **options)
            return (
             value, tail)

    def indefLenValueDecoder(self, substrate, asn1Spec, tagSet=None, length=None, state=None, decodeFun=None, substrateFun=None, **options):
        if substrateFun:
            return substrateFun((self._createComponent)(asn1Spec, tagSet, "", **options), substrate, length)
        value, substrate = decodeFun(substrate, asn1Spec, tagSet, length, **options)
        eooMarker, substrate = decodeFun(substrate, allowEoo=True, **options)
        if eooMarker is eoo.endOfOctets:
            return (
             value, substrate)
        raise error.PyAsn1Error("Missing end-of-octets terminator")


explicitTagDecoder = ExplicitTagDecoder()

class IntegerDecoder(AbstractSimpleDecoder):
    protoComponent = univ.Integer(0)

    def valueDecoder(self, substrate, asn1Spec, tagSet=None, length=None, state=None, decodeFun=None, substrateFun=None, **options):
        if tagSet[0].tagFormat != tag.tagFormatSimple:
            raise error.PyAsn1Error("Simple tag format expected")
        head, tail = substrate[:length], substrate[length:]
        if not head:
            return ((self._createComponent)(asn1Spec, tagSet, 0, **options), tail)
        else:
            value = from_bytes(head, signed=True)
            return (
             (self._createComponent)(asn1Spec, tagSet, value, **options), tail)


class BooleanDecoder(IntegerDecoder):
    protoComponent = univ.Boolean(0)

    def _createComponent(self, asn1Spec, tagSet, value, **options):
        return (IntegerDecoder._createComponent)(self, asn1Spec, tagSet, (value and 1 or 0), **options)


class BitStringDecoder(AbstractSimpleDecoder):
    protoComponent = univ.BitString(())
    supportConstructedForm = True

    def valueDecoder(self, substrate, asn1Spec, tagSet=None, length=None, state=None, decodeFun=None, substrateFun=None, **options):
        head, tail = substrate[:length], substrate[length:]
        if substrateFun:
            return substrateFun((self._createComponent)(asn1Spec, tagSet, noValue, **options), substrate, length)
        if not head:
            raise error.PyAsn1Error("Empty BIT STRING substrate")
        if tagSet[0].tagFormat == tag.tagFormatSimple:
            trailingBits = oct2int(head[0])
            if trailingBits > 7:
                raise error.PyAsn1Error("Trailing bits overflow %s" % trailingBits)
            value = self.protoComponent.fromOctetString((head[1:]), internalFormat=True, padding=trailingBits)
            return (
             (self._createComponent)(asn1Spec, tagSet, value, **options), tail)
        else:
            if not self.supportConstructedForm:
                raise error.PyAsn1Error("Constructed encoding form prohibited at %s" % self.__class__.__name__)
            substrateFun = self.substrateCollector
            bitString = self.protoComponent.fromOctetString(null, internalFormat=True)
            while head:
                component, head = decodeFun(head, self.protoComponent, substrateFun=substrateFun, **options)
                trailingBits = oct2int(component[0])
                if trailingBits > 7:
                    raise error.PyAsn1Error("Trailing bits overflow %s" % trailingBits)
                bitString = self.protoComponent.fromOctetString((component[1:]),
                  internalFormat=True, prepend=bitString,
                  padding=trailingBits)

            return (
             (self._createComponent)(asn1Spec, tagSet, bitString, **options), tail)

    def indefLenValueDecoder(self, substrate, asn1Spec, tagSet=None, length=None, state=None, decodeFun=None, substrateFun=None, **options):
        if substrateFun:
            return substrateFun((self._createComponent)(asn1Spec, tagSet, noValue, **options), substrate, length)
        else:
            substrateFun = self.substrateCollector
            bitString = self.protoComponent.fromOctetString(null, internalFormat=True)
            while substrate:
                component, substrate = decodeFun(substrate, self.protoComponent, substrateFun=substrateFun, 
                 allowEoo=True, **options)
                if component is eoo.endOfOctets:
                    break
                trailingBits = oct2int(component[0])
                if trailingBits > 7:
                    raise error.PyAsn1Error("Trailing bits overflow %s" % trailingBits)
                bitString = self.protoComponent.fromOctetString((component[1:]),
                  internalFormat=True, prepend=bitString,
                  padding=trailingBits)
            else:
                raise error.SubstrateUnderrunError("No EOO seen before substrate ends")

            return ((self._createComponent)(asn1Spec, tagSet, bitString, **options), substrate)


class OctetStringDecoder(AbstractSimpleDecoder):
    protoComponent = univ.OctetString("")
    supportConstructedForm = True

    def valueDecoder(self, substrate, asn1Spec, tagSet=None, length=None, state=None, decodeFun=None, substrateFun=None, **options):
        head, tail = substrate[:length], substrate[length:]
        if substrateFun:
            return substrateFun((self._createComponent)(asn1Spec, tagSet, noValue, **options), substrate, length)
        if tagSet[0].tagFormat == tag.tagFormatSimple:
            return ((self._createComponent)(asn1Spec, tagSet, head, **options), tail)
        else:
            if not self.supportConstructedForm:
                raise error.PyAsn1Error("Constructed encoding form prohibited at %s" % self.__class__.__name__)
            substrateFun = self.substrateCollector
            header = null
            while head:
                component, head = decodeFun(head, self.protoComponent, substrateFun=substrateFun, **options)
                header += component

            return ((self._createComponent)(asn1Spec, tagSet, header, **options), tail)

    def indefLenValueDecoder(self, substrate, asn1Spec, tagSet=None, length=None, state=None, decodeFun=None, substrateFun=None, **options):
        if substrateFun and substrateFun is not self.substrateCollector:
            asn1Object = (self._createComponent)(asn1Spec, tagSet, noValue, **options)
            return substrateFun(asn1Object, substrate, length)
        else:
            substrateFun = self.substrateCollector
            header = null
            while substrate:
                component, substrate = decodeFun(substrate,
 self.protoComponent, substrateFun=substrateFun, 
                 allowEoo=True, **options)
                if component is eoo.endOfOctets:
                    break
                header += component
            else:
                raise error.SubstrateUnderrunError("No EOO seen before substrate ends")

            return (
             (self._createComponent)(asn1Spec, tagSet, header, **options), substrate)


class NullDecoder(AbstractSimpleDecoder):
    protoComponent = univ.Null("")

    def valueDecoder(self, substrate, asn1Spec, tagSet=None, length=None, state=None, decodeFun=None, substrateFun=None, **options):
        if tagSet[0].tagFormat != tag.tagFormatSimple:
            raise error.PyAsn1Error("Simple tag format expected")
        head, tail = substrate[:length], substrate[length:]
        component = (self._createComponent)(asn1Spec, tagSet, "", **options)
        if head:
            raise error.PyAsn1Error("Unexpected %d-octet substrate for Null" % length)
        return (component, tail)


class ObjectIdentifierDecoder(AbstractSimpleDecoder):
    protoComponent = univ.ObjectIdentifier(())

    def valueDecoder(self, substrate, asn1Spec, tagSet=None, length=None, state=None, decodeFun=None, substrateFun=None, **options):
        if tagSet[0].tagFormat != tag.tagFormatSimple:
            raise error.PyAsn1Error("Simple tag format expected")
        else:
            head, tail = substrate[:length], substrate[length:]
            if not head:
                raise error.PyAsn1Error("Empty substrate")
            head = octs2ints(head)
            oid = ()
            index = 0
            substrateLen = len(head)
            while index < substrateLen:
                subId = head[index]
                index += 1
                if subId < 128:
                    oid += (subId,)
                elif subId > 128:
                    nextSubId = subId
                    subId = 0
                    while nextSubId >= 128:
                        subId = (subId << 7) + (nextSubId & 127)
                        if index >= substrateLen:
                            raise error.SubstrateUnderrunError("Short substrate for sub-OID past %s" % (oid,))
                        nextSubId = head[index]
                        index += 1

                    oid += ((subId << 7) + nextSubId,)
                elif subId == 128:
                    raise error.PyAsn1Error("Invalid octet 0x80 in OID encoding")

            if 0 <= oid[0] <= 39:
                oid = (0, ) + oid
            elif 40 <= oid[0] <= 79:
                oid = (
                 1, oid[0] - 40) + oid[1:]
            elif oid[0] >= 80:
                oid = (
                 2, oid[0] - 80) + oid[1:]
            else:
                raise error.PyAsn1Error("Malformed first OID octet: %s" % head[0])
        return (
         (self._createComponent)(asn1Spec, tagSet, oid, **options), tail)


class RealDecoder(AbstractSimpleDecoder):
    protoComponent = univ.Real()

    def valueDecoderParse error at or near `JUMP_IF_TRUE_OR_POP' instruction at offset 488_490


class AbstractConstructedDecoder(AbstractDecoder):
    protoComponent = None


class UniversalConstructedTypeDecoder(AbstractConstructedDecoder):
    protoRecordComponent = None
    protoSequenceComponent = None

    def _getComponentTagMap(self, asn1Object, idx):
        raise NotImplementedError()

    def _getComponentPositionByType(self, asn1Object, tagSet, idx):
        raise NotImplementedError()

    def _decodeComponents(self, substrate, tagSet=None, decodeFun=None, **options):
        components = []
        componentTypes = set()
        while substrate:
            component, substrate = decodeFun(substrate, **options)
            if component is eoo.endOfOctets:
                break
            components.append(component)
            componentTypes.add(component.tagSet)

        if len(componentTypes) > 1:
            protoComponent = self.protoRecordComponent
        else:
            protoComponent = self.protoSequenceComponent
        asn1Object = protoComponent.clone(tagSet=(tag.TagSet)(protoComponent.tagSet.baseTag, *tagSet.superTags))
        for idx, component in enumerate(components):
            asn1Object.setComponentByPosition(idx,
              component, verifyConstraints=False,
              matchTags=False,
              matchConstraints=False)

        return (
         asn1Object, substrate)

    def valueDecoder(self, substrate, asn1Spec, tagSet=None, length=None, state=None, decodeFun=None, substrateFun=None, **options):
        if tagSet[0].tagFormat != tag.tagFormatConstructed:
            raise error.PyAsn1Error("Constructed tag format expected")
        else:
            head, tail = substrate[:length], substrate[length:]
            if substrateFun is not None:
                if asn1Spec is not None:
                    asn1Object = asn1Spec.clone()
                elif self.protoComponent is not None:
                    asn1Object = self.protoComponent.clone(tagSet=tagSet)
                else:
                    asn1Object = (
                     self.protoRecordComponent, self.protoSequenceComponent)
                return substrateFun(asn1Object, substrate, length)
        if asn1Spec is None:
            asn1Object, trailing = (self._decodeComponents)(head, tagSet=tagSet, decodeFun=decodeFun, **options)
            if trailing:
                raise error.PyAsn1Error("Unused trailing %d octets encountered" % len(trailing))
            return (asn1Object, tail)
        else:
            asn1Object = asn1Spec.clone()
            if asn1Spec.typeId in (univ.Sequence.typeId, univ.Set.typeId):
                namedTypes = asn1Spec.componentType
                isSetType = asn1Spec.typeId == univ.Set.typeId
                isDeterministic = not isSetType and not namedTypes.hasOptionalOrDefault
                seenIndices = set()
                idx = 0
                while head:
                    if not namedTypes:
                        componentType = None
                    elif isSetType:
                        componentType = namedTypes.tagMapUnique
                    else:
                        try:
                            if isDeterministic:
                                componentType = namedTypes[idx].asn1Object
                            elif namedTypes[idx].isOptional or namedTypes[idx].isDefaulted:
                                componentType = namedTypes.getTagMapNearPosition(idx)
                            else:
                                componentType = namedTypes[idx].asn1Object
                        except IndexError:
                            raise error.PyAsn1Error("Excessive components decoded at %r" % (asn1Spec,))

                        component, head = decodeFun(head, componentType, **options)
                        if not isDeterministic:
                            if namedTypes:
                                if isSetType:
                                    idx = namedTypes.getPositionByType(component.effectiveTagSet)
                            elif namedTypes[idx].isOptional or namedTypes[idx].isDefaulted:
                                idx = namedTypes.getPositionNearType(component.effectiveTagSet, idx)
                    asn1Object.setComponentByPosition(idx,
                      component, verifyConstraints=False,
                      matchTags=False,
                      matchConstraints=False)
                    seenIndices.add(idx)
                    idx += 1

                if namedTypes:
                    if not namedTypes.requiredComponents.issubset(seenIndices):
                        raise error.PyAsn1Error("ASN.1 object %s has uninitialized components" % asn1Object.__class__.__name__)
                if namedTypes.hasOpenTypes:
                    openTypes = options.get("openTypes", {})
                    if openTypes or options.get("decodeOpenTypes", False):
                        for idx, namedType in enumerate(namedTypes.namedTypes):
                            if not namedType.openType:
                                pass
                            elif namedType.isOptional:
                                if not asn1Object.getComponentByPosition(idx).isValue:
                                    continue
                                governingValue = asn1Object.getComponentByName(namedType.openType.name)
                                try:
                                    openType = openTypes[governingValue]
                                except KeyError:
                                    try:
                                        openType = namedType.openType[governingValue]
                                    except KeyError:
                                        continue

                                component, rest = decodeFun((asn1Object.getComponentByPosition(idx).asOctets()),
                                  asn1Spec=openType)
                                asn1Object.setComponentByPosition(idx, component)

                    else:
                        asn1Object.verifySizeSpec()
            else:
                asn1Object = asn1Spec.clone()
                componentType = asn1Spec.componentType
                idx = 0
                while head:
                    component, head = decodeFun(head, componentType, **options)
                    asn1Object.setComponentByPosition(idx,
                      component, verifyConstraints=False,
                      matchTags=False,
                      matchConstraints=False)
                    idx += 1

            return (
             asn1Object, tail)

    def indefLenValueDecoder(self, substrate, asn1Spec, tagSet=None, length=None, state=None, decodeFun=None, substrateFun=None, **options):
        if tagSet[0].tagFormat != tag.tagFormatConstructed:
            raise error.PyAsn1Error("Constructed tag format expected")
        elif substrateFun is not None:
            if asn1Spec is not None:
                asn1Object = asn1Spec.clone()
            elif self.protoComponent is not None:
                asn1Object = self.protoComponent.clone(tagSet=tagSet)
            else:
                asn1Object = (
                 self.protoRecordComponent, self.protoSequenceComponent)
            return substrateFun(asn1Object, substrate, length)
        if asn1Spec is None:
            return (self._decodeComponents)(
 substrate, tagSet=tagSet, decodeFun=decodeFun, allowEoo=True, **options)
        else:
            asn1Object = asn1Spec.clone()
            if asn1Spec.typeId in (univ.Sequence.typeId, univ.Set.typeId):
                namedTypes = asn1Object.componentType
                isSetType = asn1Object.typeId == univ.Set.typeId
                isDeterministic = not isSetType and not namedTypes.hasOptionalOrDefault
                seenIndices = set()
                idx = 0
                while substrate:
                    if len(namedTypes) <= idx:
                        asn1Spec = None
                    elif isSetType:
                        asn1Spec = namedTypes.tagMapUnique
                    else:
                        try:
                            if isDeterministic:
                                asn1Spec = namedTypes[idx].asn1Object
                            elif namedTypes[idx].isOptional or namedTypes[idx].isDefaulted:
                                asn1Spec = namedTypes.getTagMapNearPosition(idx)
                            else:
                                asn1Spec = namedTypes[idx].asn1Object
                        except IndexError:
                            raise error.PyAsn1Error("Excessive components decoded at %r" % (asn1Object,))

                        component, substrate = decodeFun(substrate, asn1Spec, allowEoo=True, **options)
                        if component is eoo.endOfOctets:
                            break
                        if not isDeterministic:
                            if namedTypes:
                                if isSetType:
                                    idx = namedTypes.getPositionByType(component.effectiveTagSet)
                            elif namedTypes[idx].isOptional or namedTypes[idx].isDefaulted:
                                idx = namedTypes.getPositionNearType(component.effectiveTagSet, idx)
                    asn1Object.setComponentByPosition(idx,
                      component, verifyConstraints=False,
                      matchTags=False,
                      matchConstraints=False)
                    seenIndices.add(idx)
                    idx += 1
                else:
                    raise error.SubstrateUnderrunError("No EOO seen before substrate ends")

                if namedTypes:
                    if not namedTypes.requiredComponents.issubset(seenIndices):
                        raise error.PyAsn1Error("ASN.1 object %s has uninitialized components" % asn1Object.__class__.__name__)
                    elif namedTypes.hasOpenTypes:
                        openTypes = options.get("openTypes", None)
                        if openTypes or options.get("decodeOpenTypes", False):
                            for idx, namedType in enumerate(namedTypes.namedTypes):
                                if not namedType.openType:
                                    pass
                                else:
                                    if namedType.isOptional:
                                        if not asn1Object.getComponentByPosition(idx).isValue:
                                            continue
                                        governingValue = asn1Object.getComponentByName(namedType.openType.name)
                                        try:
                                            openType = openTypes[governingValue]
                                        except KeyError:
                                            try:
                                                openType = namedType.openType[governingValue]
                                            except KeyError:
                                                continue

                                        component, rest = decodeFun((asn1Object.getComponentByPosition(idx).asOctets()),
                                          asn1Spec=openType,
                                          allowEoo=True)
                                        if component is not eoo.endOfOctets:
                                            asn1Object.setComponentByPosition(idx, component)

                    else:
                        asn1Object.verifySizeSpec()
            else:
                asn1Object = asn1Spec.clone()
                componentType = asn1Spec.componentType
                idx = 0
                while substrate:
                    component, substrate = decodeFun(substrate, componentType, allowEoo=True, **options)
                    if component is eoo.endOfOctets:
                        break
                    asn1Object.setComponentByPosition(idx,
                      component, verifyConstraints=False,
                      matchTags=False,
                      matchConstraints=False)
                    idx += 1
                else:
                    raise error.SubstrateUnderrunError("No EOO seen before substrate ends")

            return (asn1Object, substrate)


class SequenceOrSequenceOfDecoder(UniversalConstructedTypeDecoder):
    protoRecordComponent = univ.Sequence()
    protoSequenceComponent = univ.SequenceOf()


class SequenceDecoder(SequenceOrSequenceOfDecoder):
    protoComponent = univ.Sequence()


class SequenceOfDecoder(SequenceOrSequenceOfDecoder):
    protoComponent = univ.SequenceOf()


class SetOrSetOfDecoder(UniversalConstructedTypeDecoder):
    protoRecordComponent = univ.Set()
    protoSequenceComponent = univ.SetOf()


class SetDecoder(SetOrSetOfDecoder):
    protoComponent = univ.Set()


class SetOfDecoder(SetOrSetOfDecoder):
    protoComponent = univ.SetOf()


class ChoiceDecoder(AbstractConstructedDecoder):
    protoComponent = univ.Choice()

    def valueDecoder(self, substrate, asn1Spec, tagSet=None, length=None, state=None, decodeFun=None, substrateFun=None, **options):
        head, tail = substrate[:length], substrate[length:]
        if asn1Spec is None:
            asn1Object = self.protoComponent.clone(tagSet=tagSet)
        else:
            asn1Object = asn1Spec.clone()
        if substrateFun:
            return substrateFun(asn1Object, substrate, length)
        else:
            if asn1Object.tagSet == tagSet:
                component, head = decodeFun(
                 head, (asn1Object.componentTagMap), **options)
            else:
                component, head = decodeFun(
                 head, (asn1Object.componentTagMap), 
                 tagSet, length, state, **options)
            effectiveTagSet = component.effectiveTagSet
            asn1Object.setComponentByType(effectiveTagSet,
              component, verifyConstraints=False,
              matchTags=False,
              matchConstraints=False,
              innerFlag=False)
            return (
             asn1Object, tail)

    def indefLenValueDecoder(self, substrate, asn1Spec, tagSet=None, length=None, state=None, decodeFun=None, substrateFun=None, **options):
        if asn1Spec is None:
            asn1Object = self.protoComponent.clone(tagSet=tagSet)
        else:
            asn1Object = asn1Spec.clone()
        if substrateFun:
            return substrateFun(asn1Object, substrate, length)
        else:
            if asn1Object.tagSet == tagSet:
                component, substrate = decodeFun(
                 substrate, (asn1Object.componentType.tagMapUnique), **options)
                eooMarker, substrate = decodeFun(
 substrate, allowEoo=True, **options)
                if eooMarker is not eoo.endOfOctets:
                    raise error.PyAsn1Error("No EOO seen before substrate ends")
            else:
                component, substrate = decodeFun(
                 substrate, (asn1Object.componentType.tagMapUnique), 
                 tagSet, length, state, **options)
            effectiveTagSet = component.effectiveTagSet
            asn1Object.setComponentByType(effectiveTagSet,
              component, verifyConstraints=False,
              matchTags=False,
              matchConstraints=False,
              innerFlag=False)
            return (
             asn1Object, substrate)


class AnyDecoder(AbstractSimpleDecoder):
    protoComponent = univ.Any()

    def valueDecoder(self, substrate, asn1Spec, tagSet=None, length=None, state=None, decodeFun=None, substrateFun=None, **options):
        if asn1Spec is None or asn1Spec is not None and tagSet != asn1Spec.tagSet:
            fullSubstrate = options["fullSubstrate"]
            length += len(fullSubstrate) - len(substrate)
            substrate = fullSubstrate
        if substrateFun:
            return substrateFun((self._createComponent)(asn1Spec, tagSet, noValue, **options), substrate, length)
        else:
            head, tail = substrate[:length], substrate[length:]
            return (
             (self._createComponent)(asn1Spec, tagSet, head, **options), tail)

    def indefLenValueDecoder(self, substrate, asn1Spec, tagSet=None, length=None, state=None, decodeFun=None, substrateFun=None, **options):
        if asn1Spec is not None and tagSet == asn1Spec.tagSet:
            header = null
        else:
            fullSubstrate = options["fullSubstrate"]
            header = fullSubstrate[:-len(substrate)]
        asn1Spec = self.protoComponent
        if substrateFun and substrateFun is not self.substrateCollector:
            asn1Object = (self._createComponent)(asn1Spec, tagSet, noValue, **options)
            return substrateFun(asn1Object, header + substrate, length + len(header))
        else:
            substrateFun = self.substrateCollector
            while substrate:
                component, substrate = decodeFun(substrate, asn1Spec, substrateFun=substrateFun, 
                 allowEoo=True, **options)
                if component is eoo.endOfOctets:
                    break
                header += component
            else:
                raise error.SubstrateUnderrunError("No EOO seen before substrate ends")

            if substrateFun:
                return (
                 header, substrate)
            return ((self._createComponent)(asn1Spec, tagSet, header, **options), substrate)


class UTF8StringDecoder(OctetStringDecoder):
    protoComponent = char.UTF8String()


class NumericStringDecoder(OctetStringDecoder):
    protoComponent = char.NumericString()


class PrintableStringDecoder(OctetStringDecoder):
    protoComponent = char.PrintableString()


class TeletexStringDecoder(OctetStringDecoder):
    protoComponent = char.TeletexString()


class VideotexStringDecoder(OctetStringDecoder):
    protoComponent = char.VideotexString()


class IA5StringDecoder(OctetStringDecoder):
    protoComponent = char.IA5String()


class GraphicStringDecoder(OctetStringDecoder):
    protoComponent = char.GraphicString()


class VisibleStringDecoder(OctetStringDecoder):
    protoComponent = char.VisibleString()


class GeneralStringDecoder(OctetStringDecoder):
    protoComponent = char.GeneralString()


class UniversalStringDecoder(OctetStringDecoder):
    protoComponent = char.UniversalString()


class BMPStringDecoder(OctetStringDecoder):
    protoComponent = char.BMPString()


class ObjectDescriptorDecoder(OctetStringDecoder):
    protoComponent = useful.ObjectDescriptor()


class GeneralizedTimeDecoder(OctetStringDecoder):
    protoComponent = useful.GeneralizedTime()


class UTCTimeDecoder(OctetStringDecoder):
    protoComponent = useful.UTCTime()


tagMap = {(univ.Integer.tagSet): (IntegerDecoder()), 
 (univ.Boolean.tagSet): (BooleanDecoder()), 
 (univ.BitString.tagSet): (BitStringDecoder()), 
 (univ.OctetString.tagSet): (OctetStringDecoder()), 
 (univ.Null.tagSet): (NullDecoder()), 
 (univ.ObjectIdentifier.tagSet): (ObjectIdentifierDecoder()), 
 (univ.Enumerated.tagSet): (IntegerDecoder()), 
 (univ.Real.tagSet): (RealDecoder()), 
 (univ.Sequence.tagSet): (SequenceOrSequenceOfDecoder()), 
 (univ.Set.tagSet): (SetOrSetOfDecoder()), 
 (univ.Choice.tagSet): (ChoiceDecoder()), 
 (char.UTF8String.tagSet): (UTF8StringDecoder()), 
 (char.NumericString.tagSet): (NumericStringDecoder()), 
 (char.PrintableString.tagSet): (PrintableStringDecoder()), 
 (char.TeletexString.tagSet): (TeletexStringDecoder()), 
 (char.VideotexString.tagSet): (VideotexStringDecoder()), 
 (char.IA5String.tagSet): (IA5StringDecoder()), 
 (char.GraphicString.tagSet): (GraphicStringDecoder()), 
 (char.VisibleString.tagSet): (VisibleStringDecoder()), 
 (char.GeneralString.tagSet): (GeneralStringDecoder()), 
 (char.UniversalString.tagSet): (UniversalStringDecoder()), 
 (char.BMPString.tagSet): (BMPStringDecoder()), 
 (useful.ObjectDescriptor.tagSet): (ObjectDescriptorDecoder()), 
 (useful.GeneralizedTime.tagSet): (GeneralizedTimeDecoder()), 
 (useful.UTCTime.tagSet): (UTCTimeDecoder())}
typeMap = {(univ.Set.typeId): (SetDecoder()), 
 (univ.SetOf.typeId): (SetOfDecoder()), 
 (univ.Sequence.typeId): (SequenceDecoder()), 
 (univ.SequenceOf.typeId): (SequenceOfDecoder()), 
 (univ.Choice.typeId): (ChoiceDecoder()), 
 (univ.Any.typeId): (AnyDecoder())}
for typeDecoder in tagMap.values():
    if typeDecoder.protoComponent is not None:
        typeId = typeDecoder.protoComponent.__class__.typeId
        if typeId is not None and typeId not in typeMap:
            typeMap[typeId] = typeDecoder

stDecodeTag, stDecodeLength, stGetValueDecoder, stGetValueDecoderByAsn1Spec, stGetValueDecoderByTag, stTryAsExplicitTag, stDecodeValue, stDumpRawValue, stErrorCondition, stStop = [x for x in range(10)]

class Decoder(object):
    defaultErrorState = stErrorCondition
    defaultRawDecoder = AnyDecoder()
    supportIndefLength = True

    def __init__(self, tagMap, typeMap={}):
        self._Decoder__tagMap = tagMap
        self._Decoder__typeMap = typeMap
        self._Decoder__tagCache = {}
        self._Decoder__tagSetCache = {}
        self._Decoder__eooSentinel = ints2octs((0, 0))

    def __call__Parse error at or near `JUMP_IF_TRUE_OR_POP' instruction at offset 870_872


decode = Decoder(tagMap, typeMap)