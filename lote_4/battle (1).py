# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\interface\battle.py
"""
Created on Jul 31, 2011

@author: Ragnarok
"""
from twisted.internet.error import AlreadyCalled
from client.data.utils.anchor import AnchorType, Alignment
from client.control.gui import Window, Label, Textbox, Button, Checkbox, Container, Header
from client.data.gui import styleDB
from shared.container.net import cmsg
from client.control.events.event import eventManager
from shared.container.constants import ChallengeResponses
from client.control.service.session import sessionService
from client.control.net.sending import packetManager
from client.control.utils.localization import localeInt
from client.data.gui.button import TextboxType
from twisted.internet import reactor
from client.game import desktop
REQUEST_ACCEPTED = 1
REQUEST_DENIED = 2

class ReceivedWindow(Window):

    def __init__(self):
        Window.__init__(self, desktop, position=(AnchorType.CENTER), size=(285, 190), visible=False, draggable=True, autosize=(True,
                                                                                                                               True))
        self.descriptionLbl = Label(self, position=(AnchorType.TOPLEFT), text="You received a challenge.", size=(250,
                                                                                                                 0), autosize=(False,
                                                                                                                               True))
        self.partyLbl = Label(self, position=(AnchorType.TOPLEFT), text="This is a 1v1 Battle!", autosize=(True,
                                                                                                           True))
        self.itemLbl = Label(self, position=(AnchorType.TOPLEFT), text="Items", autosize=(True,
                                                                                          True))
        self.switchingLbl = Label(self, position=(AnchorType.TOPLEFT), text="Recalling", autosize=(True,
                                                                                                   True))
        self.maxLevelLbl = Label(self, position=(AnchorType.TOPLEFT), text="Max Level", autosize=(True,
                                                                                                  True))
        self.maxPkmnLbl = Label(self, position=(AnchorType.TOPLEFT), text="Max Pokemon", autosize=(True,
                                                                                                   True))
        self.betLbl = Label(self, position=(AnchorType.TOPLEFT), text="Bet", autosize=(True,
                                                                                       True))
        self.acceptBtn = Button(self, position=(AnchorType.CENTERBOTTOM), size=(100,
                                                                                26), text="Accept", style=(styleDB.greenButtonStyle), autosize=(False,
                                                                                                                                                False))
        self.acceptBtn.addCallback("onMouseLeftClick", self._acceptChallenge)
        self.denyBtn = Button(self, position=(AnchorType.CENTERBOTTOM), size=(100,
                                                                              26), text="Deny", style=(styleDB.redButtonStyle), autosize=(False,
                                                                                                                                          False))
        self.denyBtn.addCallback("onMouseLeftClick", self._denyChallenge)
        self.fitToContent()

    def showChallenge(self, trnName, itemUse, switching, maxLevel, maxPkmn, bet, party):
        eventManager.notify("onSystemMessage", f'Received a {"party" if party else "duel"} challenge request.')
        self.show()
        if party:
            count = sessionService.group.count
            duelText = f"Party Vs Party ({count}v{count})"
        else:
            duelText = "Duel Battle (1v1)"
        self.descriptionLbl.text = f"You have been challenged by {trnName}!"
        self.partyLbl.text = f"Duel Type: {duelText}"
        self.itemLbl.text = f'Items: {"On" if itemUse else "Off"}'
        self.switchingLbl.text = f'Recalling: {"On" if switching else "Off"}'
        self.maxLevelLbl.text = f'Maximum Level: {maxLevel if maxLevel else "No Limit"}'
        self.maxPkmnLbl.text = f'Maximum Pokemon: {maxPkmn if maxPkmn else "No Limit"}'
        self.betLbl.text = f'Monetary Bet: {localeInt(bet) if bet else "No bet."}'

    def _acceptChallenge(self, widget, x, y, modifiers):
        packetManager.queueSend(cmsg.DuelResponse, REQUEST_ACCEPTED)
        self.closeWindow()

    def _denyChallenge(self, widget, x, y, modifiers):
        packetManager.queueSend(cmsg.DuelResponse, REQUEST_DENIED)
        self.closeWindow()

    def closeWindow(self):
        self.hide()


