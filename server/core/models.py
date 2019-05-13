from dataclasses import dataclass
import datetime

import bcrypt
import jwt

from PIL import Image

import os
from io import BytesIO
from sanic import Sanic
from sanic.exceptions import abort

from .utils import snowflake

from .route import Route 

class User:
    """
    User class for database that holds all information
    Abdur Raqeeb/Jason Yu
    """

    def __init__(self, app, user_id, credentials, full_name, dob, username, avatar, recent_routes, groups, stats, real_time_route, saved_routes):
        self.app = app
        self.user_id = user_id
        self.credentials = credentials
        self.dob = dob
        self.username = username
        self.avatar = avatar
        self.full_name = full_name
        self.recent_routes = recent_routes
        self.groups = groups
        self.stats = stats
        self.saved_routes = saved_routes
        self.real_time_route = real_time_route

    @classmethod
    def from_data(cls, app, data):
        """
        Generates User class from database data
        Modifies certain variables to be in python data type
        Abdur Raqeeb/Jason Yu
        """
        data['user_id']         = data.pop('_id')
        data['saved_routes']    = [SavedRoute.from_data(route) for route in data['saved_routes']]
        data['recent_routes']   = [RecentRoute.from_data(route) for route in data['recent_routes']]
        data['groups']          = [Group(app, g) for g in data.get('groups', [])]
        data['credentials']     = Credentials(**(data['credentials']))
        data['stats']           = UserStats(**(data['stats']))
        data['real_time_route'] = RealTimeRoute.from_data(**(data['real_time_route']))
        user = cls(app, **data)
        return user

    def __hash__(self):
        return self.user_id

    def check_password(self, password):
        """
        Checks encrypted password
        Abdur Raqeeb
        """
        return bcrypt.checkpw(password, self.credentials.password)

    async def update(self):
        """
        Updates user with current data
        Abdur Raqeeb
        """
        document = self.to_dict()
        await self.app.db.users.update_one({'user_id': self.user_id}, document)
    
    async def delete(self):
        """
        Deletes user from database
        Abdur Raqeeb
        """
        await self.app.db.users.delete_one({'user_id': self.user_id})
    
    async def create_group(self, name):
        
        group_id = snowflake()

        await self.app.db.groups.insert_one({   
            '_id': group_id,
            'name': name,
            'owner_id': self.user_id,
            'members': [ self.user_id ],
            'messages': []
            })
        await self.app.db.users.update_one(
            {'_id':self.user_id},
            {'$addToSet': {'groups': group_id}}
        )

    async def add_to_group(self,group_id):
        """
        Adds the user to a group
        """
        await self.app.db.groups.update_one(
            {'_id':group_id},
            {'$addToSet': {'members':self.user_id}}
        )
        await self.app.db.users.update_one(
            {'_id':self.user_id},
            {'$addToSet': {'groups': group_id}}
        )
    
    async def remove_from_group(self, group_id):
        """
        Removes the user from the group
        """
        await self.app.db.groups.update_one(
            {'_id':group_id},
            {'$pull': {'members':self.user_id}}
        )
        await self.app.db.users.update_one(
            {'_id':self.user_id},
            {'$pull': {'groups': group_id}}
        )
    
    def to_dict(self):
        """
        Returns user data as a dict
        Abdur Raqeeb/ Jason Yu
        """
        return {
            "_id": self.user_id,
            "full_name": self.full_name,
            "username": self.username,
            "avatar": self.avatar,
            "dob": self.dob,
            "recent_routes": [recent_route.to_dict() for recent_route in self.recent_routes],
            "saved_routes": {saved_route.name:saved_route.to_dict() for saved_route in self.saved_routes},
            "stats": self.stats.to_dict(),
            "credentials": self.credentials.to_dict(),
            "real_time_route" : self.real_time_route.to_dict(),
            "groups": self.groups,
        }

@dataclass
class Credentials:
    """
    Class to hold important user information
    Abdur Raqeeb
    """
    email: str
    password: str
    token: str = None

    def to_dict(self):
        return {
            "email": self.email,
            "password": self.password,
            "token": self.token,
        }

