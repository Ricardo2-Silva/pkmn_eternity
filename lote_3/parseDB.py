# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\net\login\parseDB.py
"""
Created on Jul 12, 2017

@author: Admin
"""
from shared.container.net import lmsg
import client.control.net.login.parse as login

class LoginPacketDB:

    def __init__(self):
        self.func = {(lmsg.Key): (login.Key), 
         (lmsg.Response): (login.Response), 
         (lmsg.ServerInfo): (login.ServerInfo), 
         (lmsg.Ban): (login.GotBanResponse), 
         (lmsg.QueueInfo): (login.QueueInfo)}
