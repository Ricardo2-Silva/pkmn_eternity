# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\world\char.py
"""
Created on 15 juil. 2011

@author: Kami
"""
import math, random, sys
from typing import Dict
from twisted.internet import reactor
import client.data.exceptions as exceptions, client.render.world.char as iRender, client.render.world.trainer, pyglet
from client.control.events.event import eventManager
from client.control.gui.implem import ChatMessage, HpBar, CastBar, CharacterIconTable
from client.control.service.session import sessionService
from client.control.system.anims import AnimCallable
from client.control.system.light import lightController
from client.control.system.sound import mixerController
from client.control.world.action.walking import InterfaceWalking
from client.control.world.map import Emote, Effect, QuestStatusEffect, StatusEffectObject, EnvironmentGrass, AuraSelect
from client.control.world.object import WorldObject
from client.data.container.char import charContainer
from client.data.container.map import mapContainer
from client.data.settings import gameSettings
from client.data.world.animation import Animation, AnimationSpeed
from client.data.world.map import EffectData, LightData
from shared.container.constants import CreatureAction, GroundType, FaintType, Emotes, WalkMode, StatusEffect, alwaysFlying, RefPointType, PlayerAction, WildPkmnFlag
from shared.service.direction import directionService
from shared.service.geometry import getDistanceBetweenTwoPoints, getAngleBetweenTwoPoints, getPositionOnDirection
from .action.idle import idleCharManager
from .action.physics import Jump
from .action.status import statusEffectController
from ...render.world.pokemon import PokemonRender

class CharController:
    __doc__ = " Controls the char... Like deleting them "

    def __init__(self):
        eventManager.registerListener(self)

    def onBeforeMapLoad(self):
        charContainer.wipeService()


charController = CharController()
highlightAura = AuraSelect()
selectionAura = AuraSelect()

class BasicCharObject(WorldObject):

    def __init__(self, data):
        self.onBridge = False
        self.flying = False
        self.groundType = None
        self._lastGroundType = 0
        self.wallHeight = None
        self.grassEffect = None
        self._waterLast = (0, 0)
        self.qstatus = None
        WorldObject.__init__(self, data)
        return

    def showDialogStatus(self):
        if self.data.dialogStatus:
            if not self.qstatus:
                self.qstatus = QuestStatusEffect(self)
        if self.qstatus:
            self.qstatus.updateStatus(self.data.dialogStatus)

    def applyGrass(self):
        if self.flying:
            return
        elif not self.grassEffect:
            self.grassEffect = EnvironmentGrass(self)
        else:
            if not self.grassEffect.visible:
                self.grassEffect.show()
            if self.isWalking():
                if not self.grassEffect.isAnimating():
                    self.grassEffect.startAnimation()
                self.updateGrassEffectPosition()
            elif self.grassEffect.visible:
                if self.grassEffect.isAnimating():
                    self.grassEffect.stopAnimation()
                self.updateGrassEffectPosition()

    def applyWater(self):
        self._waterDist += int(getDistanceBetweenTwoPoints(self.getPosition2D(), self._waterLast))
        x, y = list(map(int, self.getPosition2D()))
        if self._waterDist >= 8 or self._waterDist != 0 and not self.isWalking():
            e = Effect(EffectData("ripple_[5]", position=(x, y), animation=Animation(delay=0.08), refPointType=(RefPointType.BOTTOMCENTER), renderingOrder=(y + 1)))
            self._waterDist = 0
        self._waterLast = self.getPosition2D()

    def checkGroundType(self):
        """ Checks our last ground type and compares it to the current one, if not the same, removes old effect """
        changed = False
        if self._lastGroundType != self.groundType:
            changed = True
            if self._lastGroundType > 1:
                if self._lastGroundType in (GroundType.HIGH_GRASS, GroundType.LOW_GRASS):
                    if self.grassEffect:
                        if self.grassEffect.visible:
                            self.grassEffect.hide()
            self._waterDist = 0
        return changed

    def applyEnvironmentEffects(self):
        changed = self.checkGroundType()
        if self.groundType in GroundType.GRASS:
            self.applyGrass()
        elif self.groundType in GroundType.JUMP:
            eventManager.notify("onCharJump", self)
        else:
            if self.groundType in GroundType.WATER:
                self.applyWater()
        if changed:
            if self.renderer.ready:
                self.renderer.setEnvironment()
                self.renderer.setColorValues()
                self.renderer.setAlphaValues()
        self._lastGroundType = self.groundType

    def updateGrassEffectPosition(self):
        return

    def setPosition(self, x, y, z=0, applyEffects=True):
        WorldObject.setPosition(self, x, y, z)
        self.wallHeight, self.groundType = mapContainer.getEnvironmentValuesAtPosition(self.data.map, x, y)
        for child in self.child_objects:
            child.updateFromObject()

    def setPositionNoRender(self, x, y, z, applyEffects=True):
        WorldObject.setPositionNoRender(self, x, y, z)
        self.wallHeight, self.groundType = mapContainer.getEnvironmentValuesAtPosition(self.data.map, x, y)
        for child in self.child_objects:
            child.updateFromObjectNoRender()

    def setRenderPosition(self, interp):
        WorldObject.setRenderPosition(self, interp)
        for child in self.child_objects:
            child.updateFromObjectRender(interp)

    def hide(self, dt=0):
        if self.visible is False:
            return
        WorldObject.hide(self)
        if self.grassEffect:
            if self.grassEffect.visible:
                self.grassEffect.hide()


