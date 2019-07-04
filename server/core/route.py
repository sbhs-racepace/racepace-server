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
        self.location = 
        location = data['location']
        latitude = data['latitude']
        longitude = data['longitude']
        return cls(latitude, longitude, data['timestamp'], data['speed'])

    def to_dict(self):
        return {
            "location": self.location.to_dict(),
            "timestamp": self.timestamp,
            "speed": self.speed
        }

class RecentRoute:
    """
    All recent routes that user has finish are automatically stored
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
        location_packets = [Location.from_data(packet) for packet in location_packets]
        saved_route = cls(location_packets, run_info, route)
        return saved_route

    @classmethod
    def from_data(cls, data):
        """
        Generates Recent Route class from database data
        Jason Yu
        """
        location_packets = [Location.from_data(packet) for packet in data['location_packets']]
        recent_route = cls(location_packets, data['run_info'], route)
        return recent_route

    def to_dict(self):
        return {
            "location_packets": [packet.to_dict() for packet in self.location_packets],
            "run_info": self.run_info,
        }


class SavedRoute(RecentRoute):
    """
    A route that has been saved by the user to be shared on feed
    Jason Yu
    """

    def __init__(self, route_id, name, description, route_image, run_info, location_packets, route):
        super.__init__(location_packets, run_info)
        self.id = route_id
        self.name = name
        self.description = description
        self.route_image = route_image
        self.route = route

    @classmethod
    def from_data(cls, data):
        """
        Generates Saved Route class from database data
        Jason Yu
        """
        route_id = data.pop("id")
        data["location_packets"] = [LocationPacket.from_data(packet) for packet in data["location_packets"]]
        data["route"] = Route.from_data(data['route'])
        saved_route = cls(route_id, **data)
        return saved_route

    @classmethod
    def from_real_time_route(cls, name, description, route_image, run_info, location_packets):
        """
        Generates Saved Route class from real time data
        This is generally the first initialization, therefore route id is generated here
        Jason Yu
        """
        points = run_stats(real_time_route.current_distance, real_time_route.current_duration)
        route_id = str(snowflake())
        location_packets = [LocationPacket.from_data(packet) for packet in location_packets]
        saved_route = cls(route_id, name, description, route_image, run_info, location_packets)
        return saved_route

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "route_image", route_image,
            "location_packets": [packet.to_dict() for packet in self.location_packets],
            "run_info": self.run_info,
            "route": self.route.to_dict()
        }
