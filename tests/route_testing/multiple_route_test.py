from server import Route,Point
import json

with open('../mockdata/ways.json') as f: waydata = json.load(f)
with open('../mockdata/nodes.json') as f: nodedata = json.load(f)

nodes, ways = Route.transform_json_nodes_and_ways(nodedata,waydata)
node_waypoint_ids = [8109379, 2347313263, 2347313310, 1833169111, 8109372, 2347313335, 1833169115, 26635703, 2347313219, 8965926, 2347313230, 8965918, 3881588504, 18249032, 26526582, 13757633, 3200901770, 5106603995, 3200901771, 3200901772, 4092708895, 3924593359, 1839978236, 5551854462, 1839978198, 1839978228, 13764188, 3924594164, 3924594170, 3924594182, 3924594185, 3924594191, 3924594168, 1833171242, 3924594178, 3924594161, 3924594172, 3924594184, 20930159, 13764186, 20930160, 8109400]
node_waypoints = [nodes[node_id] for node_id in node_waypoint_ids]
route = Route.generate_multi_route(nodes, ways, node_waypoint_ids)
convex_points = (Route.get_convex_hull_points(node_waypoints))
convex_hull = Route.convex_hull(node_waypoints)
# print(convex_points)
print(convex_hull)
# print(node_waypoints)
print(route.route, route.distance)
