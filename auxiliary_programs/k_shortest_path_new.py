"""based on the idea of an k-shortest simple path algorithm of Kurz and Mutzel"""

import heapq
import networkx
from typing import Optional, Tuple, Any

class Path:
    def __init__(self, lost: float, parent = None, sidetrack = [], simple = True, prefix = [], Tree = None, prefixcost = 0):
        """initialization of path class

        Args:
            lost (float): length of the path
            parent (_type_, optional): parent of the path. Defaults to None.
            sidetrack (list, optional): list of used sidetrack. Defaults to [].
            simple (bool, optional): boolean if path is simple. Defaults to True.
            prefix (list, optional): prefix path. Defaults to [].
            Tree (_type_, optional): modified shortest path tree. Defaults to None.
            prefixcost (float, optional): cost of prefix. Defaults to 0.
        """
        self.lost = lost 
        self.parent = parent 
        self.sidetrack = sidetrack 
        self.simple = simple 
        self.prefix = prefix 
        self.tree = Tree 
        self.prefixcost = prefixcost 

    def __lt__(self,other):
        """compare two paths by their total length

        Args:
            other (_type_): second path

        Returns:
            _type_: boolean if path length is smaller to compared path length
        """
        return self.lost < other.lost
    
#build class local heaps
class local_heap:
    """local heap class
    """
    def __init__(self,parent):
        """initialization of path class

        Args:
            parent (_type_): parent of all paths in the local heap
        """
        self.parent = parent #parent of all paths in this heap
        self.heap = [] #initial heap

    def add_paths(self,Pp,blocks,dist,paths, G:networkx.DiGraph, sidetracks, costs, prefix_old, prefix_cost_old, s):
        """add paths to heap

        Args:
            Pp (_type_): list of sidetracks to get new paths
            blocks (_type_): block description to check whether the new path is simple
            dist (_type_): lengths in shortest path tree
            paths (_type_): paths in shortest path tree
            G (networkx.DiGraph): graph on which to operate
            sidetracks (_type_): old list of sidetracks
            costs (_type_): old costs
            prefix_old (_type_): previous prefix
            prefix_cost_old (_type_): previous prefix costs
            s (_type_): start node

        Returns:
            _type_: modified heap with new paths
        """
        for vi, w in Pp:

            #define empty list and integer for adding new arcs to prefix
            prefix_extension = []
            prefixcost_extension = 0

            #if we have no prefix than our addition to prefix start with the source node s else with the end_node of the last added sidetrack
            if prefix_old == []:
                start_prefix = s
            else:
                start_prefix = sidetracks[-1][1]

            #add all edges along the shortest path from start node of our prefix extension to start node of the sidetrack along our tree
            for v in paths[start_prefix][::-1]:
                prefix_extension.append(v)
                if v == vi:
                    break


            #compute total transit of prefix extension
            for i in range(len(prefix_extension)-1):
                prefixcost_extension = prefixcost_extension + G[prefix_extension[i]][prefix_extension[i+1]]['transit']

            #check wether new path by added sidetrack is simple and added to heap with this information
            if blocks[w] > blocks[vi]:

                #copy sidetracks and add the inserted sidetrack
                new_sidetracks = sidetracks.copy()
                new_sidetracks.append((vi,w))

                #add it to heap
                heapq.heappush(self.heap, Path(lost=(costs+G[vi][w]['transit'] - dist[vi]+ dist[w]), parent= self.parent, sidetrack=new_sidetracks, simple=True, prefix= prefix_old+prefix_extension, Tree=(dist,paths), prefixcost=prefix_cost_old+prefixcost_extension))
            
            else:
                #copy sidetracks and add the inserted sidetrack
                new_sidetracks = sidetracks.copy()
                new_sidetracks.append((vi,w))

                #add it to heap
                heapq.heappush(self.heap, Path(lost=(costs+G[vi][w]['transit'] - dist[vi]+ dist[w]), parent= self.parent, sidetrack=new_sidetracks, simple=False, prefix= prefix_old+prefix_extension, Tree=(dist,paths), prefixcost=prefix_cost_old+prefixcost_extension))

    def reuse_path(self, dist, paths,sidetracks,costs,prefix,prefixcost_old):
        """add path after it is modified to a simple path

        Args:
            dist (_type_): distances in shortest path tree
            paths (_type_): paths in shortest path tree
            sidetracks (_type_): list of sidetracks
            costs (_type_): overall cost of path
            prefix (_type_): prefix of path
            prefixcost_old (_type_): prefix cost of path
        """
        #reuse path if it is modified from not simple to simple
        heapq.heappush(self.heap, Path(lost=costs, parent=self.parent, sidetrack=sidetracks, simple=True, prefix=prefix, Tree=(dist,paths), prefixcost=prefixcost_old))

    def pop(self) -> bool | Path:
        """delete best path from heap if heap is not empty

        Returns:
            bool | Path: returns root node of heap if heap is not empty, else None
        """
        
        if not self.heap:
            return None
        return heapq.heappop(self.heap)
    
