# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\world\action\moves\normal.py
"""
Created on Feb 15, 2016

@author: Admin
"""
import random, sys, time
from twisted.internet import reactor
import pyglet
from client.control.world.map import SkillEffect, Effect, CustomEffect
from client.data.container.char import charContainer
from client.data.world.animation import AnimationEnd, Animation
from client.data.world.map import EffectData
from client.data.world.skill import ClientSkillUseInstance
from client.render.particle import ParticleSystem
from shared.container.constants import CreatureAction, RefPointType, StatusEffect, IdRange
from shared.container.skill import LinearEventSource, StaticTickEventSource, StaticEventSource
from shared.service.cycle import dayNight
from shared.service.direction import directionService
from shared.service.geometry import getAngleBetweenTwoPoints, getDistanceBetweenTwoPoints, getPositionOnDirection

class Scratch(ClientSkillUseInstance):

    def process(self):
        direction = self.data
        self.char.setFacingNear(direction)
        self.char.playAction(CreatureAction.SCRATCH)
        x, y = self.char.getPositionInFrontMiddle(direction, 10)
        Effect(EffectData("scratch_[3]", (x, y), animation=Animation(delay=0.1)))


class Focusenergy(ClientSkillUseInstance):

    def process(self):
        self.char.playAction(CreatureAction.CHARGE)
        self.charge()

    def charge(self):
        x, y = self.char.getProjection2D()
        random_direction = [
         0, 45, 90, 135, 180, 225, 270, 315]
        default_y = y + self.char.getHeight() / 2
        for i in range(8):
            new_x, new_y = getPositionOnDirection((x, default_y), random.randint(random_direction[i] - 25, random_direction[i] + 25), random.randint(20, 50))
            e2 = Effect(EffectData("effects/particles/yellow_star_small", position=(
             new_x, new_y),
              animation=Animation(delay=0.1, duration=0.4),
              metafile=True))
            e2.moveTo(random.uniform(0.2, 0.4), x, default_y)


class Leer(ClientSkillUseInstance):

    def process(self):
        self.char.setFacingNear(self.data)
        SkillEffect(EffectData("leer", (self.char.getOffsetInFrontMiddle(self.data, 10)), animation=Animation(delay=0.05), attach=(self.char), renderingOrder=(-1), metafile=True))