class DuelWindow(Window):

    def __init__(self):
        Window.__init__(self, desktop, position=(AnchorType.CENTER), size=(200, 240), draggable=True, visible=False)
        self.trainerData = None
        Header(self, text="Duel Challenge")
        self.nameLbl = Label(self, position=(AnchorType.TOPLEFT), size=(180, 20), text="Opponent: <user>")
        self.itemBox = Checkbox(self, position=(AnchorType.TOPLEFT), text="Allow Items")
        self.itemBox.setSelected(True)
        self.switchBox = Checkbox(self, position=(AnchorType.TOPLEFT), text="Allow Recall")
        self.switchBox.setSelected(True)
        self.groupBox = Checkbox(self, position=(0, 0), text="Party vs Party")
        maxLevelC = Container(self, position=(AnchorType.TOPLEFT))
        self.maxLevelLbl = Label(maxLevelC, position=(AnchorType.LEFTTOP), text="Maximum Level")
        self.maxLevelTxt = Textbox(maxLevelC, position=(AnchorType.LEFTTOP), size=(20,
                                                                                   20), text="0", type=(TextboxType.ONLY_INT), maxLetters=2)
        self.maxLevelTxt.addCallback("onLostFocus", self.checkMaxLevel)
        maxLevelC.fitToContent()
        maxPokemonC = Container(self, position=(AnchorType.TOPLEFT))
        self.maxPkmnLbl = Label(maxPokemonC, position=(AnchorType.LEFTTOP), text="Maximum Pokemon")
        self.maxPkmnTxt = Textbox(maxPokemonC, position=(AnchorType.LEFTTOP), size=(20,
                                                                                    20), text="0", type=(TextboxType.ONLY_INT), maxLetters=1)
        self.maxPkmnTxt.addCallback("onLostFocus", self.checkMaxPokemon)
        maxPokemonC.fitToContent()
        betC = Container(self, position=(AnchorType.TOPLEFT))
        self.betLbl = Label(betC, position=(AnchorType.LEFTTOP), text="Monetary Bet")
        self.betTxt = Textbox(betC, position=(AnchorType.LEFTTOP), size=(80, 20), text="0", type=(TextboxType.ONLY_INT), maxLetters=6)
        self.betTxt.addCallback("onLostFocus", self.checkBet)
        betC.fitToContent()
        self.challengeBtn = Button(self, position=(AnchorType.CENTERBOTTOM), text="Challenge", style=(styleDB.greenButtonStyle))
        self.challengeBtn.addCallback("onMouseLeftClick", self.challengeTrn)
        self.resetBtn = Button(self, position=(AnchorType.CENTERBOTTOM), text="Reset", style=(styleDB.redButtonStyle))
        self.resetBtn.addCallback("onMouseLeftClick", self.resetValues)
        self.cancelBtn = Button(self, position=(AnchorType.CENTERBOTTOM), text="Cancel", style=(styleDB.cancelButtonStyle))
        self.cancelBtn.addCallback("onMouseLeftClick", self.closeWindow)
        self.fitToContent()
        (self.groupBox.setPosition)(*self.itemBox.getRelativePosition(offx=85))

    def resetValues(self, widget, x, y, modifiers):
        self.maxLevelTxt.text = "0"
        self.maxPkmnTxt.text = "0"
        self.betTxt.text = "0"

    def checkBet(self, new_widget):
        try:
            num = int(self.betTxt.text)
        except ValueError:
            self.betTxt.text = "0"
            return
        else:
            if num > sessionService.bag.money or num < 0:
                self.betTxt.text = "0"

    def checkMaxPokemon(self, new_widget):
        try:
            num = int(self.maxPkmnTxt.text)
        except ValueError:
            self.maxPkmnTxt.text = "0"
            return
        else:
            if num > 6 or num < 0:
                self.maxPkmnTxt.text = "0"

    def checkMaxLevel(self, new_widget):
        try:
            num = int(self.maxLevelTxt.text)
        except ValueError:
            self.maxLevelTxt.text = "0"
            return
        else:
            if num < 0 or num > 100:
                self.maxLevelTxt.text = "0"

    def showChallenge(self, trainerData):
        self.trainerData = trainerData
        if not self.visible:
            self.show()
        else:
            self.groupBox.setSelected(False)
            self.nameLbl.text = f"Opponent: {trainerData.name}"
            if sessionService.group.inGroup():
                self.groupBox.show()
            else:
                self.groupBox.close()

    def challengeTrn(self, widget, x, y, modifiers):
        packetManager.queueSend(cmsg.DuelChallenge, self.trainerData.id, int(self.itemBox.isSelected()), int(self.switchBox.isSelected()), int(self.maxLevelTxt.text), int(self.maxPkmnTxt.text), int(self.betTxt.text), int(self.groupBox.isSelected()))
        self.closeWindow()

    def closeWindow(self, widget=None, x=None, y=None, modifiers=None):
        self.hide()
        self.tranerData = None


