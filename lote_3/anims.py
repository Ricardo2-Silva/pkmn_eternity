# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\system\anims.py
import pyglet, functools, math
from twisted.internet import defer, reactor

class AnimableRender(object):

    def __init__(self):
        self.anims = []
        self._scheduled = False
        self.fading = False

    def _animStep(self, dt):
        """ Steps all of the anims playing on one renderer """
        if len(self.anims) == 0:
            pyglet.clock.unschedule(self._animStep)
            self._scheduled = False
            return
        for anim in self.anims[:]:
            anim.step(dt)
            if anim.done():
                self.anims.remove(anim)
                anim.stop()
                anim.doCallbacks()

    def _startTransparency(self):
        """ When a sprite's alpha becomes 0 - 1 it needs to be rendered last- """
        self._transparent = True

    def _endTransparency(self):
        """ Restore a sprite to it's original opaque layer """
        self._transparent = False

    def fadeTo(self, duration=2, toAlpha=255, startAlpha=None):
        """ Fading changes sprite color until set alpha """
        d = defer.Deferred()
        self.fading = True
        if self.sprites:
            self._startTransparency()
            anim = MultiParallelAnim(self.sprites, FadeToOpacity, toAlpha, duration, startAlpha)
            anim += AnimCallable(d.callback, None)
            self.startAnim(anim)
        else:
            reactor.callLater(duration, d.callback, None)
        d.addCallback(self._stoppedFade)
        return d

    def fadeOut(self, duration=2):
        """ Fading changes sprite color until set alpha """
        d = defer.Deferred()
        self.fading = True
        if self.sprites:
            anim = MultiParallelAnim(self.sprites, FadeOut, duration)
            anim += AnimCallable(d.callback, None)
            self.startAnim(anim)
        else:
            reactor.callLater(duration, d.callback, None)
        d.addCallback(self._stoppedFade)
        return d

    def startAnim(self, anim):
        """ Runs an animation """
        self.anims.append(anim)
        anim.start()
        if not self._scheduled:
            self._scheduled = True
            pyglet.clock.schedule_interval(self._animStep, 0.016666666666666666)

    def removeAnim(self, anim):
        """ Stops an animation """
        self.anims.remove(anim)
        if len(self.anims) == 0:
            pyglet.clock.unschedule(self._animStep)
            self._scheduled = False

    def stopAnims(self):
        """ Forces all animations to stop """
        pyglet.clock.unschedule(self._animStep)
        self.anims.clear()
        self._scheduled = False

    def _stoppedFade(self, result=None):
        """ When stopping fade, we set the renderer is done fading """
        self.fading = False


class Animable(object):

    def __init__(self, *args, **kwargs):
        self.target = None
        self._elapsed = 0
        self._done = False
        self.duration = None
        (self.init)(*args, **kwargs)
        self.callables = []
        self.meta = False

    def reset(self):
        self._elapsed = 0
        self._done = False

    def update(self, t):
        return

    def step(self, dt):
        self._elapsed += dt
        self.update(min(1, self._elapsed / self.duration))

    def start(self):
        return

    def stop(self):
        return

    def done(self):
        return self._elapsed >= self.duration

    def doCallbacks(self):
        """ Only run when it reaches the end, will not run if force stopped """
        for callable in self.callables:
            (callable.func)(*callable.args, **callable.kwargs)

    def __add__(self, object):
        """ Adding creates a chain """
        if isinstance(object, AnimCallable):
            self.callables.append(object)
            return self
        else:
            return ChainAnims(self, object)

    def __or__(self, object):
        """ Makes them run in parallel """
        return ParallelAnims(self, object)

    def __mul__(self, value):
        if not isinstance(value, int):
            raise TypeError("Can only loop by integer values")
        if value == 1:
            return self
        else:
            if value == 0:
                return LoopAnim(self, 0)
            return LoopAnim(self, value - 1)


def MultiChainAnim(targets, function, *args, **kwargs):
    """ Helper function to combine a list of targets into a chain anim """
    return ChainAnims(*[function(target, *args, **kwargs) for target in targets])