class Global_heap:
    """Global heap to work on
    """
    def __init__(self):
        """initialize empty heap
        """
        self.heap = []

    def insert_local_heap(self, local:local_heap):
        """insert root node of a local heap

        Args:
            local (local_heap): local heap which root node should be added to global node
        """

        #get root node
        root = local.pop()
        #if local heap is not empty push the root node, its costs and the considered local heap to global heap
        if root:
            heapq.heappush(self.heap, (root.lost, root, local))


    def extract_min(self) -> Tuple[Optional[Path], Optional[local_heap]]:
        """compute the next best candidate solution

        Returns:
            tuple: (path,local_heap) if local heap is not empty, else (None,None)
        """
        

        #if global heap is already empty stop by return None,None
        if not self.heap:
            return None,None
        
        #get best candidate path and return it and its local heap
        _, path, local = heapq.heappop(self.heap)
        return path,local
    

    def reinsert_local(self, local:local_heap):
        """reinsert new root of local heap to the global heap after extracting its old root as best candidate solution

        Args:
            local (local_heap): local heap to work on
        """
        
        #get new root
        next_candidate = local.pop()
        

        #if local heap is not empty add root node to global heap
        if next_candidate:
            heapq.heappush(self.heap, (next_candidate.lost, next_candidate,local))


def compute_blocks(T: dict, path_nodes: list) -> dict:
    """computes a dictionary with ids to sort which node is in which block; important for checking wether a path is simple or not

    Args:
        T (dict): shortest path tree
        path_nodes (list): path given as a list of nodes

    Returns:
        dict: dictionary which sort any vertex to its block
    """

    #we need for computation the list of arcs of the path
    path_edges = [(path_nodes[i], path_nodes[i+1]) for i in range(len(path_nodes)-1)]
    blocked_edges = set(path_edges)
    
    #initialize block dictionary
    block = {}

    #current block id
    current_block = 0

    #add all nodes to the current block if it is reachable from vi and uses not an arc of the path
    for vi in path_nodes:
        stack = [vi]
        while stack:
            u = stack.pop()
            if u in block:
                continue
            block[u] = current_block
            for w in T.get(u, []):
                if (w,u) in blocked_edges:
                    continue
                stack.append(w)
        current_block = current_block + 1
    return block

def get_sp_tree_for_for_prefix(prefix: list, SP_tree_cache:dict,G:networkx.DiGraph,t) -> Tuple[Optional[dict], Optional[dict]]:
    """build new shortest path tree without prefix

    Args:
        prefix (list): prefix nodes
        SP_tree_cache (dict): all SP trees in cache
        G (networkx.DiGraph): Graph to work on 
        t (_type_): target node

    Returns:
        Tuple[dict, dict]: tuple of shortest distances of new tree and shortest paths of new tree except no tree exists then return None, None
    """

    key = tuple(prefix)
    #if this tree has been already computed return it
    if key in SP_tree_cache:
        return SP_tree_cache[key]


    #get copy of graph without prefix nodes
    remove_nodes = set(prefix)
    allowed_nodes = [n for n in G.nodes() if n not in remove_nodes]
    G_sub = G.subgraph(allowed_nodes).copy()

    try:
        dist_sub, paths_sub = networkx.single_source_dijkstra(G_sub.reverse(), t, weight='transit')
    except Exception:
        SP_tree_cache[key] = (None,None)
        return None,None
    
    SP_tree_cache[key] = (dist_sub,paths_sub)
    return dist_sub,paths_sub

