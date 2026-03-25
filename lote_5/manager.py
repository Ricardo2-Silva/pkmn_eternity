# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\scene\manager.py
"""
Created on Oct 21, 2016

@author: Admin
"""
import pyglet
from pyglet.gl import *
from client.data.settings import gameSettings
from client.control.events.event import eventManager
from pyglet.window import key
from pyglet.libs.win32 import _user32
from pyglet.libs.win32.constants import WM_SYSCOMMAND, SC_MINIMIZE

class Scene(object):
    __doc__ = "Scene template."

    def __init__(self):
        self.handlers = []

    def enable_handlers(self):
        return

    def on_enter(self):
        for handler in self.handlers:
            sceneManager.window.push_handlers(handler)

        pyglet.clock.schedule_interval(self.update, 0.016666666666666666)

    def on_exit(self):
        for handler in self.handlers:
            sceneManager.window.remove_handlers(handler)

        pyglet.clock.unschedule(self.update)

    def update(self, dt):
        return

    def draw(self):
        return


from client.scene.preload import PreLoadScene

class IntegerFPSDisplay(pyglet.window.FPSDisplay):

    def __init__(self, window):
        super().__init__(window)
        self.label.font_name = "Segoe UI"
        self.label.font_size = 24
        self.label.color = (255, 0, 0, 150)
        self.label.z = 1000

    def set_fps(self, fps):
        self.label.text = (f"{int(fps)}")


class SceneManager(object):

    def init(self):
        self.running = True
        width, height = gameSettings.getWindowResolution()
        self.worldResolution = gameSettings.getWorldResolution()
        self.window = pyglet.window.Window(width=width, height=height, fullscreen=(bool(gameSettings.getFullscreen())), vsync=(gameSettings.getVsync()),
          caption="Pokemon Eternity")
        self.width, self.height = width, height
        self.aspect = [
         self.window.width / 640.0, self.window.height / 480.0]
        self.show_fps = False
        self.scenes = {"Preload": (PreLoadScene(self))}
        self.scene = self.scenes["Preload"]
        self.fps_display = IntegerFPSDisplay(self.window)
        eventManager.registerListener(self)
        glEnable(GL_BLEND)
        self.window.push_handlers(self)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.F12 or symbol == key.PRINT:
            pyglet.image.get_buffer_manager().get_color_buffer().save("screenshot.png")
        elif symbol == key.F7:
            self.toggleFps()
        elif symbol == key.ENTER:
            pass
        if modifiers & key.MOD_ALT:
            if self.window.fullscreen:
                _user32.PostMessageW(self.window._hwnd, WM_SYSCOMMAND, SC_MINIMIZE, 0)

    def on_draw(self):
        self.window.clear()
        self.scene.draw()
        if self.show_fps:
            self.fps_display.draw()

    def on_close(self):
        """ Here is the handling of closing the application. Sometimes the app will crash before the GUI is even created.
            We test if any events are registered, if there are listeners to close GUI force confirmation.
            If no events, then force close it without confirmation.
        """
        if self.scene in [self.scenes.get("Preload"), self.scenes.get("Loading")]:
            eventManager.notify("onQuitGame")
        else:
            eventManager.notify("onTargetMode", None)
            eventManager.notify("onNotificationMessage", "Exit", "")

    def databaseLoaded(self, desktop):
        """ Used when the database is loaded, that way we can import the cursors """
        from client.control.system.cursor import cursor
        self.cursor = cursor
        self.window.set_icon(pyglet.resource.image("lib/system/Pokeball.ico"))
        desktop.cursor = cursor

    def toggleFps(self):
        self.show_fps = not self.show_fps

    def onForceRender(self):
        """ Forces rendering """
        pyglet.clock.tick()
        self.window.dispatch_events()
        self.window.clear()
        self.scene.draw()
        self.window.flip()

    def exists(self, sceneName):
        return sceneName in self.scenes

    def get(self, sceneName):
        return self.scenes[sceneName]

    def add(self, sceneName, scene):
        if sceneName not in self.scenes:
            self.scenes[sceneName] = scene

    def onQuitGame(self):
        from twisted.internet import reactor
        reactor.callFromThread(reactor.stop)
        pyglet.app.exit()

    def setScene(self, scene):
        if self.scene:
            self.scene.on_exit()
        self.scene = scene
        self.scene.on_enter()

    def changeScene(self, sceneName):
        if self.scene:
            self.scene.on_exit()
        self.scene = self.scenes[sceneName]
        self.scene.on_enter()

    def stop(self, dt):
        self.scene = None

    def convert(self, x, y):
        """ Converts bottom left position to top left position """
        return (
         x, self.height - y)

    def convertWorld(self, x, y):
        return (
         x, self.worldResolution[1] - y)

    def convertWorldY(self, y):
        return self.worldResolution[1] - y

    def convertY(self, y):
        return self.height - y

    def invertY(self, x, y):
        return (
         x, self.height + y)


sceneManager = SceneManager()
