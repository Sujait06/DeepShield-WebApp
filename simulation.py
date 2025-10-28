import networkx as nx
import random
from typing import List, Dict

def build_interaction_graph(nodes: List[Dict]):
    G = nx.DiGraph()
    for i, n in enumerate(nodes):
        content_id = n['id']
        G.add_node(content_id, type='content', score=n.get('score',0))
        for j in range(3):
            acc = f'acc_{i}_{j}'
            G.add_node(acc, type='account', credibility=random.uniform(0,1))
            G.add_edge(content_id, acc)
            if random.random() < 0.5 and len(nodes)>1:
                other = f'acc_{(i+1)%len(nodes)}_{random.randint(0,2)}'
                G.add_edge(acc, other)
    return G

def simulate_propagation(G, seed_nodes: List[str], steps: int = 5):
    infected = set(seed_nodes)
    newly = set(seed_nodes)
    timeline = []
    for t in range(steps):
        next_new = set()
        for node in newly:
            for nbr in G.successors(node):
                cred = G.nodes[nbr].get('credibility', 0.5)
                p = 0.2 + 0.6 * (1 - cred)
                if random.random() < p:
                    next_new.add(nbr)
        newly = next_new - infected
        infected |= newly
        timeline.append({'step': t, 'new': list(newly), 'total': len(infected)})
    return {'timeline': timeline, 'reach': len(infected), 'infected_nodes': list(infected)}
