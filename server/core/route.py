from .route_generation import Route, Point
from .points import run_stats
from .utils import snowflake

class LocationPacket:
    """
    Class that holds location in point form
    and time in float form which is seconds from inception
    Jason Yu
    """

    def __init__(self, latitude, longitude, timestamp, speed):
        self.location = Point(latitude, longitude)
        self.timestamp = timestamp
        self.speed = speed

    @classmethod
    def from_data(cls, data):
        return cls(**data)

    def to_dict(self):
        return {
            "location": self.location.to_dict(),
            "timestamp": self.timestamp,
            "speed": self.speed
        }

class Run:
    """
    A run that has been completed by user, but not saved to feed
    Jason Yu
    """

    def __init__(self, location_packets, run_info):
        self.location_packets = location_packets
        self.run_info = run_info

    @classmethod
    def from_real_time_route(cls, location_packets, run_info):
        """
        Generates Recent Route class from real time data
        Jason Yu
        """
        location_packets = [LocationPacket.from_data(packet) for packet in location_packets]
        run = cls(location_packets, run_info)
        return run

    @classmethod
    def from_data(cls, data):
        """
        Generates Recent Route class from database data
        Jason Yu
        """
        location_packets = [LocationPacket.from_data(packet) for packet in data['location_packets']]
        run = cls(location_packets, data['run_info'])
        return run

    def to_dict(self):
        return {
            "location_packets": [packet.to_dict() for packet in self.location_packets],
            "run_info": self.run_info,
        }


class SavedRun(Run):
    """
    A run that has been saved by the user to be shared on feed
    Jason Yu
    """

    def __init__(self, run_id, name, description, run_info, location_packets, likes, comments):
        super.__init__(location_packets, run_info)
        self.id = run_id
        self.name = name
        self.description = description
        self.likes = likes
        self.comments = comments

    @classmethod
    def from_data(cls, data):
        """
        Generates Saved Route class from database data
        Jason Yu
        """
        run_id = data.pop("id")
        data["location_packets"] = [LocationPacket.from_data(packet) for packet in data["location_packets"]]
        saved_run = cls(run_id, **data)
        return saved_run

    @classmethod
    def from_real_time_route(cls, name, description, run_info, location_packets, likes, comments):
        """
        Generates Saved Route class from real time data
        This is generally the first initialization, therefore route id is generated here
        Jason Yu
        """
        route_id = str(snowflake())
        location_packets = [LocationPacket.from_data(packet) for packet in location_packets]
        saved_route = cls(route_id, name, description, run_info, location_packets, likes, comments)
        return saved_route

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "location_packets": [packet.to_dict() for packet in self.location_packets],
            "run_info": self.run_info,
            "likes":self.likes,
            "comments":self.comments,
        }

class SavedRoute:
    """
    When a user generates a route and chooses to save it, they can reuse route again in the future.
    Jason Yu
    """
    def __init__(self, route_id, name, description, route):
        self.id = route_id
        self.name = name
        self.description = description
        self.route = route

    @classmethod
    def from_data(cls, data):
        runningRoute = Route.from_data(data)
        return cls(data['route_id'], data['name'], data['description'],runningRoute)

    @classmethod
    def from_real_time_route(cls, route, name, description):
        """
        Generate Saved Route with id
        """
        route_id = str(snowflake())
        saved_route = cls(route_id, name, description, route)
        return saved_route

    def to_dict(self):
        return {
            'id': self.id,
            'name':self.name,
            'route':self.route.to_dict(),
            'description':self.description,
        }
