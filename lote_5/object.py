# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\render\world\object.py
"""
Created on 22 juil. 2011

@author: Kami
"""
import client.data.exceptions as exceptions
from client.render.layer import worldLayer
import client.render.sprite as iSprite
from client.data.layer import LayerType
import pyglet
from shared.container.constants import RefPointType
from twisted.internet import defer, reactor
from client.control.system.anims import AnimableRender
from client.render.shader.default_sprite import white_sprite_shader, default_sprite_shader

class SimpleRender(AnimableRender):

    def __init__(self, ready=True):
        super().__init__()
        self.ready = ready
        self.fading = False
        self.visible = True
        self.dead = False
        self._transparent = False
        self.sprites = []

    def hide(self, dt=None):
        """ Hiding removes it from the layer """
        if not self.visible:
            raise Exception("Trying to hide already hidden object render.", self, self.object)
        self.visible = False
        self.fading = False
        pyglet.clock.unschedule(self.hide)
        if self.ready:
            self.delSprites()
            self.stopAnims()

    def show(self):
        """ Unhiding puts it back into the layer it is in """
        if self.visible:
            raise Exception("Trying to set to visible already visible object render.", self, self.object)
        self.visible = True
        self.fading = False
        pyglet.clock.unschedule(self.show)
        if self.ready:
            self.addSprites()

    def delete(self):
        """
           This will permanently remove the sprite and cannot be used again.
           Be 100% certain you will never use them or will produce errors.
        """
        self.dead = True
        self.visible = False
        self.stopAnims()
        for sprite in self.sprites:
            sprite.delete()

    def _startTransparency(self):
        """ When a sprite's alpha becomes 0 - 1 it needs to be rendered last- """
        AnimableRender._startTransparency(self)
        for sprite in self.sprites:
            sprite.batch = worldLayer.transparentBatch

    def _endTransparency(self):
        """ Restore a sprite to it's original opaque layer """
        AnimableRender._endTransparency(self)
        for sprite in self.sprites:
            sprite.batch = worldLayer.dynamicBatch

    def resetColor(self):
        for sprite in self.sprites:
            sprite.setColor(255, 255, 255)

    def enableWhite(self):
        self.setShader(white_sprite_shader)

    def disableWhite(self):
        self.setShader(default_sprite_shader)

    def setColor(self, r, g, b):
        for sprite in self.sprites:
            sprite.setColor(r, g, b)

    def setAlpha(self, alpha):
        for sprite in self.sprites:
            sprite.setAlpha(alpha)

    def setScale(self, scaleVal):
        for sprite in self.sprites:
            sprite.scale = scaleVal

    def setScales(self, scaleX, scaleY):
        for sprite in self.sprites:
            sprite.update(scale_x=scaleX, scale_y=scaleY)

    def setShader(self, program):
        for sprite in self.sprites:
            sprite.shader_program = program

    def _create(self):
        """ Create all sprites for this object. """
        raise NotImplementedError

    def _updateSize(self):
        """ Update the size of all sprites for this object. """
        for sprite in self.sprites:
            (sprite.setSize)(*self.object.getSize())

    def _updatePosition(self):
        x, y, z = self.object.getPosition()
        for sprite in self.sprites:
            sprite.setPosition(x, y, z)

    def updatePosition(self):
        """ Update position from outside."""
        self._updatePosition()

    def updateSize(self):
        """ Update position from outside."""
        self._updateSize()

    def getSize(self):
        """ returns the size of the render. """
        raise NotImplementedError

    def _addSprites(self, *sprites):
        """ Add the sprite to the layer. """
        raise NotImplementedError

    def _delSprites(self, *sprites):
        """ Delete the sprite from the layer. """
        raise NotImplementedError


class SheetRender(SimpleRender):
    __doc__ = " Abstract Render for sheets. "

    def __init__(self, ready=True):
        self._currentFrame = 0
        self._animationStep = 0
        SimpleRender.__init__(self, ready)

    def setFrame(self, col, row=0):
        """ From outside. """
        for sprite in self.sprites:
            sprite.setFrame(col, row)

    def animate(self, dt=None):
        """ Animate the sprite. """
        for sprite in self.sprites:
            sprite.nextFrame()