def MultiParallelAnim(targets, function, *args, **kwargs):
    """ Helper function to combine a list of targets into a parallel anim """
    return ParallelAnims(*[function(target, *args, **kwargs) for target in targets])


class ChainAnims(Animable):
    __doc__ = " This will move from one anim to the next and wait for completion.\n        Will override their duration. "

    def init(self, *anims):
        self._current = 0
        self._last = 0
        self.anims = list(anims)
        self.meta = True
        self.set_start()

    def step(self, dt):
        self._elapsed += dt
        self.anims[self._current]._elapsed += dt
        self.update(min(1, self._elapsed / self.duration))

    def reset(self):
        Animable.reset(self)
        self._current = 0
        self._last = 0
        for anim in self.anims:
            anim.reset()

    def start(self):
        self.anims[self._current].start()

    def set_start(self):
        self.duration = sum([anim.duration for anim in self.anims])

    def update(self, t):
        anim = self.anims[self._current]
        split = anim.duration / self.duration
        sub_t = min(1, (t - self._last) / split)
        anim.update(sub_t)
        if sub_t == 1.0:
            anim.doCallbacks()
            self._current += 1
            if self._current < len(self.anims):
                self.anims[self._current].start()
            self._last += split

    def done(self):
        return self._elapsed >= self.duration

    def __add__(self, object):
        if isinstance(object, Animable):
            if isinstance(object, ChainAnims):
                self.anims.extend(object.anims)
            else:
                self.anims.append(object)
            self.set_start()
        else:
            if isinstance(object, AnimCallable):
                self.callables.append(object)
        return self

    def __reversed__(self):
        return ChainAnims(*[reversed(anim) for anim in reversed(self.anims)])


class ParallelAnims(Animable):
    __doc__ = " This updates multiple anims at once, so they can be in sync (for instance x and y).\n        Will override their duration. "

    def init(self, *anims):
        self.anims = list(anims)
        self.meta = True
        self.set_start()

    def reset(self):
        Animable.reset(self)
        for anim in self.anims:
            anim.reset()

    def set_start(self):
        self.duration = max([anim.duration for anim in self.anims])

    def start(self):
        for anim in self.anims:
            anim.start()

    def update(self, t):
        for anim in self.anims:
            if anim._done == False:
                anim.update(min(1, self._elapsed / anim.duration))
                if self._elapsed >= anim.duration:
                    anim.doCallbacks()
                    anim._done = True

    def done(self):
        return self._elapsed >= self.duration

    def __or__(self, object):
        if isinstance(object, Animable):
            if isinstance(object, ChainAnims) or isinstance(object, ParallelAnims):
                self.anims.extend(object.anims)
            else:
                self.anims.append(object)
            self.set_start()
        else:
            if isinstance(object, AnimCallable):
                self.callables.append(object)
        return self

    def __add__(self, object):
        if isinstance(object, Animable):
            self.set_start()
            anim = ChainAnims(self, object)
            anim.set_start()
            return anim
        else:
            if isinstance(object, AnimCallable):
                self.callables.append(object)
            return self


class LoopAnim(Animable):

    def init(self, anim, count=3, mode='repeat'):
        self.anim = anim
        self.mode = mode
        self._total_count = count
        self._current_count = 0
        self.meta = True
        self.duration = anim.duration

    def reset(self):
        self._elapsed = 0
        self.anim.reset()

    def update(self, t):
        self.anim._elapsed = self._elapsed
        self.anim.update(t)
        if t == 1.0:
            if self._current_count <= self._total_count:
                self.anim.doCallbacks()
                self.reset()
                if self._total_count is not 0:
                    self._current_count += 1

    def done(self):
        """ Only finishes when the count exceeds the total, if 0 will continue until canceled """
        return self._current_count > self._total_count

    def __add__(self, object):
        """ Adding creates a chain """
        if isinstance(object, AnimCallable):
            self.callables.append(object)
            return self
        else:
            return ChainAnims(self, object)


class Lerp(Animable):

    def init(self, target, attrib, start, end, duration):
        self._start = start
        self._end = end
        self.attrib = attrib
        self.target = target
        self.duration = duration
        self.diff = end - start

    def update(self, t):
        setattr(self.target, self.attrib, self._start + self.diff * t)

    def __reversed__(self):
        return Lerp(self.target, self.attrib, self._end, self._start, self.duration)


