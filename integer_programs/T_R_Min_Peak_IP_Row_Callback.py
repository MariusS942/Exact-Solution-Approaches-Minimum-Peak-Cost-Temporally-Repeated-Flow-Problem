from gurobipy import *
import gurobipy
import networkx
import time

from auxiliary_programs.separation import separation_c_max, separation_cap
from auxiliary_programs.cost_calculator import calc_cost

def solve_IP_Row_Generation_with_Callback(Graph: networkx.DiGraph, T: int, v_best: float, s, t) -> float:
    """Solves the MPC TRF problem on a given graph with given time horizon T and minimum flow value v_best via a IP with dynamic Row Generation. Prints the used path with flow rate and total flow and returns the peak costs

    Args:
        Graph (networkx.DiGraph): given Graph
        T (int): time horizon
        v_best (float): minimum flow value
        s (_type_): source node
        t (_type_): sink node

    Returns:
        float: _description_
    """

    def separation_callback(model, where):
        """Callback Method for Constraint Separation: Starts after new MIP Solution is found and search for violated constraints. If some violated constraints are found, it will be added to the model.

        Args:
            model (_type_): Gurobi model
            where (_type_): Callback event
        """
        if where == GRB.Callback.MIPSOL:


            #get latest solution values
            sol = model.cbGetSolution(f_vars)
            C_Max_val = model.cbGetSolution(C_Max)
            f_val = {f_index_path[i]: val for i,val in enumerate(sol) if val > 0}

            #search for violated peak cost constraint
            theta, total_cost = separation_c_max(f_val,paths,Graph,T,C_Max_val)

            #if a violated peak cost constraint is found, add it
            if total_cost - 1e-6 >  C_Max_val:
                expr_c_max = gurobipy.LinExpr()
                for i,path in enumerate(paths):
                    if f[i] is not None:
                        expr_c_max += f[i] *calc_cost(Graph,path,theta,T)
                model.cbLazy(expr_c_max <= C_Max)


            #search for a violated capacity constraint
            invalid_edge = separation_cap(f_val,paths,Graph)

            #if there exists a violated capacity constraint, add it
            if invalid_edge is not None:
                expr_invalid_edge = gurobipy.LinExpr()
                for i, path in enumerate(paths):
                    if f[i] is not None and any((path[j],path[j+1]) == (invalid_edge[0],invalid_edge[1]) for j in range(len(path)-1)):
                        expr_invalid_edge += f[i]
                model.cbLazy(expr_invalid_edge <= Graph[invalid_edge[0]][invalid_edge[1]]['cap'])

    start_time_all = time.time()
    model = Model('Min_Peak_Temporally_Repeated_LP_Row_Generation')

    start_time_calc_paths = time.time()
    paths = list(networkx.all_simple_paths(Graph,source= s, target= t))
    print('Number of paths:', len(paths))
    end_time_calc_paths = time.time()
    print('Runtime Calculation Paths:', end_time_calc_paths-start_time_calc_paths)

    start_time_initialization = time.time()
    #lists for getting latest solution values
    f_vars = []
    f_index_path = []

    #one variable for each path representing the flow rates
    f= {}
    for i, path in enumerate(paths):
        transit_time = sum(Graph[path[j]][path[j+1]]['transit'] for j in range(len(path)-1))
        if transit_time <= T-1:
            f[i] = model.addVar(vtype= GRB.INTEGER, name =f'f_[{i}]')
            f_vars.append(f[i])
            f_index_path.append(i)
        else:
            f[i] = None

    #variable for the max peak cost
    C_Max = model.addVar(vtype= GRB.INTEGER)

    #constraint: total flow at least v_max (other constraints would dynamically be added )
    model.addConstr(quicksum(f[i] * (T-quicksum(Graph[path[j]][path[j+1]]['transit'] for j in range(len(path)-1))) for i,path in enumerate(paths) if f[i] is not None) >= v_best)

    #objective: minimize peak cost
    model.setObjective(C_Max,GRB.MINIMIZE)
    
    end_time_initialization = time.time()
    print('Runtime initialization model:', end_time_initialization - start_time_initialization)


    #disable default output
    model.setParam('OutputFlag', 0)

    #allowing Lazy Constraints
    model.Params.LazyConstraints = 1

    start_time_optimization = time.time()

    #optimize model with dynamic row generation in Callback method
    model.optimize(separation_callback)

    end_time_optimization = time.time()
    print('Runtime model optimization:', end_time_optimization - start_time_optimization)
    end_time_all = time.time()
    print('Runtime IP Row Generation Overall:', end_time_all-start_time_all)

    if model.Status != GRB.INFEASIBLE:
        print('Peak-Cost IP Row Generation using callback:', model.ObjVal)
        for i,var in f.items():
            if var is not None and var.X >0:
                transit_time = sum(Graph[paths[i][j]][paths[i][j+1]]['transit'] for j in range(len(paths[i])-1))
                total_flow = var.X * (T-transit_time)
                print(f'Path {paths[i]}: rate = {var.X}, total_flow = {total_flow}')
        return model.ObjVal
    else:
        print('Peak-Cost IP Row Generation: INFEASIBLE')


    

    