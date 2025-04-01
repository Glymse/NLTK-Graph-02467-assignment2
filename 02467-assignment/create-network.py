import json
import pandas as pd
import networkx as nx

# Load DataFrames
df_articles = pd.read_csv("df_articles.csv")  # Replace with actual filename
df_authors = pd.read_csv("df_authors.csv")    # Replace with actual filename

# Print column names for debugging (remove after verification)
print("df_articles columns:", df_articles.columns)
print("df_authors columns:", df_authors.columns)

# Convert 'author_ids' column from string to list if necessary
if isinstance(df_articles["author_ids"].iloc[0], str):
    df_articles["author_ids"] = df_articles["author_ids"].apply(eval)  # Convert from string to list

# Step 1: Create Weighted Edgelist
weighted_edges = {}
for _, row in df_articles.iterrows():
    authors = row["author_ids"]  # List of Author IDs
    for i in range(len(authors)):
        for j in range(i + 1, len(authors)):
            edge = tuple(sorted([authors[i], authors[j]]))  # Avoid duplicates
            weighted_edges[edge] = weighted_edges.get(edge, 0) + 1

# Convert to list of tuples for NetworkX
weighted_edgelist = [(a, b, int(w)) for (a, b), w in weighted_edges.items()]  # Ensure weight is int

# Step 2: Create Graph and Add Edges
G = nx.Graph()
G.add_weighted_edges_from(weighted_edgelist)

# Step 3: Add Node Attributes
# Convert authors data into a dictionary for quick lookup
author_info = df_authors.set_index("id").to_dict(orient="index")

for node in G.nodes():
    if node in author_info:
        G.nodes[node]["name"] = author_info[node]["display_name"]
        G.nodes[node]["country"] = author_info[node]["country_code"]
    else:
        G.nodes[node]["name"] = "Unknown"
        G.nodes[node]["country"] = "Unknown"

    # Get author's papers
    author_papers = df_articles[df_articles["author_ids"].apply(lambda x: node in x)]
    
    if not author_papers.empty:
        first_pub = int(author_papers["publication_year"].min())  # Convert to int
        total_citations = int(author_papers["cited_by_count"].sum())  # Convert to int
    else:
        first_pub = None
        total_citations = 0

    # Add attributes to node
    G.nodes[node]["first_publication"] = first_pub
    G.nodes[node]["total_citations"] = total_citations

# Step 4: Save Network as JSON
# Convert numpy types to standard Python types
data = nx.readwrite.json_graph.node_link_data(G)
data = json.loads(json.dumps(data, default=lambda x: int(x) if isinstance(x, (pd.Series, pd.DataFrame, int, float)) else str(x)))

nx.write_graphml(G, "coauthorship_network.graphml")

with open("coauthorship_network.json", "w") as f:
    json.dump(data, f, indent=4)

print("✅ Network successfully created and saved as 'coauthorship_network.json'")
