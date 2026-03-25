# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\graphics\vertexbuffer.py
"""Byte abstractions of Vertex Buffer Objects and vertex arrays.

Use :py:func:`create_buffer` or :py:func:`create_mappable_buffer` to create a
Vertex Buffer Object, or a vertex array if VBOs are not supported by the
current context.

Buffers can optionally be created "mappable" (incorporating the
:py:class:`AbstractMappable` mix-in).  In this case the buffer provides a
:py:meth:`~AbstractMappable.get_region` method which provides the most
efficient path for updating partial data within the buffer.
"""
import sys, ctypes, pyglet
from pyglet.gl import *
_enable_vbo = pyglet.options["graphics_vbo"]
_workaround_vbo_finish = False

def create_buffer(size, target=GL_ARRAY_BUFFER, usage=GL_DYNAMIC_DRAW, vbo=True):
    """Create a buffer of vertex data.

    :Parameters:
        `size` : int
            Size of the buffer, in bytes
        `target` : int
            OpenGL target buffer
        `usage` : int
            OpenGL usage constant
        `vbo` : bool
            True if a `VertexBufferObject` should be created if the driver
            supports it; otherwise only a `VertexArray` is created.

    :rtype: `AbstractBuffer`
    """
    from pyglet import gl
    if vbo:
        if gl_info.have_version(1, 5):
            if _enable_vbo:
                if not gl.current_context._workaround_vbo:
                    return VertexBufferObject(size, target, usage)
    return VertexArray(size)


def create_mappable_buffer(size, target=GL_ARRAY_BUFFER, usage=GL_DYNAMIC_DRAW, vbo=True):
    """Create a mappable buffer of vertex data.

    :Parameters:
        `size` : int
            Size of the buffer, in bytes
        `target` : int
            OpenGL target buffer
        `usage` : int
            OpenGL usage constant
        `vbo` : bool
            True if a :py:class:`VertexBufferObject` should be created if the driver
            supports it; otherwise only a :py:class:`VertexArray` is created.

    :rtype: :py:class:`AbstractBuffer` with :py:class:`AbstractMappable`
    """
    from pyglet import gl
    if vbo:
        if gl_info.have_version(1, 5):
            if _enable_vbo:
                if not gl.current_context._workaround_vbo:
                    return MappableVertexBufferObject(size, target, usage)
    return VertexArray(size)


class AbstractBuffer:
    __doc__ = "Abstract buffer of byte data.\n\n    :Ivariables:\n        `size` : int\n            Size of buffer, in bytes\n        `ptr` : int\n            Memory offset of the buffer, as used by the ``glVertexPointer``\n            family of functions\n        `target` : int\n            OpenGL buffer target, for example ``GL_ARRAY_BUFFER``\n        `usage` : int\n            OpenGL buffer usage, for example ``GL_DYNAMIC_DRAW``\n\n    "
    ptr = 0
    size = 0

    def bind(self):
        """Bind this buffer to its OpenGL target."""
        raise NotImplementedError("abstract")

    def unbind(self):
        """Reset the buffer's OpenGL target."""
        raise NotImplementedError("abstract")

    def set_data(self, data):
        """Set the entire contents of the buffer.

        :Parameters:
            `data` : sequence of int or ctypes pointer
                The byte array to set.

        """
        raise NotImplementedError("abstract")

    def set_data_region(self, data, start, length):
        """Set part of the buffer contents.

        :Parameters:
            `data` : sequence of int or ctypes pointer
                The byte array of data to set
            `start` : int
                Offset to start replacing data
            `length` : int
                Length of region to replace

        """
        raise NotImplementedError("abstract")

    def map(self, invalidate=False):
        """Map the entire buffer into system memory.

        The mapped region must be subsequently unmapped with `unmap` before
        performing any other operations on the buffer.

        :Parameters:
            `invalidate` : bool
                If True, the initial contents of the mapped block need not
                reflect the actual contents of the buffer.

        :rtype: ``POINTER(ctypes.c_ubyte)``
        :return: Pointer to the mapped block in memory
        """
        raise NotImplementedError("abstract")

    def unmap(self):
        """Unmap a previously mapped memory block."""
        raise NotImplementedError("abstract")

    def resize(self, size):
        """Resize the buffer to a new size.

        :Parameters:
            `size` : int
                New size of the buffer, in bytes

        """
        return

    def delete(self):
        """Delete this buffer, reducing system resource usage."""
        raise NotImplementedError("abstract")


