import requests, json

LOCATION = "-33.91493 151.09928 -33.91543 151.11199 -33.89894 151.11237 -33.89769 151.09898"

req = f'''
[out:json];
(
    way
        ["highway"~"."]
        (poly:"{LOCATION}");
    >;
);
out;'''.replace("\n","").replace("\t","")

resp = requests.get(f"http://overpass-api.de/api/interpreter?data={req}")
resp = resp.json()
print(resp.keys())

    
