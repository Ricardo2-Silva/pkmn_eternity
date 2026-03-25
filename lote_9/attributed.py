# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\text\formats\attributed.py
"""Extensible attributed text format for representing pyglet formatted
documents.
"""
import re, ast, pyglet
_pattern = re.compile("\n    (?P<escape_hex>\\{\\#x(?P<escape_hex_val>[0-9a-fA-F]+)\\})\n  | (?P<escape_dec>\\{\\#(?P<escape_dec_val>[0-9]+)\\})\n  | (?P<escape_lbrace>\\{\\{)\n  | (?P<escape_rbrace>\\}\\})\n  | (?P<attr>\\{\n        (?P<attr_name>[^ \\{\\}]+)\\s+\n        (?P<attr_val>[^\\}]+)\\})\n  | (?P<nl_hard1>\\n(?=[ \\t]))\n  | (?P<nl_hard2>\\{\\}\\n)\n  | (?P<nl_soft>\\n(?=\\S))\n  | (?P<nl_para>\\n\\n+)\n  | (?P<text>[^\\{\\}\\n]+)\n    ", re.VERBOSE | re.DOTALL)

class AttributedTextDecoder(pyglet.text.DocumentDecoder):

    def __init__(self):
        self.doc = pyglet.text.document.FormattedDocument()
        self.length = 0
        self.attributes = {}

    def decode(self, text, location=None):
        next_trailing_space = True
        trailing_newline = True
        for m in _pattern.finditer(text):
            group = m.lastgroup
            trailing_space = True
            if group == "text":
                t = m.group("text")
                self.append(t)
                trailing_space = t.endswith(" ")
                trailing_newline = False
            elif group == "nl_soft":
                if not next_trailing_space:
                    self.append(" ")
                trailing_newline = False
            elif group in ('nl_hard1', 'nl_hard2'):
                self.append("\n")
                trailing_newline = True
            elif group == "nl_para":
                self.append(m.group("nl_para")[1:])
                trailing_newline = True
            elif group == "attr":
                value = ast.literal_eval(m.group("attr_val"))
                name = m.group("attr_name")
                if name[0] == ".":
                    if trailing_newline:
                        self.attributes[name[1:]] = value
                    else:
                        self.doc.set_paragraph_style(self.length, self.length, {(name[1:]): value})
                else:
                    self.attributes[name] = value
            elif group == "escape_dec":
                self.append(chr(int(m.group("escape_dec_val"))))
            elif group == "escape_hex":
                self.append(chr(int(m.group("escape_hex_val"), 16)))
            elif group == "escape_lbrace":
                self.append("{")
            else:
                if group == "escape_rbrace":
                    self.append("}")
            next_trailing_space = trailing_space

        return self.doc

    def append(self, text):
        self.doc.insert_text(self.length, text, self.attributes)
        self.length += len(text)
        self.attributes.clear()
