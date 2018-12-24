import requests
import json 

data = {
    'size': 1000, # meters
    'start': '-33.963565,151.092603',
    'end': '-33.971164, 151.104033'
}

data = json.dumps(data)

resp = requests.get('http://127.0.0.1:8000/api/route', data=data)

print(resp)
print(resp.text)