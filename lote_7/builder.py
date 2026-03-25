# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: lxml\html\builder.py
"""
A set of HTML generator tags for building HTML documents.

Usage::

    >>> from lxml.html.builder import *
    >>> html = HTML(
    ...            HEAD( TITLE("Hello World") ),
    ...            BODY( CLASS("main"),
    ...                  H1("Hello World !")
    ...            )
    ...        )

    >>> import lxml.etree
    >>> print lxml.etree.tostring(html, pretty_print=True)
    <html>
      <head>
        <title>Hello World</title>
      </head>
      <body class="main">
        <h1>Hello World !</h1>
      </body>
    </html>

"""
from lxml.builder import ElementMaker
from lxml.html import html_parser
E = ElementMaker(makeelement=(html_parser.makeelement))
A = E.a
ABBR = E.abbr
ACRONYM = E.acronym
ADDRESS = E.address
APPLET = E.applet
AREA = E.area
B = E.b
BASE = E.base
BASEFONT = E.basefont
BDO = E.bdo
BIG = E.big
BLOCKQUOTE = E.blockquote
BODY = E.body
BR = E.br
BUTTON = E.button
CAPTION = E.caption
CENTER = E.center
CITE = E.cite
CODE = E.code
COL = E.col
COLGROUP = E.colgroup
DD = E.dd
DEL = getattr(E, "del")
DFN = E.dfn
DIR = E.dir
DIV = E.div
DL = E.dl
DT = E.dt
EM = E.em
FIELDSET = E.fieldset
FONT = E.font
FORM = E.form
FRAME = E.frame
FRAMESET = E.frameset
H1 = E.h1
H2 = E.h2
H3 = E.h3
H4 = E.h4
H5 = E.h5
H6 = E.h6
HEAD = E.head
HR = E.hr
HTML = E.html
I = E.i
IFRAME = E.iframe
IMG = E.img
INPUT = E.input
INS = E.ins
ISINDEX = E.isindex
KBD = E.kbd
LABEL = E.label
LEGEND = E.legend
LI = E.li
LINK = E.link
MAP = E.map
MENU = E.menu
META = E.meta
NOFRAMES = E.noframes
NOSCRIPT = E.noscript
OBJECT = E.object
OL = E.ol
OPTGROUP = E.optgroup
OPTION = E.option
P = E.p
PARAM = E.param
PRE = E.pre
Q = E.q
S = E.s
SAMP = E.samp
SCRIPT = E.script
SELECT = E.select
SMALL = E.small
SPAN = E.span
STRIKE = E.strike
STRONG = E.strong
STYLE = E.style
SUB = E.sub
SUP = E.sup
TABLE = E.table
TBODY = E.tbody
TD = E.td
TEXTAREA = E.textarea
TFOOT = E.tfoot
TH = E.th
THEAD = E.thead
TITLE = E.title
TR = E.tr
TT = E.tt
U = E.u
UL = E.ul
VAR = E.var
ATTR = dict

def CLASS(v):
    return {"class": v}


def FOR(v):
    return {"for": v}
