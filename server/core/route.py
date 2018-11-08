import math, copy
import json
from math import inf

EARTH_RADIUS = 6371000 #In metres

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
    def __init__(self, point: Point, id: str):
        self.id = id
        self.point = point
        self.ways = set() #Set of ways that it is a part of

    def __eq__(self, other: Point):
        return self.id == other.id

    @staticmethod
    def json_to_nodes(json_nodes: dict) -> dict:
        formatted_nodes = {}
        nodes = json_nodes['elements']
        for node in nodes:
            node_point = Point(node['lat'],node['lon'])
            formatted_nodes[node['id']] = Node(node_point,node['id'])
        return formatted_nodes

    def closest_node(self, nodes: dict) -> Point:
        """Returns the closest node a dictionary of nodes"""
        nodes = sorted(nodes.values(), key=lambda n: n.pos - self.point)
        closest_node = nodes[0]
        return closest_node

class Way:
    def __init__(self, nodes: list, id: str, tags):
        self.nodes = nodes
        self.id = id
        self.tags = tags

    @staticmethod
    def json_to_ways(json_ways: dict) -> dict:
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
    def find_neighbours(ways: dict) -> dict:
        """
        Generates neighbours for every node in provided ways
        """
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
    def generate_shortest_route(nodes: dict, ways: dict, start: str, end: str, preferences: dict=None) -> None:
        """
        Generates the shortest route to a destination
        Uses A* with euclidean distance as heuristic
        Uses tags to change cost of moving to nodes
        """
        unvisited = set(node_id for node_id in nodes)
        visited = set()
        path_dict = dict((node,(inf,[node])) for node in nodes)
        neighbours = Route.find_neighbours(ways)
        path_dict[start] = (0,[start])

        if end not in nodes: raise Exception('End node not in node space. Specify a valid node.')
        elif start not in nodes: raise Exception('End node not in node space. Specify a valid node.')
        else: current = start

        while True:
            current_cost,current_path = path_dict[current]
            current_neighbours = neighbours[current]
            for neighbour in current_neighbours:
                if neighbour in unvisited:
                    neighbour_cost,neighbour_path = path_dict[neighbour]
                    relative_distance = nodes[current].point - nodes[neighbour].point
                    # Added tag cost based on preferences of tags and distance as a scaling factor
                    #neighbour_tags = nodes[neighbour].tags
                    tag_cost = 0 #relative_distance * sum(preferences[tag] for tag in neighbour_tags)

                    new_cost = relative_distance + current_cost + tag_cost
                    if new_cost < neighbour_cost:
                        path_dict[neighbour] = (new_cost,current_path + [neighbour])
            unvisited.remove(current)
            visited.add(current)
            if end in visited:
                break
            else:
                min_value,next_node = inf, None
                for node_id in unvisited:
                    current_distance,path = path_dict[node_id]
                    #Heuristic value uses distance to endpoint to judge closenss
                    heuristic_value = nodes[node_id].point - nodes[end].point

                    current_value = current_distance + heuristic_value
                    if current_value < min_value: min_value,next_node = current_value,node_id
                if min_value == inf:
                    raise Exception("End node cannot be reached")
                else:
                    current = next_node

        route_distance, fastest_route = path_dict[end]
        return Route(fastest_route,route_distance)

if __name__ == '__main__':
    ways  = Way.json_to_ways(json.loads(open('ways.json').read()))
    nodes = Node.json_to_nodes(json.loads(open('nodes.json').read()))
    start = 1741123995
    end   = 1741123987
    route = Route.generate_shortest_route(nodes,ways,start,end)
    print(route.route,route.distance)