class Scaryface(ClientSkillUseInstance):

    def process(self):
        self.char.setFacingNear(self.data)
        SkillEffect(EffectData("scaryface", (0, self.char.getHeight() // 3), animation=Animation(delay=0.1), attach=(self.char), renderingOrder=(-1), metafile=True))


class Pound(ClientSkillUseInstance):

    def process(self):
        direction = self.data
        self.char.setFacingNear(direction)
        self.char.playAction(CreatureAction.ATK)
        Effect(EffectData("normal_hit_[3]", (self.char.getPositionInFrontMiddle(direction, 10)), animation=Animation(delay=0.1)))


class Hornattack(ClientSkillUseInstance):

    def process(self):
        direction = self.data
        self.char.setFacingNear(direction)
        self.char.playAction(CreatureAction.ATK)
        Effect(EffectData("normal_hit_[3]", (self.char.getPositionInFrontMiddle(direction, 10)), animation=Animation(delay=0.1)))


class Dizzypunch(ClientSkillUseInstance):

    def process(self):
        direction = self.data
        self.char.setFacingNear(direction)
        self.char.playAction(CreatureAction.PUNCH, 0)
        position = self.char.getPositionInFrontMiddle(direction, 20)
        self.punch = SkillEffect(EffectData("small_punch_[1]", position=position, animation=Animation(delay=0.4), refPointType=(RefPointType.CENTER)))
        hitChar = (charContainer.getAllCharsInDirection)(IdRange.PC_POKEMON, *position, *(0, self.data, 30, 30))
        if hitChar:
            self.onSkillDamage(None, hitChar[0])

    def onExpired(self):
        if self.punch.visible:
            self.punch.hide()

    def onSkillDamage(self, char, target, timeStamp, extraData):
        x, y = target.getPosition2D()
        e = SkillEffect(EffectData("dizzypunch", position=(x, y), refPointType=(RefPointType.CENTER), animation=Animation(delay=0.08), metafile=True))
        if random.randint(0, 100) < 30:
            target.showStatusEffect(StatusEffect.CONFUSED, 3)


class Rapidspin(ClientSkillUseInstance):

    def process(self):
        self.duration = 0.4
        x, y = self.char.getPosition2D()
        width = self.char.getHeight() / 4
        for i in range(0, 5):
            pyglet.clock.schedule_once(self._createSpin, 0.05 * i, x, y + width * i)

        self.char.playAction(CreatureAction.SPIN, 0)
        self.start()

    def _createSpin(self, dt, x, y):
        SkillEffect(EffectData("rapid_spin_[6]", (x, y), animation=Animation(delay=0.1)))


class Stomp(ClientSkillUseInstance):

    def process(self):

        def effect(_):
            pos = self.char.getPosition2D()
            l = SkillEffect(EffectData("stomp", pos, refPointType=(RefPointType.CENTER), renderingOrder=2500))

            def fadeOut():
                l.fadeOut(2)

            reactor.callLater(0.1, fadeOut)
            self.stop()

        d = self.char.playAction(CreatureAction.JUMP)
        d.addCallback(effect)
        self.start()


class Tackle(ClientSkillUseInstance):

    def process(self):
        self.direction = self.data
        self.char.setFacingNear(self.direction)
        self.startPosition = self.char.getPosition2D()
        LinearEventSource(self, *(self.startPosition), **{'speed':190,  'distance':100})
        self.totalDistance = 0
        self.createdImages = 0
        self.char.playAction(CreatureAction.WALK, 3)
        (self.createAfterImage)(*self.startPosition, *(0, ))
        self.char.clearAllOrders()
        self.start()

    def onExpired(self):
        self.char.cancelAction()

    def onSkillDamage(self, char, target, timeStamp, extraData):
        Effect(EffectData("normal_hit_[3]", position=(target.getPosition2D()), animation=Animation(delay=0.1, end=(AnimationEnd.STOP)),
          refPointType=(RefPointType.BOTTOMCENTER)))
        (self.char.setPosition)(*target.getPosition())
        self.char.applyEnvironmentEffects()
        self.char.cancelAction()
        self.char.setStunDuration(0.3 - (time.time() - timeStamp))
        self.stop(False)

    def createAfterImage(self, x, y, z):
        currentSheet = self.char.renderer.sheet
        y += currentSheet.getHeight() // 2
        sheetEffect = CustomEffect(EffectData(currentSheet,
          flip_x=(self.char.renderer._getFlip()),
          refPointType=(RefPointType.BOTTOMCENTER)))
        sheetEffect.setAlpha(254)
        sheetEffect.renderer.setFrame(self.char.renderer.bodySprite.currentFrame)
        sheetEffect.setPosition(x, y)
        d = sheetEffect.fadeOut(0.5)
        d.addCallback(self.removeImage, sheetEffect)
        self.createdImages += 1

    def removeImage(self, result, sprite):
        if sprite.visible:
            sprite.delete()

    def onSourceMove(self, source, x, y):
        self.totalDistance = int(getDistanceBetweenTwoPoints(self.startPosition, (x, y)))
        if (self.char.canMoveOnPosition)(self.direction, *self.char.getPosition2D(), *(x, y, 0)):
            self.char.setPosition(x, y)
            if self.totalDistance / 16 > self.createdImages:
                self.createAfterImage(x, y, 0)
                self.char.applyEnvironmentEffects()
        else:
            self.stop(False)


class Takedown(Tackle):
    return


class Flash(ClientSkillUseInstance):

    def process(self):
        self.char.playActionWithDelay(CreatureAction.SPATK, 0.5, 0.07)
        if dayNight.isNight() or self.char.data.map.information.is_cave:
            self.char.flashLight()


class SandParticle(ParticleSystem):
    totalParticles = 15
    life = 0.1
    lifeVariation = 0.4
    angle = 90
    angleVariation = 25
    speed = 100
    speedVariation = 20
    gravity = (0, 0)
    duration = 1


class SmokeScreenParticleSystem(ParticleSystem):
    totalParticles = 40
    life = 5.0
    lifeVariation = 3.5
    speed = 10
    speedVariation = 20
    scale = 0.5
    scaleVar = 0.8
    color = (128, 128, 128)
    gravity = (0, 0)
    duration = 10
    angle = 90
    angleVariation = 45
    xVariation = 50
    alpha = 254
    alphaLife = True


class Sandattack(ClientSkillUseInstance):

    def process(self):
        direction = self.data
        self.char.setFacingNear(direction)
        self.char.playAction(CreatureAction.SHOOT, 0.5)
        p = SandParticle(EffectData("sand", self.char.getPosition2D()))
        p.angle = direction
        p.start()


class Tailwhip(ClientSkillUseInstance):

    def process(self):
        direction = self.data
        effectDirection = directionService.getNear(direction)
        self.char.setFacing(effectDirection)
        self.duration = 0.4
        x, y = self.char.getPosition2D()
        effect = Effect(EffectData("force_[3]", position=(x, y - 20), animation=Animation(delay=0.1),
          refPointType=(RefPointType.BOTTOMCENTER),
          renderingOrder=(0 if direction > 180 else self.char.getPosition2D()[1] - 3)))
        self.char.playAction(CreatureAction.TAILWHIP, 0)
        self.start()


class Growl(ClientSkillUseInstance):

    def process(self):
        direction = self.data
        self.char.setFacingNear(direction)
        self.char.playAction(CreatureAction.SPATK, 0)
        self.timeBegin = time.time()
        self.initialPosition = x, y = self.char.getPositionInFrontMiddle(direction, 10)[:2]
        left, middle, right = directionService.getDirectionsNextTo(direction)
        directionClamps = {(directionService.UP): (0, 1), 
         (directionService.UP_RIGHT): (2, 3), 
         (directionService.RIGHT): (5, 4), 
         (directionService.DOWN_RIGHT): (6, 7), 
         (directionService.DOWN): (8, 9), 
         (directionService.DOWN_LEFT): (6, 7), 
         (directionService.LEFT): (4, 5), 
         (directionService.UP_LEFT): (2, 3)}
        leftEffect = SkillEffect(EffectData("growl_[10]", position=(
         x, y),
          animation=Animation(frames=(directionClamps[left]), delay=0.1, end=(AnimationEnd.STOP), removal=False),
          refPointType=(RefPointType.CENTER),
          flip_x=(True if left in directionService.MIRRORS else False)))
        leftEffect.renderer.grow(0.2)
        dirEffect = SkillEffect(EffectData("growl_[10]", position=(
         x, y),
          animation=Animation(frames=(directionClamps[middle]), delay=0.1, end=(AnimationEnd.STOP), removal=False),
          refPointType=(RefPointType.CENTER),
          flip_x=(True if middle in directionService.MIRRORS else False)))
        dirEffect.renderer.grow(0.2)
        rightEffect = SkillEffect(EffectData("growl_[10]", position=(
         x, y),
          animation=Animation(frames=(directionClamps[right]), delay=0.1, end=(AnimationEnd.STOP), removal=False),
          refPointType=(RefPointType.CENTER),
          flip_x=(True if right in directionService.MIRRORS else False)))
        rightEffect.renderer.grow(0.3)
        self.effects = {}
        left_source = LinearEventSource(self, x, y, 0, left, speed=160, distance=50)
        self.effects[left_source] = leftEffect
        middle_source = LinearEventSource(self, x, y, 0, middle, speed=160, distance=50)
        self.effects[middle_source] = dirEffect
        right_source = LinearEventSource(self, x, y, 0, right, speed=160, distance=50)
        self.effects[right_source] = rightEffect
        self.start()

    def onSourceMove(self, source, x, y):
        self.effects[source].setPosition(x, y)

    def onExpired(self):
        for effect in self.effects.values():
            if effect.visible:
                effect.delete()

        self.effects.clear()


class Quickattack(ClientSkillUseInstance):

    def process(self):
        charId, charType = self.data
        targetChar = charContainer.getCharByIdIfAny(charId, charType)
        if targetChar:
            if self.char.getPosition2D() != targetChar.getPosition2D():
                angle = getAngleBetweenTwoPoints(self.char.getPosition2D(), targetChar.getPosition2D())
                self.char.setFacingNear(angle)
                angleAtTarget = getAngleBetweenTwoPoints(targetChar.getPosition2D(), self.char.getPosition2D())
                targetPosition = targetChar.getPositionInFront(angleAtTarget, 20)
                (self.char.setPosition)(*targetPosition)
            self.char.playAction(CreatureAction.ATK, 0.5)
            Effect(EffectData("normal_hit_[3]", (targetChar.getPosition2D()), animation=Animation(delay=0.1)))
        else:
            sys.stderr.write(f"Tried to use skill Quick Attack, but char does not exist. {charId}, {charType}\n")


class Harden(ClientSkillUseInstance):

    def process(self):
        self.char.playAction(CreatureAction.WITHDRAW, 0)


class Defensecurl(ClientSkillUseInstance):

    def process(self):
        self.char.playAction(CreatureAction.WITHDRAW, 0)


class Minimize(ClientSkillUseInstance):

    def process(self):
        self.char.playAction(CreatureAction.WITHDRAW, 0)
        StaticEventSource(self, 0, 0, 0, self.duration)
        self.start()

    def onSourceActivate(self, source, x, y, z, count):
        print("STARTING?")
        self.char.renderer.shrink(0.5, reset=False)

    def onSourceStop(self, source, result, x, y, z):
        if self.char:
            if self.char.isReleased():
                self.char.renderer.shrink(1.0, reset=False)


class Bind(ClientSkillUseInstance):

    def process(self):
        charId, charType = self.data
        self.target = charContainer.getCharByIdIfAny(charId, charType)
        if self.target:
            if self.char.getPosition2D() != self.target.getPosition2D():
                angle = getAngleBetweenTwoPoints(self.char.getPosition2D(), self.target.getPosition2D())
                self.char.setFacingNear(angle)
            self.b = SkillEffect(EffectData("bind_back_[14]", attach=(self.target),
              position=(0, 0),
              animation=Animation(delay=0.1, duration=0, end=(AnimationEnd.STOP), removal=False),
              refPointType=(RefPointType.BOTTOMCENTER),
              renderingOrder=1))
            self.f = SkillEffect(EffectData("bind_front_[14]", position=(0, 0),
              attach=(self.target),
              animation=Animation(delay=0.1, duration=0, end=(AnimationEnd.STOP), removal=False),
              refPointType=(RefPointType.BOTTOMCENTER),
              renderingOrder=(-1)))
            self.target.damageStates.set(self)
            self.start()

    def onSkillDamage(self, char, target, timeStamp, extraData):
        if self.f.visible:
            self.f.pulseSeparate(pulseCount=2, duration=0.5, scale_x=0.85, scale_y=1)
        if self.b.visible:
            self.b.pulseSeparate(pulseCount=2, duration=0.5, scale_x=0.85, scale_y=1)

    def onExpired(self):
        if self.b.visible:
            self.b.delete()
        if self.f.visible:
            self.f.delete()


class Wrap(Bind):

    def process(self):
        charId, charType = self.data
        self.target = charContainer.getCharByIdIfAny(charId, charType)
        if self.target:
            if self.char.getPosition2D() != self.target.getPosition2D():
                angle = getAngleBetweenTwoPoints(self.char.getPosition2D(), self.target.getPosition2D())
                self.char.setFacingNear(angle)
            self.b = SkillEffect(EffectData("wrap_back_[14]", attach=(self.target),
              position=(0, 0),
              animation=Animation(delay=0.1, duration=0, end=(AnimationEnd.STOP), removal=False),
              refPointType=(RefPointType.BOTTOMCENTER),
              renderingOrder=1))
            self.f = SkillEffect(EffectData("wrap_front_[14]", position=(0, 0),
              attach=(self.target),
              animation=Animation(delay=0.1, duration=0, end=(AnimationEnd.STOP), removal=False),
              refPointType=(RefPointType.BOTTOMCENTER),
              renderingOrder=(-1)))
            self.target.damageStates.set(self)
            self.start()

    def onSkillDamage(self, char, target, timeStamp, extraData):
        if self.f.visible:
            self.f.pulseSeparate(pulseCount=2, duration=0.5, scale_x=0.85, scale_y=1)
        if self.b.visible:
            self.b.pulseSeparate(pulseCount=2, duration=0.5, scale_x=0.85, scale_y=1)

    def onExpired(self):
        if self.b.visible:
            self.b.delete()
        if self.f.visible:
            self.f.delete()


class Supersonic(ClientSkillUseInstance):

    def process(self):
        direction = self.data
        self.char.setFacingNear(direction)
        self.char.playActionWithDelay(CreatureAction.SPATK, 0.5, 0.07)
        x, y, z = self.char.getPositionInFront(direction, 10)
        LinearEventSource(self, x, y, z, direction, speed=200, distance=100)
        self.pulse = SkillEffect(EffectData("142_[8]", (x, y), animation=Animation(delay=0.05, duration=0), renderingOrder=0))
        self.start()

    def onSourceStop(self, source, result, x, y, z):
        self.pulse.delete()

    def onSourceMove(self, source, x, y):
        self.pulse.setPosition(x, y)


class Furyswipes(ClientSkillUseInstance):

    def process(self):
        self.direction = self.data
        self.char.setFacingNear(self.direction)
        StaticTickEventSource(self, 0, 0, 0, duration=0.5, count=(self.duration))
        self.char.setStunDuration(self.duration / 2)
        self.start()

    def onSourceActivate(self, source, x, y, z, count):
        self.char.playAction(CreatureAction.MULTI_STRIKE, 0)
        Effect(EffectData("normal_hit_[3]", (self.char.getPositionInFrontMiddle(self.direction, 10)[:2]),
          animation=Animation(delay=0.01)))


class Furyattack(ClientSkillUseInstance):

    def process(self):
        self.direction = self.data
        self.char.setFacingNear(self.direction)
        StaticTickEventSource(self, 0, 0, 0, duration=0.5, count=(self.duration))
        self.char.setStunDuration(self.duration / 2)
        self.start()

    def onSourceActivate(self, source, x, y, z, count):
        self.char.playAction(CreatureAction.MULTI_STRIKE, 0)
        Effect(EffectData("normal_hit_[3]", (self.char.getPositionInFrontMiddle(self.direction, 10)[:2]),
          animation=Animation(delay=0.01)))


def getRandomPositionNear(x, y, range=300):
    """ This does not check for valid positions, useful for area skills. """
    x1 = random.randint(int(x) - range, int(x) + range)
    y1 = random.randint(int(y) - range, int(y) + range)
    return (
     x1, y1)


class Smokescreen(ClientSkillUseInstance):

    def process(self):
        self.char.playActionWithDelay(CreatureAction.SPATK, 0.5, 0.07)
        p = SmokeScreenParticleSystem(EffectData("smoke[5]_(normalfast)_", self.char.getPosition2D()))
        p.angle = 90
        p.start(time.time())


class Sumopush(ClientSkillUseInstance):

    def process(self):
        self.char.playActionWithDelay(CreatureAction.PUNCH, 0.5, 0.07)
        self.char.direction = self.data


class Sumocharge(ClientSkillUseInstance):

    def process(self):
        self.direction = self.data
        self.char.setFacingNear(self.direction)
        self.startPosition = self.char.getPosition2D()
        LinearEventSource(self, *(self.startPosition), **{'speed':190,  'distance':100})
        self.totalDistance = 0
        self.createdImages = 0
        self.char.playAction(CreatureAction.WALK, 3)
        (self.createAfterImage)(*self.startPosition, *(0, ))
        self.char.clearAllOrders()
        self.start()

    def onExpired(self):
        self.char.cancelAction()

    def onSkillDamage(self, char, target, timeStamp, extraData):
        Effect(EffectData("normal_hit_[3]", position=(target.getPosition2D()), animation=Animation(delay=0.1, end=(AnimationEnd.STOP)),
          refPointType=(RefPointType.BOTTOMCENTER)))
        (self.char.setPosition)(*target.getPosition())
        self.char.applyEnvironmentEffects()
        self.char.cancelAction()
        self.char.setStunDuration(0.3 - (time.time() - timeStamp))
        self.stop(False)

    def createAfterImage(self, x, y, z):
        currentSheet = self.char.renderer.sheet
        y += currentSheet.getHeight() // 2
        sheetEffect = CustomEffect(EffectData(currentSheet,
          flip_x=(self.char.renderer._getFlip()),
          refPointType=(RefPointType.BOTTOMCENTER)))
        sheetEffect.setAlpha(254)
        sheetEffect.renderer.setFrame(self.char.renderer.bodySprite.currentFrame)
        sheetEffect.setPosition(x, y)
        d = sheetEffect.fadeOut(0.5)
        d.addCallback(self.removeImage, sheetEffect)
        self.createdImages += 1

    def removeImage(self, result, sprite):
        if sprite.visible:
            sprite.delete()

    def onSourceMove(self, source, x, y):
        self.totalDistance = int(getDistanceBetweenTwoPoints(self.startPosition, (x, y)))
        if (self.char.canMoveOnPosition)(self.direction, *self.char.getPosition2D(), *(x, y, 0)):
            self.char.setPosition(x, y)
            if self.totalDistance / 16 > self.createdImages:
                self.createAfterImage(x, y, 0)
                self.char.applyEnvironmentEffects()
        else:
            self.stop(False)


class Sumostomp(ClientSkillUseInstance):

    def process(self):
        self.char.playAction(CreatureAction.JUMP)


class Sumostance(ClientSkillUseInstance):

    def process(self):
        self.char.playAction(CreatureAction.REAR_UP, 2)
