import networkx as nx

def extract_shortest_paths(edges0):
    """Gets shortest node lengths (make sure to give 0 indexed edge list)"""
    # Make a graph from the edge list (0 indexed)
    G = nx.Graph()
    G.add_edges_from(edges0)

    # Built in function to get all shortest paths
    all_pairs = dict(nx.all_pairs_shortest_path_length(G))

    # Init distance edge lists
    dist1 = []
    dist2 = []
    dist3 = []
    dist4 = []
    dist5 = []
    for u, dists in all_pairs.items():
        for v, dist in dists.items():
            if u < v:  # avoid duplicates (since undirected)
                # Gives us all the node pairs (where lower node is first) for each distance
                if dist == 1:
                    dist1.append([u, v])
                elif dist == 2:
                    dist2.append([u, v])
                elif dist == 3:
                    dist3.append([u, v])
                elif dist == 4:
                    dist4.append([u, v])
                elif dist ==5:
                    dist5.append([u, v])

    return dist1,dist2,dist3,dist4,dist5

edges = [
    [1,2], [2,4], [4,5], [4,12], [2,3], [3,4], [3,11], [11,12],
    [3,6], [6,7], [6,9], [9,11], [7,8], [8,9], [9,10], [8,10]
]

# convert to 0-based
edges0 = [(i-1, j-1) for i, j in edges]

dist1,dist2,dist3,dist4,dist5 = extract_shortest_paths(edges0)

print(len(dist1))
print(len(dist2))
print(len(dist3))
print(len(dist4))
print(len(dist5))