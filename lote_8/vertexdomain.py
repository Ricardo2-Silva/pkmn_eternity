# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\graphics\vertexdomain.py
"""Manage related vertex attributes within a single vertex domain.

A vertex "domain" consists of a set of attribute descriptions that together
describe the layout of one or more vertex buffers which are used together to
specify the vertices in a primitive.  Additionally, the domain manages the
buffers used to store the data and will resize them as necessary to accommodate
new vertices.

Domains can optionally be indexed, in which case they also manage a buffer
containing vertex indices.  This buffer is grown separately and has no size
relation to the attribute buffers.

Applications can create vertices (and optionally, indices) within a domain
with the :py:meth:`VertexDomain.create` method.  This returns a
:py:class:`VertexList` representing the list of vertices created.  The vertex
attribute data within the group can be modified, and the changes will be made
to the underlying buffers automatically.

The entire domain can be efficiently drawn in one step with the
:py:meth:`VertexDomain.draw` method, assuming all the vertices comprise
primitives of the same OpenGL primitive mode.
"""
import re, ctypes
from pyglet.gl import *
from pyglet.graphics import allocation, vertexattribute, vertexbuffer
_usage_format_re = re.compile("\n    (?P<attribute>[^/]*)\n    (/ (?P<usage> static|dynamic|stream|none))?\n", re.VERBOSE)
_gl_usages = {
 'static': GL_STATIC_DRAW, 
 'dynamic': GL_DYNAMIC_DRAW, 
 'stream': GL_STREAM_DRAW, 
 'none': GL_STREAM_DRAW_ARB}

def _nearest_pow2(v):
    v -= 1
    v |= v >> 1
    v |= v >> 2
    v |= v >> 4
    v |= v >> 8
    v |= v >> 16
    return v + 1


def create_attribute_usage(fmt):
    """Create an attribute and usage pair from a format string.  The
    format string is as documented in `pyglet.graphics.vertexattribute`, with
    the addition of an optional usage component::

        usage ::= attribute ( '/' ('static' | 'dynamic' | 'stream' | 'none') )?

    If the usage is not given it defaults to 'dynamic'.  The usage corresponds
    to the OpenGL VBO usage hint, and for ``static`` also indicates a
    preference for interleaved arrays.  If ``none`` is specified a buffer
    object is not created, and vertex data is stored in system memory.

    Some examples:

    ``v3f/stream``
        3D vertex position using floats, for stream usage
    ``c4b/static``
        4-byte color attribute, for static usage

    :return: attribute, usage
    """
    match = _usage_format_re.match(fmt)
    attribute_format = match.group("attribute")
    attribute = vertexattribute.create_attribute(attribute_format)
    usage = match.group("usage")
    if usage:
        vbo = not usage == "none"
        usage = _gl_usages[usage]
    else:
        usage = GL_DYNAMIC_DRAW
        vbo = True
    return (attribute, usage, vbo)


def create_domain(*attribute_usage_formats):
    """Create a vertex domain covering the given attribute usage formats.
    See documentation for :py:func:`create_attribute_usage` and
    :py:func:`pyglet.graphics.vertexattribute.create_attribute` for the grammar
    of these format strings.

    :rtype: :py:class:`VertexDomain`
    """
    attribute_usages = [create_attribute_usage(f) for f in attribute_usage_formats]
    return VertexDomain(attribute_usages)


def create_indexed_domain(*attribute_usage_formats):
    """Create an indexed vertex domain covering the given attribute usage
    formats.  See documentation for :py:class:`create_attribute_usage` and
    :py:func:`pyglet.graphics.vertexattribute.create_attribute` for the grammar
    of these format strings.

    :rtype: :py:class:`VertexDomain`
    """
    attribute_usages = [create_attribute_usage(f) for f in attribute_usage_formats]
    return IndexedVertexDomain(attribute_usages)


