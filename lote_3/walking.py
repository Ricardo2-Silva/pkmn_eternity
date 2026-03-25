# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\world\action\walking.py
import math, random, time, traceback, pyglet
from twisted.internet import defer
from twisted.python import log
import client.data.exceptions as exceptions
from client.control.events import eventManager
from client.control.events.event import eventDispatcher
from client.control.events.world import worldInputManager
from client.control.net.sending import packetManager
from client.control.service.session import sessionService
from client.control.system.sound import mixerController
from client.control.world.action.pathfinding import PathFinding
from client.data.container.char import charContainer
from client.data.container.map import mapContainer
from client.interface.area import areaDisplay
from shared.container.constants import IdRange, WalkMode, GroundType, CharCategory, WildPkmnFlag
from shared.container.geometry import Rect, createQuadRotated
from shared.container.net import cmsg as clientMessages
from shared.controller.maths.maths import interpolate
from shared.service.direction import directionService
from shared.service.geometry import getAngleBetweenTwoPoints, getDistanceBetweenTwoPoints
from shared.service.ticks import UpdateTicks
UPDATES_PER_SEC = 5
UPDATE_SYNC = 1.0 / UPDATES_PER_SEC
from math import sqrt

def minDistance(A, B, E):
    AB = [
     None, None]
    AB[0] = B[0] - A[0]
    AB[1] = B[1] - A[1]
    BE = [
     None, None]
    BE[0] = E[0] - B[0]
    BE[1] = E[1] - B[1]
    AE = [
     None, None]
    AE[0] = E[0] - A[0]
    AE[1] = E[1] - A[1]
    AB_BE = AB[0] * BE[0] + AB[1] * BE[1]
    AB_AE = AB[0] * AE[0] + AB[1] * AE[1]
    reqAns = 0
    if AB_BE > 0:
        y = E[1] - B[1]
        x = E[0] - B[0]
        reqAns = sqrt(x * x + y * y)
    elif AB_AE < 0:
        y = E[1] - A[1]
        x = E[0] - A[0]
        reqAns = sqrt(x * x + y * y)
    else:
        x1 = AB[0]
        y1 = AB[1]
        x2 = AE[0]
        y2 = AE[1]
        mod = sqrt(x1 * x1 + y1 * y1)
        reqAns = abs(x1 * y2 - y1 * x2) / mod
    return reqAns


class AreaChanger:

    def __init__(self):
        self.areas = None
        self.current_area = None
        self._last_time = time.time()
        self.min_transition = 2
        eventManager.registerListener(self)

    def reset(self):
        self.areas = None
        self.current_area = None
        self._last_time = time.time()
        areaDisplay.reset()

    def onBattleEnd(self):
        if self.current_area:
            filename = self.getMusic()
            if filename:
                mixerController.playMusic(filename)

    def getMusic(self):
        bgmList = self.current_area.getLoopBGM(True)
        if bgmList or self.areas:
            bgmList = []
            for area in self.areas:
                bgmList = area.getLoopBGM(True)

            bgmList or log.msg(f"Could not find suitable BGM music for current map: {sessionService.getClientData().map.information.name}")
            return
        else:
            return random.choice(bgmList).fileName

    def _distanceToRect(self, x, y, rect):
        dx = max(rect.left - x, 0, x - rect.right)
        dy = max(rect.bottom - y, 0, y - rect.top)
        return math.sqrt(dx * dx + dy * dy)

    def update(self, dt):
        position = sessionService.getClientData().getPosition()
        self.areas = (mapContainer.getAreasAtPosition)(sessionService.getClientData().map, *position)
        if self.areas:
            self.areas.sort(key=(lambda x: x.getHeight()))
            if self.areas[0] != self.current_area:
                if time.time() - self._last_time >= self.min_transition:
                    self.current_area = self.areas[0]
                    self._last_time = time.time()
                    filename = self.getMusic()
                    if filename:
                        if not mixerController.battleMusic:
                            mixerController.playMusic(filename)
                        areaDisplay.set_area(self.current_area)
        trainer_pos = sessionService.battle.isActive() or sessionService.getClientTrainer().getPosition2D()
        pokemon_around = (charContainer.getAllWildPokemonInArea)(*trainer_pos, *(300,
                                                                                 300))
        if pokemon_around:
            dist = 999
            for pokemon in pokemon_around:
                if pokemon.data.flags & WildPkmnFlag.AGGROS:
                    facing = pokemon.getFacing()
                    quad = createQuadRotated(*pokemon.getPosition2D(), *(50, 100, facing))
                    dist = min(dist, (self._distanceToRect)(*trainer_pos, *(quad,)))

            if dist != 999:
                char = sessionService.getClientTrainer()
                char.updateWatched(dist)
        else:
            char = sessionService.getClientTrainer()
            if char.table:
                char.table.hideWatched()
            else:
                char = sessionService.getClientTrainer()
        if char.table:
            char.table.hideWatched()


