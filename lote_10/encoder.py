# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: simplejson\encoder.py
"""Implementation of JSONEncoder
"""
from __future__ import absolute_import
import re
from operator import itemgetter
import decimal
from .compat import unichr, binary_type, text_type, string_types, integer_types, PY3

def _import_speedups():
    try:
        from . import _speedups
        return (
         _speedups.encode_basestring_ascii, _speedups.make_encoder)
    except ImportError:
        return (None, None)


c_encode_basestring_ascii, c_make_encoder = _import_speedups()
from .decoder import PosInf
from .raw_json import RawJSON
ESCAPE = re.compile('[\\x00-\\x1f\\\\"]')
ESCAPE_ASCII = re.compile('([\\\\"]|[^\\ -~])')
HAS_UTF8 = re.compile("[\\x80-\\xff]")
ESCAPE_DCT = {
 '\\': '"\\\\\\\\"', 
 '"': '\'\\\\"\'', 
 '\x08': '"\\\\b"', 
 '\x0c': '"\\\\f"', 
 '\n': '"\\\\n"', 
 '\r': '"\\\\r"', 
 '\t': '"\\\\t"'}
for i in range(32):
    ESCAPE_DCT.setdefault(chr(i), "\\u%04x" % (i,))

FLOAT_REPR = repr

def encode_basestring(s, _PY3=PY3, _q='"'):
    """Return a JSON representation of a Python string

    """
    if _PY3:
        if isinstance(s, bytes):
            s = str(s, "utf-8")
    elif type(s) is not str:
        s = str.__str__(s)
    elif isinstance(s, str):
        if HAS_UTF8.search(s) is not None:
            s = unicode(s, "utf-8")
        if type(s) not in (str, unicode):
            if isinstance(s, str):
                s = str.__str__(s)
    else:
        s = unicode.__getnewargs__(s)[0]

    def replace(match):
        return ESCAPE_DCT[match.group(0)]

    return _q + ESCAPE.sub(replace, s) + _q


def py_encode_basestring_ascii(s, _PY3=PY3):
    """Return an ASCII-only JSON representation of a Python string

    """
    if _PY3:
        if isinstance(s, bytes):
            s = str(s, "utf-8")
    elif type(s) is not str:
        s = str.__str__(s)
    elif isinstance(s, str):
        if HAS_UTF8.search(s) is not None:
            s = unicode(s, "utf-8")
        if type(s) not in (str, unicode):
            if isinstance(s, str):
                s = str.__str__(s)
    else:
        s = unicode.__getnewargs__(s)[0]

    def replace(match):
        s = match.group(0)
        try:
            return ESCAPE_DCT[s]
        except KeyError:
            n = ord(s)
            if n < 65536:
                return "\\u%04x" % (n,)
            else:
                n -= 65536
                s1 = 55296 | n >> 10 & 1023
                s2 = 56320 | n & 1023
                return "\\u%04x\\u%04x" % (s1, s2)

    return '"' + str(ESCAPE_ASCII.sub(replace, s)) + '"'


encode_basestring_ascii = c_encode_basestring_ascii or py_encode_basestring_ascii

