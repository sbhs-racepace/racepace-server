import request

def file_setup(locations):
    ways_response = requests.get(f"http://overpass-api.de/api/interpreter?data=[out:json];way({locations});out;")
    ways = ways_response.text
    with open('ways.txt', 'w') as f:
        f.write(str(ways))
    nodes_response = requests.get(f"http://overpass-api.de/api/interpreter?data=[out:json];node({locations});out;")
    nodes = nodes_response.text
    with open('nodes.txt', 'w') as f:
        f.write(str(nodes))