class VertexDomain:
    __doc__ = "Management of a set of vertex lists.\n\n    Construction of a vertex domain is usually done with the\n    :py:func:`create_domain` function.\n    "
    _version = 0
    _initial_count = 16

    def __init__(self, attribute_usages):
        self.allocator = allocation.Allocator(self._initial_count)
        have_multi_texcoord = False
        for attribute, _, _ in attribute_usages:
            if isinstance(attribute, vertexattribute.MultiTexCoordAttribute):
                have_multi_texcoord = True
                break

        static_attributes = []
        attributes = []
        self.buffer_attributes = []
        for attribute, usage, vbo in attribute_usages:
            if have_multi_texcoord:
                if isinstance(attribute, vertexattribute.TexCoordAttribute):
                    attribute.convert_to_multi_tex_coord_attribute()
                if usage == GL_STATIC_DRAW:
                    static_attributes.append(attribute)
                    attributes.append(attribute)
            else:
                attributes.append(attribute)
                attribute.buffer = vertexbuffer.create_mappable_buffer((attribute.stride * self.allocator.capacity),
                  usage=usage,
                  vbo=vbo)
                attribute.buffer.element_size = attribute.stride
                attribute.buffer.attributes = (attribute,)
                self.buffer_attributes.append((attribute.buffer, (attribute,)))

        if static_attributes:
            vertexattribute.interleave_attributes(static_attributes)
            stride = static_attributes[0].stride
            buffer = vertexbuffer.create_mappable_buffer((stride * self.allocator.capacity),
              usage=GL_STATIC_DRAW)
            buffer.element_size = stride
            self.buffer_attributes.append((buffer, static_attributes))
            attributes.extend(static_attributes)
            for attribute in static_attributes:
                attribute.buffer = buffer

        self.attributes = attributes
        self.attribute_names = {}
        for attribute in attributes:
            if isinstance(attribute, vertexattribute.GenericAttribute):
                index = attribute.index
                if "generic" not in self.attribute_names:
                    self.attribute_names["generic"] = {}
                assert index not in self.attribute_names["generic"], "More than one generic attribute with index %d" % index
                self.attribute_names["generic"][index] = attribute
            elif isinstance(attribute, vertexattribute.MultiTexCoordAttribute):
                texture = attribute.texture
                if "multi_tex_coords" not in self.attribute_names:
                    self.attribute_names["multi_tex_coords"] = []
                assert texture not in self.attribute_names["multi_tex_coords"], "More than one multi_tex_coord attribute for texture %d" % texture
                self.attribute_names["multi_tex_coords"].insert(texture, attribute)
            else:
                name = attribute.plural
                assert name not in self.attributes, 'More than one "%s" attribute given' % name
                self.attribute_names[name] = attribute

    def __del__(self):
        for attribute in self.attributes:
            try:
                del attribute.buffer
            except AttributeError:
                pass

    def _safe_alloc(self, count):
        """Allocate vertices, resizing the buffers if necessary."""
        try:
            return self.allocator.alloc(count)
        except allocation.AllocatorMemoryException as e:
            capacity = _nearest_pow2(e.requested_capacity)
            self._version += 1
            for buffer, _ in self.buffer_attributes:
                buffer.resize(capacity * buffer.element_size)

            self.allocator.set_capacity(capacity)
            return self.allocator.alloc(count)

    def _safe_realloc(self, start, count, new_count):
        """Reallocate vertices, resizing the buffers if necessary."""
        try:
            return self.allocator.realloc(start, count, new_count)
        except allocation.AllocatorMemoryException as e:
            capacity = _nearest_pow2(e.requested_capacity)
            self._version += 1
            for buffer, _ in self.buffer_attributes:
                buffer.resize(capacity * buffer.element_size)

            self.allocator.set_capacity(capacity)
            return self.allocator.realloc(start, count, new_count)

    def create(self, count):
        """Create a :py:class:`VertexList` in this domain.

        :Parameters:
            `count` : int
                Number of vertices to create.

        :rtype: :py:class:`VertexList`
        """
        start = self._safe_alloc(count)
        return VertexList(self, start, count)

    def draw(self, mode, vertex_list=None):
        """Draw vertices in the domain.

        If `vertex_list` is not specified, all vertices in the domain are
        drawn.  This is the most efficient way to render primitives.

        If `vertex_list` specifies a :py:class:`VertexList`, only primitives in
        that list will be drawn.

        :Parameters:
            `mode` : int
                OpenGL drawing mode, e.g. ``GL_POINTS``, ``GL_LINES``, etc.
            `vertex_list` : `~pyglet.graphics.vertexdomain.VertexList`
                Vertex list to draw, or ``None`` for all lists in this domain.

        """
        glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
        for buffer, attributes in self.buffer_attributes:
            buffer.bind()
            for attribute in attributes:
                attribute.enable()
                attribute.set_pointer(attribute.buffer.ptr)

        if vertexbuffer._workaround_vbo_finish:
            glFinish()
        if vertex_list is not None:
            glDrawArrays(mode, vertex_list.start, vertex_list.count)
        else:
            starts, sizes = self.allocator.get_allocated_regions()
            primcount = len(starts)
        if primcount == 0:
            pass
        elif primcount == 1:
            glDrawArrays(mode, starts[0], sizes[0])
        elif gl_info.have_version(1, 4):
            starts = (GLint * primcount)(*starts)
            sizes = (GLsizei * primcount)(*sizes)
            glMultiDrawArrays(mode, starts, sizes, primcount)
        else:
            for start, size in zip(starts, sizes):
                glDrawArrays(mode, start, size)

        for buffer, _ in self.buffer_attributes:
            buffer.unbind()

        glPopClientAttrib()

    def _is_empty(self):
        return not self.allocator.starts

    def __repr__(self):
        return "<%s@%x %s>" % (self.__class__.__name__, id(self), self.allocator)


