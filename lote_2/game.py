# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\game.py
""" Graphical Imports """
import math, traceback, sys
from twisted.python import log
if getattr(sys, "frozen", False):
    log.startLogging((open("error.log", "a")), setStdout=False)

    def frozenhook(*exc_info):
        log.msg("".join((traceback.format_exception)(*exc_info)))


    sys.excepthook = frozenhook
else:
    log.startLogging(sys.stdout)
import pyglet
pyglet.options["debug_gl"] = False
import client.render.custom
if "twisted.internet.reactor" in sys.modules:
    del sys.modules["twisted.internet.reactor"]
from pigtwist import pygletreactor
pygletreactor.install()
import rabbyt, os.path
rabbyt.data_directory = os.path.dirname(__file__)
from pyglet.gl import gl_info
if not gl_info.have_version(2, 0):
    import ctypes
    ctypes.windll.user32.MessageBoxW(0, f"Version Check Failed!\nMinimum version required: 2.0\nYour OpenGL version is {gl_info.get_version()}.\nCheck and ensure your graphics driver is up to date and supported.", "OpenGL Version Check", 0)
    sys.exit(1)

def main():
    from twisted.internet import reactor
    from client.scene.manager import sceneManager
    sceneManager.init()
    reactor.callLater(0.01, importGame)
    reactor.run(call_interval=0.001)


def importGame():
    global desktop
    from client.scene.manager import sceneManager
    from client.control.gui.desktop import Desktop
    desktop = Desktop()
    import client.interface.notification, client.control.net.threads
    from client.interface import settings
    from client.scene.loading import LoadingScene
    sceneManager.add("Loading", LoadingScene())
    if "-gui" in sys.argv:
        from client.scene.gui import GuiScene
        sceneManager.add("Gui", GuiScene())
        scene = "Gui"
    elif "-testing" in sys.argv:
        from client.scene.testing import TestScene
        sceneManager.add("Testing", TestScene())
        scene = "Testing"
    elif "-creation" in sys.argv:
        from client.scene.creation import CreationScene
        sceneManager.add("Creation", CreationScene())
        scene = "Creation"
    else:
        from client.scene.login import LoginScene
        sceneManager.add("Login", LoginScene())
        scene = "Login"
    sceneManager.databaseLoaded(desktop)
    from client.data.DB import sheetExperiment
    defer = sheetExperiment.preloadPokemon()
    if defer:

        def changeSceneCB(_):
            sceneManager.changeScene(scene)

        defer.addCallback(changeSceneCB)
    else:
        sceneManager.changeScene(scene)


if __name__ == "__main__":
    desktop = None
    main()
