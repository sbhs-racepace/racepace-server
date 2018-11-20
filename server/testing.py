from core.route import *
import json

with open('mockdata/ways.json') as f:
    waydata = json.load(f)

with open('mockdata/nodes.json') as f:
    nodedata = json.load(f)

ways = Way.json_to_ways(waydata)
nodes = Node.json_to_nodes(nodedata)

start = 1741123995
end   = 1741124011

route = Route.generate_route(nodes, ways, start, end)

print(route.route, route.distance)
