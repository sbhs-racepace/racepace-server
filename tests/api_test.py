import requests
import json
from yarl import URL

api = URL('http://127.0.0.1:8000/api')


def test_route():
    data = {
        'size': 1000, # meters
        'start': '-33.965832, 151.089029',
        'end': '-33.964693, 151.090788'
    }

    resp = requests.post(api / 'route', json=data)

    print(resp)
    print(resp.json())


def login(**credentials):
    url = api/'login'
    print(url)
    resp = requests.post(url, json=credentials)
    print(resp)
    print(resp.json())


def register(**credentials):
    url = api/'register'
    resp = requests.post(url, json=credentials)
    print(resp)
    print(resp.json())


login(email='testing@gmail.com', password='testing123')


