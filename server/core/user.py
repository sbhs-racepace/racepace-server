from dataclasses import dataclass
import datetime

import bcrypt
import jwt

from sanic import Sanic
from sanic.exceptions import abort

from .utils import snowflake
from .models import SavedRoute, RecentRoute

class User:
    """
    User class for database that holds all information
    Abdur Raqeeb/Jason Yu
    """

    def __init__(self, app, user_id, **kwargs):
        self.app = app
        self.id = user_id
        self.credentials = kwargs.get('credentials')
        self.dob = kwargs.get('dob')
        self.username = kwargs.get('username')
        self.full_name = kwargs.get('full_name')
        self.recent_routes = kwargs.get('recent_routes')
        self.groups = kwargs.get('groups')
        self.stats = kwargs.get('stats')
        self.saved_routes = kwargs.get('saved_routes')
        self.real_time_route = kwargs.get('real_time_route')
        self.followers = kwargs.get('followers') # Holds user id
        self.following = kwargs.get('following') # Holds user id

    def __str__(self):
        return self.username

    @property
    def avatar_url(self):
        return f'https://racepace-sbhs.herokuapp.com/api/avatars/{self.id}.png'

    @classmethod
    def from_data(cls, app, data):
        """
        Generates User class from database data
        Modifies certain variables to be in python data type
        Abdur Raqeeb/Jason Yu
        """

        user_id = data.pop('_id')

        data['saved_routes']    = [SavedRoute.from_data(route) for route in data['saved_routes']]
        data['recent_routes']   = [RecentRoute.from_data(route) for route in data['recent_routes']]
        data['groups']          = {g['_id'] : Group(app, g) for g in data.get('groups', [])}
        data['credentials']     = Credentials(**(data['credentials']))
        data['stats']           = UserStats(**(data['stats']))
        data['real_time_route'] = RealTimeRoute.from_data(data['real_time_route'])

        user = cls(app, user_id, **data)
        return user

    def __hash__(self):
        return self.id

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
        await self.app.db.users.update_one({'user_id': self.id}, document)
    
    async def delete(self):
        """
        Deletes user from database
        Abdur Raqeeb
        """
        await self.app.db.users.delete_one({'user_id': self.id})
    
    async def create_group(self, name):
        
        group_id = snowflake()

        await self.app.db.groups.insert_one({   
            '_id': group_id,
            'name': name,
            'owner_id': self.id,
            'members': [ self.id ],
            'messages': []
            })
        await self.app.db.users.update_one(
            {'_id':self.id},
            {'$addToSet': {'groups': group_id}}
        )

    async def add_to_group(self,group_id):
        """
        Adds the user to a group
        """
        await self.app.db.groups.update_one(
            {'_id':group_id},
            {'$addToSet': {'members':self.id}}
        )
        await self.app.db.users.update_one(
            {'_id':self.id},
            {'$addToSet': {'groups': group_id}}
        )
    
    async def remove_from_group(self, group_id):
        """
        Removes the user from the group
        """
        await self.app.db.groups.update_one(
            {'_id':group_id},
            {'$pull': {'members':self.id}}
        )
        await self.app.db.users.update_one(
            {'_id':self.id},
            {'$pull': {'groups': group_id}}
        )
    
    def to_dict(self):
        """
        Returns user data as a dict
        Abdur Raqeeb/ Jason Yu
        """
        return {
            "_id": self.id,
            "full_name": self.full_name,
            "username": self.username,
            "avatar_url": self.avatar_url,
            "dob": self.dob,
            "recent_routes": [recent_route.to_dict() for recent_route in self.recent_routes],
            "saved_routes": {saved_route.name:saved_route.to_dict() for saved_route in self.saved_routes},
            "stats": self.stats.to_dict(),
            "credentials": self.credentials.to_dict(),
            "real_time_route" : self.real_time_route.to_dict(),
            "groups": self.groups,
            "followers": self.followers,
            "following": self.following,
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

@dataclass
class UserStats:
    """
    Class to hold user running stats
    Jason Yu
    """
    points: int = 0
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
            "points": self.points,
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
        user = User.from_data(self.app, data)
        self.user_cache[user.id] = user
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
            "followers": [],
            "following": [],
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
            'sub': user.id,
            'iat': datetime.datetime.utcnow()
        }
        user.credentials.token = token = jwt.encode(payload, self.app.secret)
        # Adds token to credentials
        await self.app.db.users.update_one(
            {'user_id': user.id}, 
            {'$set': {'credentials.token': token}}
        )
        
        return token