import asyncio
import functools
import bson

from sanic import Blueprint, response
from sanic.exceptions import abort
from sanic.log import logger

from core.route import Route, Point, Node, Way
from core.models import Overpass, Color, User
from core.decorators import jsonrequired, memoized, authrequired

api = Blueprint('api', url_prefix='/api')

cache = {}

@api.get('/route/multiple')
@memoized
async def multiple_route(request):
    """
    Api Endpoint that returns a multiple waypoint route
    Jason Yu/Abdur Raqueeb/Sunny Yan
    """
    data = request.args

    location_points = [Point.from_string(waypoint) for waypoint in data['waypoints']]

    min_euclidean_distance = Route.get_route_distance(location_points)
    if min_euclidean_distance > 50000: #50km
        return response.json({'success': False, 'error_message': "Route too long."})

    bounding_box = Route.bounding_points_to_string(Route.convex_hull(location_points))

    endpoint = Overpass.REQ.format(bounding_box) #Generate url to query api
    task = request.app.fetch(endpoint)

    print('Fetching map data')
    data = await asyncio.gather(task) #Data is array with response as first element
    elements = data[0]['elements'] #Nodes and Ways are together in array in json
    print('Successfuly got map data')

    #Seperate response into nodes and ways
    node_data, way_data = [], []
    for element in elements:
        if element["type"] == "node": node_data.append(element)
        elif element["type"] == "way": way_data.append(element)
        else: raise Exception("Unidentified element type")

    nodes, ways = Route.transform_json_nodes_and_ways(node_data,way_data)
    waypoint_nodes = [point.closest_node(nodes) for point in location_points]
    waypoint_ids = [node.id for node in waypoint_nodes]

    print("Generating route")
    partial = functools.partial(Route.generate_multi_route, nodes, ways, waypoint_ids)
    route = await request.app.loop.run_in_executor(None, partial)
    print("Route successfully generated")

    return response.json(route.json)

# @authrequired
@api.get('/route')
@memoized
async def route(request):
    """
    Api Endpoint that returns a route
    Jason Yu/Abdur Raqueeb/Sunny Yan
    """
    data = request.args
    
    start = Point.from_string(data.get('start'))
    end = Point.from_string(data.get('end'))

    min_euclidean_distance = start - end
    if min_euclidean_distance > 50000: #50km
        return response.json({'success': False, 'error_message': "Route too long."})

    bounding_box = Route.bounding_points_to_string(Route.two_point_bounding_box(start, end))

    endpoint = Overpass.REQ.format(bounding_box) #Generate url to query api
    task = request.app.fetch(endpoint)

    print('Fetching map data')
    data = await asyncio.gather(task) #Data is array with response as first element
    print(data)
    elements = data[0]['elements'] #Nodes and Ways are together in array in json
    print('Successfuly got map data')

    #Seperate response into nodes and ways
    node_data, way_data = [], []
    for element in elements:
        if element["type"] == "node": node_data.append(element)
        elif element["type"] == "way": way_data.append(element)
        else: raise Exception("Unidentified element type")

    nodes, ways = Route.transform_json_nodes_and_ways(node_data,way_data)
    start_node = start.closest_node(nodes)
    end_node = end.closest_node(nodes)
    
    print("Generating route")
    partial = functools.partial(Route.generate_route, nodes, ways, start_node.id, end_node.id)
    route = await request.app.loop.run_in_executor(None, partial)
    print("Route successfully generated")

    return response.json(route.json)

@authrequired
@api.patch('/users/<user_id:int>')
async def update_user(request, user_id):
    """
    Change user information
    Abdur Raqueeb
    """
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
    """
    Deletes user from database
    Abdur Raqueeb
    """
    user = await request.app.users.find_account(user_id=user_id)
    await user.delete()
    return response.json({'success': True})

@api.post('/register')
@jsonrequired
async def register(request):
    """
    Register a user into the database
    Abdur Raqueeb
    """
    user = await request.app.users.register(request)
    return response.json({'success': True})

@api.post('/login')
@jsonrequired
async def login(request):
    """
    Logs in user into the database
    Abdur Raqueeb
    """
    data = request.json
    email = data.get('email')
    password = data.get('password')
    query = {'credentials.email': email}
    account = await request.app.users.find_account(**query)
    if account is None:
        abort(403, 'Credentials invalid.')
    elif account.check_password(password) == False:
        abort(403, 'Credentials invalid.')
    token = await request.app.users.issue_token(account)
    resp = {
        'success': True,
        'token': token.decode("utf-8"),
        'user_id': account.id
    }
    return response.json(resp)


@api.post('/get_info')
@jsonrequired
async def getinfo(request):
    """
    Get user info
    Jason Yu/Sunny Yan
    """
    data = request.json
    user_id = data.get('user_id')
    print('User id', user_id)
    query = {'_id': bson.objectid.ObjectId(user_id)}
    account = await request.app.users.find_account(**query)
    info = account.to_dict()

    if account is None:
        abort(403, 'User ID invalid.')
    resp = {
        'success': True,
        'info' : {
            'full_name': info.full_name,
            'routes': info.routes,
        }
    }
    return response.json(resp)

