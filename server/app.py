import asyncio
import traceback
import os

import dotenv
import aiohttp

from sanic import Sanic
from sanic.exceptions import SanicException
from sanic.response import json

from core.route import Route
from core.endpoints import Overpass 
from core.utils import timed, cached

dotenv.load_dotenv()
dev_mode = bool(int(os.getenv('development'))) # decides wether to deploy on server or run locally

app = Sanic('majorproject')
routes = {}

async def fetch(url):
    """Makes a http get request"""
    async with app.session.get(url) as response:
        return await response.json()

@app.listener('before_server_start')
async def init(app, loop):
    app.session = aiohttp.ClientSession(loop=loop) # we use this to make web requests

@app.listener('after_server_stop')
async def aexit(app, loop):
    await app.session.close()

@app.exception(Exception)
async def on_error(request, exception):
    
    data = {
        'success': False,
        'error': str(exception)
    }

    try:
        raise(exception)
    except:
        traceback.print_exc()
            
    return json(data)

@app.get('/')
async def index(request):

    data = {
        'message': 'Welcome to the RacePace API',
        'success': True,
        'endpoints' : ['/api/route']
        }

    return json(data)


@app.get('/api/route')
@timed
@memoized
async def route(request):
    '''Api endpoint to generate the route'''

    data = request.json # get paramaters from requester (location, preferences etc.)
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
