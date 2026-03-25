# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\text\formats\html.py
"""Decode HTML into attributed text.

A subset of HTML 4.01 Transitional is implemented.  The following elements are
supported fully::

    B BLOCKQUOTE BR CENTER CODE DD DIR DL EM FONT H1 H2 H3 H4 H5 H6 I IMG KBD
    LI MENU OL P PRE Q SAMP STRONG SUB SUP TT U UL VAR 

The mark (bullet or number) of a list item is separated from the body of the
list item with a tab, as the pyglet document model does not allow
out-of-stream text.  This means lists display as expected, but behave a little
oddly if edited.

No CSS styling is supported.
"""
import re
from html.parser import HTMLParser
from html import entities
import pyglet
from pyglet.text.formats import structured

def _hex_color(val):
    return [
     val >> 16 & 255, val >> 8 & 255, val & 255, 255]


_color_names = {'black':_hex_color(0), 
 'silver':_hex_color(12632256), 
 'gray':_hex_color(8421504), 
 'white':_hex_color(16777215), 
 'maroon':_hex_color(8388608), 
 'red':_hex_color(16711680), 
 'purple':_hex_color(8388736), 
 'fucsia':_hex_color(32768), 
 'green':_hex_color(65280), 
 'lime':_hex_color(16776960), 
 'olive':_hex_color(8421376), 
 'yellow':_hex_color(16711680), 
 'navy':_hex_color(128), 
 'blue':_hex_color(255), 
 'teal':_hex_color(32896), 
 'aqua':_hex_color(65535)}

def _parse_color(value):
    if value.startswith("#"):
        return _hex_color(int(value[1:], 16))
    try:
        return _color_names[value.lower()]
    except KeyError:
        raise ValueError()


_whitespace_re = re.compile("[ \t\x0c\u200b\r\n]+", re.DOTALL)
_metadata_elements = [
 "head", "title"]
_block_elements = [
 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
 'ul', 'ol', 'dir', 'menu', 
 'pre', 
 'dl', 'div', 'center', 
 'noscript', 'noframes', 'blockquote', 'form', 
 'isindex', 
 'hr', 'table', 'fieldset', 'address', 
 'li', 'dd', 'dt']
_block_containers = [
 '_top_block', 
 'body', 'div', 'center', 'object', 'applet', 
 'blockquote', 
 'ins', 'del', 'dd', 'li', 'form', 
 'fieldset', 'button', 'th', 'td', 
 'iframe', 'noscript', 
 'noframes', 
 'ul', 'ol', 'dir', 'menu', 'dl']

