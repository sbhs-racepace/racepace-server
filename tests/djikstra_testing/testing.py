import requests
import json
import math
LOCATION = "-33.901,151.106,-33.900,151.107"
EARTH_RADIUS = 6373000


def file_setup():
    ways_response = requests.get(f"http://overpass-api.de/api/interpreter?data=[out:json];way({LOCATION});out;")
    ways = ways_response.text
    with open('ways.txt', 'w') as f:
        f.write(str(ways))
    nodes_response = requests.get(f"http://overpass-api.de/api/interpreter?data=[out:json];node({LOCATION});out;")
    nodes = nodes_response.text
    with open('nodes.txt', 'w') as f:
        f.write(str(nodes))

def deg_to_rad(deg):
    return deg * math.pi/180

def node_dist(node1,node2):
    lat1,lon1 = node1.values()
    lat2,lon2 = node2.values()
    lon1,lat1,lon2,lat2 = map(float,[lon1,lat1,lon2,lat2])
    dlon = deg_to_rad(lon2) - deg_to_rad(lon1)
    dlat = deg_to_rad(lat2) - deg_to_rad(lat1)
    a = (math.sin(dlat/2))**2 + math.cos(lat1) * math.cos(lat2) * (math.sin(dlon/2))**2
    c = 2 * math.atan2( math.sqrt(a), math.sqrt(1-a) )
    d = EARTH_RADIUS * c
    return d


ways_file = open('ways.txt','r')
ways_json = json.loads(ways_file.read())
# print(ways)

nodes_file = open('nodes.txt','r')
nodes_json = json.loads(nodes_file.read())
nodes = nodes_json['elements']
new_nodes = {}
for node in nodes:
    _,id,lat,lon = node.values()
    print(id,lat,lon)
    new_nodes[id] = {'lat':lat,'lon':lon}

start = 1741123983
end = 1741123995
start_node = new_nodes[start]
end_node = new_nodes[end]
print(start_node,end_node)
print(node_dist(start_node,end_node))
