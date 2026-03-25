# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\world\action\evolution.py
"""
Created on 30 juil. 2011

@author: Kami
"""
from client.data.container.char import charContainer
from client.control.events.event import eventManager

class EvolutionController:
    __doc__ = " Controls pokemon releasing in the world."

    def __init__(self):
        eventManager.registerListener(self)

    def onPokemonEvolve(self, pokemonData, dexId):
        char = charContainer.getCharByIdIfAny(pokemonData.id, pokemonData.idRange)
        if char:
            char.evolve(dexId)
            nameWidget = char.namePlate
            if nameWidget:
                if nameWidget.text != pokemonData.name:
                    nameWidget.text = pokemonData.name


evolutionController = EvolutionController()
