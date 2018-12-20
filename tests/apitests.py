import requests
import json 

data = {
    'size': 1000, # meters
    'location': '-33.96403,151.10120',
    'start': '-33.96403,151.10120',
    'end': '-33.9621752,151.1054158'
}

data = json.dumps(data)

resp = requests.get('http://127.0.0.1:8000/api/route', data=data)

print(resp)
print(resp.text)