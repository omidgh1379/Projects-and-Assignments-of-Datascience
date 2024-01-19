#!/bin/bash

python -c '
import networkx as nx

print("#Q-1:")
print("Nodes with High Degrees: ")
# Load graph from a GraphML file
G = nx.read_graphml("G_citation.graphml")
# Calculate degree counts and display top 10 nodes
degrees = sorted(G.degree, key=lambda x: x[1], reverse=True)[:10]
for node, degree in degrees:
    print(node, degree)

print("#Q-2:")
# Extract edges and source nodes, count occurrences of each node
edges = G.edges()
node_degrees = {}
for edge in edges:
    source = edge[0]
    if source in node_degrees:
        node_degrees[source] += 1
    else:
        node_degrees[source] = 1

# Calculate total degrees
total_degrees = sum(node_degrees.values())

# Count the number of nodes
total_nodes = len(node_degrees)

# Calculate average degree
average_degree = total_degrees / total_nodes if total_nodes > 0 else 0
print(f"Total degrees: {total_degrees}")
print(f"Total nodes: {total_nodes}")
print(f"Average degree: {average_degree}")

print("Nodes with Low Degrees: ")
low_degree_nodes = {k: v for k, v in node_degrees.items() if v <= 5}
for node, degree in sorted(low_degree_nodes.items(), key=lambda x: x[1], reverse=True)[-10:]:
    print(node, degree)

print("# Q-3:")
# Calculate the sum of shortest path lengths between all pairs of nodes
total_length = sum(len(path) - 1 for source in G for target, path in nx.bfs_edges(G, source=source))
# Calculate the total number of paths (excluding self-paths)
total_paths = sum(1 for source in G for _ in nx.bfs_edges(G, source=source))
# Calculate the average shortest path length
average_length = total_length / total_paths if total_paths > 0 else 0
print(f"Average shortest path length: {average_length}")
'