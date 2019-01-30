import requests
import json
import math
from math import inf
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

file_setup()

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


# ways_file = open('ways.txt','r')
# ways_json = json.loads(ways_file.read())
# ways = ways_json['elements']
#
# nodes_file = open('nodes.txt','r')
# nodes_json = json.loads(nodes_file.read())
# nodes = nodes_json['elements']
#
# neighbours = dict()
# roads = dict()
# for node in nodes:
#     neighbours[node['id']] = set()
#
# for way in ways:
#     way_nodes = way['nodes']
#     for current in range(len(way_nodes)):
#         if way_nodes[current] not in neighbours:
#             continue
#             # neighbours[way_nodes[current]] = set()
#         previous = current - 1 if current > 0 else None
#         next = current + 1 if current + 1 < len(way_nodes) else None
#         current_neighbours = {way_nodes[index] for index in [previous,next] if index != None}
#         neighbours[way_nodes[current]] |= current_neighbours
#
# roads = dict()
# for node,node_neighbours in neighbours.items():
#     for neighbour in node_neighbours:
#         roads[tuple(sorted((node,neighbour)))] = 1 #Temporary
#
# def djikstra(nodes,roads,start,end,neighbour_dict):
#     path_dict = dict((node,(inf,None)) for node in nodes)
#     unvisited = set(nodes)
#     visited   = set()
#     path_dict[start] = (0,[start])
#     current = start
#     # print(neighbour_dict)
#     while True:
#         current_cost,current_path = path_dict[current]
#         neighbours = neighbour_dict[current]
#         for neighbour in neighbours:
#             if neighbour in unvisited:
#                 neighbour_cost,neighbour_path = path_dict[neighbour]
#                 road_name = tuple(sorted((current,neighbour)))
#                 cost = roads[road_name] + current_cost
#                 if cost < neighbour_cost:
#                     path_dict[neighbour] = (cost,current_path + [neighbour])
#         unvisited.remove(current)
#         visited.add(current)
#         min_cost,min_node = inf,None
#         for node in unvisited:
#             cost,path = path_dict[(node)]
#             if cost < min_cost:
#                 min_cost,min_node = cost,node
#         if end in visited:
#             break
#         elif min_cost == inf:
#             return False
#         else:
#             current = min_node
#     return path_dict[end]
#
# start = 1741123983
# end = 1741123995
#
# print(djikstra([node['id'] for node in nodes],roads,start,end,neighbours))
