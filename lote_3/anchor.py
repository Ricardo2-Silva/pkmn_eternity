# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\utils\anchor.py
"""
Created on 2 juil. 2011

@author: Kami
"""
from client.data.utils.anchor import AnchorType
from client.data.gui.padding import PaddingData
noPadding = PaddingData(0, 0, 0, 0)

def getAnchorOffsets(parent, child, anchor, padding=noPadding):
    offx = 0
    offy = 0
    if anchor & AnchorType.CENTERX or anchor & AnchorType._CENTERX_FIXED:
        offx = (parent.width - child.width) / 2 - padding.left
    if anchor & AnchorType.CENTERY or anchor & AnchorType._CENTERY_FIXED:
        offy = (parent.height - child.height) / 2 - padding.top
    if anchor & AnchorType.LEFT or anchor & AnchorType._LEFT_FIXED:
        offx = 0
    if anchor & AnchorType.TOP or anchor & AnchorType._TOP_FIXED:
        offy = 0
    if anchor & AnchorType.RIGHT or anchor & AnchorType._RIGHT_FIXED:
        offx = parent.width - child.width - padding.right - padding.left
    if anchor & AnchorType.BOTTOM or anchor & AnchorType._BOTTOM_FIXED:
        offy = parent.height - child.height - padding.bottom - padding.top
    return (int(offx), int(offy))


def getAnchorOffsetsWidgetToSprite(parent, child, anchor, padding=noPadding):
    """ Only to be used for widget -> sprite calls such as TextRender """
    offx = 0
    offy = 0
    if anchor & AnchorType.CENTERX or anchor & AnchorType._CENTERX_FIXED:
        offx = (parent.width - child.getWidth()) / 2 - padding.left
    if anchor & AnchorType.CENTERY or anchor & AnchorType._CENTERY_FIXED:
        offy = (parent.height - child.getHeight()) / 2 - padding.top
    if anchor & AnchorType.LEFT or anchor & AnchorType._LEFT_FIXED:
        offx = 0
    if anchor & AnchorType.TOP or anchor & AnchorType._TOP_FIXED:
        offy = 0
    if anchor & AnchorType.RIGHT or anchor & AnchorType._RIGHT_FIXED:
        offx = parent.width - child.getWidth() - padding.right - padding.left
    if anchor & AnchorType.BOTTOM or anchor & AnchorType._BOTTOM_FIXED:
        offy = parent.height - child.getHeight() - padding.bottom - padding.top
    return (int(offx), int(offy))
