# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: simplejson\errors.py
"""Error classes used by simplejson
"""
__all__ = [
 "JSONDecodeError"]

def linecol(doc, pos):
    lineno = doc.count("\n", 0, pos) + 1
    if lineno == 1:
        colno = pos + 1
    else:
        colno = pos - doc.rindex("\n", 0, pos)
    return (
     lineno, colno)


def errmsg(msg, doc, pos, end=None):
    lineno, colno = linecol(doc, pos)
    msg = msg.replace("%r", repr(doc[pos:pos + 1]))
    if end is None:
        fmt = "%s: line %d column %d (char %d)"
        return fmt % (msg, lineno, colno, pos)
    else:
        endlineno, endcolno = linecol(doc, end)
        fmt = "%s: line %d column %d - line %d column %d (char %d - %d)"
        return fmt % (msg, lineno, colno, endlineno, endcolno, pos, end)


class JSONDecodeError(ValueError):
    __doc__ = "Subclass of ValueError with the following additional properties:\n\n    msg: The unformatted error message\n    doc: The JSON document being parsed\n    pos: The start index of doc where parsing failed\n    end: The end index of doc where parsing failed (may be None)\n    lineno: The line corresponding to pos\n    colno: The column corresponding to pos\n    endlineno: The line corresponding to end (may be None)\n    endcolno: The column corresponding to end (may be None)\n\n    "

    def __init__(self, msg, doc, pos, end=None):
        ValueError.__init__(self, errmsg(msg, doc, pos, end=end))
        self.msg = msg
        self.doc = doc
        self.pos = pos
        self.end = end
        self.lineno, self.colno = linecol(doc, pos)
        if end is not None:
            self.endlineno, self.endcolno = linecol(doc, end)
        else:
            self.endlineno, self.endcolno = (None, None)

    def __reduce__(self):
        return (self.__class__, (self.msg, self.doc, self.pos, self.end))
