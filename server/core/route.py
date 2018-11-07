import math, copy

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

    def closest_node(self, nodes):
        """Returns the closest node from a list of nodes"""
        nodes = sorted(nodes.values(), key=lambda n: n.pos - self)
        closest_node = nodes[0]
        return closest_node


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
    def __init__(self, data):
        self.id = data.get('id')
        self.dist = math.inf # weight value for djikstras algo??!? maybe in future ratings can affect the wieght
        self.neighbours = set()
        self.pos = Point(
            data.get('lat'),
            data.get('lon')
        )
    
    def __eq__(self, other):
        return self.id == other.id

        
class Way:
    def __init__(self, route, data):
        self.route = route
        self.id = data.get('id')
        self.tags = data.get('tags')
        self.nodes = [route._nodes.get(n) for n in data.get('nodes')]
        
class Route:
    """Class that generates the route"""

    def __init__(self, nodedata: dict, waydata: dict, start: str, end: str, preferences: dict=None):
        self.nodes = {n['id']: Node(n) for n in nodedata}
        self.ways = [Way(self, way) for way in waydata]
        self.start = Point(start).closest_node(self.nodes)
        self.end = Point(end).closest_node(self.nodes)
        self.pref = preferences
        self._route = []

    @property
    def json(self) -> list:
        """Returns a serializable output that can be sent as a response"""
        if self._route == []:
            self.generate_route()
        return self._route
    
    def generate_route(self) -> None:
        unvisited = copy.deepcopy(self._nodes)
        unvisited.pop(self.start.id)
        current = self.start
        current.dist = 0

        while current != self.end:
            if current in current.neighbours:
                current.neighbours.remove(current) #Removes self from list of neighbours (Bug with xml reading code)
            for node in current.neighbours:
                d = current.pos - node.pos + current.dist
                if d < node.dist:
                    node.dist = d
            unvisited.pop(current, None)
            current = sorted(unvisited.values() ,key=lambda x: x.dist)[0] #Find next node that has the lowest dist value
        
        #Work out a path using the graph
        current = self.end

        while current != self.start:
            self._route.append(sorted(nodes[current].neighbours,key=lambda x:nodes[x].dist)[0]) #Chooses the neighbour with the closest dist to start 
            current = path[-1]

if __name__ == '__main__':
    p1 = Point(-33.910,151.106)
    p2 = Point(-33.900,151.116)

    print(p1 - p2)
