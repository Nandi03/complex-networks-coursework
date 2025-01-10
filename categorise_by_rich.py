import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import random

random.seed(0)

# Step 1: Load the edge list from Excel
# Replace 'edges_list.xlsx' with the actual file name and sheet name if necessary
df = pd.read_excel('edges_2023.xlsx')

# Step 2: Create the directed graph (DiGraph) from the edge list
# Assuming the columns in the Excel are 'source', 'target' and optionally 'weight'
G = nx.from_pandas_edgelist(df, source='Source', target='Target', edge_attr='weight', create_using=nx.DiGraph())

# Step 1: Create in-degree and out-degree graphs
in_degree_G = nx.DiGraph()
in_degree_G.add_edges_from((u, v) for u, v in G.edges() if G.in_degree(v) > 0)

out_degree_G = nx.DiGraph()
out_degree_G.add_edges_from((u, v) for u, v in G.edges() if G.out_degree(u) > 0)

# Step 2: Compute rich-club coefficients
in_rich_club = nx.rich_club_coefficient(in_degree_G.to_undirected(), normalized=True)
out_rich_club = nx.rich_club_coefficient(out_degree_G.to_undirected(), normalized=True)

# Step 3: Calculate the mean as the threshold
in_rich_threshold = sum(in_rich_club.values()) / len(in_rich_club)  # Mean for in-degree rich-club coefficient
out_rich_threshold = sum(out_rich_club.values()) / len(out_rich_club)  # Mean for out-degree rich-club coefficient

print(in_rich_threshold)
print(out_rich_threshold)

# Step 4: Categorize nodes
categories = {}
for node in G.nodes():
    in_degree = in_degree_G.degree(node)
    out_degree = out_degree_G.degree(node)
    
    in_rich = in_rich_club.get(in_degree, 0)
    out_rich = out_rich_club.get(out_degree, 0)

    if in_rich > in_rich_threshold and out_rich > out_rich_threshold:
        categories[node] = "High In-Degree, High Out-Degree"
    elif in_rich > in_rich_threshold and out_rich <= out_rich_threshold:
        categories[node] = "High In-Degree, Low Out-Degree"
    elif in_rich <= in_rich_threshold and out_rich > out_rich_threshold:
        categories[node] = "Low In-Degree, High Out-Degree"
    else:
        categories[node] = "Low In-Degree, Low Out-Degree"

# Step 3: Create a DataFrame and store in Excel
df = pd.DataFrame(list(categories.items()), columns=["Country", "Rich-Club Categorization"])

# Export to Excel
output_file = 'rich_club_categorization_2023.xlsx'
df.to_excel(output_file, index=False)

print(f"Data saved to {output_file}")