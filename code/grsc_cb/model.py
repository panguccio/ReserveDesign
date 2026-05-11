import gurobipy as gb
import networkx as nx
from instance import GRSC_CB_Instance
from partial_solution import PartialSolution
import random
import time
import igraph as ig
from reserve_graph import FlowGraph
import heapq
import numpy as np

INF = 1e9  # large constant
EPS = 1e-6  # small constant


class GRSC_CB_Model:
    """
    Complete mathematical model for the GRSC-CB (Generalized Reserve Set Covering problem with Connectivity and Buffer constraints).
    
    The model:
        * selects land parcels to be included in the reserve
        * determines which will be in the core, which in the buffer zones
        * ensures a certain level of protection for each species
        * while minimizing cost of land selection
    
    This class also:
        * implements separation algorithms for the exponential number of constraints for granting connectivity
        * implements a construction heuristic and a primal heuristic to find good feasible solutions to be injected in the MIP solver
    
    Flags:
        B -> enable buffer constraints
        C -> enable connectivity constraints
    """

    def __init__(self, instance: GRSC_CB_Instance, B=True, C=True, seed=None, output_flag=False):

        self.instance = instance
        self.model = gb.Model("GRSC-CB")
        self.digraph = FlowGraph(nodes=self.instance.V, edges=self.instance.E)

        if seed is not None: 
            random.seed(seed)
            self.model.Params.Seed = seed   # set seed for reproducibility
            self.model.Params.Threads = 1  

        # allow lazy constraints to be added by the callback function
        self.model.Params.LazyConstraints = 1

        self.model.setParam('OutputFlag', int(output_flag))

        # VARIABLES

        # land parcels in the reserve
        self.x = self.model.addVars(instance.V, vtype=gb.GRB.BINARY, name="x")

        # core parcels
        self.z = self.model.addVars(instance.V, vtype=gb.GRB.BINARY, name="z")

        # protection of species
        self.u = self.model.addVars(instance.S, vtype=gb.GRB.BINARY, name="u")

        # r-arc-node separators
        self.y = self.model.addVars(instance.V, vtype=gb.GRB.BINARY, name="y")

        # OBJECTIVE FUNCTION: minimize the cost of selected land parcels
        self.model.setObjective(gb.quicksum(instance.c[i] * self.x[i] for i in instance.V), gb.GRB.MINIMIZE)

        # GENERAL CONSTRAINTS

        # suitability quota constraints for S1 and S2

        for s in instance.S_1:
            self.model.addConstr(
                gb.quicksum(instance.w[(i, s)] * self.z[i] for i in instance.v_s(s)) >= instance.lambda_s[s] * self.u[
                    s],
                name=f"S1-SQ-{s}")

        for s in instance.S_2:
            self.model.addConstr(
                gb.quicksum(instance.w[(i, s)] * self.x[i] for i in instance.v_s(s)) >= instance.lambda_s[s] * self.u[
                    s],
                name=f"S2-SQ-{s}")

        # protection constraints for S1 and S2

        self.model.addConstr(
            gb.quicksum(self.u[s] for s in instance.S_1) >= instance.P_1,
            name="S1-PROTECT")

        self.model.addConstr(
            gb.quicksum(self.u[s] for s in instance.S_2) >= instance.P_2,
            name="S2-PROTECT")

        # linking constraints
        for i in instance.V:
            self.model.addConstr(self.z[i] <= self.x[i], name=f"LINK-{i}")

        # save configuration of the constraints cuts later
        self.B = B
        self.C = C
        
        # BUFFER CONSTRAINTS
        if B:

            #  Buffer zones: select the d-neighborhood of the core as part of the buffer
            for i in instance.V:
                for j in instance.delta_d(i):
                    self.model.addConstr(
                        self.z[i] <= self.x[j],
                        name=f"d-BUFF.1-{i}-{j}")

            # Buffer zones: if a parcel is in the buffer, there must be a core in the d-neighborhood
            for i in instance.V:
                self.model.addConstr(
                    self.x[i] <= gb.quicksum(self.z[j] for j in instance.delta_d(i)),
                    name=f"d-BUFF.2-{i}")
        
        # CONNECTIVITY CONSTRAINTS
        if C:
            
            # Connected component con straints: the number of connected components in the reserve must be at most k
            self.model.addConstr(
                gb.quicksum(self.y[j] for j in instance.V) <= instance.k,
                name=f"NCOMP")
                    
        if C and not B:
            
            # Root-node constraints: a connected component must start at the core 
            for i in instance.V:
                self.model.addConstr(
                    self.y[i] <= self.x[i],
                    name=f"YX-{i}")
            
        # CONNECTIVITY + BUFFER CONSTRAINTS     
        if C and B:

            # Root-node constraints: a connected component must start at the core 
            for i in instance.V:
                self.model.addConstr(
                    self.y[i] <= self.z[i],
                    name=f"YZ-{i}")

    
    def separate_CORECON_fractional(self, z_val, y_val):
        n_nodes = len(self.instance.V)
        # build flow network
        self.digraph.build_flow_network(z_val, y_val)

        # separation of fractional solutions
        cuts = []
        tot_WA = set()

        # filtered by tau and if already in a precedent cut
        candidates = [l for l in self.instance.V if (z_val[l] < self.instance.tau or l in tot_WA)]
        
        # in reversed order because this way are more likely to skip nodes in tot_WA
        # otherwise they're ordered due to downlifting
        candidates.sort(reverse=True)
        for l in candidates:
            if l in tot_WA:
                continue
            if z_val[l] < self.instance.tau:
                continue
            
            cut = self.digraph.root_mincut(l)
            
            if cut.value >= z_val[l] - EPS:
                continue
            
            root_side = set(cut.partition[0])

            WV = []  # nodes separated by the cut
            WA = []  # arcs with capacity y that are in the cut

            for i in self.instance.V:
                i_in = i
                i_out = n_nodes + i

                if i_in in root_side and i_out not in root_side:
                    if i <= l:  # down-lifting, preventing symmetrical solutions
                        WV.append(i)

                if i_in not in root_side:
                    if i <= l:  # down-lifting
                        WA.append(i)
                        
            tot_WA.update(WA)
            if WV or WA:
                cuts.append((WV, WA, l))

        return cuts

    def separate_CORECON_integer(self, z_val, y_val):
        G = self.instance.G

        cuts = []

        core_nodes = [i for i in self.instance.V if z_val[i] > 0.5]
        if not core_nodes:
            return cuts

        core_subgraph = G.subgraph(core_nodes)

        for component in nx.connected_components(core_subgraph):
            # if at least one node is connected to the root
            if any(y_val[i] > 0.5 for i in component):  
                continue
            
            # down-lifting
            l = min(component)  
            
            WA = [i for i in component if i <= l]
            boundary = {j for i in component for j in G.neighbors(i) if j not in component}
            WV = [j for j in boundary if j <= l]
            
            if WA or WV:
                cuts.append((WV, WA, l))

        return cuts

    def separate_COVER(self, z_val, x_val, u_val):
        cuts = []
        w_dict = self.instance.w
        lambda_dict = self.instance.lambda_s
        
        for s in self.instance.S:
            Vs = list(self.instance.Vs[s])
        
            if not Vs:
                continue

            # Use precomputed sum
            Ws = self.instance._Ws[s]
            threshold = Ws - lambda_dict[s]

            if threshold <= 0:
                continue
            
            # sorts nodes in non decreasing way by z/w (S_1) or x/w (S_2)
            # sorted_Vs = sorted(Vs, key=lambda i: var_val[i] / (w_dict[(i, s)] + EPS))
            var_val = z_val if s in self.instance.S_1 else x_val
            ratios = np.array([var_val[i] / w_dict[(i, s)] for i in Vs])
            order = np.argsort(ratios)

            Cs, partial_sum = [], 0
            for idx in order:
                i = Vs[idx]
                Cs.append(i)
                partial_sum += w_dict[(i, s)]
                if partial_sum >= threshold:
                    break

            if not Cs:
                continue

            if sum(var_val[i] for i in Cs) < u_val[s] - EPS:
                cuts.append((Cs, s))
        return cuts

    def separate_SCC(self, z_val, y_val, u_val, cover_cuts):
        n_nodes = len(self.instance.V)

        cuts = []

        # build a flow network for each specie in S_1 in a cover cut
        for (Cs, s) in cover_cuts:
            if s in self.instance.S_2:
                continue

            self.digraph.build_flow_network(z_val, y_val, add_sink=True, Cs=Cs)
            
            cut = self.digraph.root_sink_mincut()
            
            if cut.value >= u_val[s] - EPS:
                continue
            
            root_side = set(cut.partition[0])

            WV = []  # nodes separated by the cut
            WA = []  # arcs with capacity y that are in the cut

            for i in self.instance.V:
                i_in = i
                i_out = n_nodes + i

                if i_in in root_side and i_out not in root_side:
                    WV.append(i)

                if i_in not in root_side:
                    WA.append(i)

            if WV or WA:
                cuts.append((WV, WA, s))

        return cuts

    def compute_shortest_path(self, set1, set2, weight_function):
        """
        Implementation for computing shortest paths between two sets of nodes
        """

        # precompute node weights based on the provided weight function
        # we need to have non negative weights for Dijkstra's algorithm, so we take max with 0
        node_weights = {i: max(0, weight_function(i)) for i in self.instance.V}

        def edge_weight(u, v, data):
            # we're computing the node weighted shortest path, so the weight of an edge can be approximated with the average of the weights of its endpoints

            return (node_weights[u] + node_weights[v]) / 2

        distances, paths = nx.multi_source_dijkstra(self.instance.G, set1, weight=edge_weight)

        best_distance = INF
        best_path = None

        for node in set2:
            if node in distances and distances[node] < best_distance:
                best_distance = distances[node]
                best_path = paths[node]

        return best_path

    # used by both the construction and primal heuristic to find a good partial solution
    def get_partial_solution(self, pool, cost):
        instance = self.instance

        solution = PartialSolution(instance)
        start_nodes = random.sample(list(pool), min(instance.k, len(pool)))

        solution.add_to_core(start_nodes)

        while not solution.feasible():
            T = solution.terminal_nodes()
            if not T or not solution.Sz:
                break
            path = self.compute_shortest_path(set1=solution.Sz, set2=T,
                                              weight_function=solution.node_cost_function(cost))
            if not path:
                break
            for node in path:
                solution.add_to_core([node])

        return solution

    def construction_heuristic(self, n_starts=20):

        best_objective = INF
        best_solution = None

        for _ in range(n_starts):
            # phase 1: create a frasible solution in a greedy fashion
            solution = self.get_partial_solution(pool=self.instance.V, cost=self.instance.c)

            # phase 2: remove uncecessary land parcels in a post-processing phase
            if solution.feasible():
                solution.post_process()
                objective = solution.objective()
                if objective < best_objective:
                    best_objective = objective
                    best_solution = solution

        return best_solution

    def primal_heuristic(self, x_tilde, y_tilde):

        pool = [i for i in self.instance.V if y_tilde[i] >= 0.001]
        if not pool:
            return None
        cost = {i: self.instance.c[i] * (1 - x_tilde[i]) for i in self.instance.V}

        # phase 1: create a frasible solution in a greedy fashion
        solution = self.get_partial_solution(pool=pool, cost=cost)

        # phase 2: remove uncecessary land parcels in a post-processing phase
        if solution.feasible():
            solution.post_process()

        return solution

    def init_counters(self):
        return {'corecon-int': 0, 'corecon-frc': 0, 'cover-s1': 0, 'cover-s2': 0, 'scc': 0}
    
    def make_callback(self, cp_heuristic=False, cutpool=None, cnt=None, verbose=False):
        """
        Returns a branch-and-cut callback function.
        """
        # standardize dictionary keys for counters
        if cnt is None: 
            cnt = self.init_counters()
        
        # local references to speed up access
        node_var = self.z if self.B else self.x
        V_list = self.instance.V
        S_list = self.instance.S
        y_vars = self.y

        def callback(model, where):
            # integer solution
            if where == gb.GRB.Callback.MIPSOL:
                node_val = {i: model.cbGetSolution(node_var[i]) for i in V_list}
                y_val    = {i: model.cbGetSolution(y_vars[i])   for i in V_list}
                # separation of CORECON constraints [z in CB, x in C]
                for (WV, WA, l) in self.separate_CORECON_integer(node_val, y_val):
                    model.cbLazy(
                        gb.quicksum(node_var[i] for i in WV) +
                        gb.quicksum(y_vars[i]   for i in WA) >= node_var[l])
                    if cutpool is not None:
                        cutpool.append((WV, WA, l))
                    cnt['corecon-int'] += 1
        
            # fractional solution (LP relaxation)
            if where == gb.GRB.Callback.MIPNODE:
                if model.cbGet(gb.GRB.Callback.MIPNODE_STATUS) != gb.GRB.OPTIMAL:
                    return

                node_val = {i: model.cbGetNodeRel(node_var[i]) for i in V_list}
                z_val    = {i: model.cbGetNodeRel(self.z[i])   for i in V_list}
                x_val    = {i: model.cbGetNodeRel(self.x[i])   for i in V_list}
                y_val    = {i: model.cbGetNodeRel(y_vars[i])   for i in V_list}
                u_val    = {s: model.cbGetNodeRel(self.u[s])   for s in S_list}

                violated_inequality_found = False

                 # separation of COVER constraints [always z]
                cover_cuts = self.separate_COVER(z_val, x_val, u_val)
                for (Cs, s) in cover_cuts:
                    if s in self.instance.S_1:
                        model.cbLazy(gb.quicksum(self.z[i] for i in Cs) >= self.u[s])
                        cnt['cover-s1'] += 1
                    else:
                        model.cbLazy(gb.quicksum(self.x[i] for i in Cs) >= self.u[s])
                        cnt['cover-s2'] += 1
                    violated_inequality_found = True

                # separation of SCC constraints [z for the network, node_val for the cut]
                for (WV, WA, s) in self.separate_SCC(z_val, y_val, u_val, cover_cuts):
                    model.cbLazy(
                        gb.quicksum(node_var[i] for i in WV) + gb.quicksum(y_vars[i]   for i in WA) >= self.u[s])
                    cnt['scc'] += 1
                    violated_inequality_found = True

                # separation of CORECON constraints [z in CB, x in C]
                if not violated_inequality_found:
                    for (WV, WA, l) in self.separate_CORECON_fractional(node_val, y_val):
                        model.cbLazy(
                            gb.quicksum(node_var[i] for i in WV) + gb.quicksum(y_vars[i]   for i in WA) >= node_var[l])
                        if cutpool is not None:
                            cutpool.append((WV, WA, l))
                        cnt['corecon-frc'] += 1

                if cp_heuristic and model.cbGet(gb.GRB.Callback.MIPNODE_OBJBST) == gb.GRB.INFINITY:
                    primal_solution = self.primal_heuristic(x_val, y_val)
                    if primal_solution and primal_solution.feasible():
                        self.cb_inject_solution(model, primal_solution)
                        if verbose:
                            print(f"\t * Solution of Primal Heuristic injected. Nodes: {primal_solution.Sx}")
            
        return callback

    def local_branching(self, initial_solution: PartialSolution, r=5, delta_r=5, max_r=20, iteration_time_limit=20,
                        overall_time_limit=180, verbose=False):
        """
        Local branching heuristic that explores the r-neighborhood of a given solution and if 
        a improvement is not found, r is incrememented, otherwise it returns at its initial value.
        
        Returns: the best solution found.
        """

        best_obj = initial_solution.objective()
        best_Sz = set(initial_solution.Sz)
        best_Sx = set(initial_solution.Sx)

        current_r = r
        start_time = time.time()
        iteration = 0

        while True:
            elapsed = time.time() - start_time

            if elapsed >= overall_time_limit:
                # overall time limit reached
                break

            if current_r > max_r:
                # max neighborhood reached
                break

            iteration += 1
            
            locbra = self.model.addConstr(
                gb.quicksum(self.z[i] for i in best_Sz) >= len(best_Sz) - current_r,
                name="LOCBRA")
            self.model.update()

            remaining = overall_time_limit - elapsed
            self.model.setParam('TimeLimit', min(iteration_time_limit, remaining))

            new_cuts = []
            cnt = self.init_counters()
            self.model.optimize(self.make_callback(cutpool=new_cuts, cnt=cnt,  verbose=True))
            if verbose and sum(cnt.values()) > 0:
                print(f"\t * Added constraints: {cnt}")

            # add cuts to the model
            for (WV, WA, l) in new_cuts:
                self.model.addConstr(
                    gb.quicksum(self.z[i] for i in WV) + gb.quicksum(self.y[i] for i in WA) >= self.z[l],
                    name="CUTPOOL"
                )

            self.model.remove(locbra)
            self.model.update()

            improved = self.model.SolCount > 0 and self.model.ObjVal < best_obj - EPS
            if improved:
                # if improvement found, r is reset
                best_obj = self.model.ObjVal
                best_Sz = {i for i in self.instance.V if self.z[i].X > 0.5}
                best_Sx = {i for i in self.instance.V if self.x[i].X > 0.5}
                current_r = r
            else:
                current_r += delta_r

        self.model.setParam('TimeLimit', gb.GRB.INFINITY)

        if verbose:
            print(f"\t * LB heuristic completed. Best objective: {best_obj:.2f}, Iterations: {iteration}")

        return best_Sx, best_Sz, best_obj

    def inject_solution(self, solution: PartialSolution):
        for i in self.instance.V:
            self.x[i].Start = 1 if i in solution.Sx else 0
            self.z[i].Start = 1 if i in solution.Sz else 0

        for s in self.instance.S:
            if solution.us(s):
                self.u[s].Start = 1
            else:
                self.u[s].Start = 0

    def cb_inject_solution(self, model, solution: PartialSolution):
        # to update the solution during the primal heuristic, we need to use cbSetSolution
        vars_to_set = []
        vals_to_set = []

        for i in self.instance.V:
            vars_to_set.append(self.x[i])
            vals_to_set.append(1 if i in solution.Sx else 0)
            
            vars_to_set.append(self.z[i])
            vals_to_set.append(1 if i in solution.Sz else 0)

        for s in self.instance.S:
            vars_to_set.append(self.u[s])
            vals_to_set.append(1 if solution.us(s) else 0)

        model.cbSetSolution(vars_to_set, vals_to_set)
        model.cbUseSolution()
    
    def solve(self, basic=False, cp_heuristic=False, lb_heuristic=False, verbose=True):
        
        if self.C: basic = True
        elif self.B: basic = False
        
        if not basic:
            self.model.optimize()
            return

        initial_solution = None

        if cp_heuristic:
            if verbose: print(f"\t * Starting construction heuristic...")
            initial_solution = self.construction_heuristic()
            if initial_solution:
                if verbose: print(f"\t * Initial solution found with Construction Heuristic. Nodes: {initial_solution.Sx}")
                self.inject_solution(initial_solution)
            

        if lb_heuristic and initial_solution:
            if verbose: print(f"\t * Starting local branching heuristic...")
            (best_Sx, best_Sz, best_obj) = self.local_branching(initial_solution, verbose=verbose)
            for i in self.instance.V:
                self.x[i].Start = 1 if i in best_Sx else 0
                self.z[i].Start = 1 if i in best_Sz else 0
        
        cnt = self.init_counters()
        if verbose: print(f"\t * Starting gurobi optimization...")
        self.model.optimize(self.make_callback(cp_heuristic=cp_heuristic, cnt=cnt, verbose=True))
        
        if verbose and sum(cnt.values()) > 0:
            print(f"\t * Added constraints: {cnt}")

    def print_graph(self):
        self.instance.draw_graph(self.x, self.z, self.u, self.B)

    def print_solution(self):
        status_map = {
            gb.GRB.OPTIMAL:    "Optimal",
            gb.GRB.SUBOPTIMAL: "Suboptimal",
            gb.GRB.TIME_LIMIT: "Time limit",
            gb.GRB.INFEASIBLE: "Infeasible",
        }
        status = self.model.Status
        print("Status:", status, status_map.get(status, f"Code {status}"))
        print("Objective:", self.model.ObjVal)
        if self.model.Status == gb.GRB.OPTIMAL:
            print("Nodes in the reserve (x):", [i for i in self.instance.V if self.x[i].X > 0.5])
            print("Nodes in the core (z):", [i for i in self.instance.V if self.z[i].X > 0.5])
            print("Species protected (u):", [s for s in self.instance.S if self.u[s].X > 0.5])
            print("r-arc-node separators (y):", [i for i in self.instance.V if self.y[i].X > 0.5])
        if status != gb.GRB.INFEASIBLE:
            self.print_graph()
