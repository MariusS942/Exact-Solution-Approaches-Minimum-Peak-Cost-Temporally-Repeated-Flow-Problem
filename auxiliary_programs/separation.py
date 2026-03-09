import networkx
from typing import Literal, Any

from auxiliary_programs.cost_calculator import calc_cost

def separation_c_max(f_sol: dict, paths: list, Graph: networkx.DiGraph, T:int, C_max: float) -> tuple[int | None, Any| Literal[0]] | tuple[None, Literal[0]]:
    """Search for time point theta where the peak cost is higher than the C_Max value

    Args:
        f_sol (dict): dict which orders each index of a path the current solution value 
        paths (list): list of all initialized paths
        Graph (networkx.DiGraph): given Graph
        T (int): Time horizon
        C_max (float): current C_Max value

    Returns:
        tuple[int | None, Any| Literal[0]] | tuple[None, Literal[0]]: If a time point theta is found with peak cost higher than C_Max value return of this time point and the peak cost else None,0
    """

    #initialize best theta and best cost
    best_theta = None
    best_cost = 0

    #search for violation
    for theta in range(T):
        cost = 0
        for i, val in f_sol.items():
            cost += val * calc_cost(Graph, paths[i], theta, T)
        
        if cost - 1e-6 > best_cost:
            best_cost = cost
            best_theta = theta

            #if violation is found break
            if best_cost - 1e-6 > C_max:
                break
    
    #return violation if a violation is found else None,0
    if best_cost - 1e-6 > C_max:
        return best_theta, best_cost
    else: 
        return None, 0
    
def separation_cap(f_sol: dict, paths: list, Graph: networkx.DiGraph) -> tuple | None:
    """Search for an arc with violated capacity

    Args:
        f_sol (dict): dict which orders each index of a path the current solution value 
        paths (list): list of all initialized paths
        Graph (networkx.DiGraph): given Graph

    Returns:
        tuple | None: violated arc if such a arc exists else None
    """

    for v,w in Graph.edges:
        if sum(f_sol[i] for i,_ in f_sol.items() if f_sol[i] is not None and any((paths[i][j],paths[i][j+1]) == (v,w) for j in range(len(paths[i])-1))) > Graph[v][w]['cap']:
            return (v,w)
        
    return None