from sanic import Blueprint, response


stats = Blueprint('stats')

@stats.get('/')
async def index(request):
    return response.html('welcome')


@stats.get('/login')
async def login(request):
    '''Logs in a user using web sessions.'''
    data = request.json
    email = data['email']
    password = data['password']
    
    query = {'credentials.email': email}
    
    user = await request.app.users.find_account(**query)
    if user is None:
        abort(403, 'Credentials invalid.')
    elif user.check_password(password) == False:
        abort(403, 'Credentials invalid.')
    token = await request.app.users.issue_token(user)
    
    request['session']['logged_in'] = True
    request['session']['token'] = token
    
    
  
  
