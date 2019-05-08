from __future__ import annotations
import copy
import json
from math import *

EARTH_RADIUS = 6371000

class Heuristic:
    """
    Heuristic used to generate routes to the users preference's
    Jason Yu
    """
    def __init__(self, file_name):
        pass
        
    def open_file(self, file_name):
        json_file = open(file_name)
        json_data = json.loads(json_file)

class Point:
    """
    Represents a geodetic point with latitude and longitude
    Jason Yu/Abdur Raqueeb/Sunny Yan
    """
    def __init__(self, latitude: float, longitude: float):
        self.latitude = round(float(latitude),9)
        self.longitude = round(float(longitude),9)

    @classmethod
    def from_string(cls, string):
        """
        Generates Point class from string data
        Abdur Raqueeb
        """
        lat, long = string.split(',')
        return cls(lat, long)

    def distance(self, other: Point) -> float:
        """
        Uses spherical geometry to calculate the surface distance between two points.
        Sunny Yan
        """
        lat1, lon1 = self
        lat2, lon2 = other
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = (
            sin(dlat / 2)
            * sin(dlat / 2)
            + cos(radians(lat1))
            * cos(radians(lat2))
            * sin(dlon / 2)
            * sin(dlon / 2)
            )
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return EARTH_RADIUS * c

    def euclidean_distance(self,other:Point):
        '''
        Euclidean distance between two points (NON SPHERICAL)
        Jason Yu
        '''
        lat1,long1 = self
        lat2,long2 = other
        return sqrt((long1-long2)**2 + (lat1-lat2)**2)

    def heuristic_distance(self, other: Point, hor_unit: float, vert_unit: float) -> float:
        """
        Heuristic value based on euclidean distance on geo units
        Jason YU
        """
        delta_lat = abs(self.latitude - other.latitude)
        delta_lon = abs(self.longitude - other.longitude)
        x_dist = hor_unit * delta_lon
        y_dist = vert_unit * delta_lat
        return x_dist**2 + y_dist**2

    def __iter__(self):
        """
        Allows for easy splitting of location data
        Abdur Raqueeb
        """
        return iter((self.latitude, self.longitude))

    def __sub__(self, other: Point) -> int:
        """
        Abdur Raqueeb
        Another way to call the distance function
        """
        return self.distance(other)

    def __repr__(self):
        return f'({self.latitude},{self.longitude})'

    def closest_node(self, nodes: dict) -> Node:
        """
        Returns the closest node from a dict of nodes
        Abdur Raqueeb
        """
        sorted_nodes = sorted(nodes.values(), key=lambda other: self - other) 
        return sorted_nodes[0]
    
    def closest_way_node(self, nodes: dict, way_node_ids: set) -> Node:
        """
        Returns closest node which is in a way from a dict of nodes and a dict of ways
        Not in use
        Jason Yu
        """
        sorted_nodes = sorted(nodes.values(), key=lambda other: self - other)
        for node in sorted_nodes:
            if node.id in way_node_ids:
                return node
        else:
            raise Exception('No way node could be found.')

    def get_midpoint(self, other) -> Point:
        """
        Midpoint of two points that is calculated via euclidean multi_distance
        Not Accurate over large distances for coordinates
        Jason Yu
        """
        delta_lat = (other.latitude - self.latitude) / 2
        delta_lon = (other.longitude - self.longitude) / 2
        return Point(self.latitude + delta_lat,self.longitude + delta_lon)

    @staticmethod
    def radians_to_degrees(radians):
        return radians / pi * 180

    def check_below_line(self,left_point,right_point):
      gradient = left_point.gradient(right_point)
      if gradient == 0: return self.latitude < left_point.latitude # If point y is less, it is below
      elif gradient == inf: return self.latitude < max([left_point.latitude,right_point.latitude]) # point y is less than max, it is below
      else:
        line_equation = lambda x: gradient * (x - left_point.longitude) + left_point.latitude
        return self.latitude <= line_equation(left_point.longitude) #Below line
    
    def gradient(self,other):
        """
        Returns gradient from point 1 to point 2
        """
        delta_y = (other.latitude - self.latitude)
        delta_x = (other.longitude - self.longitude)
        if delta_y == 0: return 0
        elif delta_x == 0: return inf
        else: return delta_y / delta_x

