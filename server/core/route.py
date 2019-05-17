from .route_generation import Route 
from .points import run_stats

class RealTimeRoute: 
    """
    Class that contains information of a real time run
    Not sure currently whether to implement on javascript side or not
    Real time route might be to connect multiple people running same race
    Jason Yu
    """
    def __init__(self, start_time, location_history=[]):
        self.location_history = location_history
        self.start_time = start_time

    @property
    def duration(self):
        return 0 if len(self.location_history) == 0 else self.end - self.start

    @property 
    def start(self):
        return self.location_history[0].time

    @property 
    def end(self):
        return self.location_history[0].time

    @property 
    def distance(self):
        locations = [location_packet.location for location_packet in self.location_history]
        return self.get_distance(locations)

    @property 
    def average_speed(self):
        if self.duration == 0:
            raise Exception('Not enough location points logged')
        else:
            return self.distance / self.duration

    @classmethod
    def from_data(cls, data):
        json_location_history = data.get('location_history', [])
        start_time = Time(**data.get('start_time'))
        location_history = [LocationPacket(location_packet.location, location_packet.time) for location_packet in json_location_history]
        real_time_route = cls(start_time, location_history)
        return real_time_route

    def update_location_history(self, location, time):
        self.location_history.append(LocationPacket(location,time))

    def calculate_speed(self, period):
        """
        Speed for the approximately last period of time
        Jason Yu
        """
        if self.duration < period:
            return self.average_speed
        else:
            for index,location_packet in reversed(list(enumerate(self.location_history))):
                if (self.end - location_packet.time) >= period:
                    time = self.end - location_packet.time
                    # Location packets within period of time
                    location_packets = self.location_history[index:]
                    locations = [location_packet.location for location_packet in location_packets]
                    total_distance = RealTimeRoute.get_distance(locations)
                    return total_distance / time
            else:
                raise Exception('No Valid Period of time')

    @staticmethod
    def get_distance(locations):
        return Route.get_route_distance(locations)

    @staticmethod
    def speed_to_pace(speed):
        """
        With Speed in m/s, returns a json pace
        """
        total_seconds = int(1000 / speed)
        minutes = int(total_seconds / 60)
        seconds = total_seconds - 60 * minutes
        return {"minutes": minutes, "seconds": seconds}

    def to_dict(self):
        return { 
            "location_history" : [location_packet.to_dict() for location_packet in self.location_history],
            "start_time": self.start_time.to_dict()
        }

class LocationPacket:
    """
    Class that holds location in point form
    and time in float form which is seconds from inception
    Jason Yu
    """
    def __init__(self, location, time):
        self.location = location
        self.time = time

    def to_dict(self):
        return {
            'latitude': self.location.latitude,
            'longitude': self.location.longitue,
            'time': self.time
        }

class Time:
    """
    Using custom time due to python time not have to dict
    Jason Yu
    """
    def __init__(self, year, month, day, hour, minute, second):
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second
    
    def to_dict(self):
        return {
            'year': self.year,
            'month': self.month,
            'day': self.day,
            'hour': self.hour,
            'minute': self.minute,
            'second': self.second,
        }

class RunningSession:
    """
    Running Session holds multiple people running the same race
    Coaches can view runners realtime data
    """
    def __init__(self, runners):
        self.runners = runners

class RecentRoute: 
    """
    All recent routes that user has finish are automatically stored
    Jason Yu
    """
    def __init__(self, route, real_time_route, points):
        self.route = route
        self.real_time_route = real_time_route
        self.points = points

    @classmethod
    def from_real_time_route(cls, real_time_route, route):
        """
        Generates Saved Route class from real time data
        Jason Yu
        """
        route = Route.from_data(**(route))
        points = run_stats(route.distance, real_time_route.duration)
        saved_route = cls(route, real_time_route, points)
        return saved_route	

    @classmethod
    def from_data(cls, data):
        """
        Generates Saved Route class from database data
        Jason Yu
        """
        data['route'] = Route.from_data(**(data['route']))
        recent_route = cls(**data)
        return recent_route
    
    def to_dict(self):
        return  {
            "route": self.route.to_dict(),
            "real_time_route": self.real_time_route.to_dict(),
            "points": self.points,
        }

class SavedRoute(RecentRoute): 
    """
    A route that has been saved by the user to be shared on feed
    Jason Yu
    """
    def __init__(self, name, description, route, real_time_route,route_image, points):
        super.__init__(route,real_time_route,points)
        self.name = name
        self.description = description	
        self.route_image = route_image

    @classmethod
    def from_data(cls, data):
        """
        Generates Saved Route class from database data
        Jason Yu
        """
        data['route'] = Route.from_data(**(data['route']))
        saved_route = cls(**data)
        return saved_route	

    @classmethod
    def from_real_time_route(cls, name, description, route_image, real_time_route, route):
        """
        Generates Saved Route class from real time data
        Jason Yu
        """
        route = Route.from_data(**(route))
        points = run_stats(route.distance, real_time_route.duration)
        saved_route = cls(name, description, route, real_time_route,route_image, points)
        return saved_route	

    def to_dict(self):
        return  {
            "name": self.name,
            "description": self.description,
            "route": self.route.to_dict(),
            "real_time_route": self.real_time_route.to_dict(),
            "route_image": self.route_image,
            "points": self.points,
        }
