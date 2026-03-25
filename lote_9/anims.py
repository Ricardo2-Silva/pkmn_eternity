# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: rabbyt\anims.py
"""
This module provides *Animators* (or *anims* for short) for Rabbyt.

*Anims* are little objects that can implement a movement function, primarily
meant to animate sprites.  The movement functions are all implemented in C, so
your sprites can be animated without any python call overhead.

For example, to linearly interpolate a sprite from x=0 to x=100 over the next
second, you can do this:

    .. sourcecode:: python

        sprite.x = rabbyt.lerp(0, 100, dt=1)

Looks like magic?

It is!  Sorta...

The ``Sprite`` class's ``x`` attribute is really a property.  If you
assign an anim to it, that anim will be called for it's value every time the
sprite needs it's x position.  Nearly all of ``Sprite``'s properties work
like this.

Anims support various arithmatic opperations.  If you add two together,
or add one with a constant number, a new anim will be returned.  Here is a
rather contrived example of doing that:

    .. sourcecode:: python

        sprite.x = rabbyt.lerp(0, 100, dt=1) + 20

(In this case, you would be better off interpolating from 20 to 120, but
whatever.)

Here is a more useful example:

    .. sourcecode:: python

        sprite2.x = sprite1.attrgetter('x') + 20

That will cause sprite2's x position to always be 20 more than sprite1's x
position.  (``Sprite.attrgetter()`` returns an anim that gets an attribute.)
This all happens in compiled C code, without any python call overhead.  (That
means you can have thousands of sprites doing this and it will still be fast.)

But sometimes you don't really need that much speed.  You can use any python
function as an anim as well.  This example does the same as the last one:

    .. sourcecode:: python

        sprite2.x = lambda: sprite1.x + 20

(``Sprite.x`` will automatically wrap the function in an ``AnimPyFunc``
instance behind the scenes.)

Using anims in your own classes
-------------------------------

You can use anims in your own class by subclassing from ``Animable`` and using
the ``anim_slot`` descriptor.  For example, a simple sprite class could start
like this:

    .. sourcecode:: python

        class MySprite(rabbyt.Animable):
            x = rabbyt.anim_slot()
            y = rabbyt.anim_slot()
            xy = rabbyt.swizzle('x', 'y')

The ``x``, ``y``, and ``xy`` attributes will behave the just like they do in
rabbyt's ``Sprite`` class.

"""
from __future__ import division
__credits__ = '\nCopyright (C) 2007  Matthew Marshall\n\nPermission is hereby granted, free of charge, to any person obtaining a copy\nof this software and associated documentation files (the "Software"), to deal\nin the Software without restriction, including without limitation the rights\nto use, copy, modify, merge, publish, distribute, sublicense, and/or sell\ncopies of the Software, and to permit persons to whom the Software is\nfurnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in\nall copies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\nIMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\nFITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\nAUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\nLIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\nOUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN\nTHE SOFTWARE.\n'
__author__ = "Matthew Marshall <matthew@matthewmarshall.org>"
from rabbyt._anims import *
import warnings, operator

class swizzle(object):
    __doc__ = "\n    ``swizzle(..., factory=tuple)``\n\n    ``swizzle`` is a descriptor used to create a shortcut for getting/setting\n    multiple attributes at once.  For example, the ``xy`` attribute for\n    ``BaseSprite`` was created by defining this in the class::\n\n        xy = swizzle('x', 'y')\n\n    If ``factory`` is given it will be used to build the value when the sizzle\n    is read.  It is passed a sequence of the values.  For example, if you're\n    using a vector class you can do this::\n\n        xy = swizzle('x', 'y', factory=MyVector)\n\n    The factory function will be passed a tuple of the assigned values as a\n    single argument.\n\n    ``swizzle`` works with any attribute in any new-style class.\n    "

    def __init__(self, *names, **kwargs):
        self.names = names
        self.factory = kwargs.pop("factory", tuple)
        self._getter = (operator.attrgetter)(*names)
        doc = "swizzle for " + ", ".join("``%s``" % s for s in names)
        self.__doc__ = kwargs.pop("doc", doc)
        if kwargs:
            raise TypeError("Unexpected keyword argument(s): %r" % kwargs.keys())

    def __get__(self, obj, type):
        if obj is None:
            return self
        else:
            return self.factory(self._getter(obj))

    def __set__(self, obj, value):
        names = self.names
        i = 0
        for v in value:
            setattr(obj, names[i], v)
            i += 1