areaChange = AreaChanger()

class OutOfView(UpdateTicks):

    def __init__(self):
        return

    def isOnMap(self, char):
        if char.visible:
            if not char.renderer.fading:
                return True
        return False

    @staticmethod
    def setOutOfView(char):
        if char.visible:
            if not char.renderer.fading:
                char.fadeOut(0.3)
                if char.getIdRange() == IdRange.PC_TRAINER:
                    pokemons = charContainer.getCharsByTrainerId(char.getId(), char.getIdRange())
                    for pokemon in pokemons:
                        if pokemon.visible and pokemon.isReleased():
                            pokemon.fadeOut(0.3)

    @staticmethod
    def setInView(char):
        if not char.visible:
            if char.getIdRange() in IdRange.POKEMON:
                if not char.isReleased():
                    return
            char.fadeIn(1)


outOfViewManager = OutOfView()

class WalkerPositionManager:
    __doc__ = " Update the position of all moving players every 0.05s. "

    def __init__(self):
        self.walkers = []
        self.interp = 0
        self._next_dt = 0
        self.last = time.time()
        self.stopped_finish = []
        self.to_run = []
        eventManager.registerListener(self)

    def reset(self):
        self.walkers.clear()
        self.stopped_finish.clear()
        self.to_run.clear()

    def onClientTrainerLoaded(self):
        return

    def onBeforeMapLoad(self):
        self.walkers.clear()
        self.stopped_finish.clear()
        self.to_run.clear()

    def add(self, character, delay=False):
        if character in self.stopped_finish:
            self.stopped_finish.remove(character)
        if not delay:
            self.walkers.append(character)
        elif character not in self.to_run:

            def addClient():
                sessionService.lastMoveSend = time.time()
                self.walkers.append(character)

            self.to_run.append(addClient)

    def delete(self, character):
        if character in self.walkers:
            self.walkers.remove(character)
        else:
            self.to_run.clear()
        if character not in self.stopped_finish:
            self.stopped_finish.append(character)

    def update(self, dt):
        for walker in self.stopped_finish:
            (walker.setPosition)(*walker.getPosition())

        self.stopped_finish.clear()
        for walker in self.walkers:
            walker.step(dt)

        while self.to_run:
            func = self.to_run.pop(0)
            func()

    def draw(self, interp):
        for walker in self.walkers:
            walker.setRenderPosition(interp)

        for walker in self.stopped_finish:
            walker.setRenderPosition(interp)


walkerPositionManager = WalkerPositionManager()
default_radian_dir = math.radians(270)