class Node(Point):
    """
    Node class holds tags and is parent to Point
    Jason Yu
    """
    def __init__(self, latitude: float, longitude: float, id: str, tags:dict):
        super().__init__(latitude, longitude)
        self.id = id
        self.tags = tags
        self.ways = set()
        self.tag_multiplier = 1

    def __eq__(self, other: Point):
        """
        Abdur Raqueeb
        """
        return self.id == other.id

    def get_tag_multiplier(self, profile):
        """
        Jason Yu
        """
        return 1

    @staticmethod
    def json_to_nodes(json_nodes: list) -> dict:
        """
        Generates a dictionary of nodes from json
        Jason Yu/Abdur Raqueeb
        """
        return {node['id']: Node.from_json(node) for node in json_nodes}

    @classmethod
    def from_json(cls, json_node: dict) -> Node:
        """
        Generates a Node class from a json
        Jason Yu/Abdur Raqueeb
        """
        return cls(json_node['lat'], json_node['lon'], json_node['id'],json_node.get('tags',{}))

class Way:
    """
    Way class is a class that holds nodes
    Jason Yu/Abdur Raqueeb
    """
    def __init__(self, nodes: list, id: str, tags):
        self.node_ids = nodes
        self.id = id
        self.tags = tags

    @classmethod
    def from_json(cls, json_way: dict):
        """
        Generates a Way class from a json
        Jason Yu/Abdur Raqueeb
        """
        return cls(json_way['nodes'], json_way['id'], json_way.get('tags',{}))

    @staticmethod
    def json_to_ways(json_ways: list):
        """
        Generates a dictionary of ways from json
        Jason Yu/Abdur Raqueeb
        """
        return {way['id']:Way.from_json(way) for way in json_ways}

    @staticmethod
    def get_way_node_ids(ways):
        """
        Gets node ids that are in ways
        Not in use
        Jason Yu
        """
        return set(node_id for way in ways.values() for node_id in way.node_ids) 

    def update_node_tags(self, nodes):
        """
        Updates node tags
        Not in use yet.
        Jason YU
        """
        for node_id in self.node_ids:
            if node_id in nodes:
                nodes[node_id].tags.update(self.tags)

