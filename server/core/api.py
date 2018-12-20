from sanic import Blueprint, response
from sanic.log import logger

from core.route import Route
from core.models import Overpass, Color, User
from core.decorators import jsonrequired, memoized, authrequired

api = Blueprint('api', url_prefix='/api')

@api.get('/route')
@memoized
@authrequired
async def route(request):
    '''Api endpoint to generate the route'''

    data = request.json

    preferences = data.get('preferences')
    bounding_box = data.get('bounding_box') #Coords seperated by spaces
    start = data.get('start') #Lat + Lon seperated by comma
    end = data.get('end')

    url = Overpass.REQ.format(bounding_box) #Generate url to query api
    map_data = await request.app.fetch(url)

    nodes, ways = {}, {}

    for element in map_data['elements']:
        id = element['id']
        if element['type'] == "node":
            nodes[id] = Node.from_json(element)
        else:
            ways[id] = Way.from_json(element)
            
    route = Route.generate_route(nodes, ways, start, end)
    return response.json(route.json)

@api.post('/api/users/update')
@authrequired
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