class Group:
    """
    A class that holds messages and information of members in a group
    Jason Yu/Sunny Yan/Abdur (DB methods)
    """
    def __init__(self, app, data):
        self.app = app
        self.id = data['group_id']
        self.name = data['name']
        self.members = data['members']
        self.owner = data['owner_id']
        self.messages = data['messages']
	
    @classmethod
    def from_db(cls, app, group_id):
        document = app.db.groups.find_one({'_id':group_id})
        return cls(app,document)

    def invite_person(self, person):
        self.members.append(person)

    def invite_people(self,people):
        for person in people:
            self.invite_person(person)

    def __iter__(self):
        return zip(vars(self).keys(),vars(self).values())

    def to_dict(self):
        return vars(self)

    def update_db(self):
        self.app.db.groups.update_one(
            {'_id': self.id},
            {'$set': self.__dict__}
        )

class RealTimeRoute: 
    """
    Class that contains information of a real time run
    Not sure currently whether to implement on javascript side or not
    Real time route might be to connect multiple people running same race
    Jason Yu
    """
    def __init__(self, location_history=[]):
        self.location_history = location_history

    @classmethod
    def from_data(cls, location_history):
        location_history = [LocationPacket(location_packet.location, location_packet.time) for location_packet in location_history]
        real_time_route = cls(location_history)
        return real_time_route

    def update_location_history(self, location, time):
        self.location_history.append(LocationPacket(location,time))

    def calculate_speed(self, period):
        """
        Speed for the last period of time
        Jason Yu
        """
        location_count = int(period / self.update_freq)
        if location_count < 2: 
            raise Exception("Period not long enough")
        else:
            history_length = len(self.location_history)
            locations = [location_packet.location for location_packet in self.location_history[(history_length-1)-location_count:]]
            total_distance = RealTimeRoute.get_distance(locations)
            speed = total_distance / period
            return speed

    def calculate_average_speed(self):
        """
        Speed for the whole duration of time
        Jason Yu
        """
        current_duration = (len(self.location_history) - 1) * self.update_freq #Total elapsed time
        locations = [location_packet.location for location_packet in self.location_history]
        total_distance = RealTimeRoute.get_distance(locations)
        speed = total_distance / current_duration
        return speed

    @staticmethod
    def get_distance(locations):
        return Route.get_route_distance(locations)

    @staticmethod
    def calculate_pace(speed):
        """Speed is in m/s"""
        total_seconds = int(1000 / speed)
        minutes = int(total_seconds / 60)
        seconds = total_seconds - 60 * minutes
        return {"minutes": minutes, "seconds": seconds}

    def to_dict(self):
        return {
            "location_history" : [location_packet.to_dict() for location_packet in self.location_history],
        }

class LocationPacket:
    def __init__(self, location, time):
        self.location = location
        self.time = time

    def to_dict(self):
        return {
            'latitude': self.location.latitude,
            'longitude': self.location.longitue,
            'time': self.time
        }

class RunningSession:
    """
    Running Session holds multiple people running the same race
    Coaches can view runners realtime data
    """
    def __init__(self, users):
        self.runners = dict((user.fullname, user) for user in users)

    def get_speeds(self, period):
        information = {}
        for user_name,user in self.runners.items(): 
            speed = user.running_session.calculate_speed(period)
            information[user_name] = speed
        return information

    def get_average_speeds(self):
        information = {}
        for user_name,user in self.runners.items(): 
            speed = user.running_session.calculate_average_speed()
            information[user_name] = speed
        return information

    def get_distances(self):
        information = {}
        for user_name,user in self.runners.items(): 
            locations = user.running_session.location_history
            distance = RealTimeRoute.get_distance(locations)
            information[user_name] = distance
        return information

@dataclass
class UserStats:
    """
    Class to hold user running stats
    Jason Yu
    """
    num_runs: int = 0
    total_distance: int = 0
    longest_distance_ran: int = None
    fastest_km : int = None
    fastest_5km: int = None
    fastest_10km : int = None
    fastest_marathon: int = None
    estimated_v02_max: int = None
    average_heart_rate: int = None
    cadence: int = None

    def to_dict(self):
        return  {
            "num_runs": self.num_runs,
            "total_distance": self.total_distance,
            "longest_distance_ran": self.longest_distance_ran,
            "fastest_km" : self.fastest_km,
            "fastest_5km": self.fastest_5km,
            "fastest_10km" : self.fastest_10km,
            "fastest_marathon": self.fastest_marathon,
            "estimated_v02_max": self.estimated_v02_max,
            "average_heart_rate": self.average_heart_rate,
            "cadence": self.cadence,
        }

