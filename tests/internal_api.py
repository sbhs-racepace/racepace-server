'''
TEST OUR API HERE
'''

import requests

LOCATION = "-33.910,151.106,-33.900,151.116"

domain = "localhost:8000"

for x in range(10):
    resp = requests.get(f'http://{domain}/api/route', json={'location': LOCATION})
    
    print(resp.text)