import xml.etree.ElementTree as et
import pickle
tree = et.parse("ways.txt")
root = tree.getroot()
ways = {}
class Way:
    def __init__(self,nodes,tags):
        self.nodes = nodes
        self.tags = tags

for child in root:
    if child.tag in {"note","meta"}:
        continue
    nodes = []
    tags = {}
    for sub in child:
        if sub.tag == "nd":
            nodes.append(sub.get("ref"))
        elif sub.tag == "tag":
            tags[sub.get("k")]=sub.get("v")
    ways[child.get("id")] = Way(nodes,tags)
    
tree = et.parse("nodes.txt")
root = tree.getroot()
nodes = {}
class Node:
    def __init__(self,pos,tags):
        self.pos = pos
        self.tags = tags

for child in root:
    if child.tag in {"note","meta"}:
        continue
    pos = (child.get("lat"),child.get("lon"))
    tags = {}
    for sub in child:
        tags[sub.get("k")]=sub.get("v")
    nodes[child.get("id")] = Node(pos,tags)
