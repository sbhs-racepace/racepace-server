import asyncio
import os

import aiohttp
from sanic import Sanic
import ujson

from utils.response import json
from utils.logic import generate_route

dev_mode = bool(os.getenv('development')) # decides wether to deploy on server or run locally

with open('data/config.json') as f:
    config = ujson.loads(f.read())

app = Sanic('majorproject')

@app.get('/')
async def index(request):


    data = {
        'message': 'Hello World!',
        'success': True
        }

    return json(data)

@app.get('/api/route')
async def route(request):
    '''Api endpoint to generate the route'''

    data = request.json # get paramaters from requester (location, prefrences etc.)
    nodes = [] # make a request to the api to get nodes around location.
    route = generate_route(nodes, data)
    return json(route)

if __name__ == '__main__':
    app.run() if dev_mode else app.run(host=config.get("host"), port=80)