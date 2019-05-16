import asyncio
import functools
import bson
import dateutil.parser

from io import BytesIO

from sanic import Blueprint, response
from sanic.exceptions import abort
from sanic.log import logger

from core.route import Route, Point, Node, Way
from core.models import Overpass, Color, User, RealTimeRoute, RunningSession, SavedRoute, RecentRoute
from core.decorators import jsonrequired, memoized, authrequired



api = Blueprint('api', url_prefix='/api')

locationCache = {}

@api.get('/route/multiple')
@memoized
async def multiple_route(request):
    """
    Api Endpoint that returns a multiple waypoint route
    Jason Yu/Abdur Raqueeb/Sunny Yan
    """
    data = request.args
    # Generate Locations and Bounding Box
    location_points = [Point.from_string(waypoint) for waypoint in data['waypoints']]
    min_euclidean_distance = Route.get_route_distance(location_points)
    # Check Valid Distance
    if min_euclidean_distance > 50000: #50km
        return response.json({'success': False, 'error_message': "Route too long."})
    bounding_box = Route.bounding_points_to_string(Route.convex_hull(location_points))
    endpoint = Overpass.REQ.format(bounding_box) #Generate url to query api
    # Fetch Node Data and Way Data
    task = request.app.fetch(endpoint)
    print('Fetching map data')
    data = await asyncio.gather(task) #Data is array with response as first element
    elements = data[0]['elements'] #Nodes and Ways are together in array in json
    print('Successfuly got map data')
    node_data, way_data = [], []
    for element in elements:
        if element["type"] == "node": node_data.append(element)
        elif element["type"] == "way": way_data.append(element)
        else: raise Exception("Unidentified element type")
    # Generate Route
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
    # Generate Bounding Box
    start = Point.from_string(data.get('start'))
    end = Point.from_string(data.get('end'))
    # Check Valid Distance
    min_euclidean_distance = start - end
    if min_euclidean_distance > 50000: #50km
        return response.json({'success': False, 'error_message': "Route too long."})
    bounding_box = Route.bounding_points_to_string(Route.two_point_bounding_box(start, end))
    endpoint = Overpass.REQ.format(bounding_box) #Generate url to query api
    # Fetch Node Data and Way Data
    task = request.app.fetch(endpoint)
    print('Fetching map data')
    data = await asyncio.gather(task) #Data is array with response as first element
    elements = data[0]['elements'] #Nodes and Ways are together in array in json
    print('Successfuly got map data')
    node_data, way_data = [], []
    for element in elements:
        if element["type"] == "node": node_data.append(element)
        elif element["type"] == "way": way_data.append(element)
        else: raise Exception("Unidentified element type")
    #Generate Route
    nodes, ways = Route.transform_json_nodes_and_ways(node_data,way_data)
    start_node = start.closest_node(nodes)
    end_node = end.closest_node(nodes)
    print("Generating route")
    partial = functools.partial(Route.generate_route, nodes, ways, start_node.id, end_node.id)
    route = await request.app.loop.run_in_executor(None, partial)
    print("Route successfully generated")
    return response.json(route.json)


@api.patch('/users/<user_id:int>')
@authrequired
async def update_user(request, user, user_id):
    """
    Change user information
    Abdur Raqueeb
    """
    data = request.json
    password = data.get('password')
    if password:
        salt = bcrypt.gensalt()
        user.credentials.password = bcrypt.hashpw(password, salt)
        await user.update()
    
    return response.json({'success': True})

@api.delete('/users/<user_id:int>')
@authrequired
async def delete_user(request, user, user_id):
    """
    Deletes user from database
    Abdur Raqueeb
    """
    await user.delete()
    return response.json({'success': True})

@api.post('/register')
@jsonrequired
async def register(request):
    """
    Register a user into the database, then logs in
    Abdur Raqueeb/Sunny Yan
    """
    user = await request.app.users.register(request)
    token = await request.app.users.issue_token(user)
    return response.json({
        'success': True,
	    'token': token.decode("utf-8"),
	    'user_id': user.id}
    )

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
    user = await request.app.users.find_account(**query)
    if user is None:
        abort(403, 'Credentials invalid.')
    elif user.check_password(password) == False:
        abort(403, 'Credentials invalid.')
    token = await request.app.users.issue_token(user)
    resp = {
        'success': True,
        'token': token.decode("utf-8"),
        'user_id': user.id
    }
    return response.json(resp)


@api.post('/get_info')
@jsonrequired
async def get_info(request):
    """
    Get user info
    Jason Yu/Sunny Yan
    """
    data = request.json
    user_id = data.get('user_id')
    query = {'_id': user_id}
    account = await request.app.users.find_account(**query)
    info = account.to_dict()
    if account is None:
        abort(403, 'User ID invalid.')
    resp = {
        'success': True,
        'info' : {
            'full_name': info['full_name'],
            'username': info['username'],
            'points': info['stats']['points'],
            'followers': info['followers'],
            'following': info['following'],
            'stats': info['stats']
        }
    }
    return response.json(resp)

