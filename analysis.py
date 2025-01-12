import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter

# Load data
edges = pd.read_excel("edges_list_2013.xlsx")  
nodes = pd.read_excel("nodes_list_2013.xlsx") 

# Invert weights (higher weights -> stronger connections -> shorter distances)
edges['weight_inverted'] = 1 / edges['weight']

# Create the directed, weighted graph
G = nx.DiGraph()

# Add edges with weights
for _, row in edges.iterrows():
    G.add_edge(row['Source'], row['Target'], weight=row['weight'])

# Add nodes (optional, if you need attributes for nodes)
for _, row in nodes.iterrows():
    if row['country'] not in G:
        G.add_node(row['country'])

# Compute centralities
# Betweenness centrality
betweenness = nx.betweenness_centrality(G, weight='weight_inverted')

# Closeness centrality
closeness = nx.closeness_centrality(G, distance='weight_inverted')

# source and sink scores
# source score: Total outgoing trade volume
source_scores = {node: sum(d['weight'] for _, _, d in G.out_edges(node, data=True)) for node in G.nodes()}
# Sink score: Total incoming trade volume
sink_scores = {node: sum(d['weight'] for _, _, d in G.in_edges(node, data=True)) for node in G.nodes()}

# Rank and display top 10 countries for each metric
def get_top_10(metric_dict, metric_name):
    sorted_metric = sorted(metric_dict.items(), key=lambda x: x[1], reverse=True)
    print(f"Top 10 countries by {metric_name}:")
    for i, (country, score) in enumerate(sorted_metric[:10], 1):
        print(f"{i}. {country}: {score}")
    print()

# Display results
get_top_10(betweenness, "betweenness centrality")
get_top_10(closeness, "closeness centrality")
get_top_10(source_scores, "source score (outgoing trade volume)")
get_top_10(sink_scores, "sink score (incoming trade volume)")

# compute degree distribution
in_degrees = [G.in_degree(node) for node in G.nodes()]
out_degrees = [G.out_degree(node) for node in G.nodes()]

# Count the frequency of each degree (ignoring edge weights)
in_degree_count = Counter(in_degrees)
out_degree_count = Counter(out_degrees)

# Extract unique degree values and their corresponding frequencies
in_degree_values, in_degree_frequencies = zip(*sorted(in_degree_count.items()))
out_degree_values, out_degree_frequencies = zip(*sorted(out_degree_count.items()))



