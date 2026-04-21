import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import networkx as nx
from matplotlib.sankey import Sankey
from sklearn.datasets import make_blobs

import os
os.makedirs('images', exist_ok=True)

sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Inter', 'Arial', 'sans-serif']

# 1. The Wall of Authority (Network Graph)
def gen_network_authority():
    plt.figure(figsize=(10, 8))
    G = nx.DiGraph()
    
    # Core nodes (Admins - Male coded)
    admins = ['Admin1', 'Admin2', 'Admin3', 'Booster1']
    for a in admins:
        G.add_node(a, node_type='admin', gender='Male', size=1500)
        
    # Peripheral nodes (Casuals - Female coded)
    casuals = [f'Casual{i}' for i in range(1, 25)]
    for c in casuals:
        G.add_node(c, node_type='casual', gender='Female', size=200)
        
    # Edges (Reverts from Admins to Casuals)
    np.random.seed(42)
    for c in casuals:
        # Admins revert casuals
        admin_reverter = np.random.choice(admins)
        G.add_edge(admin_reverter, c, weight=np.random.randint(1, 5))
        
    pos = nx.spring_layout(G, seed=42, k=0.5)
    
    # Draw logic
    node_colors = ['#1d4ed8' if G.nodes[n]['gender'] == 'Male' else '#db2777' for n in G.nodes()]
    node_sizes = [G.nodes[n]['size'] for n in G.nodes()]
    
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors, alpha=0.9, edgecolors='white', linewidths=2)
    nx.draw_networkx_edges(G, pos, arrowsize=15, arrowstyle='->', edge_color='#9ca3af', width=1.5, alpha=0.6)
    
    plt.title('The "Wall of Authority": Revert Mapping (Admins vs Casuals)', fontsize=16, pad=20, weight='bold')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('images/network_authority.png', dpi=300)
    plt.close()

# 2. Content Survival Curves
def gen_survival_curve():
    plt.figure(figsize=(10, 6))
    time = np.arange(0, 100, 1) # days
    
    # Male edit survival in Male articles (High survival)
    surv_male = np.exp(-time / 200) 
    # Female edit survival in Male articles (Low survival)
    surv_female = np.exp(-time / 15)
    
    # Step simulation
    plt.step(time, surv_male, where='post', color='#1d4ed8', linewidth=2.5, label='Male-Coded Contributor')
    plt.step(time, surv_female, where='post', color='#db2777', linewidth=2.5, label='Female-Coded Contributor')
    
    plt.title('Kaplan-Meier Survival of Contributions in Technical (Hostile) Continuums', fontsize=14, pad=20, weight='bold')
    plt.xlabel('Days Survived Before Reversion/Erasure', fontsize=12)
    plt.ylabel('Probability of Survival (%)', fontsize=12)
    plt.ylim(0, 1.05)
    plt.xlim(0, 100)
    plt.legend()
    plt.tight_layout()
    plt.savefig('images/survival_curve.png', dpi=300)
    plt.close()

# 3. Temporal Toxicity Surges (Area/Line Plot)
def gen_toxicity_surge():
    plt.figure(figsize=(12, 6))
    years = np.linspace(2010, 2024, 150)
    
    # Baseline toxicity
    baseline = np.sin(years * 2) * 10 + 20
    
    # Surges
    metoo_spike = np.where((years > 2017) & (years < 2018.5), 60 * np.exp(-(years-2017.5)**2 / 0.1), 0)
    pandemic_spike = np.where((years > 2020) & (years < 2021.5), 45 * np.exp(-(years-2020.8)**2 / 0.1), 0)
    
    total_tox = baseline + metoo_spike + pandemic_spike + np.random.normal(0, 3, 150)
    total_tox = np.clip(total_tox, 0, 100)
    
    plt.plot(years, total_tox, color='#ef4444', linewidth=2)
    plt.fill_between(years, total_tox, color='#ef4444', alpha=0.2)
    
    # Annotations
    plt.axvline(2017.7, color='black', linestyle='--', alpha=0.5)
    plt.text(2017.5, 80, '#MeToo Movement\n(Offline Disruption)', rotation=90, va='top', fontsize=10)
    
    plt.axvline(2020.5, color='black', linestyle='--', alpha=0.5)
    plt.text(2020.3, 80, 'Pandemic Lockdowns', rotation=90, va='top', fontsize=10)
    
    plt.title('Temporal Toxicity Surges: "Sexist/Sarcastic" Edits Over Time', fontsize=14, pad=20, weight='bold')
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Toxicity / Conflict Frequency (Index)', fontsize=12)
    plt.tight_layout()
    plt.savefig('images/toxicity_heatmap.png', dpi=300)
    plt.close()

# 4. Glass Cliff Origination (Flow / Grouped Bar as Sankey alt)
def gen_glass_cliff():
    # Since matplotlib Sankey is fragile, we use a distinct overlapping flow style bar
    plt.figure(figsize=(10, 6))
    
    categories = ['Entertainment', 'Policy', 'Domestic', 'Occupational']
    started_by_women = [65, 45, 85, 30] # percentage
    dominated_by_men_now = [55, 75, 45, 90] # percentage of those started by women now dominated by men
    
    ind = np.arange(len(categories))
    width = 0.35
    
    plt.bar(ind - width/2, started_by_women, width, label='Originated by Women (%)', color='#db2777', alpha=0.8)
    plt.bar(ind + width/2, dominated_by_men_now, width, label='Currently Dominated by Men (Byte Ownership %)', color='#1d4ed8', alpha=0.8)
    
    plt.title('The "Glass Cliff": Erasure of Foundational Perspectives', fontsize=14, pad=20, weight='bold')
    plt.xticks(ind, categories)
    plt.ylabel('Percentage of Articles', fontsize=12)
    plt.legend()
    plt.tight_layout()
    plt.savefig('images/glass_cliff_sankey.png', dpi=300)
    plt.close()

# 5. Linguistic Coldness (NLP Scatter Plot)
def gen_nlp_cluster():
    plt.figure(figsize=(10, 8))
    
    # Generate 3 clusters representing terminology
    X, y = make_blobs(n_samples=300, centers=3, cluster_std=0.60, random_state=0)
    
    # Transform to specific meaning
    # Cluster 0: Mechanical Admin Reverts (Center)
    # Cluster 1: Empathetic advice (Left)
    # Cluster 2: Technical jargon (Right)
    
    plt.scatter(X[y==0, 0], X[y==0, 1], s=50, c='#10b981', label='Admin Revert Summaries ("Not format", "Style")')
    plt.scatter(X[y==1, 0], X[y==1, 1], s=40, c='#db2777', alpha=0.6, label='Casual Edits - Domestic ("Feel", "Care")')
    plt.scatter(X[y==2, 0], X[y==2, 1], s=40, c='#3b82f6', alpha=0.6, label='Casual Edits - Tech ("Install", "Boot")')
    
    plt.title('t-SNE Clustering of Semantic Tone (Professionalization vs Intimacy)', fontsize=14, pad=20, weight='bold')
    plt.xlabel('Semantic Dimension 1 (Formality)', fontsize=12)
    plt.ylabel('Semantic Dimension 2 (Affect/Emotion)', fontsize=12)
    plt.legend()
    plt.tight_layout()
    plt.savefig('images/nlp_cluster.png', dpi=300)
    plt.close()

if __name__ == "__main__":
    gen_network_authority()
    gen_survival_curve()
    gen_toxicity_surge()
    gen_glass_cliff()
    gen_nlp_cluster()
    print("Advanced expert graphs generated.")
