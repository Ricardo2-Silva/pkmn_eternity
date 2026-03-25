# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\interface\help.py
"""
Created on Nov 11, 2019

@author: Admin
"""
from client.control.gui.label import Label
from client.data.utils.anchor import AnchorType
from client.control.gui.windows import Header, Window
from client.game import desktop
from client.control.events.event import eventManager, eventDispatcher
from client.data.system.help import helpConfig
from shared.container.constants import BattleType

class HelpWindow(Window):
    helpTips = {
     'pokemon_receive': '"Congratulations on your first Pokemon! You will need to release a Pokemon to battle, to do that, locate your Pokemon on the left Pokemon Party bar. You can just drag and drop it onto the overworld close to your trainer!"', 
     'pokedex': '"This is your Pokedex! You will be able to get information on Pokemon as you meet them. You can either collect data on them by capturing, or you can right click on any Pokemon to scan it."', 
     'pokemon_selection': '"The controls are the same for Pokemon and Trainers, and you will notice your Pokemon even gets a separate bar for its skills. The last 4 spots on the hotkey bar are shared between all of your selectable characters. This makes it easy to throw Pokeballs, use Potions, or whatever else you wish."', 
     'battle_npc': '"Select your Pokemon and start battling! Use the hotkeys for your skills, or use your middle mouse wheel to scroll to the right skill and target something close!\\n\\nBeware not to exhaust all your energy too quickly although it will regenerate over time!"', 
     'battle_wild': '"With a Wild Pokemon be careful as any released Pokemon could get caught in the crosshairs! You can use a Pokeball to capture, but beware as they will reject Pokeballs at full life. Wild Pokemon may also drop items, or come with a held item on capture!"'}

    def __init__(self):
        Window.__init__(self, desktop, position=(AnchorType.RIGHTCENTER), autosize=(False,
                                                                                    True), size=(200,
                                                                                                 50), visible=False)
        Header(self, "Tips", close=True)
        self.label = Label(self, position=(AnchorType.TOPLEFT), text="Hello", multiline=True, size=(180,
                                                                                                    0))
        self.fitToContent()

    def showText(self, text):
        if not helpConfig.needsHelp(text):
            return
        helpConfig.gaveHelp(text)
        if self.visible == False:
            self.show()
        self.label.text = self.helpTips[text]
        self.fitToContent()
        desktop._focusWidget = None


class HelpControl:

    def __init__(self):
        self.window = HelpWindow()
        eventManager.registerListener(self)
        eventDispatcher.push_handlers(self)

    def reset(self):
        self.window.forceHide()

    def onBattleStart(self, battleType):
        if battleType == BattleType.NPC:
            self.window.showText("battle_npc")
        elif battleType == BattleType.WILD:
            self.window.showText("battle_wild")

    def onCharSelection(self, char):
        if char.data.isPokemon():
            self.window.showText("pokemon_selection")

    def showText(self, text):
        self.window.showText(text)

    def onPokemonReceived(self, pokemonData):
        self.window.showText("pokemon_receive")


helpWindow = HelpControl()
