import requests

LOCATION = "-33.910,151.106,-33.900,151.116"

resp = requests.get(f"http://overpass-api.de/api/interpreter?data=[out:json];way({LOCATION});out;")
print(resp.json())

resp = requests.get(f"http://overpass-api.de/api/interpreter?data=[out:json];node({LOCATION});out;")
print(resp.json())

