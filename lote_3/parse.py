# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\net\login\parse.py
"""
Created on 23 juil. 2011

@author: Spira
"""
from client.control.events.event import eventManager
from client.data.DB import messageDB
from shared.service.utils import nullstrip
from shared.container.constants import LoginResponses
from client.scene.manager import sceneManager
from client.control.net.world.handler import gameNetHandler

def QueueInfo(data, loginNet):
    _, number, queueTime = data
    print(f" **** Received queue info : {queueTime}")
    if queueTime == 0:
        queueStr = "Unavailable"
    else:
        queueStr = queueTime
    eventManager.notify("onNotificationMessage", "Notification", f"The game server is currently full.\nYou are number {number} in line.\nAverage Wait Time: {queueStr}")


def Key(data, loginNet):
    _, key = data
    print(f" **** Received authentication key : {key}")
    loginNet.keyReceived(key)


def Response(data, loginNet):
    _, response = data
    print(f" **** Received login response : {response}")
    eventManager.notify("onHideNotification", "Connection")
    if response == LoginResponses.LOGIN_OK:
        print("Received ok from login server.")
        import client.control.world.load
        from client.scene.world import WorldScene
        if not sceneManager.exists("World"):
            sceneManager.add("World", WorldScene())
        sceneManager.changeScene("World")
        eventManager.notify("onShowLoadingScreen", "game", 6)
        eventManager.notify("onThreadStart", "Send")
        loginNet.readyToGetData()
    elif response == LoginResponses.BAD_PASSWORD:
        eventManager.notify("onNotificationMessage", "Notification", messageDB["LOGIN_INCORRECT"])
    elif response == LoginResponses.BAD_ACCOUNT:
        eventManager.notify("onNotificationMessage", "Notification", messageDB["LOGIN_INCORRECT"])
    elif response == LoginResponses.AUTHORIZATION_FAIL:
        eventManager.notify("onNotificationMessage", "Notification", messageDB["LOGIN_AUTHFAIL"])
    elif response == LoginResponses.ACCOUNT_EXISTS:
        eventManager.notify("onNotificationMessage", "Notification", messageDB["CREATION_ACCOUNT_EXISTS"])
    elif response == LoginResponses.OUTDATED:
        eventManager.notify("onNotificationMessage", "Notification", messageDB["LOGIN_OLD"])
    elif response == LoginResponses.ACCOUNT_CREATED_IPLIMIT:
        eventManager.notify("onNotificationMessage", "Notification", messageDB["CREATION_LIMIT"])
    elif response == LoginResponses.IPBANNED:
        eventManager.notify("onNotificationMessage", "Notification", messageDB["LOGIN_PERM_BAN"])
    elif response == LoginResponses.BANNED:
        eventManager.notify("onNotificationMessage", "Notification", messageDB["LOGIN_TEMP_BAN"])
    elif response == LoginResponses.ALREADY_LOGGED_IN:
        eventManager.notify("onNotificationMessage", "Notification", messageDB["LOGIN_LOGGED_IN"])
    elif response == LoginResponses.NO_TRAINERS:
        from client.scene.creation import CreationScene
        sceneManager.add("Creation", CreationScene())
        sceneManager.changeScene("Creation")
    elif response == LoginResponses.ACCOUNT_CREATED:
        eventManager.notify("onNotificationMessage", "Notification", messageDB["CREATION_SUCCESS"])
    elif response == LoginResponses.CREATION_OK:
        pass
    elif response == LoginResponses.CREATION_NAME_EXISTS:
        eventManager.notify("onNotificationMessage", "Notification", messageDB["CREATION_TRAINER_EXISTS"])
    elif response == LoginResponses.CREATION_NAME_LENGTH:
        eventManager.notify("onNotificationMessage", "Notification", messageDB["CHAR_LENGTH"])
    elif response == LoginResponses.NO_SERVERS:
        eventManager.notify("onNotificationMessage", "Notification", messageDB["LOGIN_NO_SERVER"])
    elif response == LoginResponses.ACCOUNT_CREATION_CLOSED:
        eventManager.notify("onNotificationMessage", "Notification", messageDB["CREATION_CLOSED"])
    elif response == LoginResponses.MAINTENENCE:
        eventManager.notify("onNotificationMessage", "Notification", messageDB["LOGIN_MAINTENENCE"])
    else:
        eventManager.notify("onNotificationMessage", "Notification", messageDB["LOGIN_UNKNOWN"])


def ServerInfo(data, loginNet):
    _, ip, port = data
    ip = nullstrip(ip)
    print(f" **** Received game_server information : {ip}:{port}")
    gameNetHandler.connect(ip, port)


def GotBanResponse(data, loginNet):
    _, timeStamp = data
    from datetime import datetime
    dt = datetime.fromtimestamp(timeStamp)
    eventManager.notify("onNotificationMessage", "Notification", f"This account is banned until {dt}")
    print("YOU ARE BANNED UNTIL", timeStamp)
    return