class AbstractMappable:

    def get_region(self, start, size, ptr_type):
        """Map a region of the buffer into a ctypes array of the desired
        type.  This region does not need to be unmapped, but will become
        invalid if the buffer is resized.

        Note that although a pointer type is required, an array is mapped.
        For example::

            get_region(0, ctypes.sizeof(c_int) * 20, ctypes.POINTER(c_int * 20))

        will map bytes 0 to 80 of the buffer to an array of 20 ints.

        Changes to the array may not be recognised until the region's
        :py:meth:`AbstractBufferRegion.invalidate` method is called.

        :Parameters:
            `start` : int
                Offset into the buffer to map from, in bytes
            `size` : int
                Size of the buffer region to map, in bytes
            `ptr_type` : ctypes pointer type
                Pointer type describing the array format to create

        :rtype: :py:class:`AbstractBufferRegion`
        """
        raise NotImplementedError("abstract")


class VertexArray(AbstractBuffer, AbstractMappable):
    __doc__ = "A ctypes implementation of a vertex array.\n\n    Many of the methods on this class are effectively no-op's, such as\n    :py:meth:`bind`, :py:meth:`unbind`, :py:meth:`map`, :py:meth:`unmap` and\n    :py:meth:`delete`; they exist in order to present\n    a consistent interface with :py:class:`VertexBufferObject`.\n\n    This buffer type is also mappable, and so :py:meth:`get_region` can be used.\n    "

    def __init__(self, size):
        self.size = size
        self.array = ctypes.c_byte * size()
        self.ptr = ctypes.cast(self.array, ctypes.c_void_p).value

    def bind(self):
        return

    def unbind(self):
        return

    def set_data(self, data):
        ctypes.memmove(self.ptr, data, self.size)

    def set_data_region(self, data, start, length):
        ctypes.memmove(self.ptr + start, data, length)

    def map(self, invalidate=False):
        return self.array

    def unmap(self):
        return

    def get_region(self, start, size, ptr_type):
        array = ctypes.cast(self.ptr + start, ptr_type).contents
        return VertexArrayRegion(array)

    def delete(self):
        return

    def resize(self, size):
        array = ctypes.c_byte * size()
        ctypes.memmove(array, self.array, min(size, self.size))
        self.size = size
        self.array = array
        self.ptr = ctypes.cast(self.array, ctypes.c_void_p).value


class VertexBufferObject(AbstractBuffer):
    __doc__ = "Lightweight representation of an OpenGL VBO.\n\n    The data in the buffer is not replicated in any system memory (unless it\n    is done so by the video driver).  While this can improve memory usage and\n    possibly performance, updates to the buffer are relatively slow.\n\n    This class does not implement :py:class:`AbstractMappable`, and so has no\n    :py:meth:`~AbstractMappable.get_region` method.  See \n    :py:class:`MappableVertexBufferObject` for a VBO class\n    that does implement :py:meth:`~AbstractMappable.get_region`.\n    "

    def __init__(self, size, target, usage):
        global _workaround_vbo_finish
        self.size = size
        self.target = target
        self.usage = usage
        self._context = pyglet.gl.current_context
        id = GLuint()
        glGenBuffers(1, id)
        self.id = id.value
        glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
        glBindBuffer(target, self.id)
        glBufferData(target, self.size, None, self.usage)
        glPopClientAttrib()
        if pyglet.gl.current_context._workaround_vbo_finish:
            _workaround_vbo_finish = True

    def bind(self):
        glBindBuffer(self.target, self.id)

    def unbind(self):
        glBindBuffer(self.target, 0)

    def set_data(self, data):
        glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
        glBindBuffer(self.target, self.id)
        glBufferData(self.target, self.size, data, self.usage)
        glPopClientAttrib()

    def set_data_region(self, data, start, length):
        glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
        glBindBuffer(self.target, self.id)
        glBufferSubData(self.target, start, length, data)
        glPopClientAttrib()

    def map(self, invalidate=False):
        glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
        glBindBuffer(self.target, self.id)
        if invalidate:
            glBufferData(self.target, self.size, None, self.usage)
        ptr = ctypes.cast(glMapBuffer(self.target, GL_WRITE_ONLY), ctypes.POINTER(ctypes.c_byte * self.size)).contents
        glPopClientAttrib()
        return ptr

    def unmap(self):
        glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
        glUnmapBuffer(self.target)
        glPopClientAttrib()

    def __del__(self):
        try:
            if self.id is not None:
                self._context.delete_buffer(self.id)
        except:
            pass

    def delete(self):
        id = GLuint(self.id)
        glDeleteBuffers(1, id)
        self.id = None

    def resize(self, size):
        temp = ctypes.c_byte * size()
        glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
        glBindBuffer(self.target, self.id)
        data = glMapBuffer(self.target, GL_READ_ONLY)
        ctypes.memmove(temp, data, min(size, self.size))
        glUnmapBuffer(self.target)
        self.size = size
        glBufferData(self.target, self.size, temp, self.usage)
        glPopClientAttrib()


