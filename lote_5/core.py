# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\render\gui\core.py
from client.render.utils.patch import PatchType, NinePatch, ThreePatch, NinePatchImage, NinePatchLine
from client.data.utils.color import Color
import client.render.sprite as iSprite, client.render.cache as cache
from client.data.gui.style import BorderType
import client.data.exceptions as exceptions, rabbyt, pyglet
from client.scene.manager import sceneManager
from client.data.gui.padding import PaddingData
from client.control.system.anims import AnimableRender

class WidgetRender(object):

    def __init__(self, widget):
        self.widget = widget


class ContainerRender(WidgetRender):
    __doc__ = " Render method for containers "

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, visibility):
        self._visible = visibility
        for child in self.widget.visibleWidgets:
            child.renderer.visible = visibility

    def destroy(self):
        return

    def delete(self):
        for child in self.widget.widgets:
            child.delete()


class AbstractRender(AnimableRender):

    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self.sprites = []
        self._visible = True
        self.duration = 0
        self.initiate()
        self._checkVisibility()

    def _startTransparency(self):
        """ When a sprite's alpha becomes 0 - 1 it needs to be rendered last- """
        AnimableRender._startTransparency(self)
        for sprite in self.sprites:
            sprite.batch = self.widget.transparentBatch

    def _endTransparency(self):
        """ Restore a sprite to it's original opaque layer """
        AnimableRender._endTransparency(self)
        for sprite in self.sprites:
            sprite.batch = self.widget.desktop.batch

    @property
    def initialOrder(self):
        return self.order + len(self.sprites)

    def _checkVisibility(self):
        """ A widget may be hidden on creation or it's parent is, on creation."""
        if self.widget.getVisibleState() is False:
            self.visible = False

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, visibility):
        self._visible = visibility
        for sprite in self.sprites:
            sprite.visible = visibility

    @property
    def batch(self):
        return self.widget.batch

    @batch.setter
    def batch(self, value):
        for sprite in self.sprites:
            sprite.batch = value

    @property
    def group(self):
        return self.widget.group

    @group.setter
    def group(self, group):
        for sprite in self.sprites:
            sprite.group = group

    @property
    def order(self):
        return self.widget.order

    @order.setter
    def order(self, value):
        for sprite in self.sprites:
            sprite.z = value + self.sprites.index(sprite)

    def delete(self):
        """ Permanently removes sprites """
        self.stopAnims()
        for sprite in self.sprites:
            sprite.delete()

        self.sprites.clear()

    def updateSize(self):
        raise exceptions.MustBeImplemented()

    def updatePosition(self):
        raise exceptions.MustBeImplemented()

    def getSize(self):
        raise exceptions.MustBeImplemented()

    def refresh(self):
        raise exceptions.MustBeImplemented()

    def setColor(self, r, g, b):
        for sprite in self.sprites:
            sprite.setColor(r, g, b)

    def setAlpha(self, alpha):
        for sprite in self.sprites:
            sprite.setAlpha(alpha)

    def _addSprites(self, *sprites):
        """ Add the sprites in the sprite list. """
        self.sprites.extend(sprites)


