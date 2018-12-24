import requests
import json

data = {
    'size': 1000, # meters
    'start': '-33.965832, 151.089029',
    'end': '-33.964693, 151.090788'
}

data = json.dumps(data)

resp = requests.post('http://127.0.0.1:8000/api/route', data=data)

print(resp)
print(resp.text)
