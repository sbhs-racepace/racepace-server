from __future__ import annotations
import math
import copy
import json
from math import inf

EARTH_RADIUS = 6371000

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

    def __init__(self, latitude: float, longitude: float):
        self.latitude = round(float(latitude),9)
        self.longitude = round(float(longitude),9)

    @classmethod
    def from_string(cls, string):
        lat, long = string.split(',')
        return cls(lat, long)

    def distance(self, other: Point) -> float:
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

    def euclidean_distance(self,other:Point):
        '''
        Euclidean distance between two points (NON SPHERICAL)
        '''
        lat1,long1 = self
        lat2,long2 = other
        return math.sqrt((long1-long2)**2 + (lat1-lat2)**2)

    def heuristic_distance(self, other: Point, hor_unit: float, vert_unit: float) -> float:
        """
        Heuristic value based on euclidean distance on geo units
        """
        delta_lat = abs(self.latitude - other.latitude)
        delta_lon = abs(self.longitude - other.longitude)
        x_dist = hor_unit * delta_lon
        y_dist = vert_unit * delta_lat
        return x_dist**2 + y_dist**2

    def __iter__(self):
        return iter((self.latitude, self.longitude))

    def __sub__(self, other: Point) -> int:
        """
        Another way to call the distance function
        >>> point1 - point2
        69
        """
        return self.distance(other)

    def __repr__(self):
        return f'{self.latitude},{self.longitude}'

    def closest_node(self, nodes: dict) -> Node:
        """Returns the closest node from a dict of nodes"""
        nodes = sorted(nodes.values(), key=lambda other: other - self)
        closest_node = nodes[0]
        return closest_node

    def get_midpoint(self, other) -> Point:
        delta_lat = (other.latitude - self.latitude) / 2
        delta_lon = (other.longitude - self.longitude) / 2
        return Point(self.latitude + delta_lat,self.longitude + delta_lon)

class Node(Point):
    def __init__(self, latitude: float, longitude: float, id: str):
        Point.__init__(self,latitude,longitude)
        self.id = id
        self.ways = set()

    def __eq__(self, other: Point):
        return self.id == other.id

    @staticmethod
    def json_to_nodes(json_nodes: dict) -> dict:
        """Returns node of json format to dict format"""
        nodes = json_nodes['elements']
        formatted_nodes = {node['id']: Node.from_json(node) for node in nodes}
        return formatted_nodes

    @classmethod
    def from_json(cls, nodedata: dict) -> Node:
        return cls(nodedata['lat'], nodedata['lon'], nodedata['id'])

class Way:
    def __init__(self, nodes: list, id: str, tags):
        self.nodes = nodes
        self.id = id
        self.tags = tags

    @classmethod
    def from_json(cls, way: dict):
        tags = way['tags'] if 'tags' in way else {}
        return cls(way['nodes'], way['id'], tags)

    @staticmethod
    def json_to_ways(json_ways):
        ways = json_ways['elements']
        formatted_ways = {way['id']:Way.from_json(way) for way in ways}
        return formatted_ways

