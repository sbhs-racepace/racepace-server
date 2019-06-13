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
from core.route_generation import Route
from core.route import RealTimeRoute
from core.misc import Overpass, Color
from core.user import User, UserBase
from core.group import Message
from core.decorators import jsonrequired, memoized, authrequired, validate_token
from core.utils import run_with_ngrok
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
        'endpoints' : 
            [
                '/api/route',
                '/api/users',
                '/api/avatars',
                '/route_images',
                '/groups',
            ]
        }

    return response.json(data)

@sio.on('connect')
async def on_connect(sid, environ):

    qs = environ['QUERY_STRING']
    token = parse_qs(qs)['token'][0]
    user_id = jwt.decode(token, app.secret)['sub']
    user = await app.users.find_account(_id=user_id)

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
        real_time_route = RealTimeRoute.setup_run(start_time, route)
        await user.set_field('real_time_route', real_time_route.to_dict())

@sio.on('end_run')
async def on_end_run(sid):
    user = (await sio.get_session(sid))['user']
    await user.set_to_dict_field('real_time_route','active', False)

@sio.on('location_update')
async def on_location_update(sid, data):
    user = (await sio.get_session(sid))['user']
    location = data.get('location')
    latitude = location['latitude']
    longitude = location['longitude']
    time = data.get('time', None)
    user.real_time_route.update_location_history(latitude, longitude, time)
    await user.set_field('real_time_route', user.real_time_route.to_dict())

@sio.on('disconnect')
async def on_disconnect(sid):
    print('Disconnected user', sid)

if __name__ == '__main__':
    if os.getenv('dev'):
        app.run(debug=True)
    else: 
        app.run(host=os.getenv('HOST', '0.0.0.0'), port=os.getenv('PORT', 80))
