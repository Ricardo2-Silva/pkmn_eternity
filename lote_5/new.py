# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\interface\pokemon\new.py
from shared.container.net import cmsg
from client.control.events.event import eventManager
from shared.container.constants import NameLength, Gender
from client.control.gui import Textbox, Button, Label, Picture, Window
from client.game import desktop
from client.data.DB import pokemonDB, messageDB
from client.render.cache import textureCache
from client.data.utils.anchor import AnchorType, Alignment
from client.data.gui import styleDB
from client.control.net.sending import packetManager
from client.control.service.session import sessionService
from client.data.settings import gameSettings
vowels = ('a', 'e', 'i', 'o', 'u')

class ReceivedWindow(Window):

    def __init__(self):
        self.pokemonId = 0
        x, y = gameSettings.getWindowCenter(285, 89)
        Window.__init__(self, desktop, position=(int(x), 50), size=(285, 89), visible=False, draggable=True)
        self.dexPic = Picture(self, position=(0, 0))
        self.descriptionLbl = Label(self, position=(45, 5), size=(280, 0), autosize=(True,
                                                                                     True), multiline=True)
        self.yesBtn = Button(self, position=(130, 48), size=(64, 26), autosize=(False,
                                                                                False), style=(styleDB.cancelButtonStyle), text="Yes")
        self.yesBtn.addCallback("onMouseLeftClick", self.changeName)
        self.noBtn = Button(self, position=(200, 48), size=(64, 26), autosize=(False,
                                                                               False), style=(styleDB.cancelButtonStyle), text="No")
        self.noBtn.addCallback("onMouseLeftClick", self.noChange)
        self.nameTxt = Textbox(self, position=(5, 50), size=(120, 20), visible=False, text="Enter a nickname.")
        self.nameTxt.addCallback("onMouseLeftClick", self.clearText)
        self.nameTxt.addCallback("onKeyReturn", self.keyChange)

    def reset(self):
        self.forceHide()

    def clearText(self, widget, x, y, modifiers):
        self.nameTxt.text = ""

    def showPokemon(self, pokemonId, dexId, gender):
        if not self.visible:
            self.show()
        elif self.pokemonId:
            self._noChange()
            if len(sessionService.getClientPokemonsData()) >= 6:
                eventManager.notify("onSystemMessage", "Your Pokemon party is full. Your Pokemon has been transferred to the PC.")
            self.pokemonId = pokemonId
            name = pokemonDB.name(dexId).title()
            prefix = "an" if name[0].lower() in vowels else "a"
            self.dexPic.setPicture(textureCache.getPokemonIcon(dexId))
            if gender == Gender.MALE:
                gendText = " (♂) [M]"
        elif gender == Gender.FEMALE:
            gendText = " (♀) [F]"
        else:
            gendText = ""
        self.descriptionLbl.text = f"You received {prefix} {name}!{gendText}\nWould you like to give it a nickname?"

    def keyChange(self):
        if self._checkName():
            self.hideWindow()

    def clear(self, btn):
        btn.text = ""

    def _checkName(self):
        text = self.nameTxt.text
        if len(text) > NameLength.POKEMON or len(text) < 3:
            eventManager.notify("onNotificationMessage", "Notification", messageDB["CHAR_LENGTH"])
            return False
        else:
            if text.isalpha() == False:
                eventManager.notify("onNotificationMessage", "Notification", messageDB["CHAR_ILLEGAL"])
                return False
            packetManager.queueSend(cmsg.NewPokemon, self.pokemonId, text.encode("utf8"))
            return True

    def changeName(self, widget, x, y, modifiers):
        if widget.text == "Yes":
            self.nameTxt.show()
            self.yesBtn.text = "Ok"
            self.noBtn.text = "Cancel"
        elif self._checkName():
            self.hideWindow()

    def _noChange(self):
        packetManager.queueSend(cmsg.NewPokemon, self.pokemonId, b'')

    def skipRename(self, pokemonId):
        packetManager.queueSend(cmsg.NewPokemon, pokemonId, b'')
        if len(sessionService.getClientPokemonsData()) >= 6:
            eventManager.notify("onSystemMessage", "Your Pokemon party is full. Your Pokemon has been transferred to the PC.")

    def noChange(self, widget, x, y, modifiers):
        self._noChange()
        self.hideWindow()

    def hideWindow(self):
        self.pokemonId = 0
        self.nameTxt.text = "Enter a nickname."
        if self.nameTxt.visible:
            self.nameTxt.hide()
        self.yesBtn.text = "Yes"
        self.hide()
        if len(sessionService.getClientPokemonsData()) >= 6:
            eventManager.notify("onSystemMessage", "Your Pokemon party is full. Your Pokemon has been transferred to the PC.")


class NewPokemon:

    def __init__(self):
        self.window = ReceivedWindow()
        eventManager.registerListener(self)

    def reset(self):
        self.window.reset()

    def onGetNewPokemon(self, pokemonId, dexId, gender):
        if gameSettings.getSkipRename():
            self.window.skipRename(pokemonId)
        else:
            self.window.showPokemon(pokemonId, dexId, gender)


newPokemonWindow = NewPokemon()