class JSONEncoder(object):
    __doc__ = "Extensible JSON <http://json.org> encoder for Python data structures.\n\n    Supports the following objects and types by default:\n\n    +-------------------+---------------+\n    | Python            | JSON          |\n    +===================+===============+\n    | dict, namedtuple  | object        |\n    +-------------------+---------------+\n    | list, tuple       | array         |\n    +-------------------+---------------+\n    | str, unicode      | string        |\n    +-------------------+---------------+\n    | int, long, float  | number        |\n    +-------------------+---------------+\n    | True              | true          |\n    +-------------------+---------------+\n    | False             | false         |\n    +-------------------+---------------+\n    | None              | null          |\n    +-------------------+---------------+\n\n    To extend this to recognize other objects, subclass and implement a\n    ``.default()`` method with another method that returns a serializable\n    object for ``o`` if possible, otherwise it should call the superclass\n    implementation (to raise ``TypeError``).\n\n    "
    item_separator = ", "
    key_separator = ": "

    def __init__(self, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, sort_keys=False, indent=None, separators=None, encoding='utf-8', default=None, use_decimal=True, namedtuple_as_object=True, tuple_as_array=True, bigint_as_string=False, item_sort_key=None, for_json=False, ignore_nan=False, int_as_string_bitcount=None, iterable_as_array=False):
        """Constructor for JSONEncoder, with sensible defaults.

        If skipkeys is false, then it is a TypeError to attempt
        encoding of keys that are not str, int, long, float or None.  If
        skipkeys is True, such items are simply skipped.

        If ensure_ascii is true, the output is guaranteed to be str
        objects with all incoming unicode characters escaped.  If
        ensure_ascii is false, the output will be unicode object.

        If check_circular is true, then lists, dicts, and custom encoded
        objects will be checked for circular references during encoding to
        prevent an infinite recursion (which would cause an OverflowError).
        Otherwise, no such check takes place.

        If allow_nan is true, then NaN, Infinity, and -Infinity will be
        encoded as such.  This behavior is not JSON specification compliant,
        but is consistent with most JavaScript based encoders and decoders.
        Otherwise, it will be a ValueError to encode such floats.

        If sort_keys is true, then the output of dictionaries will be
        sorted by key; this is useful for regression tests to ensure
        that JSON serializations can be compared on a day-to-day basis.

        If indent is a string, then JSON array elements and object members
        will be pretty-printed with a newline followed by that string repeated
        for each level of nesting. ``None`` (the default) selects the most compact
        representation without any newlines. For backwards compatibility with
        versions of simplejson earlier than 2.1.0, an integer is also accepted
        and is converted to a string with that many spaces.

        If specified, separators should be an (item_separator, key_separator)
        tuple.  The default is (', ', ': ') if *indent* is ``None`` and
        (',', ': ') otherwise.  To get the most compact JSON representation,
        you should specify (',', ':') to eliminate whitespace.

        If specified, default is a function that gets called for objects
        that can't otherwise be serialized.  It should return a JSON encodable
        version of the object or raise a ``TypeError``.

        If encoding is not None, then all input strings will be
        transformed into unicode using that encoding prior to JSON-encoding.
        The default is UTF-8.

        If use_decimal is true (default: ``True``), ``decimal.Decimal`` will
        be supported directly by the encoder. For the inverse, decode JSON
        with ``parse_float=decimal.Decimal``.

        If namedtuple_as_object is true (the default), objects with
        ``_asdict()`` methods will be encoded as JSON objects.

        If tuple_as_array is true (the default), tuple (and subclasses) will
        be encoded as JSON arrays.

        If *iterable_as_array* is true (default: ``False``),
        any object not in the above table that implements ``__iter__()``
        will be encoded as a JSON array.

        If bigint_as_string is true (not the default), ints 2**53 and higher
        or lower than -2**53 will be encoded as strings. This is to avoid the
        rounding that happens in Javascript otherwise.

        If int_as_string_bitcount is a positive number (n), then int of size
        greater than or equal to 2**n or lower than or equal to -2**n will be
        encoded as strings.

        If specified, item_sort_key is a callable used to sort the items in
        each dictionary. This is useful if you want to sort items other than
        in alphabetical order by key.

        If for_json is true (not the default), objects with a ``for_json()``
        method will use the return value of that method for encoding as JSON
        instead of the object.

        If *ignore_nan* is true (default: ``False``), then out of range
        :class:`float` values (``nan``, ``inf``, ``-inf``) will be serialized
        as ``null`` in compliance with the ECMA-262 specification. If true,
        this will override *allow_nan*.

        """
        self.skipkeys = skipkeys
        self.ensure_ascii = ensure_ascii
        self.check_circular = check_circular
        self.allow_nan = allow_nan
        self.sort_keys = sort_keys
        self.use_decimal = use_decimal
        self.namedtuple_as_object = namedtuple_as_object
        self.tuple_as_array = tuple_as_array
        self.iterable_as_array = iterable_as_array
        self.bigint_as_string = bigint_as_string
        self.item_sort_key = item_sort_key
        self.for_json = for_json
        self.ignore_nan = ignore_nan
        self.int_as_string_bitcount = int_as_string_bitcount
        if indent is not None:
            if not isinstance(indent, string_types):
                indent = indent * " "
        self.indent = indent
        if separators is not None:
            self.item_separator, self.key_separator = separators
        else:
            if indent is not None:
                self.item_separator = ","
        if default is not None:
            self.default = default
        self.encoding = encoding

    def default(self, o):
        """Implement this method in a subclass such that it returns
        a serializable object for ``o``, or calls the base implementation
        (to raise a ``TypeError``).

        For example, to support arbitrary iterators, you could
        implement default like this::

            def default(self, o):
                try:
                    iterable = iter(o)
                except TypeError:
                    pass
                else:
                    return list(iterable)
                return JSONEncoder.default(self, o)

        """
        raise TypeError("Object of type %s is not JSON serializable" % o.__class__.__name__)

    def encode(self, o):
        """Return a JSON string representation of a Python data structure.

        >>> from simplejson import JSONEncoder
        >>> JSONEncoder().encode({"foo": ["bar", "baz"]})
        '{"foo": ["bar", "baz"]}'

        """
        if isinstance(o, binary_type):
            _encoding = self.encoding
            if _encoding is not None:
                if not _encoding == "utf-8":
                    o = text_type(o, _encoding)
                if isinstance(o, string_types):
                    if self.ensure_ascii:
                        return encode_basestring_ascii(o)
            return encode_basestring(o)
        else:
            chunks = self.iterencode(o, _one_shot=True)
            if not isinstance(chunks, (list, tuple)):
                chunks = list(chunks)
            if self.ensure_ascii:
                return "".join(chunks)
            return "".join(chunks)

    def iterencode(self, o, _one_shot=False):
        """Encode the given object and yield each string
        representation as available.

        For example::

            for chunk in JSONEncoder().iterencode(bigobject):
                mysocket.write(chunk)

        """
        if self.check_circular:
            markers = {}
        else:
            markers = None
        if self.ensure_ascii:
            _encoder = encode_basestring_ascii
        else:
            _encoder = encode_basestring
        if self.encoding != "utf-8":
            if self.encoding is not None:

                def _encoder(o, _orig_encoder=_encoder, _encoding=self.encoding):
                    if isinstance(o, binary_type):
                        o = text_type(o, _encoding)
                    return _orig_encoder(o)

            def floatstr(o, allow_nan=self.allow_nan, ignore_nan=self.ignore_nan, _repr=FLOAT_REPR, _inf=PosInf, _neginf=-PosInf):
                if o != o:
                    text = "NaN"
                elif o == _inf:
                    text = "Infinity"
                elif o == _neginf:
                    text = "-Infinity"
                else:
                    if type(o) != float:
                        o = float(o)
                    return _repr(o)
                if ignore_nan:
                    text = "null"
                else:
                    if not allow_nan:
                        raise ValueError("Out of range float values are not JSON compliant: " + repr(o))
                return text

            key_memo = {}
            int_as_string_bitcount = 53 if self.bigint_as_string else self.int_as_string_bitcount
            if _one_shot and c_make_encoder is not None and self.indent is None:
                _iterencode = c_make_encoder(markers, self.default, _encoder, self.indent, self.key_separator, self.item_separator, self.sort_keys, self.skipkeys, self.allow_nan, key_memo, self.use_decimal, self.namedtuple_as_object, self.tuple_as_array, int_as_string_bitcount, self.item_sort_key, self.encoding, self.for_json, self.ignore_nan, decimal.Decimal, self.iterable_as_array)
        else:
            _iterencode = _make_iterencode(markers,
              (self.default), _encoder, (self.indent), floatstr, (self.key_separator),
              (self.item_separator), (self.sort_keys), (self.skipkeys),
              _one_shot, (self.use_decimal), (self.namedtuple_as_object),
              (self.tuple_as_array), int_as_string_bitcount,
              (self.item_sort_key),
              (self.encoding), (self.for_json), (self.iterable_as_array),
              Decimal=(decimal.Decimal))
        try:
            return _iterencode(o, 0)
        finally:
            key_memo.clear()


