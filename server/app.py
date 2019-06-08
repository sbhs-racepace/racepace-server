import asyncio
import subprocess
import socket
import datetime
import traceback
import os
import sys
from urllib.parse import parse_qs
from datetime import datetime

import socketio
import aiohttp
import bcrypt
import jwt
import xml.etree.ElementTree as ET

from sanic import Sanic, response
from sanic.exceptions import SanicException, ServerError, abort
from sanic.log import logger
from dhooks import Webhook, Embed

from motor.motor_asyncio import AsyncIOMotorClient

from core.api import api
from core.route_generation import Route
from core.route import RealTimeRoute
from core.misc import Overpass, Color
from core.user import User, UserBase
from core.decorators import jsonrequired, memoized, authrequired, validate_token
from core.utils import run_with_ngrok, snowflake, parse_snowflake
from core import config

sio = socketio.AsyncServer(async_mode='sanic')
app = Sanic('majorproject')
app.blueprint(api)
sio.attach(app)

if len(sys.argv) > 1 and sys.argv[1] == '-ngrok':
    run_with_ngrok(app)
else:
    app.ngrok_url = None

async def fetch(url):
    """Makes a http get request"""
    async with app.session.get(url) as response:
        return await response.json()

app.fetch = fetch

@app.listener('before_server_start')
async def init(app, loop):
    app.secret = config.SECRET
    app.session = aiohttp.ClientSession(loop=loop) # we use this to make web requests
    app.webhook = Webhook.Async(config.WEBHOOK_URL, session=app.session)
    app.db = AsyncIOMotorClient(config.MONGO_URI).majorproject
    app.users = UserBase(app)

    em = Embed(color=Color.green)
    em.set_author('[INFO] Starting Worker', url=app.ngrok_url)
    em.set_footer(f'Host: {socket.gethostname()}')
    em.add_field('Public URL', app.ngrok_url) if app.ngrok_url else ...

    # await app.webhook.send(embed=em)

@app.listener('after_server_stop')
async def aexit(app, loop):
    em = Embed(color=Color.orange)
    em.set_footer(f'Host: {socket.gethostname()}')
    em.set_author('[INFO] Server Stopped')

    # await app.webhook.send(embed=em)
    await app.session.close()

@app.exception(SanicException)
async def sanic_exception(request, exception):

    resp = {
        'success': False,
        'error': str(exception)
    }

    print(exception)
    # try:
    #     raise(exception)
    # except:
    #     print(exception)

    return response.json(resp, status=exception.status_code)

@app.exception(Exception)
async def on_error(request, exception):

    resp = {
        'success': False,
        'error': str(exception)
    }

    try:
        raise(exception)
    except:
        excstr = traceback.format_exc()
        print(excstr)

    if len(excstr) > 1000:
        excstr = excstr[:1000]

    em = Embed(color=Color.red)
    em.set_author('[ERROR] Exception occured on server')
    em.description = f'```py\n{excstr}```'
    em.set_footer(f'Host: {socket.gethostname()}')
    # app.add_task(app.webhook.send(embed=em))

    return response.json(resp, status=500)

@app.get('/')
async def index(request):
    data = {
        'message': 'Welcome to the RacePace API',
        'success': True,
        'endpoints' : [
            '/api/route',
            '/api/users/update',
            '/api/register',
            '/api/login']
        }

    return response.json(data)

class Message:
    def __init__(self, id, author, group_id, content=None, image=None):
        self.id = id
        self.author = author
        self.group_id = group_id
        self.content = content
        self.image = image
    
    @property
    def created_at(self):
        return parse_snowflake(int(self.id))[0]

    def to_dict(self):
        return {
            '_id': self.id,
            'content': self.content,
            'image': self.image,
            'group_id': self.group_id,
            'created_at': self.created_at,
            'author': {
                "_id": self.author.id,
                "full_name": self.author.full_name,
                "username": self.author.username,
                "avatar_url": self.author.avatar_url
                }
        }

    @classmethod
    async def create(cls, app, user, data):
        message_id = snowflake()
        content = data.get('content')
        image = data.get('image')
        msg = cls(message_id, user, data['group_id'], content, image)
        

        data = msg.to_dict()
        data['created_at'] = datetime.utcfromtimestamp(data['created_at'])
        await app.db.messages.insert_one(data)
        return msg

@sio.on('connect')
async def on_connect(sid, environ):

    qs = environ['QUERY_STRING']
    token = parse_qs(qs)['token'][0]
    user_id = jwt.decode(token, app.secret)['sub']
    user = await request.app.users.find_account(_id=user_id)

    if not user:
        print('Unknown user, Connection rejected')
        return False

    for group in user.groups.values():
        sio.enter_room(sid, group.id)
    
    sio.enter_room(sid, 'global')

    await sio.save_session(sid, {'user': user})
    print('Connected', user.username, user_id)

@sio.on('global_message')
async def on_message(sid, data):
    user = (await sio.get_session(sid))['user']
    message = await Message.create(app, user, data)
    await sio.emit('global_message', data=message.to_dict(), room='global', skip_sid=sid)

@sio.on('start_run')
async def on_start_run(sid, data):
    user = (await sio.get_session(sid))['user']
    if user.real_time_route.active == False:
        start_time = data.get('start_time')
        route = data.get('route', None) # If no route is given, none is returned, None value is handled
        class_data = {
            'start_time': start_time,
            'location_history': [],
            'route':route,
            'active':True,
            'current_distance': 0,
            'current_duration': 0,
        }
        user.real_time_route = RealTimeRoute.from_data(class_data)
        await user.replace()

@sio.on('end_run')
async def on_end_run(sid):
    user = (await sio.get_session(sid))['user']
    user.real_time_route.active = False
    await user.replace()

@sio.on('location_update')
async def on_location_update(sid, data):
    user = (await sio.get_session(sid))['user']
    location = data.get('location')
    latitude = location['latitude']
    longitude = location['longitude']
    time = data.get('time', None)
    user.real_time_route.update_location_history(latitude, longitude, time)
    print('Updating User Location', latitude, longitude)
    print('Distance',user.real_time_route.current_distance)
    print(user.real_time_route.location_history) # Checking if location history is updated
    await user.replace()

@sio.on('disconnect')
async def on_disconnect(sid):
    print(sid)

if __name__ == '__main__':
    if os.getenv('dev'):
        app.run(debug=True)
    else: 
        app.run(host=os.getenv('HOST', '0.0.0.0'), port=os.getenv('PORT', 80))