def extract_solution(paths: dict, sidetrack: list,prefix: list) -> list:
    """build new path

    Args:
        paths (dict): paths of shortest path tree
        sidetrack (list): list of sidetracks
        prefix (list): prefix

    Returns:
        list: path as a list of nodes
    """

    new_path = prefix.copy()

    for vi in paths[sidetrack[-1][1]][::-1]:
        new_path.append(vi)

    return new_path
    




def compute_k_shortest(G: networkx.DiGraph, s, t, K:int) -> list:
    """computes K simple shortest paths 

    Args:
        G (networkx.DiGraph): network to work on
        s (_type_): start node
        t (_type_): target node
        K (int): number of simple shortest paths to compute

    Returns:
        list: list of tuple(length of path, path)
    """

    #compute shortest path tree on reverse graph (need shortest path from every node to the target node)
    dist, paths = networkx.single_source_dijkstra(G.reverse(), t, weight='transit')

    #if there is no s-t path in G return empty list
    if s not in dist:
        return []
    
    #initialize solution list and output list
    sol = [(dist[s], paths[s][::-1], [], [], (dist,paths), 0)]
    output = [(dist[s], paths[s][::-1])]

    #initialize global heap
    global_heap = Global_heap()

    #initialize shortest path tree cache
    SP_tree_cache = {}

    for transit, p_nodes, sidetracks, pref, SP_tree, prefix_cost in sol:

        (dist,paths) = SP_tree

        #compute predecessor on shortest path (for shortest path tree)
        parent = {v: -1 for v in G.nodes()}
        for v in G.nodes:
            if v in paths and len(paths[v])>1:
                parent[v] = paths[v][-2]

        #build shortest path tree
        T = {v: [] for v in G.nodes}
        for v in G.nodes:
            if parent[v] != -1:
                T[parent[v]].append(v)

        #compute blocks
        blocks = compute_blocks(T,p_nodes)

        #initialize local heap with parent as actual path
        localheap = local_heap(parent=p_nodes)


        #create suffix
        if sidetracks == []:
            suffix = paths[s][::-1]
        else:
            last_sidetrack = sidetracks[-1]
            suffix = paths[last_sidetrack[1]][::-1]


        #initialize list of new potential paths
        Pp = []

        #add all possible new sidetracks to Pp
        for vi in suffix:
            if vi != t:
                for w in G.successors(vi):
                    if (vi,w) != (paths[vi][-1],paths[vi][-2]) and w in dist:
                        Pp.append((vi,w))

        
        #add new paths to local heap
        localheap.add_paths(Pp,blocks,dist,paths,G,sidetracks,transit,pref,prefix_cost,s)

        #add root node to global heap
        global_heap.insert_local_heap(localheap)

        #get best candidate solution
        path, local = global_heap.extract_min()

        new_simple_path_found = False

        #iterate as long as a new simple shortest path if found 
        while new_simple_path_found != True:
            
            #all simple paths already found
            if path == None:
                return output
            
            if path.simple == False:

                new_dist, new_paths = get_sp_tree_for_for_prefix(path.prefix, SP_tree_cache, G, t)

                #if a new tree exist modify path and reinsert in local and global heap
                if new_dist is not None and path.sidetrack[-1][1] in new_dist:
                    costs = path.prefixcost + new_dist[path.sidetrack[-1][1]] + G[path.sidetrack[-1][0]][path.sidetrack[-1][1]]['transit']
                    local.reuse_path(new_dist,new_paths,path.sidetrack, costs, path.prefix,path.prefixcost)

                global_heap.reinsert_local(local)
                path,local = global_heap.extract_min()
                paths = new_paths.copy()
            
            else:
                global_heap.reinsert_local(local)
                new_simple_path_found = True
        
        #add best new path to solutions and output
        new_path = extract_solution(path.tree[1], path.sidetrack,path.prefix)
        sol.append((path.lost, new_path, path.sidetrack, path.prefix,path.tree,path.prefixcost))
        output.append((path.lost, new_path))
        if len(sol) >= K:
            return output