class VertexList:
    __doc__ = "A list of vertices within a :py:class:`VertexDomain`.  Use\n    :py:meth:`VertexDomain.create` to construct this list.\n    "
    _colors_cache = None
    _colors_cache_version = None
    _fog_coords_cache = None
    _fog_coords_cache_version = None
    _edge_flags_cache = None
    _edge_flags_cache_version = None
    _normals_cache = None
    _normals_cache_version = None
    _secondary_colors_cache = None
    _secondary_colors_cache_version = None
    _tex_coords_cache = None
    _tex_coords_cache_version = None
    _vertices_cache = None
    _vertices_cache_version = None

    def __init__(self, domain, start, count):
        self.domain = domain
        self.start = start
        self.count = count

    def get_size(self):
        """Get the number of vertices in the list.

        :rtype: int
        """
        return self.count

    def get_domain(self):
        """Get the domain this vertex list belongs to.

        :rtype: :py:class:`VertexDomain`
        """
        return self.domain

    def draw(self, mode):
        """Draw this vertex list in the given OpenGL mode.

        :Parameters:
            `mode` : int
                OpenGL drawing mode, e.g. ``GL_POINTS``, ``GL_LINES``, etc.

        """
        self.domain.draw(mode, self)

    def resize(self, count):
        """Resize this group.

        :Parameters:
            `count` : int
                New number of vertices in the list.

        """
        new_start = self.domain._safe_realloc(self.start, self.count, count)
        if new_start != self.start:
            for attribute in self.domain.attributes:
                old = attribute.get_region(attribute.buffer, self.start, self.count)
                new = attribute.get_region(attribute.buffer, new_start, self.count)
                new.array[:] = old.array[:]
                new.invalidate()

        self.start = new_start
        self.count = count
        self._colors_cache_version = None
        self._fog_coords_cache_version = None
        self._edge_flags_cache_version = None
        self._normals_cache_version = None
        self._secondary_colors_cache_version = None
        self._tex_coords_cache_version = None
        self._vertices_cache_version = None

    def delete(self):
        """Delete this group."""
        self.domain.allocator.dealloc(self.start, self.count)

    def migrate(self, domain):
        """Move this group from its current domain and add to the specified
        one.  Attributes on domains must match.  (In practice, used to change
        parent state of some vertices).

        :Parameters:
            `domain` : `VertexDomain`
                Domain to migrate this vertex list to.

        """
        assert list(domain.attribute_names.keys()) == list(self.domain.attribute_names.keys()), "Domain attributes must match."
        new_start = domain._safe_alloc(self.count)
        for key, old_attribute in self.domain.attribute_names.items():
            old = old_attribute.get_region(old_attribute.buffer, self.start, self.count)
            new_attribute = domain.attribute_names[key]
            new = new_attribute.get_region(new_attribute.buffer, new_start, self.count)
            new.array[:] = old.array[:]
            new.invalidate()

        self.domain.allocator.dealloc(self.start, self.count)
        self.domain = domain
        self.start = new_start
        self._colors_cache_version = None
        self._fog_coords_cache_version = None
        self._edge_flags_cache_version = None
        self._normals_cache_version = None
        self._secondary_colors_cache_version = None
        self._tex_coords_cache_version = None
        self._vertices_cache_version = None

    def _set_attribute_data(self, i, data):
        attribute = self.domain.attributes[i]
        region = attribute.get_region(attribute.buffer, self.start, self.count)
        region.array[:] = data
        region.invalidate()

    @property
    def colors(self):
        """Array of color data."""
        if self._colors_cache_version != self.domain._version:
            domain = self.domain
            attribute = domain.attribute_names["colors"]
            self._colors_cache = attribute.get_region(attribute.buffer, self.start, self.count)
            self._colors_cache_version = domain._version
        region = self._colors_cache
        region.invalidate()
        return region.array

    @colors.setter
    def colors(self, data):
        self.colors[:] = data

    @property
    def fog_coords(self):
        """Array of fog coordinate data."""
        if self._fog_coords_cache_version != self.domain._version:
            domain = self.domain
            attribute = domain.attribute_names["fog_coords"]
            self._fog_coords_cache = attribute.get_region(attribute.buffer, self.start, self.count)
            self._fog_coords_cache_version = domain._version
        region = self._fog_coords_cache
        region.invalidate()
        return region.array

    @fog_coords.setter
    def fog_coords(self, data):
        self.fog_coords[:] = data

    @property
    def edge_flags(self):
        """Array of edge flag data."""
        if self._edge_flags_cache_version != self.domain._version:
            domain = self.domain
            attribute = domain.attribute_names["edge_flags"]
            self._edge_flags_cache = attribute.get_region(attribute.buffer, self.start, self.count)
            self._edge_flags_cache_version = domain._version
        region = self._edge_flags_cache
        region.invalidate()
        return region.array

    @edge_flags.setter
    def edge_flags(self, data):
        self.edge_flags[:] = data

    @property
    def normals(self):
        """Array of normal vector data."""
        if self._normals_cache_version != self.domain._version:
            domain = self.domain
            attribute = domain.attribute_names["normals"]
            self._normals_cache = attribute.get_region(attribute.buffer, self.start, self.count)
            self._normals_cache_version = domain._version
        region = self._normals_cache
        region.invalidate()
        return region.array

    @normals.setter
    def normals(self, data):
        self.normals[:] = data

    @property
    def secondary_colors(self):
        """Array of secondary color data."""
        if self._secondary_colors_cache_version != self.domain._version:
            domain = self.domain
            attribute = domain.attribute_names["secondary_colors"]
            self._secondary_colors_cache = attribute.get_region(attribute.buffer, self.start, self.count)
            self._secondary_colors_cache_version = domain._version
        region = self._secondary_colors_cache
        region.invalidate()
        return region.array

    @secondary_colors.setter
    def secondary_colors(self, data):
        self.secondary_colors[:] = data

    @property
    def tex_coords(self):
        """Array of texture coordinate data."""
        if "multi_tex_coords" not in self.domain.attribute_names:
            if self._tex_coords_cache_version != self.domain._version:
                domain = self.domain
                attribute = domain.attribute_names["tex_coords"]
                self._tex_coords_cache = attribute.get_region(attribute.buffer, self.start, self.count)
                self._tex_coords_cache_version = domain._version
            region = self._tex_coords_cache
            region.invalidate()
            return region.array
        else:
            return

    @tex_coords.setter
    def tex_coords(self, data):
        if self.tex_coords:
            self.tex_coords[:] = data

    @property
    def multi_tex_coords(self):
        """Multi-array texture coordinate data."""
        if "tex_coords" not in self.domain.attribute_names:
            if self._tex_coords_cache_version != self.domain._version:
                domain = self.domain
                attribute = domain.attribute_names["multi_tex_coords"]
                self._tex_coords_cache = []
                for a in attribute:
                    self._tex_coords_cache.append(a.get_region(a.buffer, self.start, self.count))

                self._tex_coords_cache_version = domain._version
            region = self._tex_coords_cache
            array = []
            for a in region:
                a.invalidate()
                array.append(a.array)

            return array
        else:
            return

    @multi_tex_coords.setter
    def multi_tex_coords(self, data):
        if self.multi_tex_coords:
            for a in range(0, len(self._tex_coords_cache), 1):
                if a > len(data):
                    break
                else:
                    if data[a]:
                        self._tex_coords_cache[a].array[:] = data[a]

    @property
    def vertices(self):
        """Array of vertex coordinate data."""
        if self._vertices_cache_version != self.domain._version:
            domain = self.domain
            attribute = domain.attribute_names["vertices"]
            self._vertices_cache = attribute.get_region(attribute.buffer, self.start, self.count)
            self._vertices_cache_version = domain._version
        region = self._vertices_cache
        region.invalidate()
        return region.array

    @vertices.setter
    def vertices(self, data):
        self.vertices[:] = data


