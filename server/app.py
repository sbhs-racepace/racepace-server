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

from sanic import Sanic, response
from sanic.exceptions import SanicException, ServerError, abort
from sanic.log import logger
from dhooks import Webhook, Embed

from motor.motor_asyncio import AsyncIOMotorClient

from core.api import api
from core.route import Route
from core.models import Overpass, Color, User, UserBase
from core.decorators import jsonrequired, memoized, authrequired
from core.utils import run_with_ngrok, snowflake
from core import config

app = Sanic('majorproject')
app.blueprint(api)

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

    await app.webhook.send(embed=em)

@app.listener('after_server_stop')
async def aexit(app, loop):
    em = Embed(color=Color.orange)
    em.set_footer(f'Host: {socket.gethostname()}')
    em.set_author('[INFO] Server Stopped')

    await app.webhook.send(embed=em)
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
    app.add_task(app.webhook.send(embed=em))

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
    app.run(debug=True) if config.DEV_MODE else app.run(host=config.HOST, port=80)