class MappableVertexBufferObject(VertexBufferObject, AbstractMappable):
    __doc__ = "A VBO with system-memory backed store.\n\n    Updates to the data via :py:meth:`set_data`, :py:meth:`set_data_region` and\n    :py:meth:`map` will be held in local memory until :py:meth:`bind` is\n    called.  The advantage is that fewer OpenGL calls are needed, increasing\n    performance.\n\n    There may also be less performance penalty for resizing this buffer.\n\n    Updates to data via :py:meth:`map` are committed immediately.\n    "

    def __init__(self, size, target, usage):
        super(MappableVertexBufferObject, self).__init__(size, target, usage)
        self.data = ctypes.c_byte * size()
        self.data_ptr = ctypes.cast(self.data, ctypes.c_void_p).value
        self._dirty_min = sys.maxsize
        self._dirty_max = 0

    def bind(self):
        super(MappableVertexBufferObject, self).bind()
        size = self._dirty_max - self._dirty_min
        if size > 0:
            if size == self.size:
                glBufferData(self.target, self.size, self.data, self.usage)
            else:
                glBufferSubData(self.target, self._dirty_min, size, self.data_ptr + self._dirty_min)
            self._dirty_min = sys.maxsize
            self._dirty_max = 0

    def set_data(self, data):
        super(MappableVertexBufferObject, self).set_data(data)
        ctypes.memmove(self.data, data, self.size)
        self._dirty_min = 0
        self._dirty_max = self.size

    def set_data_region(self, data, start, length):
        ctypes.memmove(self.data_ptr + start, data, length)
        self._dirty_min = min(start, self._dirty_min)
        self._dirty_max = max(start + length, self._dirty_max)

    def map(self, invalidate=False):
        self._dirty_min = 0
        self._dirty_max = self.size
        return self.data

    def unmap(self):
        return

    def get_region(self, start, size, ptr_type):
        array = ctypes.cast(self.data_ptr + start, ptr_type).contents
        return VertexBufferObjectRegion(self, start, start + size, array)

    def resize(self, size):
        data = ctypes.c_byte * size()
        ctypes.memmove(data, self.data, min(size, self.size))
        self.data = data
        self.data_ptr = ctypes.cast(self.data, ctypes.c_void_p).value
        self.size = size
        glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
        glBindBuffer(self.target, self.id)
        glBufferData(self.target, self.size, self.data, self.usage)
        glPopClientAttrib()
        self._dirty_min = sys.maxsize
        self._dirty_max = 0


class AbstractBufferRegion:
    __doc__ = "A mapped region of a buffer.\n\n    Buffer regions are obtained using :py:meth:`~AbstractMappable.get_region`.\n\n    :Ivariables:\n        `array` : ctypes array\n            Array of data, of the type and count requested by\n            :py:meth:`~AbstractMappable.get_region`.\n\n    "

    def invalidate(self):
        """Mark this region as changed.

        The buffer may not be updated with the latest contents of the
        array until this method is called.  (However, it may not be updated
        until the next time the buffer is used, for efficiency).
        """
        return


