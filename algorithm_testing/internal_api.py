'''
TEST OUR API HERE
'''

import requests

LOCATION = "-33.910,151.106,-33.900,151.116"

domain = "localhost:8000"

data = {
    'bounding_box': '-33.93689236,151.02221842,-33.93924224,151.02573748',
    'start': 1741123995,
    'stop': 1741124011
    }

resp = requests.get(f'http://{domain}/api/route', json=)

print(resp.text)