class AnimableMeta(type):

    def __new__(cls, name, bases, dict):
        animable_subclasses = [b for b in bases if hasattr(b, "_anim_slot_descriptors")]
        if len(animable_subclasses) > 1:
            raise TypeError("Cannot subclass from more than one Animable class.")
        new_class = type.__new__(cls, name, bases, dict)
        inherited_descriptors = []
        if animable_subclasses:
            a_cls = animable_subclasses[0]
            if hasattr(a_cls, "_anim_slot_descriptors"):
                inherited_descriptors.extend(a_cls._anim_slot_descriptors)
        new_descriptors = [v for v in dict.values() if isinstance(v, anim_slot)]
        used_indexes = set()
        for d in inherited_descriptors + new_descriptors:
            if d.index != -1:
                if d.index in used_indexes:
                    raise ValueError("Duplicate descriptor index %i" % d.index)
                else:
                    used_indexes.add(d.index)

        index = 0
        for d in new_descriptors:
            if d.index == -1:
                while index in used_indexes:
                    index += 1

                d.index = index
                used_indexes.add(index)
                index += 1

        new_class._anim_slot_descriptors = inherited_descriptors + new_descriptors
        new_class._anim_slot_descriptors.sort(key=(lambda d: d.index))
        new_class._anim_slot_descriptor_names = [n for n in dir(new_class) if isinstance(getattr(new_class, n), anim_slot)]
        if len(new_class._anim_slot_descriptors):
            if not len(new_class._anim_slot_descriptors) == max(used_indexes) + 1:
                raise AssertionError
        for name in new_class._anim_slot_descriptor_names:
            setattr(new_class, name, getattr(new_class, name))

        return new_class


class Animable(cAnimable, metaclass=AnimableMeta):
    __doc__ = "\n    ``Animable(**kwargs)``\n\n    This is a base class for making classes with propertys that work with anims.\n\n    For example, you can create a custom sprite class like this::\n\n        class MySprite(Animable):\n            x = anim_slot()\n            y = anim_slot()\n            xy = swizzle('x', 'y')\n            rot = anim_slot()\n\n    The ``x``, ``y``, ``xy``, and ``rot`` attributes will work just like the\n    default rabbyt ``Sprite`` class.\n\n    All ``anim_slot`` and ``swizzle`` attribute names can be passed as keyword\n    arguments to Animable.__init__::\n\n        sprite = MySprite(xy=(10,100), rot=90)\n    "
    __metaclass__ = AnimableMeta

    def __init__(self, **kwargs):
        cAnimable.__init__(self)
        for desc in self._anim_slot_descriptors:
            slot = desc.get_slot(self)
            slot.value = desc.default_value

        for name, value in kwargs.items():
            if name in self._anim_slot_descriptor_names or hasattr(self.__class__, name):
                setattr(self, name, value)
            else:
                raise ValueError("unexpected keyword argument %r" % name)

    def end_data_migrate(self, attrs):
        self.set_anim_slot_locations()
        if hasattr(self, "in_array"):
            if self.in_array is not None:
                self.set_anim_slot_locations_in_array(attrs.keys())
        for name, value in attrs.items():
            setattr(self, name, value)

    def attrgetter(self, name):
        """
        ``attrgetter(name)``

        Returns an anim that returns the value of the given attribute name.

        Perhaps this is easiest to see with an example.  The following two lines
        will both do the same thing, only the second is much, much faster:

            .. sourcecode:: python

                sprite.x = lambda: other_sprite.x

                sprite.x = other_sprite.attrgetter("x")

        The anim returned by attrgetter is implemented in C and will retrieve
        the value without doing a python attribute lookup.

        This works for any attribute that you can assign an anim to.

        ``swizzle`` descriptors are properly handled.
        """
        class_attr = getattr(self.__class__, name)
        if isinstance(class_attr, anim_slot):
            return AnimSlotReader(class_attr.get_slot(self))
        if isinstance(class_attr, swizzle):
            return tuple(self.attrgetter(n) for n in class_attr.names)


extend_types = dict(constant=1, extrapolate=2, repeat=3, reverse=4)

