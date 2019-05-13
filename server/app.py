import asyncio
import subprocess
import socket
import datetime
import traceback
import os
import sys
from urllib.parse import parse_qs

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
from core.route import Route
from core.models import Overpass, Color, User, UserBase
from core.decorators import jsonrequired, memoized, authrequired, validate_token
from core.utils import run_with_ngrok, snowflake
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


@sio.on('connect')
async def on_connect(sid, environ):
    try:
        qs = environ['QUERY_STRING']
        token = parse_qs(qs)['token'][0]
        user_id = jwt.decode(token, app.secret)['sub']
        user = await app.users.find_account(user_id=user_id)

        for group in user.groups:
            sio.enter_room(sid, group.id)

        await sio.save_session(sid, {'user': user})
        print('Connected', user_id)
    except:
        print('Connection refused')
        return False


class Message:
    def __init__(self, id, author, group, content=None, image=None):
        self.id = id
        self.author = author
        self.group = group
        self.content = content
        self.image = image

    def to_dict(self):
        return {
            'content': self.content,
            'image': self.image,
            'group': self.group.id,
            'message_id': self.id,
            'author': {
                "user_id": self.author.id,
                "full_name": self.author.full_name,
                "username": self.author.username,
                "avatar_url": self.author.avatar_url
                }
        }

    @classmethod
    async def create(self, app, user, data):
        message_id = snowflake()
        group = user.groups.get(data['group_id'])
        content = data.get('content')
        image = data.get('image')
        msg = cls(message_id, user, group, content, image)
        await self.app.db.groups.update_one(
            {'group_id': self.group.id},
            {'$push': {'messages': msg.to_dict()}}
            )

@sio.on('message')
async def on_message(sid, data):
    user = (await sio.get_session(sid))['user']
    group = user.groups.get(data['group_id'])

    if not group:
        return

    message = await Message.create(app, user, data)

@sio.on('location_update')
async def on_location_update(sid, data):
    user = (await sio.get_session(sid))
    print(data)

@sio.on('disconnect')
async def on_disconnect(sid):
    print(sid)

if __name__ == '__main__':
    if os.getenv('dev'):
        app.run(debug=True)
    else: 
        app.run(host=os.getenv('HOST', '0.0.0.0'), port=os.getenv('PORT', 80))
