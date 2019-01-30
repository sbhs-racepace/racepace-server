import os

from core.route import *
from mockdata.data_generation import data_generation
import json

location = Point(-33.8796735,151.2053924)
vert_unit,hor_unit = Route.get_coordinate_units(location)
bounding_box = Route.square_bounding(1000,1000,location,vert_unit,hor_unit)
# data_generation(bounding_box)

with open('ways.json') as f:
    waydata = json.load(f)

with open('nodes.json') as f:
    nodedata = json.load(f)

ways = Way.json_to_ways(waydata)
nodes = Node.json_to_nodes(nodedata)

#Need to add function that checks if you can actually get to this coordinate

start_id = 8109379
end_id   = 8109400

route = Route.generate_route(nodes, ways, start_id, end_id)
print(nodes[start_id] - nodes[end_id])
print(route.route, route.distance)