class Route:
    def __init__(self, route: list, distance: int, routeID=None):
        self.route = route
        self.distance = distance
        self.id = routeID #ID in database

    @property
    def json(self):
        return {
            "success": True,
            "route": self.route,
            "dist": self.distance,
            "id": self.id
        }

    @staticmethod
    def get_coordinate_units(location):
        """Coordinate unit in terms of metres for localized area
        Horizontal Unit is distance for 1 unit of longitude
        Vertical Unit is distance for 1 unit of latitude
        """
        latitude,longitude = location
        hor_unit  = location - Point(latitude,longitude + 1)
        vert_unit  = location - Point(latitude + 1,longitude)
        return vert_unit, hor_unit

    @classmethod
    def rectangle_bounding_box(cls,location:Point,length:float,width:float)-> str:
        """
        Takes point and generates rectangular bounding box
        around point with width and length
        """
        vert_unit,hor_unit = cls.get_coordinate_units(location)
        latitude,longitude = location
        lat_unit = (width/2) / vert_unit
        lon_unit = (length/2) / hor_unit
        la1 = latitude - lat_unit
        lo1 = longitude - lon_unit
        la2 = latitude + lat_unit
        lo2 = longitude + lon_unit
        bounding_coords = ','.join(list(map(str,[la1,lo1,la2,lo2])))
        return bounding_coords

    @classmethod
    def two_point_bounding_box(cls,location:Point,other_location:Point)-> str:
        """
        Takes two points and generates rectangular bounding box
        that is uniquely oritentated about points
        """
        vert_unit,hor_unit = cls.get_coordinate_units(location)
        pi = math.pi
        lat1,long1 = location
        lat2,long2 = other_location
        # distance = math.sqrt((lat2 - lat1)**2 + (long2 - long1)**2)

        distance = location - other_location
        vert_scale = distance / vert_unit
        hor_scale = distance / hor_unit

        theta = math.atan2((lat2 - lat1),(long2 - long1))
        mlat1,mlong1 = lat1 + math.sin(theta - pi) * vert_scale, long1 + math.cos(theta - pi) * hor_scale
        mlat2,mlong2 = lat2 + math.sin(theta)      * vert_scale, long2 + math.cos(theta)      * hor_scale
        theta2 = (2*pi - (pi/2 - theta))
        a = Point(mlat1 + math.sin(theta2)      * vert_scale, mlong1 + math.cos(theta2)      * hor_scale)
        b = Point(mlat1 + math.sin(theta2 - pi) * vert_scale, mlong1 + math.cos(theta2 - pi) * hor_scale)
        c = Point(mlat2 + math.sin(theta2)      * vert_scale, mlong2 + math.cos(theta2)      * hor_scale)
        d = Point(mlat2 + math.sin(theta2 - pi) * vert_scale, mlong2 + math.cos(theta2 - pi) * hor_scale)

        print(a,b,c,d)

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
                if node not in neighbours: neighbours[node] = set()
                neighbours[node] |= node_neighbours
        return neighbours

    @classmethod
    async def from_database(cls,db,route_id):
        """
        Creates a route object from a route stored in the database
        """
        route = await db.find_one({'id_':route_id})
        return cls(route_id, **route['route'])

    @classmethod
    async def from_GPX(cls, nodes: dict, track): #<--XML object
        route = [Node(pt[0],pt.get[1],"").closest_distance(nodes)
                 for pt in track]
        dist = cls.get_route_distance(route,nodes)
        return cls(route,dist)

    @classmethod
    def generate_route(cls, nodes: dict, ways: dict, start_id: int, end_id: int, preferences: dict=None) -> Route:
        """
        Generates the shortest route to a destination
        Uses A* with euclidean distance as heuristic
        Uses tags to change cost of moving to nodes
        """
        unvisited = set(node_id for node_id in nodes)
        visited = set()
        path_dict = dict((node,(inf,[node])) for node in nodes)
        neighbours = cls.find_neighbours(ways)
        path_dict[start_id] = (0,[start_id])
        vert_unit,hor_unit = cls.get_coordinate_units(nodes[start_id])
        end_point = nodes[end_id]

        if end_id not in nodes:     raise Exception('End node not in node space. Specify a valid node.')
        elif start_id not in nodes: raise Exception('End node not in node space. Specify a valid node.')
        elif end_id not in neighbours or start_id not in neighbours: raise Exception('No connecting neighbour')
        else: current = start_id

        while True:
            current_point = nodes[current]
            current_cost,current_path = path_dict[current]
            current_neighbours = neighbours[current]
            for neighbour in current_neighbours:
                if neighbour in unvisited:
                    neighbour_cost,neighbour_path = path_dict[neighbour]
                    neighbour_point = nodes[neighbour]
                    heuristic_distance = current_point.heuristic_distance(neighbour_point,vert_unit,hor_unit)
                    tag_cost = 0 #heuristic_distance * sum(preferences[tag] for tag in neighbour_tags)
                    new_cost = heuristic_distance + current_cost + tag_cost
                    if new_cost < neighbour_cost:
                        path_dict[neighbour] = (new_cost,current_path + [neighbour])
            unvisited.remove(current)
            visited.add(current)
            if end_id in visited: break
            else:
                min_cost,next_node = inf, None
                for node_id in unvisited:
                    current_distance,path = path_dict[node_id]
                    current_point = nodes[node_id]
                    heuristic_distance = end_point.heuristic_distance(current_point,vert_unit,hor_unit)
                    current_cost = current_distance + heuristic_distance
                    if current_cost < min_cost: min_cost,next_node = current_cost,node_id
                if min_cost == inf: raise Exception("End node cannot be reached")
                else: current = next_node

        heuristic_cost, fastest_route = path_dict[end_id]
        actual_distance = cls.get_route_distance(fastest_route,nodes)
        return cls(fastest_route,actual_distance)

    @staticmethod
    def get_route_distance(fastest_route:list,nodes:dict)-> float:
        route_points = [nodes[node_id] for node_id in fastest_route]
        actual_distance = sum(route_points[index]-route_points[index+1] for index in range(len(route_points)-1))
        return actual_distance

    async def save_route(self, db, userid):
        #Adds to database of routes
        document = {
            "author":userid,
            "route":{
                "route":self.route,
                "distance":self.distance,
                }
            }
        self.id = await db.routes.insert_one(document).inserted_id

if __name__ == '__main__':
    a = Point(0, 0)
    b = Point(10, 10)
    Route.two_point_bounding_box(b,a)