class WorldObjectRender(SheetRender):
    __doc__ = " Abstract Render for an object "

    def __init__(self, gameObject, ready=True):
        """ Save the object which is gonna be rendered. """
        SheetRender.__init__(self, ready)
        self.object = gameObject
        self.layerType = gameObject.data.layerType
        self._animating = False
        assert self.layerType in LayerType.ALL_LAYERS, "Wrong Layer Type: {0}".format(self.layerType)
        if self.ready:
            self._initiate()

    @property
    def renderingOrder(self):
        """ Shortcut to sprites render """
        return self.sprites[0].renderingOrder

    @property
    def dirty(self):
        """ If we have sprites and a sprite's rendering order is no longer the same as it's last one,
        we need to update the layer to re-order sprites """
        return self.visible and self.ready and self.sprites[0].renderingOrder != self.sprites[0].addedOnRenderingOrder

    def _startTransparency(self):
        """ When a sprite's alpha becomes 0 - 1 it needs to be rendered last- """
        AnimableRender._startTransparency(self)
        for sprite in self.sprites:
            sprite.batch = worldLayer.transparentBatch

    def _endTransparency(self):
        """ Restore a sprite to it's original opaque layer """
        AnimableRender._endTransparency(self)
        for sprite in self.sprites:
            sprite.batch = worldLayer.dynamicBatch

    def setRenderingOrder(self, value):
        for sprite in self.sprites:
            sprite.renderingOrder = value

    def getSize(self):
        if self.sprites:
            return self.sprites[0].getSize()
        else:
            return (24, 24)

    def _initiate(self):
        self._create()
        self._updatePosition()
        self._finalize()

    def _finalize(self):
        return

    def _addSprites(self, *sprites):
        return

    def addSprites(self):
        group, batch, transparent = worldLayer.getAllLayerRenders(LayerType.LAYERED)
        for sprite in self.sprites:
            if sprite.opacity > 0:
                if sprite.opacity < 255:
                    sprite_batch = transparent
                else:
                    sprite_batch = batch
                if sprite.batch is not sprite_batch:
                    sprite.batch = sprite_batch
                if sprite.visible is False:
                    sprite.visible = True

    def delSprites(self):
        for sprite in self.sprites:
            if sprite.visible is True:
                sprite.visible = False

    def _delSprites(self, *sprites):
        return

    def _updatePosition(self):
        """ Update the position of all sprites for this object. """
        x, y = self.object.getDiffEffectProjection2D()
        for sprite in self.sprites:
            sprite.setPosition(x, y)

    def resetRenderState(self):
        """Resets the sprites previous state to the current state."""
        for sprite in self.sprites:
            sprite.resetRenderState()

    def setRenderPosition(self, x, y, z, interp):
        for sprite in self.sprites:
            sprite.setPositionInterpolate(x, y - z, y, interp)

    def _createShadow(self, sheet, group, batch, referencePoint=RefPointType.CENTER, flip_x=False, frame=0):
        """ Add a shadow to the sprite. """
        group, batch = worldLayer.getLayerRender(LayerType.LAYERED, True)
        shadowSprite = iSprite.PygletSheet(sheet, group=group, batch=batch)
        shadowSprite.z_offset = -1
        shadowSprite.setTransformation(sheet, 0, 0, flip_x=flip_x, flip_y=True)
        shadowSprite.setFrame(frame)
        shadowSprite.customSize = True
        shadowSprite.setRGBA(0, 0, 0, 50)
        shadowSprite.setScale(0.95, 0.4)
        shadowSprite.offset = getShadowPosition(self.sheet.grid[frame], shadowSprite, referencePoint)
        return shadowSprite

    def setEnvironment(self):
        """ Implemented by player instead """
        return


def getShadowPosition(original, shadow, referencePoint):
    """ Takes the position and makes it center. """
    offx, offy = (0, 0)
    if referencePoint & RefPointType.CENTERX:
        offx = original.width / 2 - shadow.width / 2
    if referencePoint & RefPointType.CENTERY:
        offy = original.height / 2 - shadow.height / 2
    if referencePoint & RefPointType.LEFT:
        offx = original.width / 2 - shadow.width / 2
    if referencePoint & RefPointType.TOP:
        offy = shadow.height / 2
    if referencePoint & RefPointType.RIGHT:
        offx = shadow.right
    if referencePoint & RefPointType.BOTTOM:
        offy = -(shadow.height / 2)
    return (offx, offy)