class SavedRoute: 
    """
    A route that has been saved by the user to be shared on feed
    Jason Yu
    """
    def __init__(self, name, route, start_time, duration, real_time_route, route_image, points, description):
        self.name = name
        self.route = route
        self.start_time = start_time
        self.duration = duration
        self.real_time_route = real_time_route 
        self.route_image = route_image	
        self.points = points
        self.description = description	

    @classmethod
    def from_data(cls, data):
        """
        Generates Saved Route class from database data
        Jason Yu
        """
        data['route'] = Route.from_data(**(data['route']))
        saved_route = cls(**data)
        return saved_route	

    def to_dict(self):
        return  {
            "name": self.name,
            "route": self.route.to_dict(),
            "start_time": self.start_time,
            "duration": self.duration,
            "real_time_route": self.real_time_route.to_dict(),
            "points": self.points,
            "description": self.description,
            "route_image": self.route_image,
        }

class RecentRoute: 
    """
    All recent routes that user has finish are automatically stored
    Jason Yu
    """
    def __init__(self, route, start_time, duration, real_time_route):
        self.route = route
        self.start_time = start_time
        self.duration = duration
        self.real_time_route = real_time_route

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
            "start_time": self.start_time,
            "duration": self.duration,
            "route": self.route.to_dict(),
            "real_time_route": self.real_time_route.to_dict(),
        }

class UserBase:
    def __init__(self, app):
        self.app = app
        self.user_cache = {}
        self.group_cache = {}
    
    async def find_account(self, **query):
        """
        Returns a user object based on the query
        Abdur Raqeeb
        """
        # Checks if user can be retrieved from cache
        if len(query) == 1 and 'user_id' in query:
            user =  self.user_cache.get(query['user_id'])
            if user:
                return user
        data = await self.app.db.users.find_one(query)
        if not data: 
            return None
        print(data)
        user = User.from_data(self.app, data)
        self.user_cache[user.user_id] = user
        return user

    async def register(self, request):
        """
        Registers user to database
        Abdur Raqeeb
        """
        data = request.json
        # Extracting fields
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name')
        dob = data.get('dob')
        username = data.get('username')
        # Creating intial user stat template
        initial_stats = UserStats()
        #Reading Default Avatar Image
        with open('server/core/resources/avatar.png','rb') as img:
            avatar = img.read()
        # Verifying Valid Account
        query = {'credentials.email': email}
        exists = await self.find_account(**query)
        if exists: abort(403, 'Email already in use.') 
        # Unique User Id
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password, salt)
        user_id = str(snowflake())
        # Adding Avatar to images
        await self.app.db.images.insert_one({
            'user_id': user_id,
            'avatar': avatar
            })
        # Generates document for DB
        document = {
            "_id": user_id,
            "recent_routes": [],
            "saved_routes": {},
            "full_name": full_name,
            "username": username,
            "avatar": avatar,
            "dob": dob,
            "stats": initial_stats.to_dict(),
            "credentials": {
                "email": email,
                "password": hashed,
                "token": None
            },
            "real_time_route" : { 
                "location_history" : [],
            },
            "groups": [],
        }
        # Adds user to DB
        await self.app.db.users.insert_one(document)
        user = User.from_data(self.app, document)
        return user

    async def issue_token(self, user):
        '''
        Creates and returns a token if not already existing
        Abdur Raqeeb
        '''
        if user.credentials.token:
            return user.credentials.token
        #Generates info for token
        payload = {
            'sub': user.user_id,
            'iat': datetime.datetime.utcnow()
        }
        user.credentials.token = token = jwt.encode(payload, self.app.secret)
        # Adds token to credentials
        await self.app.db.users.update_one(
            {'user_id': user.user_id}, 
            {'$set': {'credentials.token': token}}
        )
        
        return token

class Overpass:
    """Sunny"""
    BASE = 'http://overpass-api.de/api/interpreter?data='
    REQ = BASE + '''
[out:json];
(
    way
        [highway]
        (poly:"{}");
    >;
);
out;'''.replace("\n","").replace("\t","")
    #^^Replace statements only required to make the command easier to read
    #You can put this command in one line in the final version
    #Command description: Finds all ways with the tag highway in the area given,
    #then finds all nodes associated with these ways

class Color:
    green = 0x2ecc71
    red = 0xe74c3c
    orange = 0xe67e22
