from gurobipy import *
import networkx
import time



from auxiliary_programs.k_shortest_path_new import compute_k_shortest
from auxiliary_programs.cost_calculator import calc_cost
from auxiliary_programs.bottleneck import bottleneck_path


def add_Var(model, f, paths: list, Graph: networkx.DiGraph, new_path: list, T: int, capacity, max_flow, peak):
    """add new path variable to given model

    Args:
        model (_type_): given model
        f (_type_): path variables representing the flow rates
        paths (list): list of all already computed paths
        Graph (networkx.DiGraph): given Graph
        new_path (list): path that will be added
        T (int): Time horizon
        capacity (_type_): capacity constraints
        max_flow (_type_): max flow constraints
        peak (_type_): peak-cost constraints
    """

    new_index = len(paths)
    transit_time = sum(Graph[new_path[j]][new_path[j+1]]['transit'] for j in range(len(new_path)-1))

    #only add path variable if path is not too long
    if transit_time <= T-1:
        f[new_index] = model.addVar(column = Column(
                                                    list(1 if any ((new_path[j],new_path[j+1]) == (v,w) for j in range(len(new_path)-1)) else 0 for v,w in Graph.edges) + [T-sum(Graph[new_path[j]][new_path[j+1]]['transit'] for j in range(len(new_path)-1))] + list(calc_cost(Graph,new_path,theta,T) for theta in range(T))
                                                    
                                                    , list(capacity[(v,w)] for v,w in Graph.edges) + [max_flow] + list(peak[theta] for theta in range(T))))
        paths.append(new_path)
    else:
        f[new_index] = None
    return 0


def solve_heuristic(Graph: networkx.DiGraph, T: int, v_best: float, exponent:int , s, t) -> float:
    """Heuristic to solve the MPC TRF problem on a given graph with given time horizon T and minimum flow value v_best. Only uses n paths with the smallest total transit time. If this paths are not necessary to get a solution the heuristic adds paths with the highest bottleneck capacity. Prints the used paths with flow rates and total flow and returns the peak costs

    Args:
        Graph (networkx.DiGraph): given Graph
        T (int): time horizon
        v_best (float): minimum flow value
        exponent (int): number of exponent for number of used paths
        s (_type_): source node
        t (_type_): sink node

    Returns:
        float: computed minimum peak cost
    """
    start_time_all = time.time()
    model = Model('Shortest_Path_Capacity_Extend_heuristic')
    
    n = Graph.number_of_nodes()

    #compute the simple paths
    start_time_calc_paths = time.time()
    simple_paths = compute_k_shortest(Graph,s,t,n**exponent)
    paths = [new_path for _,new_path in  simple_paths]
    print('Number of paths:',len(paths))
    end_time_calc_paths = time.time()
    print('Used exponent:', exponent)
    print('Runtime Calculation Paths:', end_time_calc_paths-start_time_calc_paths)

    start_time_initialization = time.time()
    #one variable for each path representing the flow rates
    f = {}
    for i,path in enumerate(paths):
        transit_time = sum(Graph[path[j]][path[j+1]]['transit'] for j in range(len(path)-1))
        if transit_time <= T-1:
            f[i] = model.addVar(vtype=GRB.CONTINUOUS, name=f'f_[{i}]')
        else:
            f[i] = None

    #variable for the max peak cost
    C_Max = model.addVar(vtype=GRB.CONTINUOUS)

    #constraints
    #constraint no. 1: capacity constraint
    capacity = model.addConstrs(quicksum(f[i] for i,path in enumerate(paths) if f[i] is not None and any((path[j],path[j+1]) == (v,w) for j in range(len(path)-1))) <= Graph[v][w]['cap'] for v,w in Graph.edges)

    #constraint no.2: flow must be at least v_best
    max_flow = model.addConstr(quicksum(f[i]*(T-quicksum(Graph[path[j]][path[j+1]]['transit'] for j in range(len(path)-1))) for i,path in enumerate(paths) if f[i] is not None) >= v_best)

    #constraint no.3: Peak-Cost
    peak = model.addConstrs(quicksum(f[i]*calc_cost(Graph,path,theta,T) for i,path in enumerate(paths) if f[i] is not None) <= C_Max for theta in range(T))

    #objective: Minimize Peak-Cost
    model.setObjective(C_Max, GRB.MINIMIZE)

    end_time_initialization = time.time()
    print('Runtime initialization model:', end_time_initialization - start_time_initialization)

    #disable any default output
    model.setParam('OutputFlag', 0)

    #copy Graph for computing potential bottleneck paths
    H = Graph.copy()
    
    #search variable to end the coming while loop
    marker = True

    start_time_optimization = time.time()
    while marker:

        #solve model
        model.optimize()

        #if solution found stop
        if model.Status != GRB. INFEASIBLE:
            marker = False

        #else add bottleneck path
        else:
            new_path, bottleneck_cap = bottleneck_path(H,s,t)

            #if no new path found: model infeasible
            if new_path == []:
                break

            #add new variable
            if new_path not in paths:
                add_Var(model,f,paths,Graph,new_path,T,capacity,max_flow,peak)

            
            #modify auxiliary Graph to compute new bottleneck paths
            for j in range(len(new_path)-1):
                H[new_path[j]][new_path[j+1]]['cap'] = H[new_path[j]][new_path[j+1]]['cap'] - bottleneck_cap
    end_time_optimization = time.time()
    print('Runtime model optimization:', end_time_optimization - start_time_optimization)
    end_time_all = time.time()
    print('Runtime Heuristic Overall:', end_time_all-start_time_all)

    if model.Status != GRB.INFEASIBLE:
        print('Peak-Cost Heuristic:', model.ObjVal)
        for i,var in f.items():
            if var is not None and var.X >0:
                transit_time = sum(Graph[paths[i][j]][paths[i][j+1]]['transit'] for j in range(len(paths[i])-1))
                total_flow = var.X * (T-transit_time)
                print(f'Path {paths[i]}: rate = {var.X}, total_flow = {total_flow}')
        return model.ObjVal
    else:
        print('Peak-Cost Heuristic: INFEASIBLE')