from .route_generation import Route, Point
from .points import run_stats
from .utils import snowflake

class RealTimeRoute: 
    """
    Class that contains information of a real time run
    Not sure currently whether to implement on javascript side or not
    Real time route might be to connect multiple people running same race
    Jason Yu
    """
    def __init__(self, start_time=None, location_history=[], route=None, active=False, current_distance=0,current_duration=0):
        self.location_history = location_history
        self.start_time = start_time
        self.route = route
        self.active = active
        self.current_distance = current_distance
        self.current_duration = current_duration

    @property 
    def average_speed(self):
        if self.current_duration == 0:
            return None 
        else:
            return self.current_distance / self.current_duration

    @property 
    def most_recent_time(self):
        return self.location_history[-1].time

    @classmethod
    def setup_run(cls, start_time, route):
        class_data = {
            'start_time': start_time,
            'location_history': [],
            'route':route,
            'active':True,
            'current_distance': 0,
            'current_duration': 0,
        }
        real_time_route = RealTimeRoute.from_data(class_data)
        return real_time_route

    @classmethod
    def from_data(cls, data):
        if data['start_time'] is not None:
            data['start_time'] = Time(**data['start_time'])
        if data['route'] is not None:
            data['route'] = Route.from_data(**data['route'])
        data['location_history'] = [LocationPacket(**location_packet) for location_packet in data['location_history']]
        real_time_route = cls(**data)
        return real_time_route

    def update_location_history(self, latitude, longitude, time):
        current_location_packet = LocationPacket(latitude, longitude, time)
        if len(self.location_history) >= 1:
            previous_location_packet = self.location_history[-1]
            self.current_distance += current_location_packet.location - previous_location_packet.location
            self.current_duration += current_location_packet.time - previous_location_packet.time
        self.location_history.append(current_location_packet)

    def calculate_speed(self, period):
        """
        Speed for the approximately last period of time
        Jason Yu
        """
        if self.current_duration < period:
            return self.average_speed
        else:
            for index in reversed(range(len(self.location_history))):
                location_packet = self.location_history[index]
                if (self.most_recent_time - location_packet.time) >= period:
                    time = self.most_recent_time - location_packet.time
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
        if speed is None: 
            return {'minutes':'--','seconds':'--'}
        else:
            total_seconds = int(1000 / speed)
            minutes = int(total_seconds / 60)
            seconds = total_seconds - 60 * minutes
            return {"minutes": minutes, "seconds": seconds}

    def to_dict(self):
        return { 
            "location_history" : [location_packet.to_dict() for location_packet in self.location_history],
            "start_time": None if self.start_time is None else self.start_time.to_dict(),
            "route": None if self.route is None else self.route.to_dict(),
            "active": self.active,
            "current_distance": self.current_distance,
            "current_duration": self.current_duration,
        }

class LocationPacket:
    """
    Class that holds location in point form
    and time in float form which is seconds from inception
    Jason Yu
    """
    def __init__(self, latitude, longitude, time):
        self.location = Point(latitude, longitude)
        self.time = time

    def to_dict(self):
        return {
            'latitude': self.location.latitude,
            'longitude': self.location.longitude,
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
    def __init__(self, real_time_route, points):
        self.real_time_route = real_time_route
        self.points = points

    @classmethod
    def from_real_time_route(cls, real_time_route):
        """
        Generates Recent Route class from real time data
        Jason Yu
        """
        points = run_stats(real_time_route.current_distance, real_time_route.current_duration)
        saved_route = cls(real_time_route, points)
        return saved_route	

    @classmethod
    def from_data(cls, data):
        """
        Generates Recent Route class from database data
        Jason Yu
        """
        print(data)
        data['real_time_route'] = RealTimeRoute.from_data(**(data['real_time_route']))
        recent_route = cls(**data)
        return recent_route
    
    def to_dict(self):
        return  {
            "real_time_route": self.real_time_route.to_dict(),
            "points": self.points,
        }

class SavedRoute(RecentRoute): 
    """
    A route that has been saved by the user to be shared on feed
    Jason Yu
    """
    def __init__(self, route_id, name, description, real_time_route,route_image, points):
        super.__init__(real_time_route,points)
        self.id = route_id
        self.name = name
        self.description = description	
        self.route_image = route_image

    @classmethod
    def from_data(cls, data):
        """
        Generates Saved Route class from database data
        Jason Yu
        """
        route_id = data.pop('id')
        data['real_time_route'] = RealTimeRoute.from_data(**(data['real_time_route']))
        saved_route = cls(route_id,**data)
        return saved_route	

    @classmethod
    def from_real_time_route(cls, name, description, route_image, real_time_route):
        """
        Generates Saved Route class from real time data
        This is generally the first initialization, therefore route id is generated here
        Jason Yu
        """
        points = run_stats(real_time_route.current_distance, real_time_route.current_duration)
        route_id = str(snowflake())
        saved_route = cls(route_id, name, description, real_time_route, route_image, points)
        return saved_route	

    def to_dict(self):
        return  {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "real_time_route": self.real_time_route.to_dict(),
            "route_image": self.route_image,
            "points": self.points,
        }
