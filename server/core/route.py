import math

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

    def __init__(self, latitude, longitude):
        self.latitude = float(latitude)
        self.longitude = float(longitude)


    def distance(self, other):
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

    def __sub__(self, other):
        """
        Another way to call the distance function
        >>> point1 - point2
        69
        """
        return self.distance(other)


class Node:
    def __init__(self, data):
        self.id = data.get('id')
        self.weight = 0 # weight value for djikstras algo??!? maybe in future ratings can affect the wieght
        self.neighbours = set()
        self.pos = Position(
            data.get('lat'),
            data.get('long')
        )

        
class Way:
    def __init__(self, data, nodes):
        self.id = data.get('id')
        self.tags = data.get('tags')
        self.nodes = nodes
        

class Route:
    """Class that generates the route"""

    def __init__(self, nodedata, waydata, preferences=None):
        # sunny can u help in the creation of the node objects
        self._nodes = {n['id'] : Node(n) for n in nodedata} # stored in a dictionary for efficiency in next line
        self.ways = [Way(w, [self._nodes[n] for n in w['nodes']]) for w in waydata]
        self.preferences = preferences # things such as elevation/greenery etc

    @property
    def nodes(self):
        return self._nodes.values()

    @property
    def json(self):
        """Returns a serializable output that can be sent as a response"""
        
        return {'message': 'soz m8 not implemented yet'}
    
    def generate_route(self):
        return NotImplemented

if __name__ == '__main__':
    pass
    # do testing here buddies
