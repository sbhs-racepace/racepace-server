import asyncio
import subprocess
import traceback
import os

import dotenv
import aiohttp
import bcrypt

from sanic import Sanic
from sanic.exceptions import NotFound, InvalidUsage, abort
from sanic.response import json
from sanic.log import logger

from motor.motor_asyncio import AsyncIOMotorClient

from core.route import Route
from core.enum import Overpass, Color
from core.decorators import json_required, memoized
from core.utils import run_with_ngrok, Snowflake
from core.discord import Embed, Webhook

dotenv.load_dotenv()
dev_mode = bool(int(os.getenv('development'))) # decides wether to deploy on server or run locally

status_icon = 'http://icons-for-free.com/free-icons/png/250/353838.png'

app = Sanic('majorproject')

if dev_mode:
    run_with_ngrok(app)

routes = {}

async def fetch(url):
    """Makes a http get request"""
    async with app.session.get(url) as response:
        return await response.json()

@app.listener('before_server_start')
async def init(app, loop):
    app.snowflake = Snowflake()
    app.session = aiohttp.ClientSession(loop=loop) # we use this to make web requests
    app.webhook = Webhook(os.getenv('webhook_url'), session=app.session, is_async=True)
    app.db = AsyncIOMotorClient(os.getenv('mongo_uri')).majorproject

    em = Embed(color=Color.green)
    em.set_author('[INFO] Starting Worker', url=app.ngrok_url)
    em.add_field('Public URL', app.ngrok_url)

    await app.webhook.send(embeds=em)

@app.listener('after_server_stop')
async def aexit(app, loop):
    em = Embed(color=Color.orange)
    em.set_author('[INFO] Server Stopped')

    await app.webhook.send(embeds=em)
    await app.session.close()

@app.exception(Exception)
async def on_error(request, exception):
    
    data = {
        'success': False,
        'error': str(exception)
    }

    if not isinstance(exception, (NotFound, InvalidUsage)):
        try:
            raise(exception)
        except:
            excstr = traceback.format_exc()
            print(excstr)
        
        em = Embed(color=Color.red)
        em.set_author('[ERROR] Exception occured on server')
        em.description = f'```py\n{excstr}```'
        app.add_task(app.webhook.send('<@&511869566394040322>', embeds=em)) # ping developers when an error occurs
            
    return json(data)

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

    if await account_exists(username):
        abort(403, 'email is already in use')

    document = {
        "user_id": app.snowflake.generate_id(),
        "email": email,
        "password": hashed,
        "salt": salt
    }

    await app.db.insert_one(document)
    return json({'success': True})

@app.get('/api/login')
@json_required
async def login(request):
    pass

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