@api.post('/send_real_time_location')
@jsonrequired
@authrequired
async def update_runner_location(request, user):
    """
    Sends current location of user
    Jason Yu
    """
    data = request.json
    location = data.get('location')
    time = data.get('time')
	# Update User Location
    user.updateOne({'$push': {'real_time_route.location_history': {"location": location, "time": time}}})
    locationCache[user] = (location,time)
    resp = {
        'success': True,
	}
    return response.json(resp)

@api.post('/get_locations')
async def get_locations(request):
	group_id = request.json.group_id
	group = await request.app.group.from_db(group_id,request.app)
	
	groupLocations = {}
	for user, locationPacket in locationCache.items():
		if user.id in group.members:
			groupLocations[user.full_name] = locationPacket
	
	return response.json(groupLocations)

@api.post('/save_route')
@jsonrequired
@authrequired
async def save_route(request, user):
    """
    Sends current Route of user
    Jason Yu
    """
    data = request.json
    name = data.get('name')
    start_time = data.get('start_time')
    duration = data.get('duration')
    points = data.get('points')
    description = data.get('description')
    route = Route.from_data(**data.get('route'))
    # Saving Route Image
    route_image = route.generateStaticMap()
    await request.app.db.images.insert_one({
        'user_id': user.id,
        'route_name': name,
        'route_image': route_image
    })
    saved_route = SavedRoute(name, route, start_time, duration, None, route_image, points, description)
    # Adding Saved Route to DB
    user.saved_routes[name] = saved_route.to_dict()
    user.update()
    resp = {
        'success': True,
    }
    return response.json(resp)

@api.post('/save_recent_route')
@authrequired
@jsonrequired
async def save_recent_route(request, user):
    """
    Sends current location of user
    Jason Yu
    """
    data = request.json
    start_time = data.get('start_time')
    duration = data.get('duration')
    route = Route.from_data(**data.get('route'))
    recent_route = RecentRoute(route, start_time, duration)
    curr_num_recent_routes = len(user.recent_routes)
    #Makes sure that only the most recent routes are saved
    max_recent_routes = 10
    if (curr_num_recent_routes < max_recent_routes):
        user.recent_routes.append(recent_route.to_dict())
    else:
        user.recent_routes = user.recent_routes[curr_num_recent_routes+1-max_recent_routes:]
        user.recent_routes.append(recent_route.to_dict())
    #Updating DB
    user.update()
    resp = {
        'success': True,
    }
    return response.json(resp)

@api.post('/get_saved_routes')
@authrequired
@jsonrequired
async def get_saved_routes(request, user):
    """
    Gets saved routes of user
    Jason Yu
    """
    data = request.json
    saved_routes_json = [saved_route.to_dict() for saved_route in user.saved_routes]
    resp = {
        'success': True,
        'saved_routes_json': saved_routes_json,
    }
    return response.json(resp)

@api.post('/get_recent_routes')
@authrequired
@jsonrequired
async def get_recent_routes(request, user):
    """
    Gets recent routes of user
    Jason Yu
    """
    data = request.json
    recent_routes = [recent_route.to_dict() for recent_route in user.recent_routes]
    resp = {
        'success': True,
        'recent_routes': recent_routes,
    }
    return response.json(resp)

@api.post('/groups/create')
@authrequired
@jsonrequired
async def create_group(request, user):
    info = request.json
    await user.create_group(info)
    return response.json({'success': True})

@api.patch('/groups/<group_id>/edit')
@authrequired
@jsonrequired
async def edit_group(request, user, group_id):
    pass

@api.delete('/groups/<group_id>/delete')
@authrequired
async def delete_group(request, user, group_id):
    pass

@api.get('/groups/<group_id>/messages')
@authrequired
async def get_previous_messages(request, user, group_id):
    if not group_id == 'global':
        abort(404) # groups not implemented yet
    
    before = dateutil.parser.parse(request.args.get('before'))
    limit = 50

    query = {
        'group_id': group_id, 
        'created_at': {
            '$lte': before
            }
        }

    cursor = request.app.db.messages.find(query).sort('created_at', -1)
    cursor.limit(limit)

    messages = []

    async for msg in cursor:
        msg['created_at'] = msg['created_at'].timestamp()
        messages.append(msg)

    return response.json(messages)

@api.get('/route_images/<user_id>/<route_name>')
async def get_route_image(request,user_id,route_name):
    doc = await request.app.db.images.find_one({'user_id': user_id, 'route_name':route_name})
    if not doc:
        abort(404)
    return response.raw(doc['route_image'], content_type='image/png')

@api.get('/avatars/<user_id>.png')
async def get_user_image(request,user_id):
    doc = await request.app.db.images.find_one({'user_id': user_id})
    if not doc:
        abort(404)
    return response.raw(doc['avatar'], content_type='image/png')

@api.patch('/avatars/update')
@authrequired
async def update_user_image(request, user):
    avatar = request.body 
    await request.app.db.images.update_one({'user_id': user.id}, {'$set': {'avatar': avatar}})
    return response.json({'success': True})

@api.post('/find_friends')
@authrequired
@jsonrequired
async def find_friends(request,user):
    name = request.json.name
    results = request.app.db.users.find({"full_name":{"$regex":name}})
    results = [{"user_id":user.id,"name":user.name,"bio":user.bio} for user in results]
    return response.json(results)
        
    









