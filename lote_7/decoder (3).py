# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyasn1\codec\der\decoder.py
from pyasn1.codec.cer import decoder
from pyasn1.type import univ
__all__ = [
 "decode"]

class BitStringDecoder(decoder.BitStringDecoder):
    supportConstructedForm = False


class OctetStringDecoder(decoder.OctetStringDecoder):
    supportConstructedForm = False


RealDecoder = decoder.RealDecoder
tagMap = decoder.tagMap.copy()
tagMap.update({(univ.BitString.tagSet): (BitStringDecoder()), 
 (univ.OctetString.tagSet): (OctetStringDecoder()), 
 (univ.Real.tagSet): (RealDecoder())})
typeMap = decoder.typeMap.copy()
for typeDecoder in tagMap.values():
    if typeDecoder.protoComponent is not None:
        typeId = typeDecoder.protoComponent.__class__.typeId
        if typeId is not None and typeId not in typeMap:
            typeMap[typeId] = typeDecoder

class Decoder(decoder.Decoder):
    supportIndefLength = False


decode = Decoder(tagMap, typeMap)