class IncompleteInterpolateAnim(IncompleteAnimBase):
    __doc__ = "\n    An instance of IncompleteInterpolateAnim is returned by ``lerp`` etc. when\n    they are not given all of the arguments needed to operate.  These arguments\n    will be filled in when it is added to an anim slot.\n\n    For example:\n\n        sprite.x = lerp(end=10, dt=2)\n\n    Calling ``lerp(end=10, dt=2)`` returns an incomplete anim, because both\n    ``start`` and ``startt`` are missing.  When the incomplete anim is assigned\n    to ``sprite.x``, ``start`` is filled in with the previous value of\n    ``sprite.x`` and ``startt`` is filled in with the current time.\n    "

    def __init__(self, kwargs, missing):
        self.kwargs = kwargs
        self.missing = missing

    def complete(self, **new_args):
        """
        ``complete(self, **new_args)``

        Returns a new anim, using ``new_args`` to fill it in.

        This method doesn't modify the IncompleteInterpolateAnim.

        If the anim still isn't complete, a new IncompleteInterpolateAnim is
        returned.
        """
        kwargs = self.kwargs.copy()
        missing = self.missing.copy()
        for name in self.missing:
            if name in new_args:
                missing.remove(name)
                kwargs[name] = new_args[name]

        if "endt" not in kwargs:
            if "startt" in kwargs:
                if "dt" in kwargs:
                    kwargs["endt"] = kwargs["startt"] + kwargs["dt"]
                    missing.remove("endt")
        if "startt" not in kwargs:
            if "endt" in kwargs:
                if "dt" in kwargs:
                    kwargs["startt"] = kwargs["endt"] - kwargs["dt"]
                    missing.remove("startt")
        if "t" in kwargs:
            missing.difference_update(set(('startt', 'endt')))
            if isinstance(kwargs["t"], IncompleteAnimBase):
                complete_args = dict(start=0, end=1)
                kwargs["t"] = (kwargs["t"].complete)(**complete_args)
        if missing:
            return self.__class__(kwargs, missing)
        else:
            kwargs.pop("dt", None)
            return InterpolateAnim(**kwargs)

    def force_complete(self, **new_args):
        """
        ``force_complete(self, **new_args)``

        Calls ``complete(**new_args)``, raising an exception if the result is
        still incomplete.

        This method will also fill in ``startt`` with the result of
        ``get_time()``.
        """
        if "startt" not in new_args:
            new_args["startt"] = get_time()
        else:
            value = (self.complete)(**new_args)
            if isinstance(value, IncompleteAnimBase):
                raise ValueError("Unable to complete missing arguments: " + str(tuple(value.missing)))
            else:
                return value


def _handle_time_args(startt, endt, dt):
    if startt is None:
        startt = get_time()
    else:
        if endt is None:
            if dt is None:
                raise ValueError("Either dt or endt must be given.")
            endt = startt + dt
        assert startt < endt
    return (startt, endt)


def _interpolate(method, start=None, end=None, startt=None, endt=None, dt=None, t=None, extend='constant'):
    try:
        if start is not None:
            iter(start)
        else:
            if end is not None:
                iter(end)
            if start is None:
                if end is None:
                    raise TypeError
    except TypeError:
        args = dict(start=start, end=end, startt=startt, endt=endt, dt=dt, t=t,
          extend=extend,
          method=method)
        args = dict((k, v) for k, v in args.items() if v is not None)
        missing = set(('start', 'end', 'startt', 'endt', 'extend', 'method')).difference(set(args.keys()))
        return IncompleteInterpolateAnim(args, missing).complete()
    else:
        if start is None:
            start = [
             None] * len(end)
        if end is None:
            end = [
             None] * len(start)
        return [_interpolate(method, s, e, startt, endt, dt, t, extend) for s, e in zip(start, end)]


def lerp(start=None, end=None, startt=None, endt=None, dt=None, t=None, extend='constant'):
    """
    ``lerp(start, end, [startt,] [endt,] [dt,] [t,] [extend])``

    Linearly interpolates between ``start`` and ``end`` as time moves from
    ``startt`` to ``endt``.

    ``startt`` is the time to start.

    To specify the ending time, use either ``endt``, which is the absolute
    time, or ``dt``, which is relative from ``startt``.

    For example, the following are equivalent:

        .. sourcecode:: python

            lerp(0, 1, rabbyt.get_time(), endt=rabbyt.get_time()+1)
            lerp(0, 1, rabbyt.get_time(), dt=1)

    ``extend`` is a string defining what to do before ``startt`` and after
    ``endt``. Possible values are:

        ``"constant"``
            The value will be locked between ``start`` and ``end``.  *This is
            the default.*

        ``"extrapolate"``
            After the value hits ``end`` it just keeps going!

        ``"repeat"``
            After the value hits ``end`` it will start over again at
            ``start``.

        ``"reverse"``
            After the value hits ``end`` it will reverse, moving back to
            ``start``.

    Check out the ``extend_modes.py`` example to see all four side by side.

    If any required values are omitted, ``lerp`` will return an
    ``IncompleteInterpolateAnim`` instance, which will have the missing values
    filled in when assigned to an anim slot.  So instead of doing this:

        .. sourcecode:: python

            # long way:
            sprite.x = lerp(start=sprite.x, end=10, startt=get_time(), dt=1)

    ... you could do this:

        .. sourcecode:: python

            # shortcut with same result:
            sprite.x = lerp(end=10, dt=1)

    Both ``start`` and ``startt`` are missing, so ``lerp`` returns an incomplete
    anim.  When it is assigned to ``sprite.x``, ``start`` is filled in with
    the previous value of ``sprite.x`` and ``startt`` is filled in with the
    current time.

    ``start`` and ``end`` can either be numbers, or tuples of numbers.  If
    they are tuples, a tuple of anims will be returned.  For example, this
    line:

        .. sourcecode:: python

            sprite.rgba = lerp((0,1,0,.5), (1,0,1,1), dt=1)

    is equivalent to this:

        .. sourcecode:: python

            sprite.red   = lerp(0, 1, dt=1)
            sprite.green = lerp(1, 0, dt=1)
            sprite.blue  = lerp(0, 1, dt=1)
            sprite.alpha = lerp(.5,1, dt=1)

    TODO document t [startt and endt (mostly) ignored when used]

    """
    return _interpolate("lerp", start, end, startt, endt, dt, t, extend)