class VertexBufferObjectRegion(AbstractBufferRegion):
    __doc__ = "A mapped region of a VBO."

    def __init__(self, buffer, start, end, array):
        self.buffer = buffer
        self.start = start
        self.end = end
        self.array = array

    def invalidate(self):
        buffer = self.buffer
        buffer._dirty_min = min(buffer._dirty_min, self.start)
        buffer._dirty_max = max(buffer._dirty_max, self.end)


class VertexArrayRegion(AbstractBufferRegion):
    __doc__ = "A mapped region of a vertex array.\n\n    The :py:meth:`~AbstractBufferRegion.invalidate` method is a no-op but is\n    provided in order to present a consistent interface with\n    :py:meth:`VertexBufferObjectRegion`.\n    "

    def __init__(self, array):
        self.array = array


class IndirectArrayRegion(AbstractBufferRegion):
    __doc__ = "A mapped region in which data elements are not necessarily contiguous.\n\n    This region class is used to wrap buffer regions in which the data\n    must be accessed with some stride.  For example, in an interleaved buffer\n    this region can be used to access a single interleaved component as if the\n    data was contiguous.\n    "

    def __init__(self, region, size, component_count, component_stride):
        """Wrap a buffer region.

        Use the `component_count` and `component_stride` parameters to specify
        the data layout of the encapsulated region.  For example, if RGBA
        data is to be accessed as if it were packed RGB, ``component_count``
        would be set to 3 and ``component_stride`` to 4.  If the region
        contains 10 RGBA tuples, the ``size`` parameter is ``3 * 10 = 30``.

        :Parameters:
            `region` : `AbstractBufferRegion`
                The region with interleaved data
            `size` : int
                The number of elements that this region will provide access to.
            `component_count` : int
                The number of elements that are contiguous before some must
                be skipped.
            `component_stride` : int
                The number of elements of interleaved data separating
                the contiguous sections.

        """
        self.region = region
        self.size = size
        self.count = component_count
        self.stride = component_stride
        self.array = self

    def __repr__(self):
        return "IndirectArrayRegion(size=%d, count=%d, stride=%d)" % (
         self.size, self.count, self.stride)

    def __getitem__(self, index):
        count = self.count
        if not isinstance(index, slice):
            elem = index // count
            j = index % count
            return self.region.array[elem * self.stride + j]
        else:
            start = index.start or 0
            stop = index.stop
            step = index.step or 1
            if start < 0:
                start = self.size + start
            if stop is None:
                stop = self.size
            else:
                if stop < 0:
                    stop = self.size + stop
            if not step == 1:
                if not step % count == 0:
                    raise AssertionError("Step must be multiple of component count")
            data_start = start // count * self.stride + start % count
            data_stop = stop // count * self.stride + stop % count
            data_step = step * self.stride
            value_step = step * count
            value = [
             0] * ((stop - start) // step)
            stride = self.stride
            for i in range(count):
                value[i::value_step] = self.region.array[data_start + i:data_stop + i:data_step]

            return value

    def __setitem__(self, index, value):
        count = self.count
        if not isinstance(index, slice):
            elem = index // count
            j = index % count
            self.region.array[elem * self.stride + j] = value
            return
        start = index.start or 0
        stop = index.stop
        step = index.step or 1
        if start < 0:
            start = self.size + start
        elif stop is None:
            stop = self.size
        else:
            if stop < 0:
                stop = self.size + stop
        if not step == 1:
            assert step % count == 0, "Step must be multiple of component count"
            data_start = start // count * self.stride + start % count
            data_stop = stop // count * self.stride + stop % count
            if step == 1:
                data_step = self.stride
                value_step = count
                for i in range(count):
                    self.region.array[data_start + i:data_stop + i:data_step] = value[i::value_step]

        else:
            data_step = step // count * self.stride
        self.region.array[data_start:data_stop:data_step] = value

    def invalidate(self):
        self.region.invalidate()