class ChallengePlayer:

    def __init__(self):
        self.window = DuelWindow()
        self.requestWindow = ReceivedWindow()
        eventManager.registerListener(self)
        self.countDown = 5
        self._countdownDefer = None

    def onBattleEnd(self):
        self.cancelCountdown()

    def showChallenge(self, trainerData):
        self.window.showChallenge(trainerData)

    def onChallengeRequest(self, trnName, itemUse, minLevel, maxLevel, maxPkmn, bet, party):
        self.requestWindow.showChallenge(trnName, itemUse, minLevel, maxLevel, maxPkmn, bet, party)

    def startCountdown(self):
        self.countDown = 5
        self.lowerCountDown()

    def cancelCountdown(self):
        if self._countdownDefer:
            try:
                self._countdownDefer.cancel()
            except AlreadyCalled:
                pass

    def lowerCountDown(self):
        eventManager.notify("onSystemMessage", f"Battle Will Begin in... {self.countDown}.")
        self.countDown -= 1
        if self.countDown == 0:
            eventManager.notify("onSystemMessage", "BATTLE HAS BEGUN!")
            self._countdownDefer = None
        else:
            self._countdownDefer = reactor.callLater(1, self.lowerCountDown)

    def onChallengeResponse(self, response):
        if response == ChallengeResponses.SENT:
            eventManager.notify("onSystemMessage", "Challenge was sent to player.")
        elif response == ChallengeResponses.ACCEPTED:
            eventManager.notify("onSystemMessage", "All players have accepted!")
            self.startCountdown()
        elif response == ChallengeResponses.CANCELED:
            eventManager.notify("onSystemMessage", "Challenge was declined.")
            self.requestWindow.close()
        elif response == ChallengeResponses.FORFEIT:
            eventManager.notify("onSystemMessage", "Opponent has forfeited the match.")
        elif response == ChallengeResponses.INBATTLE:
            eventManager.notify("onSystemMessage", "Player is in battle already.")
        elif response == ChallengeResponses.OFFLINE:
            eventManager.notify("onSystemMessage", "Player is not online.")
        elif response == ChallengeResponses.LOSE:
            eventManager.notify("onSystemMessage", "You have lost the duel.")
        elif response == ChallengeResponses.WIN:
            eventManager.notify("onSystemMessage", "You have won the duel.")
        elif response == ChallengeResponses.RANGE:
            eventManager.notify("onSystemMessage", "You are not in range.")
        elif response == ChallengeResponses.BUSY:
            eventManager.notify("onSystemMessage", "Player is currently busy.")
        elif response == ChallengeResponses.INVALID_CONDITION:
            eventManager.notify("onSystemMessage", "One or more players do not meet the conditions to accept.")
            self.requestWindow.close()
        elif response == ChallengeResponses.PARTY_MEMBER_RANGE_FAIL:
            eventManager.notify("onSystemMessage", "One or more of your party members are not within range.")
        elif response == ChallengeResponses.PARTY_OPPONENTS_RANGE_FAIL:
            eventManager.notify("onSystemMessage", "One or more of your opponents are not within range.")
        elif response == ChallengeResponses.PARTY_OPPONENTS_NO_GROUP:
            eventManager.notify("onSystemMessage", "Your opponent has no party and cannot participate in a party battle.")
        elif response == ChallengeResponses.PARTY_MEMBER_DECLINED:
            eventManager.notify("onSystemMessage", "One your party members declined the challenge.")
            self.requestWindow.close()
        elif response == ChallengeResponses.PARTY_OPPONENTS_DECLINED:
            eventManager.notify("onSystemMessage", "One of your opponents party members declined the challenge.")
            self.requestWindow.close()
        elif response == ChallengeResponses.PARTY_MEMBER_MATCH:
            eventManager.notify("onSystemMessage", "Your online party count is higher than the opponents party, they must match.")
        elif response == ChallengeResponses.PARTY_OPPONENTS_MATCH:
            eventManager.notify("onSystemMessage", "The online party count of your opponent is higher than yours, they must match.")
        elif response == ChallengeResponses.PARTY_MEMBER_BUSY:
            eventManager.notify("onSystemMessage", "A party member is currently busy.")
            self.requestWindow.close()
        elif response == ChallengeResponses.PARTY_OPPONENTS_BUSY:
            eventManager.notify("onSystemMessage", "An opponents party member is currently busy.")
            self.requestWindow.close()
        elif response == ChallengeResponses.PARTY_SAME_PARTY:
            eventManager.notify("onSystemMessage", "A party battle has to be between two different parties.")
        elif response == ChallengeResponses.PARTY_TIMEOUT:
            eventManager.notify("onSystemMessage", "Someone has failed to accept the challenge within the time limit.")
            self.requestWindow.close()
        elif response == ChallengeResponses.DUEL_TIMEOUT:
            eventManager.notify("onSystemMessage", "The opponent failed to accept the challenge within the time limit.")
            self.requestWindow.close()
        elif response == ChallengeResponses.PARTY_WIN:
            eventManager.notify("onSystemMessage", "Your party won the battle!")
        elif response == ChallengeResponses.PARTY_LOSS:
            eventManager.notify("onSystemMessage", "Your party lost the battle.")
        elif response == ChallengeResponses.PARTY_REMOVED:
            eventManager.notify("onSystemMessage", "You were removed from the party battle.")


playerChallenge = ChallengePlayer()
