# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\render\gui\picture.py
import client.render.cache as cache
from client.render.gui.core import AbstractRender
from client.render.sprite import GUIPygletSprite, GUIPygletSheet
from client.data import exceptions
from client.data.sprite import Sheet
from client.control.world.animation import animationManager
from twisted.internet import reactor
import pyglet

class PictureRender(AbstractRender):

    def initiate(self):
        self.pictureSprite = None
        if self.widget.picture:
            self.sprites.append(self._createPictureSprite())

    def destroy(self):
        return

    def createAndAdd(self):
        self.sprites.append(self._createPictureSprite())
        self._checkVisibility()

    def _createPictureSprite(self):
        if isinstance(self.widget.picture, str):
            self.pictureSprite = GUIPygletSprite((cache.textureCache.getImageFile(self.widget.picture)), z=(self.order + 1),
              group=(self.widget.group),
              batch=(self.widget.batch),
              subpixel=True)
        else:
            try:
                self.pictureSprite = GUIPygletSprite((self.widget.picture), z=(self.order + 1),
                  group=(self.widget.group),
                  batch=(self.widget.batch),
                  subpixel=True)
            except IOError:
                raise Exception(f"This picture instance is not supported: {self.widget.picture}")

        return self.pictureSprite

    def refreshPicture(self):
        if self.widget.picture:
            if isinstance(self.widget.picture, str):
                self.pictureSprite.image = cache.textureCache.getImageFile(self.widget.picture)
            else:
                try:
                    self.pictureSprite.image = self.widget.picture
                except Exception as err:
                    raise Exception(f"This picture instance is not supported: {self.widget.picture}", err)

            if not self.sprites:
                self.sprites = [
                 self.pictureSprite]
                self.visible = True
            self._checkVisibility()

    def getSize(self):
        if self.widget.picture:
            return self.pictureSprite.getSize()
        else:
            return (0, 0)

    def _updatePicturePosition(self):
        if self.widget.picture:
            (self.pictureSprite.setPosition)(*self.widget.position)

    def _updatePictureSize(self):
        if self.widget.picture:
            (self.pictureSprite.setSize)(*self.widget.size)

    def updatePosition(self):
        self._updatePicturePosition()

    def removePicture(self):
        self.visible = False
        self.sprites = []

    def updateSize(self):
        self._updatePictureSize()
        self.updatePosition()


class AnimatedPictureRender(PictureRender):

    def _createPictureSprite(self):
        self.stopOnFrame = None
        self.currentFrame = 0
        picture = self.widget.picture
        if not isinstance(picture, Sheet):
            raise Exception(f"This picture instance is not supported: {self.widget.picture}")
        self.pictureSprite = GUIPygletSheet((self.widget.picture), z=(self.order + 1),
          group=(self.widget.group),
          batch=(self.widget.batch))
        if self.widget.autosize[0] is False:
            self.pictureSprite.customSize = True
        self.sprites = [self.pictureSprite]

    def _updatePicturePosition(self):
        if self.widget.picture:
            (self.pictureSprite.setPosition)(*self.widget.position)

    def setFrame(self, frameNum):
        self.pictureSprite.setFrame(frameNum)

    def animate(self, dt):
        self.pictureSprite.nextFrame()
        if self.stopOnFrame is not None:
            if self.pictureSprite.currentFrame == self.stopOnFrame:
                pyglet.clock.unschedule(self.animate)
                return

    def runAnimation(self, duration, stopOnFrame=None):
        self.stopOnFrame = stopOnFrame
        pyglet.clock.unschedule(self.animate)
        pyglet.clock.schedule_interval(self.animate, self.widget.picture.getAnimationDelay())

    def playAnimation(self):
        self.stopOnFrame = 0
        pyglet.clock.unschedule(self.animate)
        pyglet.clock.schedule_interval(self.animate, self.widget.picture.getAnimationDelay())

    def loopAnimation(self):
        pyglet.clock.unschedule(self.animate)
        pyglet.clock.schedule_interval(self.animate, self.widget.picture.getAnimationDelay())

    def stopAnimation(self):
        pyglet.clock.unschedule(self.animate)

    def refreshPicture(self):
        if self.widget.picture:
            if isinstance(self.widget.picture, str):
                self.pictureSprite.image = cache.textureCache.getImageFile(self.widget.picture)
            elif hasattr(self.widget.picture, "frames"):
                self.pictureSprite.setSheet(self.widget.picture)
            else:
                try:
                    self.pictureSprite.image = self.widget.picture
                except Exception as err:
                    raise Exception(f"This picture instance is not supported: {self.widget.picture}", err)

            if not self.sprites:
                self.sprites = [
                 self.pictureSprite]
                self.visible = True
            self._checkVisibility()
