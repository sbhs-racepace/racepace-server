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
    Abdur Raqueeb
    """
    email: str
    password: str
    token: str = None

class User:
    """
    User class for database that holds all information
    Abdur Raqueeb
    """
    fields = ('id', 'credentials', 'routes')

    def __init__(self, app, user_id, credentials):
        self.app = app
        self.id = user_id
        self.credentials = credentials
        self.routes = []
        self.name = None
        
    def __hash__(self):
        return self.id

    @classmethod
    def from_data(cls, app, data):
        """
        Generates User class from python data
        Abdur Raqueeb
        """
        user_id = data['user_id']
        credentials = Credentials(*data['credentials'].values())
        user = cls(app, user_id, credentials)
        user.routes = data['routes']
        return user

    def check_password(self, password):
        """
        Checks encrypted password
        Abdur Raqueeb
        """
        return bcrypt.checkpw(password, self.credentials.password)

    async def update(self):
        """
        Updates user with current data
        Abdur Raqueeb
        """
        document = self.to_dict()
        await self.app.db.users.update_one({'user_id': self.id}, document)
    
    async def delete(self):
        """
        Deletes user from database
        Abdur Raqueeb
        """
        await self.app.db.users.delete_one({'user_id': self.id})
    
    def to_dict(self):
        """
        Returns user data as a dict
        Abdur Raqueeb
        """
        return {
            "user_id": self.id,
            "routes": self.routes,
            "credentials": {
                "email": self.credentials.email,
                "password": self.credentials.password,
                "token": self.credentials.token
            }
        }



class UserBase:
    def __init__(self, app):
        self.app = app
    
    async def find_account(self, **query):
        '''Returns a user object based on the query'''
        data = await self.app.db.users.find_one(query)

        if not data:
            return None
        
        user = User.from_data(self.app, data)

        return user

    async def register(self, request):
        """
        Registers user to database
        Abdur Raqueeb
        """
        data = request.json

        email = data.get('email')
        password = data.get('password')
        name = data.get('name')

        query = {'credentials.email': email}
        exists = await self.find_account(**query)
        if exists: abort(403, 'Email already in use.') 

        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password, salt)

        document = {
            "user_id": snowflake(),
            "name": name,
            "routes": {},
            "credentials": {
                "email": email,
                "password": hashed,
                "token": None
            }
        }

        user = User.from_data(self.app, document)

        await self.app.db.users.insert_one(document)

        return user

    async def issue_token(self, user):
        '''
        Creates and returns a token if not already existing
        Abdur Raqueeb
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
    BASE = 'http://overpass-api.de/api/interpreter?data=[out:json];'
    NODE = BASE + 'node(poly:"{}");out;'
    WAY = BASE + 'way(poly:"{}");out;'

class Color:
    green = 0x2ecc71
    red = 0xe74c3c
    orange = 0xe67e22
