import asyncio
import os

import aiohttp
from sanic import Sanic
import ujson

from core.response import json
from core.route import Route
from core.endpoints import Overpass 

dev_mode = bool(os.getenv('development')) # decides wether to deploy on server or run locally

with open('data/config.json') as f:
    config = ujson.loads(f.read())

app = Sanic('majorproject')

@app.listener('before_server_start')
async def init(app, loop):
    app.session = aiohttp.ClientSession(loop=loop) # we use this to make web requests

@app.listener('after_server_stop')
async def aexit(app, loop):
    app.session.close()

@app.get('/')
async def index(request):

    data = {
        'message': 'Welcome to the RunBuddy API',
        'success': True,
        'endpoints' : ['/api/route']
        }

    return json(data)

@app.get('/api/route')
async def route(request):
    '''Api endpoint to generate the route'''

    data = request.json # get paramaters from requester (location, preferences etc.)
    preferences = data.get('preferences') 
    location = data.get('location')

    node_endpoint = Overpass.NODE.format(location)
    way_endpoint = Overpass.WAY.format(location)

    async with app.session.get(node_endpoint) as response:
        nodedata = await response.json()
    
    async with app.session.get(way_endpoint) as response:
        waydata = await response.json()

    map = Route(nodedata['elements'], waydata['elements'], preferences)
    route.generate_route()

    return json(route.json)

if __name__ == '__main__':
    app.run() if dev_mode else app.run(host=config.get("host"), port=80)