class IndexedVertexDomain(VertexDomain):
    __doc__ = "Management of a set of indexed vertex lists.\n\n    Construction of an indexed vertex domain is usually done with the\n    `create_indexed_domain` function.\n    "
    _initial_index_count = 16

    def __init__(self, attribute_usages, index_gl_type=GL_UNSIGNED_INT):
        super(IndexedVertexDomain, self).__init__(attribute_usages)
        self.index_allocator = allocation.Allocator(self._initial_index_count)
        self.index_gl_type = index_gl_type
        self.index_c_type = vertexattribute._c_types[index_gl_type]
        self.index_element_size = ctypes.sizeof(self.index_c_type)
        self.index_buffer = vertexbuffer.create_mappable_buffer((self.index_allocator.capacity * self.index_element_size),
          target=GL_ELEMENT_ARRAY_BUFFER)

    def _safe_index_alloc(self, count):
        """Allocate indices, resizing the buffers if necessary."""
        try:
            return self.index_allocator.alloc(count)
        except allocation.AllocatorMemoryException as e:
            capacity = _nearest_pow2(e.requested_capacity)
            self._version += 1
            self.index_buffer.resize(capacity * self.index_element_size)
            self.index_allocator.set_capacity(capacity)
            return self.index_allocator.alloc(count)

    def _safe_index_realloc(self, start, count, new_count):
        """Reallocate indices, resizing the buffers if necessary."""
        try:
            return self.index_allocator.realloc(start, count, new_count)
        except allocation.AllocatorMemoryException as e:
            capacity = _nearest_pow2(e.requested_capacity)
            self._version += 1
            self.index_buffer.resize(capacity * self.index_element_size)
            self.index_allocator.set_capacity(capacity)
            return self.index_allocator.realloc(start, count, new_count)

    def create(self, count, index_count):
        """Create an :py:class:`IndexedVertexList` in this domain.

        :Parameters:
            `count` : int
                Number of vertices to create
            `index_count`
                Number of indices to create

        """
        start = self._safe_alloc(count)
        index_start = self._safe_index_alloc(index_count)
        return IndexedVertexList(self, start, count, index_start, index_count)

    def get_index_region(self, start, count):
        """Get a region of the index buffer.

        :Parameters:
            `start` : int
                Start of the region to map.
            `count` : int
                Number of indices to map.

        :rtype: Array of int
        """
        byte_start = self.index_element_size * start
        byte_count = self.index_element_size * count
        ptr_type = ctypes.POINTER(self.index_c_type * count)
        return self.index_buffer.get_region(byte_start, byte_count, ptr_type)

    def draw(self, mode, vertex_list=None):
        """Draw vertices in the domain.

        If `vertex_list` is not specified, all vertices in the domain are
        drawn.  This is the most efficient way to render primitives.

        If `vertex_list` specifies a :py:class:`VertexList`, only primitives in
        that list will be drawn.

        :Parameters:
            `mode` : int
                OpenGL drawing mode, e.g. ``GL_POINTS``, ``GL_LINES``, etc.
            `vertex_list` : `IndexedVertexList`
                Vertex list to draw, or ``None`` for all lists in this domain.

        """
        glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
        for buffer, attributes in self.buffer_attributes:
            buffer.bind()
            for attribute in attributes:
                attribute.enable()
                attribute.set_pointer(attribute.buffer.ptr)

        self.index_buffer.bind()
        if vertexbuffer._workaround_vbo_finish:
            glFinish()
        if vertex_list is not None:
            glDrawElements(mode, vertex_list.index_count, self.index_gl_type, self.index_buffer.ptr + vertex_list.index_start * self.index_element_size)
        else:
            starts, sizes = self.index_allocator.get_allocated_regions()
            primcount = len(starts)
        if primcount == 0:
            pass
        elif primcount == 1:
            glDrawElements(mode, sizes[0], self.index_gl_type, self.index_buffer.ptr + starts[0] * self.index_element_size)
        elif gl_info.have_version(1, 4):
            starts = [s * self.index_element_size + self.index_buffer.ptr for s in starts]
            starts = (ctypes.POINTER(GLvoid) * primcount)(*(GLintptr * primcount)(*starts))
            sizes = (GLsizei * primcount)(*sizes)
            glMultiDrawElements(mode, sizes, self.index_gl_type, starts, primcount)
        else:
            for start, size in zip(starts, sizes):
                glDrawElements(mode, size, self.index_gl_type, self.index_buffer.ptr + start * self.index_element_size)

        self.index_buffer.unbind()
        for buffer, _ in self.buffer_attributes:
            buffer.unbind()

        glPopClientAttrib()


