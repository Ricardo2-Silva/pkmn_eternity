# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\data\container\world.py
import rabbyt, ujson
from client.data.file import fileManager, archive
from shared.container.geometry import Rect
CHUNK_SIZE = 64

class Chunk:
    __slots__ = [
     "loaded", "items"]

    def __init__(self):
        self.loaded = False
        self.items = []


class SpatialHash:

    def __init__(self, left, top, right, bottom, size):
        self.grid = {}
        self.size = size
        for x in range(int(left / size), int(right / size) + 1):
            self.grid[x] = {}
            for y in range(int(bottom / size), int(top / size) + 1):
                self.grid[x][y] = []

    def add(self, rect):
        for x in range(int(rect.left / self.size), int(rect.right / self.size)):
            for y in range(int(rect.bottom / self.size), int(rect.top / self.size)):
                self.grid[x][y].append(rect)


class World:

    def __init__(self):
        self.game_maps = {}
        self.grid = {}
        self.world_bounds = [
         -1, 1, 1, 0]
        self.build_grid()
        self.load_world()

    def load_world(self):
        from client.data.DB import mapDB
        map_one = mapDB.getByName("A_TOWN1")
        map_one.coordinates = (0, 0)
        filename = fileManager.getMap(map_one.information.fileName)
        map_one.data = ujson.loads(archive.readFile(filename))
        map_one.size = map_one.data["map_size"]
        map_two = mapDB.getByName("ROUTE1")
        filename = fileManager.getMap(map_two.information.fileName)
        map_two.data = ujson.loads(archive.readFile(filename))
        map_two.size = map_two.data["map_size"]
        map_two.coordinates = (0, 1)
        self.add_map(map_one)
        self.add_map(map_two)
        self.spatial = SpatialHash(*self.calculate_offsets(), *(CHUNK_SIZE,))
        for game_map in self.game_maps.values():
            self.spatial.add(game_map)

    def build_grid(self):
        for x in range(self.world_bounds[0], self.world_bounds[2] + 1):
            self.grid[x] = {}
            for y in range(self.world_bounds[1], self.world_bounds[3] + 1):
                self.grid[x][y] = None

    def get_adjacent_maps(self, name):
        world_map = self.maps[name]
        game_maps = []
        for x in range(-2, 2):
            for y in range(-2, 2):
                try:
                    world_map_section = self.grid[world_map.coordinates[0] + x][world_map.coordinates[1] + y]
                    if world_map_section:
                        game_maps.append(world_map_section)
                except KeyError:
                    continue

        return game_maps

    def world_position_to_map(self, x, y):
        return

    def get_chunks(self, gameMap, x, y):
        """ Get's the nearest map chunks based on gameMap and x, y position."""
        x, y = self.map_to_world_position(gameMap, x, y)
        world_chunk_x = x // CHUNK_SIZE
        world_chunk_y = y // CHUNK_SIZE
        for i in range(world_chunk_x - 10, world_chunk_x + 11):
            for j in range(world_chunk_y - 6, world_chunk_x + 7):
                self._get_chunk(i, j)

    def _get_chunk(self, x, y):
        chunk = self.grid[x][y]
        if not chunk.loaded:
            for game_maps in chunk.items:
                map_chunk = game_maps.get_world_chunk(x, y)
                self._load_map_chunk(map_chunk)

            chunk.loaded = True
        else:
            for game_maps in chunk.items:
                if game_maps.visible is False:
                    game_maps.visible = True

    def load_world_chunk(self, chunk_x, chunk_y):
        if self._loaded(chunk_x, chunk_y):
            return
        game_maps = rabbyt.collisions.aabb_collide_single(Rect(chunk_x * CHUNK_SIZE, chunk_y * CHUNK_SIZE, CHUNK_SIZE, CHUNK_SIZE), self.game_maps.values())
        self.load_chunk(chunk_x, chunk_y)

    def get_map_in_direction(self, game_map, x, y):
        """ Gets a map at a specific coordinate next to a map
            x = 1 : Map to the right, x = -1 : Map to the left,
            y = 1 : Map to the north, y = -1 : Map to the south
        """
        try:
            return self.grid[game_map.coordinates[0] + x][game_map.coordinates[1] + y]
        except KeyError:
            return

    def get_start_world_coordinate(self, game_map):
        return

    def add_map(self, world_map):
        self.game_maps[world_map.name] = world_map
        self.grid[world_map.coordinates[0]][world_map.coordinates[1]] = world_map

    def calculate_offsets(self):
        """ Uses map sizes of each grid to determine where the bottom left point should be,
         returns max dimensions of all of the maps for the spatial hash.
         """
        l, t, r, b = (0, 0, 0, 0)
        for game_map in self.game_maps.values():
            x_step = -1 if game_map.coordinates[0] < 0 else 1
            for x in range(0, game_map.coordinates[0], x_step):
                width = self.grid[x][0].size[0] * x_step
                game_map.world_position[0] += height

            l = min(l, game_map.world_position[0])
            r = max(r, game_map.world_position[0] + game_map.width)
            y_step = -1 if game_map.coordinates[1] < 0 else 1
            for y in range(0, game_map.coordinates[1], y_step):
                height = self.grid[0][y].size[1] * y_step
                game_map.world_position[1] += height

            b = min(b, game_map.world_position[1])
            t = max(t, game_map.world_position[1] + game_map.height)
            game_map.set_rect()

        print(l, t, r, b)
        return (
         l, t, r, b)


world = World()