class InterfaceWalking(object):
    __doc__ = " All objects that implement this interface can Walk.\n\n        Required Methods:   - setAction(action).\n                            - setFacing(Direction)\n                            - _getFollowSettings()\n    "

    def __init__(self):
        self._direction = 270
        self._directionRadians = default_radian_dir
        self._walkingInDirection = False
        self._speedBonus = 0
        self._positionToGo = []
        self._targetToFollow = None
        self._followers = []
        self._following = False
        self._waitingForTargetToBeFar = False
        self._hasAlteredDirection = False
        self._originalDirection = None
        self.keyedDirection = None
        self._clipping = False
        self._can_stop = True
        self._forced_update = False
        self._blockedFollowPos = False
        self._lastPos = (0, 0)
        self._walkingNum = 0
        self._walkingOrder = {}
        self._steps = 0
        self._lastSendPos = (0, 0)
        self.onBridge = False
        self.event = None
        self._start_time = None
        self._total_distance = 0

    def getWalkOrderNum(self):
        return self._walkingNum

    def getWalkOrder(self, orderNum):
        if orderNum in self._walkingOrder:
            return self._walkingOrder[orderNum]
        else:
            return

    def setLastPos(self, pos):
        self._lastSendPos = pos

    def setWalkOrderNumber(self, number):
        self._walkingNum = number

    def increaseWalkOrder(self, pos):
        num = self.getWalkOrderNum()
        self._walkingOrder[num] = pos
        self._walkingNum = (num + 1) % 255
        self._lastSendPos = pos

    def removeOrderNum(self, num):
        del self._walkingOrder[num]

    def clearAllOrders(self):
        self._walkingNum = 0
        self._walkingOrder.clear()

    def resetWalkingOrder(self):
        self._walkingOrder.clear()

    def resetWalkingOrderNum(self):
        self._walkingNum = 0

    def setStunDuration(self, duration):
        if duration > 0:
            if self.isWalking():
                self.stopWalking()
            self.data.setStunDuration(duration, worldInputManager.attemptAutoMove if self == sessionService.getSelectedChar() else None)

    def isWaitingForTargetToBeFar(self):
        return self._waitingForTargetToBeFar

    def waitsForTargetToBeFar(self):
        if self.isWaitingForTargetToBeFar():
            raise Exception("The char waits for the target to be Far already.")
        self._waitingForTargetToBeFar = True
        self.setAction(self.stopAction)

    def stopWaitingForTargetToBeFar(self):
        if not self.isWaitingForTargetToBeFar():
            raise Exception("The char waits for the target to be Far already.")
        self._waitingForTargetToBeFar = False
        self.setAction(self.moveAction)

    @property
    def followTarget(self):
        return self._targetToFollow

    @followTarget.setter
    def followTarget(self, char):
        if char:
            if self._targetToFollow == char:
                raise Exception("The walker already follow this target.")
            char._followers.append(self)
        else:
            if self._targetToFollow is None:
                raise Exception("The walker already doesn't have a target.")
            self._targetToFollow._followers.remove(self)
        self._targetToFollow = char

    def beginToGoTo(self, x, y, z):
        self._positionToGo.append((x, y, z))
        if not self.isWalking():
            self.beginToWalk()

    def stopGoto(self, x, y):
        self._positionToGo.append((x, y))
        if not self.isWalking():
            self.beginToWalk()

    def _getFollowSettings(self):
        raise exceptions.MustBeImplemented()

    def canWalk(self):
        return True

    def beginToWalk(self, delay=False):
        if self.isWalking():
            raise Exception("Walker already moves. Can not begin to move.")
        self._speedBonus = 0
        self._walkingInDirection = True
        self.setAction(self.moveAction)
        walkerPositionManager.add(self, delay)
        for follower in self._followers:
            if follower.visible:
                follower.isWalking() or follower.walkToTarget()

    def stopWalking(self):
        if not self.isWalking():
            if not self._following:
                raise Exception("Walker already doesn't move. Can not stop moving.", self.data.name)
        self.setAction(self.stopAction)
        walkerPositionManager.delete(self)
        self._walkingInDirection = False
        self._hasAlteredDirection = False
        self.keyedDirection = None
        self._following = False
        self._can_stop = True
        self._positionToGo.clear()
        self.applyEnvironmentEffects()
        if self.event:
            self.event.callback(None)
            self.event = None

    def clippingMode(self, modeBool):
        self._clipping = modeBool

    def isWalking(self):
        return self._walkingInDirection

    def startFollowing(self, target):
        if self.canMove():
            self.data.walkMode = WalkMode.FOLLOW
            assert self.followTarget != target, f"{self.data.name} is already following target: {target.data.name} FollowTarget: {self.followTarget.data.name}."
            self.followTarget = target
            print("BEGIN WALK TO TARGET. CHAR IS NOT FOLLOWING:", self.data.name)
            self.walkToTarget()
            if self in sessionService.getClientPokemons():
                if target == sessionService.trainer:
                    if sessionService.getSelectedChar() == self:
                        if not sessionService.getSelectedChar() == sessionService.trainer:
                            print("-------- FORCING TRAINER?")
                            eventDispatcher.dispatch_event("onCharSelection", sessionService.trainer)
        else:
            print("CANT FOLLOW")
        print("-END FOLLOWING")

    def walkToTarget(self):
        """ This function is just the movement part of the follow process. Use this separately to force char to walk.
            Assumes target is already set. """
        if not self._targetToFollow:
            raise AssertionError("Char has no target.")
        else:
            assert self._following is False, "Already following."
            self._following = True
            if not self.isWalking():
                self.beginToWalk()

    def stopFollow(self):
        print("STOP FOLLOWING CALL - STOP WALKING AND SET FOLLOW TARGET NONE")
        self.data.walkMode = WalkMode.FREE
        self.followTarget = None
        if self.isWalking():
            self.stopWalking()

    def getTotalWalkingSpeed(self):
        """ return walking speed + bonus """
        return self.getWalkingSpeed() + self._speedBonus

    def _calcBonusSpeed(self):
        if not self._following:
            raise Exception("Trying to calculate Bonus speed of a walker not following.")
        if self._speedBonus != 0:
            raise Exception("It already have a bonus speed !")
        self._speedBonus = self._targetToFollow.getWalkingSpeed() - self.getWalkingSpeed() + 5

    def isGoingToPosition(self):
        return bool(self._positionToGo)

    def _move(self, direction, toX, toY):
        """ Moves the player one direction, to be used on both axi to prevent diagonal sticking. """
        x, y, z = self.getPosition()
        if self.canMoveOnPosition(direction, x, y, x + toX, y + toY):
            return True
        else:
            return False

    def _checkDirectionWalkable(self, direction, x, y):
        if math.isclose(x, 0, abs_tol=0.001) or not self._move(direction, x, 0):
            x = 0
        else:
            if math.isclose(y, 0, abs_tol=0.001) or not self._move(direction, 0, y):
                y = 0
            if math.isclose(x, 0, abs_tol=0.001) and math.isclose(y, 0, abs_tol=0.001) or not self._move(direction, x, y):
                y = 0
                x = 0
        return (
         x, y)

    def _stepClientParse error at or near `COME_FROM' instruction at offset 274_2

    def _step(self, dt):
        """Steps to a position. Used for non directly player controlled."""
        if self.getFacing() != self.direction:
            self.setFacingNear(self.direction)
        x, y, z = self.getPosition()
        distance = self._calcDistance(dt)
        tX = math.cos(self._directionRadians) * distance
        tY = math.sin(self._directionRadians) * distance
        self.setPosition(x + tX, y + tY, 0)

    def _checkStep(self, distance, dt):
        """
        Determines if we should send an update packet to server.
        :type distance: float
        :type t: float
        """
        if sessionService.isSelected(self):
            self._steps += 1
            if self._steps >= 10 or self._forced_update:
                packetManager.queueSend(clientMessages.PosAndDir, self.data, self.getWalkOrderNum(), self.getFacing())
                sessionService.lastMoveSend = time.time()
                self.increaseWalkOrder(self.getPosition2D())
                self._steps = 0
                if self._forced_update:
                    self._forced_update = False

    def _directionPacket(self, angle):
        if sessionService.isSelected(self):
            if not self.isGoingToPosition():

                def trash():
                    timed = time.time()
                    packetManager.queueSend(clientMessages.PosAndDir, self.data, self.getWalkOrderNum(), angle)
                    sessionService.lastMoveSend = timed
                    self.increaseWalkOrder(self.getPosition2D())
                    self._steps = 0

                walkerPositionManager.to_run.append(trash)

    def stopPacket(self):
        if sessionService.isSelected(self):
            if sessionService.startMovePosition == self.getPosition2D():
                sessionService.startMovePosition = None
                return
            sessionService.startMovePosition = None
            if not self._can_stop:
                return
            timed = time.time()
            packetManager.queueSend(clientMessages.StopAndDir, self.data, self.getWalkOrderNum(), self.getFacing())
            sessionService.lastMoveSend = timed
            self.increaseWalkOrder(self.getPosition2D())
            self._steps = 0

    def _getAllowedGroundTypes(self, direction):
        groundTypes = GroundType.GROUND_WALKABLE
        if sessionService.isClientChar(self):
            if direction == directionService.DOWN:
                groundTypes |= GroundType.DOWN_ONLY
            elif direction == directionService.LEFT:
                groundTypes |= GroundType.LEFT_ONLY
        elif direction == directionService.RIGHT:
            groundTypes |= GroundType.RIGHT_ONLY
        elif sessionService.canSwim():
            groundTypes |= GroundType.ALL_WATER
        else:
            groundTypes |= GroundType.DOWN_ONLY | GroundType.LEFT_ONLY | GroundType.RIGHT_ONLY | GroundType.ALL_WATER
        return groundTypes

    def _checkSpecialGrounds(self, direction, x, y):
        wallHeight, groundType = mapContainer.getEnvironmentValuesAtPosition(self.data.map, x, y, 19)
        if self.onBridge:
            if wallHeight == -1:
                self.onBridge = False
        else:
            if wallHeight == -2:
                self.onBridge = True
            if sessionService.isSelected(self):
                if direction == directionService.DOWN and groundType & GroundType.DOWN_ONLY:
                    self._can_stop = False
        if direction == directionService.LEFT:
            if groundType & GroundType.LEFT_ONLY:
                self._can_stop = False
            if direction == directionService.RIGHT and groundType & GroundType.RIGHT_ONLY:
                self._can_stop = False
        else:
            if self._can_stop == False:
                self._can_stop = True
                self._forced_update = True
        return self._forced_update

    def canMoveOnPosition(self, direction, x, y, tx, ty, z=0):
        if not mapContainer.positionInBounds(tx, ty):
            return False
        else:
            allowedGroundTypes = self._getAllowedGroundTypes(direction)
            if charContainer.getAllCollidingObjects(tx, ty, 8, 8):
                return False
            if self.data.walkMode == WalkMode.FREE or self.data.walkMode == WalkMode.FOLLOW and sessionService.isSelected(self):
                if sessionService.isClientChar(self):
                    moverPath = mapContainer.charIsPathWalkable(self, (
                     x, y),
                      (
                     tx, ty),
                      allowedWallHeight=(self.getZ()),
                      allowedGroundTypes=allowedGroundTypes,
                      radius=19)
                    if moverPath:
                        return True
                    else:
                        return False
                else:
                    if mapContainer.charIsPathWalkable(self, (
                     x, y),
                      (
                     tx, ty),
                      allowedWallHeight=(self.getZ()),
                      allowedGroundTypes=allowedGroundTypes,
                      radius=19):
                        return True
                    else:
                        return False
            else:
                return False

    def _calcDistance(self, dt):
        """ Calculate how much pixels for dt time. """
        return self.getTotalWalkingSpeed() * dt

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, angle):
        self._direction = angle
        self._directionRadians = math.radians(angle)
        self.setFacingNear(angle)

    def setFollowPosition(self):
        """ Forces to the stopped follow position without walking."""
        x, y = self._getFollowPosition()
        self.setPosition(x, y, self.getZ())

    def _getFollowPosition(self):
        if not self._targetToFollow:
            raise Exception("Impossible to get the following position if no target.")
        target = self._targetToFollow
        distanceFromTarget, followAngle = self._getFollowSettings()
        x, y = target.getPosition2D()
        x += distanceFromTarget * math.cos(math.radians(target.direction + 180 + followAngle))
        y += distanceFromTarget * math.sin(math.radians(target.direction + 180 + followAngle))
        return (
         int(x), int(y))

    def _stepToPosition(self, dt):
        """ Step to reach the positionToGo. """
        distance = getDistanceBetweenTwoPoints(self.getPosition2D(), self._positionToGo[0][:2])
        if self.getPosition() == self._positionToGo[0] or distance <= self._calcDistance(dt):
            pos = self._positionToGo.pop(0)
            if not self._positionToGo:
                if self.isWalking():
                    self.stopWalking()
                else:
                    if self.followTarget:
                        self.walkToTarget()
                    if sessionService.isClientTrainer(self):
                        self.clearAllOrders()
                return
        angle = getAngleBetweenTwoPoints(self.getPosition2D(), self._positionToGo[0][:2])
        if self.direction != angle:
            self.direction = angle
        self._step(dt)

    def _stepToFollowPosition(self, dt):
        position = self._getFollowPosition()
        distance = getDistanceBetweenTwoPoints(self.getPosition2D(), position)
        if distance <= self._calcDistance(dt):
            x, y = position
            self.setPosition(x, y, self.getZ())
            self._speedBonus = 0
            if self._targetToFollow.isWalking():
                if self.isWaitingForTargetToBeFar():
                    return
                self.waitsForTargetToBeFar()
            else:
                if self.isWaitingForTargetToBeFar():
                    self.stopWaitingForTargetToBeFar()
                self.stopWalking()
        else:
            angle = getAngleBetweenTwoPoints(self.getPosition2D(), position)
            self.direction = angle
            if self.isWaitingForTargetToBeFar():
                self.stopWaitingForTargetToBeFar()
            if distance > 50:
                if self._speedBonus == 0:
                    self._calcBonusSpeed()
                self._step(dt)

    def step(self, dt):
        """ move for a step. """
        if not self.data.canMove():
            if self._clipping == False:
                self.stopWalking()
        if self.isGoingToPosition():
            self._stepToPosition(dt)
        elif self._following:
            self._stepToFollowPosition(dt)
        else:
            self._stepClient(dt)
        self.applyEnvironmentEffects()


class WalkingCharsController:
    __doc__ = " Get events from eventManager about movement, and make chars moving. "

    def __init__(self):
        eventManager.registerListener(self)
        self.movementTime = time.time()

    def onClientCharWarp(self, char, mapId, mapx, mapy):
        char.clearAllOrders()

    def onMovingKeyDown(self, key):
        if sessionService.waiting:
            return
        else:
            char = sessionService.getSelectedChar()
            if char:
                if not char.canMove() or char.isGoingToPosition():
                    return
            direction = worldInputManager.getDirectionFromKeyDown(key)
            char.keyedDirection = direction
            if not char._can_stop:
                return
            changed_dir = char.direction != direction
            if changed_dir:
                char.direction = direction
            if char.isWalking():
                if char.followTarget:
                    char.stopWalking()
        if not char.isWalking():
            currentTime = time.time()
            if sessionService.startMovePosition == char.getPosition2D():
                if not changed_dir:
                    return
                packetManager.queueSend(clientMessages.PosAndDir, char.data, char.getWalkOrderNum(), direction)
                sessionService.lastMoveSend = time.time()
                char.increaseWalkOrder(char.data.getPosition())
                char._steps = 0
                char.beginToWalk(True)
                sessionService.startMovePosition = char.getPosition2D()
        if changed_dir:
            char._directionPacket(direction)

    def _stopWalking(self, char, packet=True):
        if char.isWalking():
            char.stopWalking()
            if packet:
                walkerPositionManager.to_run.append(char.stopPacket)

    def onMoveForceStop(self, sendPacket):
        char = sessionService.getSelectedChar()
        if char:
            if char.isWalking():
                char.stopWalking()
                if sendPacket:
                    walkerPositionManager.to_run.clear()
                    char.stopPacket()

    def onMovingKeyUp(self, key):
        if sessionService.waiting:
            return
        else:
            char = sessionService.getSelectedChar()
            if char:
                if not char.canMove() or char.isGoingToPosition():
                    return
            direction = worldInputManager.getDirectionFromKeyUp(key)
            char.keyedDirection = direction
            if direction is None:
                if char._can_stop:
                    self._stopWalking(char)
            elif not char._can_stop:
                return
        if char.direction != direction:

            def changeDir():
                char.direction = direction
                packetManager.queueSend(clientMessages.PosAndDir, char.data, char.getWalkOrderNum(), direction)
                sessionService.lastMoveSend = time.time()
                char.increaseWalkOrder(char.getPosition2D())
                char._steps = 0

            walkerPositionManager.to_run.append(changeDir)

    def getOffset(self, currentPos, serverPos):
        x, y = currentPos
        x1, y1 = serverPos
        return [
         x - x1, y - y1]

    def onServerSaysCharMove(self, char, orderNum, position, direction):
        if sessionService.isClientChar(char):
            processPos = char.getWalkOrder(orderNum)
            if processPos:
                char.removeOrderNum(orderNum)
                if position != processPos:
                    print("********CORRECTION MOVEMENT:", position, "PROCESS POS", processPos, "ORDER NUM", orderNum)
                    (char.setPosition)(*position)
                    char.setWalkOrderNumber(orderNum)
                    char.setLastPos(position)
                    print("MOVE TO CORRECT POS", char.getPosition2D())
                else:
                    print("WALK ORDER DOES NOT EXIST")
                return
            if not char.visible:
                if not char.fading:
                    outOfViewManager.setInView(char)
        else:
            if char.getPosition2D() == position:
                if char.direction != direction:
                    char.direction = direction
            if char.followTarget:
                char.stopFollow()
        (char.beginToGoTo)(*position, *(char.z,))

    def onServerSaysCharStop(self, char, orderNum, position, direction):
        if sessionService.isClientChar(char):
            processPos = char.getWalkOrder(orderNum)
            if processPos:
                char.removeOrderNum(orderNum)
                if position != processPos:
                    print("*******CORRECTION: OUR CHAR STOPPED", position, "PROCESS POS", processPos, "ORDER NUM", orderNum)
                    (char.setPosition)(*position)
                    char.setWalkOrderNumber(orderNum)
                    char.setLastPos(position)
            else:
                print("Server corrected position.")
                (char.setPosition)(*position)
            return
        (char.stopGoto)(*position)

        def directionChange(result):
            if char.direction != direction:
                char.direction = direction

        d = defer.Deferred()
        d.addCallback(directionChange)
        char.event = d


walkingCharsController = WalkingCharsController()