import asyncio
import functools

from sanic import Blueprint, response
from sanic.log import logger

from core.route import Route, Point, Node, Way
from core.models import Overpass, Color, User
from core.decorators import jsonrequired, memoized, authrequired

api = Blueprint('api', url_prefix='/api')

cache = {}

@api.get('/route')
@memoized
async def route(request):
    '''Api endpoint to generate the route'''

    data = request.json

    start = Point.from_string(data.get('start'))
    end = Point.from_string(data.get('end'))

    midpoint = start.get_midpoint(end)
    length = width = (start - end) * 1.5
    bounding_box = Route.square_bounding(midpoint, length, width)

    nodes_enpoint = Overpass.NODE.format(bounding_box) #Generate url to query api
    ways_endpoint = Overpass.WAY.format(bounding_box)

    tasks = [
        request.app.fetch(nodes_enpoint),
        request.app.fetch(ways_endpoint)
        ]

    nodedata, waydata = await asyncio.gather(*tasks)

    nodes = {n['id']: Node.from_json(n) for n in nodedata['elements']}
    ways = {w['id']: Way.from_json(w) for w in waydata['elements']}

    start_node = start.closest_node(nodes)
    end_node = end.closest_node(nodes)

    partial = functools.partial(Route.generate_route, nodes, ways, start_node.id, end_node.id)

    route = await request.app.loop.run_in_executor(None, partial)
    
    return response.json(route.json)

@api.post('/api/users/update')
# @authrequired
async def update_user(request):
    """Change password"""
    data = request.json
    token = request.token

    password = data.get('password')

    user_id = jwt.decode(token, app.secret)['sub']

    user = await request.app.users.find_account(user_id=user_id)

    salt = bcrypt.gensalt()

    user.credentials.password = bcrypt.hashpw(password, salt)
 
    await user.update()

    return response.json({'success': True})

@api.post('/api/register')
@jsonrequired
async def register(request):
    """Register a user into the database"""

    user = await app.users.register(request)

    return response.json({'success': True})

@api.post('/api/login')
@jsonrequired
async def login(request):
    data = request.json

    email = data.get('email')
    password = data.get('password')

    query = {'credentials.email': email}

    account = await app.users.find_account(**query)

    if account is None or not account.check_password(password):
        abort(403, 'Credentials invalid.')

    token = await app.users.issue_token(account)

    response = {
        'success': True,
        'token': token.decode("utf-8")
    }

    return response.json(response)