def ease(start=None, end=None, startt=None, endt=None, dt=None, t=None, extend='constant', method='sine'):
    """
    ``ease(start, end, [startt,] [endt,] [dt,] [t,] [extend,] [method,])``

    Interpolates between ``start`` and ``end``, easing in and out of the
    transition.

    ``method`` is the easing method to use.  It defaults to "sine".  See the
    "interpolation.py" example in the rabbyt source distribution for more.

    TODO List the valid interpolation methods here (perhaps with descriptions.)

    All other argments are identical to ``lerp``.
    """
    return _interpolate("ease_" + method, start, end, startt, endt, dt, t, extend)


def ease_in(start=None, end=None, startt=None, endt=None, dt=None, t=None, extend='constant', method='sine'):
    """
    ``ease_in(start, end, [startt,] [endt,] [dt,] [t,] [extend,] [method,])``

    Interpolates between ``start`` and ``end``, easing into the
    transition.  (So the movement starts out slow.)

    See the docs for ``ease`` for more information.
    """
    return _interpolate("ease_in_" + method, start, end, startt, endt, dt, t, extend)


def ease_out(start=None, end=None, startt=None, endt=None, dt=None, t=None, extend='constant', method='sine'):
    """
    ``ease_out(start, end, [startt,] [endt,] [dt,] [t,] [extend,] [method,])``

    Interpolates between ``start`` and ``end``, easing out of the
    transition.  (The movement starts fast and ends slow.)

    See the docs for ``ease`` for more information.
    """
    return _interpolate("ease_out_" + method, start, end, startt, endt, dt, t, extend)


def exponential(start=None, end=None, startt=None, endt=None, dt=None, t=None, extend='constant'):
    """
    ``exponential`` is deprecated.  Use ``ease_in(... method='exponential')``
    instead.
    """
    warnings.warn("exponential is deprecated.  Use ease_in(... method='exponential') instead.", stacklevel=2)
    return ease_in(start, end, startt, endt, dt, t, extend, "exponential")


def cosine(start=None, end=None, startt=None, endt=None, dt=None, t=None, extend='constant'):
    """
    ``cosine`` is deprecated.  Use ``ease_out`` instead.
    """
    warnings.warn("cosine is deprecated.  Use ease_out instead.", stacklevel=2)
    return ease_out(start, end, startt, endt, dt, t, extend, "sine")


def sine(start=None, end=None, startt=None, endt=None, dt=None, t=None, extend='constant'):
    """
    ``sine`` is deprecated.  Use ``ease_in`` instead.
    """
    warnings.warn("sine is deprecated. Use ease_in instead.", stacklevel=2)
    return ease_in(start, end, startt, endt, dt, t, extend, "sine")


def wrap(bounds, parent, static=True):
    """
    ``wrap(bounds, parent, static=True) -> AnimWrap or tuple of AnimWraps``

    Wraps a parent ``Anim`` to fit within ``bounds``.  ``bounds`` should be an
    object that supports item access for at least ``bounds[0]`` and
    ``bounds[1]``.  (A list or tuple with a length of 2 would work great.)

    If ``static`` is ``True``, ``bounds`` is only read once and stored in C
    variables for fast access. This is much faster, but doesn't work if
    ``bounds`` is an object you wish to mutate.

    If ``parent`` is a iterable, a tuple of anims will be returned instead
    of a single one.  (This is similar to ``lerp()``.)
    """
    try:
        iter(parent)
    except TypeError:
        return AnimWrap(bounds, parent, static)
    else:
        return tuple([AnimWrap(bounds, p, static) for p in parent])


