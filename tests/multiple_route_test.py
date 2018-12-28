import sys
import os

sys.path.append("../server")

from core.route import *

from mock_data.data_generation import data_generation
import json

location = Point(-33.8796735,151.2053924)
vert_unit,hor_unit = Route.get_coordinate_units(location)
bounding_box = Route.rectangle_bounding_box(location,1000,1000)
# data_generation(bounding_box)

with open('mock_data/ways.json') as f:
    waydata = json.load(f)

with open('mock_data/nodes.json') as f:
    nodedata = json.load(f)

ways = Way.json_to_ways(waydata)
nodes = Node.json_to_nodes(nodedata)

node_waypoints = [8109379, 2347313263, 2347313310, 1833169111, 8109372, 2347313335, 1833169115, 26635703, 2347313219, 8965926, 2347313230, 8965918, 3881588504, 18249032, 26526582, 13757633, 3200901770, 5106603995, 3200901771, 3200901772, 4092708895, 3924593359, 1839978236, 5551854462, 1839978198, 1839978228, 13764188, 3924594164, 3924594170, 3924594182, 3924594185, 3924594191, 3924594168, 1833171242, 3924594178, 3924594161, 3924594172, 3924594184, 20930159, 13764186, 20930160, 8109400]


route = Route.generate_multi_route(nodes, ways, node_waypoints)
print(route.route, route.distance)
