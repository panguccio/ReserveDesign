import gurobipy as gb
import numpy as np
import networkx as nx
from grsc_cb_instance import GRSC_CB_Instance
from grsc_cb_partial_solution import PartialSolution
import random
import time

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

    def __init__(self, instance: GRSC_CB_Instance, B=False, C=False):

        self.instance = instance
        self.model = gb.Model("GRSC-CB")

        # allow lazy constraints to be added by the callback function
        self.model.Params.LazyConstraints = 1

        self.model.setParam('OutputFlag', 0)

        # VARIABLES

        # x[i] = 1 if land parcel i is selected in the reserve, 0 otherwise
        self.x = self.model.addVars(instance.V, vtype=gb.GRB.BINARY, name="x")

        # z[i] = 1 if land parcel i is in the core, 0 otherwise
        self.z = self.model.addVars(instance.V, vtype=gb.GRB.BINARY, name="z")

        # u[s] = 1 if species s is protected, 0 otherwise
        self.u = self.model.addVars(instance.S, vtype=gb.GRB.BINARY, name="u")

        # y[i] = 1 if land parcel i is in the buffer zone, 0 otherwise
        self.y = self.model.addVars(instance.V, vtype=gb.GRB.BINARY, name="y")

        # OBJECTIVE FUNCTION: minimize the cost of selected land parcels
        self.model.setObjective(gb.quicksum(instance.c[i] * self.x[i] for i in instance.V), gb.GRB.MINIMIZE)

        # GENERAL CONSTRAINTS

        # Suitability quota constraints for S1 and S2: the ecological suitability of the reserve must be at least lambda_s[s] for each

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

        # Protection constraints for S1 and S2: at least P_1 species in S_1 and P_2 species in S_2 must be protected

        self.model.addConstr(
            gb.quicksum(self.u[s] for s in instance.S_1) >= instance.P_1,
            name="S1-PROTECT")

        self.model.addConstr(
            gb.quicksum(self.u[s] for s in instance.S_2) >= instance.P_2,
            name="S2-PROTECT")

        # Linking constraints: if a parcel is in the core, then it's in the reserve
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
            
            # Connected component constraints: the number of connected components in the reserve must be at most k
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
    
    def separate_CORECON_fractional(self, z_val, y_val, tau=0.5):

        # build flow network
        DG = self.build_flow_network(z_val, y_val)

        # separation of fractional solutions
        cuts = []

        for l in self.instance.V:
            if z_val[l] < tau:
                continue

            try:
                cut_val, (root_side, l_side) = nx.minimum_cut(
                    DG, 'root', (l, 'out'), capacity='capacity')
            except Exception:
                continue

            if cut_val >= z_val[l] - EPS:
                continue

            WV = []  # nodes separated by the cut
            WA = []  # arcs with capacity y that are in the cut

            for i in self.instance.V:
                i_in = (i, 'in')
                i_out = (i, 'out')

                if i_in in root_side and i_out in l_side:
                    if i <= l:  # down-lifting, preventing symmetrical solutions
                        WV.append(i)

                if i_in not in root_side:
                    if i <= l:  # down-lifting
                        WA.append(i)

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

            WA = list(component)
            WV = list({j for i in component for j in G.neighbors(i) if j not in component})

            # down-lifting
            l = min(component)  
            cuts.append((WV, WA, l))

        return cuts

    def separate_COVER(self, z_val, x_val, u_val):

        cuts = []

        for s in self.instance.S:
            var_val = z_val if s in self.instance.S_1 else x_val

            Vs = self.instance.v_s(s)
            if not Vs:
                continue

            Ws = sum(self.instance.w[(i, s)] for i in Vs)
            threshold = Ws - self.instance.lambda_s[s]

            if threshold <= 0:
                continue

            # sorts nodes in non decreasing way by z/w (S_1) or x/w (S_2)
            sorted_Vs = sorted(Vs, key=lambda i: var_val[i] / (self.instance.w[(i, s)] + EPS), reverse=True)

            Cs = []
            partial_sum = 0
            for i in sorted_Vs:
                Cs.append(i)
                partial_sum += self.instance.w[(i, s)]
                if partial_sum >= threshold:
                    break

            if not Cs:
                continue

            if sum(var_val[i] for i in Cs) < u_val[s] - EPS:
                cuts.append((Cs, s))

        return cuts

    def separate_SCC(self, z_val, y_val, u_val, cover_cuts):

        cuts = []

        # build a flow network for each specie in S_1 in a cover cut
        for (Cs, s) in cover_cuts:
            if s in self.instance.S_2:
                continue

            DG = self.build_flow_network(z_val, y_val, add_sink=True, Cs=Cs)

            try:
                cut_val, (root_side, sink_side) = nx.minimum_cut(
                    DG, 'root', 'sink', capacity='capacity')
            except Exception:
                continue

            if cut_val >= u_val[s] - EPS:
                continue

            WV = []  # nodes separated by the cut
            WA = []  # arcs with capacity y that are in the cut

            for i in self.instance.V:
                i_in = (i, 'in')
                i_out = (i, 'out')

                if i_in in root_side and i_out in sink_side:
                    WV.append(i)

                if i_in not in root_side:
                    WA.append(i)

            if WV or WA:
                cuts.append((WV, WA, s))

        return cuts

    def build_flow_network(self, z_val, y_val, add_sink=False, Cs=None):
        DG = nx.DiGraph()

        DG.add_node('root')
        if add_sink:
            DG.add_node('sink')

        for i in self.instance.V:
            DG.add_edge((i, 'in'), (i, 'out'), capacity=max(0, z_val[i]))
            DG.add_edge('root', (i, 'in'), capacity=max(0, y_val[i]))

        for (u, v) in self.instance.E:
            DG.add_edge((u, 'out'), (v, 'in'), capacity=INF)
            DG.add_edge((v, 'out'), (u, 'in'), capacity=INF)

        if add_sink:
            for i in Cs:
                DG.add_edge((i, 'out'), 'sink', capacity=INF)

        return DG

    def compute_shortest_path(self, set1, set2, weight_function):
        # Implementation for computing shortest paths between two sets of nodes

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
            if not T:
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
        cost = {i: self.instance.c[i] * (1 - x_tilde[i]) for i in self.instance.V}

        # phase 1: create a frasible solution in a greedy fashion
        solution = self.get_partial_solution(pool=pool, cost=cost)

        # phase 2: remove uncecessary land parcels in a post-processing phase
        if solution.feasible():
            solution.post_process()

        return solution

    def make_callback(self, cp_heuristic=False, cutpool=None, verbose=False):
        """
        Returns a branch-and-cut callback function.
        """
        
        def callback(model, where):

            # integer solution
            if where == gb.GRB.Callback.MIPSOL:
                z_val = {i: model.cbGetSolution(self.z[i]) for i in self.instance.V}
                y_val = {i: model.cbGetSolution(self.y[i]) for i in self.instance.V}

                # separation of CORECON constraints
                for (WV, WA, l) in self.separate_CORECON_integer(z_val, y_val):
                    model.cbLazy(gb.quicksum(self.z[i] for i in WV) + gb.quicksum(self.y[i] for i in WA) >= self.z[l])
                    if cutpool is not None:
                        cutpool.append((WV, WA, l))
                    if verbose:
                        print(f"Add constraint CORECON (integer): WV={WV}, WA={WA}, l={l}")

                        # fractional solution (LP relaxation)
            if where == gb.GRB.Callback.MIPNODE:
                if model.cbGet(gb.GRB.Callback.MIPNODE_STATUS) != gb.GRB.OPTIMAL:
                    return

                z_val = {i: model.cbGetNodeRel(self.z[i]) for i in self.instance.V}
                x_val = {i: model.cbGetNodeRel(self.x[i]) for i in self.instance.V}
                y_val = {i: model.cbGetNodeRel(self.y[i]) for i in self.instance.V}
                u_val = {s: model.cbGetNodeRel(self.u[s]) for s in self.instance.S}

                violated_inequality_found = False

                # separation of COVER constraints
                cover_cuts = self.separate_COVER(z_val, x_val, u_val)
                for (Cs, s) in cover_cuts:
                    if s in self.instance.S_1:
                        model.cbLazy(gb.quicksum(self.z[i] for i in Cs) >= self.u[s])
                        if verbose:
                            print(f"Add constraint COVER (S1): Cs={Cs}, s={s}")
                    else:
                        model.cbLazy(gb.quicksum(self.x[i] for i in Cs) >= self.u[s])
                        if verbose:
                            print(f"Add constraint COVER (S2): Cs={Cs}, s={s}")
                    violated_inequality_found = True

                # separation of SCC constraints
                for (WV, WA, s) in self.separate_SCC(z_val, y_val, u_val, cover_cuts):
                    model.cbLazy(gb.quicksum(self.z[i] for i in WV) + gb.quicksum(self.y[i] for i in WA) >= self.u[s])
                    if verbose:
                        print(f"Add constraint SCC: WV={WV}, WA={WA}, s={s}")
                    violated_inequality_found = True

                # separation of CORECON constraints
                if not violated_inequality_found:
                    for (WV, WA, l) in self.separate_CORECON_fractional(z_val, y_val):
                        model.cbLazy(
                            gb.quicksum(self.z[i] for i in WV) + gb.quicksum(self.y[i] for i in WA) >= self.z[l])
                        if cutpool is not None:
                            cutpool.append((WV, WA, l))
                        if verbose:
                            print(f"Add constraint CORECON (fractional): WV={WV}, WA={WA}, l={l}")

                if cp_heuristic and self.model.cbGet(gb.GRB.Callback.MIPNODE_OBJBST) == gb.GRB.INFINITY:
                    primal_solution = self.primal_heuristic(x_val, y_val)
                    if primal_solution and primal_solution.feasible():
                        self.inject_solution(primal_solution)
                        if verbose:
                            print("Primal heuristic solution injected")

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
            self.model.optimize(self.make_callback(cutpool=new_cuts, verbose=True))

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
            print(f"LB completed. Best objective: {best_obj:.2f}, Iterations: {iteration}")

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

    def solve(self, basic=False, cp_heuristic=False, lb_heuristic=False, verbose=False):

        if not basic:
            self.model.optimize()
            return

        initial_solution = None

        if cp_heuristic:
            initial_solution = self.construction_heuristic()
            if initial_solution:
                self.inject_solution(initial_solution)

        if lb_heuristic and initial_solution:
            (best_Sx, best_Sz, best_obj) = self.local_branching(initial_solution, verbose=verbose)
            for i in self.instance.V:
                self.x[i].Start = 1 if i in best_Sx else 0
                self.z[i].Start = 1 if i in best_Sz else 0

        self.model.optimize(self.make_callback(cp_heuristic=cp_heuristic, verbose=True))

    def print_graph(self):
        self.instance.draw_graph(self.x, self.z, self.u)

    def print_solution(self):
        print("Status:", self.model.Status)
        print("Objective:", self.model.ObjVal)
        if self.model.Status == gb.GRB.OPTIMAL:
            print("Nodes in the reserve (x):", [i for i in self.instance.V if self.x[i].X > 0.5])
            print("Nodes in the core (z):", [i for i in self.instance.V if self.z[i].X > 0.5])
            print("Species protected (u):", [s for s in self.instance.S if self.u[s].X > 0.5])
