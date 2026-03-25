# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: shared\controller\net\netbase.py
from twisted.internet.protocol import Protocol, Factory, ClientFactory, DatagramProtocol
import zlib
from twisted.internet import reactor, ssl

def compressData(data, compress=1):
    if len(data) > 12:
        data = zlib.compress(data, compress)
    return data


def decompressData(data):
    try:
        data = zlib.decompress(data)
    except Exception:
        pass

    return data


class TCPServer(Factory):
    noisy = False

    def connect(self, host, port, useSSL=True):
        self.host = host
        self.port = port
        if useSSL:
            return reactor.listenSSL(port, self, ssl.DefaultOpenSSLContextFactory("shared/eternity.key", "shared/eternity.crt"))
        else:
            return reactor.listenTCP(port, self)


class TCPClient(ClientFactory):
    noisy = False

    def connect(self, host, port, useSSL=True):
        if useSSL:
            connection = reactor.connectSSL(host, port, self, ssl.ClientContextFactory())
        else:
            connection = reactor.connectTCP(host, port, self)
        return connection


class UDPServer(DatagramProtocol):

    def input_func(self, sock, host, port, address):
        return

    def output_func(self, sock, host, port, address):
        return

    def connect_func(self, sock, host, port):
        return

    def sql_connect_func(self, sock, host, port, user, pw, db):
        return

    def quit_func(self, host, port):
        return

    def connect(self, host, port):
        self.host = host
        self.port = port
        self.socket = reactor.listenUDP(self.port, self)

    def startProtocol(self):
        self.connectionMade()

    def connectionMade(self):
        print(f"we are now bound to {self.host}:{self.port}")

    def datagramReceived(self, data, xxx_todo_changeme):
        host, port = xxx_todo_changeme
        return

    def sendData(self, data, compress=False):
        self.transport.write(data, self.lastaddress)

    def sendTo(self, destination, data, compress=False):
        self.transport.write(data, destination)

    def quit(self):
        self.socket.stopListening()
        self.quit_func(self.host, self.port)


class UDPClient(DatagramProtocol):

    def input_func(self, sock, host, port, address):
        return

    def output_func(self, sock, host, port, address):
        return

    def connect_func(self, sock, host, port):
        return

    def sql_connect_func(self, sock, host, port, user, pw, db):
        return

    def quit_func(self, host, port):
        return

    def connect(self, host, port):
        self.host = host
        self.port = port
        self.socket = reactor.listenUDP(0, self)

    def startProtocol(self):
        self.transport.connect(self.host, self.port)
        self.connectionMade()

    def connectionMade(self):
        print(f"we are now bound to {self.host}:{self.port}")

    def datagramReceived(self, data, xxx_todo_changeme1):
        host, port = xxx_todo_changeme1
        return

    def connectionRefused(self):
        print("Noone listening")

    def sendData(self, data, compress=False):
        self.transport.write(data)

    def sendTo(self, destination, data, compress=False):
        self.transport.write(data, destination)

    def quit(self):
        self.socket.stopListening()
        self.quit_func(self.host, self.port)
