# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\gui\picture.py
from client.control.gui.widget import StylizedWidget
from client.data.gui import styleDB
import client.render.gui as iCoreRender
from shared.container.constants import RefPointType

class Picture(StylizedWidget):
    renderClass = iCoreRender.PictureRender
    maxDepth = 2

    def __init__(self, parent, picture=None, style=styleDB.defaultPictureStyle, position=(0, 0), size=(0, 0), draggable=False, visible=True, enableEvents=False, autosize=(True, True), refPointType=RefPointType.TOPLEFT):
        if size[0] != 0:
            autosize = (False, True)
        if size[1] != 0:
            autosize = (
             autosize[0], False)
        self.picture = picture
        self.autosize = autosize
        self.referencePoint = refPointType
        StylizedWidget.__init__(self, style, parent, position, size, draggable, visible, enableEvents)

    def setSize(self, width, height):
        rwidth, rheight = self.renderer.getSize()
        if self.autosize[0] == True:
            width = rwidth
        if self.autosize[1] == True:
            height = rheight
        StylizedWidget.setSize(self, width, height)

    def setPicture(self, picture):
        if picture:
            if not self.renderer.pictureSprite:
                self.picture = picture
                self.renderer.createAndAdd()
                self.updatePosition()
                return
            self.picture = picture
            self.renderer.refreshPicture()
            (self.setSize)(*self.size)
        else:
            self.picture = None
            self.renderer.removePicture()

    def removePicture(self):
        self.setPicture(None)


class AnimatedPicture(Picture):
    renderClass = iCoreRender.AnimatedPictureRender

    def __init__(self, *args, **kwargs):
        (Picture.__init__)(self, *args, **kwargs)

    def hide(self):
        self.renderer.stopAnimation()
        Picture.hide(self)

    def destroy(self):
        self.renderer.stopAnimation()
        Picture.destroy(self)

    def runAnimation(self, duration, stopOnFrame=0):
        self.renderer.runAnimation(duration, stopOnFrame)

    def loopAnimation(self):
        self.renderer.loopAnimation()

    def playAnimation(self):
        """Simple function for one playthrough."""
        self.renderer.playAnimation()

    def stopAnimation(self):
        self.renderer.stopAnimation()

    def setFrame(self, frame):
        self.renderer.setFrame(frame)


class PictureScissor(Picture):
    renderClass = iCoreRender.AnimatedPictureRender