class Char(BasicCharObject, InterfaceWalking):

    def __init__(self, data, stopAction=CreatureAction.STOP, moveAction=CreatureAction.WALK):
        self.stopAction = stopAction
        self.moveAction = moveAction
        InterfaceWalking.__init__(self)
        BasicCharObject.__init__(self, data)
        self.actions = [
         stopAction]
        self.fadeOutDefer = None
        self.jumping = False
        self.audio = None
        self.chatMessage = None
        self.emoteEffect = None
        if gameSettings.getAlwaysNames():
            self.createNamePlate()
        self.wallHeight, self.groundType = mapContainer.getEnvironmentValuesAtPosition(self.data.map, data.x, data.y)
        self.applyEnvironmentEffects()
        self.resetRenderState()

    def setPosition(self, x, y, z=0, applyEffects=True):
        BasicCharObject.setPosition(self, x, y, z, applyEffects=applyEffects)
        if self.audio:
            self.audio.setPosition(x, y, z)

    def flashLight(self, light='light', color=(255, 255, 255), size=(128, 128)):
        lightController.addCharLight(self, LightData(light, self.getPosition2D(), color, size, "none"))

    def highlight(self):
        """ When the char is overed it's highlighted. """
        WorldObject.highlight(self)
        if not sessionService.isSelected(self):
            if highlightAura.setChar(self):
                highlightAura.forceUnHide()

    def unHighlight(self):
        WorldObject.unHighlight(self)
        highlightAura.removeChar()
        highlightAura.forceHide()

    def selected(self):
        """ When player gets selection """
        selectionAura.setChar(self)
        selectionAura.forceUnHide()

    def deselected(self):
        selectionAura.forceHide()

    def canMove(self):
        """ Tells if the char is allowed to move or not. """
        return self.data.canMove()

    def canAttack(self):
        return self.data.canAttack()

    def canOpenMenu(self):
        """ Tells if the menu can be opened for the char or not. """
        return self.data.canOpenMenu()

    def canBeSelected(self):
        return self.data.canBeSelected()

    def emote(self, name):
        """ Show an emote over the char. """
        if not self.emoteEffect:
            self.emoteEffect = Emote(name, self)
        else:
            self.emoteEffect.updateEmote(name)

    def inFrontPositionRange(self, direction, range):
        nx = math.cos(math.radians(direction)) * range
        ny = math.sin(math.radians(direction)) * range
        return (
         nx, ny)

    def getPositionInFrontMiddle(self, direction, distance, offsetX=0, offsetY=0):
        x, y, z = self.getPositionInFront(direction, distance, offsetX, offsetY)
        return (
         x, y + self.getHeight() / 3.0)

    def getOffsetInFrontMiddle(self, direction, distance, offsetX=0, offsetY=0):
        x, y = self.getOffsetInFront(direction, distance, offsetX, offsetY)
        return (
         x, y + self.getHeight() / 3.0)

    def getPositionTop(self, direction, range):
        x, y, z = self.getPositionInFront(direction, range)
        return (
         x, y)

    def getChatMessage(self):
        """ Return chat message. Create if doesn't exist.
            Moved from creation to speed up loading: Not all characters will use chat."""
        if self.chatMessage is None:
            self.chatMessage = ChatMessage(self)
        return self.chatMessage

    def stopMoving(self):
        if self.isWalking():
            self.stopWalking()

    @property
    def name(self):
        return self.data.name

    def getAction(self):
        return self.actions[0]

    def throw(self, item, x, y):
        """ Makes the character throw item to x, y """
        self.setFacingNear(getAngleBetweenTwoPoints(self.getPosition2D(), (x, y)))
        (item.setPosition)(*self.getPositionInFrontMiddle(self.direction, 0))
        cb = item.throws((x, y))
        return cb

    def playAction(self, action, duration=0):
        """ Difference between setting action and playing is playing will revert to base action.
            Setting action sets base action.
            Duration above 0 will override framedata.
         """
        callback = self._setActionStackable(action)
        if duration == 0:
            if callback:
                callback.addCallback(self._deleteActionCallback, action)
            else:
                if self.renderer.ready:
                    duration = self.renderer.getActionDuration(action) * 1 / 60.0
                pyglet.clock.schedule_once(self.deleteAction, duration, action)
        else:
            pyglet.clock.schedule_once(self.deleteAction, duration, action)
        return callback

    def _deleteActionCallback(self, result, action):
        pyglet.clock.schedule_once(self.deleteAction, 0, action)

    def deleteAction(self, dt, action):
        oldAction = self.getAction()
        if action in self.actions:
            if len(self.actions) > 1:
                self.actions.remove(action)
        else:
            if oldAction != self.getAction():
                self._setAction(oldAction, self.getAction(), True if len(self.actions) > 1 else False)
            assert len(self.actions), f"There are no more actions ! After deleting... {CreatureAction.toString[action]}"

    def setAction(self, action):
        """ Unstackable action, resets action """
        if action == self.getAction():
            return
        self._setAction(self.getAction(), action, False)

    def _setActionStackable(self, action):
        if action == self.getAction():
            return
        else:
            callback = self._setAction(self.getAction(), action, True)
            return callback

    def _setAction(self, oldAction, newAction, stackable=False):
        if oldAction == newAction:
            raise Exception("You can't set the same action two times for a char.")
        elif self.renderer.ready:
            callback = self.renderer.setAction(newAction)
        else:
            callback = None
        if stackable:
            self.actions.insert(0, newAction)
        else:
            self.actions = [
             newAction]
        return callback

    def setFacingNear(self, facing):
        facing = directionService.getNear(facing)
        self.setFacing(facing)

    def setFacing(self, facing):
        if facing != self.getFacing():
            self.data.facing = facing
            if self.renderer.ready:
                self.renderer.setFacing(facing)

    def getFacing(self):
        return self.data.facing

    def idleReaction(self):
        if self.renderer.ready:
            if self.getZ() == 0:
                self.playAction(CreatureAction.IDLE)
            else:
                self.playAction(CreatureAction.FLY, 1)

    def getWalkingSpeed(self):
        if self._following:
            tWalkingSpeed = self.followTarget.getWalkingSpeed()
            if tWalkingSpeed <= self.data.walkingSpeed:
                return tWalkingSpeed - 2
        return self.data.walkingSpeed

    def getIdRange(self):
        return self.data.idRange

    def getCategory(self):
        return self.data.category

    def getId(self):
        return self.data.getId()

    def fadeTo(self, duration, alpha=255.0):
        """ WARNING: This fades EVERYTHING including shadow. Only use for specific cases."""
        self.renderer.fadeTo(duration, alpha)
        for lObject in self.child_objects:
            if not lObject.visible:
                lObject.fadeTo(duration, alpha)

    def fadeIn(self, duration):
        d = self.renderer.fadeIn(duration)
        for lObject in self.child_objects:
            if lObject.visible:
                lObject.fadeIn(duration)

        return d

    def fadeOut(self, duration):
        d = self.renderer.fadeOut(duration)
        d.addCallback(self.hide)
        for lObject in self.child_objects:
            if lObject.visible:
                lObject.fadeOut(duration)

        return d

    def hide(self, dt=0):
        BasicCharObject.hide(self)
        for object in self.child_objects:
            if object.visible:
                object.hide()

    def show(self):
        BasicCharObject.show(self)
        for object in self.child_objects:
            if not object.visible and object.startVisible:
                object.show()

    def changeChar(self, fileId):
        raise exceptions.MustBeImplemented


