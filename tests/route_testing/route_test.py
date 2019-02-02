from server import Route,Point
import json

with open('../mockdata/ways.json') as f: waydata = json.load(f)
with open('../mockdata/nodes.json') as f: nodedata = json.load(f)

nodes, ways = Route.transform_json_nodes_and_ways(nodedata,waydata)

start_id = 8109379
end_id   = 8109400


route = Route.generate_route(nodes, ways, start_id, end_id)
print(route.route, route.distance)