class Spiral(Animable):

    def init(self, target, direction, startAngle, radius, duration):
        self._start = list(target.position)
        self.direction = direction
        self.radius = radius
        self.target = target
        self.duration = duration
        self.i = 0
        self.angle = startAngle

    def update(self, t):
        self.i += 1
        self.angle = (self.angle + self.i) * 0.25
        new_x = self._start[0] + math.cos(self.angle) * self.radius
        new_y = self._start[1] + math.sin(self.angle) * self.radius * 0.75
        self._start[0] += math.cos(math.radians(self.direction)) * 10 * t
        self._start[1] += math.sin(math.radians(self.direction)) * t
        self.target.setPosition(new_x, new_y)


class Delay(Animable):
    __doc__ = " Dummy animable to create gaps. "

    def init(self, delay):
        self.duration = delay


class Ease(Lerp):

    def update(self, t):
        x = 1 - math.cos(t * math.pi * 0.5)
        setattr(self.target, self.attrib, self._start + self.diff * x)


class FadeIn(Animable):

    def init(self, target, duration):
        self.target = target
        self.duration = duration

    def update(self, t):
        self.target.opacity = 255 * t

    def __reversed__(self):
        return FadeOut(self.target, self.duration)


class FadeOut(Animable):

    def init(self, target, duration):
        self.target = target
        self.duration = duration
        self.start_opacity = target.opacity

    def update(self, t):
        self.target.opacity = self.start_opacity * (1 - t)

    def __reversed__(self):
        return FadeIn(self.target, self.duration)


class FadeToOpacity(Animable):

    def init(self, target, alpha, duration, startAlpha=None):
        self.target = target
        self.duration = duration
        self.target_alpha = alpha
        if startAlpha:
            self.initial_alpha = startAlpha
        else:
            self.initial_alpha = target.opacity

    def update(self, t):
        self.target.opacity = self.initial_alpha + (self.target_alpha - self.initial_alpha) * t

    def __reversed__(self):
        return FadeToOpacity(self.target, self.initial_alpha, self.duration, self.target_alpha)


class FadeColor(Animable):

    def init(self, target, color, duration, startColor=None):
        self.target = target
        self.duration = duration
        self.target_color = color
        if startColor:
            self.initial_color = startColor
        else:
            self.initial_color = target.color

    def update(self, t):
        self.target.color = (
         self.initial_color[0] + (self.target_color[0] - self.initial_color[0]) * t,
         self.initial_color[1] + (self.target_color[1] - self.initial_color[1]) * t,
         self.initial_color[2] + (self.target_color[2] - self.initial_color[2]) * t)


class FadeColorAlpha(Animable):
    __doc__ = " Fades RGBA, because they are normally separate calls,\n        saves some CPU "

    def init(self, target, color, duration, startColor=None):
        self.target = target
        self.duration = duration
        self.target_color = color
        if startColor:
            self.initial_color = startColor
        else:
            self.initial_color = (
             *target.color, target.opacity)

    def update(self, t):
        self.target._opacity = (
         self.initial_color[3] + (self.target_color[3] - self.initial_color[3]) * t,)
        self.target.color = (
         self.initial_color[0] + (self.target_color[0] - self.initial_color[0]) * t,
         self.initial_color[1] + (self.target_color[1] - self.initial_color[1]) * t,
         self.initial_color[2] + (self.target_color[2] - self.initial_color[2]) * t)


class ScaleBy(Animable):

    def init(self, target, scale, duration):
        self.target = target
        self.duration = duration
        self.target_scale = scale
        self.start_scale = target.scale
        self.delta = self.target_scale - self.start_scale

    def update(self, t):
        self.target.scale = self.start_scale + self.delta * t


class ScaleTo(Animable):

    def init(self, target, startScale, endScale, duration):
        self.target = target
        self.duration = duration
        self.target_scale = endScale
        self.start_scale = startScale
        self.delta = self.target_scale - self.start_scale

    def update(self, t):
        self.target.scale = self.start_scale + self.delta * t

    def __reversed__(self):
        return ScaleTo(self.target, self.target_scale, self.start_scale, self.duration)


