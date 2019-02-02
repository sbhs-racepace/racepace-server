import requests

def data_generation(bounding_box):
    ways_response = requests.get(f"http://overpass-api.de/api/interpreter?data=[out:json];way({bounding_box});out;")
    ways = ways_response.text
    with open('ways.json', 'w') as f:
        f.write(str(ways))
    nodes_response = requests.get(f"http://overpass-api.de/api/interpreter?data=[out:json];node({bounding_box});out;")
    nodes = nodes_response.text
    with open('nodes.json', 'w') as f:
        f.write(str(nodes))
