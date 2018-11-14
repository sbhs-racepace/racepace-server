import asyncio
import subprocess
import traceback
import os
import sys

import dotenv
import aiohttp
import bcrypt
import datetime

from sanic import Sanic
from sanic.exceptions import SanicException, ServerError, abort
from sanic.response import json
from sanic.log import logger

from motor.motor_asyncio import AsyncIOMotorClient

from core.route import Route
from core.enum import Overpass, Color
from core.decorators import json_required, memoized
from core.utils import run_with_ngrok, snowflake
from core.discord import Embed, Webhook

dotenv.load_dotenv()
dev_mode = bool(int(os.getenv('development'))) # decides wether to deploy on server or run locally

status_icon = 'http://icons-for-free.com/free-icons/png/250/353838.png'

app = Sanic('majorproject')


if len(sys.argv) > 1 and sys.argv[1] == '-ngrok':
    run_with_ngrok(app)
else:
    app.ngrok_url = None

routes = {}
tokens = {}


async def fetch(url):
    """Makes a http get request"""
    async with app.session.get(url) as response:
        return await response.json()

@app.listener('before_server_start')
async def init(app, loop):
    app.session = aiohttp.ClientSession(loop=loop) # we use this to make web requests
    app.webhook = Webhook(os.getenv('webhook_url'), session=app.session, is_async=True)
    app.db = AsyncIOMotorClient(os.getenv('mongo_uri')).majorproject

    em = Embed(color=Color.green)
    em.set_author('[INFO] Starting Worker', url=app.ngrok_url)
    em.add_field('Public URL', app.ngrok_url) if app.ngrok_url else ...

    await app.webhook.send(embeds=em)

@app.listener('after_server_stop')
async def aexit(app, loop):
    em = Embed(color=Color.orange)
    em.set_author('[INFO] Server Stopped')

    await app.webhook.send(embeds=em)
    await app.session.close()

@app.exception(SanicException)
async def sanic_exception(request, exception):

    response = {
        'success': False,
        'error': str(exception)
    }

    try:
        raise(exception)
    except:
        traceback.print_exc()

    return json(response, status=exception.status_code)

@app.exception(Exception)
async def on_error(request, exception):
    
    response = {
        'success': False,
        'error': str(exception)
    }

    if not isinstance(exception, SanicException):
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
        app.add_task(app.webhook.send(embeds=em))
        
    return json(response, status=500)

@app.get('/')
async def index(request):

    data = {
        'message': 'Welcome to the RacePace API',
        'success': True,
        'endpoints' : [
            '/api/route',
            '/api/register']
        }

    return json(data)

async def account_exists(email):
    return bool(await app.db.users.find_one({'email': email}))

@app.patch('/api/users/<user_id>/update')
async def update_user(request, user_id):
    return NotImplemented

@app.post('/api/register')
@json_required
async def register(request):
    """Register a user into the database"""
    data = request.json

    email = data.get('email')
    password = data.get('password')

    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)

    if await account_exists(email):
        abort(403, 'email is already in use')

    document = {
        "user_id": snowflake(),
        "credentials": {
            "email": email,
            "password": hashed,
            "salt": salt
        }
    }

    await app.db.users.insert_one(document)
    return json({'success': True})

@app.get('/api/login')
@json_required
async def login(request):
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not await account_exists(email):
        abort(403, 'email not found')
    
    userdata = app.db.users.find_one({"credentials": {"email": email}})
    salt = userdata["credentials"]["salt"]
    password_hash = userdata["credentials"]["password"]
    if bcrypt.hashpw(password,salt) == password_hash:
        token = bcrypt.gensalt()
        while token in tokens:
            token = bcrypt.gensalt()
        tokens[token] = str(datetime.datetime.now())
        return json({"success": True,
                     "token":token})
    else:
        abort(403, 'invalid password')

@app.get('/api/route')
@memoized
@json_required
async def route(request):
    '''Api endpoint to generate the route'''

    data = request.json

    preferences = data.get('preferences')
    bounding_box = data.get('bounding_box')
    start = data.get('start') #Lat + Lon seperated by comma
    end = data.get('end')

    response = {
        'success': True,
        'data': None
        }
        
    node_endpoint = Overpass.NODE.format(bounding_box)
    way_endpoint = Overpass.WAY.format(bounding_box)

    tasks = [fetch(node_endpoint), fetch(way_endpoint)]
    nodedata, waydata = await asyncio.gather(*tasks) # concurrently make the two api calls

    nodes = {n['id']: Node.from_json(n) for n in nodedata['elements']}
    ways = {w['id']: Way.from_json(w) for w in waydata['elements']}

    route = Route.generate_route(nodes, ways, start, end)
    return json(route.json)

if __name__ == '__main__':
    app.run() if dev_mode else app.run(host=os.getenv('host'), port=80)
