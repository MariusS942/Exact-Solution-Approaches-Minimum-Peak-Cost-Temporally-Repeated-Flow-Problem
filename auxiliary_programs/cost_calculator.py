import networkx

def calc_cost(Graph: networkx.DiGraph, path: list, theta: int, T: int) -> float:
    """calculates the cost of a given path at time theta

    Args:
        Graph (networkx.DiGraph): given Graph
        path (list): given path
        theta (int): given time point
        T (int): given time horizon

    Returns:
        float: cost of path at time theta
    """

    #total transit time
    tau_path = sum(Graph[path[j]][path[j+1]]['transit'] for j in range(len(path)-1))

    #initialize total cost and accumulated time variable
    total_cost = 0
    time_acc = 0

    #calculating cost up to max end in path of sending flow
    for i in range(len(path)-1):
        v = path[i]
        w = path[i+1]
        transit = Graph[v][w]['transit']
        cost = Graph[v][w]['cost']

        if theta < time_acc + transit:
            remaining = theta - time_acc
            total_cost = total_cost + cost * remaining
            break
            
        else:
            total_cost = total_cost + cost * transit
            time_acc = time_acc + transit
    
    #reinitialize accumulated time variable
    time_acc = 0

    #subtract cost up to beginning in path of sending flow
    for i in range(len(path)-1):
        v = path[i]
        w = path[i+1]
        transit = Graph[v][w]['transit']
        cost = Graph[v][w]['cost']

        if T >= theta + tau_path - time_acc:
            break
        
        else:
            remaining = -1 * (T- theta - tau_path + time_acc)
            total_cost = total_cost - cost * min(transit,remaining)
            time_acc = time_acc + transit

    return total_cost
    

