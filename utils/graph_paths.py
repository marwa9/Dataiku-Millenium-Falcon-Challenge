# -*- coding: utf-8 -*-
"""
@author: Marwa Kechaou
"""

# Identify bidirectional edges to find possible paths.
# All edges are bidirectional except those including departure and arrival nodes
def get_bidirectional_edges(edges,departure,arrival,planets_distances):
    bidirectional_edges = []
    edges_distances = dict()
    for k,edge in enumerate(edges):
        i,j = edge[0],edge[1]
        if i == departure or j == arrival: 
            bidirectional_edges.append([i,j])
            edges_distances[i+j] = planets_distances[k]
        else:
            bidirectional_edges.append([i,j])
            bidirectional_edges.append([j,i])  
            edges_distances[i+j] = planets_distances[k]
            edges_distances[j+i] = planets_distances[k]
    return bidirectional_edges,edges_distances

# Construct thc acyclic graph necessary to identify all paths from departure to arrival  
# graph[i] is a list of all nodes (planets) that can be visited from node i
def graph_construction(dict_planets,planets,bidirectional_edges):           
    graph = []
    for p in dict_planets.keys():
        connections = []
        for j in planets:
            if j !=p:
                if [p,j] in bidirectional_edges:
                    connections.append(dict_planets[j])
        graph.append(connections)
    return graph

# Look for all possible paths from departure to arrival
def All_Paths_Departure_Arrival_bidirectionel(graph):
    def dfs(node, path):
        if node == n - 1:
            paths.append(path)
            return
        for neighbor in graph[node]:
            if neighbor not in path:
                dfs(neighbor, path + [neighbor])
    n = len(graph)
    paths = []
    dfs(0, [0])
    return paths