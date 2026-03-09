import networkx
import ast

def rebuild_graph(document: str) -> networkx.DiGraph:
    """build digraph by the edge and node information given by document.txt

    Args:
        document (str): name of document

    Returns:
        networkx.DiGraph: builded DiGraph
    """
    G = networkx.DiGraph()
    with open(fr'instances_series_parallel/{document}.txt', 'r') as file:
        for line in file:
            if line.startswith("nodes"):
                nodes = ast.literal_eval(line.split("=", 1)[1].strip())

            elif line.startswith("edges"):
                edges = ast.literal_eval(line.split("=",1)[1].strip())
        G.add_edges_from(edges)
    return G
        