def bezier3(p0, p1, p2, p3, startt=None, endt=None, dt=None, t=None, extend='constant'):
    """
    ``bezier3(p0, p1, p2, p3, [startt,] [endt,] [dt,] [t,] [extend])``

    Interpolates along a cubic bezier curve as defined by ``p0``, ``p1``,
    ``p2``, and ``p3``.

    ``startt``, ``endt``, ``dt``, ``t``, and ``extend`` work as in ``lerp()``.

    ``p0``, ``p1``, ``p2``, and ``p3`` can be tuples, but they must all be the
    same length.
    """
    extend = extend_types[extend]
    if t is None:
        startt, endt = _handle_time_args(startt, endt, dt)
    else:
        startt = endt = 0
    try:
        [iter(p) for p in [p0, p1, p2, p3]]
    except TypeError:
        return AnimStaticCubicBezier(p0, p1, p2, p3, startt, endt, t, extend)
    else:
        return [AnimStaticCubicBezier(p0, p1, p2, p3, startt, endt, t, extend) for p0, p1, p2, p3 in zip(p0, p1, p2, p3)]


class IncompleteChainAnim(IncompleteAnimBase):

    def __init__(self, anims):
        self.anims = anims

    def complete(self, **new_args):
        anims = []
        complete = True
        for anim in self.anims:
            if isinstance(anim, IncompleteAnimBase):
                anim = (anim.complete)(**new_args)
            elif isinstance(anim, IncompleteAnimBase):
                if "end" in anim.kwargs:
                    new_args["start"] = anim.kwargs["end"]
                else:
                    new_args.pop("start", None)
                if "endt" in anim.kwargs:
                    new_args["startt"] = anim.kwargs["endt"]
                else:
                    new_args.pop("startt", None)
                complete = False
            else:
                new_args["start"] = anim.end
                new_args["startt"] = anim.endt
            anims.append(anim)

        if complete:
            return ChainAnim(anims)
        else:
            return IncompleteChainAnim(anims)

    def force_complete(self, **new_args):
        if "startt" not in new_args:
            new_args["startt"] = get_time()
        else:
            chain = (self.complete)(**new_args)
            if isinstance(chain, IncompleteAnimBase):
                raise ValueError("Unable to complete chain")
            else:
                return chain


def chain(*anims):
    """
    ``chain(...)``

    ``chain`` provides a way to automatically run anims in a sequence.  For
    example, you can move a sprite in a square like this::

        now = get_time()
        sprite.xy = chain(
                lerp(( 0, 0), (10, 0),    now, now+10),
                lerp((10, 0), (10,10), now+10, now+20),
                lerp((10,10), ( 0,10), now+20, now+30),
                lerp(( 0,10), ( 0, 0), now+30, now+40))

    If you ommit the ``start`` and ``startt`` arguments of lerp, they will
    be filled in from ``end`` and ``endt`` of the the previous lerp.  So
    this is a less verbose way to do the same thing as above::

        sprite.xy = chain(
                lerp((0,0), (10, 0), dt=10),
                lerp(end=(10,10), dt=10),
                lerp(end=( 0,10), dt=10),
                lerp(end=( 0, 0), dt=10))

    Currently, ``lerp``, ``ease``, ``ease_in``, and ``ease_out`` are the only
    anims that can be used with ``chain``.
    """
    sequence_count = 0
    sequence_lens = set()
    for anim in anims:
        try:
            sequence_lens.add(len(anim))
            sequence_count += 1
        except TypeError:
            pass

    if sequence_count:
        if sequence_count != len(anims):
            raise ValueError("Arguments must be either all Anims or all sequences!  (%d out of %d passed arguments were sequences.)" % (
             sequence_count, len(anims)))
        if len(sequence_lens) != 1:
            raise ValueError("All sequence arguments must be the same length! (Lengths found were: %r)" % tuple(sequence_lens))
        count = sequence_lens.pop()
        return tuple(chain(*(a[i] for a in anims)) for i in range(count))
    else:
        return IncompleteChainAnim(anims).complete()


def rate(target):
    """
    ``rate(anim)``

    Returns an anim that tracks the rate of change in another anim.

    TODO example and full disclosure of deficiencies
    """
    return AnimRate(target)


__docs_all__ = "set_time get_time add_time lerp ease ease_in ease_out chain wrap Anim AnimConst AnimPyFunc AnimProxy ".split()