class BasicRender(AbstractRender):
    spriteClass = iSprite.GUIPygletSprite

    def setParentLink(self, gameObject, offsetX=0, offsetY=0):
        for sprite in self.sprites:
            sprite.setParentLink(gameObject, offsetX, offsetY)

    def destroy(self):
        return

    def resetRenderState(self):
        for sprite in self.sprites:
            sprite.resetRenderState()

    def updateSize(self):
        """ update the size of the sprites """
        Style = self.widget.getStyle()
        self._updateBackgroundSize(Style.background)
        self._updateBorderSize(Style.border)
        self.updatePosition()

    def _updateBackgroundSize(self, backgroundData):
        if backgroundData:
            if backgroundData.color is not None:
                (self.backgroundSprite.setSize)(*self.widget.size)
            if backgroundData.image:
                if backgroundData.patchType == PatchType.THREE:
                    (self.backgroundSprite.setSize)(*self.widget.size)
                    return
                if backgroundData.patchType == PatchType.THREE_VERT:
                    (self.backgroundSprite.setSize)(*self.widget.size)
                    return
                if backgroundData.patchType == PatchType.NINE:
                    (self.backgroundSprite.setSize)(*self.widget.size)
            elif backgroundData.patchType == PatchType.FOUR_IMAGE:
                self.backgroundSprite.setSize(backgroundData.image.width, backgroundData.image.height)

    def _updateBorderSize(self, borderData):
        if borderData:
            if borderData.type == BorderType.LINE:
                (self.borderSprite.setSize)(*self.widget.size)
            if borderData.type == BorderType.IMAGE:
                padding = borderData.padding
                (self.borderSprite.setSize)(*self.widget.size)
                return

    def updatePosition(self):
        """ update the position of the sprites """
        Style = self.widget.getStyle()
        self._updateBackgroundPosition(Style.background)
        self._updateBorderPosition(Style.border)

    def setRenderPosition(self, interp):
        """ update the position of the sprites """
        Style = self.widget.getStyle()
        self._updateBackgroundRenderPosition(Style.background, interp)
        self._updateBorderRenderPosition(Style.border, interp)

    def refresh(self):
        """ refresh the entire sprite """
        Style = self.widget.getStyle()
        self._refreshBackgroundSprites(Style.background)
        self.updatePosition()

    def _updateBorderPosition(self, borderData):
        if borderData:
            if borderData.type == BorderType.LINE:
                (self.borderSprite.setPosition)(*self.widget.position)
            if borderData.type == BorderType.IMAGE:
                (self.borderSprite.setPosition)(*self.widget.position)

    def _updateBorderRenderPosition(self, borderData, interp):
        if borderData:
            if borderData.type == BorderType.LINE:
                (self.borderSprite.setPositionInterpolate)(*self.widget.position, *(interp,))
            if borderData.type == BorderType.IMAGE:
                (self.borderSprite.setPositionInterpolate)(*self.widget.position, *(interp,))

    def refreshBackground(self):
        backgroundData = self.widget.getStyle().background
        self._refreshBackgroundSprites(backgroundData)
        self._updateBackgroundSize(backgroundData)

    def updateBackgroundPosition(self):
        self._updateBackgroundPosition(self.widget.getStyle().background)

    def setBackgroundColor(self, r, g, b):
        self.backgroundSprite.setColor(r, g, b)

    def createBackgroundAndAdd(self):
        style = self.widget.getStyle()
        self.sprites.insert(0, self._createBackgroundSprites(style.background))
        self._checkVisibility()

    def _createBackgroundSprites(self, backgroundData):
        """

        :param backgroundData:
        """
        if backgroundData:
            if backgroundData.color is not None:
                self.backgroundSprite = self.spriteClass((cache.textureCache.getBackgroundColor(backgroundData.color)), z=(self.initialOrder),
                  group=(self.widget.group),
                  batch=(self.widget.batch))
                if backgroundData.alpha is not 255:
                    self.backgroundSprite.setAlpha(backgroundData.alpha)
        else:
            if backgroundData.image:
                if backgroundData.patchType in (PatchType.NOPATCH, PatchType.FOUR_IMAGE):
                    self.backgroundSprite = self.spriteClass((backgroundData.image), z=(self.initialOrder),
                      group=(self.widget.group),
                      batch=(self.widget.batch))
            elif backgroundData.patchType in (PatchType.THREE, PatchType.THREE_VERT, PatchType.NINE):
                try:
                    ninepatch = backgroundData.image.patch
                except AttributeError:
                    ninepatch = backgroundData.image

                self.backgroundSprite = iSprite.PatchSprite(ninepatch, padding=(PaddingData(0, 0, 0, 0)),
                  x=(self.widget.x),
                  y=(self.widget.y),
                  z=(self.initialOrder),
                  width=(self.widget.width),
                  height=(self.widget.height),
                  batch=(self.widget.batch),
                  group=(self.widget.group))
            else:
                self.backgroundSprite = self.spriteClass((cache.textureCache.getBackgroundColor(Color.TRANSPARENT)), z=(self.initialOrder),
                  group=(self.widget.group),
                  batch=(self.widget.batch))
            return self.backgroundSprite

    def _refreshBackgroundSprites(self, backgroundData):
        if backgroundData:
            if backgroundData.color is not None:
                self.backgroundSprite.image = cache.textureCache.getBackgroundColor(backgroundData.color)
                if backgroundData.alpha is not self.backgroundSprite.opacity:
                    self.backgroundSprite.setAlpha(backgroundData.alpha)
                if backgroundData.image:
                    if backgroundData.patchType in (PatchType.NOPATCH, PatchType.FOUR_IMAGE):
                        self.backgroundSprite.image = backgroundData.image
            elif backgroundData.patchType == PatchType.THREE:
                self.backgroundSprite.image = backgroundData.image.texture

    def _updateBackgroundPosition(self, backgroundData):
        if backgroundData:
            (self.backgroundSprite.setPosition)(*self.widget.position)

    def _updateBackgroundRenderPosition(self, backgroundData, interp):
        if backgroundData:
            (self.backgroundSprite.setPositionInterpolate)(*self.widget.position, *(interp,))

    def _createBorderSprites(self, borderData):
        if borderData:
            if borderData.type == BorderType.LINE:
                self.borderSprite = iSprite.LineBorderSprite(x=(self.widget.x), y=(self.widget.y),
                  z=(self.initialOrder),
                  width=(self.widget.width),
                  height=(self.widget.height),
                  batch=(self.widget.batch),
                  group=(self.widget.group),
                  color=(borderData.color + (borderData.alpha,)),
                  left=(borderData.left),
                  top=(borderData.top),
                  right=(borderData.right),
                  bottom=(borderData.bottom))
            if borderData.type == BorderType.IMAGE:
                ninepatch = borderData.images
                self.borderSprite = iSprite.PatchSprite(ninepatch, padding=(borderData.padding),
                  x=(self.widget.x),
                  y=(self.widget.y),
                  z=(self.initialOrder),
                  width=(self.widget.width),
                  height=(self.widget.height),
                  batch=(self.widget.batch),
                  group=(self.widget.group))
        return self.borderSprite

    def initiate(self):
        """ initiate the render """
        style = self.widget.getStyle()
        if style.background:
            self.sprites.append(self._createBackgroundSprites(style.background))
        if style.border:
            self.sprites.append(self._createBorderSprites(style.border))

    def getSize(self):
        """ Return the size of the render (border is ignored) """
        Style = self.widget.getStyle()
        background = Style.background
        width = 0
        height = 0
        if background:
            if background.image:
                if background.patchType == PatchType.THREE:
                    height = self.backgroundSprite.texture.height
                    width = self.backgroundSprite.texture.width
                elif background.patchType == PatchType.NINE:
                    height = self.backgroundSprite.texture.height
                    width = self.backgroundSprite.texture.width
            elif background.patchType == PatchType.NOPATCH:
                height = background.image.height
                width = background.image.width
        return (width, height)


class StylizedContainerRender(BasicRender, ContainerRender):

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, visibility):
        for sprite in self.sprites:
            sprite.visible = visibility

        for child in self.widget.visibleWidgets:
            child.renderer.visible = visibility

    @property
    def order(self):
        return self.widget.order

    @order.setter
    def order(self, value):
        for sprite in self.sprites:
            sprite.z = value + self.sprites.index(sprite)
