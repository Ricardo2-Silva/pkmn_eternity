# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\render\particle.py
import time, pyglet, math
from client.control.world.map import Effect
from client.data.world.map import EffectData
import random

class ParticleSystem(object):
    __doc__ = "\n      Simple particle engine that allows adjustments over time for simplicity.\n      Note: The follow variations range from both before and after of the original point.\n      Example: If angle is 90 and variation is 90, it will go 90 + (-90 -> 90) giving you 180 degrees variation.\n      - angleVariation:\n      - xVariation:\n      - yVariation\n    "
    particleClass = Effect
    totalParticles = 8
    life = 0.2
    lifeVariation = 2
    angle = 90
    angleVariation = 1
    speed = 100
    speedVariation = 1
    scaleLife = False
    rotation = 0
    rotationVariation = 0
    rotateLife = False
    scale = 1
    scaleVar = 0
    xVariation = 0
    yVariation = 0
    gravity = (0, 0)
    duration = 4
    alpha = 255
    alphaLife = False
    color = None

    def __init__(self, data):
        self.data = data
        self.emit_counter = 0
        self.particle_count = 0
        self.particles = []
        self.emission_rate = self.totalParticles / self.life
        self.active = True
        self.elapsed = 0
        self.reusable = []

    def start(self, startTime=None):
        self.active = True
        pyglet.clock.schedule_interval(self.step, 0.016666666666666666)
        if startTime:
            t = time.time() - startTime
            print("DIFFERENCE", t)

    def add_particle(self):
        if self.reusable:
            e = self.reusable.pop(0)
            (e.setPosition)(*e.originalPosition)
            e.renderer.resetFrame()
            e.show()
        else:
            e = self.particleClass(self.data.copy())
            x, y = e.getPosition2D()
            if self.xVariation:
                x += random.randrange(-self.xVariation, self.xVariation)
            if self.yVariation:
                y += random.randrange(-self.yVariation, self.yVariation)
            e.setPosition(x, y)
            e.originalPosition = (x, y)
            if self.color:
                (e.setColor)(*self.color)
            e.life = self.life + self.lifeVariation * random.random()
            e.startLife = e.life
            if self.alphaLife:
                e.renderer.stopAnims()
                e.fadeTo(e.life, 0, self.alpha)
            elif self.alpha != 255:
                e.setAlpha(self.alpha)
        e.angle = math.radians(self.angle + random.randrange(-self.angleVariation, self.angleVariation) * random.random())
        e.speed = self.speed + self.speedVariation * random.random()
        e.velocity = [
         math.cos(e.angle) * e.speed,
         math.sin(e.angle) * e.speed]
        e.scale = self.scale + self.scaleVar * random.random()
        e.rotation = self.rotation + self.rotationVariation * random.random()
        e.setScale(e.scale)
        self.particles.append(e)

    def stopEmitting(self):
        self.active = False

    def stop(self):
        pyglet.clock.unschedule(self.step)
        self.active = False
        for particle in self.particles + self.reusable:
            particle.delete()

        del self.particles

    def update_particles(self, dt):
        for particle in self.particles:
            particle.life -= dt
            if self.scaleLife:
                scale = particle.scale * (particle.life / particle.startLife)
            else:
                scale = particle.scale
            if self.rotateLife:
                particle.rotation += particle.life / particle.startLife
            particle.velocity[0] += self.gravity[0]
            particle.velocity[1] += self.gravity[1]
            particle.updateMultiple(particle.getX() + particle.velocity[0] * dt, particle.getY() + particle.velocity[1] * dt, particle.rotation, scale)
            if particle.life <= 0:
                particle.hide()
                self.particles.remove(particle)
                self.reusable.append(particle)

    def step(self, dt):
        self.particle_count = sum(particle.life >= 0 for particle in self.particles)
        if self.active:
            rate = 1.0 / self.emission_rate
            self.emit_counter += dt
            while self.particle_count < self.totalParticles and self.emit_counter > rate:
                self.add_particle()
                self.emit_counter -= rate

            self.elapsed += dt
            if self.duration != -1:
                if self.duration < self.elapsed:
                    self.stopEmitting()
        self.update_particles(dt)
        if not self.active:
            if self.particle_count == 0:
                self.stop()


class GroupParticleSystem(ParticleSystem):
    __doc__ = "\n      This particle system takes a list of effects to create multiple particles at once.\n    "

    def add_particle(self):
        if self.reusable:
            e = self.reusable.pop(0)
            (e.setPosition)(*e.originalPosition)
            e.renderer.resetFrame()
            e.show()
        else:
            e = self.particleClass(random.choice(self.data).copy())
            x, y = e.getPosition2D()
            if self.xVariation:
                x += random.randrange(-self.xVariation, self.xVariation)
            if self.yVariation:
                y += random.randrange(-self.yVariation, self.yVariation)
            e.setPosition(x, y)
            e.originalPosition = (x, y)
        e.life = self.life + self.lifeVariation * random.random()
        e.startLife = e.life
        e.angle = math.radians(self.angle + random.randrange(-self.angleVariation, self.angleVariation) * random.random())
        e.speed = self.speed + self.speedVariation * random.random()
        e.velocity = [
         math.cos(e.angle) * e.speed,
         math.sin(e.angle) * e.speed]
        e.scale = self.scale + self.scaleVar * random.random()
        e.rotation = int(self.rotation + self.rotationVariation * random.random())
        e.setScale(e.scale)
        self.particles.append(e)
