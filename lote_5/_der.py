# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: cryptography\hazmat\_der.py
from __future__ import absolute_import, division, print_function
import six
from cryptography.utils import int_from_bytes, int_to_bytes
CONSTRUCTED = 32
CONTEXT_SPECIFIC = 128
INTEGER = 2
BIT_STRING = 3
OCTET_STRING = 4
NULL = 5
OBJECT_IDENTIFIER = 6
SEQUENCE = 16 | CONSTRUCTED
SET = 17 | CONSTRUCTED
PRINTABLE_STRING = 19
UTC_TIME = 23
GENERALIZED_TIME = 24

class DERReader(object):

    def __init__(self, data):
        self.data = memoryview(data)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_value is None:
            self.check_empty()

    def is_empty(self):
        return len(self.data) == 0

    def check_empty(self):
        if not self.is_empty():
            raise ValueError("Invalid DER input: trailing data")

    def read_byte(self):
        if len(self.data) < 1:
            raise ValueError("Invalid DER input: insufficient data")
        ret = six.indexbytes(self.data, 0)
        self.data = self.data[1:]
        return ret

    def read_bytes(self, n):
        if len(self.data) < n:
            raise ValueError("Invalid DER input: insufficient data")
        ret = self.data[:n]
        self.data = self.data[n:]
        return ret

    def read_any_element(self):
        tag = self.read_byte()
        if tag & 31 == 31:
            raise ValueError("Invalid DER input: unexpected high tag number")
        length_byte = self.read_byte()
        if length_byte & 128 == 0:
            length = length_byte
        else:
            length_byte &= 127
            if length_byte == 0:
                raise ValueError("Invalid DER input: indefinite length form is not allowed in DER")
            length = 0
            for i in range(length_byte):
                length <<= 8
                length |= self.read_byte()
                if length == 0:
                    raise ValueError("Invalid DER input: length was not minimally-encoded")

        if length < 128:
            raise ValueError("Invalid DER input: length was not minimally-encoded")
        body = self.read_bytes(length)
        return (tag, DERReader(body))

    def read_element(self, expected_tag):
        tag, body = self.read_any_element()
        if tag != expected_tag:
            raise ValueError("Invalid DER input: unexpected tag")
        return body

    def read_single_element(self, expected_tag):
        with self:
            return self.read_element(expected_tag)

    def read_optional_element(self, expected_tag):
        if len(self.data) > 0:
            if six.indexbytes(self.data, 0) == expected_tag:
                return self.read_element(expected_tag)
        return

    def as_integer(self):
        if len(self.data) == 0:
            raise ValueError("Invalid DER input: empty integer contents")
        else:
            first = six.indexbytes(self.data, 0)
            if first & 128 == 128:
                raise ValueError("Negative DER integers are not supported")
            if len(self.data) > 1:
                second = six.indexbytes(self.data, 1)
                if first == 0:
                    if second & 128 == 0:
                        raise ValueError("Invalid DER input: integer not minimally-encoded")
        return int_from_bytes(self.data, "big")


def encode_der_integer(x):
    if not isinstance(x, six.integer_types):
        raise ValueError("Value must be an integer")
    if x < 0:
        raise ValueError("Negative integers are not supported")
    n = x.bit_length() // 8 + 1
    return int_to_bytes(x, n)


def encode_der(tag, *children):
    length = 0
    for child in children:
        length += len(child)

    chunks = [
     six.int2byte(tag)]
    if length < 128:
        chunks.append(six.int2byte(length))
    else:
        length_bytes = int_to_bytes(length)
        chunks.append(six.int2byte(128 | len(length_bytes)))
        chunks.append(length_bytes)
    chunks.extend(children)
    return (b'').join(chunks)
