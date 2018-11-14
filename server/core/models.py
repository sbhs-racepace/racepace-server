from dataclasses import dataclass
import datetime

import bcrypt
import jwt

from sanic import Sanic
from sanic.exceptions import abort

from .utils import snowflake



@dataclass
class Credentials:
    email: str
    password: str
    token: str = None

class User:
    def __init__(self, app, user_id, email, password, token=None):
        self.app = app
        self.id = user_id
        self.name = None
        self.credentials = Credentials(email, password, token)

    @classmethod
    def from_data(cls, app, data):
        user_id = data['user_id']
        credentials = data['credentials']
        email, password, token = credentials.values()
        user = cls(app, user_id, email, password, token)
        return user

    @classmethod
    async def register(cls, request):

        app = request.app
        data = request.json

        email = data.get('email')
        password = data.get('password')

        query = {'credentials.email': email}
        exists = await cls.find_account(app, **query)
        if exists: abort(403, 'Email already in use.') 

        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password, salt)

        document = {
            "user_id": snowflake(),
            "credentials": {
                "email": email,
                "password": hashed,
                "token": None
            }
        }

        user = cls.from_data(app, document)

        await app.db.users.insert_one(document)

        return user

    @classmethod
    async def find_account(cls, app, **query):
        '''Returns a user object based on the query'''
        data = await app.db.users.find_one(query)

        if not data:
            return None
        
        user = cls.from_data(app, data)

        return user

    async def issue_token(self):
        '''Creates and returns a token if not already existing'''
        if self.credentials.token:
            return self.credentials.token

        payload = {
            'sub': self.id,
            'iat': datetime.datetime.utcnow()
        }

        self.credentials.token = token = jwt.encode(payload, self.app.secret)

        await self.app.db.users.update_one(
            {'user_id': self.id}, 
            {'$set': {'credentials.token': token}}
        )

        return token

    def check_password(self, password):
        return bcrypt.checkpw(password, self.credentials.password)

class Overpass:
    BASE = 'http://overpass-api.de/api/interpreter?data=[out:json];'
    NODE = BASE + 'node({});out;'
    WAY = BASE + 'way({});out;'

class Color:
    green = 0x2ecc71
    red = 0xe74c3c
    orange = 0xe67e22