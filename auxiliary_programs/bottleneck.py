import networkx
import numpy
from typing import Tuple

def bottleneck_weight(G: networkx.DiGraph, s,t) -> float:
    """compute the largest bottleneck capacity of a s-t path in G

    Args:
        G (networkx.DiGraph): given Digraph
        s (_type_): start node
        t (_type_): target node

    Returns:
        float: largest bottleneck capacity of a s-t path in G
    """
    F = G.edges()
    capacities = [G[v][w]['cap'] for v,w in F]
    while len(F) > 1:
        capacities = {G[v][w]['cap'] for v,w in F}
        if len(set(capacities)) ==1:
            return next(iter(capacities))
        
        median = numpy.median(list(capacities))

        H = G.copy()
        for v,w in G.edges:
            if G[v][w]['cap'] < median:
                H.remove_edge(v,w)
        
        if networkx.has_path(H,s,t):
            F = [[v,w] for v,w in F if G[v][w]['cap'] >= median]
        else:
            F = [[v,w] for v,w in F if G[v][w]['cap'] < median]

    return G[F[0][0]][F[0][1]]['cap']


def bottleneck_path(G: networkx.DiGraph,s,t) -> Tuple[list, float]:
    """computes the s-t path with largest bottleneck capacity

    Args:
        G (networkx.DiGraph): Digraph
        s (_type_): start node
        t (_type_): target node

    Returns:
        Tuple[list, float]: s-t path with largest bottleneck capacity and its bottleneck capacity
    """
    bottleneck = bottleneck_weight(G,s,t)
    H = G.copy()
    if bottleneck == 0:
        path = []
        return path, bottleneck
    else:
        for v,w in G.edges:
            if G[v][w]['cap'] < bottleneck:
                H.remove_edge(v,w)
    
    try:
        path = networkx.dijkstra_path(H,s,t)
    except networkx.NetworkXNoPath:
        path = []
    return path, bottleneck