class ScaleXTo(Animable):

    def init(self, target, startScale, endScale, duration):
        self.target = target
        self.duration = duration
        self.target_scale = endScale
        self.start_scale = startScale
        self.delta = self.target_scale - self.start_scale

    def update(self, t):
        self.target.scale_x = self.start_scale + self.delta * t

    def __reversed__(self):
        return ScaleXTo(self.target, self.target_scale, self.start_scale, self.duration)


class ScaleYTo(Animable):

    def init(self, target, startScale, endScale, duration):
        self.target = target
        self.duration = duration
        self.target_scale = endScale
        self.start_scale = startScale
        self.delta = self.target_scale - self.start_scale

    def update(self, t):
        self.target.scale_y = self.start_scale + self.delta * t

    def __reversed__(self):
        return ScaleYTo(self.target, self.target_scale, self.start_scale, self.duration)


class MoveTo(Animable):

    def init(self, target, coordinate, duration):
        self.target = target
        self.end_position = coordinate
        self.duration = duration
        self.start_position = self.target.position

    def update(self, t):
        self.target.update(self.start_position[0] + (self.end_position[0] - self.start_position[0]) * t, self.start_position[1] + (self.end_position[1] - self.start_position[1]) * t)


class MoveBy(MoveTo):

    def init(self, target, coordinates, duration):
        self.target = target
        self.start_position = self.target.position
        self.coordinates = coordinates
        self.duration = duration

    def start(self):
        self.start_position = self.target.position
        self.end_position = (self.start_position[0] + self.coordinates[0], self.start_position[1] + self.coordinates[1])

    def update(self, t):
        self.target.update(self.start_position[0] + (self.end_position[0] - self.start_position[0]) * t, self.start_position[1] + (self.end_position[1] - self.start_position[1]) * t)


class MoveToTarget(Animable):
    __doc__ = " This will keep source moving towards a targets position "

    def init(self, source, target, duration, offset_x=(lambda: 0), offset_y=(lambda: 0)):
        self.source = source
        self.target = target
        self.duration = duration
        self.start_position = self.target.position
        self.offset_x = offset_x
        self.offset_y = offset_y

    def update(self, t):
        self.source.update(self.start_position[0] + self.offset_x() + (self.target.x - self.start_position[0]) * t, self.start_position[1] + self.offset_y() + (self.target.y - self.start_position[1]) * t)


class MoveToTargetObject(Animable):
    __doc__ = " This will keep source moving towards a targets position "

    def init(self, source, target, duration, offset_x=(lambda: 0), offset_y=(lambda: 0)):
        self.source = source
        self.target = target
        self.duration = duration
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.mode = "ease_out"

    def update(self, t):
        sX, sY = self.source.getPosition2D()
        tX, tY = self.target.getPosition2D()
        t = modify_time(t, self.mode)
        self.source.setPosition(sX + self.offset_x() + (tX - sX) * t, sY + self.offset_y() + (tY - sY) * t)


class MoveToMovingPosition(Animable):
    __doc__ = " This will keep source moving towards a targets position "

    def init(self, source, target_position, duration, offset_x=(lambda: 0), offset_y=(lambda: 0)):
        self.source = source
        self.target = target_position
        self.duration = duration
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.mode = "lerp"

    def update(self, t):
        sX, sY = self.source.getPosition2D()
        tX, tY = self.target
        t = modify_time(t, self.mode)
        self.source.setPosition(sX + self.offset_x() + (tX - sX) * t, sY + self.offset_y() + (tY - sY) * t)


class OrbitPosition(Animable):
    __doc__ = " This will keep source moving towards a targets position "

    def init(self, source, target_position, radius, duration, speed, startAngle=0):
        self.source = source
        self.target = target_position
        self.duration = duration
        self._angle = startAngle
        self.speed = speed
        self.radius = radius

    def update(self, t):
        self._angle += 1 * self.speed
        tX, tY = self.target
        tx = tX + math.cos(self._angle) * self.radius
        ty = tY + math.sin(self._angle) * self.radius * 0.75
        self.source.setPosition(tx, ty)