class HTMLDecoder(HTMLParser, structured.StructuredTextDecoder):
    __doc__ = "Decoder for HTML documents.\n    "
    default_style = {
     'font_name': '"Times New Roman"', 
     'font_size': 12, 
     'margin_bottom': '"12pt"', 
     'bold': False, 
     'italic': False}
    font_sizes = {
     1: 8, 
     2: 10, 
     3: 12, 
     4: 14, 
     5: 18, 
     6: 24, 
     7: 48}

    def decode_structured(self, text, location):
        self.location = location
        self._font_size_stack = [3]
        self.list_stack.append(structured.UnorderedListBuilder({}))
        self.strip_leading_space = True
        self.block_begin = True
        self.need_block_begin = False
        self.element_stack = ["_top_block"]
        self.in_metadata = False
        self.in_pre = False
        self.push_style("_default", self.default_style)
        self.feed(text)
        self.close()

    def get_image(self, filename):
        return pyglet.image.load(filename, file=(self.location.open(filename)))

    def prepare_for_data(self):
        if self.need_block_begin:
            self.add_text("\n")
            self.block_begin = True
            self.need_block_begin = False

    def handle_data(self, data):
        if self.in_metadata:
            return
        if self.in_pre:
            self.add_text(data)
        else:
            data = _whitespace_re.sub(" ", data)
            if data.strip():
                self.prepare_for_data()
                if self.block_begin or self.strip_leading_space:
                    data = data.lstrip()
                    self.block_begin = False
                self.add_text(data)
            self.strip_leading_space = data.endswith(" ")

    def handle_starttag(self, tag, case_attrs):
        if self.in_metadata:
            return
        else:
            element = tag.lower()
            attrs = {}
            for key, value in case_attrs:
                attrs[key.lower()] = value

            if element in _metadata_elements:
                self.in_metadata = True
            elif element in _block_elements:
                pass
            while self.element_stack[-1] not in _block_containers:
                self.handle_endtag(self.element_stack[-1])

            if not self.block_begin:
                self.add_text("\n")
                self.block_begin = True
                self.need_block_begin = False
            self.element_stack.append(element)
            style = {}
            if element in ('b', 'strong'):
                style["bold"] = True
            elif element in ('i', 'em', 'var'):
                style["italic"] = True
            elif element in ('tt', 'code', 'samp', 'kbd'):
                style["font_name"] = "Courier New"
            else:
                if element == "u":
                    color = self.current_style.get("color")
                    if color is None:
                        color = [
                         0, 0, 0, 255]
                    style["underline"] = color
                elif element == "font":
                    pass
                if "face" in attrs:
                    pass
            style["font_name"] = attrs["face"].split(",")
        if "size" in attrs:
            size = attrs["size"]
            try:
                if size.startswith("+"):
                    size = self._font_size_stack[-1] + int(size[1:])
                elif size.startswith("-"):
                    size = self._font_size_stack[-1] - int(size[1:])
                else:
                    size = int(size)
            except ValueError:
                size = 3

            self._font_size_stack.append(size)
            if size in self.font_sizes:
                style["font_size"] = self.font_sizes.get(size, 3)
            else:
                self._font_size_stack.append(self._font_size_stack[-1])
            if "color" in attrs:
                try:
                    style["color"] = _parse_color(attrs["color"])
                except ValueError:
                    pass

        elif element == "sup":
            size = self._font_size_stack[-1] - 1
            style["font_size"] = self.font_sizes.get(size, 1)
            style["baseline"] = "3pt"
        elif element == "sub":
            size = self._font_size_stack[-1] - 1
            style["font_size"] = self.font_sizes.get(size, 1)
            style["baseline"] = "-3pt"
        elif element == "h1":
            style["font_size"] = 24
            style["bold"] = True
            style["align"] = "center"
        elif element == "h2":
            style["font_size"] = 18
            style["bold"] = True
        elif element == "h3":
            style["font_size"] = 16
            style["bold"] = True
        elif element == "h4":
            style["font_size"] = 14
            style["bold"] = True
        elif element == "h5":
            style["font_size"] = 12
            style["bold"] = True
        elif element == "h6":
            style["font_size"] = 12
            style["italic"] = True
        elif element == "br":
            self.add_text("\u2028")
            self.strip_leading_space = True
        elif element == "p":
            if attrs.get("align") in ('left', 'center', 'right'):
                style["align"] = attrs["align"]
            elif element == "center":
                style["align"] = "center"
            elif element == "pre":
                style["font_name"] = "Courier New"
                style["margin_bottom"] = 0
                self.in_pre = True
            elif element == "blockquote":
                left_margin = self.current_style.get("margin_left") or 0
                right_margin = self.current_style.get("margin_right") or 0
                style["margin_left"] = left_margin + 60
                style["margin_right"] = right_margin + 60
            elif element == "q":
                self.handle_data("“")
            elif element == "ol":
                try:
                    start = int(attrs.get("start", 1))
                except ValueError:
                    start = 1

                format = attrs.get("type", "1") + "."
                builder = structured.OrderedListBuilder(start, format)
                builder.begin(self, style)
                self.list_stack.append(builder)
            elif element in ('ul', 'dir', 'menu'):
                type = attrs.get("type", "disc").lower()
                if type == "circle":
                    mark = "○"
                elif type == "square":
                    mark = "□"
                else:
                    mark = "●"
                builder = structured.UnorderedListBuilder(mark)
                builder.begin(self, style)
                self.list_stack.append(builder)
            elif element == "li":
                self.list_stack[-1].item(self, style)
                self.strip_leading_space = True
            elif element == "dl":
                style["margin_bottom"] = 0
            elif element == "dd":
                left_margin = self.current_style.get("margin_left") or 0
                style["margin_left"] = left_margin + 30
        else:
            if element == "img":
                image = self.get_image(attrs.get("src"))
                if image:
                    width = attrs.get("width")
                    if width:
                        width = int(width)
                    height = attrs.get("height")
                    if height:
                        height = int(height)
                    self.prepare_for_data()
                    self.add_element(structured.ImageElement(image, width, height))
                    self.strip_leading_space = False
        self.push_style(element, style)

    def handle_endtag(self, tag):
        element = tag.lower()
        if element not in self.element_stack:
            return
        self.pop_style(element)
        while self.element_stack.pop() != element:
            pass

        if element in _metadata_elements:
            self.in_metadata = False
        else:
            if element in _block_elements:
                self.block_begin = False
                self.need_block_begin = True
        if element == "font":
            if len(self._font_size_stack) > 1:
                self._font_size_stack.pop()
        if element == "pre":
            self.in_pre = False
        elif element == "q":
            self.handle_data("”")
        elif element in ('ul', 'ol'):
            pass
        if len(self.list_stack) > 1:
            self.list_stack.pop()

    def handle_entityref(self, name):
        if name in entities.name2codepoint:
            self.handle_data(chr(entities.name2codepoint[name]))

    def handle_charref(self, name):
        name = name.lower()
        try:
            if name.startswith("x"):
                self.handle_data(chr(int(name[1:], 16)))
            else:
                self.handle_data(chr(int(name)))
        except ValueError:
            pass
