from __future__ import annotations

import math
import copy
import json
from math import inf


EARTH_RADIUS = 6371.009

class Point:
    """
    Represents a geodetic point with latitude and longitude

    Attributes
    ----------
    latitude : float
        A floating point value in degrees representing latitude
    longitude : float
        A floating point value in degrees representing longitude
    """

    def __init__(self, *coords: float or str):
        latitude, longitude = coords if len(coords) > 1 else coords[0].split(',')
        self.latitude = float(latitude)
        self.longitude = float(longitude)

    def distance(self, other: Point) -> int:
        """
        Uses spherical geometry to calculate the surface distance between two points.

        Parameters
        ----------
        other : Point
            Another point object to calculate the distance against

        Returns
        -------
        int
            The calculated distance in kilometers
        """

        lat1, lon1 = self
        lat2, lon2 = other

        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)

        a = (
            math.sin(dlat / 2)
            * math.sin(dlat / 2)
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(dlon / 2)
            * math.sin(dlon / 2)
            )

        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return EARTH_RADIUS * c

    def __iter__(self):
        return iter((self.latitude, self.longitude))

    def __sub__(self, other) -> int:
        """
        Another way to call the distance function
        >>> point1 - point2
        69
        """
        return self.distance(other)


class Node:
    def __init__(self, id: int, position: Point, tags: list=[]):
        self.id = id
        self.pos = position
        self.tags = tags

    def __eq__(self, other):
        return self.id == other.id

    @classmethod
    def from_json(cls, nodedata: dict) -> Node:
        position = Point(nodedata['lat'], nodedata['lon'])
        return cls(nodedata['id'], position)

    def closest_node(self, nodes: dict) -> Node:
        """Returns the closest node from a list of nodes"""
        nodes = sorted(nodes.values(), key=lambda n: n.pos - self.pos)
        closest_node = nodes[0]
        return closest_node

class Way:
    def __init__(self, nodes, id, tags):
        self.nodes = nodes
        self.id = id
        self.tags = tags

    @classmethod
    def from_json(cls, way: dict):
        return cls(way['nodes'], way['id'], way['tags'])

class Route:
    def __init__(self, route: list, distance: int):
        self.route = route
        self.distance = distance
    
    @property
    def json(self):
        return { 
            "success": True,
            "data": self.route
        }

    @staticmethod
    def find_neighbours(ways) -> dict:
        neighbours = {}
        for way in ways.values():
            way_nodes = way.nodes
            for index, node in enumerate(way_nodes):
                node_neighbours = set()
                if (index - 1) > 0: node_neighbours.add(way_nodes[index - 1])
                if (index + 1) < len(way_nodes): node_neighbours.add(way_nodes[index + 1])
                if node not in neighbours:
                    neighbours[node] = set()
                neighbours[node] |= node_neighbours
        return neighbours

    @classmethod
    def generate_route(cls, nodes: dict, ways: dict, start: int, end: int, preferences: dict=None) -> Route:
        unvisited = set(node_id for node_id in nodes)
        visited = set()
        path_dict = dict((node,(inf,[node])) for node in nodes)
        neighbours = cls.find_neighbours(ways)
        path_dict[start] = (0,[start])

        current = start
        while True:
            current_distance,current_path = path_dict[current]
            current_neighbours = neighbours[current]
            for neighbour in current_neighbours:
                if neighbour in unvisited:
                    neighbour_distance,neighbour_path = path_dict[neighbour]
                    neighbour_point = nodes[neighbour].pos
                    relative_distance = nodes[current].pos.distance(neighbour_point)
                    new_distance = relative_distance + current_distance
                    if new_distance < neighbour_distance:
                        path_dict[neighbour] = (new_distance,current_path + [neighbour])
            unvisited.remove(current)
            visited.add(current)
            if end in visited:
                break
            else:
                min_distance,next_node = inf, None
                for node_id in unvisited:
                    current_distance,path = path_dict[node_id]
                    if current_distance < min_distance: min_distance,next_node = current_distance,node_id
                if min_distance == inf:
                    raise Exception("Can't get to end node")
                else:
                    current = next_node

        route_distance, fastest_route = path_dict[end]
        return cls(fastest_route,route_distance)

if __name__ == '__main__':
    with open('ways.json') as f:
        waydata = json.load(f).get('elements')
    
    with open('nodes.json') as f:
        nodedata = json.load(f).get('elements')

    ways = {w['id']: Way.from_json(w) for w in waydata}
    nodes = {n['id']: Node.from_json(n) for n in nodedata}

    start = 1741123995
    end   = 1741124011

    route = Route.generate_route(nodes, ways, start, end)

    print(route.route, route.distance)
