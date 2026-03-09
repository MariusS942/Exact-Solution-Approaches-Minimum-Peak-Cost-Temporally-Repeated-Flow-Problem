This repository provides all instances and code used for the computational studies of the master's thesis *Minimum-Peak-Cost Temporally Repeated Flows: Complexity and Exact Solution Approaches* submitted to the Chair of Combinatorial Optimization (RWTH Aachen University) by Marius Schieren.

For the computational study, two different sets of instances were used: real street network instances and randomly generated series-parallel instances.

The first set of 150 test instances was generated from five different street networks derived from OpenStreetMap (©OpenStreetMap contributors,
available under the Open Database License - ODbL) data. The transit times of arcs were computed as rounded driving times for the corresponding street segments and lie in the interval [1,100]; integer capacities and costs were generated uniformly at random from [1,10].
The networks contain between 80 and 150 nodes and between 500 and 50,000 (s,t)-paths.

Each network is saved in a file `<name_of_network>.graphhml`, which also includes all arc capacities, costs, and transit times. For each network, a corresponding file `<name_of_network>.txt` is provided. Each line of this file consists of:
1. the name of the source node, 
2. the x- and y-coordinates of the source node,
3. the name of the sink node,
4. the x- and y-coordinates of the sink node, and 
5. the coordinates of the bounding box to retrieve the network via the OSM bounding box function.

To load the networks, only the `.graphhml` files are needed. To use the networks without the arc capacities, costs, and transit times, the coordinates of the bounding box are provided.  

The second instance set of 50 test instances is randomly generated series-parallel networks. The integer transit time, capacity, and cost of each arc is generated uniformly at random from [1,10].
The networks contain 102 nodes and between 120 and 620,000 (s,t)-paths.

To load the networks, a specialized parser (`parse_SP.py`) is included with the repository. The parser takes the instance number as input and generates a NetworkX DiGraph. 

Each instance can also be used for other flow-over-time problems.

Besides instances, this repository also includes the source code used in the described master's thesis. In the computational study, the runtimes of four methods are analyzed: default LP, dynamic LP, and greedy heuristic using |V(G)| or |V(G)|^2 paths. All methods were also tested using integrality requirements. The methods are stored in the directories linear_programs or integer_programs. The file `T_R_Min_Peak_LP.py` provides the source code for the default LP. The file `T_R_Min_Peak_LP_Row_Generation.py` includes the dynamic LP, and `shortest_capacity_extend_heuristic.py` contains the LP heuristic. The file `T_R_Min_Peak_IP.py` provides the source code for the default IP. The file `T_R_Min_Peak_IP_Row_Callback.py` contains the dynamic IP, and `shortest_capacity_extend_heuristic_integer.py` contains the IP heuristic.

To repeat the computation of a specific instance, the `execute_job_<instance set + integer/linear>_slurm.py` files can be used. Each computation requires the method, the task ID, and, if applicable, the city name for a city instance. For example, to run the computation using the IP heuristic with |V(G)|^2 paths on the city instance "Burtscheid Sankt_Michael Marienhospital", use the command: `python -m Computational_Study.slurm.execute_job_city_IP_slurm --city Burtscheid --task_id 11 --method Heu_n^2`.

The source code was implemented using `Python 3.12.9` and `Gurobi 12.0.0`.