class NPCWorldObject(Char):
    referencePoint = RefPointType.BOTTOMLEFT
    renderClass = iRender.NPCWorldObjectRender

    def __init__(self, data):
        super().__init__(data)
        self.showDialogStatus()

    def applyEnvironmentEffects(self):
        return


class WildBerryObject(NPCWorldObject):
    referencePoint = RefPointType.BOTTOMCENTER
    renderClass = iRender.NPCBerryObjectRender

    def __init__(self, data):
        super().__init__(data)

    def applyEnvironmentEffects(self):
        return


class Pokemon(Char):
    __doc__ = " Control view of an char. "
    statusEffectObjects: Dict[(int, StatusEffectObject)]
    renderClass = PokemonRender

    def __init__(self, data):
        if data.dexId in alwaysFlying:
            stopAction = CreatureAction.IDLE
        else:
            stopAction = data.action
        Char.__init__(self, data, stopAction=stopAction)
        self.barObject = None
        self.castObject = None
        self.table = None
        self.statusEffectObjects = {}
        for status in StatusEffect.ALL:
            self.statusEffectObjects[status] = None

        self.renderLoadFinished()

    def addEliteIcon(self):
        if not self.table:
            self.table = CharacterIconTable(self)
        self.table.addEliteIcon()

    def showCaptureStatus(self):
        if self.data.flags & WildPkmnFlag.NOCATCH:
            if not self.table:
                self.table = CharacterIconTable(self)
            self.table.addNoCatch()

    def removeCaptureStatus(self):
        if self.table:
            self.table.removeNoCatch()

    def renderLoadFinished(self):
        """ Is  after the renderer is done loading frame info and sprite data necessary for actions.
            Just in case we do async, this can be called after the object is done.
         """
        if self.renderer.ready:
            if self.isFainted():
                self.faint(FaintType.KO)
            else:
                if self.data.dexId in alwaysFlying:
                    self.flying = True
                self.renderer.setAction(self.stopAction)

    def delete(self):
        pyglet.clock.unschedule(self.deleteAction)
        pyglet.clock.unschedule(self._faintEffect)
        pyglet.clock.unschedule(self._emoteLoop)
        super().delete()

    def hide(self, dt=0):
        if self.visible is False:
            return
        else:
            Char.hide(self)
            if idleCharManager.isIdle(self):
                idleCharManager.delete(self)
            if self.barObject:
                self.getBarObject().forceHide()
            if self.castObject:
                self.getCastObject().forceHide()
        pyglet.clock.unschedule(self.deleteAction)
        pyglet.clock.unschedule(self._faintEffect)
        pyglet.clock.unschedule(self._emoteLoop)

    def show(self):
        Char.show(self)
        self.renderLoadFinished()

    @property
    def skillStates(self):
        return self.data.skillStates

    @property
    def damageStates(self):
        return self.data.damageStates

    def throw(self, item, x, y):
        """ Makes the character throw item to x, y """
        self.setFacingNear(getAngleBetweenTwoPoints(self.getPosition2D(), (x, y)))
        self.playAction((CreatureAction.ATK), duration=0.3)
        item.throws((x, y))

    def getHurt(self, duration=0.2, repeat=1):
        """ TODO: Depending on skillId and damageType, shows specific damage animations & effects. """
        self.playAction(CreatureAction.HURT, duration)

    def getAction(self):
        return self.actions[0]

    def revive(self):
        pyglet.clock.unschedule(self._faintEffect)
        pyglet.clock.unschedule(self._emoteLoop)
        if self.emoteEffect:
            if self.emoteEffect.visible:
                self.emoteEffect.hide()
            self.playAction(CreatureAction.SPATK)
            self.setAction(CreatureAction.STOP)
            if self.data.walkMode == WalkMode.FOLLOW:
                trainer = charContainer.getCharByIdIfAny(self.data.trainerId, self.data.trainerIdRange)
                if trainer:
                    if not self.followTarget:
                        self.startFollowing(trainer)
        else:
            sys.stderr.write(f"Warning: Tried to set follow on revive but trainer didn't exist. {self.data.id}, trainer: ({self.data.trainerId}, {self.data.trainerIdRange})\n")

    def faint(self, faintType):
        self.data.stats.hp.current = 0
        statusEffectController.cureAll(self.data)
        self.cureAllStatusEffects()
        if self in sessionService.getClientPokemons():
            self.clearAllOrders()
        if not self.visible:
            return
        self.stopMoving()
        mixerController.playSound("Faint")
        self.delLinkedSkills()
        if faintType == FaintType.KO:
            self.beDead()
        elif faintType == FaintType.AFRAID:
            self.beAfraid()
        elif faintType == FaintType.REFUSE:
            self.beRefusing()
        elif faintType == FaintType.LEAVE:
            self.clippingMode(True)
            self.emote(Emotes.EMBARASSED)
            self.leaveAndDisappear(3, 200)
        else:
            if faintType == FaintType.BLOWN_AWAY:
                self.clippingMode(True)
                self.emote(Emotes.SUPRISED)
                self.leaveAndDisappear(0.6, 200)
        if self.data.isWildPokemon():
            if faintType not in FaintType.MOVING_FAINTS:
                d = self.fadeOut(5)
                d.addCallback(self._removeOnStop)

    def leaveAndDisappear(self, fadetime, distance):
        self.goToRandomDirection(distance)
        d = self.fadeOut(fadetime)

        def cleanUp(result):
            if self.isWalking():
                self.stopWalking()
            self._removeOnStop(None)

        d.addCallback(cleanUp)

    def spawn(self):
        """Plays a spawn effect"""
        self.playAction(CreatureAction.ATK, 0.7)
        Jump(self)
        if self.groundType & GroundType.LOW_GRASS or self.groundType & GroundType.HIGH_GRASS:
            x, y = self.getPosition2D()
            Effect(EffectData("grass_spawn_[4]", position=(
             x, y + self.getHeight() // 2),
              animation=Animation(delay=0.1)))
        elif self.groundType & GroundType.SHALLOW_WATER or self.groundType & GroundType.DEEP_WATER:
            x, y = self.getPosition2D()
            Effect(EffectData("water_spawn_01[5]_(fast)_", position=(
             x, y),
              animation=Animation(delay=(AnimationSpeed.FAST))))
        else:
            x, y = self.getCenter()
            Effect(EffectData("spawn_01", position=(
             x, y),
              animation=Animation(delay=(AnimationSpeed.FAST))))
        if self.data.shiny:
            eventManager.notify("onCharPlayEffect", self, "Shiny")

    def goToRandomDirection(self, range=100):
        x, y, z = self.getPositionInFront(directionService.getRandom(), range)
        self.beginToGoTo(x, y, z)

    def _removeOnStop(self, result):
        """ Remove chars when disappeared. Will only fail to remove if char has been removed due to a map change which is ok."""
        try:
            if self.isWalking():
                self.stopWalking()
            if self.grassEffect:
                if self.grassEffect.visible:
                    self.grassEffect.hide()
            charContainer.delChar(self)
        except Exception:
            pass

    def repeatUntil(self, delay, function, event, predicat):
        """ Repeat <function> until <event> reach and <predicat> return True about <event> """
        return

    def showStatusEffect(self, status, duration):
        effect = self.statusEffectObjects[status]
        if effect is None:
            self.statusEffectObjects[status] = StatusEffectObject(status, self)
        else:
            self.statusEffectObjects[status].startVisible = True
        if self.statusEffectObjects[status].visible == False:
            self.statusEffectObjects[status].show()

    def cureStatusEffect(self, status):
        if self.statusEffectObjects[status]:
            pyglet.clock.unschedule(self.statusEffectObjects[status].hide)
            if self.statusEffectObjects[status].visible:
                self.statusEffectObjects[status].hide()
            self.statusEffectObjects[status].startVisible = False

    def cureAllStatusEffects(self):
        for status in self.statusEffectObjects:
            self.cureStatusEffect(status)

    def _emoteLoop(self, dt, emote):
        self.emote(emote)

    def _faintEffect(self, dt, faintType):
        if faintType == FaintType.AFRAID:
            self.renderer.tremble(1, 2, 0.03)
            self.emote(Emotes.EMBARASSED)
        elif faintType == FaintType.REFUSE:
            self.playAction(CreatureAction.SPATK, 0.7)
            self.renderer.pulse(1, 0.2, 1.1)
            self.emote(Emotes.DISAGREE)
        elif faintType == FaintType.KO:
            self.emote(Emotes.DEAD)

    def beDead(self):
        self.setAction(CreatureAction.DEAD)
        self._faintEffect(0, FaintType.KO)
        pyglet.clock.schedule_interval(self._faintEffect, 4, FaintType.KO)

    def beAfraid(self):
        self.setAction(CreatureAction.IDLE)
        self._faintEffect(0, FaintType.AFRAID)
        pyglet.clock.schedule_interval(self._faintEffect, 4, FaintType.AFRAID)

    def beRefusing(self):
        self.setAction(CreatureAction.IDLE)
        self._faintEffect(0, FaintType.REFUSE)
        pyglet.clock.schedule_interval(self._faintEffect, 3, FaintType.REFUSE)

    def updateHpBar(self):
        self.getBarObject().updateHp(self.getHpPer())

    def setHpPer(self, per):
        self.getBarObject().updateHp(per)

    def getHpPer(self):
        mi, ma = self.data.stats.hp.values
        return float(mi) / float(ma)

    def setHp(self, amount):
        self.data.stats.hp.current = amount
        if self.isReleased():
            self.setHpPer(self.getHpPer())

    def getCastObject(self):
        if not self.castObject:
            self.castObject = CastBar(self)
        return self.castObject

    def getBarObject(self):
        if not self.barObject:
            self.barObject = HpBar(self)
        return self.barObject

    def hasTrainer(self):
        return self.data.hasTrainer()

    def isReleased(self):
        return self.data.isReleased()

    def setReleased(self, value):
        self.data.setReleased(value)

    def changeChar(self, dexId):
        self.data.dexId = dexId
        self.renderer.changeSprites()

    def isFainted(self):
        return self.data.isFainted()

    def evolve(self, dexId):
        if self.data.evolving:
            raise Exception("The char is already evolving ! Trying to evolve again?!")
        else:
            if sessionService.isClientChar(self):
                eventManager.notify("onHideGui")
            else:
                backToFollow = False
                if self.isWalking():
                    self.stopWalking()
                if self.data.walkMode == WalkMode.FOLLOW:
                    backToFollow = True
                    self.data.walkMode = WalkMode.FREE
            self.data.evolving = True
            self.setAction(CreatureAction.IDLE)
            if self.renderer.ready:
                self.renderer.enableWhite()
                self.renderer.setEvolveState()
                reactor.callLater(2, self.renderer.pulse, 16, 0.5, 1.2)
        self.emote(Emotes.SUPRISED)
        x, y = self.getProjection2D()
        effectsToTerminate = []

        def s0():
            random_direction = [
             0, 45, 90, 135, 180, 225, 270, 315]
            default_y = y + self.getHeight() / 2
            for i in range(8):
                new_x, new_y = getPositionOnDirection((x, default_y), random_direction[i], random.randint(20, 50))
                e2 = Effect(EffectData("ball_bright_[4]", position=(new_x, new_y), animation=Animation(delay=0.1, duration=0)))
                e2.moveTo(random.uniform(0.5, 1.5), x, default_y, "repeat")
                effectsToTerminate.append(e2)

        def s1():
            e = Effect(EffectData("evolutionShine_[6]"))
            e.setPosition(x, y + self.getHeight() / 2)
            e.setAlpha(254)
            e.renderer.pulse(6, 1)
            reactor.callLater(6.1, e.renderer.flash, 0.5)

        def s2():
            if self.renderer.ready:
                self.setAction(CreatureAction.STOP)
                self.changeChar(dexId)
                self.renderer.disableWhite()
                self.renderer.setNormalAlpha()
            for effect in effectsToTerminate:
                effect.renderer.stop()
                if effect.visible:
                    effect.delete()

        def s3():
            self.data.evolving = False
            if sessionService.isClientChar(self):
                eventManager.notify("onShowGui")
            if backToFollow:
                self.data.walkMode = WalkMode.FOLLOW
                if not sessionService.isSelected(self):
                    self.walkToTarget()

        reactor.callLater(1, s0)
        reactor.callLater(4, s1)
        reactor.callLater(10.1, s2)
        reactor.callLater(10.8, s3)

    def fadeOut(self, duration):
        d = Char.fadeOut(self, duration)
        if idleCharManager.isIdle(self):
            idleCharManager.delete(self)
        return d

    def release(self):
        """ What happen visibly on the pokemon when it gets released. """
        if self.visible:
            raise Exception("Trying to release visible pokemon !")
        else:
            if not self.isReleased():
                print("====NOT RELEASED")
                return
            else:
                self.show()
                if self.renderer.ready:
                    self.renderer.setRGBA(255, 145, 145, 0)
                    self.renderer.setScale(1.0)
                e = Effect(EffectData("rosecircle", position=(self.getPosition2D())))
                e.setAlpha(210)
                e.setSize(50, 50)
                end = e.flash(0.8, 2.0)
                if self.renderer.ready:
                    end += AnimCallable(self.renderer.setRGBA, 255, 255, 255, 255)
                    if self.data.shiny:

                        def shinyCheck():
                            eventManager.notify("onCharPlayEffect", self, "Shiny")

                        end += AnimCallable(shinyCheck)
            self.applyEnvironmentEffects()
            if self.renderer.ready:
                self.renderer.fadeIn()

    def recall(self, source=None):
        """ What happen visibly on the pokemon when it gets recalled.
            If a source is specified, effect will move towards source.
        """
        if not self.visible:
            raise Exception("Trying to recall hidden pokemon !")
        else:
            pyglet.clock.unschedule(self._faintEffect)
            pyglet.clock.unschedule(self._emoteLoop)
            self.stopMoving()
            self.clearAllOrders()
            if self.grassEffect:
                if self.grassEffect.visible:
                    self.grassEffect.hide()
            if self.renderer.ready:
                self.renderer.setColor(255, 145, 145)
                self.renderer.shrink(scale=0.2, duration=0.7, reset=False)
            d = self.fadeOut(1)
            x, y = self.getProjection2D()
            e = Effect(EffectData("rosecircle", position=(x, y + self.getHeight() // 2), renderingOrder=(self.getProjection2D()[1] + 1)))
            e.setAlpha(240)
            e.flash(0.8, 0.1)
            self.data.skillStates.wipe()
            self.data.damageStates.wipe()
            if source:
                (e.moveTo)(*(0.7, ), *source.getPosition2D())
                (self.renderer.moveTo)(*(0.7, ), *source.getPosition2D())
        return d

    def _getFollowSettings(self):
        return (
         self.data.distanceFromTrainer, self.data.angleFromTrainer)

    def _checkIdle(self, lastAction, newAction):
        if lastAction in (CreatureAction.STOP, CreatureAction.IDLE_FLYING, CreatureAction.IDLE):
            if idleCharManager.isIdle(self):
                idleCharManager.delete(self)
        if newAction == CreatureAction.STOP or newAction == CreatureAction.IDLE_FLYING:
            if not idleCharManager.isIdle(self):
                idleCharManager.add(self)

    def _setAction(self, oldAction, newAction, stackable=False):
        action = Char._setAction(self, oldAction, newAction, stackable)
        self._checkIdle(oldAction, newAction)
        return action

    def cancelAction(self):
        """ Cancels an action early """
        pyglet.clock.unschedule(self.deleteAction)
        if len(self.actions) > 1:
            self.deleteAction(None, self.getAction())

    def playAction(self, action, duration=0):
        self.renderer.playAction(duration)
        return Char.playAction(self, action, duration=duration)

    def playActionWithDelay(self, action, duration=0, delay=0.5):
        """ Play an action x times. """

        def delayedAction(dt, action, duration):
            if self.visible:
                self.playAction(action, duration)

        pyglet.clock.schedule_once(delayedAction, delay, action, duration)

    def __repr__(self):
        return f"Pokemon(id={self.data.id}, name={self.data.name}, dexId={self.data.dexId})"


class PCTrainer(Char):
    __doc__ = " Control view of an char. "
    renderClass = client.render.world.trainer.NPCTrainerRender

    def __init__(self, data):
        Char.__init__(self, data, stopAction=(PlayerAction.IDLE))

    def canMove(self):
        """ Tells if the char is allowed to move or not. """
        return True

    def canAttack(self):
        return True

    def canOpenMenu(self):
        """ Tells if the menu can be opened for the char or not. """
        return True

    def canBeSelected(self):
        return True


class NewPCTrainer(Char):
    renderClass = client.render.world.trainer.PlayerTrainerRender

    def __init__(self, data):
        Char.__init__(self, data, stopAction=(PlayerAction.STOP), moveAction=(PlayerAction.WALK))
        self.table = None
        self.renderer._updatePosition()

    def __repr__(self):
        return f"PlayerTrainer(id={self.data.id}, name={self.data.name})"

    def updateWatched(self, distance):
        if not self.table:
            self.table = CharacterIconTable(self)
        self.table.updateWatched(distance)

    def throw(self, item, x, y):
        """ Makes the character throw item to x, y """
        self.setFacingNear(getAngleBetweenTwoPoints(self.getPosition2D(), (x, y)))
        if self.groundType not in GroundType.WATER:
            self.playAction(PlayerAction.THROW, 0.3)
        (item.setPosition)(*self.getPositionInFrontMiddle(self.direction, 0))
        cb = item.throws((x, y))
        return cb

    def applyWater(self):
        if self.stopAction != PlayerAction.STOP_SWIM:
            self.stopAction = PlayerAction.STOP_SWIM
            self.moveAction = PlayerAction.SWIMMING
            if self.isWalking():
                self.setAction(self.moveAction)
            else:
                self.setAction(self.stopAction)
        Char.applyWater(self)

    def applyEnvironmentEffects(self):
        if self.renderer.ready:
            changed = self.checkGroundType()
            if self.groundType in GroundType.GRASS:
                self.applyGrass()
            elif self.groundType in GroundType.JUMP:
                eventManager.notify("onCharJump", self)
        elif self.groundType in GroundType.WATER:
            self.applyWater()
        else:
            if self.groundType not in GroundType.WATER:
                if self.stopAction != PlayerAction.STOP:
                    self.stopAction = PlayerAction.STOP
                    self.moveAction = PlayerAction.WALK
                    if self.isWalking():
                        self.setAction(self.moveAction)
                    else:
                        self.setAction(self.stopAction)
        if changed:
            self.renderer.setEnvironment()
            self.renderer.setColorValues()
            self.renderer.setAlphaValues()
            self.renderer.applyEnvironment()
        self._lastGroundType = self.groundType

    def canMove(self):
        """ Tells if the char is allowed to move or not. """
        return True

    def canAttack(self):
        return True

    def canOpenMenu(self):
        """ Tells if the menu can be opened for the char or not. """
        return True

    def canBeSelected(self):
        return True


class NPCTrainer(PCTrainer):

    def __init__(self, data):
        super().__init__(data)
        self.showDialogStatus()


class NPCPokemon(Pokemon):

    def __init__(self, data):
        super().__init__(data)
        self.showDialogStatus()

    def __repr__(self):
        return f"NPCPokemon(id={self.data.id}, name={self.data.name}, dexId={self.data.dexId})"


class NPCBattlePokemon(Pokemon):

    def __init__(self, data):
        super().__init__(data)
        self.showDialogStatus()

    def __repr__(self):
        return f"NPCBattlePokemon(id={self.data.id}, name={self.data.name}, dexId={self.data.dexId})"


class PCPokemon(Pokemon):

    def __repr__(self):
        return f"PCPokemon(id={self.data.id}, name={self.data.name}, dexId={self.data.dexId})"
