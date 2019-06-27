from math import inf

nodes = ["A", "B", "C", "D", "E"]
roads = {"AB": 1, "BC": 2, "CD": 3, "AE": 1, "DE": 1}

start = "A"
end = "D"


def construct_neighbours(nodes, roads):
    neighbours = dict((node, []) for node in nodes)
    for road in roads:
        start, end = list(road)
        neighbours[start].append(end)
        neighbours[end].append(start)
    return neighbours


def djikstra(nodes, roads, start, end):
    path_dict = dict((node, (inf, None)) for node in nodes)
    unvisited = set(nodes)
    visited = set()
    neighbour_dict = construct_neighbours(nodes, roads)
    path_dict[start] = (0, [start])
    current = start

    while True:
        current_cost, current_path = path_dict[current]
        neighbours = neighbour_dict[current]
        for neighbour in neighbours:
            if neighbour in unvisited:
                neighbour_cost, neighbour_path = path_dict[neighbour]
                road_name = "".join(sorted(current + neighbour))
                cost = roads[road_name] + current_cost
                if cost < neighbour_cost:
                    path_dict[neighbour] = (cost, current_path + [neighbour])
        unvisited.remove(current)
        visited.add(current)
        min_cost, min_node = inf, None
        for node in unvisited:
            cost, path = path_dict[(node)]
            if cost < min_cost:
                min_cost, min_node = cost, node
        if end in visited:
            break
        elif min_cost == inf:
            print(path_dict)
            raise Exception("Can't traverse infinte path")
        else:
            current = min_node
    return path_dict[end]


print(djikstra(nodes, roads, start, end))
