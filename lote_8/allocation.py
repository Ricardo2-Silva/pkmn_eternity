# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\graphics\allocation.py
"""Memory allocation algorithm for vertex arrays and buffers.

The region allocator is used to allocate vertex indices within a vertex
domain's  multiple buffers.  ("Buffer" refers to any abstract buffer presented
by :py:mod:`pyglet.graphics.vertexbuffer`.
 
The allocator will at times request more space from the buffers. The current
policy is to double the buffer size when there is not enough room to fulfil an
allocation.  The buffer is never resized smaller.

The allocator maintains references to free space only; it is the caller's
responsibility to maintain the allocated regions.
"""

class AllocatorMemoryException(Exception):
    __doc__ = "The buffer is not large enough to fulfil an allocation.\n\n    Raised by `Allocator` methods when the operation failed due to\n    lack of buffer space.  The buffer should be increased to at least\n    requested_capacity and then the operation retried (guaranteed to\n    pass second time).\n    "

    def __init__(self, requested_capacity):
        self.requested_capacity = requested_capacity


class Allocator:
    __doc__ = "Buffer space allocation implementation."
    __slots__ = ('capacity', 'starts', 'sizes')

    def __init__(self, capacity):
        """Create an allocator for a buffer of the specified capacity.

        :Parameters:
            `capacity` : int
                Maximum size of the buffer.

        """
        self.capacity = capacity
        self.starts = []
        self.sizes = []

    def set_capacity(self, size):
        """Resize the maximum buffer size.
        
        The capaity cannot be reduced.

        :Parameters:
            `size` : int
                New maximum size of the buffer.

        """
        assert size > self.capacity
        self.capacity = size

    def alloc(self, size):
        """Allocate memory in the buffer.

        Raises `AllocatorMemoryException` if the allocation cannot be
        fulfilled.

        :Parameters:
            `size` : int
                Size of region to allocate.
               
        :rtype: int
        :return: Starting index of the allocated region.
        """
        if not size >= 0:
            raise AssertionError
        else:
            if size == 0:
                return 0
            else:
                if not self.starts:
                    if size <= self.capacity:
                        self.starts.append(0)
                        self.sizes.append(size)
                        return 0
                    raise AllocatorMemoryException(size)
                if self.starts[0] > size:
                    self.starts.insert(0, 0)
                    self.sizes.insert(0, size)
                    return 0
            free_start = self.starts[0] + self.sizes[0]
            for i, (alloc_start, alloc_size) in enumerate(zip(self.starts[1:], self.sizes[1:])):
                free_size = alloc_start - free_start
                if free_size == size:
                    self.sizes[i] += free_size + alloc_size
                    del self.starts[i + 1]
                    del self.sizes[i + 1]
                    return free_start
                if free_size > size:
                    self.sizes[i] += size
                    return free_start
                free_start = alloc_start + alloc_size

            free_size = self.capacity - free_start
            if free_size >= size:
                self.sizes[-1] += size
                return free_start
        raise AllocatorMemoryException(self.capacity + size - free_size)

    def reallocParse error at or near `POP_JUMP_IF_TRUE' instruction at offset 256_258

    def dealloc(self, start, size):
        """Free a region of the buffer.

        :Parameters:
            `start` : int
                Starting index of the region.
            `size` : int
                Size of the region.

        """
        if not size >= 0:
            raise AssertionError
        elif size == 0:
            return
        elif not self.starts:
            raise AssertionError
        else:
            for i, (alloc_start, alloc_size) in enumerate(zip(self.starts, self.sizes*())):
                p = start - alloc_start
                if p >= 0:
                    if size <= alloc_size - p:
                        break

            assert p >= 0 and size <= alloc_size - p, "Region not allocated"
            if p == 0:
                if size == alloc_size:
                    del self.starts[i]
                    del self.sizes[i]
            if p == 0:
                self.starts[i] += size
                self.sizes[i] -= size
            elif size == alloc_size - p:
                self.sizes[i] -= size
            else:
                self.sizes[i] = p
                self.starts.insert(i + 1, start + size)
                self.sizes.insert(i + 1, alloc_size - (p + size))

    def get_allocated_regions(self):
        """Get a list of (aggregate) allocated regions.

        The result of this method is ``(starts, sizes)``, where ``starts`` is
        a list of starting indices of the regions and ``sizes`` their
        corresponding lengths.

        :rtype: (list, list)
        """
        return (
         self.starts, self.sizes)

    def get_fragmented_free_size(self):
        """Returns the amount of space unused, not including the final
        free block.

        :rtype: int
        """
        if not self.starts:
            return 0
        else:
            total_free = 0
            free_start = self.starts[0] + self.sizes[0]
            for i, (alloc_start, alloc_size) in enumerate(zip(self.starts[1:], self.sizes[1:])):
                total_free += alloc_start - free_start
                free_start = alloc_start + alloc_size

            return total_free

    def get_free_size(self):
        """Return the amount of space unused.
        
        :rtype: int
        """
        if not self.starts:
            return self.capacity
        else:
            free_end = self.capacity - (self.starts[-1] + self.sizes[-1])
            return self.get_fragmented_free_size() + free_end

    def get_usage(self):
        """Return fraction of capacity currently allocated.
        
        :rtype: float
        """
        return 1.0 - self.get_free_size() / float(self.capacity)

    def get_fragmentation(self):
        """Return fraction of free space that is not expandable.
        
        :rtype: float
        """
        free_size = self.get_free_size()
        if free_size == 0:
            return 0.0
        else:
            return self.get_fragmented_free_size() / float(self.get_free_size())

    def __str__(self):
        return "allocs=" + repr(list(zip(self.starts, self.sizes)))

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, str(self))