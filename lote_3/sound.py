# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\system\sound.py
"""
Created on 22 juil. 2011

@author: Spira
"""
from typing import Optional
import pyglet, time
from client.control.system.anims import Lerp, AnimCallable, AnimableRender
from client.data.settings import gameSettings
from client.control.events.event import eventManager
from pyglet.media import Player
import random, sys
from shared.container.constants import BattleType
t = time.time()
soundLoader = pyglet.resource.Loader(['audio', 
 'audio/BGM', 
 'audio/BGM/Day', 
 'audio/BGM/Night', 
 'audio/BGM/Battles'])
EFFECT_FOLDER = "Effects/"
GUI_FOLDER = "GUI/"
EVENT_FOLDER = "Events/"
BGM_FOLDER = "BGM/"
ENVIRONMENT_FOLDER = "Environment/"
print("LOADING SOUNDS START")
t1 = time.time()
AUDIO_ENABLED = True
audio_driver = pyglet.media.get_audio_driver()
try:
    gameListener = audio_driver.get_listener()
    gameListener.up_orientation = (0, -1, 0)
    gameListener.forward_orientation = (0, 1, 1)
except AttributeError:

    class DummmyGameListener:
        return


    gameListener = DummmyGameListener()
    AUDIO_ENABLED = False

class SoundDB(object):

    def __init__(self):
        self.cacheSoundsAtStart = False
        self.filenames = {'ButtonClose':GUI_FOLDER + "Button 5.mp3", 
         'Notification':GUI_FOLDER + "Button 6.mp3", 
         'MenuSelect':GUI_FOLDER + "Button 2.mp3", 
         'WindowClose':GUI_FOLDER + "Close Menu_Pokedex.mp3", 
         'MouseOver':GUI_FOLDER + "Mouse Over_Tab.mp3", 
         'QuestAccept':GUI_FOLDER + "Quest Accept.mp3", 
         'EnterInside':EFFECT_FOLDER + "Entering Door.wav", 
         'ExitInside':EFFECT_FOLDER + "Exit Door.wav", 
         'LevelUp':EFFECT_FOLDER + "LevelUp.wav", 
         'Faint':EFFECT_FOLDER + "Faint.wav", 
         'Ball Drop':EFFECT_FOLDER + "balldrop.wav", 
         'Ball Shake':EFFECT_FOLDER + "ballshake.wav", 
         'Ball Open':EFFECT_FOLDER + "open pokeball.wav", 
         'Growl':EFFECT_FOLDER + "4_stat_growl_1.wav", 
         'PhysicalImpact1':EFFECT_FOLDER + "p_impact_1.wav", 
         'PhysicalImpact2':EFFECT_FOLDER + "p_impact_2.wav", 
         'PhysicalImpact3':EFFECT_FOLDER + "p_impact_3.wav", 
         'Jump':EFFECT_FOLDER + "Jump.wav", 
         'recall':EFFECT_FOLDER + "Recall.wav", 
         'bump':EFFECT_FOLDER + "bump.wav", 
         'Choose':EFFECT_FOLDER + "Choose.wav", 
         'Select':EFFECT_FOLDER + "Choose.wav", 
         'Save':EFFECT_FOLDER + "save.wav", 
         'Dex Select':EFFECT_FOLDER + "dexselect.wav", 
         'rain':ENVIRONMENT_FOLDER + "Thunder & Rain.mp3", 
         'stream':ENVIRONMENT_FOLDER + "Stream.mp3", 
         'wind':ENVIRONMENT_FOLDER + "Wind Soft.mp3"}
        if self.cacheSoundsAtStart:
            for name, filename in self.filenames.items():
                self.getSound(name)

    def getSound(self, name):
        if name not in self.__dict__:
            try:
                self.__dict__[name] = soundLoader.media((self.filenames[name]), streaming=False)
                self.__dict__[name].filename = name
            except pyglet.resource.ResourceNotFoundException as msg:
                sys.stderr.write(f"Some sounds in the database did not load may cause errors. {name}\n")
                return

        return self.__dict__[name]


soundDB = SoundDB()
print("LOADING SOUNDS DONE", time.time() - t1)
battleMusic = {(BattleType.NPC): ('Pokemon Eternity - PVP Trainer Battle v. 1.2', ), 
 (BattleType.WILD): ('Pokemon Eternity - Trainer Battle 1', ), 
 (BattleType.GYM): ('Pokemon Eternity - Gym Battle', ), 
 (BattleType.LEGENDARY): ('Pokemon Eternity - Legendary Large Battle!', )}

class EnvironmentSound(pyglet.media.Player):
    __doc__ = " Player will only play a specific sound in a loop. "

    def __init__(self, filename, x, y, volume, distance=None, gain=None):
        pyglet.media.Player.__init__(self)
        self.setPosition(x, y, 0)
        if not distance:
            self.min_distance = 50
            self.max_distance = 400
            if self.max_distance:
                self.max_mute = 1
        else:
            self.min_distance, self.max_distance = distance
        if self.max_distance:
            self.max_mute = 1

    def pixelsToMeters(self, pixel):
        return pixel

    def setPosition(self, x, y, z=0):
        self.position = (
         x, y, z)

    def playSound(self, source):
        self.queue(source)
        self.play()

    def stopSound(self):
        self.pause()


