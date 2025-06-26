import json
import networkx as nx
import matplotlib.pyplot as plt

# Load your JSON file
with open('data/input/small_evacuation_data.json', 'r') as f:
    data = json.load(f)

G = nx.Graph()

# Add residential areas
for ra in data["residential_areas"]:
    G.add_node(ra["id"], label=ra["population"], node_type="RA")

# Add places of refuge
for pr in data["places_of_refuge"]:
    G.add_node(pr["id"], label=pr["capacity"], node_type="PR")

# Add edges with distance as weight
for edge in data["edges"]:
    G.add_edge(edge["from"], edge["to"], weight=edge["distance_km"])

# Node colors based on type
color_map = []
for node in G:
    node_type = G.nodes[node]["node_type"]
    color_map.append("skyblue" if node_type == "RA" else "lightgreen")

# Labels and edge weights
labels = {node: G.nodes[node]["label"] for node in G.nodes}
#edge_labels = nx.get_edge_attributes(G, "weight")

# Layout and drawing
pos = nx.spring_layout(G, seed=42, k=0.7)

plt.figure(figsize=(10, 10)) 

nx.draw_networkx_nodes(G, pos, node_color=color_map, node_size=600)
nx.draw_networkx_labels(G, pos, labels=labels, font_size=8)

nx.draw_networkx_edges(G, pos, alpha=0.2)

plt.title("Residential Areas and Places of Refuge")
plt.tight_layout()
plt.show()
