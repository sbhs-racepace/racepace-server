import asyncio
import functools

from sanic import Blueprint, response
from sanic.exceptions import abort
from sanic.log import logger

from core.route import Route, Point, Node, Way
from core.models import Overpass, Color, User
from core.decorators import jsonrequired, memoized, authrequired

api = Blueprint('api', url_prefix='/api')

cache = {}

@api.post('/route')
@memoized
@authrequired
async def route(request):
    '''Api endpoint to generate the route'''

    data = request.json

    start = Point.from_string(data.get('start'))
    end = Point.from_string(data.get('end'))

    bounding_box = Route.two_point_bounding_box(start, end)

    nodes_enpoint = Overpass.NODE.format(bounding_box) #Generate url to query api
    ways_endpoint = Overpass.WAY.format(bounding_box)

    print(nodes_enpoint)
    print(ways_endpoint)

    tasks = [
        request.app.fetch(nodes_enpoint),
        request.app.fetch(ways_endpoint)
        ]

    nodedata, waydata = await asyncio.gather(*tasks)

    nodes, ways = Route.transform_json_nodes_and_ways(node_data,way_data)

    start_node = start.closest_node(nodes)
    end_node = end.closest_node(nodes)

    partial = functools.partial(Route.generate_route, nodes, ways, start_node.id, end_node.id)

    route = await request.app.loop.run_in_executor(None, partial)

    return response.json(route.json)

@api.patch('/users/<user_id:int>')
@authrequired
async def update_user(request, user_id):
    """Change user stuff"""
    data = request.json
    token = request.token

    password = data.get('password')

    user_id = jwt.decode(token, request.app.secret)['sub']

    user = await request.app.users.find_account(user_id=user_id)

    salt = bcrypt.gensalt()

    user.credentials.password = bcrypt.hashpw(password, salt)

    await user.update()

    return response.json({'success': True})

@api.delete('/users/<user_id:int>')
@authrequired
async def delete_user(request, user_id):
    user = await request.app.users.find_account(user_id=user_id)
    await user.delete()
    return response.json({'success': True})

@api.post('/register')
@jsonrequired
async def register(request):
    """Register a user into the database"""

    user = await request.app.users.register(request)

    return response.json({'success': True})

@api.post('/login')
@jsonrequired
async def login(request):
    data = request.json

    email = data.get('email')
    password = data.get('password')

    query = {'credentials.email': email}

    account = await request.app.users.find_account(**query)

    if account is None or not account.check_password(password):
        abort(403, 'Credentials invalid.')

    token = await request.app.users.issue_token(account)

    resp = {
        'success': True,
        'token': token.decode("utf-8"),
        'user_id': account.id
    }

    return response.json(resp)