def getMedia(filename, streaming=False):
    """Use this to handle music."""
    try:
        source = soundLoader.media(filename, streaming=streaming)
    except pyglet.resource.ResourceNotFoundException as msg:
        sys.stderr.write(f"Audio file was not found: {filename}\n")
        return

    return source


class CharSoundPlayer(pyglet.media.Player):
    __doc__ = " Each char will have it's own Player "

    def __init__(self):
        pyglet.media.Player.__init__(self)
        self.setPosition(0, 0, 0)
        self.cone_inner_angle = 360
        self.outer_cone_angle = 360
        self.cone_orientation = (1, 0, -1)
        self.cone_outer_gain = 0
        self.min_distance = 500
        self.max_distance = 900

    def setPosition(self, x, y, z=0):
        self.position = (
         x, y, z)

    def playSound(self, effectName):
        if AUDIO_ENABLED:
            try:
                sound = soundDB.getSound(effectName)
            except KeyError as e:
                print("Failed to play", e)
                return

            self.volume = gameSettings.getEffectVolume() / 100
            self.queue(sound)
            self.play()


class Music:

    def __init__(self, fileName, battle):
        self.fileName = fileName
        self.source = soundLoader.media(fileName, streaming=True)
        self.battle = battle
        self.player = pyglet.media.Player()
        self.player.volume = self.get_volume_channel() / 100
        self.player.loop = True
        self.player.queue(self.source)

    def get_volume_channel(self):
        if self.battle:
            return gameSettings.getBattleBgmVolume()
        else:
            return gameSettings.getBgmVolume()

    def play(self):
        self.player.play()

    def stop(self):
        self.player.pause()
        self.rewind()

    def rewind(self):
        self.player.seek(0.0)

    def pause(self):
        self.player.pause()

    def unpause(self):
        self.player.play()

    def fadeout(self):
        self.stop()

    def is_playing(self):
        return self.player.playing

    def get_position(self):
        return self.player.time * 1000.0

    def set_volume(self, newVolume):
        self.player.volume = newVolume

    def __repr__(self):
        return f"Music(filename='{self.fileName}', playing={self.player.playing})"


class MusicFader(AnimableRender):
    source: Optional[Music]

    def __init__(self):
        super().__init__()
        self._fading = False
        self.in_volume = 0
        self.source = None

    def play(self, source: Music, in_volume, duration):
        self.in_volume = in_volume
        if self._fading:
            self.stopAnims()
        else:
            self._fading = True
            if self.source:
                vol = self.source.player.volume
                self.anim = Lerp((self.source.player), "volume", vol, 0, duration=(duration / 2))
                self.anim += AnimCallable(self.source.pause)
                self.anim += AnimCallable(self._startNext, source)
                self.anim += Lerp((source.player), "volume", 0, in_volume, duration=(duration / 2))
            else:
                self._startNext(source)
            self.anim = Lerp((source.player), "volume", 0, in_volume, duration=duration)
        self.anim += AnimCallable(self._finish, self.source, source)
        self.source = source
        self.startAnim(self.anim)
        return self.anim

    def _startNext(self, source: Music):
        source.set_volume(0)
        source.play()

    def stop(self):
        if self._fading:
            self.stopAnims()
            self._fading = False

    def queue(self, source):
        self.bgmChannel.queue(source)

    def _finish(self, original, source):
        self._fading = False


class SinglePlayer(Player):

    def __init__(self, filename, players):
        Player.__init__(self)
        self._players = players
        self._players[filename] = self
        self._filename = filename

    def on_player_eos(self):
        del self._players[self._filename]


