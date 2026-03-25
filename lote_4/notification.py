# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\interface\notification.py
from client.control.gui import Window, Button, Label, Datatable, LineRoundedContainer
from client.control.service.session import sessionService
from client.data.settings import gameSettings
from client.control.events.event import eventManager
from client.data.utils.anchor import AnchorType, Alignment
from client.data.DB import messageDB
from client.data.gui import styleDB
from client.data.utils.color import Color
from client.game import desktop

class SimpleMessageWindow(Window):

    def __init__(self):
        Window.__init__(self, desktop, size=(200, 150), position=(gameSettings.getWindowCenter(200, 150)), draggable=True)
        self.messageLabel = Label(self, size=(180, 0), position=(0, 20), autosize=(False,
                                                                                   True), alignment=(Alignment.CENTER), multiline=True)
        self.setId("SimpleMessageWindow")
        self.hide()

    def displayMessage(self, message):
        self.show()
        self.setActive()
        self.messageLabel.text = message
        self.fitToContent()

    def hideWindow(self, widget, x, y, modifiers):
        self.hide()

    def onKeyReturn(self):
        self.hide()


class ConfirmationWindow(Window):
    confirmSize = (250, 170)

    def __init__(self):
        self.runFunc = None
        self.runArgs = []
        Window.__init__(self, desktop, size=(self.confirmSize), position=(gameSettings.getWindowCenter(250, 170)), draggable=True, visible=False)
        self.messageLabel = Label(self, size=(240, 0), position=(0, 20), autosize=(False,
                                                                                   True), alignment=(Alignment.CENTER), multiline=True)
        self.confirmButton = Button(self, text="Ok", size=(75, 0), autosize=(False,
                                                                             True), position=(AnchorType.BOTTOMLEFT))
        self.confirmButton.addCallbackEnd("onMouseLeftClick", self.runFunction)
        self.cancelButton = Button(self, text="Cancel", size=(75, 0), autosize=(False,
                                                                                True), position=(AnchorType.BOTTOMRIGHT))
        self.cancelButton.addCallbackEnd("onMouseLeftClick", self.hideWindow)

    def hide(self):
        Window.hide(self)
        self.runFunc = None
        self.runArgs = []

    def runFunction(self, widget, x, y, modifiers):
        (self.runFunc)(*self.runArgs)
        self.hide()

    def hideWindow(self, widget, x, y, modifiers):
        self.hide()

    def verify(self, message, function, *args, yes=False):
        if yes is True:
            self.confirmButton.text = "Yes"
            self.cancelButton.text = "No"
        else:
            self.confirmButton.text = "Ok"
            self.cancelButton.text = "Cancel"
        self.show()
        self.setActive()
        self.messageLabel.text = message
        self.fitToContent()
        self.runFunc = function
        self.runArgs = args


confirmWindow = ConfirmationWindow()

class ExitWindow(Window):

    def __init__(self):
        Window.__init__(self, desktop, position=(0, 0), draggable=False, size=(gameSettings.getScaledUIWindowResolution()), style=(styleDB.windowsNoStyle), autosize=(False,
                                                                                                                                                                      False), visible=True)
        self.setBackground(color=(Color.BLACK), alpha=100)
        self.setAlwaysOnTop()
        self.round = LineRoundedContainer(self, size=(200, 0), autosize=(False, True), color=(Color.WHITE), position=(AnchorType.CENTER))
        self.messageLabel = Label((self.round), text=(messageDB["QUIT_GAME_CHECK"]), size=(180,
                                                                                           0), position=(AnchorType.TOPCENTER), autosize=(False,
                                                                                                                                          True), multiline=True, alignment=(Alignment.CENTER))
        self.table = Datatable((self.round), maxCols=1, position=(AnchorType.TOPCENTER))
        self.table.setInternalMargins(0, 8)
        self.settingsButton = Button((self.table), text="Settings", size=(76, 0), autosize=(False,
                                                                                            True), clickSound="ButtonClose")
        self.settingsButton.addCallback("onMouseLeftClick", self.openSettings)
        self.exitButton = Button((self.table), text="Quit Game", size=(76, 0), autosize=(False,
                                                                                         True), clickSound="ButtonClose")
        self.exitButton.addCallback("onMouseLeftClick", self.exitGame)
        self.cancelButton = Button((self.table), text="Cancel", size=(76, 0), autosize=(False,
                                                                                        True), clickSound="ButtonClose")
        self.cancelButton.addCallback("onMouseLeftClick", self.clickHide)
        self.table.add(self.settingsButton)
        self.table.add(self.exitButton)
        self.table.add(self.cancelButton)
        self.table.fitToContent()
        self.round.fitToContent()
        self.setId("Exit")
        self.fitToContent()
        self.hide()

    def hide(self):
        super().hide()

    def show(self):
        self.renderer.backgroundSprite.batch = desktop.batch
        if sessionService.ingame:
            self.table.emptyMatrix()
            self.table.add(self.settingsButton)
            self.table.add(self.exitButton)
            self.table.add(self.cancelButton)
            self.table.fitToContent()
            self.round.fitToContent()
        else:
            self.table.emptyMatrix()
            self.table.add(self.settingsButton)
            self.table.add(self.exitButton)
            self.table.add(self.cancelButton)
            self.table.fitToContent()
            self.round.fitToContent()
        super().show()
        desktop.reOrder()
        self.renderer.backgroundSprite.batch = desktop.transparent

    def clickHide(self, widget, x, y, modifiers):
        self.hide()

    def displayMessage(self, message):
        self.show()
        self.setActive()
        self.fitToContent()

    def logoutOfGame(self, widget, x, y, modifiers):
        if sessionService.isInBattle():
            self.forceHide()
            eventManager.notify("onBattleMessage", "You cannot logout while in a battle!", log=False)
            return
        if sessionService.trade:
            self.forceHide()
            eventManager.notify("onBattleMessage", "You cannot logout while in a trade!", log=False)
            return
        from client.control.net.world.handler import gameNetHandler
        defer = gameNetHandler.disconnect()

        def close(result):
            from client.control.system.logout import logoutManager
            self.hide()
            from client.scene.manager import sceneManager
            sceneManager.changeScene("Login")
            logoutManager.onGameLogout()

        defer.addBoth(close)

    def openSettings(self, widget, x, y, modifiers):
        self.hide()
        eventManager.notify("onWidgetShow", "Settings")

    def exitGame(self, widget, x, y, modifiers):
        from client.control.net.world.handler import gameNetHandler
        defer = gameNetHandler.disconnect()
        if defer is not None:

            def close(result):
                eventManager.notify("onQuitGame")

            defer.addBoth(close)
        else:
            eventManager.notify("onQuitGame")


