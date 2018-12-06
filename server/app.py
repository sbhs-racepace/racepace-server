import asyncio
import subprocess
import socket
import datetime
import traceback
import os
import sys

import aiohttp
import bcrypt
import jwt
import xml.etree.ElementTree as ET

from sanic import Sanic
from sanic.exceptions import SanicException, ServerError, abort
from sanic.response import json
from sanic.log import logger

from motor.motor_asyncio import AsyncIOMotorClient

from core.route import Route, Point
from core.models import Overpass, Color, User
from core.decorators import jsonrequired, memoized, authrequired
from core.utils import run_with_ngrok, snowflake
from core.discord import Embed, Webhook

dev_mode = bool(int(os.getenv('development'))) # decides wether to deploy on server or run locally

status_icon = 'http://icons-for-free.com/free-icons/png/250/353838.png'

app = Sanic('majorproject')
import_codes = {}

if len(sys.argv) > 1 and sys.argv[1] == '-ngrok':
    run_with_ngrok(app)
else:
    app.ngrok_url = None

async def fetch(url):
    """Makes a http get request"""
    async with app.session.get(url) as response:
        return await response.json()

@app.listener('before_server_start')
async def init(app, loop):
    app.secret = os.getenv('secret')
    app.session = aiohttp.ClientSession(loop=loop) # we use this to make web requests
    app.webhook = Webhook(os.getenv('webhook_url'), session=app.session, is_async=True)
    app.db = AsyncIOMotorClient(os.getenv('mongo_uri')).majorproject

    em = Embed(color=Color.green)
    em.set_author('[INFO] Starting Worker', url=app.ngrok_url)
    em.set_footer(f'Host: {socket.gethostname()}')
    em.add_field('Public URL', app.ngrok_url) if app.ngrok_url else ...

    await app.webhook.send(embeds=em)

@app.listener('after_server_stop')
async def aexit(app, loop):
    em = Embed(color=Color.orange)
    em.set_footer(f'Host: {socket.gethostname()}')
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
        em.set_footer(f'Host: {socket.gethostname()}')
        app.add_task(app.webhook.send(embeds=em))

    return json(response, status=500)

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

    return json(data)

@app.post('/api/users/update')
@authrequired
async def update_user(request):
    """Change password"""
    data = request.json
    token = request.token

    userID = jwt.decode(token, app.secret)['sub']
    query = {"user_id":userID}
    user = await User.find_account(app, **query)
    password = data.get('password')
    salt = bcrypt.gensalt()
    user.credentials.password = bcrypt.hashpw(password, salt)
    await user.update_user(app.db)

    return json({'success': True})

@app.post('/api/register')
@jsonrequired
async def register(request):
    """Register a user into the database"""

    user = await User.register(request)

    return json({'success': True})

@app.post('/api/login')
@jsonrequired
async def login(request):
    data = request.json

    email = data.get('email')
    password = data.get('password')

    query = {'credentials.email': email}

    account = await User.find_account(app, **query)

    if account is None or not account.check_password(password):
        abort(403, 'Credentials invalid.')

    token = await account.issue_token()

    response = {
        'success': True,
        'token': token.decode("utf-8")
    }

    return json(response)

@app.post('/api/route')
@memoized
@authrequired
async def route(request):
    '''Api endpoint to generate the route'''

    data = request.json

    preferences = data.get('preferences')
    bounding_box = data.get('bounding_box') #Coords seperated by spaces
    start = data.get('start') #Lat + Lon seperated by comma
    end = data.get('end')

    url = Overpass.ALL.format(bounding_box) #Generate url to query api
    map_data = await fetch(url)

    #Find where the node data ends and way data starts
    for i,element in enumerate(map_data['elements']):
        if element['type']=="way":
            break

    nodes = {n['id']: Node.from_json(n) for n in map_data['elements'][:i]}
    ways = {w['id']: Way.from_json(w) for w in map_data['elements'][i:]}

    route = Route.generate_route(nodes, ways, start, end)
    return json(route.json)

@app.post('api/importGPX')
async def importGPX(request):
    data = request.json
    if data.get('usercode') in import_codes:
        userID = import_codes[data.get('usercode')]
    elif request.token:
        userID = jwt.decode(request.token, app.secret)['sub']
    else:
        abort(401, "No token or usercode supplied")
    
    #Read GPX file and convert coords to floats
    file = request.files.get('gpx')
    root = ET.fromstring(file.body)
    trk = root.getchildren()[1].getchildren()[1]
    trk = [(float(pt.get('lat')),float(pt.get('lon')))
           for pt in trk]

    #Work out the bounding box and download the node data for that area
    bound1 = " ".join(max(trk, key=lambda pt: pt[0]))
    bound2 = " ".join(min(trk, key=lambda pt: pt[0]))
    bound3 = " ".join(max(trk, key=lambda pt: pt[1]))
    bound4 = " ".join(min(trk, key=lambda pt: pt[1]))
    bounding_box = " ".join((bound1,bound2,bound3,bound4))
    url = Overpass.NODES.format(bounding_box)
    nodes = await fetch(url)

    #Create a route object
    route = Route.from_GPX(nodes, trk)
    route.save_route(app.db, userID)

if __name__ == '__main__':
    app.run() if dev_mode else app.run(host=os.getenv('host'), port=80)
