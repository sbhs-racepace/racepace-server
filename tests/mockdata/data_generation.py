import requests
from server import Route,Point

def data_generation(bounding_box):
    ways_response = requests.get(f"http://overpass-api.de/api/interpreter?data=[out:json];way({bounding_box});out;")
    ways = ways_response.text
    with open('ways.json', 'w') as f:
        f.write(str(ways))
    nodes_response = requests.get(f"http://overpass-api.de/api/interpreter?data=[out:json];node({bounding_box});out;")
    nodes = nodes_response.text
    with open('nodes.json', 'w') as f:
        f.write(str(nodes))

if __name__ == '__main__': 
    location = Point(-33.8796735,151.2053924)
    vert_unit,hor_unit = Route.get_coordinate_units(location)
    bounding_box = Route.rectangle_bounding_box(location,1000,1000)
    data_generation(bounding_box)
