import math, copy
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

    def __init__(self, *coords):
        latitude, longitude = coords if len(coords) > 1 else coords[0].split(',')
        self.latitude = float(latitude)
        self.longitude = float(longitude)

    def distance(self, other) -> int:
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
    def __init__(self, point, id):
        self.id = id
        self.point = point

    def __eq__(self, other):
        return self.id == other.id

    @staticmethod
    def json_to_nodes(json_nodes):
        formatted_nodes = {}
        nodes = json_nodes['elements']
        for node in nodes:
            node_point = Point(node['lat'],node['lon'])
            formatted_nodes[node['id']] = Node(node_point,node['id'])
        return formatted_nodes

    def closest_node(self, nodes):
        """Returns the closest node from a list of nodes"""
        nodes = sorted(nodes.values(), key=lambda n: n.pos - self.point)
        closest_node = nodes[0]
        return closest_node

class Way:
    def __init__(self, nodes, id, tags):
        self.nodes = nodes
        self.id = id
        self.tags = tags

    @staticmethod
    def json_to_ways(json_ways):
        formatted_ways = {}
        ways = json_ways['elements']
        for way in ways:
            formatted_ways[way['id']] = Way(way['nodes'], way['id'], way['tags'])
        return formatted_ways

class Route:
    def __init__(self, route: list, distance: int):
        self.route = route
        self.distance = distance

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

    @staticmethod
    def generate_route(nodes: dict, ways: dict, start: str, end: str, preferences: dict=None) -> None:
        unvisited = set(node_id for node_id in nodes)
        visited = set()
        path_dict = dict((node,(inf,[node])) for node in nodes)
        neighbours = Route.find_neighbours(ways)
        path_dict[start] = (0,[start])

        current = start
        while True:
            current_distance,current_path = path_dict[current]
            current_neighbours = neighbours[current]
            for neighbour in current_neighbours:
                if neighbour in unvisited:
                    neighbour_distance,neighbour_path = path_dict[neighbour]
                    neighbour_point = nodes[neighbour].point
                    relative_distance = nodes[current].point.distance(neighbour_point)
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
        return Route(fastest_route,route_distance)

if __name__ == '__main__':
    ways = Way.json_to_ways(json.loads(open('ways.json').read()))
    nodes = Node.json_to_nodes(json.loads(open('nodes.json').read()))
    start = 1741123995
    end   = 1741124011
    route = Route.generate_route(nodes,ways,start,end)
    print(route.route,route.distance)
