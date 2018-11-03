import xml.etree.ElementTree as et
import copy, math

def deg2rad(deg):
    rad = deg * math.pi/180
    return rad

def dist(node1,node2):
    lat1,lon1 = nodes[node1].pos
    lat2,lon2 = nodes[node2].pos
    lon1,lat1,lon2,lat2 = map(float,[lon1,lat1,lon2,lat2])
    dlon = deg2rad(lon2) - deg2rad(lon1) 
    dlat = deg2rad(lat2) - deg2rad(lat1)
    a = (math.sin(dlat/2))**2 + math.cos(lat1) * math.cos(lat2) * (math.sin(dlon/2))**2 
    c = 2 * math.atan2( math.sqrt(a), math.sqrt(1-a) ) 
    d = 6373000 * c
    return d

tree = et.parse("nodes.txt")
root = tree.getroot()
nodes = {}
class Node:
    def __init__(self,pos,tags):
        self.pos = pos #Tuple of lat and lon
        self.tags = tags #Dictionary of tags (road names and other info
        self.neighbours = set() #Set of neighbour's node IDs
        self.dist = math.inf #Distance value for Dijkstra's algorithm
    

for child in root:
    if child.tag in {"note","meta"}:
        continue
    pos = (child.get("lat"),child.get("lon"))
    tags = {}
    for sub in child:
        tags[sub.get("k")]=sub.get("v")
    nodes[int(child.get("id"))] = Node(pos,tags)

tree = et.parse("ways.txt")
root = tree.getroot()
ways = {}


class Way:
    def __init__(self,nodes,tags):
        self.nodes = nodes
        self.tags = tags


# TODO: YO SUNNY CAN u help transfer what u did here into the utils/route.py file? kinda hard to see whats going on here

for child in root:
    if child.tag in {"note","meta"}:
        continue
    nodes_temp = []
    tags_temp = {}
    for sub in child:
        if sub.tag == "nd":
            id_ = int(sub.get("ref"))                
            if id_ in nodes:
                nodes_temp.append(id_)
        elif sub.tag == "tag":
            tags_temp[sub.get("k")]=sub.get("v")
    
    if "highway" not in tags_temp or len(nodes_temp) <= 1:
        continue
    nodes[nodes_temp[0]].neighbours.add(nodes_temp[1])
    for i,nodeID in enumerate(nodes_temp[1:-1],1):
        if child.get("id") == "162293685":
            print(nodes_temp[i-1],nodes_temp[i+1],nodeID,i)
        nodes[nodeID].neighbours.add(nodes_temp[i-1])
        nodes[nodeID].neighbours.add(nodes_temp[i+1])
    nodes[nodes_temp[-1]].neighbours.add(nodes_temp[-2])
    ways[int(child.get("id"))] = Way(nodes_temp,tags_temp)    

#TESTING POINTS (Location on Google Maps below)
START = 1734579066 #Albert Rd & Brighton Ave, Croydon Park (Albert Rd exit)
END = 1742072577 #7-12 (End of) Coorilla Ave, Croydon Park
unvisited = copy.copy(nodes)
unvisited.pop(START)
visited = [] #FOR DEBUG
current = START
nodes[START].dist = 0
while current != END:
    if current in nodes[current].neighbours:
        nodes[current].neighbours.remove(current)
        #Delete self from neighbours (can't see where it is being added)
    for node in nodes[current].neighbours:
        d = dist(current,node) + nodes[current].dist
        if d < nodes[node].dist:
            nodes[node].dist = d
    unvisited.pop(current,None)
    visited.append(current) #FOR DEBUG
    last = current
    current = sorted(unvisited,key=lambda x:nodes[x].dist)[0]

# Unsure about this part (how to get the shortest path once alg. has finished
current = END
path = []
while current != START:
    path.append(sorted(nodes[current].neighbours,key=lambda x:nodes[x].dist)[0])
    current = path[-1]
print(path)
