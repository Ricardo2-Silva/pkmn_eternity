# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\model\codecs\__init__.py
from pyglet.util import Codecs, Decoder, Encoder, DecodeException, EncodeException
_codecs = Codecs()
add_decoders = _codecs.add_decoders
get_decoders = _codecs.get_decoders
add_encoders = _codecs.add_encoders
get_encoders = _codecs.get_encoders

class ModelDecodeException(DecodeException):
    return


class ModelEncodeException(EncodeException):
    return


class ModelDecoder(Decoder):

    def decode(self, file, filename, batch):
        """Decode the given file object and return an instance of `Model`.
        Throws ModelDecodeException if there is an error.  filename
        can be a file type hint.
        """
        raise NotImplementedError()


class ModelEncoder(Encoder):

    def encode(self, model, file, filename):
        """Encode the given model to the given file.  filename
        provides a hint to the file format desired.  options are
        encoder-specific, and unknown options should be ignored or
        issue warnings.
        """
        raise NotImplementedError()


def add_default_model_codecs():
    try:
        from pyglet.model.codecs import obj
        add_decoders(obj)
    except ImportError:
        pass
