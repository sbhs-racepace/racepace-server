from core.route import *
from mockdata.data_generation import data_generation
import json

location = Point(-33.8796735,151.2053924)
bounding_box = Route.square_bounding(1000,1000,location)
# data_generation(bounding_box)

with open('ways.json') as f:
    waydata = json.load(f)

with open('nodes.json') as f:
    nodedata = json.load(f)

ways = Way.json_to_ways(waydata)
nodes = Node.json_to_nodes(nodedata)

#Need to add function that checks if you can actually get to this coordinate

start = 8109379
end   = 8109400

route = Route.generate_route(nodes, ways, start, end)
print(nodes[start].point - nodes[end].point)
print(route.route, route.distance)
