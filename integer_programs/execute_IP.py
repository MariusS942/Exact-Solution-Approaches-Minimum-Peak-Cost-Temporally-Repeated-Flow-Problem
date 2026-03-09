import networkx
import osmnx
import os
import sys
import random

from T_R_Min_Peak_IP import solve_IP
from T_R_Min_Peak_IP_Row_Callback import solve_IP_Row_Generation_with_Callback
from integer_programs.shortest_capacity_extend_integer import solve_heuristic_IP
from auxiliary_programs.max_flow import get_max_flow_value


def execute_IPs(city: str, origin: str, origin_coordinates: tuple, arrival: str, arrival_coordinates: tuple, Graph: networkx.MultiGraph, T:int, repeats: int, method:str):
    """Runs all LP repeats times and saves all relevant information in .txt files in specific dir

    Args:
        city (str): name of city
        origin (str): name of origin place
        origin_coordinates (tuple): coordinates of origin place
        arrival (str): name of arrival place
        arrival_coordinates (tuple): coordinates of origin place
        Graph (networkx.MultiGraph): given city graph
        T (int): time horizon
        repeats (int): number of repeats
        method (str): name of method
    """
    
    #select target directory
    target_dir = 'enter path'

    #make specific directory
    os.makedirs(fr'{target_dir}/{city}/{origin}_{arrival}', exist_ok=True)

    #calculate start and target node
    s = osmnx.distance.nearest_nodes(Graph, origin_coordinates[0], origin_coordinates[1])
    t = osmnx.distance.nearest_nodes(Graph, arrival_coordinates[0], arrival_coordinates[1])

    #convert to digraph
    H = osmnx.convert.to_digraph(Graph, weight='transit')

    for u,v,data in H.edges(data=True):
        data['cap'] = float(data['cap'])
        data['transit'] = float(data['transit'])
        data['cost'] = float(data['cost'])


    #get max flow value
    v_best = get_max_flow_value(H,s,t,T)

    #repeat number of repeats times
    for i in range(1,repeats+1):


        #open textfile
        sys.stdout = open(fr'{target_dir}/{city}/{origin}_{arrival}/{origin}_{arrival}_{method}.txt', 'w', buffering=1)

        if  method  == 'IP':
            obj_val_LP = solve_IP(H,T,0.8 *v_best,s,t)

        elif method == 'IP_row_call':
            obj_val_LP_Row = solve_IP_Row_Generation_with_Callback(H,T,0.8*v_best,s,t)

        elif method == 'Heu_n':
            obj_val_heu = solve_heuristic_IP(H,T,0.8*v_best,1,s,t)

        elif method == 'Heu_n^2':
            obj_val_heu = solve_heuristic_IP(H,T,0.8*v_best,2,s,t)