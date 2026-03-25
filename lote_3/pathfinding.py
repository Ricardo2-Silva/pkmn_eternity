# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\world\action\pathfinding.py
"""
Created on Nov 17, 2019

@author: Admin
"""
import math, time
from queue import PriorityQueue
from twisted.internet.threads import deferToThread
from shared.service.geometry import getDistanceBetweenTwoPoints
from shared.container.constants import GroundType
from shared.service.direction import directionService
from client.data.container.map import mapContainer
STEP_SIZE = 18
directionText = ('RIGHT', 'UP_RIGHT', 'UP', 'UP_LEFT', 'LEFT', 'DOWN_LEFT', 'DOWN',
                 'DOWN_RIGHT')
NPC_WALKABLE = GroundType.NOTHING | GroundType.HIGH_GRASS | GroundType.LOW_GRASS | GroundType.SHALLOW_WATER | GroundType.DEEP_WATER

class PathFinding:

    def __init__(self):
        self.currentPosition = (0, 0)
        self.endPosition = (0, 0)
        self.properPath = []
        self.ignoreList = []
        self.map = None

    @staticmethod
    def hCost(p1, p2):
        """Heuristic"""
        x0, y0 = p1
        x1, y1 = p2
        return math.hypot(x1 - x0, y1 - y0)

    def calculateMovementCost(self, startPosition, nextPosition):
        x, y = startPosition
        x1, y1 = nextPosition
        return abs(x - x1) + abs(y - y1)

    def decideNextValidPosition(self):
        score = {}
        toBeChecked = []
        for direction in directionService.NO_DIAGONAL:
            nextPosition = self.getPositionInDirection(self.currentPosition, direction)
            cost = self.calculateMovementCost(nextPosition, self.endPosition)
            if nextPosition not in self.ignoreList:
                if mapContainer.isPathWalkable((self.map), (self.currentPosition),
                  nextPosition,
                  allowedWallHeight=0,
                  allowedGroundTypes=NPC_WALKABLE,
                  radius=STEP_SIZE):
                    toBeChecked.append(nextPosition)
                    score[nextPosition] = cost
                else:
                    self.ignoreList.append(nextPosition)

        if not score:
            return False
        else:
            self.currentPosition = min(score, key=(score.get))
            self.properPath.append(self.currentPosition)
            self.ignoreList.extend(toBeChecked)
            return True

    @staticmethod
    def hCost(p1, p2):
        """Heuristic"""
        x0, y0 = p1
        x1, y1 = p2
        return math.hypot(x1 - x0, y1 - y0)

    def newPathFind(self, playerMap, start, end, smooth=False):
        """This will use path finding based on distance """
        if not (mapContainer.isPositionWalkable)(None,
 playerMap, *end, **{"radius": STEP_SIZE}):
            return []
        count = 0
        open_set = PriorityQueue()
        open_set.put((0, count, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: (self.hCost(start, end))}
        open_set_hash = {
         start}
        closed_neighbors = []
        t1 = time.perf_counter()
        while not open_set.empty():
            current = open_set.get()[2]
            open_set_hash.remove(current)
            distance = getDistanceBetweenTwoPoints(current, end)
            print("GOING", current, end)
            if distance <= STEP_SIZE:
                if mapContainer.isPathWalkable(playerMap, current,
                  end,
                  allowedWallHeight=0,
                  allowedGroundTypes=NPC_WALKABLE,
                  radius=STEP_SIZE):
                    came_from[end] = current
                    current = end
                else:
                    return []
            if current == end:
                nodes = [
                 end]
                while current in came_from:
                    current = came_from[current]
                    print("VALUE", current)
                    nodes.append(current)

                print("TIME TO PATH FIND", time.perf_counter() - t1, nodes)
                if smooth:
                    smoothed = self.smoothNodes(nodes, playerMap)
                    smoothed.reverse()
                    return smoothed
                else:
                    nodes.reverse()
                    return nodes
            temp_g_score = g_score[current] + 1
            for direction in directionService.ALL_DIRECTIONS:
                neighbor = self.getPositionInDirection(current, direction)
                if neighbor in closed_neighbors:
                    continue
                if not (mapContainer.isPositionInBounds)(playerMap, *neighbor):
                    closed_neighbors.append(neighbor)
                elif mapContainer.isPathWalkable(playerMap, current,
                  neighbor,
                  allowedWallHeight=0,
                  allowedGroundTypes=NPC_WALKABLE,
                  radius=STEP_SIZE):
                    if neighbor not in g_score:
                        g_score[neighbor] = float("inf")
                    else:
                        if temp_g_score < g_score[neighbor]:
                            came_from[neighbor] = current
                            g_score[neighbor] = temp_g_score
                            f_score[neighbor] = temp_g_score + self.hCost(neighbor, end)
                            if neighbor not in open_set_hash:
                                count += 1
                                open_set.put((f_score[neighbor], count, neighbor))
                                open_set_hash.add(neighbor)
                            else:
                                closed_neighbors.append(neighbor)

    def beginPathFind(self, playerMap, startPos, endPos):
        self.map = playerMap
        self.endPosition = endPos
        self.currentPosition = startPos
        self.ignoreList.append(startPos)
        goal = False
        while not goal:
            if not self.decideNextValidPosition():
                goal = True
            distance = getDistanceBetweenTwoPoints(self.currentPosition, self.endPosition)
            if distance < STEP_SIZE:
                goal = True

        if self.properPath:
            return self.properPath
        else:
            return []

    def _threadPathFind(self, playerMap, start, end, smooth=True):
        """This will use path finding based on distance """
        count = 0
        open_set = PriorityQueue()
        open_set.put((0, count, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: (self.hCost(start, end))}
        open_set_hash = {
         start}
        closed_neighbors = []
        t1 = time.perf_counter()
        while not open_set.empty():
            current = open_set.get()[2]
            open_set_hash.remove(current)
            distance = getDistanceBetweenTwoPoints(current, end)
            if current == end:
                nodes = []
                while current in came_from:
                    current = came_from[current]
                    nodes.append(current)

                print("TIME TO PATH FIND", time.perf_counter() - t1)
                if smooth:
                    return self.smoothNodes(nodes, playerMap)
                else:
                    return nodes
            temp_g_score = g_score[current] + 1
            for direction in directionService.NO_DIAGONAL:
                neighbor = self.getPositionInDirection(current, direction)
                if neighbor in closed_neighbors:
                    continue
                if not (playerMap.isPositionInBounds)(*neighbor):
                    closed_neighbors.append(neighbor)
                else:
                    if mapContainer.isPathWalkable((self.map), (self.currentPosition),
                      neighbor,
                      allowedWallHeight=0,
                      allowedGroundTypes=NPC_WALKABLE,
                      radius=STEP_SIZE):
                        if neighbor not in g_score:
                            g_score[neighbor] = float("inf")
                        if temp_g_score < g_score[neighbor]:
                            came_from[neighbor] = current
                            g_score[neighbor] = temp_g_score
                            f_score[neighbor] = temp_g_score + self.hCost(neighbor, end)
                            if neighbor not in open_set_hash:
                                count += 1
                                open_set.put((f_score[neighbor], count, neighbor))
                                open_set_hash.add(neighbor)
                            else:
                                closed_neighbors.append(neighbor)

        return []

    def beginPathFindDefer(self, playerMap, startPos, endPos):
        d = deferToThread(self.newPathFind, playerMap, startPos, endPos)
        d.addErrback(self._printErrors)
        return d

    def _printErrors(self, error):
        print("ERROR", error)

    def smoothNodes2(self, nodes):
        """ Checks walking between check point, node and next node.
             If the next position is walkable, eliminate the node as it's redundant
            'smooths' out the walking a little bit
        """
        smooth = list(nodes)
        checkPoint = nodes[0]
        for index, currentNode in enumerate(nodes):
            if checkPoint == currentNode:
                pass
            elif index + 1 == len(nodes):
                pass
            else:
                nextNode = nodes[index + 1]
                if mapContainer.isPathWalkable((self.map), checkPoint, nextNode, allowedWallHeight=0, allowedGroundTypes=NPC_WALKABLE,
                  radius=STEP_SIZE):
                    smooth.remove(currentNode)
                else:
                    checkPoint = currentNode

        print(smooth)
        return smooth

    def smoothNodes(self, nodes, playerMap):
        """ Checks walking between check point, node and next node.
             If the next position is walkable, eliminate the node as it's redundant
            'smooths' out the walking a little bit
        """
        smooth = list(nodes)
        checkPoint = nodes[0]
        for index, currentNode in enumerate(nodes):
            if checkPoint == currentNode:
                pass
            elif index + 1 == len(nodes):
                pass
            else:
                nextNode = nodes[index + 1]
                if mapService.isPathWalkablePrecise(playerMap, checkPoint,
                  nextNode,
                  allowedWallHeight=0,
                  allowedGroundTypes=NPC_WALKABLE,
                  radius=STEP_SIZE):
                    smooth.remove(currentNode)
                else:
                    checkPoint = currentNode

        return smooth

    def getPositionInDirection(self, startPosition, direction):
        x, y = startPosition
        nx = x + math.cos(math.radians(direction)) * STEP_SIZE
        ny = y + math.sin(math.radians(direction)) * STEP_SIZE
        return (
         int(nx), int(ny))
