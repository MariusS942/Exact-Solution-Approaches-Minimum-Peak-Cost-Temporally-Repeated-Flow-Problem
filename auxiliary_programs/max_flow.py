import networkx

def get_max_flow_value(G: networkx.DiGraph, source, sink, T: int) -> float:
    """compute maximum flow value of given network

    Args:
        G (networkx.DiGraph): given Graph
        source (_type_): given source node
        sink (_type_): given sink node
        T (int): time horizon

    Returns:
        float: max flow value
    """

    G.add_nodes_from(['auxiliary'])
    G.add_edges_from([('auxiliary',source)])
    G.add_edges_from([(sink, 'auxiliary', {'transit': -T})])

    flow_value = networkx.min_cost_flow_cost(G, demand='NONE', capacity='cap', weight='transit')

    G.remove_nodes_from(['auxiliary'])

    return -flow_value