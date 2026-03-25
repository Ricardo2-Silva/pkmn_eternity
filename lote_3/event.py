# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\events\event.py
from client.data.events.event import CallbackPriority
import traceback

def Debug(msg, _type='Message'):
    print(f"     {_type}: {msg}")


class InterfaceDynamicEventListener:
    __doc__ = " stores Callbacks for a specific event. "

    def __init__(self):
        self.callbacks = {}
        self.prevents = []

    def addCallback(self, evName, function, *args):
        (self.addCallbackWithPriority)(evName, CallbackPriority.ON_START, function, *args)

    def addCallbackStart(self, evName, function, *args):
        (self.addCallbackWithPriority)(evName, CallbackPriority.ON_START, function, *args)

    def addCallbackEnd(self, evName, function, *args):
        (self.addCallbackWithPriority)(evName, CallbackPriority.ON_END, function, *args)

    def deleteCallback(self, evName):
        if evName not in self.callbacks:
            raise Exception("A callback for the event " + evName + " was not found.")
        del self.callbacks[evName]

    def addCallbackWithPriority(self, evName, priority, function, *args):
        if priority not in CallbackPriority.ALL_PRIORITY:
            raise Exception("Wrong priority for callback.")
        else:
            if evName not in self.callbacks:
                self.callbacks[evName] = {(CallbackPriority.ON_START): [], (CallbackPriority.ON_END): []}
            if (function, args) in self.callbacks[evName][priority]:
                raise Exception("A callback for the event " + evName + "already exist with same arguments.")
        self.callbacks[evName][priority].insert(0, (function, args))

    def hasCallbackOnEvent(self, evName):
        if evName in self.callbacks:
            return True
        else:
            return False

    def hasCallback(self, evName, priority, func, *args):
        if evName in self.callbacks:
            if (
             func, args) in self.callbacks[evName][priority]:
                return True
        return False

    def isEventIgnored(self, evName):
        return evName in self.prevents

    def preventDefault(self, *evNames):
        """ Do not call basic function of this event name. """
        for evName in evNames:
            self.prevents.append(evName)

    def allowDefault(self, *evNames):
        for evName in evNames:
            if evName in self.prevents:
                self.prevents.remove(evName)

    def notify(self, name, *args):
        """ Notify the eventManager of an event. """
        global eventManager
        (eventManager.notify)(name, *args)

    def runCallback(self, evName, *args):
        if evName not in self.prevents:
            if hasattr(self, evName):
                (getattr(self, evName))(*args)
        ran = False
        if evName in self.callbacks:
            for priority in CallbackPriority.ALL_PRIORITY:
                for func, cArgs in self.callbacks[evName][priority]:
                    func(*args + cArgs)
                    ran = True

        return ran


class EventManager:
    __doc__ = "\n    This object is responsible for coordinating most communication between the\n    Model, View, and Controller.\n    "

    def __init__(self):
        from weakref import WeakKeyDictionary
        self.listeners = WeakKeyDictionary()
        self.eventQueue = []

    def registerListener(self, listener):
        if isinstance(listener, InterfaceDynamicEventListener):
            raise Exception("The listener is refused. It's instance of InterfaceDynamicEventListener.")
        self.listeners[listener] = 1

    def unregisterListener(self, listener):
        if listener in self.listeners.keys():
            del self.listeners[listener]

    def notify(self, name, *args, **kwargs):
        """ If safe is set to 1, then the event will be sent during the main loop
                During the tickevent event. (By default)"""
        for listener in self.listeners.keys():
            if hasattr(listener, name):
                (getattr(listener, name))(*args, **kwargs)

    def any_listeners(self, name):
        """ Check if we have any listeners for this event"""
        for listener in self.listeners.keys():
            if hasattr(listener, name):
                return True

        return False


eventManager = EventManager()
import pyglet

class PygletEventManager(pyglet.event.EventDispatcher):
    return


PygletEventManager.register_event_type("onCharSelection")
eventDispatcher = PygletEventManager()
# global eventDispatcher ## Warning: Unused global
