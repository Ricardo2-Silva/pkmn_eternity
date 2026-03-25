# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\net\world\parse\movement.py
from client.control.events.event import eventManager
from client.data.container.char import charContainer
from shared.container.constants import Direction, IdRange
import sys
from client.control.world.warp import warpController

def Fly(data):
    """ This packet changes the Z value of the Pokemon """
    _, charId, idRange, z = data
    print("FLYING")
    char = charContainer.getCharById(charId, idRange)
    eventManager.notify("onCharFly", char, z)


def Jump(data):
    _, charId, idRange = data
    char = charContainer.getCharById(charId, idRange)
    eventManager.notify("onCharJump", char)


def DirectionLook(data):
    _, charId, idRange, directionNum = data
    char = charContainer.getCharByIdIfAny(charId, idRange)
    if char:
        intDirection = directionNum % 10
        deg = Direction.toDeg[intDirection]
        char.setFacing(deg)


def PosAndDir(data):
    """ Movement packet. Give the current position of a char, and the direction he is going to."""
    _, orderNum, charId, charType, x, y, directionNum = data
    char = charContainer.getCharByIdIfAny(charId, charType)
    if not char:
        sys.stderr.write(f"Error : Trying to posAndDir a non existing char: {charId}, type: {charType}! \n")
        return
    else:
        intDirection = directionNum % 10
        if directionNum > 10:
            eventManager.notify("onServerSaysCharStop", char, orderNum, (x, y), Direction.toDeg[intDirection])
        else:
            eventManager.notify("onServerSaysCharMove", char, orderNum, (x, y), Direction.toDeg[intDirection])


def MakeFollow(data):
    """ Make a character follow another """
    _, charId, charIdRange, targetId, targetIdRange = data
    char = charContainer.getCharById(charId, charIdRange)
    target = charContainer.getCharById(targetId, targetIdRange)
    print("- MAKE FOLLOW PACKET - FROM SERVER: MAKING CHAR", char.name, "FOLLOW", target.name, char.followTarget)
    if char.followTarget != target:
        char.startFollowing(target)


def SpeedChange(data):
    _, charId, charIdRange, speed, duration = data
    char = charContainer.getCharByIdIfAny(charId, charIdRange)
    if char:
        char.data.setWalkingSpeed(speed)


def StopFollow(data):
    """ Make a character stop following another, and sets its "stop_pos,
        the pos he has to go to, before being controllable. """
    _, charId, charIdRange, x, y = data
    char = charContainer.getCharById(charId, charIdRange)
    print("-PACKET: Stop Follow", char)
    char.stopFollow()
    char.setPosition(x, y)


def GotoPosition(data):
    """ Make a character going to a specific position, with a specific speed. """
    _, charId, charType, x, y, z = data
    char = charContainer.getCharByIdIfAny(charId, charType)
    if not char:
        sys.stderr.write(f"Error : Trying to make Goto a non existing char: {charId} {IdRange.toStr[charType]}! \n")
        return
    char.beginToGoTo(x, y, z)


def StopGotoPosition(data):
    _, charId, charType, x, y, z = data
    char = charContainer.getCharByIdIfAny(charId, charType)
    if not char:
        sys.stderr.write(f"Error : Trying to stop goto a non existing char: {charId} type: {IdRange.toStr[charType]}! \n")
        return
    char.stopGoto(x, y)


def CharWarp(data):
    _, charId, idRange, mapId, entering = data
    char = charContainer.getCharByIdIfAny(charId, idRange)
    if not char:
        sys.stderr.write(f"Error : Char that warped doesn't exist to our client! {charId} \n")
        return
    eventManager.notify("onCharWarp", char, mapId, entering)


def ClientCharWarp(data):
    _, charId, idRange, mapId, mapX, mapY = data
    print("----------- RECEIVED CHAR WARP")
    char = charContainer.getCharById(charId, idRange)
    eventManager.notify("onClientCharWarp", char, mapId, mapX, mapY)
    eventManager.notify("onClientCharWarped", char)


class WarpData:

    def __init__(self, warpId, idRange):
        self.id = warpId
        self.idRange = idRange


def WarpPoint(data):
    _, warpId, x, y, width, height, graphicId = data
    warpObj = charContainer.getDataByIdIfAny(warpId, IdRange.WARP)
    if not warpObj:
        warp = warpController.createWarp(warpId, x, y, width, height, graphicId)
        charContainer.addDataIfNotExist(WarpData(warpId, IdRange.WARP))