class NotificationWindow(SimpleMessageWindow):

    def __init__(self):
        Window.__init__(self, desktop, size=(200, 150), position=(gameSettings.getWindowCenter(200, 150)), draggable=True)
        self.messageLabel = Label(self, size=(180, 0), position=(0, 20), autosize=(False,
                                                                                   True), alignment=(Alignment.CENTER), multiline=True)
        self.setId("Notification")
        self.setAlwaysOnTop()
        self.hide()
        self.okButton = Button(self, text="Ok", size=(76, 0), autosize=(False, True), position=(AnchorType.BOTTOMCENTER))
        self.okButton.addCallbackEnd("onMouseLeftClick", self.hideWindow)

    def hideWindow(self, widget, x, y, modifiers):
        eventManager.notify("onAllowConnectButton", True)
        self.hide()

    def onKeyReturn(self):
        eventManager.notify("onAllowConnectButton", True)
        self.hide()


class ConnectionWindow(SimpleMessageWindow):

    def __init__(self):
        Window.__init__(self, desktop, size=(200, 80), position=(gameSettings.getWindowCenter(200, 150)), draggable=False)
        self.messageLabel = Label(self, size=(180, 0), position=(0, 20), autosize=(False,
                                                                                   True), multiline=True, alignment=(Alignment.CENTER))
        self.setAlwaysOnTop()
        self.setId("Connection")
        self.hide()

    def displayMessage(self, message):
        self.show()
        self.setActive()
        self.messageLabel.text = message
        self.fitToContent()

    def hideWindow(self, widget, x, y, modifiers):
        self.hide()

    def onKeyReturn(self):
        eventManager.notify("onAllowConnectButton", True)
        self.hide()


class DisconnectWindow(SimpleMessageWindow):

    def __init__(self):
        SimpleMessageWindow.__init__(self)
        self.okButton = Button(self, position=(AnchorType.BOTTOMCENTER), text="Exit Game", size=(76,
                                                                                                 0), autosize=(False,
                                                                                                               True))
        self.okButton.addCallbackEnd("onMouseLeftClick", self.exitGame)
        self.setId("Disconnect")

    def logoutOfGame(self, widget, x, y, modifiers):
        from client.control.net.world.handler import gameNetHandler
        from client.control.system.logout import logoutManager
        self.hide()
        from client.scene.manager import sceneManager
        sceneManager.changeScene("Login")
        logoutManager.onGameLogout()

    def exitGame(self, widget, x, y, modifiers):
        eventManager.notify("onQuitGame")


class Notification:

    def __init__(self):
        self.windows = {}
        self.windows["Exit"] = ExitWindow()
        self.windows["Connection"] = ConnectionWindow()
        self.windows["Notification"] = NotificationWindow()
        self.windows["Disconnect"] = DisconnectWindow()
        eventManager.registerListener(self)

    def onNotificationMessage(self, notificationId, message='Unknown message.'):
        for name in self.windows:
            if name == notificationId:
                window = self.windows[name]
                if window.visible:
                    window.hide()
                    return

        window = self.windows[notificationId]
        window.displayMessage(message)

    def onHideNotification(self, notificationId):
        window = self.windows[notificationId]
        if window.visible == True:
            window.hide()

    def onDisplayNotification(self, notificationId, message):
        self.windows[notificationId].displayMessage(message)


notificationControl = Notification()
