import networkx
import os
import sys

from linear_programs.T_R_Min_Peak_LP import solve_LP
from linear_programs.T_R_Min_Peak_LP_Row_Generation import solve_LP_Row_Generation
from linear_programs.shortest_capacity_extend_heuristic import solve_heuristic
from auxiliary_programs.max_flow import get_max_flow_value

def execute_LPs(file: str, Graph: networkx.MultiGraph, T:int, repeats: int, method:str):
    """Runs all LP repeats times and saves all relevant information in .txt files in specific dir

    Args:
        file (str): name of file from which we derive the graph
        Graph (networkx.MultiGraph): given SP graph
        T (int): time horizon
        repeats (int): number of repeats
        method (str): name of method
    """
    
    #select target directory
    target_dir = 'enter path'

    #make specific directory
    os.makedirs(fr'{target_dir}/{file}', exist_ok=True)

    #get max flow value
    v_best = get_max_flow_value(Graph,'s','t',T)

    #repeat number of repeats times
    for i in range(1,repeats+1):


        #open textfile
        sys.stdout = open(fr'{target_dir}/{file}/{file}_{method}.txt', 'w', buffering=1)

        #start LPs
        if  method  == 'LP':
            obj_val_LP = solve_LP(Graph,T,0.8 *v_best,'s','t')

        elif method == 'LP_row':
            obj_val_LP_Row = solve_LP_Row_Generation(Graph,T,0.8*v_best,'s','t')

        elif method == 'Heu_n':
            obj_val_heu_n = solve_heuristic(Graph,T,0.8*v_best, 1 ,'s','t')

        elif method == 'Heu_n^2':
            obj_val_heu_n2 = solve_heuristic(Graph,T,0.8*v_best, 2, 's','t')