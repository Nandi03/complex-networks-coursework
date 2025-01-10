import networkx as nx
import pandas as pd
import numpy as np
from collections import defaultdict

# Load the edges for the two years from Excel
edges_year1 = pd.read_excel('edges_list_2013.xlsx')
edges_year2 = pd.read_excel('edges_2023.xlsx')

# Create directed graphs for each year
G_year1 = nx.from_pandas_edgelist(edges_year1, source='Source', target='Target', edge_attr='weight', create_using=nx.DiGraph())
G_year2 = nx.from_pandas_edgelist(edges_year2, source='Source', target='Target', edge_attr='weight', create_using=nx.DiGraph())

# Combine all unique nodes from both graphs
all_nodes = set(G_year1.nodes).union(set(G_year2.nodes))

# Add missing nodes to each graph (in case one graph is missing a node)
G_year1.add_nodes_from(all_nodes)
G_year2.add_nodes_from(all_nodes)
# Invert weights for Year 1
for u, v, data in G_year1.edges(data=True):
    if data["weight"] > 0:  # Avoid division by zero
        data["inv_weight"] = 1 / data["weight"]
    else:
        data["inv_weight"] = float('inf')  # Assign a very large distance

# Invert weights for Year 2
for u, v, data in G_year2.edges(data=True):
    if data["weight"] > 0:
        data["inv_weight"] = 1 / data["weight"]
    else:
        data["inv_weight"] = float('inf')


# Compute centralities for Year 1 and Year 2
betweenness_year1 = nx.betweenness_centrality(G_year1, weight="inv_weight", normalized=True)
closeness_year1 = nx.closeness_centrality(G_year1, distance="inv_weight")
# sink_year1 = nx.in_degree_centrality(G_year1, weight="weight")
# source_year1 = nx.out_degree_centrality(G_year1, weight="weight")

betweenness_year2 = nx.betweenness_centrality(G_year2, weight="inv_weight", normalized=True)
closeness_year2 = nx.closeness_centrality(G_year2, distance="inv_weight")
# sink_year2 = nx.in_degree_centrality(G_year2, weight="weight")
# source_year2 = nx.out_degree_centrality(G_year2, weight="weight")

# Compute sink (weighted in-degree) and source (weighted out-degree) for Year 1
sink_year1 = {node: sum(weight for _, _, weight in G_year1.in_edges(node, data="weight")) for node in G_year1.nodes()}
source_year1 = {node: sum(weight for _, _, weight in G_year1.out_edges(node, data="weight")) for node in G_year1.nodes()}

# Compute sink and source for Year 2
sink_year2 = {node: sum(weight for _, _, weight in G_year2.in_edges(node, data="weight")) for node in G_year2.nodes()}
source_year2 = {node: sum(weight for _, _, weight in G_year2.out_edges(node, data="weight")) for node in G_year2.nodes()}


# Rank countries by each centrality for both years
def rank_countries(centrality_dict):
    return {k: rank for rank, (k, v) in enumerate(sorted(centrality_dict.items(), key=lambda item: item[1], reverse=True), 1)}

betweenness_rank_year1 = rank_countries(betweenness_year1)
closeness_rank_year1 = rank_countries(closeness_year1)
sink_rank_year1 = rank_countries(sink_year1)
source_rank_year1 = rank_countries(source_year1)

betweenness_rank_year2 = rank_countries(betweenness_year2)
closeness_rank_year2 = rank_countries(closeness_year2)
sink_rank_year2 = rank_countries(sink_year2)
source_rank_year2 = rank_countries(source_year2)

# Combine rankings into a single dataframe
rank_data = pd.DataFrame({
    'Country': list(all_nodes),
    'Betweenness_Year1': [betweenness_rank_year1.get(country, None) for country in all_nodes],
    'Closeness_Year1': [closeness_rank_year1.get(country, None) for country in all_nodes],
    'Sink_Year1': [sink_rank_year1.get(country, None) for country in all_nodes],
    'Source_Year1': [source_rank_year1.get(country, None) for country in all_nodes],
    'Betweenness_Year2': [betweenness_rank_year2.get(country, None) for country in all_nodes],
    'Closeness_Year2': [closeness_rank_year2.get(country, None) for country in all_nodes],
    'Sink_Year2': [sink_rank_year2.get(country, None) for country in all_nodes],
    'Source_Year2': [source_rank_year2.get(country, None) for country in all_nodes]
})

# Function to calculate stability and categorize countries
def calculate_stability_and_categorize(df, threshold=10):
    stability = []
    betweenness_ranking = df.sort_values('Betweenness_Year2').reset_index()

    # Determine the midpoint of the closeness ranking
    midpoint = len(betweenness_ranking) // 2
    top_half_countries = set(betweenness_ranking.iloc[midpoint:]['Country'])
    bottom_half_countries = set(betweenness_ranking.iloc[:midpoint]['Country'])

    sink_ranking = df.sort_values('Sink_Year2').reset_index()

    # Determine the midpoint of the closeness ranking
    midpoint = len(sink_ranking) // 4
    top_half_countries = set(sink_ranking.iloc[:midpoint]['Country'])
    bottom_half_countries = set(sink_ranking.iloc[:midpoint]['Country'])

    for _, row in df.iterrows():
        # Determine rank changes
        rank_changes = {}
        for centrality in [ 'Betweenness', 'Closeness', 'Sink', 'Source']:
            rank_year1 = row[f'{centrality}_Year1']
            rank_year2 = row[f'{centrality}_Year2']
            if rank_year1 is not None and rank_year2 is not None:
                rank_changes[centrality] = rank_year2 - rank_year1

        # Determine overall stability based on rank changes
        is_stable = all(abs(change) <= threshold for centrality, change in rank_changes.items() if centrality != 'Source')

        is_improving =  any(change < 0 for change in rank_changes.values())

        # Categorize countries based on stability and closeness ranking
        if is_stable:
            if not row['Country'] in top_half_countries:
                stability_score = "unstable and improving"
            else:
                stability_score = 'Stable'
        elif is_improving:
            stability_score = 'unstable and improving'

        else:
            stability_score = 'unstable and not improving'

        stability.append(stability_score)

    df['Stability'] = stability

# Apply the updated stability categorization
calculate_stability_and_categorize(rank_data)

# Save the updated results to a new Excel file
rank_data.to_excel('stability_analysis.xlsx', index=False)