class IndexedVertexList(VertexList):
    __doc__ = "A list of vertices within an :py:class:`IndexedVertexDomain` that are\n    indexed. Use :py:meth:`IndexedVertexDomain.create` to construct this list.\n    "
    _indices_cache = None
    _indices_cache_version = None

    def __init__(self, domain, start, count, index_start, index_count):
        super(IndexedVertexList, self).__init__(domain, start, count)
        self.index_start = index_start
        self.index_count = index_count

    def draw(self, mode):
        self.domain.draw(mode, self)

    def resize(self, count, index_count):
        """Resize this group.

        :Parameters:
            `count` : int
                New number of vertices in the list.
            `index_count` : int
                New number of indices in the list.

        """
        old_start = self.start
        super(IndexedVertexList, self).resize(count)
        if old_start != self.start:
            diff = self.start - old_start
            self.indices[:] = [i + diff for i in self.indices]
        new_start = self.domain._safe_index_realloc(self.index_start, self.index_count, index_count)
        if new_start != self.index_start:
            old = self.domain.get_index_region(self.index_start, self.index_count)
            new = self.domain.get_index_region(self.index_start, self.index_count)
            new.array[:] = old.array[:]
            new.invalidate()
        self.index_start = new_start
        self.index_count = index_count
        self._indices_cache_version = None

    def delete(self):
        """Delete this group."""
        super(IndexedVertexList, self).delete()
        self.domain.index_allocator.dealloc(self.index_start, self.index_count)

    def migrate(self, domain):
        """Move this group from its current indexed domain and add to the 
        specified one.  Attributes on domains must match.  (In practice, used 
        to change parent state of some vertices).

        :Parameters:
            `domain` : `IndexedVertexDomain`
                Indexed domain to migrate this vertex list to.

        """
        old_start = self.start
        old_domain = self.domain
        super(IndexedVertexList, self).migrate(domain)
        if old_start != self.start:
            diff = self.start - old_start
            region = old_domain.get_index_region(self.index_start, self.index_count)
            old_indices = region.array
            old_indices[:] = [i + diff for i in old_indices]
            region.invalidate()
        old = old_domain.get_index_region(self.index_start, self.index_count)
        old_domain.index_allocator.dealloc(self.index_start, self.index_count)
        new_start = self.domain._safe_index_alloc(self.index_count)
        new = self.domain.get_index_region(new_start, self.index_count)
        new.array[:] = old.array[:]
        new.invalidate()
        self.index_start = new_start
        self._indices_cache_version = None

    def _set_index_data(self, data):
        region = self.domain.get_index_region(self.index_start, self.index_count)
        region.array[:] = data
        region.invalidate()

    @property
    def indices(self):
        """Array of index data."""
        if self._indices_cache_version != self.domain._version:
            domain = self.domain
            self._indices_cache = domain.get_index_region(self.index_start, self.index_count)
            self._indices_cache_version = domain._version
        region = self._indices_cache
        region.invalidate()
        return region.array

    @indices.setter
    def indices(self, data):
        self.indices[:] = data
