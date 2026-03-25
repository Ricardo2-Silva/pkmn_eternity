# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\world\effects.py
"""
Created on Jul 15, 2015

@author: Admin
"""
import math
from client.control.events.event import eventManager
from client.control.service.session import sessionService
from client.control.system.anims import FadeColor, MultiParallelAnim, AnimCallable
from client.render.cache import textureCache
from client.render.particle import GroupParticleSystem, ParticleSystem
from twisted.internet import reactor, defer
from client.control.world.map import Effect, CustomEffect, ImageEffect, MapObject
from client.data.world.map import EffectData, MapObjectData
from client.data.world.animation import AnimType, AnimDirection, Animation, AnimationEnd
from shared.container.constants import RefPointType, StatType, StatusEffect
import pyglet, random

class ShinyParticleSystem(GroupParticleSystem):
    particleClass = ImageEffect
    totalParticles = 6
    life = 0.9
    lifeVariation = 0.3
    angle = 90
    angleVariation = 45
    speed = 80
    speedVariation = 0
    rotation = 0
    rotationVariation = 0
    scaleLife = False
    scale = 1.0
    scaleVar = 0
    gravity = (0, -3)
    xVariation = 5
    yVariation = 0
    duration = 1.3


class HealParticleSystem(GroupParticleSystem):
    particleClass = ImageEffect
    totalParticles = 8
    life = 0.3
    lifeVariation = 0.4
    angle = 90
    angleVariation = 5
    speed = 25
    speedVariation = 70
    rotation = 0
    rotationVariation = 0
    scaleLife = False
    scale = 1.0
    scaleVar = 0
    gravity = (0, 0)
    xVariation = 12
    yVariation = 0
    duration = 1.0


class CureParticleSystem(ParticleSystem):
    particleClass = Effect
    totalParticles = 8
    life = 0.3
    lifeVariation = 0.4
    angle = 90
    angleVariation = 5
    speed = 25
    speedVariation = 70
    rotation = 0
    rotationVariation = 360
    scaleLife = False
    scale = 1.0
    scaleVar = 0
    gravity = (0, 0)
    xVariation = 12
    yVariation = 0
    duration = 1.0


