from math import inf

graph = [[1,2,3],
         [1,4,1],
         [1,1,1]]
         
start = (0,0)
end = (2,2)
vector = ((1,0),(-1,0),(0,1),(0,-1))

height = len(graph)
width  = len(graph[0])
nodes = [(x,y) for x in range(height) for y in range(width)]

def basic_djikstra(start,end,nodes):
    visited = set()
    unvisited = set(nodes)
    cost_dict = dict((coord,(inf,None)) for coord in nodes)
    x,y = start
    cost_dict[(x,y)] = (0,[(x,y)])
    while True:
        current_cost,current_path = cost_dict[(x,y)]
        for x_delta,y_delta in vector:
            n_x,n_y = (x + x_delta,y + y_delta)
            if (n_x,n_y) in unvisited:
                neighbour_cost,neighbour_path = cost_dict[(n_x,n_y)]
                cost = graph[n_y][n_x] + current_cost
                if neighbour_cost > cost:
                    cost_dict[(n_x,n_y)] = (cost,current_path + [(n_x,n_y)])
        unvisited.remove((x,y))
        visited.add((x,y))
        min_cost,min_coord = inf,(None,None)
        for c_x,c_y in unvisited:
            cost,path = cost_dict[(c_x,c_y)]
            if cost < min_cost:
                min_cost = cost
                min_coord = (c_x,c_y)
        if len(unvisited) == 0:
            break
        elif min_cost == inf:
            raise Exception("Can't traverse infinte path")
        else:
            x,y = min_coord
    return cost_dict[end]

print(basic_djikstra(start,end,nodes))