class JSONEncoderForHTML(JSONEncoder):
    __doc__ = "An encoder that produces JSON safe to embed in HTML.\n\n    To embed JSON content in, say, a script tag on a web page, the\n    characters &, < and > should be escaped. They cannot be escaped\n    with the usual entities (e.g. &amp;) because they are not expanded\n    within <script> tags.\n\n    This class also escapes the line separator and paragraph separator\n    characters U+2028 and U+2029, irrespective of the ensure_ascii setting,\n    as these characters are not valid in JavaScript strings (see\n    http://timelessrepo.com/json-isnt-a-javascript-subset).\n    "

    def encode(self, o):
        chunks = self.iterencode(o, True)
        if self.ensure_ascii:
            return "".join(chunks)
        else:
            return "".join(chunks)

    def iterencode(self, o, _one_shot=False):
        chunks = super(JSONEncoderForHTML, self).iterencode(o, _one_shot)
        for chunk in chunks:
            chunk = chunk.replace("&", "\\u0026")
            chunk = chunk.replace("<", "\\u003c")
            chunk = chunk.replace(">", "\\u003e")
            if not self.ensure_ascii:
                chunk = chunk.replace("\u2028", "\\u2028")
                chunk = chunk.replace("\u2029", "\\u2029")
            yield chunk


