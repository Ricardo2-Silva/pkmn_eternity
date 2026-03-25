# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyasn1\codec\cer\decoder.py
from pyasn1 import error
from pyasn1.codec.ber import decoder
from pyasn1.compat.octets import oct2int
from pyasn1.type import univ
__all__ = [
 "decode"]

class BooleanDecoder(decoder.AbstractSimpleDecoder):
    protoComponent = univ.Boolean(0)

    def valueDecoder(self, substrate, asn1Spec, tagSet=None, length=None, state=None, decodeFun=None, substrateFun=None, **options):
        head, tail = substrate[:length], substrate[length:]
        if not head or length != 1:
            raise error.PyAsn1Error("Not single-octet Boolean payload")
        else:
            byte = oct2int(head[0])
            if byte == 255:
                value = 1
            elif byte == 0:
                value = 0
            else:
                raise error.PyAsn1Error("Unexpected Boolean payload: %s" % byte)
        return (
         (self._createComponent)(asn1Spec, tagSet, value, **options), tail)


BitStringDecoder = decoder.BitStringDecoder
OctetStringDecoder = decoder.OctetStringDecoder
RealDecoder = decoder.RealDecoder
tagMap = decoder.tagMap.copy()
tagMap.update({(univ.Boolean.tagSet): (BooleanDecoder()), 
 (univ.BitString.tagSet): (BitStringDecoder()), 
 (univ.OctetString.tagSet): (OctetStringDecoder()), 
 (univ.Real.tagSet): (RealDecoder())})
typeMap = decoder.typeMap.copy()
for typeDecoder in tagMap.values():
    if typeDecoder.protoComponent is not None:
        typeId = typeDecoder.protoComponent.__class__.typeId
        if typeId is not None and typeId not in typeMap:
            typeMap[typeId] = typeDecoder

class Decoder(decoder.Decoder):
    return


decode = Decoder(tagMap, decoder.typeMap)
