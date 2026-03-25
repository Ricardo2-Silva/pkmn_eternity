# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\world\action\moves\psychic.py
"""
Created on Feb 15, 2016

@author: Admin
"""
from client.data.world.skill import ClientSkillUseInstance
from shared.container.constants import CreatureAction, RefPointType
from client.control.world.map import SkillEffect, MultiImageEffect, ImageEffect
from client.data.world.map import EffectData
from client.data.world.animation import AnimType, Animation
from shared.service.geometry import getAngleBetweenTwoPoints
from client.render.shader.default_sprite import pulse_shader, bubble_shader, ripple_shader, shield_shader
import pyglet
from client.data.layer import LayerType
from client.data.container.map import mapContainer
from client.render.cache import textureCache
from client.data.system.background import BackgroundOption, BackgroundData
from client.control.system.background import backgroundController
from pyglet.gl.gl import GL_DST_COLOR, GL_ZERO
from client.control.system.anims import AnimCallable

class Confusion(ClientSkillUseInstance):

    def process(self):
        self.char.playAction(CreatureAction.SPECIAL, 0)
        direction = getAngleBetweenTwoPoints(self.char.getPosition2D(), self.data)
        self.char.setFacingNear(direction)
        self.flashConfusion()

    def flashConfusion(self):
        bg = ImageEffect(EffectData((textureCache.getBackgroundColor((255, 255, 255))), position=(0,
                                                                                                  0),
          layerType=(LayerType.LAYERED),
          refPointType=(RefPointType.BOTTOMLEFT),
          blend_src=GL_DST_COLOR,
          blend_dest=GL_ZERO))
        (bg.setScales)(*mapContainer.getMapSize())
        bg.setAlpha(254)
        bg.setColor(134, 31, 120)
        anim = bg.fadeColor(0.2, (184, 128, 216), startColor=(232, 144, 160))
        anim += bg.fadeColor(0.2, (104, 144, 144), startColor=(184, 128, 216))
        anim += bg.fadeColor(0.2, (232, 144, 160), startColor=(104, 144, 144))
        anim *= 3
        anim += AnimCallable(bg.delete)
        bg.renderer.startAnim(anim)


class Disable(ClientSkillUseInstance):
    return


class Agility(ClientSkillUseInstance):

    def process(self):
        self.char.playAction(CreatureAction.DOUBLE, 0)
