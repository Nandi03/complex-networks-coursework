import pandas as pd
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

# Load the edge list from an Excel file
edge_list = pd.read_excel("edges_list_2013.xlsx")
G = nx.from_pandas_edgelist(edge_list, source="Source", target="Target", edge_attr="weight", create_using=nx.DiGraph())

pagerank_results = nx.pagerank(G, weight="weight", alpha=0.85)  # Replace G_year2 with your graph

# Sort by PageRank values (descending order)
sorted_pagerank = sorted(pagerank_results.items(), key=lambda x: x[1], reverse=True)

# Convert to a DataFrame for easy handling
pagerank_df = pd.DataFrame(sorted_pagerank, columns=['Country', 'PageRank'])
import matplotlib.pyplot as plt

# Plot the top 20 countries by PageRank
top_n = 20
plt.figure(figsize=(12, 6))
plt.bar(pagerank_df['Country'][:top_n], pagerank_df['PageRank'][:top_n], color='skyblue')
plt.xticks(rotation=45, ha='right')
plt.xlabel('Country')
plt.ylabel('PageRank Score')
plt.title(f'Top {top_n} Countries by PageRank')
plt.tight_layout()
plt.show()

plt.figure(figsize=(12, 6))
plt.scatter(range(len(pagerank_df)), pagerank_df['PageRank'], color='orange', alpha=0.7)
plt.xlabel('Countries (Ranked)')
plt.ylabel('PageRank Score')
plt.title('PageRank Distribution Across All Countries')
plt.tight_layout()
plt.show()