class EffectController:
    healParticles = textureCache.getEffectXml("effects/particles/heal_particles", RefPointType.CENTER)
    starShinies = [textureCache.getImageFile("lib/effects/starshiny_01.png"), textureCache.getImageFile("lib/effects/starshiny_02.png")]
    cureParticles = textureCache.getEffect("heal_[6]", RefPointType.CENTER)

    def __init__(self):
        """ Manages all built in effects."""
        eventManager.registerListener(self)
        self.builtInEffects = {'Revive':self.revive, 
         'LevelUp':self.levelUp, 
         'Warp':self.warp, 
         'Explode':self.explode, 
         'Buff':self.buff, 
         'Heal':self.heal, 
         'Debuff':self.debuff, 
         'FullHeal':self.pokeballHeals, 
         'Shiny':self.shinyEffect, 
         'Cure':self.cure}
        self.statEffects = {(StatType.ATK): "red", 
         (StatType.DEF): "green", 
         (StatType.SPATK): "purple", 
         (StatType.SPDEF): "white", 
         (StatType.SPEED): "blue", 
         (StatType.ENERGY): "yellow", 
         (StatType.CRIT_CHANCE): "yellow", 
         (StatType.ACCURACY): "white", 
         (StatType.EVASION): "yellow"}
        self.cureColors = {(StatusEffect.PARALYSIS): (255, 255, 102), 
         (StatusEffect.BURN): (194, 30, 86), 
         (StatusEffect.FREEZE): (0, 150, 255), 
         (StatusEffect.POISON): (128, 0, 128), 
         (StatusEffect.SLEEP): (170, 255, 0)}

    def onCharPlayEffect(self, char, effect, *args):
        (self.builtInEffects[effect])(char, *args)

    def pokeballHeals(self, char):
        positions = {
         0: (5, 26), 1: (15, 26), 
         2: (5, 22), 3: (15, 22), 
         4: (5, 18), 5: (15, 18)}
        balls = []
        start_x, start_y = char.getPosition2D()
        pokemon = sessionService.getClientPokemonsData()
        pokemon.sort(key=(lambda pkmn: pkmn.lineupId))

        def add_ball(i, pokemon_data):
            x = start_x + positions[i][0]
            y = start_y + positions[i][1]
            balls.append(MapObject(MapObjectData(char.data.map, "zitems/pokeball", (
             x, y), False, y + 10)))

        def flash_all():
            ball_sprites = [ball.renderer.sprite for ball in balls]
            anim = MultiParallelAnim(ball_sprites, FadeColor, (0, 0, 0), 1)
            anim += MultiParallelAnim(ball_sprites, FadeColor, (50, 0, 50), 1)
            anim += MultiParallelAnim(ball_sprites, FadeColor, (255, 0, 0), 1)
            anim += MultiParallelAnim(ball_sprites, FadeColor, (0, 0, 255), 1)
            balls[0].startAnim(anim)

        for i in range(len(pokemon)):
            reactor.callLater(0.2 * i, add_ball, i, pokemon[i])

        reactor.callLater(0.2 * len(pokemon), flash_all)

    def shinyEffect(self, char):
        if char.visible:
            x, y = char.getPosition2D()
            system = ShinyParticleSystem([EffectData(particle, position=(x, y + char.getHeight()), refPointType=(RefPointType.CENTER)) for particle in self.starShinies])
            system.start()

    def heal(self, char):
        if char.visible:
            x, y = char.getProjection2D()
            system = HealParticleSystem([EffectData(particle, position=(x, y), refPointType=(RefPointType.CENTER)) for particle in self.healParticles.texture])
            system.start()
            char.updateHpBar()

    def cure(self, char, statusEffect=None):
        if char.visible:
            x, y = char.getProjection2D()
            for i in range(3):
                reactor.callLater(i * 0.15, self._generateCuteParticle, i, char, statusEffect)

    def _generateCuteParticle(self, i, char, statusEffect):
        x, y = char.getPosition2D()
        effect = Effect(EffectData("heal_[6]", position=(x, y), animation=Animation(delay=0.25, end=(AnimationEnd.STOP), removal="delete"),
          refPointType=(RefPointType.CENTER)))
        (effect.setColor)(*self.cureColors.get(statusEffect, (255, 255, 255)))
        startAngle = i * 36.0
        effect.renderer.spiral(90, startAngle, random.randint(17, 23), 1.3)

    def buff(self, char, stat):
        if char.visible:
            width = char.getWidth() / 4
            for num in range(5):
                pyglet.clock.schedule_once(self._createParticle, num * random.choice((0.05,
                                                                                      0.1,
                                                                                      0.03)), stat, "reverse", char, -char.getWidth() / 2 + width * num, random.randint(-8, 15))

            Effect(EffectData(f"stat_{self.statEffects[stat]}_base_[6]", position=(0,
                                                                                   -5),
              animation=Animation(delay=0.1),
              refPointType=(RefPointType.BOTTOMCENTER),
              attach=char,
              renderingOrder=1))

    def debuff(self, char, stat):
        if char.visible:
            width = char.getWidth() / 4
            for num in range(5):
                pyglet.clock.schedule_once(self._createParticle, num * random.choice((0.05,
                                                                                      0.1,
                                                                                      0.03)), stat, "normal", char, -char.getWidth() / 2 + width * num, random.randint(-8, 15))

            Effect(EffectData(f"stat_{self.statEffects[stat]}_base_[6]", position=(0,
                                                                                   0),
              animation=Animation(frames=(reversed(range(6))), delay=0.1),
              refPointType=(RefPointType.BOTTOMCENTER),
              attach=char,
              renderingOrder=1))

    def _createParticle(self, dt, stat, direction, char, x, y):
        try:
            fileId = f"stat_{self.statEffects[stat]}_[7]"
        except KeyError:
            fileId = "stat_yellow_[7]"

        if direction == "reverse":
            animation = Animation(frames=(reversed(range(7))), delay=(random.choice((0.05,
                                                                                     0.1,
                                                                                     0.03))))
        else:
            animation = Animation(frames=(range(7)), delay=(random.choice((0.05, 0.1,
                                                                           0.03))))
        Effect(EffectData(fileId, position=(
         x, y),
          animation=animation,
          refPointType=(RefPointType.BOTTOMCENTER),
          attach=char,
          renderingOrder=(random.randint(-1, 2))))

    def explode(self, char):
        x, y = char.getProjection2D()
        e = Effect(EffectData("explode_[4]", position=(x, y + char.getHeight() / 2), refPointType=(RefPointType.CENTER), animation=Animation(delay=0.1)))

    def warp(self, char):
        x, y = char.getProjection2D()
        e = Effect(EffectData("warp_[10]", position=(x, y + char.getHeight() / 2), refPointType=(RefPointType.CENTER), animation=Animation(delay=0.1, duration=1.5)))
        e.setAlpha(254)

    def revive(self, char):
        char.revive()
        anim = char.renderer.pulse(1, 0.5, 1.2)
        x, y = char.getProjection2D()
        e = Effect(EffectData("evolutionLight_[4](veryfast)", animation=Animation(delay=0.1)))
        e.setPosition(x, y + char.getHeight() / 2)
        e.renderer.flash(0.5)

    def levelUp(self, char):
        e = Effect(EffectData("levelup_circle_[10]", position=(0, 4), refPointType=(RefPointType.CENTER), animation=Animation(delay=0.05),
          attach=char,
          renderingOrder=2))

        def circle():
            e = Effect(EffectData("circle_white_[6]", position=(0, 0), refPointType=(RefPointType.BOTTOMCENTER), animation=Animation(delay=0.05),
              attach=char,
              renderingOrder=(-1)))

        def beam():
            e = Effect(EffectData("levelup_beam_[10]", position=(-2, -10), refPointType=(RefPointType.BOTTOMCENTER), animation=Animation(delay=0.05),
              attach=char,
              renderingOrder=(-1)))
            e.setAlpha(200)
            e = Effect(EffectData("levelup_beam_star_[10]", position=(0, 0), refPointType=(RefPointType.CENTER), animation=Animation(delay=0.05),
              attach=char,
              renderingOrder=2))

        reactor.callLater(0.5, beam)
        reactor.callLater(0.55, circle)


effectManager = EffectController()
