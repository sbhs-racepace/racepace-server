import sys
import os

sys.path.append("../server")

from core.route import *


with open('mock_data/ways.json') as f:
    waydata = json.load(f)

with open('mock_data/nodes.json') as f:
    nodedata = json.load(f)

ways = Way.json_to_ways(waydata)
nodes = Node.json_to_nodes(nodedata)

tag_keys = set()
nodes_with_tags = [n for n in nodes.values() if n.tags]

for node in nodes_with_tags:
    for tag in node.tags:
        tag_keys.add(tag)

print(tag_keys)
