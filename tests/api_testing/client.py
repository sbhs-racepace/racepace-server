import requests
import json

class TestApiClient:
    BASE = 'http://127.0.0.1:8000/api'

    def __init__(self, token=None):
        self.session = requests.Session()
        self.token = token
        self.user_id = 0
        if token:
            self.session.headers = {
                'Authorization': 'Bearer ' + token
            }
    
    def register_user(self, **credentials):
        url = self.BASE + '/register'
        resp = self.session.post(url, json=credentials).json()
        if resp['success']:
            print('Created user with email: {email} and password: {password}'.format(**credentials))
        else:
            print(resp['error'])
        return resp
    
    def login(self, **credentials):
        url = self.BASE + '/login'
        resp = self.session.post(url, json=credentials)
        data = resp.json()
        if data['success']:
            self.session.headers = {
                'Authorization': 'Bearer '+ data['token']
                }
            self.user_id = data['user_id']
            print(f"Logged into user account with id: {data['user_id']}")
        else:
            print(data['error'])
        return data
    
    def delete_account(self, user_id=None):
        user_id = user_id or self.user_id
        url = self.BASE + f'/users/{user_id}'
        resp = self.session.delete(url).json()
        if resp['success']:
            print(f'Deleted user account with id: {user_id}')
        else:
            print(resp['error'])
        return resp

    def get_route(self, start, end):
        response = requests.get(self.BASE+'/route', params={'start':start,'end':end})
        return response.json()

    def create_group(self, **info):
        resp = self.session.post(self.BASE+'/groups/create', json=info)
        return response.json()

    def get_multiple_route(self, waypoints):
        response = requests.get(self.BASE + '/route/multiple', params={'waypoints': waypoints})
        return response.json()




