from dataclasses import dataclass
import datetime

import bcrypt
import jwt

from sanic import Sanic
from sanic.exceptions import abort

from .utils import snowflake

@dataclass
class Credentials:
    """
    Class to hold important user information
    Abdur Raqeeb
    """
    email: str
    password: str
    token: str = None

class User:
    """
    User class for database that holds all information
    Abdur Raqeeb/Jason Yu
    """

    def __init__(self, app, user_id, credentials, full_name='temp', dob='temp', username='temp'):
        self.app = app
        self.id = user_id
        self.credentials = credentials
        self.dob = dob
        self.username = username
        self.routes = []
        self.full_name = full_name
        self.groups = {}

    def __hash__(self):
        return self.id

    @classmethod
    def from_data(cls, app, data):
        """
        Generates User class from python data
        Abdur Raqeeb
        """
        print(data)
        routes,credentials = data.pop('routes'),data.pop('credentials')
        user = cls(app=app, **data)
        user.routes = routes
        return user

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
    
    async def create_group(self):
        return NotImplemented
    
    async def edit_group(self):
        return NotImplemented
    
    async def delete_group(self):
        return NotImplemented
    
    def to_dict(self):
        """
        Returns user data as a dict
        Abdur Raqeeb
        """
        return {
            "user_id": self.id,
            "routes": self.routes,
            "full_name": self.full_name,
            "username": self.username,
            "dob": self.dob,
            "credentials": {
                "email": self.credentials.email,
                "password": self.credentials.password,
                "token": self.credentials.token,
            }
        }

class SavedRoute: 
    """
    A route that has been saved by the user to be shared on feed
    """
    def __init__(self, route, start_time, end_time, duration):
        self.route = route
        self.distance = route.distance
        self.start_time = start_time
        self.end_time = end_time
        self.duration = duration

class Group:
    """
    A class that holds messages and information of members in a group
    Jason Yu
    """
    def __init__(self, id, name, members, owner):
        self.id = id
        self.name = name
        self.members = members
        self.owner = owner
        self.messages = []

    def invite_person(self, person):
        self.members.append(person)

    def invite_people(self,people):
        for person in people:
            self.invite_person(person)

class UserBase:
    def __init__(self, app):
        self.app = app
    
    async def find_account(self, **query):
        """
        Returns a user object based on the query
        Abdur Raqeeb
        """
        data = await self.app.db.users.find_one(query)
        if not data:
            return None
        
        user = User.from_data(self.app, data)

        return user

    async def register(self, request):
        """
        Registers user to database
        Abdur Raqeeb
        """
        data = request.json

        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name')
        dob = data.get('dob')
        username = data.get('username')
        query = {'credentials.email': email}
        exists = await self.find_account(**query)
        if exists: abort(403, 'Email already in use.') 

        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password, salt)

        document = {
            "full_name": full_name,
            "routes": {},
            "credentials": {
                "email": email,
                "password": hashed,
                "token": None
            },
            "username": username,
            "dob": dob,
        }

        result = await self.app.db.users.insert_one(document)
        document['user_id'] = str(result.inserted_id)
        user = User.from_data(self.app, document)
        return user

    async def issue_token(self, user):
        '''
        Creates and returns a token if not already existing
        Abdur Raqeeb
        '''
        if user.credentials.token:
            return user.credentials.token

        payload = {
            'sub': user.id,
            'iat': datetime.datetime.utcnow()
        }

        user.credentials.token = token = jwt.encode(payload, self.app.secret)

        await self.app.db.users.update_one(
            {'user_id': user.id}, 
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
