# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\world\action\capture.py
"""
Created on 30 juil. 2011

@author: Kami
"""
from client.control.events.event import eventManager
from client.data.container.char import charContainer
from shared.container.constants import CreatureAction, Emotes
from twisted.internet import reactor
from shared.service.geometry import getPositionOnDirection
import random
from client.control.system.anims import AnimCallable

class CaptureController:

    def __init__(self):
        eventManager.registerListener(self)

    def captureFails(self, result, ball, x, y, z, wildPokemon, tremble):
        anim = ball.captureFail(tremble)
        anim += AnimCallable(wildPokemon.setPosition, x, y)
        anim += AnimCallable(wildPokemon.release)
        anim += AnimCallable(ball.waitAndRemove, 3)

    def onPokemonCaptureResult(self, wildPokemon, ball, x, y, z, tremble, result):
        wildPokemon = wildPokemon
        if result != 2:
            if not wildPokemon.visible:
                wildPokemon.show()
            d = wildPokemon.recall(ball)
            ball.capture()
            if result == 1:
                ball.captureSuccess(tremble)
        elif result == 0:
            d.addCallback(self.captureFails, ball, x, y, z, wildPokemon, tremble)
        else:
            wildPokemon.playAction(CreatureAction.ATK, 0.5)
            wildPokemon.emote(Emotes.ANGRY_MARK)
            angle = random.randint(0, 360)
            wildPokemon.setFacingNear(angle)
            newBallPosition = getPositionOnDirection(wildPokemon.getPosition2D(), angle, 60)
            ball.captureRefused(newBallPosition)
        charContainer.delChar(ball)


captureController = CaptureController()