def _make_iterencode(markers, _default, _encoder, _indent, _floatstr, _key_separator, _item_separator, _sort_keys, _skipkeys, _one_shot, _use_decimal, _namedtuple_as_object, _tuple_as_array, _int_as_string_bitcount, _item_sort_key, _encoding, _for_json, _iterable_as_array, _PY3=PY3, ValueError=ValueError, string_types=string_types, Decimal=None, dict=dict, float=float, id=id, integer_types=integer_types, isinstance=isinstance, list=list, str=str, tuple=tuple, iter=iter):
    if _use_decimal:
        if Decimal is None:
            Decimal = decimal.Decimal
        else:
            if _item_sort_key:
                if not callable(_item_sort_key):
                    raise TypeError("item_sort_key must be None or callable")
            if _sort_keys:
                if not _item_sort_key:
                    _item_sort_key = itemgetter(0)
    else:
        if _int_as_string_bitcount is not None:
            if _int_as_string_bitcount <= 0 or not isinstance(_int_as_string_bitcount, integer_types):
                raise TypeError("int_as_string_bitcount must be a positive integer")

    def _encode_int(value):
        skip_quoting = _int_as_string_bitcount is None or _int_as_string_bitcount < 1
        if type(value) not in integer_types:
            value = int(value)
        if skip_quoting or -1 << _int_as_string_bitcount < value < 1 << _int_as_string_bitcount:
            return str(value)
        else:
            return '"' + str(value) + '"'

    def _iterencode_list(lst, _current_indent_level):
        if not lst:
            yield "[]"
            return
        else:
            if markers is not None:
                markerid = id(lst)
                if markerid in markers:
                    raise ValueError("Circular reference detected")
                markers[markerid] = lst
            buf = "["
            if _indent is not None:
                _current_indent_level += 1
                newline_indent = "\n" + _indent * _current_indent_level
                separator = _item_separator + newline_indent
                buf += newline_indent
            else:
                newline_indent = None
            separator = _item_separator
        first = True
        for value in lst:
            if first:
                first = False
            else:
                buf = separator
            if isinstance(value, string_types):
                yield buf + _encoder(value)
            elif _PY3:
                pass
            if isinstance(value, bytes) and _encoding is not None:
                yield buf + _encoder(value)
            elif isinstance(value, RawJSON):
                yield buf + value.encoded_json
            elif value is None:
                yield buf + "null"
            elif value is True:
                yield buf + "true"
            elif value is False:
                yield buf + "false"
            elif isinstance(value, integer_types):
                yield buf + _encode_int(value)
            elif isinstance(value, float):
                yield buf + _floatstr(value)
            elif _use_decimal and isinstance(value, Decimal):
                yield buf + str(value)
            else:
                yield buf
                for_json = _for_json and getattr(value, "for_json", None)
                if for_json:
                    if callable(for_json):
                        chunks = _iterencode(for_json(), _current_indent_level)
                    if isinstance(value, list):
                        chunks = _iterencode_list(value, _current_indent_level)
                else:
                    _asdict = _namedtuple_as_object and getattr(value, "_asdict", None)
                if _asdict:
                    if callable(_asdict):
                        chunks = _iterencode_dict(_asdict(), _current_indent_level)
                    elif _tuple_as_array:
                        if isinstance(value, tuple):
                            chunks = _iterencode_list(value, _current_indent_level)
                        if isinstance(value, dict):
                            chunks = _iterencode_dict(value, _current_indent_level)
                    else:
                        chunks = _iterencode(value, _current_indent_level)
                    for chunk in chunks:
                        yield chunk

        if first:
            yield "[]"
        else:
            if newline_indent is not None:
                _current_indent_level -= 1
                yield "\n" + _indent * _current_indent_level
            yield "]"
        if markers is not None:
            del markers[markerid]

    def _stringify_key(key):
        if isinstance(key, string_types):
            pass
        elif _PY3 and isinstance(key, bytes):
            if _encoding is not None:
                key = str(key, _encoding)
            if isinstance(key, float):
                key = _floatstr(key)
            elif key is True:
                key = "true"
            elif key is False:
                key = "false"
        elif key is None:
            key = "null"
        elif isinstance(key, integer_types):
            if type(key) not in integer_types:
                key = int(key)
            key = str(key)
        elif _use_decimal:
            if isinstance(key, Decimal):
                key = str(key)
            if _skipkeys:
                key = None
        else:
            raise TypeError("keys must be str, int, float, bool or None, not %s" % key.__class__.__name__)
        return key

    def _iterencode_dictParse error at or near `POP_JUMP_IF_TRUE' instruction at offset 260_262

    def _iterencode(o, _current_indent_level):
        if isinstance(o, string_types):
            yield _encoder(o)
        elif _PY3:
            if isinstance(o, bytes):
                if _encoding is not None:
                    yield _encoder(o)
                if isinstance(o, RawJSON):
                    yield o.encoded_json
                elif o is None:
                    yield "null"
                elif o is True:
                    yield "true"
                elif o is False:
                    yield "false"
                elif isinstance(o, integer_types):
                    yield _encode_int(o)
                elif isinstance(o, float):
                    yield _floatstr(o)
                else:
                    for_json = _for_json and getattr(o, "for_json", None)
                    if for_json:
                        if callable(for_json):
                            for chunk in _iterencode(for_json(), _current_indent_level):
                                yield chunk

                    if isinstance(o, list):
                        for chunk in _iterencode_list(o, _current_indent_level):
                            yield chunk

            else:
                _asdict = _namedtuple_as_object and getattr(o, "_asdict", None)
                if _asdict:
                    if callable(_asdict):
                        for chunk in _iterencode_dict(_asdict(), _current_indent_level):
                            yield chunk

                if _tuple_as_array:
                    if isinstance(o, tuple):
                        for chunk in _iterencode_list(o, _current_indent_level):
                            yield chunk

                if isinstance(o, dict):
                    for chunk in _iterencode_dict(o, _current_indent_level):
                        yield chunk

        elif _use_decimal and isinstance(o, Decimal):
            yield str(o)
        else:
            while _iterable_as_array:
                try:
                    o = iter(o)
                except TypeError:
                    break

                for chunk in _iterencode_list(o, _current_indent_level):
                    yield chunk

                return

            if markers is not None:
                markerid = id(o)
                if markerid in markers:
                    raise ValueError("Circular reference detected")
                markers[markerid] = o
            o = _default(o)
            for chunk in _iterencode(o, _current_indent_level):
                yield chunk

            if markers is not None:
                del markers[markerid]

    return _iterencode