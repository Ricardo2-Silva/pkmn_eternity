# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: twisted\python\context.py
"""
Dynamic pseudo-scoping for Python.

Call functions with context.call({key: value}, func); func and
functions that it calls will be able to use 'context.get(key)' to
retrieve 'value'.

This is thread-safe.
"""
from __future__ import division, absolute_import
from threading import local
from twisted.python._oldstyle import _oldStyle
defaultContextDict = {}
setDefault = defaultContextDict.__setitem__

@_oldStyle
class ContextTracker:
    __doc__ = '\n    A L{ContextTracker} provides a way to pass arbitrary key/value data up and\n    down a call stack without passing them as parameters to the functions on\n    that call stack.\n\n    This can be useful when functions on the top and bottom of the call stack\n    need to cooperate but the functions in between them do not allow passing the\n    necessary state.  For example::\n\n        from twisted.python.context import call, get\n\n        def handleRequest(request):\n            call({\'request-id\': request.id}, renderRequest, request.url)\n\n        def renderRequest(url):\n            renderHeader(url)\n            renderBody(url)\n\n        def renderHeader(url):\n            return "the header"\n\n        def renderBody(url):\n            return "the body (request id=%r)" % (get("request-id"),)\n\n    This should be used sparingly, since the lack of a clear connection between\n    the two halves can result in code which is difficult to understand and\n    maintain.\n\n    @ivar contexts: A C{list} of C{dict}s tracking the context state.  Each new\n        L{ContextTracker.callWithContext} pushes a new C{dict} onto this stack\n        for the duration of the call, making the data available to the function\n        called and restoring the previous data once it is complete..\n    '

    def __init__(self):
        self.contexts = [defaultContextDict]

    def callWithContext(self, newContext, func, *args, **kw):
        """
        Call C{func(*args, **kw)} such that the contents of C{newContext} will
        be available for it to retrieve using L{getContext}.

        @param newContext: A C{dict} of data to push onto the context for the
            duration of the call to C{func}.

        @param func: A callable which will be called.

        @param *args: Any additional positional arguments to pass to C{func}.

        @param **kw: Any additional keyword arguments to pass to C{func}.

        @return: Whatever is returned by C{func}

        @raise: Whatever is raised by C{func}.
        """
        self.contexts.append(newContext)
        try:
            return func(*args, **kw)
        finally:
            self.contexts.pop()

    def getContext(self, key, default=None):
        """
        Retrieve the value for a key from the context.

        @param key: The key to look up in the context.

        @param default: The value to return if C{key} is not found in the
            context.

        @return: The value most recently remembered in the context for C{key}.
        """
        for ctx in reversed(self.contexts):
            try:
                return ctx[key]
            except KeyError:
                pass

        return default


class ThreadedContextTracker(object):

    def __init__(self):
        self.storage = local()

    def currentContext(self):
        try:
            return self.storage.ct
        except AttributeError:
            ct = self.storage.ct = ContextTracker()
            return ct

    def callWithContext(self, ctx, func, *args, **kw):
        return (self.currentContext().callWithContext)(ctx, func, *args, **kw)

    def getContext(self, key, default=None):
        return self.currentContext().getContext(key, default)


def installContextTracker(ctr):
    global call
    global get
    global theContextTracker
    theContextTracker = ctr
    call = theContextTracker.callWithContext
    get = theContextTracker.getContext


installContextTracker(ThreadedContextTracker())