class Path:

    def at(self, t):
        return


class BezierPath(Path):

    def __init__(self, a, b, ac, bc):
        self.a = a
        self.b = b
        self.ac = ac
        self.bc = bc

    def at(self, t):

        def calc(i):
            a = self.a[i]
            b = self.ac[i]
            c = self.bc[i]
            d = self.b[i]
            return (1 - t) ** 3 * a + 3 * t * (1 - t) ** 2 * b + 3 * t ** 2 * (1 - t) * c + t ** 3 * d

        return (
         calc(0), calc(1))

    def __repr__(self):
        return "Bezier( (%i,%i), (%i,%i), (%i, %i), (%i,%i) )" % (
         self.a[0], self.a[0],
         self.b[0], self.b[1],
         self.ac[0], self.ac[1],
         self.bc[0], self.bc[1])


class BezierPathObjects(Path):

    def __init__(self, source, target, ac, bc):
        self.a = source
        self.b = target
        self.ac = ac
        self.bc = bc

    def at(self, t):

        def calc(i):
            a = self.a.getCenter()[i]
            b = self.ac[i]
            c = self.bc[i]
            d = self.b.getCenter()[i]
            return (1 - t) ** 3 * a + 3 * t * (1 - t) ** 2 * b + 3 * t ** 2 * (1 - t) * c + t ** 3 * d

        return (
         calc(0), calc(1))

    def __repr__(self):
        return "Bezier( (%i,%i), (%i,%i), (%i, %i), (%i,%i) )" % (
         self.a[0], self.a[0],
         self.b[0], self.b[1],
         self.ac[0], self.ac[1],
         self.bc[0], self.bc[1])


class Bezier(Animable):
    __doc__ = "Moves a `CocosNode` object through a bezier path by modifying it's position attribute.\n    Example::\n        action = Bezier( bezier_conf.path1, 5 )   # Moves the sprite using the\n        sprite.do( action )                       # bezier path 'bezier_conf.path1'\n                                                  # in 5 seconds\n    "

    def init(self, target, bezier, duration=5, forward=True):
        """Init method
        :Parameters:
            `bezier` : bezier_configuration instance
                A bezier configuration
            `duration` : float
                Duration time in seconds
        """
        self.target = target
        self.duration = duration
        self.bezier = bezier
        self.forward = forward
        self.start()

    def start(self):
        self.start_position = self.target.position

    def update(self, t):
        if self.forward:
            p = self.bezier.at(t)
        else:
            p = self.bezier.at(1 - t)
        self.target.position = (
         self.start_position[0] + p[0],
         self.start_position[1] + p[1])

    def __reversed__(self):
        return Bezier(self.bezier, self.duration, not self.forward)


class BezierTargetObject(Animable):

    def init(self, source, target, bezier, duration=5, forward=True):
        self.source = source
        self.target = target
        self.duration = duration
        self.bezier = bezier
        self.forward = forward

    def update(self, t):
        if self.forward:
            p = self.bezier.at(t)
        else:
            p = self.bezier.at(1 - t)
        self.source.setPosition(p[0], p[1])

    def __reversed__(self):
        return Bezier(self.bezier, self.duration, not self.forward)


class AnimCallable(object):

    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __add__(self, object):
        if isinstance(object, Animable):
            object.callables.append(self)
            return object

    def __repr__(self):
        return f"AnimCallable(func={self.func}, args={self.args})"


def modify_time(t, mode):
    """ Modifies the time to a specific mode """
    if mode == "lerp":
        return t
    else:
        if mode == "ease":
            return -math.cos(t * math.pi) * 0.5 + 0.5
        else:
            if mode == "ease_in":
                return 1 - math.cos(t * math.pi * 0.5)
            if mode == "ease_out":
                return math.sin(t * math.pi * 0.5)
            if mode == "ease_quad":
                t *= 2
                if t < 1.0:
                    x = 0.5 * math.pow(t, 3)
            else:
                t -= 2
                x = 0.5 * math.pow(t, 3) + 1
            return x
