import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Load the edge list from an Excel file
edge_list = pd.read_excel("edges_2023.xlsx")
G = nx.from_pandas_edgelist(edge_list, source="Source", target="Target", edge_attr="weight", create_using=nx.DiGraph())

# Load categories from centrality DataFrame (assumes you already calculated categories)
centrality_df = pd.read_excel("centrality_measure_2023.xlsx")
categories = centrality_df.set_index("Country")["Category"].to_dict()


# Assign radii based on categories
def categorize_positions(G, categories):
    core_radius = 0.3  # Core countries closer to the center
    semi_periphery_radius = 0.6  # Semi-periphery countries in the middle
    periphery_radius = 1.0  # Periphery countries on the outermost circle
    
    # Initialize positions dictionary
    positions = {}
    
    # Divide nodes by categories
    core_nodes = [node for node in G.nodes if categories[node] == "Core"]
    semi_periphery_nodes = [node for node in G.nodes if categories[node] == "Semi-Periphery"]
    periphery_nodes = [node for node in G.nodes if categories[node] == "Periphery"]
    
    # Helper function to assign positions in a circle
    def assign_positions(nodes, radius, start_angle=0):
        angle_step = 2 * np.pi / len(nodes)
        positions.update({
            node: (radius * np.cos(start_angle + i * angle_step),
                   radius * np.sin(start_angle + i * angle_step))
            for i, node in enumerate(nodes)
        })
    
    # Assign positions for each group
    assign_positions(core_nodes, core_radius)
    assign_positions(semi_periphery_nodes, semi_periphery_radius)
    assign_positions(periphery_nodes, periphery_radius)
    
    return positions

# Use your existing graph and categories
positions = categorize_positions(G, categories)

# Plot the network
plt.figure(figsize=(12, 8))
colors = {"Core": "red", "Semi-Periphery": "green", "Periphery": "blue"}
node_colors = [colors[categories[node]] for node in G.nodes]

nx.draw(
    G, pos=positions, with_labels=True, node_size=500,
    node_color=node_colors, edge_color="gray", font_size=8
)
plt.title("Global Petroleum Trade Network - Categorized Layout")
plt.show()