class MixerController:
    currentMusic: Optional[Music]

    def __init__(self):
        eventManager.registerListener(self)
        self._uniqueSources = []
        self._sourcePlayers = []
        self.soundCache = {}
        self.musicCache = {}
        self.currentMusic = None
        self.battleMusic = None
        self.effectChannel = Player()
        self.guiChannel = Player()
        self.environmentChannel = Player()
        self.environmentChannel.volume = gameSettings.getEnvironmentVolume() / 100
        self.environmentChannel.loop = True
        self.rain = None
        self.bgEnabled = True
        self.effectEnabled = True
        self.fader = MusicFader()
        self.initialize()

    def onQuitGame(self):
        if self.currentMusic:
            self.currentMusic.stop()

    def onBeforeMapLoad(self):
        if self.environmentChannel.playing:
            self.environmentChannel.pause()
        if self.currentMusic:
            self.currentMusic.pause()

    def onLogout(self):
        self.onBeforeMapLoad()

    def onAfterMapLoad(self):
        if self.environmentChannel.playing:
            self.environmentChannel.play()
        if self.currentMusic:
            self.currentMusic.play()

    def dummysound(self):
        return

    def initialize(self):
        self.setVolumeSettings()

    def setVolumeSettings(self):
        """ Set all the volume stuff"""
        self.effectChannel.volume = gameSettings.getEffectVolume() / 100
        self.guiChannel.volume = gameSettings.getGuiVolume() / 100
        self.setMusicVolume()
        self.environmentChannel.volume = gameSettings.getEnvironmentVolume() / 100

    def updateMusicVolume(self, value):
        if self.currentMusic:
            self.currentMusic.set_volume(value)

    def updateBattleVolume(self, value):
        if self.battleMusic:
            self.currentMusic.set_volume(value)

    def setMusicVolume(self):
        for filename in self.musicCache:
            music = self.musicCache[filename]
            music.set_volume(music.get_volume_channel() / 100)

    def canPlaySound(self):
        if not self.bgEnabled or AUDIO_ENABLED is False:
            return False
        else:
            return True

    def canPlayEffects(self):
        if not self.canPlaySound():
            return False
        else:
            return True

    def getSound(self, fileName, folder=EFFECT_FOLDER):
        return

    def _getMusic(self, fileName, battle=False):
        if fileName in self.musicCache:
            return self.musicCache[fileName]
        else:
            music = Music(fileName, battle)
            self.musicCache[fileName] = music
            return music

    def playRain(self):
        if AUDIO_ENABLED:
            if self.rain is False:
                self.environmentChannel.play()
                self.rain = True
            elif self.rain is None:
                sound = soundDB.getSound("rain")
                self.environmentChannel.queue(sound)
                self.environmentChannel.play()
                self.rain = True

    def stopRain(self):
        if self.rain == True:
            self.environmentChannel.pause()
            self.rain = False

    def playSound(self, filename, unique=False, interrupt=False):
        """Plays a sound effect of filename.
        If interrupt is True, it will interrupt any music it is playing to play the effect.
        If unique is True, it will only allow one effect to play at once.
        """
        if not self.canPlaySound():
            return self.dummysound()
        else:
            if unique:
                if filename in self._uniqueSources:
                    return
            sound = soundDB.getSound(filename)
            if sound:
                self._playSource(sound, self.effectChannel.volume, unique, interrupt)

    def playGui(self, name):
        if not self.canPlaySound():
            return self.dummysound()
        sound = soundDB.getSound(name)
        self.guiChannel.queue(sound)
        self.guiChannel.play()

    def onBattleEnd(self):
        self.stopBattleMusic()

    def onBattleStart(self, battleType):
        self.startBattleMusic(battleType)

    def startBattleMusic(self, battleType):
        if not self.battleMusic:
            bgm_list = battleMusic.get(battleType, ('Pokemon Eternity - Trainer Battle 1', ))
            fileName = random.choice(bgm_list)
            self.playMusic((fileName + ".mp3"), duration=1, battle=True)
            self.battleMusic = fileName

    def stopBattleMusic(self):
        if self.battleMusic:
            if self.currentMusic:
                self.currentMusic.stop()
            self.battleMusic = None

    def playMusic(self, fileName, duration=1, battle=False):
        """
        Stream music directly from disk while playing
        Loop = Number of times music will play. Any negative = Continuous
        """
        if int(gameSettings.getBgmState()):
            if AUDIO_ENABLED:
                if not fileName:
                    return
                if self.currentMusic:
                    if self.currentMusic.fileName == fileName:
                        return
        try:
            music = self._getMusic(fileName, battle)
        except pyglet.resource.ResourceNotFoundException:
            sys.stderr.write(f"Warning: Music file not found {fileName}\n")
            return
        else:
            self.fader.play(music, music.get_volume_channel() / 100, duration)
            self.currentMusic = music

    def _playSource(self, source, volume, unique=False, interrupt=False, position=None):
        if interrupt:
            if self.currentMusic:
                self.stopMusic()
        else:
            player = Player()
            player.volume = volume
            if position:
                player.position = position
            player.queue(source)
            player.play()
            self._sourcePlayers.append(player)
            if unique:
                self._uniqueSources.append(source.filename)

        def _on_player_eos():
            self._sourcePlayers.remove(player)
            player.on_player_eos = None
            if interrupt:
                if self.currentMusic:
                    self.fader.play(self.currentMusic, self.currentMusic.get_volume_channel() / 100, 1)
            if unique:
                self._uniqueSources.remove(source.filename)

        player.on_player_eos = _on_player_eos
        return player

    def stopMusic(self):
        if self.currentMusic:
            self.currentMusic.stop()

    def playCry(self, dexId):
        if allowCrys:
            if AUDIO_ENABLED:
                sound = pyglet.resource.media(f"audio/Crys/{str(dexId).zfill(3)}Cry.wav")
                self._playSource(sound, 0.3)

    def onItemAdd(self, nameId, quantity):
        self.playSound("LevelUp", unique=True)


allowCrys = True
mixerController = MixerController()
print("LOADED MIXER", time.time() - t)
