from gurobipy import *
from auxiliary_programs.cost_calculator import calc_cost
import networkx
import time

def solve_IP(Graph: networkx.DiGraph, T:int, v_best:float, s,t) -> float:
    """Solves the MPC TRF problem on a given graph with given time horizon T and minimum flow value v_best via a IP. Prints the used path with flow rate and total flow and returns the peak costs

    Args:
        Graph (networkx.DiGraph): given Graph
        T (int): time horizon
        v_best (float): minimum flow value
        s (_type_): source node
        t (_type_): sink node

    Returns:
        float: minimum peak cost
    """

    start_time_all = time.time()
    model = Model("Min_Peak_Temporally_Repeated_LP")

    #calculate each possible simple s-t path
    start_time_calc_paths = time.time()
    paths = list(networkx.all_simple_paths(Graph,source= s, target= t))
    print('Number of paths:', len(paths))
    end_time_calc_paths = time.time()
    print('Runtime Calculation Paths:', end_time_calc_paths-start_time_calc_paths)
    
    start_time_initialization = time.time()
    #one variable for each path representing the flow rate
    f = {}
    for i, path in enumerate(paths):
        transit_time = sum(Graph[path[j]][path[j+1]]['transit'] for j in range(len(path)-1))
        if transit_time <= T-1:
            f[i] = model.addVar(vtype= GRB.INTEGER, name=f'f_[{i}]')
        else:
            f[i] = None

    #variable for the max peak cost
    C_Max = model.addVar(vtype= GRB.INTEGER)

    #constraints:
    
    #constraint no.1: capacity constraint
    for v,w in Graph.edges:
        model.addConstr(quicksum(f[i] for i,path in enumerate(paths) if f[i] is not None and any((path[j],path[j+1]) == (v,w) for j in range(len(path)-1))) <= Graph[v][w]['cap'], name=f'cap_[{v,w}]')

    #constraint no.2: total flow at least v_max
    model.addConstr(quicksum(f[i]* (T-quicksum(Graph[path[j]][path[j+1]]['transit'] for j in range(len(path)-1))) for i,path in enumerate(paths) if f[i] is not None) >= v_best, name=f'flow')

    #constraint no.3: max peak cost
    for theta in range(T):
        model.addConstr(quicksum(f[i] * calc_cost(Graph, path,theta, T) for i,path in enumerate(paths) if f[i] is not None) <= C_Max, name=f'Peak_cost_{theta}')
    
    #objective minimize peak cost
    model.setObjective(C_Max, GRB.MINIMIZE)

    end_time_initialization = time.time()
    print('Runtime initialization model:', end_time_initialization - start_time_initialization)


    #disable default output
    model.setParam('OutputFlag',0)

    start_time_optimization = time.time()
    model.optimize()
    end_time_optimization = time.time()
    print('Runtime model optimization:', end_time_optimization - start_time_optimization)
    end_time_all = time.time()
    print('Runtime IP Overall:', end_time_all-start_time_all)

    if model.Status != GRB.INFEASIBLE:
        print('Peak-Cost IP:', model.ObjVal)
        for i,var in f.items():
            if var is not None and var.X >0:
                transit_time = sum(Graph[paths[i][j]][paths[i][j+1]]['transit'] for j in range(len(paths[i])-1))
                total_flow = var.X * (T-transit_time)
                print(f'Path {paths[i]}: rate = {var.X}, total_flow = {total_flow}')
        return model.ObjVal
    else:
        print('Peak-Cost IP: INFEASIBLE')