class Route:
    """
    Class that describes a running route
    Jason Yu/Abdur Raqueeb
    """
    def __init__(self, route: list, distance: int):
        self.route = route
        self.distance = distance

    @property
    def json(self):
        """
        Jason Yu/Abdur Raqueeb
        """
        json = self.to_dict()
        json['success'] = True
        return json

    def to_dict(self):
        """
        Jason Yu/Abdur Raqueeb
        """
        route = [{'latitude': node.latitude, 'longitude': node.longitude} for node in route_nodes]
        return {
            "route": route,
            "dist": self.distance
        }

    @classmethod
    def from_data(cls, route, distance):
        route = [Point(node_json.latitude, node_json.longitude) for node_json in route]
        return cls(route, distance)

    @classmethod
    def rectangle_bounding_box(cls,location:Point,length:float,width:float)-> str:
        """
        Takes point and generates rectangular bounding box
        around point with width and length
        Jason Yu
        """
        vert_unit,hor_unit = cls.get_coordinate_units(location)
        latitude,longitude = location
        lat_unit = (width/2) / vert_unit
        lon_unit = (length/2) / hor_unit
        point1 = Point(latitude - lat_unit, longitude - lon_unit)
        point2 = Point(latitude + lat_unit, longitude + lon_unit)
        return [point1, point2]

    @classmethod
    def two_point_bounding_box(cls,location:Point,other:Point)-> str:
        """
        Takes two points and generates rectangular bounding box
        that is uniquely oritentated about points
        Jason Yu
        """
        #Constants and distance units
        vert_unit,hor_unit = cls.get_coordinate_units(location)
        lat1,long1 = location
        lat2,long2 = other
        #Scaling factors
        distance = location - other
        vert_scale = distance / vert_unit
        hor_scale = distance / hor_unit
        delta_lat = other.latitude - location.latitude
        delta_lon = other.longitude - location.longitude
        #Two Point Extensions for intial in either direction
        theta = atan2(delta_lat, delta_lon) #Intial theta based on intial points
        point1 = Point(location.latitude + sin(theta) * vert_scale,location.longitude + cos(theta) * hor_scale)
        point2 = Point(other.latitude + sin(theta - pi) * vert_scale,other.longitude + cos(theta - pi) * hor_scale)
        #Four perpendicular vertices extended from extensions in either direction
        theta2 = (theta - pi/2) #Perpendicular to initial theta
        a = Point(point1.latitude + sin(theta2)      * vert_scale, point1.longitude + cos(theta2)      * hor_scale)
        b = Point(point1.latitude + sin(theta2 - pi) * vert_scale, point1.longitude + cos(theta2 - pi) * hor_scale)
        c = Point(point2.latitude + sin(theta2)      * vert_scale, point2.longitude + cos(theta2)      * hor_scale)
        d = Point(point2.latitude + sin(theta2 - pi) * vert_scale, point2.longitude + cos(theta2 - pi) * hor_scale)
        #Point Order
        return [a,b,d,c]

    @classmethod 
    def get_convex_hull_points(cls, waypoints: list):
        """
        Gets points for convex hull from a list of nodes
        By Jason Yu
        """
        pairs = zip(waypoints[:-1], waypoints[1:])
        points = []
        for start, end in pairs:
            bounding_box_points = cls.two_point_bounding_box(start,end)
            points += bounding_box_points
        return points

    @classmethod
    def convex_hull(cls, points: list)-> str:
        """
        Generates a convex hull from a list of waypoint nodes
        By Jason Yu
        """
        if len(points) == 2: return cls.two_point_bounding_box(points[0],points[1])
        points = cls.get_convex_hull_points(points)
        starting_point = min(points, key=lambda point: point.latitude)
        theta_dict = {}
        for point in points:
            if point is starting_point: continue
            delta_x = point.longitude - starting_point.longitude
            delta_y = point.latitude - starting_point.latitude
            theta = Point.radians_to_degrees(atan2(delta_y,delta_x))
            theta_dict[point] = theta
        sorted_points = sorted(theta_dict, key=lambda k:theta_dict[k])
        left, right = [], []
        while True:
            if len(sorted_points) < 2:
                if len(sorted_points) == 1: left.append(sorted_points.pop())
                break
            left_point = sorted_points.pop()
            right_point = sorted_points.pop(0)
            left.append(left_point)
            right.append(right_point)
            sorted_points = [point for point in sorted_points if not point.check_below_line(left_point,right_point)]
        convex_hull = [starting_point] + right + list(reversed(left))
        return convex_hull

    @classmethod
    async def from_database(cls,db,route_id):
        """
        Creates a route object from a route stored in the database
        Abdur
        """
        route = await db.find_one({'id_':route_id})
        return cls(route_id, **route['route'])

    @classmethod
    def generate_route(cls, nodes: dict, ways: dict, start_id: int, end_id: int) -> Route:
        """
        Generates the shortest route to a destination
        Uses A* with euclidean distance as heuristic
        Uses tags to change cost of moving to nodes
        Jason Yu
        """
        #Set up constants, sets and distance units
        unvisited = set(node_id for node_id in nodes)
        visited = set()
        path_dict = dict((node,(inf,[node])) for node in nodes)
        neighbours = cls.find_neighbours(ways)
        path_dict[start_id] = (0,[start_id])
        vert_unit,hor_unit = cls.get_coordinate_units(nodes[start_id])
        end_point = nodes[end_id]
        #Verify whether route can be completed
        if end_id not in nodes:     raise Exception('End node not in node space. Specify a valid node.')
        elif start_id not in nodes: raise Exception('Start node not in node space. Specify a valid node.')
        elif end_id not in neighbours or start_id not in neighbours: raise Exception('No connecting neighbour')
        else: current = start_id
        #Loop through nodes and find all best sub-routes to then determine best route
        while True:
            current_point = nodes[current]
            current_cost,current_path = path_dict[current]
            current_neighbours = neighbours[current]
            #Loop neighbours and determine lowest heuristic value for sub-route
            for neighbour in (current_neighbours & unvisited): #Intersection of neighbours and unvisited
                neighbour_cost,neighbour_path = path_dict[neighbour]
                neighbour_node = nodes[neighbour]
                # Determine heuristic distance which is modified by tag multiplier
                heuristic_cost = neighbour_node.tag_multiplier * current_point.heuristic_distance(neighbour_node,vert_unit,hor_unit)
                new_cost = heuristic_cost + current_cost
                if new_cost < neighbour_cost:
                    path_dict[neighbour] = (new_cost,current_path + [neighbour])
            #Update visited and unvisited to stop backtracking
            unvisited.remove(current)
            visited.add(current)
            #Find next node which is cheapest accounting for distance to end
            if end_id == current: break
            else:
                unvisited_node_costs = dict()
                for node_id in unvisited:
                    current_distance,path = path_dict[node_id]
                    current_cost = current_distance + end_point.heuristic_distance(nodes[node_id],vert_unit,hor_unit)
                    unvisited_node_costs[node_id] = current_cost
                next_node,cost = min(unvisited_node_costs.items(),key=lambda item:item[1])
                if cost == inf:
                    raise Exception("End node cannot be reached")
                else: current = next_node
        #Retrieve route, calculate actual distance
        heuristic_cost, fastest_route = path_dict[end_id]
        route = [nodes[node_id] for node_id in fastest_route]
        actual_distance = cls.get_route_distance([nodes[node_id] for node_id in fastest_route])
        return cls(route, actual_distance)

    @classmethod
    def generate_multi_route(cls, nodes: dict, ways: dict, node_waypoint_ids: list) -> Route:
        """
        Generate route that passes through all way points in order
        Jason Yu
        """
        start = node_waypoint_ids[0]
        multi_distance = 0
        multi_route = [start]
        pairs = zip(node_waypoint_ids[:-1], node_waypoint_ids[1:])
        for current_node, next_node in pairs:
            route = cls.generate_route(nodes,ways,current_node,next_node)
            multi_distance += route.distance
            multi_route += route.route[1:]
        route = [nodes[node_id] for node_id in multi_route]
        return cls(route,multi_distance)

    @staticmethod
    def get_route_distance(fastest_route_nodes:list)-> float:
        """
        Find route distance from route nodes
        Jason Yu
        """
        return sum(fastest_route_nodes[index]-fastest_route_nodes[index+1] for index in range(len(fastest_route_nodes)-1))

    @staticmethod
    def find_neighbours(ways: dict) -> dict:
        """
        Generates neighbours for every node in provided ways
        Jason Yu
        """
        neighbours = {}
        for way in ways.values():
            for index, node in enumerate(way.node_ids):
                if node not in neighbours: neighbours[node] = set()
                if (index - 1) != -1: neighbours[node].add(way.node_ids[index - 1])
                if (index + 1) != len(way.node_ids): neighbours[node].add(way.node_ids[index + 1])
        return neighbours

    @staticmethod
    def get_coordinate_units(location):
        """
        Coordinate unit in terms of metres for localized area
        Horizontal Unit is distance for 1 unit of longitude
        Vertical Unit is distance for 1 unit of latitude
        Jason Yu
        """
        latitude,longitude = location
        hor_unit  = location - Point(latitude,longitude + 1)
        vert_unit  = location - Point(latitude + 1,longitude)
        return vert_unit, hor_unit

    @staticmethod
    def transform_json_nodes_and_ways(nodes_json:dict,ways_json:dict,profile:dict={}):
        """
        Convert node and way data to objects
        Update node tags and multipliers
        Jason Yu
        """
        nodes = Node.json_to_nodes(nodes_json)
        ways = Way.json_to_ways(ways_json)
        for way in ways.values():
            way.update_node_tags(nodes)
        for node in nodes.values():
            node.get_tag_multiplier(profile)
        return nodes,ways

    @staticmethod
    def bounding_points_to_string(points):
        return ' '.join(f'{p.latitude} {p.longitude}' for p in points)

    async def save_route(self, db, user_id):
        """
        Adds to database of routes
        """
        document = {
            "author":user_id,
            "route":{
                "route":self.route,
                "distance":self.distance,
                }
            }
        self.id = await db.routes.insert_one(document).inserted_id
		
	def generateStaticMap(self):
		"""
		Generate static 100x100 PNG of the route, encoded in Base64
		"""
		m = StaticMap(100,100)
		route = map(lambda pt:list(pt),self.route)
		for pts in zip(route[:-1],route[1:]):
			line = Line(pts,"blue", 2)
			m.add_line(line)
		image = m.render()
		buffer = BytesIO()
		image.save(buffer, format="PNG")
		return buffer

if __name__ == '__main__':
    pass
